


## First run

### Alembic migration 
Run the command 
```bash
cd chatpdf
uv run alembic init migrations
uv run alembic revision --autogenerate -m "initial schema"
```


run the app 
```bash
uv run streamlit run app.py
```