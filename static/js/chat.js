// document.addEventListener("DOMContentLoaded", function () {

//     const input = document.getElementById("user-input");
//     const chatBox = document.getElementById("chat-box");

//     window.sendMessage = function () {

//         let message = input.value.trim();
//         if (!message) return;

//         appendMessage(message, "user-msg");
//         input.value = "";

//         fetch("/chat", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ message: message })
//         })
//         .then(response => response.json())
//         .then(data => {

//             console.log("Server Data:", data);

//             let botReply = "No response received";

//             if (data && data.response) {
//                 botReply = data.response;
//             }

//             appendMessage(botReply, "bot-msg");
//         })
//         .catch(error => {
//             console.error(error);
//             appendMessage("Server error.", "bot-msg");
//         });
//     };

//     function appendMessage(text, className) {
//         let div = document.createElement("div");
//         div.className = className;
//         div.innerText = text;
//         chatBox.appendChild(div);
//         chatBox.scrollTop = chatBox.scrollHeight;
//     }

// });


document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    // Send message
    window.sendMessage = async function () {
        let message = input.value.trim();
        if (!message) return; // ignore empty messages

        // Append user message
        appendMessage(message, "user-message");
        input.value = "";

        // Show typing indicator
        const typingDiv = appendMessage("Bot is typing...", "bot-message typing");

        try {
            let response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            let data = await response.json();

            // Remove typing indicator
            typingDiv.remove();

            // Safely get bot response
            let botReply = (data && typeof data.response === "string") ? data.response : null;

            if (botReply && botReply.trim() !== "") {
                appendMessage(botReply, "bot-message");
            } else {
                appendMessage("Sorry, I couldn't generate a response.", "bot-message error");
            }

        } catch (error) {
            console.error(error);
            if (typingDiv) typingDiv.remove();
            appendMessage("Server error occurred.", "bot-message error");
        }
    };

    // Append message to chatbox and scroll
    function appendMessage(text, className) {
        let div = document.createElement("div");
        div.className = className;
        div.innerText = text;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
        return div; // return div for typing indicator removal
    }

    // Press Enter to send
    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") sendMessage();
    });

});