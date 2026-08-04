document.addEventListener("DOMContentLoaded", () => {
  const csrfToken = window.APP_CONFIG?.csrfToken || "";
  const root = document.documentElement;
  const chatApp = document.querySelector(".chat-app");
  const sidebar = document.getElementById("sidebar");
  const sidebarBackdrop = document.getElementById("sidebarBackdrop");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");
  const themeToggle = document.getElementById("themeToggle");
  const chatList = document.getElementById("chatList");
  const chatSearch = document.getElementById("chatSearch");
  const newChatBtn = document.getElementById("newChatBtn");
  const messages = document.getElementById("messages");
  const welcomePanel = document.getElementById("welcomePanel");
  const messageInput = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const charCount = document.getElementById("charCount");
  const modelSelect = document.getElementById("modelSelect");
  const chatTitle = document.getElementById("chatTitle");
  const deleteChatBtn = document.getElementById("deleteChatBtn");
  const renameChatBtn = document.getElementById("renameChatBtn");
  const regenerateBtn = document.getElementById("regenerateBtn");
  const exportTxtBtn = document.getElementById("exportTxtBtn");
  const exportPdfBtn = document.getElementById("exportPdfBtn");
  const renameChatModalEl = document.getElementById("renameChatModal");
  const deleteChatModalEl = document.getElementById("deleteChatModal");
  const exportChatModalEl = document.getElementById("exportChatModal");
  const newChatModalEl = document.getElementById("newChatModal");
  const renameChatInput = document.getElementById("renameChatInput");
  const renameChatSaveBtn = document.getElementById("renameChatSaveBtn");
  const deleteChatConfirmBtn = document.getElementById("deleteChatConfirmBtn");
  const deleteChatName = document.getElementById("deleteChatName");
  const newChatTitleInput = document.getElementById("newChatTitleInput");
  const newChatModelSelect = document.getElementById("newChatModelSelect");
  const createChatConfirmBtn = document.getElementById("createChatConfirmBtn");

  if (!messages || !messageInput || !sendBtn) {
    initThemeOnly();
    return;
  }

  let currentChatId = null;
  let isStreaming = false;
  const initialChatId = chatApp?.dataset.initialChatId?.trim() || "";
  let pendingRenameTitle = "";

  const renameChatModal = renameChatModalEl && window.bootstrap ? new bootstrap.Modal(renameChatModalEl) : null;
  const deleteChatModal = deleteChatModalEl && window.bootstrap ? new bootstrap.Modal(deleteChatModalEl) : null;
  const exportChatModal = exportChatModalEl && window.bootstrap ? new bootstrap.Modal(exportChatModalEl) : null;
  const newChatModal = newChatModalEl && window.bootstrap ? new bootstrap.Modal(newChatModalEl) : null;

  initThemeOnly();
  bindEvents();
  updateComposerState();

  if (initialChatId) {
    void openChat(initialChatId);
  }

  function bindEvents() {
    sendBtn.addEventListener("click", sendMessage);
    messageInput.addEventListener("input", () => {
      charCount.textContent = `${messageInput.value.length} / 4000`;
      autoresizeComposer();
      updateComposerState();
    });
    messageInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });
    chatList?.addEventListener("click", (event) => {
      const item = event.target.closest(".chat-item");
      if (item) openChat(item.dataset.chatId);
    });
    chatSearch?.addEventListener("input", debounce(searchChats, 250));
    sidebarToggle?.addEventListener("click", openSidebar);
    sidebarCloseBtn?.addEventListener("click", closeSidebar);
    sidebarBackdrop?.addEventListener("click", closeSidebar);
    deleteChatBtn?.addEventListener("click", openDeleteChatModal);
    renameChatBtn?.addEventListener("click", openRenameChatModal);
    regenerateBtn?.addEventListener("click", regenerateResponse);
    exportTxtBtn?.addEventListener("click", openExportChatModal);
    exportPdfBtn?.addEventListener("click", openExportChatModal);
    newChatBtn?.addEventListener("click", openNewChatModal);

    renameChatSaveBtn?.addEventListener("click", saveRenameChat);
    deleteChatConfirmBtn?.addEventListener("click", confirmDeleteChat);
    createChatConfirmBtn?.addEventListener("click", createNewChat);
    exportChatModalEl?.querySelectorAll("[data-export-format]").forEach((button) => {
      button.addEventListener("click", () => {
        const format = button.dataset.exportFormat || "txt";
        closeModal(exportChatModal);
        exportChat(format);
      });
    });
  }

  function initThemeOnly() {
    const savedTheme = localStorage.getItem("chatbox-theme") || "dark";
    root.dataset.theme = savedTheme;
    setThemeIcon(savedTheme);
    themeToggle?.addEventListener("click", () => {
      const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = nextTheme;
      localStorage.setItem("chatbox-theme", nextTheme);
      setThemeIcon(nextTheme);
    });
  }

  function setThemeIcon(theme) {
    const icon = themeToggle?.querySelector("i");
    if (icon) icon.className = theme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
  }

  function startNewChat() {
    currentChatId = null;
    chatTitle.textContent = "Start a new conversation";
    messages.innerHTML = "";
    welcomePanel.hidden = false;
    setActiveChat(null);
    updateChatActions();
    messageInput.focus();
    closeSidebar();
  }

  function openSidebar() {
    document.body.classList.add("sidebar-open");
  }

  function closeSidebar() {
    document.body.classList.remove("sidebar-open");
  }

  async function openChat(chatId) {
    if (!chatId || isStreaming) return;
    const data = await requestJson(`/api/chats/${chatId}`);
    currentChatId = data.chat.id;
    chatTitle.textContent = data.chat.title;
    modelSelect.value = data.chat.model || modelSelect.value;
    messages.innerHTML = "";
    data.messages.forEach((message) => appendMessage(message.role, message.content));
    welcomePanel.hidden = data.messages.length > 0;
    setActiveChat(chatId);
    updateChatActions();
    scrollToBottom();
    closeSidebar();
  }

  async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || isStreaming) return;

    appendMessage("user", text);
    messageInput.value = "";
    messageInput.dispatchEvent(new Event("input"));
    welcomePanel.hidden = true;

    const assistantNode = appendMessage("assistant", "", true);
    setStreaming(true);

    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          message: text,
          chat_id: currentChatId,
          model: modelSelect.value,
        }),
      });

      if (!response.ok || !response.body) throw new Error("Unable to stream response.");

      let assistantText = "";
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() || "";
        for (const eventText of events) {
          const parsed = parseSseEvent(eventText);
          if (parsed.event === "meta") {
            currentChatId = parsed.data.chat_id;
            updateChatActions();
          }
          if (!parsed.event && parsed.data?.chunk) {
            assistantText += parsed.data.chunk;
            updateMessageContent(assistantNode, assistantText, true);
          }
          if (parsed.event === "done") {
            currentChatId = parsed.data.chat_id;
          }
        }
      }

      updateMessageContent(assistantNode, assistantText || "No response received.");
      await refreshChats();
    } catch (error) {
      updateMessageContent(assistantNode, `Sorry, something went wrong: ${error.message}`);
    } finally {
      setStreaming(false);
      updateChatActions();
    }
  }

  async function regenerateResponse() {
    if (!currentChatId || isStreaming) return;
    const assistantNode = appendMessage("assistant", "", true);
    setStreaming(true);
    try {
      const data = await requestJson(`/api/chats/${currentChatId}/regenerate`, { method: "POST" });
      updateMessageContent(assistantNode, data.response || "No response received.");
      await refreshChats();
    } catch (error) {
      updateMessageContent(assistantNode, `Unable to regenerate: ${error.message}`);
    } finally {
      setStreaming(false);
    }
  }

  async function searchChats() {
    await refreshChats(chatSearch.value);
  }

  async function refreshChats(query = "") {
    const data = await requestJson(`/api/chats?q=${encodeURIComponent(query)}`);
    chatList.innerHTML = "";
    if (!data.chats.length) {
      chatList.innerHTML = '<div class="empty-history">No chats found</div>';
      return;
    }
    data.chats.forEach((chat) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = `chat-item${chat.id === currentChatId ? " active" : ""}`;
      item.dataset.chatId = chat.id;
      item.dataset.title = chat.title;
      item.innerHTML = `<span class="chat-item-title"></span><span class="chat-item-meta">${chat.message_count || 0} messages</span>`;
      item.querySelector(".chat-item-title").textContent = chat.title;
      chatList.appendChild(item);
      if (chat.id === currentChatId) chatTitle.textContent = chat.title;
    });
  }

  async function deleteCurrentChat() {
    if (!currentChatId) return;
    await requestJson(`/api/chats/${currentChatId}`, { method: "DELETE" });
    startNewChat();
    await refreshChats();
  }

  async function renameCurrentChat() {
    if (!currentChatId) return;
    const title = pendingRenameTitle || chatTitle.textContent;
    await requestJson(`/api/chats/${currentChatId}`, {
      method: "PATCH",
      body: JSON.stringify({ title: title.trim() }),
    });
    chatTitle.textContent = title.trim();
    await refreshChats(chatSearch?.value || "");
  }

  function openRenameChatModal() {
    if (!currentChatId || !renameChatModal) return;
    pendingRenameTitle = chatTitle.textContent || "";
    if (renameChatInput) renameChatInput.value = pendingRenameTitle;
    renameChatModal.show();
    setTimeout(() => renameChatInput?.focus(), 150);
  }

  async function saveRenameChat() {
    if (!currentChatId) return;
    const nextTitle = (renameChatInput?.value || "").trim();
    if (!nextTitle) return;
    await requestJson(`/api/chats/${currentChatId}`, {
      method: "PATCH",
      body: JSON.stringify({ title: nextTitle }),
    });
    chatTitle.textContent = nextTitle;
    closeModal(renameChatModal);
    await refreshChats(chatSearch?.value || "");
  }

  function openDeleteChatModal() {
    if (!currentChatId || !deleteChatModal) return;
    if (deleteChatName) deleteChatName.textContent = chatTitle.textContent || "this conversation";
    deleteChatModal.show();
  }

  async function confirmDeleteChat() {
    if (!currentChatId) return;
    await requestJson(`/api/chats/${currentChatId}`, { method: "DELETE" });
    closeModal(deleteChatModal);
    startNewChat();
    await refreshChats();
  }

  function openExportChatModal() {
    if (!currentChatId || !exportChatModal) return;
    exportChatModal.show();
  }

  function openNewChatModal() {
    if (!newChatModal) return;
    closeSidebar();
    if (newChatTitleInput) newChatTitleInput.value = "";
    if (newChatModelSelect && modelSelect) newChatModelSelect.value = modelSelect.value;
    newChatModal.show();
    setTimeout(() => newChatTitleInput?.focus(), 150);
  }

  async function createNewChat() {
    const title = (newChatTitleInput?.value || "").trim() || "New Chat";
    const model = normalizeModelName(newChatModelSelect?.value || modelSelect?.value || "");
    const data = await requestJson("/api/chats", {
      method: "POST",
      body: JSON.stringify({ title, model }),
    });
    closeModal(newChatModal);
    modelSelect.value = data.model || model;
    await refreshChats(chatSearch?.value || "");
    await openChat(data.chat_id);
  }

  function exportChat(type) {
    if (currentChatId) window.location.href = `/api/export/${currentChatId}.${type}`;
  }

  function closeModal(modalInstance) {
    modalInstance?.hide();
  }

  function normalizeModelName(model) {
    const available = window.APP_CONFIG?.models || [];
    return available.includes(model) ? model : available[1] || model;
  }

  async function requestJson(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
        ...(options.headers || {}),
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Request failed.");
    return data;
  }

  function appendMessage(role, content, typing = false) {
    const row = document.createElement("article");
    row.className = `message-row ${role}`;
    row.innerHTML = `
      <div class="message-avatar">${role === "user" ? "You" : "AI"}</div>
      <div class="message-bubble">
        <div class="message-content"></div>
        <div class="message-actions">
          <button type="button" class="copy-message" title="Copy message"><i class="fa-regular fa-copy"></i></button>
        </div>
      </div>`;
    messages.appendChild(row);
    row.querySelector(".copy-message").addEventListener("click", () => copyToClipboard(content || row.dataset.raw || ""));
    updateMessageContent(row, content, typing);
    scrollToBottom();
    return row;
  }

  function updateMessageContent(row, content, typing = false) {
    row.dataset.raw = content;
    const target = row.querySelector(".message-content");
    if (typing && !content) {
      target.innerHTML = '<span class="typing-dots"><span></span><span></span><span></span></span>';
      return;
    }
    target.innerHTML = renderMarkdown(content);
    addCodeCopyButtons(target);
    scrollToBottom();
  }

  function renderMarkdown(text) {
    if (window.marked) {
      window.marked.setOptions({ breaks: true, gfm: true });
      return window.marked.parse(escapeHtml(text || ""));
    }
    return escapeHtml(text || "").replace(/\n/g, "<br>");
  }

  function addCodeCopyButtons(container) {
    container.querySelectorAll("pre").forEach((pre) => {
      if (pre.querySelector(".copy-code")) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "copy-code";
      button.innerHTML = '<i class="fa-regular fa-copy"></i>';
      button.title = "Copy code";
      button.addEventListener("click", () => copyToClipboard(pre.querySelector("code")?.innerText || pre.innerText));
      pre.appendChild(button);
      if (window.hljs) window.hljs.highlightElement(pre.querySelector("code") || pre);
    });
  }

  function parseSseEvent(eventText) {
    const lines = eventText.split("\n");
    let event = "";
    let data = "";
    lines.forEach((line) => {
      if (line.startsWith("event:")) event = line.slice(6).trim();
      if (line.startsWith("data:")) data += line.slice(5).trim();
    });
    return { event, data: data ? JSON.parse(data) : null };
  }

  function setActiveChat(chatId) {
    document.querySelectorAll(".chat-item").forEach((item) => {
      item.classList.toggle("active", item.dataset.chatId === chatId);
    });
  }

  function updateChatActions() {
    const disabled = !currentChatId;
    [deleteChatBtn, renameChatBtn, regenerateBtn, exportTxtBtn, exportPdfBtn].forEach((button) => {
      if (button) button.disabled = disabled;
    });
  }

  function setStreaming(value) {
    isStreaming = value;
    sendBtn.disabled = value || !messageInput.value.trim();
    messageInput.disabled = value;
    sendBtn.classList.toggle("loading", value);
  }

  function updateComposerState() {
    sendBtn.disabled = isStreaming || !messageInput.value.trim();
  }

  function autoresizeComposer() {
    messageInput.style.height = "auto";
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 180)}px`;
  }

  function scrollToBottom() {
    messages.parentElement.scrollTop = messages.parentElement.scrollHeight;
  }

  function copyToClipboard(text) {
    navigator.clipboard?.writeText(text || "");
  }

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
  }

  function debounce(fn, delay) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delay);
    };
  }
});
