/**
 * Shopping cart — handles local guest cart and backend API synchronization for logged in users.
 */

const CART_KEY = 'nexora_cart';

function getLocalCart() {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY)) || [];
  } catch {
    return [];
  }
}

function saveLocalCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
}

async function getCart() {
  if (isLoggedIn()) {
    try {
      const backendItems = await getBackendCart();
      const formatted = backendItems.map(item => ({
        id: item.product.id,
        name: item.product.name,
        price: item.product.price,
        image_url: item.product.image_url,
        quantity: item.quantity,
        stock: item.product.stock
      }));
      return formatted;
    } catch (e) {
      console.warn('Failed to fetch backend cart, fallback to local', e);
      return getLocalCart();
    }
  }
  return getLocalCart();
}

async function addToCart(item) {
  if (isLoggedIn()) {
    try {
      await addBackendCartItem(item.id, item.quantity || 1);
      showToast(`${item.name} added to cart`, 'success');
      updateCartCount();
      return;
    } catch (e) {
      console.warn('Backend cart add failed, saving locally', e);
    }
  }

  const cart = getLocalCart();
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

  saveLocalCart(cart);
  showToast(`${item.name} added to cart`, 'success');
  updateCartCount();
}

async function removeFromCart(productId) {
  if (isLoggedIn()) {
    try {
      await removeBackendCartItem(productId);
    } catch (e) {
      console.warn('Backend cart remove error', e);
    }
  }
  saveLocalCart(getLocalCart().filter((i) => i.id !== productId));
  showToast('Item removed from cart', 'info');
  updateCartCount();
}

async function updateQuantity(productId, quantity) {
  if (quantity <= 0) {
    await removeFromCart(productId);
    return;
  }

  if (isLoggedIn()) {
    try {
      await addBackendCartItem(productId, quantity);
      updateCartCount();
      return;
    } catch (e) {
      console.warn('Backend cart update quantity error', e);
    }
  }

  const cart = getLocalCart();
  const item = cart.find((i) => i.id === productId);
  if (!item) return;

  item.quantity = quantity;
  saveLocalCart(cart);
  updateCartCount();
}

async function clearCart() {
  if (isLoggedIn()) {
    try {
      await clearBackendCart();
    } catch (e) {}
  }
  localStorage.removeItem(CART_KEY);
  updateCartCount();
}

async function getCartTotal() {
  const cart = await getCart();
  return cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

async function updateCartCount() {
  const badge = document.getElementById('cart-count');
  if (!badge) return;

  const cart = await getCart();
  const count = cart.reduce((sum, item) => sum + item.quantity, 0);
  badge.textContent = count;
  if (count > 0) {
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateCartCount();
});
