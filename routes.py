from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_service import generate_insights, generate_plan_artifacts, parse_messy_prompt
from models import MPMealSlot, MPPlan, MPRecipe, SessionLocal, from_json, to_json


router = APIRouter()


class PlanRequest(BaseModel):
    query: str
    preferences: str = ""


class InsightsRequest(BaseModel):
    selection: str
    context: str = ""


class RebalanceRequest(BaseModel):
    plan_id: int
    from_day: str
    to_day: str
    meal: str


class SubstituteRequest(BaseModel):
    plan_id: int
    day: str
    meal: str
    avoid_ingredient: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/seed")
def seed_data(db: Session = Depends(get_db)):
    if db.query(MPRecipe).count() > 0:
        return {"status": "ok", "message": "Seed already present"}

    recipes = [
        MPRecipe(name="Chicken Rice Bowls", meal_type="lunch", tags_json=to_json(["high protein", "budget"]), ingredients_json=to_json(["chicken", "rice", "broccoli"]), prep_minutes=30, protein_g=42, cost_tier="low", leftover_score=3),
        MPRecipe(name="Turkey Chili", meal_type="dinner", tags_json=to_json(["batch", "budget"]), ingredients_json=to_json(["turkey", "beans", "tomato"]), prep_minutes=40, protein_g=38, cost_tier="low", leftover_score=4),
        MPRecipe(name="Tofu Stir-Fry", meal_type="dinner", tags_json=to_json(["vegetarian", "quick"]), ingredients_json=to_json(["tofu", "mixed vegetables", "soy sauce"]), prep_minutes=25, protein_g=24, cost_tier="low", leftover_score=2),
        MPRecipe(name="Overnight Oats", meal_type="breakfast", tags_json=to_json(["quick", "prep ahead"]), ingredients_json=to_json(["oats", "milk", "chia"]), prep_minutes=10, protein_g=18, cost_tier="low", leftover_score=1),
        MPRecipe(name="Salmon Bowls", meal_type="dinner", tags_json=to_json(["high protein"]), ingredients_json=to_json(["salmon", "rice", "spinach"]), prep_minutes=30, protein_g=35, cost_tier="medium", leftover_score=2),
    ]
    db.add_all(recipes)
    db.commit()
    return {"status": "ok", "message": "Seed data created", "count": len(recipes)}


@router.post("/plan")
@router.post("/plan")
async def create_plan(payload: PlanRequest, db: Session = Depends(get_db)):
    structured = await parse_messy_prompt(payload.query, payload.preferences)

    fallback_assumptions = [
        "Assumed 2 servings per main meal.",
        "Assumed one shared weekly grocery run.",
        "Assumed weekday lunches are portable.",
    ]

    if structured.get("fallback"):
        structured = {
            "goals": ["high protein", "budget-friendly", "simple prep"],
            "servings": 2,
            "budget": "low",
            "schedule": "weeknight-friendly",
            "dietary_constraints": ["no peanuts" if "peanut" in payload.query.lower() else "none"],
            "assumptions": fallback_assumptions,
            "confidence": "low",
        }

    artifacts = await generate_plan_artifacts(structured)

    if artifacts.get("fallback"):
        items = [
            {"day": "Mon", "breakfast": "Overnight Oats", "lunch": "Chicken Rice Bowls", "dinner": "Turkey Chili"},
            {"day": "Tue", "breakfast": "Greek Yogurt Cup", "lunch": "Chicken Rice Bowls", "dinner": "Tofu Stir-Fry"},
            {"day": "Wed", "breakfast": "Egg Muffins", "lunch": "Turkey Chili", "dinner": "Salmon Bowls"},
            {"day": "Thu", "breakfast": "Overnight Oats", "lunch": "Chicken Rice Bowls", "dinner": "Sheet-Pan Fajitas"},
            {"day": "Fri", "breakfast": "Cottage Cheese Box", "lunch": "Chickpea Wrap", "dinner": "Pasta Bake"},
            {"day": "Sat", "breakfast": "Egg Muffins", "lunch": "Leftover Bowls", "dinner": "Turkey Chili"},
            {"day": "Sun", "breakfast": "Overnight Oats", "lunch": "Rotisserie Salad", "dinner": "Lentil Curry"},
        ]
        artifacts = {
            "summary": "Assumption-aware weekly meal prep draft generated from incomplete input.",
            "items": items,
            "score": 78,
            "grocery_list": [
                {"item": "chicken breast", "quantity": "1.5 kg"},
                {"item": "rice", "quantity": "2 kg"},
                {"item": "broccoli", "quantity": "6 cups"},
                {"item": "beans", "quantity": "5 cans"},
            ],
            "prep_batch": [
                "Cook rice in one batch.",
                "Roast broccoli and fajita vegetables.",
                "Prepare 6 lunch containers.",
            ],
            "meal_prep_notes": ["Use chili leftovers for Wed lunch.", "Freeze one chili portion for weekend."],
            "assumptions": structured.get("assumptions", fallback_assumptions),
            "confidence": "low",
        }

    plan = MPPlan(
        title=f"Meal Prep Plan - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        source_query=payload.query,
        preferences_json=to_json({"preferences": payload.preferences}),
        summary=artifacts.get("summary", "Weekly meal prep plan"),
        assumptions_json=to_json(artifacts.get("assumptions", [])),
        confidence=artifacts.get("confidence", "medium"),
        is_draft=artifacts.get("confidence", "medium") == "low",
        grocery_json=to_json(artifacts.get("grocery_list", [])),
        prep_notes_json=to_json(artifacts.get("meal_prep_notes", [])),
        rebalance_history_json=to_json([]),
    )
    db.add(plan)
    db.flush()

    for day_entry in artifacts.get("items", []):
        for meal_name in ["breakfast", "lunch", "dinner"]:
            recipe = str(day_entry.get(meal_name, "Chef's Choice"))
            slot = MPMealSlot(
                plan_id=plan.id,
                day=str(day_entry.get("day", "Mon")),
                meal=meal_name,
                recipe_name=recipe,
                portions=2,
                prep_effort="medium",
                rationale="Chosen for protein, prep speed, and leftover utility.",
                leftover_portions=1 if meal_name == "dinner" else 0,
            )
            db.add(slot)

    db.commit()

    return {
        "summary": artifacts.get("summary", "Weekly meal plan built."),
        "items": artifacts.get("items", []),
        "score": artifacts.get("score", 75),
        "plan_id": plan.id,
        "assumptions": artifacts.get("assumptions", []),
        "confidence": artifacts.get("confidence", "medium"),
    }


@router.post("/insights")
@router.post("/insights")
async def post_insights(payload: InsightsRequest):
    result = await generate_insights(payload.selection, payload.context)
    if result.get("fallback"):
        return {
            "insights": [
                "Your dinners carry most leftover potential; moving one impacts lunch coverage.",
                "Protein target is strongest on Tue-Thu in this draft.",
            ],
            "next_actions": [
                "Swap one quick dinner into Monday to reduce prep stress.",
                "Consolidate overlapping produce into one roast batch.",
            ],
            "highlights": ["Assumption-aware draft", "Grocery basket optimized for one weekly run"],
        }
    return {
        "insights": result.get("insights", []),
        "next_actions": result.get("next_actions", []),
        "highlights": result.get("highlights", []),
    }


@router.post("/rebalance")
def rebalance_plan(payload: RebalanceRequest, db: Session = Depends(get_db)):
    slots = db.query(MPMealSlot).filter(MPMealSlot.plan_id == payload.plan_id, MPMealSlot.meal == payload.meal).all()
    from_slot = next((s for s in slots if s.day == payload.from_day), None)
    to_slot = next((s for s in slots if s.day == payload.to_day), None)

    if not from_slot or not to_slot:
        return {"status": "error", "message": "Could not find meal slots for rebalance."}

    from_slot.day, to_slot.day = to_slot.day, from_slot.day

    all_slots = db.query(MPMealSlot).filter(MPMealSlot.plan_id == payload.plan_id).all()
    grocery_multiplier = max(1, len([s for s in all_slots if s.meal == "dinner"]) // 3)
    leftovers_total = sum([s.leftover_portions for s in all_slots])

    plan = db.query(MPPlan).filter(MPPlan.id == payload.plan_id).first()
    history = from_json(plan.rebalance_history_json, []) if plan else []
    history.append(
        {
            "event": "swap",
            "from_day": payload.from_day,
            "to_day": payload.to_day,
            "meal": payload.meal,
            "leftovers_total": leftovers_total,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    if plan:
        plan.rebalance_history_json = to_json(history)

    db.commit()

    return {
        "status": "ok",
        "leftovers_total": leftovers_total,
        "grocery_adjustments": [
            {"item": "rice", "delta": f"+{grocery_multiplier} cups"},
            {"item": "mixed vegetables", "delta": "+2 cups"},
        ],
        "prep_timing": [
            "Move batch roast to earlier in the week.",
            "Pack two lunch containers right after swapped dinner.",
        ],
        "rebalance_events": len(history),
    }


@router.post("/substitute")
def substitute_meal(payload: SubstituteRequest, db: Session = Depends(get_db)):
    slot = (
        db.query(MPMealSlot)
        .filter(MPMealSlot.plan_id == payload.plan_id, MPMealSlot.day == payload.day, MPMealSlot.meal == payload.meal)
        .first()
    )
    if not slot:
        return {"status": "error", "message": "Meal slot not found."}

    recipes = db.query(MPRecipe).all()
    candidates = []
    for r in recipes:
        ingredients = from_json(r.ingredients_json, [])
        if payload.avoid_ingredient and any(payload.avoid_ingredient.lower() in str(i).lower() for i in ingredients):
            continue
        candidates.append(r)

    candidates = sorted(candidates, key=lambda x: (-x.protein_g, x.prep_minutes))
    if not candidates:
        return {"status": "error", "message": "No substitution candidates available."}

    replacement = candidates[0]
    old = slot.recipe_name
    slot.recipe_name = replacement.name
    slot.prep_effort = "low" if replacement.prep_minutes <= 20 else "medium"
    slot.rationale = f"Substituted for protein/time fit. Avoided: {payload.avoid_ingredient or 'none'}."

    db.commit()

    return {
        "status": "ok",
        "day": payload.day,
        "meal": payload.meal,
        "previous_recipe": old,
        "replacement_recipe": replacement.name,
        "replacement_meta": {
            "protein_g": replacement.protein_g,
            "prep_minutes": replacement.prep_minutes,
            "cost_tier": replacement.cost_tier,
        },
    }


@router.get("/plans")
@router.get("/plans")
def list_saved_plans(db: Session = Depends(get_db)):
    plans = db.query(MPPlan).order_by(MPPlan.created_at.desc()).limit(20).all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "summary": p.summary,
            "confidence": p.confidence,
            "is_draft": p.is_draft,
            "created_at": p.created_at.isoformat(),
            "assumptions": from_json(p.assumptions_json, []),
            "grocery_list": from_json(p.grocery_json, []),
            "meal_prep_notes": from_json(p.prep_notes_json, []),
        }
        for p in plans
    ]
