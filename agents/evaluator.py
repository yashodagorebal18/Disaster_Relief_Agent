from typing import Dict, Any
from project.tools.tools import verify_source
from project.core.a2a_protocol import make_message
import uuid

class Evaluator:
    def __init__(self):
        pass

    def evaluate(self, candidates_payload: Dict[str, Any]) -> Dict[str, Any]:
        candidates = candidates_payload.get('candidates', [])
        issues = []
        accepted = True
        confidence = 1.0
        final_list = []
        for c in candidates:
            rec = c.get('resource', {})
            # Basic checks: no hallucinated blank addresses, verification status
            if not rec.get('address'):
                issues.append(f"Missing address for {rec.get('name')}")
                continue
            if not c.get('is_verified'):
                # include but mark as unverified and lower confidence
                c['note'] = 'unverified'
                confidence -= 0.1
            final_list.append(c)
        if len(final_list) == 0:
            accepted = False
            confidence = 0.2
            issues.append('No verified resources found')
        # safety check: if any resource claims medical and not verified -> escalate
        for c in final_list:
            if rec.get('type','').lower() == 'medical' and not c.get('is_verified'):
                accepted = False
                issues.append('Medical resource not verified')
        evaluation = {
            'evaluation_id': str(uuid.uuid4()),
            'accepted': accepted,
            'confidence': max(0.0, confidence),
            'issues': issues,
            'final_list': final_list
        }
        msg = make_message(from_agent='evaluator', to_agent='ui', session_id=None, payload_type='evaluation', payload=evaluation)
        return {'evaluation': evaluation, 'message': msg}
