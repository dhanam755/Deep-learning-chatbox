
// document.addEventListener("DOMContentLoaded", function () {

//     const input = document.getElementById("user-input");
//     const chatBox = document.getElementById("chat-box");

   
//     window.sendMessage = async function () {
//         let message = input.value.trim();
//         if (!message) return; 


//         appendMessage(message, "user-message");
//         input.value = "";

      
//         const typingDiv = appendMessage("Bot is typing...", "bot-message typing");

//         try {
//             let response = await fetch("/chat", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ message: message })
//             });

//             let data = await response.json();

           
//             typingDiv.remove();

//             let botReply = (data && typeof data.response === "string") ? data.response : null;

//             if (botReply && botReply.trim() !== "") {
//                 appendMessage(botReply, "bot-message");
//             } else {
//                 appendMessage("Sorry, I couldn't generate a response.", "bot-message error");
//             }

//         } catch (error) {
//             console.error(error);
//             if (typingDiv) typingDiv.remove();
//             appendMessage("Server error occurred.", "bot-message error");
//         }
//     };


//     function appendMessage(text, className) {
//         let div = document.createElement("div");
//         div.className = className;
//         div.innerText = text;
//         chatBox.appendChild(div);
//         chatBox.scrollTop = chatBox.scrollHeight;
//         return div; 
//     }


//     input.addEventListener("keypress", function (e) {
//         if (e.key === "Enter") sendMessage();
//     });

// });






document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const chatList = document.getElementById("chat-list");

    let chats = [];
    let currentChat = [];

    // ---------------- LOAD HISTORY ---------------- //

    async function loadHistory() {

        try {
            let res = await fetch("/history");
            let data = await res.json();

            chats = data || [];

            renderSidebar();

        } catch (err) {
            console.error("History load error:", err);
        }
    }

    // ---------------- SIDEBAR ---------------- //

    function renderSidebar() {

        chatList.innerHTML = "";

        chats.forEach((chat, index) => {

            let item = document.createElement("div");
            item.className = "chat-item";
            item.innerText = chat.user || "Chat";

            item.onclick = () => openChat(index);

            chatList.appendChild(item);
        });
    }

    // ---------------- OPEN CHAT ---------------- //

    function openChat(index) {

        chatBox.innerHTML = "";

        let chat = chats[index];

        appendMessage(chat.user, "user-message");
        appendMessage(chat.bot, "bot-message");
    }

    // ---------------- SEND MESSAGE ---------------- //

    window.sendMessage = async function () {

        let message = input.value.trim();

        if (!message) return;

        appendMessage(message, "user-message");
        input.value = "";

        const typing = appendMessage("Bot is typing...", "bot-message");

        try {

            let res = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message: message})
            });

            let data = await res.json();

            typing.remove();

            appendMessage(data.response, "bot-message");

            chats.push({
                user: message,
                bot: data.response
            });

            renderSidebar();

        } catch (err) {

            typing.remove();
            appendMessage("Server error", "bot-message");

        }
    }

    // ---------------- ADD MESSAGE ---------------- //

    function appendMessage(text, className) {

        let div = document.createElement("div");
        div.className = className;
        div.innerText = text;

        chatBox.appendChild(div);

        chatBox.scrollTop = chatBox.scrollHeight;

        return div;
    }

    // ---------------- ENTER SEND ---------------- //

    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") sendMessage();
    });

    // ---------------- START ---------------- //

    loadHistory();

});