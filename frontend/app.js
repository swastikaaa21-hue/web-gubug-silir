// Global State
const state = {
    menu: [],
    cart: [],
    currentView: 'landing',
    searchQuery: '',
    activeCategory: 'Semua',
    selectedPayment: '',
    paymentMethods: [
        { id: 'cash', name: 'Tunai', icon: 'banknote', color: 'text-green' },
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
                        <img src="${item.image}" alt="${item.name}" class="menu-img">
                        ${badgeHtml}
                        ${item.favorite || item.is_favorite ? `<button class="fav-btn"><i data-lucide="heart" fill="currentColor"></i></button>` : ''}
                    </div>
                    <div class="menu-content">
                        <h3 class="menu-title">${item.name}</h3>
                        <p class="menu-desc">${item.desc || item.description || ''}</p>
                        <div class="menu-footer">
                            <span class="menu-price">${this.formatMoney(item.price)}</span>
                            <button class="add-btn" onclick="app.addToCart(${item.id})">
                                <i data-lucide="plus"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        lucide.createIcons();
    },

    addToCart(id) {
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
                <img src="${item.image}" alt="${item.name}" class="cart-item-img">
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
                qrisContainer.classList.remove('hidden');
            } else {
                qrisContainer.classList.add('hidden');
            }
        }
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
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
