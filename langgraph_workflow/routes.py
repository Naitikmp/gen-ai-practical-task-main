import json
import logging
from fastapi import APIRouter, Depends
from utils import (
    create_response,
    initialize_session,
    update_state_result,
    process_user_input_update_session_data
)
import os
from langgraph_workflow.models import ChatRequest
from langgraph_workflow.workflow import LanggraphAgents
import uuid

# Create a directory to store session files
SESSION_DIR = "sessions_data"
os.makedirs(SESSION_DIR, exist_ok=True)

router = APIRouter(prefix="/agent", tags=["agent"])

lang_agent = LanggraphAgents()
logger = logging.getLogger(__name__)

# session_id = str(uuid.uuid4())

@router.post("/game")
async def chat(request: ChatRequest, graph=Depends(lang_agent.build_workflow)):
    try:
        logger.info("========= Inside Game API =========")
        
        
        session_id = request.session_id
        logger.debug(f"Request Session ID: '{request.session_id}'")
        session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
        
        initialize_session(session_id, session_file)    
        data = process_user_input_update_session_data(session_file, request)
        with open(session_file, "r") as f:
                game_data = json.load(f)
        chat_history = game_data.get("chat_history", {})
        print(f"Data after processing user input: {data}")
        if request.user_input == "result":
            return create_response(message="Results fetched sussccessfully", status_code=200, success=True, data=data)
            
        ############### Start the workflow ###############
        # TODO: Initialize state with user input
        intial_state = {
            "user_input": request.user_input,
            "game_data": data,
            "chat_history": chat_history,
            "session_id": session_id,
            "session_file": session_file,
            "current_game_type": request.game_type,
            "answer": "",
            "game_status": game_data.get("game_status", "ongoing")
            }
        
        result_state = await graph.ainvoke(input=intial_state)
        # Update the result state
        update_state_result(result_state)
        
        # TODO: Add appropriate response to data_res dict from result_state
        data_res = {
            "session_id": result_state.get("session_id"),
            "session_file": result_state.get("session_file"),
            "answer": result_state.get("answer", "No answer found")
        }
        
        logger.debug(f"Answer for the user query: '{result_state.get('answer')}'")
        return create_response(message="Answer retrieved successfully", status_code=200, success=True, data=data_res)
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return create_response(message="Something went wrong while retrieving the answer", status_code=500, success=False, data={})
