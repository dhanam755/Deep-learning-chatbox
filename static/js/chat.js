
document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

   
    window.sendMessage = async function () {
        let message = input.value.trim();
        if (!message) return; 


        appendMessage(message, "user-message");
        input.value = "";

      
        const typingDiv = appendMessage("Bot is typing...", "bot-message typing");

        try {
            let response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            let data = await response.json();

           
            typingDiv.remove();

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


    function appendMessage(text, className) {
        let div = document.createElement("div");
        div.className = className;
        div.innerText = text;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
        return div; 
    }


    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") sendMessage();
    });

});