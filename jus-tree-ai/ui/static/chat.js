// Handle chat box interaction.
let firstTimeOpening = true;
const toggleChat = () => {
    let chatContainer = document.getElementById("chat-container");
    chatContainer.style.display = (chatContainer.style.display === "block") ? "none" : "block";
    // Handle first-time launching the window.
    if (firstTimeOpening) {
        firstTimeOpening = false;
        let chatBox = document.getElementById("chat-box");
        // Append initial bot message.
        let botMsgElement = document.createElement("div");
        botMsgElement.classList.add("message", "bot-message");
        botMsgElement.textContent = "Hello! I am a JusTreeAI Bot helping you with DUO student finance. Please provide your details to determine your grant eligibility. " +
                                    "These include: age, university program, program duration, recognition, and nationality. I am excited to help you!";
        chatBox.appendChild(botMsgElement);
    }
}

// Handle user interaction.
const handleKeyPress = (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
}

// Handle sending messages.
const sendMessage = () => {
    let inputField = document.getElementById("user-input");
    let userMessage = inputField.value.trim();
    if (userMessage === "") return;
    let chatBox = document.getElementById("chat-box");
    // Append user message.
    let userMsgElement = document.createElement("div");
    userMsgElement.classList.add("message", "user-message");
    userMsgElement.textContent = userMessage;
    chatBox.appendChild(userMsgElement);
    inputField.value = "";
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    // Show "Bot is typing..." message.
    let typingElement = document.createElement("div");
    typingElement.classList.add("message", "typing");
    typingElement.textContent = "Bot is typing...";
    chatBox.appendChild(typingElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    // Wait 1 second before showing the actual bot response.
    // TODO: instead of 1 sec wait for actual bot response!
    setTimeout(() => {
        typingElement.remove();
        fetch("/chat", {
            method: "POST",
            body: JSON.stringify({ message: userMessage }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => {
            // Append bot response.
            let botMsgElement = document.createElement("div");
            botMsgElement.classList.add("message", "bot-message");
            botMsgElement.textContent = data.response;
            chatBox.appendChild(botMsgElement);
            chatBox.scrollTop = chatBox.scrollHeight;
        });
    }, 1000);
}
