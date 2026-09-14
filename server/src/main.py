from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.database import Base, engine
from src.core.mongo import connect_to_mongo, close_mongo_connection, mongo_manager
import src.models  # Assicura che i modelli vengano registrati nei metadati di Base

# Import dei router dei controller
from src.controllers.auth_controller import router as auth_router
from src.controllers.space_controller import router as space_router
from src.controllers.category_controller import router as category_router
from src.controllers.transaction_controller import router as transaction_router
from src.controllers.charts_controller import router as charts_router
from src.controllers.report_controller import router as report_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inizializza le tabelle all'avvio dell'applicazione se non presenti
    Base.metadata.create_all(bind=engine)
    await connect_to_mongo()
    yield
    await close_mongo_connection()


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
app.include_router(transaction_router)
app.include_router(charts_router)
app.include_router(report_router)

@app.get("/health", tags=["Health"])
async def health_check():
    mongo_status = "connected" if mongo_manager.client is not None else "disconnected"
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "databases": {
            "postgres": "connected",
            "mongodb": mongo_status,
        },
    }