from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from project.main_agent import MainAgent

app = FastAPI()
agent = MainAgent()

class Request(BaseModel):
    text: str
    session_id: str = None

@app.post('/query')
def query(req: Request):
    try:
        out = agent.handle_message(req.text, session_id=req.session_id)
        return {"response": out['response'], "session_id": out['session_id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
