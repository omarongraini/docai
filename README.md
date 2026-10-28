


## Quick start

### clone and install deps
```bash
git clone <repo>
cd chatpdf
uv sync
```
### add env vars
```bash
cp .env.example .env
cp docker/.env.postgres.example docker/.env.postgres
```
Edit the env files based on your preferences

### Database creation
```bash
cd docker
docker compose up -d --wait
```

### run the database migration
```bash 
cd ..
uv run alembic upgrade head
```

### run the chat app
```bash 
uv run streamlit run app_chat.py
```


### Development

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```

## Maintenance

If you change your `EMBED_MODEL`, `CHUNK_SIZE`, or `CHUNK_OVERLAP` in `.env`, your existing database vectors and chunks become incompatible. You do not need to re-upload your PDFs. Use the built-in reindex CLI to reconstruct the text from the database and safely re-chunk/re-embed everything in place.

> **⚠️ WARNING:**
> If you change `EMBED_MODEL`, you **must** first run the Alembic migration to update the database column dimension (e.g., from `vector(1536)` to `vector(768)`). If you skip the migration, the insert will fail.

Run the reindexer after migrating:

```bash
uv run reindex
```
## Known limitations

- **No conversational memory** — each question retrieves and answers independently. Follow-ups like "what about 2024?" won't resolve pronouns.
- **Naive retrieval for broad questions** — "should I invest?" returns whatever ranks highest; ask specific questions for best results.
- **No authentication** — single-user local app.
- **Character-based chunking** — the recursive splitter respects paragraph, sentence, and word boundaries (and fixes PDF hyphenation), but does not use semantic/AI chunking.

## License

MIT