/**
 * Auth helpers — JWT storage, login/logout, and navbar user icon updates.
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
  return user;
}

async function registerUser(fullName, email, password) {
  const user = await register(fullName, email, password);
  const data = await login(email, password);
  setToken(data.access_token);
  setStoredUser(user);
  updateNavAuth();
  return user;
}

function logoutUser() {
  removeToken();
  updateNavAuth();
}

function updateNavAuth() {
  const link = document.getElementById('nav-auth-link');
  if (!link) return;

  if (isLoggedIn()) {
    const user = getStoredUser();
    link.href = 'orders.html';
    link.title = user ? user.full_name : 'My orders';
    link.innerHTML = '<i class="ti ti-user-check text-[18px] text-indigo-400"></i>';
  } else {
    link.href = 'login.html';
    link.title = 'Sign in';
    link.innerHTML = '<i class="ti ti-user text-[18px]"></i>';
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
