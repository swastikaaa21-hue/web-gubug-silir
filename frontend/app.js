// Global State
const state = {
    menu: [],
    cart: [],
    currentView: 'landing',
    searchQuery: '',
    activeCategory: 'Semua',
    selectedPayment: 'qris',
    paymentMethods: [
        { id: 'qris', name: 'QRIS', icon: 'qr-code', color: 'text-gray' },
    ],
    categories: [
        { key: 'Semua', icon: 'chef-hat' },
        { key: 'Makanan', icon: 'utensils-crossed' },
        { key: 'Minuman', icon: 'coffee' },
        { key: 'Snack', icon: 'cookie' }
    ]
};

// --- API Calls ---
async function fetchMenu() {
    try {
        const res = await fetch('/api/menu');
        const data = await res.json();
        state.menu = data;
        app.renderMenu();
    } catch (e) {
        console.error("Failed to fetch menu:", e);
    }
}

async function submitOrder(orderData) {
    try {
        const res = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });
        return await res.json();
    } catch (e) {
        console.error("Failed to submit order:", e);
        return { success: false };
    }
}

// --- App Logic ---
const app = {
    init() {
        // Init Lucide Icons
        lucide.createIcons();
        
        // Fetch Menu
        fetchMenu();
        
        // Render Initial UI
        this.renderCategories();
        this.renderPaymentMethods();
        this.selectPayment('qris');
        
        // Setup Scroll Animations
        this.setupScrollAnimations();
    },

    setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    // Optional: unobserve after animating once
                    // observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    },

    showView(viewId) {
        // Hide all views
        document.querySelectorAll('.view').forEach(el => {
            el.classList.add('hidden');
            el.classList.remove('active');
        });
        
        // Show target view
        const target = document.getElementById(`view-${viewId}`);
        if(target) {
            target.classList.remove('hidden');
            target.classList.add('active');
        }
        
        // Update nav active state
        document.querySelectorAll('.nav-link').forEach(el => {
            if (el.getAttribute('data-nav') === viewId) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });
        
        state.currentView = viewId;
        this.updateCartCount(); // re-evaluate floating cart visibility
        window.scrollTo(0, 0);
    },

    toggleCart() {
        const drawer = document.getElementById('cart-drawer');
        const overlay = document.getElementById('cart-overlay');
        
        if (drawer.classList.contains('hidden')) {
            drawer.classList.remove('hidden');
            overlay.classList.remove('hidden');
            this.renderCart();
        } else {
            drawer.classList.add('hidden');
            overlay.classList.add('hidden');
        }
    },

    // --- Rendering ---
    renderCategories() {
        const container = document.getElementById('category-filters');
        if(!container) return;
        
        container.innerHTML = state.categories.map(cat => `
            <button class="cat-btn ${state.activeCategory === cat.key ? 'active' : ''}" 
                    onclick="app.setCategory('${cat.key}')">
                <i data-lucide="${cat.icon}"></i> ${cat.key}
            </button>
        `).join('');
        lucide.createIcons();
    },

    setCategory(cat) {
        state.activeCategory = cat;
        this.renderCategories();
        this.renderMenu();
    },

    renderMenu() {
        const container = document.getElementById('menu-grid');
        if(!container) return;
        
        const searchInput = document.getElementById('search-input');
        state.searchQuery = searchInput ? searchInput.value.toLowerCase() : '';

        const filtered = state.menu.filter(item => {
            const matchCat = state.activeCategory === 'Semua' || item.category === state.activeCategory;
            const matchSearch = item.name.toLowerCase().includes(state.searchQuery) || 
                                (item.desc && item.desc.toLowerCase().includes(state.searchQuery));
            return matchCat && matchSearch;
        });

        if (filtered.length === 0) {
            container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 3rem; color: #6b7280;">Menu tidak ditemukan.</div>`;
            return;
        }

        container.innerHTML = filtered.map(item => {
            let badgeHtml = '';
            if (item.badge === 'spicy') {
                badgeHtml = `<span class="menu-badge badge-spicy">🌶️ Lv.${item.spiceLevel || item.spice_level}</span>`;
            } else if (item.badge === 'ice') {
                badgeHtml = `<span class="menu-badge badge-ice"><i data-lucide="snowflake" style="width:12px; height:12px; display:inline-block"></i> Ice</span>`;
            }

            return `
                <div class="menu-card">
                    <div class="menu-img-wrap">
                        <img src="${item.image ? encodeURI(item.image) : ''}" alt="${item.name}" class="menu-img">
                        ${badgeHtml}
                        ${item.favorite || item.is_favorite ? `<button class="fav-btn"><i data-lucide="heart" fill="currentColor"></i></button>` : ''}
                    </div>
                    <div class="menu-content">
                        <h3 class="menu-title">${item.name}</h3>
                        <p class="menu-desc">${item.desc || item.description || ''}</p>
                        <div class="menu-footer">
                            <span class="menu-price">${this.formatMoney(item.price)}</span>
                            <button class="add-btn" onclick="app.addToCart(event, ${item.id})">
                                <i data-lucide="plus"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        lucide.createIcons();
    },

    addToCart(event, id) {
        const item = state.menu.find(i => i.id === id);
        if(!item) return;

        const existing = state.cart.find(i => i.id === id);
        if (existing) {
            existing.qty += 1;
        } else {
            state.cart.push({ ...item, qty: 1 });
        }
        this.updateCartCount();
        
        // Visual feedback (could be a toast)
        const btn = event.currentTarget;
        const icon = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="check"></i>';
        lucide.createIcons();
        setTimeout(() => { btn.innerHTML = icon; lucide.createIcons(); }, 1000);
    },

    updateCartCount() {
        const count = state.cart.reduce((sum, item) => sum + item.qty, 0);
        document.getElementById('cart-count').innerText = count;
        
        // Update floating cart
        const floatingCart = document.getElementById('floating-cart');
        if (floatingCart) {
            if (count > 0 && state.currentView !== 'checkout' && state.currentView !== 'receipt') {
                document.getElementById('floating-cart-count').innerText = count;
                const total = state.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
                document.getElementById('floating-cart-total').innerText = this.formatMoney(total);
                floatingCart.classList.add('visible');
            } else {
                floatingCart.classList.remove('visible');
            }
        }
    },

    renderCart() {
        const container = document.getElementById('cart-items');
        
        if (state.cart.length === 0) {
            container.innerHTML = `<div style="text-align:center; padding: 2rem; color: #9ca3af;">Keranjang Anda kosong</div>`;
            document.getElementById('cart-total-price').innerText = 'Rp 0';
            return;
        }

        container.innerHTML = state.cart.map(item => `
            <div class="cart-item">
                <img src="${item.image ? encodeURI(item.image) : ''}" alt="${item.name}" class="cart-item-img">
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-price">${this.formatMoney(item.price)}</div>
                </div>
                <div class="cart-item-controls">
                    <button onclick="app.updateQty(${item.id}, -1)"><i data-lucide="minus"></i></button>
                    <span class="cart-item-qty">${item.qty}</span>
                    <button onclick="app.updateQty(${item.id}, 1)"><i data-lucide="plus"></i></button>
                </div>
            </div>
        `).join('');

        const total = state.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
        document.getElementById('cart-total-price').innerText = this.formatMoney(total);
        lucide.createIcons();
    },

    updateQty(id, delta) {
        const item = state.cart.find(i => i.id === id);
        if(!item) return;
        
        item.qty += delta;
        if (item.qty <= 0) {
            state.cart = state.cart.filter(i => i.id !== id);
        }
        
        this.updateCartCount();
        this.renderCart();
    },

    showCheckout() {
        if (state.cart.length === 0) {
            alert("Keranjang Anda kosong!");
            return;
        }
        this.toggleCart();
        this.showView('checkout');
        this.renderCheckoutSummary();
    },

    renderPaymentMethods() {
        const container = document.getElementById('payment-methods');
        if(!container) return;
        
        container.innerHTML = state.paymentMethods.map(pm => `
            <div class="payment-card ${state.selectedPayment === pm.id ? 'active' : ''}" 
                 onclick="app.selectPayment('${pm.id}')">
                <i data-lucide="${pm.icon}"></i>
                <span>${pm.name}</span>
            </div>
        `).join('');
        lucide.createIcons();
    },

    selectPayment(id) {
        state.selectedPayment = id;
        this.renderPaymentMethods();
        
        const qrisContainer = document.getElementById('qris-container');
        
        if (qrisContainer) {
            if (id === 'qris') {
                qrisContainer.style.display = 'block';
            } else {
                qrisContainer.style.display = 'none';
            }
        }
    },

    sendWAProof() {
        if (state.cart.length === 0) {
            alert("Keranjang Anda kosong!");
            return;
        }

        let message = "Hallo kak, aku pesan\n";
        state.cart.forEach(item => {
            message += `- ${item.qty}x ${item.name} (${this.formatMoney(item.price * item.qty)})\n`;
        });

        const notes = document.getElementById('order-notes').value;
        if (notes && notes.trim() !== '') {
            message += `\nCatatan: ${notes.trim()}`;
        }

        const encodedMessage = encodeURIComponent(message);
        const waUrl = `https://wa.me/62895414999978?text=${encodedMessage}`;
        window.open(waUrl, '_blank');
    },

    renderCheckoutSummary() {
        const container = document.getElementById('checkout-summary-items');
        
        container.innerHTML = state.cart.map(item => `
            <div class="summary-item">
                <div>
                    <span class="qty">${item.qty}x</span>
                    <span>${item.name}</span>
                </div>
                <span>${this.formatMoney(item.price * item.qty)}</span>
            </div>
        `).join('');

        const total = state.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
        document.getElementById('checkout-total-price').innerText = this.formatMoney(total);
    },

    async processCheckout() {
        if (!state.selectedPayment) {
            alert("Mohon pilih metode pembayaran.");
            return;
        }

        const total = state.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
        const notes = document.getElementById('order-notes').value;

        const orderData = {
            total_amount: total,
            payment_method: state.selectedPayment,
            notes: notes,
            items: state.cart.map(item => ({
                menu_item_id: item.id,
                quantity: item.qty
            }))
        };

        // Call API
        const result = await submitOrder(orderData);
        
        if (result.success) {
            const showReceipt = () => {
                document.getElementById('receipt-order-id').innerText = `#ORD-${result.order_id}`;
                document.getElementById('receipt-total').innerText = this.formatMoney(total);
                document.getElementById('receipt-payment').innerText = state.paymentMethods.find(p => p.id === state.selectedPayment).name;
                this.showView('receipt');
            };

            if (result.snap_token) {
                // Trigger Midtrans Snap
                window.snap.pay(result.snap_token, {
                    onSuccess: function(result){
                        showReceipt();
                    },
                    onPending: function(result){
                        alert("Menunggu pembayaran...");
                        showReceipt();
                    },
                    onError: function(result){
                        alert("Pembayaran gagal!");
                    },
                    onClose: function(){
                        alert('Anda menutup pop-up tanpa menyelesaikan pembayaran');
                    }
                });
            } else {
                // Untuk Tunai atau jika token tidak ada
                showReceipt();
            }
        } else {
            alert("Pesanan gagal diproses. Silakan coba lagi.");
        }
    },

    clearCart() {
        state.cart = [];
        this.updateCartCount();
        state.selectedPayment = '';
        this.renderPaymentMethods();
        document.getElementById('order-notes').value = '';
    },

    formatMoney(amount) {
        return 'Rp ' + amount.toLocaleString('id-ID');
    },

    // --- Admin Logic ---
    adminToken: null,

    openAdminModal() {
        const modal = document.getElementById('admin-login-modal');
        modal.style.display = 'flex';
        // Trigger reflow to ensure transition works
        void modal.offsetWidth;
        modal.style.opacity = '1';
        document.querySelector('#admin-login-modal .modal-content').style.transform = 'scale(1)';
        document.getElementById('admin-password').focus();
    },
    
    closeAdminModal() {
        document.getElementById('admin-login-modal').style.opacity = '0';
        document.querySelector('#admin-login-modal .modal-content').style.transform = 'scale(0.9)';
        setTimeout(() => {
            document.getElementById('admin-login-modal').style.display = 'none';
        }, 300);
    },

    async loginAdmin() {
        const password = document.getElementById('admin-password').value;
        try {
            const res = await fetch('/api/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });
            if(res.ok) {
                const data = await res.json();
                this.adminToken = data.token;
                
                // Show modal animation
                document.getElementById('admin-login-modal').style.display = 'flex';
                // Trigger reflow
                void document.getElementById('admin-login-modal').offsetWidth;
                document.getElementById('admin-login-modal').style.opacity = '1';
                document.querySelector('#admin-login-modal .modal-content').style.transform = 'scale(1)';
                
                setTimeout(() => {
                    this.closeAdminModal();
                    this.showView('admin');
                    this.switchAdminTab('menu');
                    document.getElementById('admin-password').value = '';
                }, 500); // small delay to see success
            } else {
                alert('Sandi salah!');
            }
        } catch(e) {
            console.error(e);
            alert('Terjadi kesalahan saat login.');
        }
    },

    logoutAdmin() {
        this.adminToken = null;
        this.showView('landing');
    },

    switchAdminTab(tab) {
        document.querySelectorAll('.admin-tab').forEach(el => {
            el.classList.remove('active');
            el.style.borderBottom = '3px solid transparent';
            el.style.color = '#666';
        });
        document.querySelectorAll('.admin-content').forEach(el => el.classList.add('hidden'));
        
        const activeTab = document.getElementById(`tab-${tab}`);
        activeTab.classList.add('active');
        activeTab.style.borderBottom = '3px solid var(--primary)';
        activeTab.style.color = 'var(--primary)';
        
        document.getElementById(`admin-content-${tab}`).classList.remove('hidden');

        if(tab === 'menu') {
            this.loadAdminMenu();
        } else if (tab === 'stats') {
            this.loadAdminStats();
        }
    },

    async loadAdminMenu() {
        try {
            const res = await fetch('/api/admin/menu');
            const data = await res.json();
            const tbody = document.getElementById('admin-menu-table-body');
            tbody.innerHTML = data.map(item => `
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 1rem;">${item.name}</td>
                    <td style="padding: 1rem;">${item.category}</td>
                    <td style="padding: 1rem;">${this.formatMoney(item.price)}</td>
                    <td style="padding: 1rem;">${item.is_active ? '<span style="color:green;font-weight:bold;">Aktif</span>' : '<span style="color:red;">Disembunyikan</span>'}</td>
                    <td style="padding: 1rem; text-align: right;">
                        <button onclick='app.editMenu(${JSON.stringify(item).replace(/'/g, "&#39;")})' style="background:var(--primary);color:white;border:none;padding:0.3rem 0.8rem;border-radius:4px;cursor:pointer;">Edit</button>
                    </td>
                </tr>
            `).join('');
        } catch(e) {
            console.error(e);
        }
    },

    async loadAdminStats() {
        const period = document.getElementById('stats-period').value;
        try {
            const res = await fetch(`/api/admin/stats?period=${period}`);
            const data = await res.json();
            
            document.getElementById('stats-revenue').innerText = this.formatMoney(data.total_revenue);
            document.getElementById('stats-items-sold').innerText = data.total_items_sold;
            
            const topItemsContainer = document.getElementById('stats-top-items');
            if(data.top_items.length === 0) {
                topItemsContainer.innerHTML = '<p style="color:#666;text-align:center;">Belum ada data penjualan.</p>';
            } else {
                topItemsContainer.innerHTML = data.top_items.map((item, idx) => `
                    <div style="display:flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                        <div>
                            <span style="font-weight:bold; color: #333; margin-right: 0.5rem;">#${idx+1}</span>
                            <span>${item.name} <small style="color:#888;">(${item.category})</small></span>
                        </div>
                        <span style="font-weight:bold; color:var(--primary);">${item.sold} terjual</span>
                    </div>
                `).join('');
            }
        } catch(e) {
            console.error(e);
        }
    },

    showAddMenuModal() {
        document.getElementById('menu-form-title').innerText = 'Tambah Menu';
        document.getElementById('menu-form-id').value = '';
        document.getElementById('menu-form-name').value = '';
        document.getElementById('menu-form-category').value = 'Makanan';
        document.getElementById('menu-form-price').value = '';
        document.getElementById('menu-form-desc').value = '';
        document.getElementById('menu-form-active').checked = true;
        document.getElementById('menu-form-modal').style.display = 'flex';
    },

    editMenu(item) {
        document.getElementById('menu-form-title').innerText = 'Edit Menu';
        document.getElementById('menu-form-id').value = item.id;
        document.getElementById('menu-form-name').value = item.name;
        document.getElementById('menu-form-category').value = item.category;
        document.getElementById('menu-form-price').value = item.price;
        document.getElementById('menu-form-desc').value = item.description || '';
        document.getElementById('menu-form-active').checked = item.is_active;
        document.getElementById('menu-form-modal').style.display = 'flex';
    },

    async saveMenu() {
        const id = document.getElementById('menu-form-id').value;
        const payload = {
            name: document.getElementById('menu-form-name').value,
            category: document.getElementById('menu-form-category').value,
            price: parseFloat(document.getElementById('menu-form-price').value),
            description: document.getElementById('menu-form-desc').value,
            is_active: document.getElementById('menu-form-active').checked
        };

        const url = id ? `/api/admin/menu/${id}` : `/api/admin/menu`;
        const method = id ? 'PUT' : 'POST';

        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if(res.ok) {
                document.getElementById('menu-form-modal').style.display = 'none';
                this.loadAdminMenu();
                fetchMenu(); // Refresh public menu
            } else {
                alert('Gagal menyimpan menu');
            }
        } catch(e) {
            console.error(e);
            alert('Terjadi kesalahan');
        }
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
