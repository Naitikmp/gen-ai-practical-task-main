import logging
from langgraph_workflow.models import WorkflowState
from langchain_openai import ChatOpenAI
from utils import load_session, load_required_game_data
from langgraph_workflow.config import games_dict

# TODO: use OpenAI LLM using LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=None,
    max_retries=2,
)

logger = logging.getLogger(__name__)

async def game_selector_node(state: WorkflowState):
    """ Select the game type based on user input.
        Task: Implement the logic to select and validate the game type.
    """
    try:
        logger.info("\n################### NODE: game_selector_node ###################")
        
        # TODO: load the session data by retrieving 'session id' and 'session file' from the state 
        session_id = state.get("session_id")
        session_file = state.get("session_file")
        current_game_type = state.get("current_game_type")
        if not current_game_type:
            logger.error("No game type specified in the state.")
            return None
        if current_game_type not in games_dict:
            logger.error(f"Game type '{current_game_type}' not found in games_dict.")
            return None
        game_data = load_session(session_id, session_file,current_game_type)
        
        chat_history = load_required_game_data(game_data)
        logger.debug(f"chat_history: {chat_history}")
        
        # TODO: Add game type and chat history to the state and return it
        state["current_game_type"] = current_game_type
        state["chat_history"] = chat_history
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        raise e
