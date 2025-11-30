from datetime import datetime
import uuid
from typing import Any, Dict

def make_message(from_agent: str, to_agent: str, session_id: str, payload_type: str, payload: Any, confidence: float = 1.0, ttl: int = 30) -> Dict[str, Any]:
    return {
        'message_id': str(uuid.uuid4()),
        'from_agent': from_agent,
        'to_agent': to_agent,
        'timestamp_iso': datetime.utcnow().isoformat() + 'Z',
        'session_id': session_id,
        'payload_type': payload_type,
        'payload': payload,
        'meta': {
            'confidence': confidence,
            'ttl': ttl
        }
    }
