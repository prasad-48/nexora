/**
 * Floating AI chat widget — bottom-right futuristic bubble that expands into a chat panel.
 */

function initChatWidget() {
  const container = document.getElementById('chat-widget-container');
  if (!container) return;

  container.innerHTML = `
    <div id="chat-panel" class="fixed bottom-20 sm:bottom-24 right-4 sm:right-6 z-50 w-[calc(100vw-2rem)] sm:w-[380px] max-w-[380px] h-[min(520px,calc(100vh-6rem))] glass-panel-static flex-col overflow-hidden shadow-2xl border border-cyan-500/30 hidden animate-fadeIn">
      <!-- Header -->
      <div class="bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950 px-5 py-4 flex items-center justify-between border-b border-white/10">
        <div class="flex items-center gap-3">
          <div class="relative w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center p-[2px]">
            <div class="w-full h-full bg-slate-950 rounded-full flex items-center justify-center">
              <i class="ti ti-cpu text-cyan-400 text-xl"></i>
            </div>
            <span class="absolute bottom-0 right-0 w-3 h-3 bg-emerald-400 border-2 border-slate-950 rounded-full"></span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <p class="text-white text-sm font-bold tracking-wide">Nexora AI</p>
              <span class="badge-neon badge-cyan text-[9px] py-0 px-1.5">GPT-v2</span>
            </div>
            <p class="text-cyan-300/70 text-xs">Electronics & Order Assistant</p>
          </div>
        </div>
        <button id="chat-close" type="button" class="w-8 h-8 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors flex items-center justify-center">
          <i class="ti ti-x text-sm"></i>
        </button>
      </div>

      <!-- Quick Suggestion Chips -->
      <div class="px-4 py-2 bg-slate-950/60 border-b border-white/5 flex gap-2 overflow-x-auto no-scrollbar">
        <button type="button" onclick="sendQuickChat('Show laptops under ₹60000')" class="chip-btn text-xs px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 hover:bg-cyan-500/20 whitespace-nowrap">
          ⚡ Best Laptops
        </button>
        <button type="button" onclick="sendQuickChat('Track my recent order')" class="chip-btn text-xs px-2.5 py-1 rounded-lg bg-purple-500/10 text-purple-300 border border-purple-500/20 hover:bg-purple-500/20 whitespace-nowrap">
          📦 Track Order
        </button>
        <button type="button" onclick="sendQuickChat('Compare flagship phones')" class="chip-btn text-xs px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 hover:bg-emerald-500/20 whitespace-nowrap">
          ⚖️ Compare
        </button>
      </div>

      <!-- Messages Body -->
      <div id="chat-messages" class="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-slate-950/80"></div>

      <!-- Footer Input -->
      <div class="px-4 py-3 border-t border-white/10 bg-slate-950">
        <form id="chat-form" class="flex gap-2">
          <input
            id="chat-input"
            type="text"
            placeholder="Ask about products, specs, tracking..."
            autocomplete="off"
            class="input-futuristic py-2 text-xs"
          >
          <button type="submit" id="chat-send" class="glow-btn-primary px-3 py-2 rounded-xl text-sm shrink-0">
            <i class="ti ti-send"></i>
          </button>
        </form>
      </div>
    </div>

    <!-- Floating Avatar Trigger Button -->
    <button id="chat-toggle" type="button" class="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full chat-avatar-glow bg-gradient-to-tr from-cyan-500 via-indigo-600 to-purple-600 text-white shadow-2xl flex items-center justify-center transition-transform hover:scale-110">
      <i class="ti ti-sparkles text-2xl"></i>
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

  function formatText(raw) {
    let html = escapeHtml(raw);
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/_(.*?)_/g, '<em>$1</em>');
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  function appendMessage(text, role) {
    const isUser = role === 'user';
    const bubble = document.createElement('div');
    bubble.className = `flex ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`;
    bubble.innerHTML = `
      <div class="max-w-[88%] px-4 py-2.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
        isUser
          ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-br-none shadow-lg'
          : 'glass-panel-static text-gray-200 border border-white/10 rounded-bl-none'
      }">${formatText(text)}</div>
    `;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }

  function appendLoading() {
    const el = document.createElement('div');
    el.id = 'chat-loading';
    el.className = 'flex justify-start';
    el.innerHTML = `
      <div class="px-4 py-2.5 rounded-2xl rounded-bl-none glass-panel-static border border-white/10 text-xs text-cyan-400">
        <span class="inline-flex gap-1 items-center">
          <span>AI analyzing</span>
          <span class="animate-bounce">.</span>
          <span class="animate-bounce" style="animation-delay: 0.15s">.</span>
          <span class="animate-bounce" style="animation-delay: 0.3s">.</span>
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

  window.sendQuickChat = function(query) {
    input.value = query;
    handleSend();
  };

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

  appendMessage('Greetings! ⚡ I am your Nexora AI Assistant. Ask me anything about electronics, product specs, comparison, or tracking your order!', 'bot');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', initChatWidget);
