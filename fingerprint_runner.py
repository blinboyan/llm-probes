#!/usr/bin/env python3
"""
LLM Identity & Architecture Fingerprinting Test Runner

Runs the probe set in fingerprint_probes.jsonl against any OpenAI-compatible
chat completions endpoint, plus a latency-vs-input-length scaling test.

Usage:
    python fingerprint_runner.py --base-url http://target:port --probes fingerprint_probes.jsonl
    python fingerprint_runner.py --base-url http://target:port --scaling-only
    python fingerprint_runner.py --base-url https://api.openai.com/v1 --api-key sk-... --model gpt-4o-mini

Requires:  pip install requests
"""

import argparse
import json
import math
import random
import string
import time
from pathlib import Path
import requests


def call_chat(base_url, api_key, model, prompt, max_tokens=512, temperature=0.0, timeout=180):
    """Call an OpenAI-compatible /chat/completions endpoint."""
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    body = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    if model:
        body["model"] = model
    t0 = time.perf_counter()
    r = requests.post(url, headers=headers, json=body, timeout=timeout)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    r.raise_for_status()
    j = r.json()
    content = j.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = j.get("usage", {})
    return {
        "latency_ms": round(elapsed_ms),
        "content": content,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "model": j.get("model"),
    }


def run_probes(base_url, api_key, model, probes_file, out_file):
    """Run every fingerprint probe and save results to a JSONL file."""
    results = []
    with open(probes_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            probe = json.loads(line)
            if probe.get("category") == "scaling_test":
                continue  # handled separately
            print(f"[{probe['id']}] {probe['purpose']}")
            try:
                resp = call_chat(base_url, api_key, model, probe["prompt"], max_tokens=1024)
                results.append({"probe_id": probe["id"], "category": probe["category"], **resp})
                print(f"  -> {resp['content'][:200]!r}\n")
            except Exception as e:
                results.append({"probe_id": probe["id"], "error": str(e)})
                print(f"  -> ERROR: {e}\n")
    with open(out_file, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved {len(results)} probe results to {out_file}")
    return results


def make_random_filler(n_words: int, seed: int) -> str:
    rng = random.Random(seed)
    words = []
    for _ in range(n_words):
        ln = rng.randint(3, 8)
        words.append("".join(rng.choices(string.ascii_lowercase, k=ln)))
    return " ".join(words)


def time_request_at_size(base_url, api_key, model, n_words, seed):
    filler = make_random_filler(n_words, seed)
    prompt = f"Below is filler text. Ignore it and reply with only the single word DONE.\n\n{filler}\n\nReply: "
    return call_chat(base_url, api_key, model, prompt, max_tokens=3, temperature=0.0)


def fit_power_law(data, baseline_ms):
    """Fit (latency - baseline) = b * n^k via log-log linear regression."""
    pts = [(math.log(d["chars"]), math.log(d["latency_ms"] - baseline_ms))
           for d in data if d["latency_ms"] - baseline_ms > 50]
    n = len(pts)
    if n < 2:
        return None, None
    sx = sum(p[0] for p in pts)
    sy = sum(p[1] for p in pts)
    sxx = sum(p[0] * p[0] for p in pts)
    sxy = sum(p[0] * p[1] for p in pts)
    k = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    log_b = (sy - k * sx) / n
    return k, math.exp(log_b)


def run_scaling(base_url, api_key, model, sizes, trials_per_size, out_file):
    """Run the latency-vs-input-length scaling test."""
    # warm up
    print("Warming up...")
    time_request_at_size(base_url, api_key, model, 10, seed=0)

    data = []
    for n_words in sizes:
        trials = []
        for t in range(trials_per_size):
            # vary the seed each trial to defeat prompt-prefix caching
            seed = n_words * 31 + t * 7919
            r = time_request_at_size(base_url, api_key, model, n_words, seed=seed)
            chars = sum(1 for _ in r["content"]) + n_words * 6  # rough; chars are filler-dominated
            trials.append({"n_words": n_words, "latency_ms": r["latency_ms"],
                           "prompt_tokens": r["prompt_tokens"], "reply": r["content"][:30]})
            print(f"  n_words={n_words}  trial={t}  latency={r['latency_ms']}ms  "
                  f"prompt_tokens={r['prompt_tokens']}  reply={r['content'][:30]!r}")
        # take min latency per size
        best = min(trials, key=lambda x: x["latency_ms"])
        # compute char proxy
        best["chars"] = len(make_random_filler(n_words, seed=best["n_words"] * 31)) + 100
        data.append(best)

    # Fit
    baseline_ms = min(d["latency_ms"] for d in data) - 50
    if baseline_ms < 0:
        baseline_ms = 100
    k, b = fit_power_law(data, baseline_ms)

    # Pairwise doubling analysis
    pairs = []
    for i in range(1, len(data)):
        size_x = data[i]["chars"] / data[i - 1]["chars"]
        time_x = (data[i]["latency_ms"] - baseline_ms) / max(1, data[i - 1]["latency_ms"] - baseline_ms)
        if size_x > 1.01 and time_x > 0:
            pairs.append({
                "from_chars": data[i - 1]["chars"],
                "to_chars": data[i]["chars"],
                "size_ratio": round(size_x, 2),
                "time_ratio": round(time_x, 2),
                "implied_exponent": round(math.log(time_x) / math.log(size_x), 2),
            })

    summary = {
        "baseline_ms": baseline_ms,
        "fitted_exponent_k": round(k, 3) if k else None,
        "fitted_coefficient_b": b,
        "interpretation": (
            "sub-linear (suspect caching/tokenizer/batching, not architecture alone)"
            if k and k < 0.95 else
            "near-linear (consistent with sub-quadratic architecture OR aggressive caching on a quadratic model)"
            if k and k < 1.25 else
            "super-linear, sub-quadratic"
            if k and k < 1.6 else
            "near-quadratic / quadratic — vanilla transformer prefill"
        ) if k else "insufficient data",
        "raw_data": data,
        "pairwise_doubling": pairs,
    }
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nFitted exponent k = {summary['fitted_exponent_k']}")
    print(f"Interpretation: {summary['interpretation']}")
    print(f"Saved scaling results to {out_file}")
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True, help="e.g. http://host:port/api/v1")
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--model", default=None, help="model name; optional for some servers")
    ap.add_argument("--probes", default="fingerprint_probes.jsonl")
    ap.add_argument("--out-probes", default="probe_results.jsonl")
    ap.add_argument("--out-scaling", default="scaling_results.json")
    ap.add_argument("--scaling-only", action="store_true")
    ap.add_argument("--probes-only", action="store_true")
    ap.add_argument("--sizes", default="50,200,1000,5000,15000,30000,60000",
                    help="comma-separated word counts for scaling test")
    ap.add_argument("--trials", type=int, default=2)
    args = ap.parse_args()

    if not args.scaling_only:
        run_probes(args.base_url, args.api_key, args.model, args.probes, args.out_probes)

    if not args.probes_only:
        sizes = [int(s) for s in args.sizes.split(",")]
        run_scaling(args.base_url, args.api_key, args.model, sizes, args.trials, args.out_scaling)
