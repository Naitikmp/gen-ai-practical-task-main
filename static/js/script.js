let gameType = localStorage.getItem('gameType');
let context = [];  // Stores interaction history
let gameCount = 1;
window.onload = () => {
  // Display game type and count
  updateGameInfo();
  console.log('➡ gameType:', gameType)
  // On pag e load, get the first question
  fetch('/api/v1/agent/game', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      user_input: gameType,
      user_query: "",
      game_type: gameType,
      end_game: false
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      updateConversation(data.data.answer);
      context.push({ ai: data.data.answer });
    } else {
      updateConversation("Error loading game. Please return to the menu and try again.");
    }
  })
  .catch(error => {
    console.error("API Error:", error);
    updateConversation("Error connecting to the server. Please return to the menu and try again.");
  });
  
  // Add enter key event listener
  document.getElementById("user-response").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      submitAnswer();
    }
  });
};

function updateGameInfo() {
  // Format game type for display
  let displayGameType = gameType === 'number_game' ? 'Number Game' : 'Word Game';
  document.getElementById("game-type-display").innerText = displayGameType;
  document.getElementById("game-count").innerText = `Game #${gameCount}`;
}

function submitAnswer() {
  const userInput = document.getElementById("user-response").value.trim();
  if (!userInput) return;

  // Disable input while processing
  toggleInputState(false);
  
  context.push({ user: userInput });

  fetch('/api/v1/agent/game', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_input: userInput,
      user_query: "",
      game_type: gameType,
      end_game: false
    })
  })
  .then(res => res.json())
  .then(data => {
    console.log('➡ data original:--->', data);
    if (data.success) {

      console.log('➡ data original:', data);
      updateConversation(data.data.answer);
      console.log('➡ data answer:', data.data.answer);
      context.push({ ai: data.data.answer});
      document.getElementById("user-response").value = "";

      if (data.data.game_status === "done") {
        // Game is over, show final message
        document.getElementById("back-btn").style.display = "block";
      }
    } else {
      updateConversation("Error processing your answer. Please try again.");
    }
    // Re-enable input
    toggleInputState(true);
  })
  .catch(error => {
    console.error("API Error:", error);
    updateConversation("Error connecting to the server. Please try again.");
    toggleInputState(true);
  });
}

function toggleInputState(enabled) {
  document.getElementById("user-response").disabled = !enabled;
  document.getElementById("submit-btn").disabled = !enabled;
}

function updateConversation(message) {
  document.getElementById("agent-question").innerText = message;
}

function returnToMenu() {
  localStorage.removeItem('gameType');
  window.location.href = '/';
}
