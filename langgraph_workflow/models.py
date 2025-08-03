from pydantic import BaseModel
from typing import TypedDict

class ChatRequest(BaseModel):
    user_input: str
    end_game : bool = False
    game_type: str = None
    user_query: str = None
    session_id: str = None
    chat_history : dict = None
    
# Define state schema
class WorkflowState(TypedDict):
    user_input: str =""
    game_data: dict
    chat_history: dict
    session_id: str = None
    session_file: str = None
    current_game_type: str = None
    answer: str
    game_status: str