from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.v1.identity import router as identity_router
from app.api.v1.routes import router as api_router
from app.core.lifespan import lifespan

app = FastAPI(version="0.1.0", title="KeelHQ API v1", lifespan=lifespan)

app.include_router(api_router)
app.include_router(identity_router)

register_exception_handlers(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", port=8000, reload=True)
