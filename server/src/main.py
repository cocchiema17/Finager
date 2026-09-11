from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.database import Base, engine
import src.models  # Assicura che i modelli vengano registrati nei metadati di Base
from src.controllers.auth_controller import router as auth_router
from src.controllers.space_controller import router as space_router
from src.controllers.category_controller import router as category_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inizializza le tabelle all'avvio dell'applicazione se non presenti
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrazione delle rotte dei controller
app.include_router(auth_router)
app.include_router(space_router)
app.include_router(category_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}