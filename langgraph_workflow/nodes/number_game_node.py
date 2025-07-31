import logging
from langgraph_workflow.models import WorkflowState
from langchain_core.output_parsers import JsonOutputParser
from langgraph_workflow.prompt_templates.nodes_prompts import number_game_prompt
from pydantic import BaseModel, Field
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
import os
logger = logging.getLogger(__name__)
if not os.environ.get("OPENAI_API_KEY"):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define your desired data structure.
class NumberGameModel(BaseModel):
    ai: str = Field(description="question asked by ai to user")
    status: str = Field(description="game status, either inprogress or done")

# Set up a parser + inject instructions into the prompt template.
parser = JsonOutputParser(pydantic_object=NumberGameModel)
format_instructions = parser.get_format_instructions()

async def number_game_node(state: WorkflowState):
    """ Number Game Node for guessing the number """
    try:
        logger.info("\n################### NODE: number_game_node ###################")
        """
        # TODO: 
        
        - Make a LLM call with the number_game_prompt and NumberGameModel (or format_instructions)
        - Get the response from the LLM -> assign it to llm_response
        - Validate the LLM response structure  (if it's not a dict, convert it into dict)
        - Log the LLM response
        - Add the response to the state and return it
        
        Note: 
        - You can either use LangChain or OpenAI API to make the LLM call
        - Accordingly you can modify 'number_game_prompt' however you want (if you want)
        """

        user_input = state.get("user_input")
        chat_history = state.get("chat_history", {})
        current_game_type = state.get("current_game_type")
        if not current_game_type:
            logger.error("No game type specified in the state.")
            return None
        if current_game_type != "number_game":
            logger.error(f"Game type '{current_game_type}' is not 'number_game'.")
            return None
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0,
            max_tokens=None,
            max_retries=2,
            api_key=os.getenv("OPENAI_API_KEY")
        ) 
        prompt_template = number_game_prompt.format_messages(
            user_input=user_input,
            chat_history=str(chat_history),
            format_instructions=format_instructions
        )

        response = await llm.ainvoke(prompt_template)
        logger.debug(f"LLM Response: {response.content}")

        try:
            llm_response = response.content

            if isinstance(llm_response, str):
                llm_response = llm_response.strip()
                if llm_response.startswith("```json") or llm_response.startswith("```"):
                    llm_response = llm_response.strip("`")
                    llm_response = llm_response.replace("json", "", 1).strip()

                try:
                    llm_response = json.loads(llm_response)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON string in response.content: {llm_response}")
                    llm_response = {"ai": "Invalid response format", "status": "error"}

            state["answer"] = llm_response.get("ai", "")
            state["game_status"] = llm_response.get("status", "inprogress")
            turn_number = str(len(chat_history) + 1)
            chat_history[turn_number] = {"user": user_input, "ai": state["answer"]}
            state["chat_history"] = chat_history

            return state
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from LLM response: {str(e)}")
            llm_response = {"ai": "Invalid response format", "status": "error"}
            state["answer"] = llm_response.get("ai", "")
            state["game_status"] = llm_response.get("status", "error")
        except TypeError as e:
            logger.error(f"TypeError: {str(e)} - LLM response is not a dict.")
            llm_response = {"ai": "Invalid response format", "status": "error"}
            state["answer"] = llm_response.get("ai", "")
            state["game_status"] = llm_response.get("status", "error")
        except KeyError as e:
            logger.error(f"KeyError: {str(e)} - LLM response missing expected keys.")
            llm_response = {"ai": "Invalid response format", "status": "error"}
            state["answer"] = llm_response.get("ai", "")
            state["game_status"] = llm_response.get("status", "error")
        except ValueError as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            llm_response = {"ai": "Invalid response format", "status": "error"}
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        raise e
    