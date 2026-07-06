from fastapi import FastAPI
from app.api.v1.routes import router
from app.api.v1.identity import router as local_user_router

app = FastAPI(version="0.1.0", title="KeelHQ API v1")

app.include_router(router)
app.include_router(local_user_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", port=8000, reload=True)
