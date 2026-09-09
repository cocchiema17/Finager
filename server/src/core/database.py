from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from src.core.config import settings

# Engine di connessione al database
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Impostalo su True se vuoi loggare ogni singola query SQL
    pool_pre_ping=True,  # Verifica che la connessione sia ancora viva prima di usarla
)

# Session factory per creare nuove sessioni DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe Base da cui erediteranno tutti i modelli SQLAlchemy
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency per fornire una sessione DB per ogni richiesta HTTP."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()