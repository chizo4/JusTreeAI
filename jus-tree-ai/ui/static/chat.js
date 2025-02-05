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
const sendMessage = async () => {
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
    try {
        // Send user message and wait for response.
        const response = await fetch("/chat", {
            method: "POST",
            body: JSON.stringify({ message: userMessage }),
            headers: { "Content-Type": "application/json" }
        });
        // Ensure response is valid.
        if (!response.ok) {
            throw new Error("Failed to fetch response from server.");
        }
        const data = await response.json();
        // Remove "Bot is typing..." message.
        typingElement.remove();
        // Append bot response.
        let botMsgElement = document.createElement("div");
        botMsgElement.classList.add("message", "bot-message");
        botMsgElement.textContent = data.response;
        chatBox.appendChild(botMsgElement);
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        console.error("Error fetching response:", error);
        typingElement.remove();
        // Append error message in chat.
        let errorMsgElement = document.createElement("div");
        errorMsgElement.classList.add("message", "bot-message");
        errorMsgElement.textContent = "Error: Unable to get a response. Please try again.";
        chatBox.appendChild(errorMsgElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
};
