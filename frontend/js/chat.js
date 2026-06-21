/**
 * Floating AI chat widget — bottom-right bubble that expands into a chat panel.
 */

function initChatWidget() {
  const container = document.getElementById('chat-widget-container');
  if (!container) return;

  container.innerHTML = `
    <div id="chat-panel" class="fixed bottom-20 sm:bottom-24 right-4 sm:right-6 z-50 w-[calc(100vw-2rem)] sm:w-[360px] max-w-[360px] h-[min(480px,calc(100vh-6rem))] bg-white rounded-2xl shadow-card border border-gray-100 hidden flex-col overflow-hidden">
      <div class="bg-[#0a0a0a] px-5 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-indigo-500/20 flex items-center justify-center">
            <i class="ti ti-robot text-indigo-400 text-lg"></i>
          </div>
          <div>
            <p class="text-white text-sm font-semibold">Nexora Assistant</p>
            <p class="text-gray-400 text-xs">Ask about products & orders</p>
          </div>
        </div>
        <button id="chat-close" type="button" class="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors flex items-center justify-center">
          <i class="ti ti-x text-sm"></i>
        </button>
      </div>

      <div id="chat-messages" class="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-[#f7f7f9]"></div>

      <div class="px-4 py-3 border-t border-gray-100 bg-white">
        <form id="chat-form" class="flex gap-2">
          <input
            id="chat-input"
            type="text"
            placeholder="Ask anything..."
            autocomplete="off"
            class="flex-1 px-4 py-2.5 rounded-xl bg-gray-50 border-0 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 placeholder:text-gray-400"
          >
          <button type="submit" id="chat-send" class="w-10 h-10 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white flex items-center justify-center transition-colors shrink-0">
            <i class="ti ti-send text-sm"></i>
          </button>
        </form>
      </div>
    </div>

    <button id="chat-toggle" type="button" class="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-indigo-500 hover:bg-indigo-400 text-white shadow-lg shadow-indigo-500/30 flex items-center justify-center transition-colors">
      <i class="ti ti-message-circle text-xl sm:text-2xl"></i>
    </button>
  `;

  const panel = document.getElementById('chat-panel');
  const toggle = document.getElementById('chat-toggle');
  const closeBtn = document.getElementById('chat-close');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');
  const sendBtn = document.getElementById('chat-send');

  function openChat() {
    panel.classList.remove('hidden');
    panel.classList.add('flex');
    toggle.classList.add('hidden');
    input.focus();
  }

  function closeChat() {
    panel.classList.add('hidden');
    panel.classList.remove('flex');
    toggle.classList.remove('hidden');
  }

  function appendMessage(text, role) {
    const isUser = role === 'user';
    const bubble = document.createElement('div');
    bubble.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;
    bubble.innerHTML = `
      <div class="max-w-[85%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
        isUser
          ? 'bg-indigo-500 text-white rounded-br-md'
          : 'bg-white text-gray-700 shadow-sm border border-gray-100 rounded-bl-md'
      }">${escapeHtml(text)}</div>
    `;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }

  function appendLoading() {
    const el = document.createElement('div');
    el.id = 'chat-loading';
    el.className = 'flex justify-start';
    el.innerHTML = `
      <div class="px-4 py-2.5 rounded-2xl rounded-bl-md bg-white shadow-sm border border-gray-100 text-sm text-gray-400">
        <span class="inline-flex gap-1">
          <span class="animate-bounce">·</span>
          <span class="animate-bounce" style="animation-delay: 0.15s">·</span>
          <span class="animate-bounce" style="animation-delay: 0.3s">·</span>
        </span>
      </div>
    `;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }

  function removeLoading() {
    const el = document.getElementById('chat-loading');
    if (el) el.remove();
  }

  async function handleSend() {
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    input.disabled = true;
    sendBtn.disabled = true;

    appendMessage(text, 'user');
    appendLoading();

    try {
      const data = await sendChatMessage(text);
      removeLoading();
      appendMessage(data.reply, 'bot');
    } catch (err) {
      removeLoading();
      appendMessage(err.message || 'Something went wrong. Please try again.', 'bot');
    }

    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }

  toggle.addEventListener('click', openChat);
  closeBtn.addEventListener('click', closeChat);
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    handleSend();
  });

  appendMessage('Hi! I can help you find products, check specs, or answer questions about Nexora.', 'bot');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', initChatWidget);
