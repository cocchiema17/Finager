from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
import src.models  # Importa i modelli per registrare le tabelle nel database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inizializza le tabelle all'avvio dell'applicazione se non presenti
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",
)

# Middleware CORS (come avevi in app.use("*", cors(...)) su Express)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint base per verificare lo stato del server."""
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}