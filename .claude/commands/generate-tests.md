Generate chapter verification tests for the markdown file at `$ARGUMENTS`.

## What to do

1. Read the chapter markdown file.
2. Read `chapters/tests/helpers.py` — use `run()`, `background()`, and `wait_for_http()`.
3. Read existing chapter tests in `chapters/tests/` for style reference.
4. Extract every runnable code block and its expected output from the chapter.
5. Write a test file at `chapters/tests/test_<chapter_name>.py`.

## Rules

- One test class per chapter file, named `TestChapter<NN>`.
- One test per code block or distinct claim (e.g. "this command fails", "this endpoint returns X").
- Use `run()` for commands that should succeed — it raises on non-zero exit, that IS the assertion. Don't string-match "passed".
- Use `background()` for long-running processes (servers). Always use a port offset (18000+) to avoid collisions.
- Assert on actual behavior, not output strings. Check return codes, HTTP responses, JSON payloads.
- If the chapter says something "doesn't work" or "won't run", test that it actually behaves that way (exits without serving, returns an error, etc).
- Don't add negative tests unless the chapter explicitly demonstrates a failure case.
- Keep it simple. No fixtures unless shared setup is unavoidable.

## After writing

Run `uv run pytest chapters/tests/<new_test_file>.py -v` and make sure everything passes.
