const chatArea = document.getElementById('chat-area');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const speakButton = document.getElementById('speak-button');

// Speech Recognition
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)(); // Cross-browser compatibility
recognition.lang = 'en-US';
recognition.continuous = false;

speakButton.addEventListener('click', () => {
    recognition.start();
});

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    sendMessage(); // Automatically send
};

recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    displayMessage("Error in speech recognition. Please try again.", "bot");
};


// Text Input and Send
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const message = userInput.value.trim();
    if (message === "") return;

    displayMessage(message, 'user');
    userInput.value = '';

    fetch('/api/chat', {  // Correct URL (important!)
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => {
        if (!response.ok) { // Check for HTTP errors (4xx or 5xx)
            throw new Error(`HTTP error ${response.status}`);  // Throw an error to be caught
        }
        return response.json();
    })
    .then(data => {
        if (data.response) { // Check if 'response' key exists
            displayMessage(data.response, 'bot');
            speakResponse(data.response);
        } else if (data.error) {
            displayMessage("Error: " + data.error, 'bot');
            console.error("Server Error:", data.error); // Log the error to the console
        } else {
            displayMessage("Unexpected response from server.", 'bot');
            console.error("Unexpected server response:", data); // Log the full response
        }

    })
    .catch(error => {
        console.error('Fetch Error:', error); // Log the fetch error
        displayMessage("Error communicating with the server. Please check the console.", "bot");
    });
}


function displayMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender);  // Add a class for styling (optional)
    messageDiv.textContent = `${sender === 'user' ? 'You: ' : 'Bot: '} ${message}`;
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Text-to-Speech
function speakResponse(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
}