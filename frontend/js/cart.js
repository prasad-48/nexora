/**
 * Shopping cart — persisted in localStorage across page visits.
 */

const CART_KEY = 'nexora_cart';

function getCart() {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY)) || [];
  } catch {
    return [];
  }
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
}

function addToCart(item) {
  const cart = getCart();
  const existing = cart.find((i) => i.id === item.id);

  if (existing) {
    existing.quantity += item.quantity || 1;
  } else {
    cart.push({
      id: item.id,
      name: item.name,
      price: item.price,
      image_url: item.image_url || null,
      quantity: item.quantity || 1,
    });
  }

  saveCart(cart);
  updateCartCount();
}

function removeFromCart(productId) {
  saveCart(getCart().filter((i) => i.id !== productId));
  updateCartCount();
}

function updateQuantity(productId, quantity) {
  if (quantity <= 0) {
    removeFromCart(productId);
    return;
  }

  const cart = getCart();
  const item = cart.find((i) => i.id === productId);
  if (!item) return;

  item.quantity = quantity;
  saveCart(cart);
  updateCartCount();
}

function getCartTotal() {
  return getCart().reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function updateCartCount() {
  const badge = document.getElementById('cart-count');
  if (!badge) return;

  const count = getCart().reduce((sum, item) => sum + item.quantity, 0);
  badge.textContent = count;
}

function clearCart() {
  localStorage.removeItem(CART_KEY);
  updateCartCount();
}
