from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from models import Base, SessionLocal, engine
from routes import router


app = FastAPI(title="Build Web App API", version="1.0.0")

Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    html = """
    <html>
      <head>
        <title>Build Web App - Meal Prep Planning API</title>
        <style>
          body { font-family: Arial, sans-serif; background: #0f1115; color: #e8e8e8; margin: 0; padding: 24px; }
          .card { background: #171a21; border: 1px solid #2a2f3a; border-radius: 12px; padding: 20px; max-width: 980px; margin: 0 auto; }
          h1 { margin-top: 0; color: #9fe870; }
          h2 { color: #ffb86b; }
          code { background: #222734; padding: 2px 6px; border-radius: 6px; }
          a { color: #79c0ff; text-decoration: none; }
          ul { line-height: 1.8; }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Build Web App API</h1>
          <p>Turn a rough meal-prep idea into a practical weekly plan, grocery list, and prep-ready workflow in one pass.</p>

          <h2>Endpoints</h2>
          <ul>
            <li><code>GET /health</code> - Service health check</li>
            <li><code>GET /seed</code> - Seed demo recipe data</li>
            <li><code>POST /plan</code> and <code>POST /api/plan</code> - Build weekly meal plan from messy prompt</li>
            <li><code>POST /insights</code> and <code>POST /api/insights</code> - AI coaching insights for current selection</li>
            <li><code>POST /rebalance</code> - Rebalance leftovers, grocery and prep timing after meal move</li>
            <li><code>POST /substitute</code> - Smart meal substitution respecting constraints</li>
            <li><code>GET /plans</code> and <code>GET /api/plans</code> - Saved prep batch pantry shelf</li>
          </ul>

          <h2>Tech Stack</h2>
          <ul>
            <li>FastAPI + SQLAlchemy (PostgreSQL-ready, SQLite fallback)</li>
            <li>DigitalOcean Serverless Inference via <code>httpx</code></li>
            <li>Model: <code>anthropic-claude-4.6-sonnet</code> (configurable)</li>
          </ul>

          <p><a href="/docs">OpenAPI Docs</a> | <a href="/redoc">ReDoc</a></p>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.on_event("startup")
def startup_seed():
    db = SessionLocal()
    try:
        from models import MPRecipe, to_json

        if db.query(MPRecipe).count() == 0:
            db.add_all([
                MPRecipe(name="Chicken Rice Bowls", meal_type="lunch", tags_json=to_json(["high protein", "budget"]), ingredients_json=to_json(["chicken", "rice", "broccoli"]), prep_minutes=30, protein_g=42, cost_tier="low", leftover_score=3),
                MPRecipe(name="Turkey Chili", meal_type="dinner", tags_json=to_json(["batch", "budget"]), ingredients_json=to_json(["turkey", "beans", "tomato"]), prep_minutes=40, protein_g=38, cost_tier="low", leftover_score=4),
                MPRecipe(name="Overnight Oats", meal_type="breakfast", tags_json=to_json(["quick", "prep ahead"]), ingredients_json=to_json(["oats", "milk", "chia"]), prep_minutes=10, protein_g=18, cost_tier="low", leftover_score=1),
            ])
            db.commit()
    finally:
        db.close()
