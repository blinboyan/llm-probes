# Probe 10: Multi-File Feature — Markdown Note System (Comprehensive)

## Prompt to give the agent

> Build a CLI note-taking app in Python that stores notes as Markdown files.
>
> Commands:
> - `notes add "Title" --tags tag1,tag2` — creates a timestamped .md file in `./notes/`
>   - Opens content from stdin (or `--body "text"` flag)
>   - Adds YAML frontmatter: title, date, tags
> - `notes list` — lists all notes (title, date, tags) in a table
>   - `--tag filter` — filter by tag
>   - `--sort date|title` — sort order
> - `notes search "query"` — full-text search across all notes, shows matching snippets
> - `notes export --format json` — export all notes as JSON
>
> Requirements:
> - Use `argparse` or `click` for CLI
> - Store notes as individual .md files with YAML frontmatter
> - Use only standard library (except `click` if chosen, and `pyyaml`)
> - Include at least 5 tests covering add, list, search, and export
> - Handle errors gracefully (missing notes dir, bad input, etc.)
>
> Create a proper project structure.

## What to evaluate

### Architecture
- Is there a clear separation between CLI, storage, and note model?
- How are notes stored? (individual .md files with frontmatter is correct)
- Is the project structure reasonable? (not too flat, not too deep)

### Functionality
- Does `add` actually create files with correct frontmatter?
- Does `list` parse frontmatter and display a readable table?
- Does `search` do actual full-text search with context snippets?
- Does `export` produce valid JSON with all note data?
- Does tag filtering work?

### Tests
- Do tests use temp directories (not polluting real filesystem)?
- Do they test the actual CLI interface or just internal functions?
- Are there tests for error cases?

### Process
- How many turns did it take?
- Did the agent create all files in a logical order?
- Did it run the tests to verify?
- Did it create unnecessary files (CI config, Docker, etc.)?

## Expected file structure

```
notes_app/
  __init__.py (or just a flat structure)
  cli.py
  storage.py
  models.py (optional)
  tests/
    test_cli.py or test_notes.py
  requirements.txt (if using click/pyyaml)
```

## Red flags
- Massive over-engineering (database, config files, plugin system)
- No YAML frontmatter (just storing plain text)
- Tests that create files in the working directory
- No error handling for missing directories
- Creating 15+ files
