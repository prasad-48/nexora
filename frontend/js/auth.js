/**
 * Auth helpers — JWT storage, login/logout, and navbar user icon & profile menu updates.
 */

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function removeToken() {
  clearAuthSession();
}

function isLoggedIn() {
  return !!getToken();
}

function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setStoredUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

async function loginUser(email, password) {
  const data = await login(email, password);
  setToken(data.access_token);
  const user = await getMe();
  setStoredUser(user);
  updateNavAuth();
  showToast(`Welcome back, ${user.full_name.split(' ')[0]}!`, 'success');
  return user;
}

async function registerUser(fullName, email, password) {
  const user = await register(fullName, email, password);
  const data = await login(email, password);
  setToken(data.access_token);
  setStoredUser(user);
  updateNavAuth();
  showToast('Account created successfully!', 'success');
  return user;
}

function logoutUser() {
  removeToken();
  updateNavAuth();
  showToast('Logged out successfully', 'info');
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 500);
}

function updateNavAuth() {
  const container = document.getElementById('nav-auth-container');
  if (!container) return;

  if (isLoggedIn()) {
    const user = getStoredUser();
    const initials = user ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase() : 'U';
    const isAdmin = user && user.is_admin;

    container.innerHTML = `
      <div class="relative group">
        <button id="user-profile-btn" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:border-cyan-500/50 transition-all text-sm font-medium">
          <div class="w-7 h-7 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold text-xs flex items-center justify-center">
            ${initials}
          </div>
          <span class="hidden md:inline text-gray-200">${user ? user.full_name.split(' ')[0] : 'Account'}</span>
          <i class="ti ti-chevron-down text-xs text-gray-400"></i>
        </button>

        <div class="absolute right-0 mt-2 w-56 glass-panel-static p-2 shadow-2xl rounded-2xl hidden group-hover:block z-50 animate-fadeIn">
          <div class="px-3 py-2 border-b border-white/10 mb-1">
            <p class="text-xs text-cyan-400 font-semibold uppercase tracking-wider">Signed in as</p>
            <p class="text-sm font-bold text-white truncate">${user ? user.full_name : ''}</p>
            <p class="text-xs text-gray-400 truncate">${user ? user.email : ''}</p>
          </div>

          ${isAdmin ? `
            <a href="admin.html" class="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-cyan-300 hover:bg-cyan-500/10 transition-colors">
              <i class="ti ti-dashboard text-base"></i>
              <span>Admin Dashboard</span>
              <span class="ml-auto badge-neon badge-cyan">Admin</span>
            </a>
          ` : ''}

          <a href="orders.html" class="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-gray-300 hover:bg-white/5 transition-colors">
            <i class="ti ti-package text-base text-purple-400"></i>
            <span>My Orders</span>
          </a>

          <a href="cart.html" class="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-gray-300 hover:bg-white/5 transition-colors">
            <i class="ti ti-shopping-cart text-base text-cyan-400"></i>
            <span>My Cart</span>
          </a>

          <button onclick="logoutUser()" class="w-full text-left flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-rose-400 hover:bg-rose-500/10 transition-colors mt-1 border-t border-white/5">
            <i class="ti ti-logout text-base"></i>
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <a href="login.html" class="glow-btn-primary py-2 px-4 text-xs sm:text-sm">
        <i class="ti ti-user text-sm"></i>
        <span>Sign In</span>
      </a>
    `;
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  if (isLoggedIn() && !getStoredUser()) {
    try {
      const user = await getMe();
      setStoredUser(user);
    } catch {
      removeToken();
    }
  }
  updateNavAuth();
});
