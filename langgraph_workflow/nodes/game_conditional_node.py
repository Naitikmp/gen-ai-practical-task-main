import logging
from langgraph_workflow.models import WorkflowState
from langgraph_workflow.config import games_dict
logger = logging.getLogger(__name__)

def route_to_game(state: WorkflowState):
    """ Route to the game based on the current game type. 
        Task: Implement the logic to route to the appropriate game.
    """
    try:
        """
        TODO:

        - Retrieve the current game type from the state
        - Validate if the current game type exists in games_dict
        - Log the selected game type
        - Return the appropriate game based on current_game_type
        """
        current_game_type = state.get("current_game_type")
        if not current_game_type:
            logger.error("No game type specified in the state.")
            return None
        if current_game_type not in games_dict:
            logger.error(f"Game type '{current_game_type}' not found in games_dict.")
            return None
        logger.info(f"Routing to game: {current_game_type}")
        game_node = games_dict[current_game_type]
        return game_node
    
    except KeyError as e:
        logger.error(f"KeyError: {str(e)} - Check if 'current_game_type' is set in the state.")
        
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        raise e