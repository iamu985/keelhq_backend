from fastapi import FastAPI
from app.api.v1.routes import router

app = FastAPI(version="0.1.0", title="KeelHQ API v1")

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", port=8000, reload=True)
