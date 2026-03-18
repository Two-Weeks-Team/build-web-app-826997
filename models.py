import json
import os
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg://"):
        return raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    return raw_url


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
)

is_sqlite = DATABASE_URL.startswith("sqlite")
is_local = ("localhost" in DATABASE_URL) or ("127.0.0.1" in DATABASE_URL)

connect_args = {}
if is_sqlite:
    connect_args = {"check_same_thread": False}
elif not is_local:
    connect_args = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class MPRecipe(Base):
    __tablename__ = "mp_recipe"

    id = Integer().with_variant(Integer, "sqlite")
    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    name = __import__("sqlalchemy").Column(String(200), nullable=False, unique=True)
    meal_type = __import__("sqlalchemy").Column(String(50), nullable=False)
    tags_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    ingredients_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    prep_minutes = __import__("sqlalchemy").Column(Integer, nullable=False, default=20)
    protein_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=20)
    cost_tier = __import__("sqlalchemy").Column(String(20), nullable=False, default="medium")
    leftover_score = __import__("sqlalchemy").Column(Integer, nullable=False, default=1)


class MPPlan(Base):
    __tablename__ = "mp_plan"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    title = __import__("sqlalchemy").Column(String(200), nullable=False)
    source_query = __import__("sqlalchemy").Column(Text, nullable=False)
    preferences_json = __import__("sqlalchemy").Column(Text, nullable=False, default="{}")
    summary = __import__("sqlalchemy").Column(Text, nullable=False, default="")
    assumptions_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    confidence = __import__("sqlalchemy").Column(String(30), nullable=False, default="medium")
    is_draft = __import__("sqlalchemy").Column(Boolean, nullable=False, default=False)
    grocery_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    prep_notes_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    rebalance_history_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)

    meals = relationship("MPMealSlot", back_populates="plan", cascade="all, delete-orphan")


class MPMealSlot(Base):
    __tablename__ = "mp_meal_slot"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    plan_id = __import__("sqlalchemy").Column(Integer, ForeignKey("mp_plan.id"), nullable=False, index=True)
    day = __import__("sqlalchemy").Column(String(20), nullable=False)
    meal = __import__("sqlalchemy").Column(String(20), nullable=False)
    recipe_name = __import__("sqlalchemy").Column(String(200), nullable=False)
    portions = __import__("sqlalchemy").Column(Integer, nullable=False, default=2)
    prep_effort = __import__("sqlalchemy").Column(String(20), nullable=False, default="medium")
    rationale = __import__("sqlalchemy").Column(Text, nullable=False, default="")
    leftover_portions = __import__("sqlalchemy").Column(Integer, nullable=False, default=0)

    plan = relationship("MPPlan", back_populates="meals")


def to_json(data):
    return json.dumps(data, ensure_ascii=False)


def from_json(text, fallback):
    try:
        return json.loads(text)
    except Exception:
        return fallback
