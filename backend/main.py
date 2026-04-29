from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 App starting...")

app = FastAPI(
    title="AI Gift Finder API",
    description="Backend API for the AI-powered baby gift finder",
    version="1.0.0"
)

# ===============================
# STATIC FILES (Frontend)
# ===============================
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"Frontend mounted at /frontend from {frontend_path}")
else:
    logger.warning("Frontend folder not found. Skipping static mount.")

# ===============================
# CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# REQUEST MODEL
# ===============================
class QueryRequest(BaseModel):
    query: str

# ===============================
# SAFE PIPELINE LOADING (IMPORTANT)
# ===============================
pipeline = None

def get_pipeline_safe():
    global pipeline
    if pipeline is None:
        try:
            from .langchain_pipeline import get_pipeline
            pipeline = get_pipeline()
            logger.info("Pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Pipeline loading failed: {e}", exc_info=True)
            pipeline = None
    return pipeline

# ===============================
# ROUTES
# ===============================
@app.get("/")
async def root():
    return {"message": "AI Gift Finder API is running 🚀"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/recommend")
async def recommend(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"Request: {request.query}")

    try:
        pipeline_instance = get_pipeline_safe()

        if pipeline_instance is None:
            raise HTTPException(
                status_code=500,
                detail="AI pipeline failed to load (check API keys or memory limits)"
            )

        response = await pipeline_instance.run(request.query)
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# ===============================
# LOCAL RUN (NOT USED IN RENDER)
# ===============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)