from project.agents.planner import Planner
from project.agents.worker import Worker
from project.agents.evaluator import Evaluator
from project.memory.session_memory import SessionMemoryStore
from project.core.observability import log_event

class MainAgent:
    def __init__(self):
        self.planner = Planner()
        self.worker = Worker()
        self.evaluator = Evaluator()
        self.sessions = SessionMemoryStore(ttl_seconds=60*60*24)

    def handle_message(self, user_input: str, session_id: str = None) -> dict:
        # session management
        if session_id:
            session = self.sessions.get_session(session_id)
            if not session:
                session = self.sessions.create_session()
        else:
            session = self.sessions.create_session()
        log_event('info', 'request_received', {'session_id': session.get('session_id'), 'user_input': user_input})
        # Planner builds plan
        plan_package = self.planner.build_plan(user_input, session)
        plan = plan_package.get('plan')
        log_event('debug', 'plan_built', plan)
        # Worker executes
        worker_out = self.worker.execute_plan(plan)
        log_event('debug', 'worker_executed', {'plan_id': plan.get('plan_id')})
        # Evaluator checks
        eval_out = self.evaluator.evaluate(worker_out.get('payload'))
        evaluation = eval_out.get('evaluation')
        log_event('info', 'evaluation_done', {'accepted': evaluation.get('accepted'), 'confidence': evaluation.get('confidence')})
        # Build user-facing response
        if not evaluation.get('accepted'):
            response_text = "I'm sorry — I couldn't find verified resources nearby. Please contact local emergency services or try a different query."
            if evaluation.get('issues'):
                response_text += " Issues: " + ", ".join(evaluation.get('issues'))
        else:
            lines = []
            for item in evaluation.get('final_list'):
                lines.append(item.get('summary'))
            response_text = "\n".join(lines)
        # update session memory
        self.sessions.update_session(session.get('session_id'), {'last_intent': plan.get('intent'), 'last_location': plan.get('location')})
        audit = {
            'request': user_input,
            'plan': plan,
            'final_response': response_text,
            'evaluator': evaluation
        }
        log_event('debug', 'audit_entry', audit)
        return {'response': response_text, 'session_id': session.get('session_id'), 'audit': audit}

def run_agent(user_input: str):
    agent = MainAgent()
    result = agent.handle_message(user_input)
    return result['response']
