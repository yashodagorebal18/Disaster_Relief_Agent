from typing import Dict, Any, List
from project.tools.tools import geocode_location, search_resources, summarize_resource, verify_source, check_recency
from project.core.a2a_protocol import make_message

class Worker:
    def __init__(self):
        pass

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        # geocode
        loc = geocode_location(plan.get('location', {}))
        candidates = search_resources(plan.get('query_terms', []), loc, max_results=plan.get('max_results',5), filters=plan.get('filters'))
        # enrich candidate records
        enriched = []
        for c in candidates:
            rec = c['record']
            verified = c.get('verified_by')
            is_verified = verify_source(verified) if verified else False
            recent = check_recency(c.get('last_updated', ''), threshold_days=365)
            summary = summarize_resource(c)
            enriched.append({
                'resource': rec,
                'summary': summary,
                'distance_km': c.get('distance_km'),
                'is_verified': is_verified,
                'recent': recent
            })
        payload = {
            'plan_id': plan.get('plan_id'),
            'candidates': enriched,
            'query_location': loc
        }
        msg = make_message(from_agent='worker', to_agent='evaluator', session_id=None, payload_type='candidates', payload=payload)
        return {'payload': payload, 'message': msg}
