from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.config import settings
import os
import json
import logging

logger = logging.getLogger(__name__)
# General JSON response to return in API response
def create_response(message: str, status_code: int, success: bool = False, **kwargs):
    """ General JSON response """
    
    return JSONResponse(
      status_code = status_code,
      content = {
          'success': success,
          'message': message,
          **jsonable_encoder(kwargs)
        }
    )

# Initializes session JSON
def initialize_session(session_id, session_file, game_type=""):
    if not os.path.exists(session_file):
        game_data = {
            "session_id": session_id,
            "current_game_type": game_type,
            "game_status": "",
            "word_game_cnt": 0,
            "number_game_cnt": 0,
            "word_game": {},
            "number_game": {},
            "chat_history": {}
        }
        with open(session_file, "w") as f:
            json.dump(game_data, f, indent=4)
        print(f"✅ New session created: {session_file}")
    else:
        print(f"📂 Session already exists: {session_file}")
        
# Update session based on user_input
def update_game_type_and_count(game_data, user_input):
    if user_input in ["word_game", "number_game"]:
        game_data["current_game_type"] = user_input
        game_data["game_status"] = "inprogress"
        print(f"🎮 Game type set to: {user_input}")
    return game_data

def load_session(session_id, session_file, game_type=None):
    # Load or initialize session file
    if not os.path.exists(session_file):
        print(f"❌ Session file does not exist: {session_file}")
        return None
    else:
        with open(session_file, "r") as f:
            game_data = json.load(f)
        print(f"📂 Loaded session data for: {session_id}")
        return game_data

def load_required_game_data(game_data):
    try:
        current_game = game_data.get("current_game_type")
        current_game_cnt = current_game+"_cnt"
        
        # Create a new key for the current game session
        game_key = f"game{game_data[current_game_cnt]}"
        history = game_data[current_game].get(game_key)
        
        return history
    except Exception as e:
        raise e

def update_state_result(result_state):
    try:
        session_file = result_state.get('session_file')
        with open(session_file, "r") as f:
            game_data = json.load(f)

        current_type = game_data.get("current_game_type")
        current_status = result_state.get("game_status", "")
        user_input = result_state.get("user_input")
        ai_answer = result_state.get("answer")
        chat_history = result_state.get("chat_history", {})
        game_data["chat_history"] = chat_history
        
        game_data["game_status"] = current_status
        counter = game_data.get(f"{current_type}_cnt", 0)
        game_key = f"game{counter}"

        # Ensure the game key exists
        if game_key not in game_data[current_type]:
            game_data[current_type][game_key] = []

        game_rounds = game_data[current_type][game_key]

        # CASE: Last AI message waiting for user input
        if game_rounds and game_rounds[-1].get("user") == "":
            game_rounds[-1]["user"] = user_input

            # If game is done, don’t append new AI message
            if current_status != "done" and ai_answer:
                game_rounds.append({"ai": ai_answer, "user": ""})

        else:
            # Otherwise append new interaction normally
            if user_input and ai_answer:
                game_rounds.append({"user": user_input, "ai": ai_answer})
                if current_status != "done":
                    game_rounds.append({"ai": ai_answer, "user": ""})

        # Save updated rounds
        game_data[current_type][game_key] = game_rounds

        # CASE: Game complete
        if current_status == "done":
            game_data[f"{current_type}_cnt"] += 1
            game_data[f"{current_type}_cnt"] = int(game_data.get(f"{current_type}_cnt", 0))
            
            # Explicitly increment the total counter for result reporting
            if current_type == "word_game":
                game_data["word_game_cnt"] = game_data.get("word_game_cnt", 0) + 1
            elif current_type == "number_game":
                game_data["number_game_cnt"] = game_data.get("number_game_cnt", 0) + 1

            game_data['game_status'] = ""

        with open(session_file, "w") as f:
            json.dump(game_data, f, indent=4)

        print(f"✅ Game state updated: {game_key} | Status: {current_status}")
        print("---\n")

    except Exception as e:
        print('➡ error in update_state_result:', e)
        raise e
  
def process_user_input_update_session_data(session_file, request):
    with open(session_file, "r") as f:
        game_data = json.load(f)

    user_input = request.user_input.lower().strip()
    print('➡ user_input:===>', user_input)

    if user_input in ["word_game", "number_game"]:
        game_data = update_game_type_and_count(game_data, user_input)

        # Create new game entry if not already exists
        game_type = user_input
        counter = game_data.get(f"{game_type}_cnt", 0)
        game_key = f"game{counter}"

        if game_key not in game_data[game_type]:
            game_data[game_type][game_key] = []

    elif user_input == "result":
        msg = f"You have played {game_data.get('word_game_cnt', 0)} word games and {game_data.get('number_game_cnt', 0)} number games."
        print('➡ msg:', msg)
        return msg

    else:
        current_type = game_data.get("current_game_type")
        if not current_type:
            return {"error": "No game type selected yet. Start with 'word_game' or 'number_game'."}

        counter = game_data.get(f"{current_type}_cnt")
        game_key = f"game{counter}"

        if game_key not in game_data[current_type]:
            return {"error": f"Current game entry '{game_key}' not found."}

    with open(session_file, "w") as f:
        json.dump(game_data, f, indent=4)