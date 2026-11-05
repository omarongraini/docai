


## Quick start

### clone and install deps
```bash
git clone <repo>
cd docai
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

### run the CV eval app
```bash 
uv run streamlit run app_cv.py
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
> If you change `EMBED_MODEL`, you **must** first run the Alembic migration to update the database column dimension (e.g., from `vector(first_dimention)` to `vector(second_dimention)`). If you skip the migration, the insert will fail.

Run the reindexer after migrating or in case the embed model changes:

```bash
uv run reindex
```
## Known limitations

- **No conversational memory** — each question retrieves and answers independently. Follow-ups like "what about 2024?" won't resolve pronouns.

## License

MIT