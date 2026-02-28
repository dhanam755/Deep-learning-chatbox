function sendMessage() {
    let input = document.getElementById("user-input");
    let message = input.value;

    if (message.trim() === "") return;

    addMessage(message, "user");

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.response, "bot");
    });

    input.value = "";
}

function addMessage(text, sender) {
    let chatBox = document.getElementById("chat-box");
    let messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}