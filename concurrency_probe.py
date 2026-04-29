#!/usr/bin/env python3
"""
Load Balancer & Concurrency Probe

Tests whether the target endpoint has:
1. Multiple backends (load balancer detection via response fingerprinting)
2. Concurrency handling (parallel request behavior)
3. Rate limiting
4. Connection pooling behavior

Usage:
    python concurrency_probe.py
    python concurrency_probe.py --base-url http://host:port/api/v1 --concurrency 10
"""

import argparse
import hashlib
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import Counter


# .env loader
def load_env(path=".env"):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


load_env(Path(__file__).parent / ".env")

try:
    import requests
except ImportError:
    print("ERROR: pip install requests")
    sys.exit(1)


def call_chat(base_url, api_key, model, prompt, max_tokens=64,
              temperature=0.0, timeout=60):
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
    return {
        "latency_ms": round(elapsed_ms),
        "content": content,
        "model": j.get("model"),
        "id": j.get("id", ""),
        "created": j.get("created"),
        "headers": dict(r.headers),
    }


# ===========================================================================
# Test 1: Response fingerprinting for LB detection
# ===========================================================================
def probe_lb_fingerprint(cfg, n_requests=10):
    """Send identical requests and compare response headers/IDs for backend variation."""
    print("\n" + "=" * 60)
    print("TEST 1: Load Balancer Detection (Response Fingerprinting)")
    print("=" * 60)

    # Fixed prompt with temperature=0 for deterministic output
    prompt = "Reply with exactly: PONG"
    results = []

    print(f"Sending {n_requests} identical sequential requests...")
    for i in range(n_requests):
        try:
            resp = call_chat(cfg["base_url"], cfg["api_key"], cfg["model"],
                             prompt, max_tokens=16, temperature=0.0)
            # Fingerprint: server headers, response ID patterns, content hash
            server = resp["headers"].get("server", resp["headers"].get("Server", ""))
            x_powered = resp["headers"].get("x-powered-by", "")
            via = resp["headers"].get("via", "")
            x_request_id = resp["headers"].get("x-request-id", "")
            cf_ray = resp["headers"].get("cf-ray", "")

            # Content fingerprint
            content_hash = hashlib.md5(resp["content"].encode()).hexdigest()[:8]

            results.append({
                "idx": i,
                "latency_ms": resp["latency_ms"],
                "server": server,
                "x_powered_by": x_powered,
                "via": via,
                "x_request_id": x_request_id,
                "cf_ray": cf_ray,
                "response_id": resp["id"],
                "content_hash": content_hash,
                "content_preview": resp["content"][:50],
                "model_field": resp["model"],
                "created": resp["created"],
            })
            print(f"  [{i+1}] {resp['latency_ms']}ms  id={resp['id'][:30]}  "
                  f"hash={content_hash}  server={server or '(none)'}")
        except Exception as e:
            results.append({"idx": i, "error": str(e)})
            print(f"  [{i+1}] ERROR: {e}")

    # Analyze for LB signals
    print("\n--- Analysis ---")

    # Check response ID patterns
    ids = [r.get("response_id", "") for r in results if "response_id" in r]
    id_prefixes = Counter(id[:20] for id in ids if id)
    print(f"Response ID prefixes: {dict(id_prefixes)}")

    # Check server headers
    servers = Counter(r.get("server", "(none)") for r in results if "server" in r)
    print(f"Server headers: {dict(servers)}")

    # Check content consistency
    hashes = Counter(r.get("content_hash", "") for r in results if "content_hash" in r)
    print(f"Content hash distribution: {dict(hashes)}")

    # Check all interesting headers
    all_headers = set()
    for r in results:
        if "headers" not in r:
            continue
        # headers were stored but not in results list... check via first result
    if results and "x_request_id" in results[0]:
        x_ids = [r.get("x_request_id", "") for r in results]
        unique_xids = len(set(x_ids))
        print(f"X-Request-ID unique values: {unique_xids}/{len(x_ids)}")

    # Latency variance
    latencies = [r["latency_ms"] for r in results if "latency_ms" in r]
    if latencies:
        print(f"Latency: min={min(latencies)}ms, max={max(latencies)}ms, "
              f"mean={statistics.mean(latencies):.0f}ms, stdev={statistics.stdev(latencies):.0f}ms")

    # LB verdict
    lb_signals = []
    if len(servers) > 1:
        lb_signals.append("multiple Server headers")
    if len(hashes) > 1:
        lb_signals.append("inconsistent responses to identical prompts")
    if len(id_prefixes) > 1 and any(p for p in id_prefixes if p):
        lb_signals.append("varying response ID patterns")
    if latencies and statistics.stdev(latencies) > 500:
        lb_signals.append("high latency variance (may indicate different backends)")

    if lb_signals:
        print(f"\nLB signals detected: {', '.join(lb_signals)}")
    else:
        print(f"\nNo clear LB signals. Likely single backend or very consistent LB.")

    return {"test": "lb_fingerprint", "n_requests": n_requests,
            "servers": dict(servers), "content_hashes": dict(hashes),
            "latency_stats": {
                "min": min(latencies) if latencies else None,
                "max": max(latencies) if latencies else None,
                "mean": round(statistics.mean(latencies)) if latencies else None,
                "stdev": round(statistics.stdev(latencies)) if len(latencies) > 1 else None,
            },
            "lb_signals": lb_signals, "details": results}


# ===========================================================================
# Test 2: Concurrent request behavior
# ===========================================================================
def probe_concurrency(cfg, concurrency_levels=None):
    """Send parallel requests and measure throughput scaling."""
    print("\n" + "=" * 60)
    print("TEST 2: Concurrency Handling")
    print("=" * 60)

    if concurrency_levels is None:
        concurrency_levels = [1, 2, 4, 8, 16]

    prompt = "What is 2+2? Reply with just the number."
    results_by_level = {}

    for n in concurrency_levels:
        print(f"\n  Concurrency={n}:")
        latencies = []
        errors = 0

        def do_request(idx):
            try:
                return call_chat(cfg["base_url"], cfg["api_key"], cfg["model"],
                                 prompt, max_tokens=16, temperature=0.0, timeout=120)
            except Exception as e:
                return {"error": str(e)}

        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=n) as pool:
            futures = [pool.submit(do_request, i) for i in range(n)]
            for f in as_completed(futures):
                result = f.result()
                if "error" in result:
                    errors += 1
                else:
                    latencies.append(result["latency_ms"])

        wall_time = (time.perf_counter() - t0) * 1000

        if latencies:
            mean_lat = statistics.mean(latencies)
            throughput = n / (wall_time / 1000)  # requests per second
            print(f"    Wall time: {wall_time:.0f}ms | Mean latency: {mean_lat:.0f}ms | "
                  f"Min: {min(latencies)}ms | Max: {max(latencies)}ms | "
                  f"Throughput: {throughput:.2f} req/s | Errors: {errors}")
        else:
            mean_lat = None
            throughput = 0
            print(f"    All {n} requests failed!")

        results_by_level[n] = {
            "concurrency": n,
            "wall_time_ms": round(wall_time),
            "mean_latency_ms": round(mean_lat) if mean_lat else None,
            "min_latency_ms": min(latencies) if latencies else None,
            "max_latency_ms": max(latencies) if latencies else None,
            "throughput_rps": round(throughput, 2),
            "errors": errors,
            "successful": len(latencies),
        }

    # Analyze scaling
    print("\n--- Concurrency Scaling Analysis ---")
    levels = sorted(results_by_level.keys())
    baseline = results_by_level.get(1, {})
    baseline_lat = baseline.get("mean_latency_ms", 0)

    for n in levels:
        r = results_by_level[n]
        if baseline_lat and r.get("mean_latency_ms"):
            slowdown = r["mean_latency_ms"] / baseline_lat
            print(f"  N={n:2d}: mean_latency={r['mean_latency_ms']:5d}ms  "
                  f"slowdown={slowdown:.2f}x  throughput={r['throughput_rps']:.2f} req/s  "
                  f"errors={r['errors']}")
        else:
            print(f"  N={n:2d}: {r}")

    # Detect queuing behavior
    if len(levels) >= 2 and baseline_lat:
        max_level = max(levels)
        max_r = results_by_level[max_level]
        if max_r.get("mean_latency_ms"):
            slowdown = max_r["mean_latency_ms"] / baseline_lat
            if slowdown > max_level * 0.8:
                print(f"\n  => SERIAL PROCESSING detected: {max_level}x concurrency "
                      f"causes {slowdown:.1f}x slowdown (near-linear with N).")
                print(f"     Suggests single backend with request queuing.")
            elif slowdown > max_level * 0.3:
                print(f"\n  => PARTIAL PARALLELISM: {max_level}x concurrency "
                      f"causes {slowdown:.1f}x slowdown.")
                print(f"     Suggests limited parallelism (few backends or GPU batching).")
            else:
                print(f"\n  => GOOD PARALLELISM: {max_level}x concurrency "
                      f"causes only {slowdown:.1f}x slowdown.")
                print(f"     Suggests multiple backends or efficient batching.")

    return {"test": "concurrency", "results": results_by_level}


# ===========================================================================
# Test 3: Rate limiting detection
# ===========================================================================
def probe_rate_limit(cfg, burst_size=20):
    """Send rapid burst of requests to detect rate limiting."""
    print("\n" + "=" * 60)
    print("TEST 3: Rate Limiting Detection")
    print("=" * 60)

    prompt = "Say OK"
    results = []

    print(f"Sending {burst_size} requests as fast as possible...")
    t0_burst = time.perf_counter()

    for i in range(burst_size):
        try:
            resp = call_chat(cfg["base_url"], cfg["api_key"], cfg["model"],
                             prompt, max_tokens=8, temperature=0.0, timeout=30)
            results.append({
                "idx": i,
                "latency_ms": resp["latency_ms"],
                "status": "ok",
            })
            # Check for rate limit headers
            headers = resp.get("headers", {})
            for key in ["x-ratelimit-limit", "x-ratelimit-remaining",
                        "x-ratelimit-reset", "retry-after"]:
                if key in headers:
                    results[-1][key] = headers[key]
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 0
            results.append({"idx": i, "status": f"http_{status_code}", "error": str(e)[:100]})
            if status_code == 429:
                retry_after = e.response.headers.get("retry-after", "?")
                print(f"  [{i+1}] RATE LIMITED (429) — retry-after: {retry_after}")
            else:
                print(f"  [{i+1}] HTTP {status_code}")
        except Exception as e:
            results.append({"idx": i, "status": "error", "error": str(e)[:100]})

    burst_time = (time.perf_counter() - t0_burst) * 1000

    ok_results = [r for r in results if r["status"] == "ok"]
    rate_limited = [r for r in results if "429" in str(r.get("status", ""))]
    errors = [r for r in results if r["status"] not in ("ok",) and "429" not in str(r.get("status", ""))]

    print(f"\n  Burst of {burst_size} in {burst_time:.0f}ms")
    print(f"  Successful: {len(ok_results)}")
    print(f"  Rate-limited (429): {len(rate_limited)}")
    print(f"  Other errors: {len(errors)}")

    if ok_results:
        lats = [r["latency_ms"] for r in ok_results]
        print(f"  Latency: min={min(lats)}ms, max={max(lats)}ms, mean={statistics.mean(lats):.0f}ms")

        # Check for progressive slowdown (soft rate limiting / queuing)
        first_half = lats[:len(lats)//2]
        second_half = lats[len(lats)//2:]
        if first_half and second_half:
            first_mean = statistics.mean(first_half)
            second_mean = statistics.mean(second_half)
            if second_mean > first_mean * 1.5:
                print(f"  Progressive slowdown detected: first half avg={first_mean:.0f}ms, "
                      f"second half avg={second_mean:.0f}ms")

    # Check for rate limit headers
    rl_headers = {}
    for r in ok_results:
        for key in ["x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset"]:
            if key in r:
                rl_headers[key] = r[key]
    if rl_headers:
        print(f"  Rate limit headers found: {rl_headers}")
    else:
        print(f"  No rate limit headers detected")

    return {"test": "rate_limit", "burst_size": burst_size,
            "burst_time_ms": round(burst_time),
            "successful": len(ok_results), "rate_limited": len(rate_limited),
            "errors": len(errors), "rate_limit_headers": rl_headers,
            "details": results}


# ===========================================================================
# Test 4: Server identity probing (HTTP-level)
# ===========================================================================
def probe_server_identity(cfg):
    """Probe the server at the HTTP level for infrastructure clues."""
    print("\n" + "=" * 60)
    print("TEST 4: Server Identity (HTTP-Level Probing)")
    print("=" * 60)

    base = cfg["base_url"].rstrip("/")
    results = {}

    # Probe various endpoints
    endpoints = [
        ("root", base.rsplit("/api/v1", 1)[0] if "/api/v1" in base else base),
        ("api_root", base),
        ("models", base + "/models"),
        ("health", base.rsplit("/api/v1", 1)[0] + "/health" if "/api/v1" in base else base + "/health"),
        ("openapi", base.rsplit("/api/v1", 1)[0] + "/docs" if "/api/v1" in base else base + "/docs"),
        ("version", base.rsplit("/api/v1", 1)[0] + "/version" if "/api/v1" in base else base + "/version"),
    ]

    for name, url in endpoints:
        try:
            r = requests.get(url, timeout=10, allow_redirects=False)
            interesting_headers = {k: v for k, v in r.headers.items()
                                   if k.lower() in [
                                       "server", "x-powered-by", "via", "x-request-id",
                                       "x-served-by", "x-backend", "x-cache",
                                       "cf-ray", "x-vercel-id", "x-amz-request-id",
                                       "alt-svc", "content-type",
                                   ]}
            body_preview = r.text[:200] if r.ok else r.text[:100]
            print(f"  {name} ({url}):")
            print(f"    Status: {r.status_code}")
            if interesting_headers:
                for k, v in interesting_headers.items():
                    print(f"    {k}: {v}")
            if r.ok and body_preview:
                print(f"    Body: {body_preview!r}")
            results[name] = {
                "url": url, "status": r.status_code,
                "headers": interesting_headers,
                "body_preview": body_preview,
            }
        except Exception as e:
            results[name] = {"url": url, "error": str(e)[:100]}
            print(f"  {name}: ERROR: {str(e)[:80]}")

    # Check /models endpoint specifically for model list
    try:
        r = requests.get(base + "/models", timeout=10)
        if r.ok:
            models_data = r.json()
            print(f"\n  Available models:")
            if isinstance(models_data, dict) and "data" in models_data:
                for m in models_data["data"][:10]:
                    print(f"    - {m.get('id', m)}")
            else:
                print(f"    {json.dumps(models_data)[:300]}")
            results["models_list"] = models_data
    except Exception:
        pass

    return {"test": "server_identity", "results": results}


# ===========================================================================
# Test 5: Connection behavior (keep-alive, TLS, etc.)
# ===========================================================================
def probe_connection(cfg, n=5):
    """Test connection reuse and keep-alive behavior."""
    print("\n" + "=" * 60)
    print("TEST 5: Connection Behavior")
    print("=" * 60)

    base_url = cfg["base_url"]
    prompt = "Say hi"

    # Test with session (connection reuse)
    session = requests.Session()
    session_lats = []
    print(f"  With connection reuse (Session), {n} requests:")
    for i in range(n):
        url = base_url.rstrip("/") + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if cfg["api_key"]:
            headers["Authorization"] = f"Bearer {cfg['api_key']}"
        body = {"messages": [{"role": "user", "content": prompt}],
                "max_tokens": 8, "temperature": 0, "stream": False}
        if cfg["model"]:
            body["model"] = cfg["model"]
        t0 = time.perf_counter()
        r = session.post(url, headers=headers, json=body, timeout=30)
        lat = (time.perf_counter() - t0) * 1000
        session_lats.append(round(lat))
        print(f"    [{i+1}] {round(lat)}ms")
    session.close()

    # Test without session (new connection each time)
    no_session_lats = []
    print(f"  Without connection reuse (new conn), {n} requests:")
    for i in range(n):
        resp = call_chat(base_url, cfg["api_key"], cfg["model"],
                         prompt, max_tokens=8, temperature=0.0, timeout=30)
        no_session_lats.append(resp["latency_ms"])
        print(f"    [{i+1}] {resp['latency_ms']}ms")

    session_mean = statistics.mean(session_lats) if session_lats else 0
    no_session_mean = statistics.mean(no_session_lats) if no_session_lats else 0

    print(f"\n  Session (reuse) avg: {session_mean:.0f}ms")
    print(f"  No session (new conn) avg: {no_session_mean:.0f}ms")
    diff = no_session_mean - session_mean
    print(f"  Connection overhead: ~{diff:.0f}ms per new connection")

    return {
        "test": "connection_behavior",
        "session_mean_ms": round(session_mean),
        "no_session_mean_ms": round(no_session_mean),
        "connection_overhead_ms": round(diff),
    }


# ===========================================================================
# Main
# ===========================================================================
def main():
    ap = argparse.ArgumentParser(description="LB & Concurrency Probe")
    ap.add_argument("--base-url", default=os.environ.get("BASE_URL"))
    ap.add_argument("--api-key", default=os.environ.get("API_KEY"))
    ap.add_argument("--model", default=os.environ.get("MODEL"))
    ap.add_argument("--concurrency", default="1,2,4,8,16",
                    help="Comma-separated concurrency levels to test")
    ap.add_argument("--burst", type=int, default=20,
                    help="Burst size for rate limit test")
    ap.add_argument("--output", default="concurrency_results.json")
    args = ap.parse_args()

    if not args.base_url:
        print("ERROR: --base-url required (or set BASE_URL in .env)")
        sys.exit(1)

    cfg = {
        "base_url": args.base_url,
        "api_key": args.api_key or None,
        "model": args.model or None,
    }
    concurrency_levels = [int(x) for x in args.concurrency.split(",")]

    print("=" * 60)
    print("LOAD BALANCER & CONCURRENCY PROBE")
    print("=" * 60)
    print(f"Target: {cfg['base_url']}")
    print()

    all_results = {
        "endpoint": cfg["base_url"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    t0 = time.perf_counter()
    all_results["server_identity"] = probe_server_identity(cfg)
    all_results["lb_fingerprint"] = probe_lb_fingerprint(cfg)
    all_results["concurrency"] = probe_concurrency(cfg, concurrency_levels)
    all_results["rate_limit"] = probe_rate_limit(cfg, args.burst)
    all_results["connection"] = probe_connection(cfg)
    elapsed = time.perf_counter() - t0

    # Final verdict
    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)

    lb_signals = all_results["lb_fingerprint"].get("lb_signals", [])
    conc = all_results["concurrency"].get("results", {})
    c1 = conc.get(1, {}).get("mean_latency_ms", 0)
    c_max = conc.get(max(concurrency_levels), {})
    c_max_lat = c_max.get("mean_latency_ms", 0)

    if lb_signals:
        print(f"  Load Balancer: LIKELY ({', '.join(lb_signals)})")
    else:
        print(f"  Load Balancer: NOT DETECTED (single backend probable)")

    if c1 and c_max_lat:
        ratio = c_max_lat / c1
        if ratio > max(concurrency_levels) * 0.7:
            print(f"  Concurrency: SERIAL (N={max(concurrency_levels)} -> {ratio:.1f}x slowdown)")
        elif ratio > 2:
            print(f"  Concurrency: LIMITED PARALLEL (N={max(concurrency_levels)} -> {ratio:.1f}x slowdown)")
        else:
            print(f"  Concurrency: GOOD PARALLEL (N={max(concurrency_levels)} -> {ratio:.1f}x slowdown)")

    rl = all_results["rate_limit"]
    if rl.get("rate_limited", 0) > 0:
        print(f"  Rate Limiting: YES ({rl['rate_limited']}/{rl['burst_size']} requests blocked)")
    else:
        print(f"  Rate Limiting: NOT DETECTED in burst of {rl['burst_size']}")

    conn = all_results["connection"]
    print(f"  Connection Overhead: ~{conn['connection_overhead_ms']}ms per new connection")

    print(f"\nTotal probe time: {elapsed:.1f}s")
    all_results["total_time_s"] = round(elapsed, 1)

    with open(args.output, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
