# Portfolio Dashboard — Structured Products Tracking

Tracks 11 structured products with risk metrics, daily valuations, and cash flow projections.

**Stages 1–2 complete:**
- Full schema (PostgreSQL) with products, underlyings, observations, valuations
- 3 real products seeded: UBS autocall, SocGen capital-protected ZC, DB capital-protected note
- Dashboard endpoint (`/api/dashboard`) with calculated distances, status, performance
- React frontend displaying products with traffic-light risk status

---

## Quick Start (Local Dev)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL running locally, OR Supabase account

### Step 1: Clone & setup backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure database

Create `.env` file in the `backend/` directory:

```
DATABASE_URL=postgresql://user:password@localhost:5432/portfolio
DEBUG=false
ENVIRONMENT=development
```

**Option A: Local PostgreSQL**
```bash
createdb portfolio
# (adjust user/password as needed)
```

**Option B: Supabase**
1. Create a free account at https://supabase.com
2. Create a new project
3. Copy the connection string from Settings → Database → URI
4. Paste into `DATABASE_URL` in `.env`

### Step 3: Run migrations & seed

```bash
cd backend
alembic upgrade head
python seed.py
```

Expected output: `✓ Seeded 3 products successfully`

### Step 4: Start backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs on http://localhost:8000

### Step 5: Start frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

Open http://localhost:5173 in browser → you should see a table of 3 products with calculated distances and risk status.

---

## API Endpoint (Stage 2)

**GET /api/dashboard?as_of_date=2025-09-08**

Returns:
```json
{
  "as_of_date": "2025-09-08",
  "products": [
    {
      "id": 1,
      "name": "37% on IREN, Nebius",
      "isin": "CH1566087354",
      "market_value": 984300.0,
      "worst_performance_pct": 71.2,
      "worst_underlying": "IREN Ltd",
      "distance_to_strike_pts": 11.2,
      "distance_to_autocall_pts": -20.8,
      "status": "orange",
      "missing_fields": []
    },
    ...
  ],
  "aggregates": {
    "total_market_value": 2978900.0,
    "product_count": 3
  }
}
```

---

## Test: Validate Stage 2 Calculations

Manual test: IREN at 44.00, Reference Level 61.78, strike 60%.

- **Expected performance:** 44.00 / 61.78 = 71.2%
- **Expected distance to strike:** 71.2 − 60 = 11.2 points
- **Expected distance to autocall (98% level):** 71.2 − 98 = −26.8 points

Verify these numbers appear in the dashboard `/api/dashboard` response or the React table.

---

## Next: Stage 3–7

Stages 3–7 are scaffolded but not yet implemented:
- Stage 3: Observation tracking (mark past observations as paid/missed)
- Stage 4: Entry screen + product creation form
- Stage 5: Funding management & loan tracking
- Stage 6: Cash flow projection & credit limit breach calculation
- Stage 7: User auth & audit log

Each stage is 1–4 hours and depends only on the database schema and stage-2 endpoint.

---

## Deployment (Later)

When you're ready to deploy:

1. Create GitHub repo, push code
2. Create Railway account, connect GitHub repo
3. Set env var `DATABASE_URL` to Supabase connection string
4. Railway auto-builds Docker, deploys to `https://your-app.railway.app`

No ops, no babysitting. Just git push.

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'app'"**
→ Make sure you're in `backend/` directory when running uvicorn.

**"psycopg2.OperationalError: could not connect to server"**
→ Check DATABASE_URL. If using local Postgres, verify server is running: `psql -U postgres` should work.

**Frontend shows "Error: Failed to fetch dashboard"**
→ Check backend is running on :8000. Check browser console for CORS errors.

**"Table 'products' already exists" from seed.py**
→ Data is already seeded. Just refresh the frontend to see it.

---

## Project Structure

```
portfolio-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py            # Database + settings
│   │   ├── models.py            # SQLAlchemy ORM
│   │   ├── main.py              # FastAPI routes
│   │   └── domain/
│   │       ├── __init__.py
│   │       └── portfolio.py      # Business logic (pure functions)
│   ├── alembic/
│   │   ├── env.py
│   │   ├── versions/
│   │   │   ├── 001_initial_schema.py
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── requirements.txt
│   └── seed.py                  # Initialize 3 products
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React app
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── .env.example
└── README.md
```

---

## Questions?

- **Schema**: See `/path/to/PROMPT_FINAL_PORTFOLIO_DASHBOARD.md` §3 for full model spec
- **Calculations**: See `/path/to/domain/portfolio.py` for all metric formulas
- **API**: See `/path/to/PROMPT_FINAL_PORTFOLIO_DASHBOARD.md` §7 for endpoint spec
