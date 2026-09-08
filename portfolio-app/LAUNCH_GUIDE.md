# Launch Guide — Portfolio Dashboard

## What you have

✅ **Complete backend** (Stages 1–2):
- PostgreSQL schema with 6 core tables
- 3 real products seeded (UBS, SocGen, Deutsche Bank)
- Endpoint `/api/dashboard` that calculates all metrics
- Pure business logic in `domain/portfolio.py`

✅ **Working frontend** (Stage 2):
- React app that calls `/api/dashboard`
- Table showing products, performance, distances, status
- Styled with color-coded risk status

✅ **Database agnostic**:
- SQLAlchemy works with PostgreSQL, MySQL, SQLite (for local testing)
- Alembic migrations ready
- Supabase-ready connection

---

## Launch (5 minutes)

### Terminal 1: Backend

```bash
cd portfolio-app/backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate      # macOS/Linux
# or
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env (copy from .env.example in root)
# If using local SQLite (easiest for testing):
echo "DATABASE_URL=sqlite:///portfolio.db" > .env

# Alternative: if you want PostgreSQL locally:
# echo "DATABASE_URL=postgresql://postgres:password@localhost/portfolio" > .env

# Run migrations
alembic upgrade head

# Seed 3 products
python seed.py

# Start backend (runs on :8000)
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Terminal 2: Frontend

```bash
cd portfolio-app/frontend

# Install Node packages
npm install

# Start dev server (runs on :5173, proxies /api to backend)
npm run dev
```

You should see:
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Terminal 3: Open browser

Open **http://localhost:5173** in your browser.

You should see:
- Dashboard title with today's date
- Aggregates box showing total market value
- Table with 3 products (UBS IREN/Nebius, SocGen ZC, DB SOFR note)
- Each row shows: name, market value, performance %, distances, status

---

## Test the Dashboard

**Quick validation** that Stage 2 is working:

1. Look at the **"37% on IREN, Nebius"** row (UBS product)
2. Spot is manually set to **44.00**, Reference Level is **61.78**, strike is **60%**
3. You should see:
   - **Worst Perf %:** 71.2 (= 44.00 / 61.78 × 100)
   - **To Strike:** 11.2 pts (= 71.2 − 60)
   - **To Autocall:** −20.8 pts (= 71.2 − 98)
   - **Status:** orange (< 15 points to strike)

If these numbers match, **the engine is working correctly.**

---

## What's next?

**Stages 3–7 (future):**

Once you're happy with this working:
1. **Stage 3** — Observation screen: mark past observations as paid/missed
2. **Stage 4** — Create product form + upload term sheet
3. **Stage 5** — Funding management: cost-of-funds, loan tranches
4. **Stage 6** — Cash flow projection
5. **Stage 7** — User auth + audit log

Each stage adds one feature and is 1–4 hours of work.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: app` | Make sure you're in `backend/` directory when running uvicorn |
| `No such table: products` | Run `alembic upgrade head` and `python seed.py` |
| Frontend shows "Error" | Check backend is running on `:8000`. Open http://localhost:8000/api/dashboard to test |
| Can't connect to database | Check `DATABASE_URL` in `.env`. If using local SQLite, file will auto-create |

---

## Deployment (when ready)

1. Create GitHub repo
2. Push code
3. Sign up for Railway or Render
4. Connect GitHub repo
5. Set `DATABASE_URL` to Supabase PostgreSQL connection string
6. Deploy

Done. One command: `git push` triggers auto-build and deploy.

---

## Questions?

- **Code structure?** → See `README.md` in `portfolio-app/`
- **Spec & full API?** → See `PROMPT_FINAL_PORTFOLIO_DASHBOARD.md`
- **Business logic?** → See `backend/app/domain/portfolio.py`
- **Database schema?** → See `backend/alembic/versions/001_initial_schema.py`
