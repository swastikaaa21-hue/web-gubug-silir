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
        if (app && app.showToast) {
            app.showToast("Gagal memuat menu. Periksa koneksi internet Anda.", "error");
        }
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
        if (app && app.showToast) {
            app.showToast("Pesanan gagal diproses. Server tidak merespon.", "error");
        }
        return { success: false };
    }
}

// --- App Logic ---
const app = {
    init() {
        // Init Lucide Icons
        lucide.createIcons();
        
        // Load cart from localStorage
        this.loadCart();
        
        // Load admin token
        const savedToken = localStorage.getItem('gubugsilir_admin_token');
        if (savedToken) {
            this.adminToken = savedToken;
        }

        // Fetch Menu
        fetchMenu();
        
        // Render Initial UI
        this.renderCategories();
        this.renderPaymentMethods();
        this.selectPayment('qris');
        
        // Setup Scroll Animations
        this.setupScrollAnimations();
    },

    loadCart() {
        const savedCart = localStorage.getItem('gubugsilir_cart');
        if (savedCart) {
            try {
                state.cart = JSON.parse(savedCart);
                this.updateCartCount();
            } catch (e) {
                console.error('Failed to parse saved cart');
            }
        }
    },

    saveCart() {
        localStorage.setItem('gubugsilir_cart', JSON.stringify(state.cart));
    },

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'info';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'alert-circle';
        
        toast.innerHTML = `<i data-lucide="${icon}"></i> <span>${message}</span>`;
        container.appendChild(toast);
        lucide.createIcons();
        
        // Show animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after 3s
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
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
        
        // Hide navbar if admin view, adjust body padding for fixed navbar
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (viewId === 'admin') {
                navbar.style.display = 'none';
                document.body.style.paddingTop = '0';
            } else {
                navbar.style.display = 'flex';
                document.body.style.paddingTop = '';
            }
        }
        
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
            if (item.category && item.category.startsWith('Varian - ')) return false;
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
            return `
                <div class="menu-card" style="cursor: pointer;" onclick="app.showMenuDetail(${item.id})">
                    <div class="menu-img-wrap">
                        <img src="${item.image || ''}" alt="${item.name}" loading="lazy" class="menu-img" ${(item.image && item.image.includes('gelas')) || item.name === 'Kelapa Muda Utuh' ? 'style="object-position: center 15%;"' : ''}>
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

    populateVariantModal(variantCategory, ulId) {
        const ul = document.getElementById(ulId);
        if (!ul) return;
        const variants = state.menu.filter(i => i.category === variantCategory);
        if (variants.length === 0) {
            ul.innerHTML = '<li style="padding: 0.5rem 0; color: #666; text-align: center;">Tidak ada varian yang tersedia saat ini.</li>';
            return;
        }
        ul.innerHTML = variants.map(v => `
            <li style="padding: 0; margin-bottom: 0.5rem;">
                <button onclick="app.addVariantToCart(event, ${v.id}, '${ulId.split('-')[0]}-popup-modal')" 
                        style="width: 100%; text-align: left; background: white; border: 1px solid #ddd; padding: 0.8rem 1rem; border-radius: 8px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                    <span style="font-weight: 500;">${v.name}</span> 
                    <strong style="color: var(--primary);">Rp ${v.price.toLocaleString('id-ID')} <i data-lucide="plus" style="width: 16px; height: 16px; vertical-align: middle; margin-left: 0.5rem;"></i></strong>
                </button>
            </li>
        `).join('');
        lucide.createIcons();
    },

    addVariantToCart(event, id, modalId) {
        const item = state.menu.find(i => i.id === id);
        if(!item) return;

        const existing = state.cart.find(i => i.id === id);
        if (existing) {
            existing.qty += 1;
        } else {
            state.cart.push({ ...item, qty: 1 });
        }
        this.updateCartCount();

        // Visual feedback
        const btn = event.currentTarget;
        const icon = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="check" style="width: 16px; height: 16px;"></i> Berhasil ditambahkan';
        lucide.createIcons();
        setTimeout(() => { 
            btn.innerHTML = icon; 
            lucide.createIcons(); 
        }, 800);
    },

    addToCart(event, id) {
        if (event) event.stopPropagation();
        const item = state.menu.find(i => i.id === id);
        if(!item) return;

        let isPopupTrigger = false;

        if (item.name === 'Es Teh Jumbo') {
            const modal = document.getElementById('teh-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Es Teh Jumbo', 'teh-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }

        if (item.name === 'Pop Ice') {
            const modal = document.getElementById('popice-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Pop Ice', 'popice-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }

        if (item.name === 'Extra Joss') {
            const modal = document.getElementById('extrajoss-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Extra Joss', 'extrajoss-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }

        if (item.name === 'Nutrisari') {
            const modal = document.getElementById('nutrisari-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Nutrisari', 'nutrisari-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }

        if (item.name === 'Es Good Day') {
            const modal = document.getElementById('goodday-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Es Good Day', 'goodday-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }

        if (item.name === 'Es Kelapa Muda') {
            const modal = document.getElementById('kelapa-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Es Kelapa Muda', 'kelapa-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }

        if (item.name === 'Kelapa Muda Utuh') {
            const modal = document.getElementById('kelapa-utuh-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Kelapa Muda Utuh', 'kelapa-utuh-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }

        if (item.name === 'Gorengan') {
            const modal = document.getElementById('gorengan-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Gorengan', 'gorengan-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }

        if (item.name === 'Seblak') {
            const modal = document.getElementById('seblak-popup-modal');
            if (modal) {
                this.populateVariantModal('Varian - Seblak', 'seblak-variant-list');
                modal.style.display = 'flex';
                void modal.offsetWidth;
                modal.style.opacity = '1';
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) modalContent.style.transform = 'scale(1)';
            }
            isPopupTrigger = true;
        }
        
        // Prevent base items from entering cart if they only serve to trigger popups
        if (isPopupTrigger) return;

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

    showMenuDetail(id) {
        const item = state.menu.find(i => i.id === id);
        if(!item) return;

        const imgEl = document.getElementById('detail-modal-img');
        if (item.image) {
            imgEl.src = item.image;
            imgEl.style.display = 'block';
        } else {
            imgEl.style.display = 'none';
        }
        
        document.getElementById('detail-modal-title').innerText = item.name;
        document.getElementById('detail-modal-desc').innerText = item.desc || item.description || 'Deskripsi tidak tersedia.';
        document.getElementById('detail-modal-price').innerText = this.formatMoney(item.price);
        
        const btn = document.getElementById('detail-modal-add-btn');
        btn.onclick = (e) => {
            this.addToCart(e, id);
            this.closeMenuDetail();
        };

        const modal = document.getElementById('menu-detail-modal');
        modal.style.display = 'flex';
        void modal.offsetWidth;
        modal.style.opacity = '1';
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) modalContent.style.transform = 'scale(1)';
    },

    closeMenuDetail() {
        const modal = document.getElementById('menu-detail-modal');
        modal.style.opacity = '0';
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) modalContent.style.transform = 'scale(0.9)';
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
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
        
        this.saveCart();
    },

    renderCart() {
        const container = document.getElementById('cart-items');
        
        if (state.cart.length === 0) {
            container.innerHTML = `<div style="text-align:center; padding: 2rem; color: #9ca3af;">Keranjang Anda kosong</div>`;
            document.getElementById('cart-total-price').innerText = 'Rp 0';
            return;
        }

        container.innerHTML = state.cart.map(item => `
            <div class="cart-item" style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                <div class="cart-item-info" style="flex: 1;">
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

    async submitAndSendWA() {
        if (state.cart.length === 0) {
            alert("Keranjang Anda kosong!");
            return;
        }
        if (!state.selectedPayment) {
            alert("Mohon pilih metode pembayaran.");
            return;
        }

        const total = state.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
        const notes = document.getElementById('order-notes').value;

        // Siapkan data pesanan untuk backend
        const orderData = {
            total_amount: total,
            payment_method: state.selectedPayment,
            notes: notes,
            items: state.cart.map(item => ({
                menu_item_id: item.id,
                quantity: item.qty
            }))
        };

        // Simpan pesanan ke database
        const result = await submitOrder(orderData);
        
        if (!result.success) {
            alert("Pesanan gagal diproses. Silakan coba lagi.");
            return;
        }

        // Siapkan pesan WhatsApp
        let message = "Hallo kak, aku pesan\n";
        state.cart.forEach(item => {
            message += `- ${item.qty}x ${item.name} (${this.formatMoney(item.price * item.qty)})\n`;
        });
        if (notes && notes.trim() !== '') {
            message += `\nCatatan: ${notes.trim()}`;
        }
        const encodedMessage = encodeURIComponent(message);
        const waUrl = `https://wa.me/62895414999978?text=${encodedMessage}`;

        // Isi data struk
        document.getElementById('receipt-order-id').innerText = `#ORD-${result.order_id}`;
        document.getElementById('receipt-payment').innerText = state.paymentMethods.find(p => p.id === state.selectedPayment)?.name || 'Tunai';
        
        const now = new Date();
        document.getElementById('receipt-date').innerText = now.toLocaleDateString('id-ID');
        document.getElementById('receipt-time').innerText = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });

        const tbody = document.getElementById('receipt-table-body');
        tbody.innerHTML = state.cart.map(item => `
            <tr style="border-bottom: 1px dashed #eee;">
                <td style="padding: 12px 8px; text-align: center; color: #333;">${item.name}</td>
                <td style="padding: 12px 8px; text-align: center; color: #333;">${item.qty}</td>
                <td style="padding: 12px 8px; text-align: center; color: #333;">${this.formatMoney(item.price)}</td>
                <td style="padding: 12px 8px; text-align: center; color: #333; font-weight: 500;">${this.formatMoney(item.price * item.qty)}</td>
            </tr>
        `).join('');
        document.getElementById('receipt-total').innerText = this.formatMoney(total);

        // Pindah ke halaman struk dan buka WA
        this.showView('receipt');
        window.open(waUrl, '_blank');
    },

    downloadReceiptPDF() {
        // Gulir ke atas untuk mencegah bug html2canvas memotong elemen
        window.scrollTo(0, 0);
        
        const element = document.getElementById('receipt-print-area');
        const opt = {
            margin:       [4, 3, 3, 3], // [top, right, bottom, left] or [top, left, bottom, right] dalam mm
            filename:     `Invoice_${document.getElementById('receipt-order-id').innerText}.pdf`,
            image:        { type: 'jpeg', quality: 1 },
            html2canvas:  { scale: 2, useCORS: true, scrollY: 0 },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak:    { mode: 'avoid-all' }
        };
        html2pdf().set(opt).from(element).save();
        // Reset state
        state.cart = [];
        this.updateCartCount();
        state.selectedPayment = '';
        this.renderPaymentMethods();
        document.getElementById('order-notes').value = '';
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
                localStorage.setItem('gubugsilir_admin_token', data.token);
                
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
        localStorage.removeItem('gubugsilir_admin_token');
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
            const res = await fetch('/api/admin/menu', {
                headers: { 'Authorization': `Bearer ${this.adminToken}` }
            });
            if (res.status === 401) {
                this.showToast('Sesi berakhir, silakan login kembali', 'error');
                this.logoutAdmin();
                return;
            }
            this.adminMenuData = await res.json();
            this.renderAdminMenuTable();
        } catch(e) {
            console.error(e);
        }
    },

    filterAdminMenu(query) {
        this.adminSearchQuery = (query || '').toLowerCase();
        this.renderAdminMenuTable();
    },

    renderAdminMenuTable() {
        const tbody = document.getElementById('admin-menu-table-body');
        if (!tbody) return;
        
        const data = this.adminSearchQuery 
            ? this.adminMenuData.filter(item => 
                (item.name && item.name.toLowerCase().includes(this.adminSearchQuery)) || 
                (item.category && item.category.toLowerCase().includes(this.adminSearchQuery))
              )
            : this.adminMenuData;

        const mainMenus = data.filter(item => !item.category.startsWith('Varian - '));
        const subMenus = data.filter(item => item.category.startsWith('Varian - '));

        let html = '';
        mainMenus.forEach(main => {
            html += `
            <tr style="border-bottom: 1px solid #eee; background: white;">
                <td style="padding: 1rem; font-weight: bold;">${main.name}</td>
                <td style="padding: 1rem;">${main.category}</td>
                <td style="padding: 1rem;">${this.formatMoney(main.price)}</td>
                <td style="padding: 1rem;">${main.is_active ? '<span style="color:green;font-weight:bold;">Aktif</span>' : '<span style="color:red;">Disembunyikan</span>'}</td>
                <td style="padding: 1rem; text-align: right;">
                    <button onclick='app.editMenu(${JSON.stringify(main).replace(/'/g, "&#39;")})' style="background:var(--primary);color:white;border:none;padding:0.3rem 0.8rem;border-radius:4px;cursor:pointer; margin-right: 0.5rem;">Edit</button>
                    <button onclick='app.triggerImageUpload(${main.id})' style="background:#3b82f6;color:white;border:none;padding:0.3rem 0.8rem;border-radius:4px;cursor:pointer; margin-right: 0.5rem;"><i data-lucide="image" style="width:14px;height:14px;display:inline-block;vertical-align:middle;"></i> Gambar</button>
                    <button onclick='app.showAddSubMenuModal("${main.name}")' style="background:#10b981;color:white;border:none;padding:0.3rem 0.8rem;border-radius:4px;cursor:pointer; margin-right: 0.5rem;">+ Sub-Menu</button>
                    <button onclick='app.confirmDeleteMenu(${main.id}, "${main.name.replace(/"/g, "&quot;")}", false)' style="background:#ef4444;color:white;border:none;padding:0.3rem 0.8rem;border-radius:4px;cursor:pointer;"><i data-lucide="trash-2" style="width:14px;height:14px;display:inline-block;vertical-align:middle;"></i> Hapus</button>
                </td>
            </tr>`;
            
            const variants = subMenus.filter(sub => sub.category === `Varian - ${main.name}`);
            variants.forEach(variant => {
                html += `
                <tr style="border-bottom: 1px solid #eee; background: #f9fafb;">
                    <td style="padding: 0.75rem 1rem 0.75rem 3rem; color: #4b5563;">└ ${variant.name}</td>
                    <td style="padding: 0.75rem 1rem; color: #6b7280; font-size: 0.9em;">${variant.category}</td>
                    <td style="padding: 0.75rem 1rem; color: #4b5563;">${this.formatMoney(variant.price)}</td>
                    <td style="padding: 0.75rem 1rem;">${variant.is_active ? '<span style="color:green;font-size:0.9em;">Aktif</span>' : '<span style="color:red;font-size:0.9em;">Disembunyikan</span>'}</td>
                    <td style="padding: 0.75rem 1rem; text-align: right;">
                        <button onclick='app.editMenu(${JSON.stringify(variant).replace(/'/g, "&#39;")})' style="background:var(--primary);color:white;border:none;padding:0.2rem 0.6rem;border-radius:4px;cursor:pointer;font-size:0.85em;margin-right: 0.5rem;">Edit</button>
                        <button onclick='app.triggerImageUpload(${variant.id})' style="background:#3b82f6;color:white;border:none;padding:0.2rem 0.6rem;border-radius:4px;cursor:pointer;font-size:0.85em;margin-right: 0.5rem;">Gambar</button>
                        <button onclick='app.confirmDeleteMenu(${variant.id}, "${variant.name.replace(/"/g, "&quot;")}", true)' style="background:#ef4444;color:white;border:none;padding:0.2rem 0.6rem;border-radius:4px;cursor:pointer;font-size:0.85em;"><i data-lucide="trash-2" style="width:12px;height:12px;display:inline-block;vertical-align:middle;"></i> Hapus</button>
                    </td>
                </tr>`;
            });
        });
        
        const renderedVariantIds = new Set();
        mainMenus.forEach(main => {
            subMenus.filter(sub => sub.category === `Varian - ${main.name}`).forEach(v => renderedVariantIds.add(v.id));
        });
        
        const orphanSubMenus = subMenus.filter(sub => !renderedVariantIds.has(sub.id));
        orphanSubMenus.forEach(variant => {
            html += `
            <tr style="border-bottom: 1px solid #eee; background: #f9fafb;">
                <td style="padding: 0.75rem 1rem 0.75rem 3rem; color: #4b5563;">└ ${variant.name}</td>
                <td style="padding: 0.75rem 1rem; color: #6b7280; font-size: 0.9em;">${variant.category}</td>
                <td style="padding: 0.75rem 1rem; color: #4b5563;">${this.formatMoney(variant.price)}</td>
                <td style="padding: 0.75rem 1rem;">${variant.is_active ? '<span style="color:green;font-size:0.9em;">Aktif</span>' : '<span style="color:red;font-size:0.9em;">Disembunyikan</span>'}</td>
                <td style="padding: 0.75rem 1rem; text-align: right;">
                    <button onclick='app.editMenu(${JSON.stringify(variant).replace(/'/g, "&#39;")})' style="background:var(--primary);color:white;border:none;padding:0.2rem 0.6rem;border-radius:4px;cursor:pointer;font-size:0.85em;margin-right:0.5rem;">Edit</button>
                    <button onclick='app.triggerImageUpload(${variant.id})' style="background:#3b82f6;color:white;border:none;padding:0.2rem 0.6rem;border-radius:4px;cursor:pointer;font-size:0.85em;margin-right:0.5rem;">Gambar</button>
                    <button onclick='app.confirmDeleteMenu(${variant.id}, "${variant.name.replace(/"/g, "&quot;")}", true)' style="background:#ef4444;color:white;border:none;padding:0.2rem 0.6rem;border-radius:4px;cursor:pointer;font-size:0.85em;"><i data-lucide="trash-2" style="width:12px;height:12px;display:inline-block;vertical-align:middle;"></i> Hapus</button>
                </td>
            </tr>`;
        });

        tbody.innerHTML = html;
        lucide.createIcons();
    },

    async loadAdminStats() {
        const period = document.getElementById('stats-period').value;
        try {
            const res = await fetch(`/api/admin/stats?period=${period}`, {
                headers: { 'Authorization': `Bearer ${this.adminToken}` }
            });
            if (res.status === 401) {
                this.showToast('Sesi berakhir, silakan login kembali', 'error');
                this.logoutAdmin();
                return;
            }
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
        
        const catSelect = document.getElementById('menu-form-category');
        // Reset to default options if there were custom ones
        Array.from(catSelect.options).forEach(opt => {
            if (opt.value.startsWith('Varian - ')) opt.remove();
        });
        catSelect.value = 'Makanan';
        catSelect.disabled = false;
        
        document.getElementById('menu-form-price').value = '';
        document.getElementById('menu-form-desc').value = '';
        document.getElementById('menu-form-active').checked = true;
        document.getElementById('menu-form-modal').style.display = 'flex';
    },

    showAddSubMenuModal(parentMenuName) {
        document.getElementById('menu-form-title').innerText = `Tambah Sub-Menu (${parentMenuName})`;
        document.getElementById('menu-form-id').value = '';
        document.getElementById('menu-form-name').value = '';
        
        const catSelect = document.getElementById('menu-form-category');
        const customCat = `Varian - ${parentMenuName}`;
        let exists = false;
        for (let i = 0; i < catSelect.options.length; i++) {
            if (catSelect.options[i].value === customCat) exists = true;
        }
        if (!exists) {
            const newOption = document.createElement('option');
            newOption.value = customCat;
            newOption.text = customCat;
            catSelect.appendChild(newOption);
        }
        catSelect.value = customCat;
        catSelect.disabled = true; // Lock the category
        
        document.getElementById('menu-form-price').value = '';
        document.getElementById('menu-form-desc').value = '';
        document.getElementById('menu-form-active').checked = true;
        document.getElementById('menu-form-modal').style.display = 'flex';
    },

    editMenu(item) {
        document.getElementById('menu-form-title').innerText = 'Edit Menu';
        document.getElementById('menu-form-id').value = item.id;
        document.getElementById('menu-form-name').value = item.name;
        
        const catSelect = document.getElementById('menu-form-category');
        let exists = false;
        for (let i = 0; i < catSelect.options.length; i++) {
            if (catSelect.options[i].value === item.category) exists = true;
        }
        if (!exists) {
            const newOption = document.createElement('option');
            newOption.value = item.category;
            newOption.text = item.category;
            catSelect.appendChild(newOption);
        }
        catSelect.value = item.category;
        catSelect.disabled = item.category.startsWith('Varian - '); // Lock if it's a sub-menu
        
        document.getElementById('menu-form-price').value = item.price;
        document.getElementById('menu-form-desc').value = item.description || '';
        document.getElementById('menu-form-active').checked = item.is_active;
        document.getElementById('menu-form-modal').style.display = 'flex';
    },

    async saveMenu() {
        const id = document.getElementById('menu-form-id').value;
        const catSelect = document.getElementById('menu-form-category');
        
        const payload = {
            name: document.getElementById('menu-form-name').value,
            category: catSelect.value,
            price: parseFloat(document.getElementById('menu-form-price').value),
            description: document.getElementById('menu-form-desc').value,
            is_active: document.getElementById('menu-form-active').checked
        };

        const url = id ? `/api/admin/menu/${id}` : `/api/admin/menu`;
        const method = id ? 'PUT' : 'POST';

        try {
            const res = await fetch(url, {
                method: method,
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.adminToken}`
                },
                body: JSON.stringify(payload)
            });
            
            if (res.status === 401) {
                this.showToast('Sesi berakhir, silakan login kembali', 'error');
                this.logoutAdmin();
                document.getElementById('menu-form-modal').style.display = 'none';
                return;
            }

            if(res.ok) {
                document.getElementById('menu-form-modal').style.display = 'none';
                this.showToast('Menu berhasil disimpan', 'success');
                this.loadAdminMenu();
                fetchMenu(); // Refresh public menu
            } else {
                alert('Gagal menyimpan menu');
            }
        } catch(e) {
            console.error(e);
            alert('Terjadi kesalahan');
        }
    },

    currentUploadMenuId: null,

    triggerImageUpload(id) {
        this.currentUploadMenuId = id;
        document.getElementById('admin-image-upload').click();
    },

    async uploadMenuImage(event) {
        const file = event.target.files[0];
        if (!file || !this.currentUploadMenuId) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showToast('Mengupload gambar...', 'info');
            const res = await fetch(`/api/admin/menu/${this.currentUploadMenuId}/image`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.adminToken}`
                },
                body: formData
            });

            if (res.ok) {
                this.showToast('Gambar berhasil diupload', 'success');
                this.loadAdminMenu();
                fetchMenu();
            } else {
                const data = await res.json();
                this.showToast(data.detail || 'Gagal mengupload gambar', 'error');
            }
        } catch (e) {
            console.error(e);
            this.showToast('Terjadi kesalahan saat upload', 'error');
        } finally {
            event.target.value = ''; // Reset input
        }
    },

    confirmDeleteMenu(id, name, isSubMenu) {
        let message = `Apakah Anda yakin ingin menghapus "${name}"?`;
        if (!isSubMenu) {
            message += '\n\n⚠️ PERHATIAN: Semua sub-menu/varian dari menu ini juga akan ikut terhapus!';
        }
        message += '\n\nData yang sudah dihapus tidak bisa dikembalikan.';
        
        if (confirm(message)) {
            this.deleteMenu(id);
        }
    },

    async deleteMenu(id) {
        try {
            this.showToast('Menghapus menu...', 'info');
            const res = await fetch(`/api/admin/menu/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.adminToken}`
                }
            });

            if (res.status === 401) {
                this.showToast('Sesi berakhir, silakan login kembali', 'error');
                this.logoutAdmin();
                return;
            }

            if (res.ok) {
                this.showToast('Menu berhasil dihapus', 'success');
                this.loadAdminMenu();
                fetchMenu(); // Refresh public menu
            } else {
                const data = await res.json();
                this.showToast(data.detail || 'Gagal menghapus menu', 'error');
            }
        } catch (e) {
            console.error(e);
            this.showToast('Terjadi kesalahan saat menghapus', 'error');
        }
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
