import uuid
from typing import Dict, Any
from project.core.a2a_protocol import make_message

class Planner:
    """Planner: parses user input, extracts intent, location, urgency, and builds a plan JSON.
    Deterministic rules for beginner-friendly prototype.
    """

    INTENT_KEYWORDS = {
        "shelter": ["shelter", "safe", "housing", "stay"],
        "food": ["food", "meal", "eat", "distribution"],
        "medical": ["medical", "hospital", "injury", "sick", "triage"],
        "evacuation": ["evacuate", "evacuation", "route", "exit"],
        "info": ["info", "information", "help"]
    }

    RISK_PRIORITY = {
        "medical": 1,
        "evacuation": 2,
        "shelter": 3,
        "food": 4,
        "info": 5
    }

    def __init__(self):
        pass

    def classify_intent(self, text: str) -> str:
        t = text.lower()
        scores = {k: 0 for k in self.INTENT_KEYWORDS}
        for intent, kws in self.INTENT_KEYWORDS.items():
            for kw in kws:
                if kw in t:
                    scores[intent] += 1
        # choose highest score; tie-breaker by risk priority
        best = max(scores.items(), key=lambda kv: (kv[1], -self.RISK_PRIORITY[kv[0]]))
        if best[1] == 0:
            return "info"
        return best[0]

    def extract_location(self, text: str) -> Dict[str, Any]:
        # Very simple heuristic: look for lat/lon pair in the text
        # or city names — for prototype, check for 'springfield'
        loc = {"city": None, "lat": None, "lon": None}
        if "springfield" in text.lower():
            loc.update({"city": "Springfield", "lat": 40.7128, "lon": -74.0060})
        return loc

    def build_plan(self, user_input: str, session_memory: Dict[str, Any]) -> Dict[str, Any]:
        intent = self.classify_intent(user_input)
        loc = self.extract_location(user_input)
        urgency = "high" if intent == "medical" else "normal"
        max_results = 5
        filters = {}
        # incorporate accessibility from session memory
        if session_memory and session_memory.get("accessibility_needs"):
            filters["accessibility"] = session_memory.get("accessibility_needs")
        plan = {
            "plan_id": str(uuid.uuid4()),
            "intent": intent,
            "query_terms": [intent],
            "location": loc,
            "urgency": urgency,
            "filters": filters,
            "max_results": max_results,
            "output_format": "short_list"
        }
        msg = make_message(from_agent="planner", to_agent="worker", session_id=session_memory.get("session_id") if session_memory else None, payload_type="plan", payload=plan)
        return {"plan": plan, "message": msg}
