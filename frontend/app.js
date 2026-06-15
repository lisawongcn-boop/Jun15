const state = {
  personas: [],
  activePersona: null,
  history: [],
  loading: false,
};

const matchScreen = document.getElementById("match-screen");
const chatScreen = document.getElementById("chat-screen");
const personaList = document.getElementById("persona-list");
const messagesEl = document.getElementById("messages");
const typingEl = document.getElementById("typing");
const icebreakersEl = document.getElementById("icebreakers");
const composer = document.getElementById("composer");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const backBtn = document.getElementById("back-btn");
const chatAvatar = document.getElementById("chat-avatar");
const chatName = document.getElementById("chat-name");
const statusBar = document.getElementById("status-bar");

function initials(name) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function showScreen(screen) {
  matchScreen.classList.toggle("active", screen === "match");
  chatScreen.classList.toggle("active", screen === "chat");
}

function renderPersonas() {
  personaList.innerHTML = state.personas
    .map(
      (persona) => `
      <article class="persona-card" data-id="${persona.id}">
        <div class="avatar" style="background:${persona.avatar_color}">
          ${initials(persona.name)}
        </div>
        <div class="persona-info">
          <h2>${persona.name}, ${persona.age}</h2>
          <div class="tagline">${persona.tagline}</div>
          <div class="bio">${persona.bio}</div>
          <div class="interests">
            ${persona.interests
              .map((tag) => `<span class="interest-tag">${tag}</span>`)
              .join("")}
          </div>
        </div>
      </article>
    `
    )
    .join("");

  personaList.querySelectorAll(".persona-card").forEach((card) => {
    card.addEventListener("click", () => openChat(card.dataset.id));
  });
}

function appendMessage(role, content) {
  const bubble = document.createElement("div");
  bubble.className = `message ${role}`;
  bubble.textContent = content;
  messagesEl.appendChild(bubble);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setTyping(visible) {
  typingEl.classList.toggle("visible", visible);
  if (visible) {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
}

function renderIcebreakers(items) {
  icebreakersEl.innerHTML = items
    .map(
      (text) =>
        `<button type="button" class="icebreaker-chip" data-text="${text.replace(/"/g, "&quot;")}">${text}</button>`
    )
    .join("");

  icebreakersEl.querySelectorAll(".icebreaker-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      messageInput.value = chip.dataset.text;
      messageInput.focus();
    });
  });
}

async function openChat(personaId) {
  const persona = state.personas.find((p) => p.id === personaId);
  if (!persona) return;

  state.activePersona = persona;
  state.history = [];
  messagesEl.innerHTML = "";
  chatAvatar.textContent = initials(persona.name);
  chatAvatar.style.background = persona.avatar_color;
  chatName.textContent = `${persona.name}, ${persona.age}`;
  statusBar.textContent = "";

  appendMessage(
    "system-hint",
    `You matched with ${persona.name}. Break the ice or tap a suggestion below.`
  );

  showScreen("chat");
  messageInput.focus();

  try {
    const res = await fetch("/api/icebreakers?count=4");
    const data = await res.json();
    renderIcebreakers(data.icebreakers);
  } catch {
    renderIcebreakers([]);
  }
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message || !state.activePersona || state.loading) return;

  state.loading = true;
  sendBtn.disabled = true;
  messageInput.disabled = true;

  appendMessage("user", message);
  state.history.push({ role: "user", content: message });
  setTyping(true);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        persona_id: state.activePersona.id,
        message,
        history: state.history.slice(0, -1),
      }),
    });

    if (!res.ok) {
      throw new Error("Chat request failed");
    }

    const data = await res.json();
    setTyping(false);
    appendMessage("assistant", data.reply);
    state.history.push({ role: "assistant", content: data.reply });
    statusBar.textContent =
      data.source === "openai"
        ? "Powered by OpenAI"
        : "Demo mode — add OPENAI_API_KEY for smarter replies";
  } catch {
    setTyping(false);
    appendMessage(
      "system-hint",
      "Something went wrong. Please try again in a moment."
    );
  } finally {
    state.loading = false;
    sendBtn.disabled = false;
    messageInput.disabled = false;
    messageInput.value = "";
    messageInput.focus();
  }
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(messageInput.value);
});

backBtn.addEventListener("click", () => {
  state.activePersona = null;
  state.history = [];
  showScreen("match");
});

async function init() {
  try {
    const res = await fetch("/api/personas");
    state.personas = await res.json();
    renderPersonas();
  } catch {
    personaList.innerHTML =
      '<p class="persona-info bio">Could not load personas. Is the server running?</p>';
  }
}

init();
