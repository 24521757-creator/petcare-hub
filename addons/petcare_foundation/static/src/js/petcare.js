/** @odoo-module **/

function initPetcare() {
    document.querySelectorAll('[data-petcare-nav]').forEach((nav) => {
        if (nav.dataset.ready) return;
        nav.dataset.ready = '1';
        const toggle = nav.querySelector('.petcare-menu-toggle');
        const drawer = nav.querySelector('.petcare-drawer');
        const backdrop = nav.querySelector('.petcare-drawer-backdrop');
        const close = nav.querySelector('.petcare-drawer-close');
        const setDrawer = (open) => {
            drawer.classList.toggle('is-open', open);
            drawer.setAttribute('aria-hidden', String(!open));
            drawer.toggleAttribute('inert', !open);
            toggle.setAttribute('aria-expanded', String(open));
            backdrop.hidden = !open;
            document.body.classList.toggle('pc-drawer-open', open);
            if (open) close.focus(); else toggle.focus();
        };
        toggle.addEventListener('click', () => setDrawer(true));
        close.addEventListener('click', () => setDrawer(false));
        backdrop.addEventListener('click', () => setDrawer(false));
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && drawer.classList.contains('is-open')) setDrawer(false);
        });

        // Ẩn huy hiệu số lượng Giỏ hàng & Yêu thích khi bằng 0, chỉ hiện khi >= 1
        const syncCounterBadge = (badge) => {
            const num = parseInt((badge.textContent || '').trim(), 10);
            const isEmpty = Number.isNaN(num) || num <= 0;
            if (badge.classList.contains('is-empty') !== isEmpty) {
                badge.classList.toggle('is-empty', isEmpty);
            }
            if (!isEmpty) {
                if (badge.classList.contains('d-none')) badge.classList.remove('d-none');
                if (badge.style.display === 'none') badge.style.display = '';
            }
        };
        nav.querySelectorAll('.petcare-cart-count').forEach((badge) => {
            syncCounterBadge(badge);
            const observer = new MutationObserver(() => syncCounterBadge(badge));
            observer.observe(badge, {
                childList: true,
                characterData: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['class', 'style'],
            });
        });

        // Đồng bộ lại số Yêu thích nếu người dùng xóa sản phẩm ngay trên trang /shop/wishlist
        const wishTable = document.querySelector('#o_comparelist_table');
        if (wishTable && !wishTable.dataset.pcSyncReady) {
            wishTable.dataset.pcSyncReady = '1';
            const syncFromWishTable = () => {
                const count = wishTable.querySelectorAll('tbody tr').length;
                document.querySelectorAll('.pc_wish_count').forEach((el) => {
                    el.textContent = String(count);
                    syncCounterBadge(el);
                });
            };
            const wishObserver = new MutationObserver(syncFromWishTable);
            wishObserver.observe(wishTable, { childList: true, subtree: true });
        }

        // Đồng bộ tức thì nếu Odoo cập nhật .my_wish_quantity ở header mặc định
        const nativeWishQty = document.querySelector('header#top .my_wish_quantity');
        if (nativeWishQty && !nativeWishQty.dataset.pcMirrorReady) {
            nativeWishQty.dataset.pcMirrorReady = '1';
            const mirrorWish = () => {
                const count = parseInt((nativeWishQty.textContent || '').trim(), 10) || 0;
                document.querySelectorAll('.pc_wish_count').forEach((el) => {
                    el.textContent = String(count);
                    syncCounterBadge(el);
                });
            };
            new MutationObserver(mirrorWish).observe(nativeWishQty, {
                childList: true,
                characterData: true,
                subtree: true,
            });
        }

        // Chewy-style mega-menu hover intent & keyboard/click support
        const menus = [...nav.querySelectorAll('[data-petcare-menu]')];
        const megaBackdrop = nav.querySelector('.petcare-mega-backdrop');
        let closeTimer = null;
        const setOpenMenu = (activeMenu) => {
            menus.forEach((menu) => {
                const open = menu === activeMenu;
                menu.classList.toggle('is-open', open);
                const trigger = menu.querySelector('.petcare-menu-trigger');
                if (trigger) trigger.setAttribute('aria-expanded', String(open));
            });
            if (megaBackdrop) megaBackdrop.hidden = !activeMenu;
        };
        menus.forEach((menu) => {
            menu.addEventListener('mouseenter', () => {
                clearTimeout(closeTimer);
                setOpenMenu(menu);
            });
            menu.addEventListener('mouseleave', () => {
                clearTimeout(closeTimer);
                closeTimer = setTimeout(() => setOpenMenu(null), 160);
            });
            menu.addEventListener('focusin', () => {
                clearTimeout(closeTimer);
                setOpenMenu(menu);
            });
            menu.addEventListener('focusout', (event) => {
                if (!menu.contains(event.relatedTarget)) {
                    clearTimeout(closeTimer);
                    closeTimer = setTimeout(() => setOpenMenu(null), 120);
                }
            });
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') setOpenMenu(null);
        });
        window.addEventListener('scroll', () => {
            if (window.scrollY > 70) setOpenMenu(null);
        }, { passive: true });
    });
    const updateScroll = () => document.body.classList.toggle('pc-scrolled', window.scrollY > 70);
    window.addEventListener('scroll', updateScroll, { passive: true });
    updateScroll();

    document.querySelectorAll('.pc-carousel').forEach((carousel) => {
        if (carousel.dataset.ready) return;
        carousel.dataset.ready = '1';
        const slides = [...carousel.querySelectorAll('.pc-slide')];
        const dots = [...carousel.querySelectorAll('.pc-dot')];
        const pause = carousel.querySelector('.pc-pause');
        let current = 0;
        let stopped = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        let timer;
        function show(index) {
            current = (index + slides.length) % slides.length;
            slides.forEach((slide, i) => {
                slide.classList.toggle('is-active', i === current);
                slide.setAttribute('aria-hidden', String(i !== current));
            });
            dots.forEach((dot, i) => {
                dot.classList.toggle('is-active', i === current);
                if (i === current) dot.setAttribute('aria-current', 'true');
                else dot.removeAttribute('aria-current');
            });
        }
        function schedule() {
            clearInterval(timer);
            if (!stopped) timer = setInterval(() => show(current + 1), 5500);
            pause.textContent = stopped ? '▶' : '❚❚';
            pause.setAttribute('aria-label', stopped ? 'Phát trình chiếu' : 'Tạm dừng trình chiếu');
        }
        carousel.querySelector('.pc-prev').addEventListener('click', () => { show(current - 1); schedule(); });
        carousel.querySelector('.pc-next').addEventListener('click', () => { show(current + 1); schedule(); });
        dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); schedule(); }));
        pause.addEventListener('click', () => { stopped = !stopped; schedule(); });
        carousel.addEventListener('mouseenter', () => clearInterval(timer));
        carousel.addEventListener('mouseleave', schedule);
        carousel.addEventListener('focusin', () => clearInterval(timer));
        carousel.addEventListener('focusout', (event) => { if (!carousel.contains(event.relatedTarget)) schedule(); });
        schedule();
    });
    document.querySelectorAll('input.o_wsale_attribute_search_bar').forEach((input) => {
        if (input.placeholder.startsWith('Search ')) input.placeholder = input.placeholder.replace('Search ', 'Tìm ');
    });

    // Trang chi tiết sản phẩm: phóng to 2.25x & di chuyển ảnh theo chuột kiểu Chewy
    const productGallery = document.querySelector('#product_detail .o_wsale_product_images');
    if (productGallery && !productGallery.dataset.pcZoomReady) {
        productGallery.dataset.pcZoomReady = '1';
        const stages = productGallery.querySelectorAll('.carousel-item');
        const targets = stages.length ? stages : [productGallery];
        targets.forEach((stage) => {
            const img = stage.querySelector('img.product_detail_img, img');
            if (!img) return;
            stage.classList.add('pc-zoom-stage');
            let pausedByClick = false;

            const applyZoom = (event) => {
                const rect = stage.getBoundingClientRect();
                const x = Math.max(0, Math.min(100, ((event.clientX - rect.left) / rect.width) * 100));
                const y = Math.max(0, Math.min(100, ((event.clientY - rect.top) / rect.height) * 100));
                stage.classList.add('is-zooming');
                img.style.setProperty('transform-origin', `${x.toFixed(1)}% ${y.toFixed(1)}%`, 'important');
                img.style.setProperty('transform', 'scale(2.25)', 'important');
            };

            const resetZoom = () => {
                stage.classList.remove('is-zooming');
                img.style.setProperty('transform', 'scale(1)', 'important');
                img.style.setProperty('transform-origin', 'center center', 'important');
            };

            stage.addEventListener('mouseenter', (event) => {
                if (event.target.closest('.pc-wish-fab')) return;
                pausedByClick = false;
                applyZoom(event);
            });
            stage.addEventListener('mousemove', (event) => {
                if (event.target.closest('.pc-wish-fab')) {
                    resetZoom();
                    return;
                }
                if (pausedByClick) return;
                applyZoom(event);
            });
            stage.addEventListener('mouseleave', () => {
                pausedByClick = false;
                resetZoom();
            });
            stage.addEventListener('click', (event) => {
                if (event.target.closest('.pc-wish-fab, .carousel-control-prev, .carousel-control-next, button, a')) return;
                event.preventDefault();
                event.stopPropagation();
                if (stage.classList.contains('is-zooming')) {
                    pausedByClick = true;
                    resetZoom();
                } else {
                    pausedByClick = false;
                    applyZoom(event);
                }
            }, true);
        });
    }

    // Nút tim yêu thích nổi trên ảnh sản phẩm (đồng bộ trực tiếp với Odoo product.wishlist)
    const showToast = (html) => {
        let toast = document.querySelector('.pc-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.className = 'pc-toast';
            toast.setAttribute('role', 'status');
            document.body.appendChild(toast);
        }
        toast.innerHTML = html;
        toast.classList.add('is-visible');
        clearTimeout(toast._timer);
        toast._timer = setTimeout(() => toast.classList.remove('is-visible'), 3200);
    };

    document.querySelectorAll('.pc-wish-fab').forEach((btn) => {
        if (btn.dataset.ready) return;
        btn.dataset.ready = '1';
        btn.addEventListener('click', async (event) => {
            event.preventDefault();
            event.stopPropagation();
            const variantInput = document.querySelector('#product_detail input.product_id');
            const productId = parseInt((variantInput && variantInput.value) || btn.dataset.productId, 10);
            if (!productId || btn.dataset.busy === '1') return;
            btn.dataset.busy = '1';
            try {
                const res = await fetch('/petcare/wishlist/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: { product_id: productId } }),
                });
                const data = await res.json();
                const result = data && data.result;
                if (result && typeof result.in_wish === 'boolean') {
                    btn.classList.toggle('is-wished', result.in_wish);
                    btn.classList.remove('is-popping');
                    void btn.offsetWidth;
                    btn.classList.add('is-popping');
                    btn.setAttribute('aria-pressed', String(result.in_wish));
                    btn.setAttribute('title', result.in_wish ? 'Bỏ khỏi yêu thích' : 'Thêm vào yêu thích');
                    const icon = btn.querySelector('i');
                    if (icon) {
                        icon.classList.toggle('fa-heart', result.in_wish);
                        icon.classList.toggle('fa-heart-o', !result.in_wish);
                    }
                    document.querySelectorAll('.pc_wish_count').forEach((el) => {
                        el.textContent = String(result.count);
                        const isEmpty = !result.count || result.count <= 0;
                        el.classList.toggle('is-empty', isEmpty);
                        if (!isEmpty) {
                            el.classList.remove('d-none');
                            if (el.style.display === 'none') el.style.display = '';
                        }
                    });
                    showToast(
                        result.in_wish
                            ? '<span>♥ Đã thêm vào danh sách yêu thích</span><a href="/shop/wishlist">Xem danh sách →</a>'
                            : '<span>Đã bỏ khỏi danh sách yêu thích</span>'
                    );
                }
            } finally {
                btn.dataset.busy = '0';
            }
        });
    });

    // Nút tim yêu thích (.o_add_wishlist) trên các thẻ sản phẩm trang /shop:
    // Bắt sự kiện ở capture phase trên document để gọi trực tiếp /petcare/wishlist/toggle & nhảy số header ngay lập tức
    document.querySelectorAll('.oe_product_cart .o_add_wishlist').forEach((btn) => {
        btn.removeAttribute('disabled');
        btn.disabled = false;
    });
    if (!document.body.dataset.pcShopWishReady) {
        document.body.dataset.pcShopWishReady = '1';
        document.addEventListener('click', async (event) => {
            const btn = event.target.closest('.oe_product_cart .o_add_wishlist');
            if (!btn) return;
            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();
            if (btn.dataset.busy === '1') return;
            const card = btn.closest('.oe_product_cart');
            const quickAdd = card && card.querySelector('.pc-quick-add-btn');
            const productId = parseInt(
                btn.dataset.productProductId
                || (quickAdd && quickAdd.dataset.productId)
                || '0',
                10
            );
            if (!productId) return;
            btn.dataset.busy = '1';
            try {
                const res = await fetch('/petcare/wishlist/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: { product_id: productId },
                    }),
                });
                const data = await res.json();
                const result = data && data.result;
                if (result && typeof result.in_wish === 'boolean') {
                    btn.classList.toggle('o_in_wishlist', result.in_wish);
                    btn.removeAttribute('disabled');
                    btn.disabled = false;
                    btn.setAttribute('aria-pressed', String(result.in_wish));
                    btn.setAttribute('title', result.in_wish ? 'Bỏ khỏi danh sách yêu thích' : 'Thêm vào danh sách yêu thích');
                    const icon = btn.querySelector('.fa');
                    if (icon) {
                        icon.classList.toggle('fa-heart', result.in_wish);
                        icon.classList.toggle('fa-heart-o', !result.in_wish);
                    }
                    const count = parseInt(result.count || 0, 10);
                    document.querySelectorAll('.pc_wish_count').forEach((el) => {
                        el.textContent = String(count);
                        const isEmpty = !count || count <= 0;
                        el.classList.toggle('is-empty', isEmpty);
                        if (!isEmpty) {
                            el.classList.remove('d-none');
                            if (el.style.display === 'none') el.style.display = '';
                        }
                    });
                    showToast(
                        result.in_wish
                            ? '<span>♥ Đã thêm vào danh sách yêu thích</span><a href="/shop/wishlist">Xem danh sách →</a>'
                            : '<span>Đã bỏ khỏi danh sách yêu thích</span>'
                    );
                }
            } finally {
                btn.dataset.busy = '0';
            }
        }, true);
    }

    // Nút "Thêm vào giỏ hàng" trực tiếp 1-click trên từng thẻ sản phẩm /shop (không mở popup Cấu hình)
    document.querySelectorAll('.pc-quick-add-btn').forEach((btn) => {
        if (btn.dataset.ready) return;
        btn.dataset.ready = '1';
        btn.addEventListener('click', async (event) => {
            event.preventDefault();
            event.stopPropagation();
            if (btn.dataset.busy === '1') return;
            const productId = parseInt(btn.dataset.productId || '0', 10);
            const templateId = parseInt(btn.dataset.productTemplateId || '0', 10);
            if (!productId && !templateId) return;

            btn.dataset.busy = '1';
            btn.classList.add('is-loading');
            const label = btn.querySelector('span');
            const icon = btn.querySelector('i');
            try {
                const res = await fetch('/petcare/cart/quick_add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            product_id: productId,
                            product_template_id: templateId,
                            quantity: 1,
                        },
                    }),
                });
                const data = await res.json();
                const result = data && data.result;
                if (result && result.ok) {
                    const qty = parseInt(result.cart_quantity || 0, 10);
                    document.querySelectorAll('.my_cart_quantity').forEach((el) => {
                        el.textContent = String(qty);
                        const isEmpty = !qty || qty <= 0;
                        el.classList.toggle('is-empty', isEmpty);
                        if (!isEmpty) {
                            el.classList.remove('d-none');
                            if (el.style.display === 'none') el.style.display = '';
                        }
                    });
                    btn.classList.add('is-added');
                    if (icon) {
                        icon.classList.remove('fa-shopping-cart');
                        icon.classList.add('fa-check');
                    }
                    if (label) label.textContent = 'Đã thêm vào giỏ';
                    showToast('<span>✓ Đã thêm vào giỏ hàng</span><a href="/shop/cart">Xem giỏ hàng →</a>');
                    clearTimeout(btn._resetTimer);
                    btn._resetTimer = setTimeout(() => {
                        btn.classList.remove('is-added');
                        if (icon) {
                            icon.classList.remove('fa-check');
                            icon.classList.add('fa-shopping-cart');
                        }
                        if (label) label.textContent = 'Thêm vào giỏ hàng';
                    }, 900);
                }
            } finally {
                btn.classList.remove('is-loading');
                btn.dataset.busy = '0';
            }
        });
    });

    // Tab lọc dịch vụ trên trang /petcare/services
    document.querySelectorAll('.pc-svc-tabs').forEach((tabBar) => {
        if (tabBar.dataset.ready) return;
        tabBar.dataset.ready = '1';
        const tabs = [...tabBar.querySelectorAll('.pc-svc-tab')];
        const cards = [...document.querySelectorAll('.pc-salon-card')];
        tabs.forEach((tab) => {
            tab.addEventListener('click', () => {
                const filter = tab.dataset.svcFilter;
                tabs.forEach((t) => {
                    const active = t === tab;
                    t.classList.toggle('is-active', active);
                    t.setAttribute('aria-selected', String(active));
                });
                cards.forEach((card) => {
                    card.hidden = filter !== 'all' && card.dataset.svcType !== filter;
                });
            });
        });
    });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initPetcare);
else initPetcare();
