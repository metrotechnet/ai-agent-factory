from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class Decision(str, Enum):
    ALLOW = "allow"
    REFUSE = "refuse"
    ALLOW_WITH_CONSTRAINTS = "allow_with_constraints"


@dataclass
class RefusalResult:
    decision: Decision
    reasons: List[str]
    matched_patterns: List[str]
    response: Optional[str] = None
    # You can log this for auditability:
    metadata: Optional[Dict[str, Any]] = None


# --- Refusal templates (FR) ---
REFUSAL_TEMPLATE_FR = """Je peux fournir de l’information générale à visée éducative,
mais je ne peux pas donner de recommandations, de chiffres cibles, d’exemples de menus,
ni répondre à des situations personnelles ou cliniques.

Pour ce type de question, consulte un professionnel de la santé qualifié (ou un diététiste-nutritionniste).
Ne modifie pas un traitement sans avis médical. En cas d’urgence, contacte les services d’urgence.
"""

REFUSAL_MINOR_FR = """Je peux fournir de l’information générale à visée éducative,
mais je ne peux pas répondre à des demandes liées à la perte de poids ou à des objectifs corporels chez les mineurs.

Pour un accompagnement sécuritaire, parle à un parent/tuteur et consulte un professionnel de la santé qualifié.
En cas d’urgence, contacte les services d’urgence.
"""

REFUSAL_MEDICATION_FR = """Je ne peux pas répondre aux questions sur la compatibilité d’un médicament avec un régime, un jeûne,
un supplément ou un changement d’alimentation, car cela relève d’un avis clinique.

Consulte un professionnel de la santé qualifié (médecin ou pharmacien) pour une réponse adaptée à ta situation.
Ne modifie pas ton traitement sans avis médical.
"""


# --- Pattern library ---
# Keep these patterns simple and explainable (auditable).
PATTERNS = {
    # Clinical conditions (examples, extend as needed)
    "clinical_condition": [
        r"\bdiab[eè]te\b", r"\bhypertension\b", r"\bcholest[eé]rol\b", r"\binsuffisance r[eé]nale\b",
        r"\bmaladie\b", r"\bcancer\b", r"\bceliaqu(e|ie)\b", r"\ballergie\b", r"\bintol[eé]rance\b",
        r"\banxi[eé]t[eé]\b", r"\bd[eé]pression\b", r"\bTCA\b", r"\btrouble(s)? alimentaire(s)?\b",
        r"\bgrossesse\b", r"\ballaitement\b"
    ],
    # Medications
    "medication": [
        r"\bmetformin(e)?\b", r"\binsuline\b", r"\bstatine(s)?\b", r"\bantid[eé]presseur(s)?\b",
        r"\bm[eé]dicament(s)?\b", r"\btraitement\b", r"\bposologie\b"
    ],
    # Supplements
    # "supplement": [
    #     r"\bsuppl[eé]ment(s)?\b", r"\bvitamine\b", r"\bmin[eé]ral\b", r"\bmagnesium\b", r"\bcr[eé]atine\b",
    #     r"\bomega[- ]?3\b", r"\bprobiotique(s)?\b"
    # ],
    # Personal targets / coaching
    "personalized_request": [
        r"\bcombien\b.*\b(calorie|kcal|protéine|glucide|lipide)\b",
        r"\b(pour moi|dans mon cas|à mon sujet)\b",
        r"\bje (fais|pèse)\b", r"\bj[' ]ai \d{1,3}\s*ans\b",
        r"\bobjectif\b", r"\bperdre du poids\b", r"\bmaigrir\b", r"\bs[eé]cher\b"
    ],
    # Meal plan requests
    "meal_plan": [
        r"\bmenu\b", r"\bplan alimentaire\b", r"\bplan de repas\b", r"\bexemple de repas\b",
        r"\bquoi manger\b", r"\bpetit[- ]d[eé]jeuner\b", r"\bd[eé]jeuner\b", r"\bd[iî]ner\b",
        r"\bcollation(s)?\b"
    ],
    # High-risk thresholds / numbers (optional; if you want to refuse any numeric diet target)
    "numeric_targets": [
        r"\b\d+\s*(kcal|calories|mg|g\/kg|g)\b",
        r"\b\d{2,4}\s*(kcal|calories)\b"
    ],
    # Minors
    "minor": [
        r"\bj[' ]ai\s*(1[0-7])\s*ans\b",
        r"\b(je suis|j'ai)\s*(1[0-7])\b"
    ],
    # Emergency / self-harm / not eating (nutrition context can still be urgent)
    "possible_emergency": [
        r"\b(j[' ]ai arr[eê]t[eé] de manger|je ne mange plus)\b",
        r"\b(malaise|[eé]vanoui|vertige(s)?)\b",
        r"\b(douleur(s)? intense(s)?|saignement)\b"
    ],
}


def _match_patterns(text: str, patterns: List[str]) -> List[str]:
    hits = []
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.append(pat)
    return hits


def refusal_engine_fr(question: str, history_text: str = "", context: str = "") -> RefusalResult:
    """
    Decide whether to refuse before calling the LLM.
    - question/history/context are used ONLY for risk detection (not for generating advice).
    """
    combined = f"{question}\n{history_text}\n{context}".strip()

    matched: Dict[str, List[str]] = {}
    reasons: List[str] = []

    # Evaluate categories
    for category, pats in PATTERNS.items():
        hits = _match_patterns(combined, pats)
        if hits:
            matched[category] = hits

    # Decision logic (keep it deterministic and auditable)
    if "medication" in matched:
        return RefusalResult(
            decision=Decision.REFUSE,
            reasons=["Medication / clinical compatibility question"],
            matched_patterns=matched["medication"],
            response=REFUSAL_MEDICATION_FR,
            metadata={"matched_categories": list(matched.keys())}
        )

    if "minor" in matched and ("personalized_request" in matched or "meal_plan" in matched):
        return RefusalResult(
            decision=Decision.REFUSE,
            reasons=["Minor + weight/plan/personalized request"],
            matched_patterns=matched["minor"] + matched.get("personalized_request", []) + matched.get("meal_plan", []),
            response=REFUSAL_MINOR_FR,
            metadata={"matched_categories": list(matched.keys())}
        )

    if "possible_emergency" in matched:
        # You can have a separate emergency template if you prefer
        return RefusalResult(
            decision=Decision.REFUSE,
            reasons=["Possible emergency / urgent situation"],
            matched_patterns=matched["possible_emergency"],
            response=REFUSAL_TEMPLATE_FR,
            metadata={"matched_categories": list(matched.keys())}
        )

    # Clinical conditions (diabetes, renal, etc.) => refuse to avoid clinical advice
    if "clinical_condition" in matched:
        return RefusalResult(
            decision=Decision.REFUSE,
            reasons=["Clinical condition mentioned"],
            matched_patterns=matched["clinical_condition"],
            response=REFUSAL_TEMPLATE_FR,
            metadata={"matched_categories": list(matched.keys())}
        )

    # Meal plans or personal targets => refuse
    if "meal_plan" in matched:
        return RefusalResult(
            decision=Decision.REFUSE,
            reasons=["Meal plan request"],
            matched_patterns=matched["meal_plan"],
            response=REFUSAL_TEMPLATE_FR,
            metadata={"matched_categories": list(matched.keys())}
        )

    if "personalized_request" in matched:
        return RefusalResult(
            decision=Decision.REFUSE,
            reasons=["Personalized recommendation request"],
            matched_patterns=matched["personalized_request"],
            response=REFUSAL_TEMPLATE_FR,
            metadata={"matched_categories": list(matched.keys())}
        )

    # Supplements are tricky: your prompt says never recommend specific supplements/dosages.
    # Here we choose ALLOW_WITH_CONSTRAINTS (let LLM explain general info but avoid recommendation).
    if "supplement" in matched:
        return RefusalResult(
            decision=Decision.ALLOW_WITH_CONSTRAINTS,
            reasons=["Supplement mentioned (allow general info only)"],
            matched_patterns=matched["supplement"],
            response=None,
            metadata={"matched_categories": list(matched.keys())}
        )

    # Numeric targets in the user text (optional policy choice)
    if "numeric_targets" in matched:
        return RefusalResult(
            decision=Decision.ALLOW_WITH_CONSTRAINTS,
            reasons=["Numeric targets mentioned (avoid numbers in reply)"],
            matched_patterns=matched["numeric_targets"],
            response=None,
            metadata={"matched_categories": list(matched.keys())}
        )

    return RefusalResult(
        decision=Decision.ALLOW,
        reasons=[],
        matched_patterns=[],
        response=None,
        metadata={"matched_categories": list(matched.keys())}
    )


# Example integration point:
def validate_user_query(question: str, context: str, history_text: str, llm_call_fn):
    """
    llm_call_fn should be your function that calls OpenAI with your system prompt.
    """
    risk = refusal_engine_fr(question=question, history_text=history_text, context=context)

    # If refuse, return template immediately (no LLM call)
    if risk.decision == Decision.REFUSE:
        return {
            "decision": risk.decision.value,
            "reasons": risk.reasons,
            "answer": risk.response,
            "audit": asdict(risk)
        }

    # If allow_with_constraints, call LLM but tighten constraints
    system_suffix = ""
    if risk.decision == Decision.ALLOW_WITH_CONSTRAINTS:
        system_suffix = (
            "\n\nADDITIONAL CONSTRAINTS:\n"
            "- Do not recommend any specific product/supplement/brand.\n"
            "- Do not provide dosages or numeric targets.\n"
            "- Keep it general and educational.\n"
        )


    return {
        "decision": risk.decision.value,
        "reasons": risk.reasons,
        "audit": asdict(risk)
    }
