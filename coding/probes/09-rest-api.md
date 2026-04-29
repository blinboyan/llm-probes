# Probe 09: REST API with Tests (Comprehensive)

## Prompt to give the agent

> Build a simple URL shortener API using Python and Flask (or FastAPI — your choice).
>
> Endpoints:
> - `POST /shorten` — accepts `{"url": "https://example.com"}`, returns `{"short_url": "http://localhost:5000/abc123", "id": "abc123"}`
> - `GET /<id>` — redirects to the original URL (302)
> - `GET /stats/<id>` — returns `{"id": "abc123", "url": "https://...", "clicks": 42, "created_at": "..."}`
>
> Requirements:
> - Use an in-memory store (no database needed)
> - Short IDs should be 6 characters, alphanumeric
> - Validate that the input URL is actually a URL
> - Return appropriate HTTP status codes (201, 302, 404, 400)
> - Include tests using pytest that cover all endpoints and error cases
>
> Create a complete, runnable project with a requirements.txt.

## What to evaluate

- Does the API actually work end-to-end?
- Are all status codes correct? (201 for create, 302 for redirect, 404 for missing, 400 for bad input)
- URL validation: does it reject non-URLs?
- Tests: do they cover happy path AND error cases (missing ID, bad URL, etc.)?
- Project structure: is it organized or all in one file? (one file is fine for this scope)
- Did it include a requirements.txt?
- Click counting: does the stats endpoint actually track clicks?

## Process evaluation

- Did the agent create everything in one shot, or need multiple rounds?
- Did it run the tests to verify they pass?
- Did it ask for framework preference or just pick one? (picking one is better here)
- How many files were created? (3-4 is ideal: app.py, test_app.py, requirements.txt, maybe a README)

## Red flags
- No URL validation
- Tests that don't actually test HTTP responses (just unit testing internal functions)
- Using a database when in-memory was specified
- Not tracking clicks
- Creating 10+ files for this simple task
