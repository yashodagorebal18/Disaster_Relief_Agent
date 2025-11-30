import uuid
import time
from typing import Dict, Any

class SessionMemoryStore:
    def __init__(self, ttl_seconds: int = 60*60*24):
        self.store = {}
        self.ttl = ttl_seconds

    def create_session(self, initial: Dict[str, Any] = None) -> Dict[str, Any]:
        sid = str(uuid.uuid4())
        now = time.time()
        data = initial.copy() if initial else {}
        data.update({"session_id": sid, "created_at": now, "last_seen": now})
        self.store[sid] = data
        return data

    def get_session(self, session_id: str) -> Dict[str, Any]:
        s = self.store.get(session_id)
        if not s:
            return None
        if time.time() - s.get('last_seen',0) > self.ttl:
            del self.store[session_id]
            return None
        s['last_seen'] = time.time()
        return s

    def update_session(self, session_id: str, data: Dict[str, Any]):
        s = self.store.get(session_id)
        if not s:
            return None
        s.update(data)
        s['last_seen'] = time.time()
        return s

    def delete_session(self, session_id: str):
        if session_id in self.store:
            del self.store[session_id]
