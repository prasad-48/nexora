/**
 * Centralized API client — all backend calls go through these functions.
 * Automatically attaches the JWT Bearer token when one is stored in localStorage.
 */

const TOKEN_KEY = 'nexora_token';
const USER_KEY = 'nexora_user';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function handleSessionExpired() {
  clearAuthSession();
  const onLoginPage = window.location.pathname.endsWith('login.html');
  if (!onLoginPage) {
    window.location.href = 'login.html?expired=true';
  }
}

async function apiRequest(endpoint, options = {}) {
  const { skipAuth = false, headers: extraHeaders = {}, ...fetchOptions } = options;
  const headers = { 'Content-Type': 'application/json', ...extraHeaders };

  const token = skipAuth ? null : localStorage.getItem(TOKEN_KEY);
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, { ...fetchOptions, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body.detail;
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map((d) => d.msg || d).join(', ')
        : `Request failed (${res.status})`;

    if (res.status === 401 && token && !skipAuth) {
      handleSessionExpired();
      throw new ApiError('Session expired, please log in again', 401);
    }

    throw new ApiError(message, res.status);
  }

  if (res.status === 204) return null;
  return res.json();
}

async function register(fullName, email, password) {
  return apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ full_name: fullName, email, password }),
    skipAuth: true,
  });
}

async function login(email, password) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
    skipAuth: true,
  });
}

async function getMe() {
  return apiRequest('/auth/me');
}

async function getProducts({ search, category, minPrice, maxPrice, featured } = {}) {
  const params = new URLSearchParams();
  if (search) params.set('search', search);
  if (category) params.set('category', category);
  if (minPrice != null) params.set('min_price', minPrice);
  if (maxPrice != null) params.set('max_price', maxPrice);
  if (featured != null) params.set('featured', featured);
  const query = params.toString();
  return apiRequest(`/products${query ? `?${query}` : ''}`);
}

async function getProduct(productId) {
  return apiRequest(`/products/${productId}`);
}

async function createOrder(address, items) {
  return apiRequest('/orders/', {
    method: 'POST',
    body: JSON.stringify({ address, items }),
  });
}

async function getMyOrders() {
  return apiRequest('/orders/me');
}

async function sendChatMessage(message) {
  const endpoint = localStorage.getItem(TOKEN_KEY) ? '/chat/me' : '/chat/';
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}
