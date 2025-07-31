import logging
from langgraph.graph import END, StateGraph
from langgraph_workflow.models import WorkflowState
from langgraph_workflow.nodes import (
    game_conditional_node,
    game_selector_node,
    number_game_node,
    word_game_node
)

logger = logging.getLogger(__name__)

# Workflow builder
class LanggraphAgents:
    def __init__(self):
        self.workflow = None
    
    def build_workflow(self):
        try:
            workflow = StateGraph(WorkflowState)
                        
            # Add nodes
            workflow.add_node("game_selector_node", game_selector_node.game_selector_node)
            workflow.add_node("number_game_node", number_game_node.number_game_node)
            workflow.add_node("word_game_node", word_game_node.word_game_node)
                
            workflow.add_conditional_edges('game_selector_node', game_conditional_node.route_to_game)
            
            # Add end nodes
            workflow.add_edge("number_game_node", END)
            workflow.add_edge("word_game_node", END)
            
            # TODO: Set the entry point to the game_selector_node
            workflow.set_entry_point("game_selector_node")
            
            self.workflow = workflow.compile()
            return self.workflow
        except Exception as e:
            logger.error(f"Exception in build workflow: {str(e)}")
            raise e
        