/**
 * Admin Panel Management logic — Dashboard, Product CRUD, Order Status Management
 */

document.addEventListener('DOMContentLoaded', async () => {
  const user = getStoredUser();
  if (!isLoggedIn() || !user || !user.is_admin) {
    showToast('Admin authorization required', 'error');
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 1200);
    return;
  }

  initAdminTabs();
  await loadDashboard();
  await loadProductsTable();
  await loadOrdersTable();
});

function initAdminTabs() {
  const tabBtns = document.querySelectorAll('.admin-tab-btn');
  const tabContents = document.querySelectorAll('.admin-tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      tabBtns.forEach(b => {
        b.classList.remove('bg-cyan-500/20', 'text-cyan-300', 'border-cyan-500/50');
        b.classList.add('text-gray-400');
      });
      btn.classList.add('bg-cyan-500/20', 'text-cyan-300', 'border-cyan-500/50');
      btn.classList.remove('text-gray-400');

      tabContents.forEach(c => {
        if (c.id === `tab-${target}`) {
          c.classList.remove('hidden');
        } else {
          c.classList.add('hidden');
        }
      });
    });
  });
}

async function loadDashboard() {
  try {
    const stats = await getAdminDashboard();

    document.getElementById('stat-revenue').textContent = `₹${stats.total_revenue.toLocaleString('en-IN')}`;
    document.getElementById('stat-orders').textContent = stats.total_orders;
    document.getElementById('stat-products').textContent = stats.total_products;
    document.getElementById('stat-users').textContent = stats.total_users;

    // Render Low Stock Table
    const lowStockContainer = document.getElementById('low-stock-list');
    if (stats.low_stock_products.length === 0) {
      lowStockContainer.innerHTML = '<p class="text-xs text-gray-400 py-2">All product inventory levels are healthy! 🎉</p>';
    } else {
      lowStockContainer.innerHTML = stats.low_stock_products.map(p => `
        <div class="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-white/5">
          <div class="flex items-center gap-3">
            <img src="${p.image_url || 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=100'}" class="w-10 h-10 object-cover rounded-lg">
            <div>
              <p class="text-sm font-semibold text-white">${p.name}</p>
              <p class="text-xs text-gray-400">Stock: <span class="text-rose-400 font-bold">${p.stock} units left</span></p>
            </div>
          </div>
          <button onclick="quickUpdateStock(${p.id}, ${p.stock + 10})" class="glow-btn-secondary py-1 px-3 text-xs">
            + Quick Restock (10)
          </button>
        </div>
      `).join('');
    }
  } catch (err) {
    showToast(err.message || 'Failed to load dashboard metrics', 'error');
  }
}

async function loadProductsTable() {
  const container = document.getElementById('admin-products-table-body');
  if (!container) return;

  try {
    const products = await getProducts();
    container.innerHTML = products.map(p => `
      <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
        <td class="px-4 py-3 text-xs font-semibold text-gray-300">#${p.id}</td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-3">
            <img src="${p.image_url || 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=100'}" class="w-10 h-10 object-cover rounded-xl border border-white/10">
            <div>
              <p class="text-sm font-bold text-white">${p.name}</p>
              <p class="text-xs text-gray-400">${p.brand}</p>
            </div>
          </div>
        </td>
        <td class="px-4 py-3 text-xs text-cyan-300 font-medium">${p.category}</td>
        <td class="px-4 py-3 text-sm font-bold text-white">₹${p.price.toLocaleString('en-IN')}</td>
        <td class="px-4 py-3">
          <span class="badge-neon ${p.stock > 5 ? 'badge-green' : 'badge-red'}">
            ${p.stock} in stock
          </span>
        </td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-2">
            <button onclick="openProductModal(${p.id})" class="p-2 rounded-xl bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20 transition-colors">
              <i class="ti ti-edit"></i>
            </button>
            <button onclick="handleDeleteProduct(${p.id})" class="p-2 rounded-xl bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-colors">
              <i class="ti ti-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    container.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-rose-400 text-sm">Error loading products</td></tr>`;
  }
}

async function loadOrdersTable() {
  const container = document.getElementById('admin-orders-table-body');
  if (!container) return;

  try {
    const orders = await getAdminOrders();
    container.innerHTML = orders.map(o => `
      <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
        <td class="px-4 py-3 text-xs font-bold text-cyan-400">#ORD-${o.id}</td>
        <td class="px-4 py-3 text-xs text-gray-300">User #${o.user_id}</td>
        <td class="px-4 py-3 text-xs text-gray-300 max-w-[200px] truncate" title="${o.address}">${o.address}</td>
        <td class="px-4 py-3 text-sm font-bold text-white">₹${o.total_amount.toLocaleString('en-IN')}</td>
        <td class="px-4 py-3">
          <span class="badge-neon ${o.payment_status === 'paid' ? 'badge-green' : 'badge-purple'}">
            ${o.payment_status || 'pending'}
          </span>
        </td>
        <td class="px-4 py-3">
          <select onchange="handleOrderStatusChange(${o.id}, this.value)" class="bg-slate-900 border border-white/10 text-xs text-gray-200 rounded-xl px-2.5 py-1.5 focus:border-cyan-400 focus:outline-none">
            <option value="pending" ${o.status === 'pending' ? 'selected' : ''}>Pending</option>
            <option value="processing" ${o.status === 'processing' ? 'selected' : ''}>Processing</option>
            <option value="shipped" ${o.status === 'shipped' ? 'selected' : ''}>Shipped</option>
            <option value="delivered" ${o.status === 'delivered' ? 'selected' : ''}>Delivered</option>
            <option value="cancelled" ${o.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
          </select>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    container.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-rose-400 text-sm">Error loading orders</td></tr>`;
  }
}

window.handleOrderStatusChange = async function(orderId, newStatus) {
  try {
    await updateOrderStatus(orderId, newStatus);
    showToast(`Order #${orderId} updated to ${newStatus}`, 'success');
    await loadDashboard();
  } catch (err) {
    showToast(err.message || 'Failed to update order status', 'error');
  }
};

window.quickUpdateStock = async function(productId, newStock) {
  try {
    const existing = await getProduct(productId);
    await updateProduct(productId, { ...existing, stock: newStock });
    showToast(`Restocked product stock to ${newStock}`, 'success');
    await loadDashboard();
    await loadProductsTable();
  } catch (err) {
    showToast('Failed to restock', 'error');
  }
};

window.handleDeleteProduct = async function(productId) {
  if (!confirm(`Are you sure you want to delete product #${productId}?`)) return;
  try {
    await deleteProduct(productId);
    showToast('Product deleted successfully', 'success');
    await loadProductsTable();
    await loadDashboard();
  } catch (err) {
    showToast(err.message || 'Failed to delete product', 'error');
  }
};

window.openProductModal = async function(productId = null) {
  const modal = document.getElementById('product-modal');
  const form = document.getElementById('product-form');
  const title = document.getElementById('modal-title');

  form.reset();
  document.getElementById('product-id').value = productId || '';

  if (productId) {
    title.textContent = `Edit Product #${productId}`;
    try {
      const p = await getProduct(productId);
      document.getElementById('p-name').value = p.name;
      document.getElementById('p-brand').value = p.brand;
      document.getElementById('p-category').value = p.category;
      document.getElementById('p-price').value = p.price;
      document.getElementById('p-old-price').value = p.old_price || '';
      document.getElementById('p-stock').value = p.stock;
      document.getElementById('p-rating').value = p.rating;
      document.getElementById('p-image').value = p.image_url || '';
      document.getElementById('p-desc').value = p.description;
      document.getElementById('p-featured').checked = p.is_featured;
    } catch (e) {
      showToast('Could not load product details', 'error');
      return;
    }
  } else {
    title.textContent = 'Add New Product';
  }

  modal.classList.remove('hidden');
  modal.classList.add('flex');
};

window.closeProductModal = function() {
  const modal = document.getElementById('product-modal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
};

window.saveProductSubmit = async function(e) {
  e.preventDefault();
  const productId = document.getElementById('product-id').value;

  const data = {
    name: document.getElementById('p-name').value,
    brand: document.getElementById('p-brand').value,
    category: document.getElementById('p-category').value,
    price: parseFloat(document.getElementById('p-price').value),
    old_price: document.getElementById('p-old-price').value ? parseFloat(document.getElementById('p-old-price').value) : null,
    stock: parseInt(document.getElementById('p-stock').value),
    rating: parseFloat(document.getElementById('p-rating').value) || 0.0,
    image_url: document.getElementById('p-image').value || null,
    description: document.getElementById('p-desc').value,
    is_featured: document.getElementById('p-featured').checked
  };

  try {
    if (productId) {
      await updateProduct(productId, data);
      showToast('Product updated successfully', 'success');
    } else {
      await createProduct(data);
      showToast('Product created successfully', 'success');
    }
    closeProductModal();
    await loadProductsTable();
    await loadDashboard();
  } catch (err) {
    showToast(err.message || 'Failed to save product', 'error');
  }
};
