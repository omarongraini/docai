


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

### run the app
```bash 
uv run streamlit run app.py
```


### Development

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```
## Known limitations

- **No conversational memory** — each question retrieves and answers
  independently. Follow-ups like "what about 2024?" won't resolve pronouns.
- **Naive retrieval for broad questions** — "should I invest?" returns
  whatever ranks highest; ask specific questions for best results.
- **No streaming for Arabic** — buffered to preserve RTL alignment.
- **No authentication** — single-user local app.
- **Chunking is character-based** — recursive splitter respects paragraph and
  sentence boundaries but has no semantic awareness.

## License

MIT