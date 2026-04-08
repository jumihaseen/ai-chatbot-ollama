const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

function getCurrentTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addMessage(sender, text) {
    const row = document.createElement("div");
    row.className = "message-row";

    const bubble = document.createElement("div");
    bubble.className = `message ${sender}`;
    bubble.textContent = text;

    const time = document.createElement("span");
    time.className = "timestamp";
    time.textContent = getCurrentTime();

    row.appendChild(bubble);
    row.appendChild(time);
    chatBox.appendChild(row);
    scrollToBottom();
}

function showTypingIndicator() {
    const typing = document.createElement("div");
    typing.id = "typing-indicator";
    typing.className = "typing";
    typing.textContent = "Bot is typing...";
    chatBox.appendChild(typing);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typing = document.getElementById("typing-indicator");
    if (typing) {
        typing.remove();
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage("user", message);
    userInput.value = "";
    showTypingIndicator();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message }),
        });

        const raw = await response.text();
        let data = null;
        try {
            data = raw ? JSON.parse(raw) : null;
        } catch {
            data = null;
        }

        hideTypingIndicator();

        const reply =
            data && typeof data.response === "string" && data.response.trim()
                ? data.response
                : null;

        if (reply) {
            addMessage("bot", reply);
        } else if (!response.ok) {
            addMessage(
                "bot",
                "Sorry, the server returned an error. Please try again in a moment."
            );
        } else {
            addMessage("bot", "No response received.");
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage(
            "bot",
            "Sorry, I can't reach the chat server right now. Check that the app is running and try again."
        );
    }
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Starter greeting for users.
addMessage("bot", "Hello! How can I assist you today?");
