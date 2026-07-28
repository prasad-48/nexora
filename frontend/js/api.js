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

function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'ti-info-circle';
  if (type === 'success') icon = 'ti-circle-check';
  if (type === 'error') icon = 'ti-alert-circle';

  toast.innerHTML = `
    <i class="ti ${icon} text-lg"></i>
    <span class="text-sm font-medium">${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(50px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function handleSessionExpired() {
  clearAuthSession();
  const onLoginPage = window.location.pathname.endsWith('login.html');
  if (!onLoginPage) {
    showToast('Session expired. Please log in again.', 'error');
    setTimeout(() => {
      window.location.href = 'login.html?expired=true';
    }, 1000);
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

async function getCategories() {
  return apiRequest('/products/meta/categories');
}

// Cart endpoints
async function getBackendCart() {
  return apiRequest('/cart/');
}

async function addBackendCartItem(productId, quantity = 1) {
  return apiRequest('/cart/items', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, quantity }),
  });
}

async function removeBackendCartItem(productId) {
  return apiRequest(`/cart/items/${productId}`, {
    method: 'DELETE',
  });
}

async function clearBackendCart() {
  return apiRequest('/cart/clear', {
    method: 'DELETE',
  });
}

// Order & Payment endpoints
async function createOrder(address, items, paymentMethod = 'razorpay') {
  return apiRequest('/orders/', {
    method: 'POST',
    body: JSON.stringify({ address, items, payment_method: paymentMethod }),
  });
}

async function verifyRazorpayPayment(orderId, razorpayOrderId, razorpayPaymentId, razorpaySignature) {
  return apiRequest('/orders/verify-payment', {
    method: 'POST',
    body: JSON.stringify({
      order_id: orderId,
      razorpay_order_id: razorpayOrderId,
      razorpay_payment_id: razorpayPaymentId,
      razorpay_signature: razorpaySignature
    })
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

// Admin API endpoints
async function getAdminDashboard() {
  return apiRequest('/admin/dashboard');
}

async function getAdminOrders() {
  return apiRequest('/admin/orders');
}

async function createProduct(productData) {
  return apiRequest('/products/', {
    method: 'POST',
    body: JSON.stringify(productData),
  });
}

async function updateProduct(productId, productData) {
  return apiRequest(`/products/${productId}`, {
    method: 'PUT',
    body: JSON.stringify(productData),
  });
}

async function deleteProduct(productId) {
  return apiRequest(`/products/${productId}`, {
    method: 'DELETE',
  });
}

async function updateOrderStatus(orderId, status) {
  return apiRequest(`/orders/${orderId}/status?new_status=${status}`, {
    method: 'PATCH',
  });
}
