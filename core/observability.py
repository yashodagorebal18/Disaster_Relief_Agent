import logging
from typing import Dict, Any

logger = logging.getLogger('disaster_assistant')
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def log_event(level: str, event: str, data: Dict[str, Any] = None):
    if data is None:
        data = {}
    if level == 'debug':
        logger.debug(f"{event} | {data}")
    elif level == 'info':
        logger.info(f"{event} | {data}")
    elif level == 'warn':
        logger.warning(f"{event} | {data}")
    elif level == 'error':
        logger.error(f"{event} | {data}")
