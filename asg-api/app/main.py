from fastapi import FastAPI

from app.api import sessions, scoring, internal, admin, products, quality, wizard

app = FastAPI(
    title="ASG — Authenticity Score Generator",
    version="0.1.0",
    description="B2B API for luxury goods authentication using vision AI",
)

app.include_router(sessions.router)
app.include_router(scoring.router)
app.include_router(internal.router)
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(quality.router)
app.include_router(wizard.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
