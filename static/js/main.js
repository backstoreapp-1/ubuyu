/* Ubuyu Marketplace - JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    updateCartBadge();
    loadNotifications();
});

// Cart Management
function updateCartBadge() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const badge = document.getElementById('cart-badge');
    if (cart.length > 0) {
        badge.textContent = cart.length;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

function addToCart(productId) {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const existing = cart.find(item => item.id === productId);
    if (existing) {
        existing.qty++;
    } else {
        cart.push({ id: productId, qty: 1 });
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge();
}

function removeFromCart(productId) {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    cart = cart.filter(item => item.id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge();
}

// Notifications
function loadNotifications() {
    if (!document.querySelector('.navbar')) return;
    
    fetch('/api/notifications/unread')
        .then(r => r.json())
        .then(data => {
            if (data.unread > 0) {
                const badge = document.getElementById('notif-badge');
                badge.textContent = data.unread;
                badge.style.display = 'flex';
            }
        });
}

function toggleNotifications() {
    // display notification overlay
    let panel = document.getElementById('notif-panel');
    if (!panel) return;
    if (panel.style.display === 'block') {
        panel.style.display = 'none';
        return;
    }
    fetch('/api/notifications')
        .then(r => r.json())
        .then(data => {
            const list = panel.querySelector('.notif-list');
            list.innerHTML = '';
            data.forEach(n => {
                const item = document.createElement('div');
                item.className = 'notif-item' + (n.is_read ? '' : ' unread');
                item.innerHTML = `<strong>${n.title}</strong><p>${n.content}</p><small>${n.created_at}</small>`;
                list.appendChild(item);
            });
            panel.style.display = 'block';
            // clear badge
            const badge = document.getElementById('notif-badge');
            if (badge) badge.style.display = 'none';
        });
}

function toggleCart() {
    let panel = document.getElementById('cart-panel');
    if (!panel) return;
    if (panel.style.display === 'block') {
        panel.style.display = 'none';
        return;
    }
    // build cart content
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const list = panel.querySelector('.cart-list');
    list.innerHTML = '';
    if (cart.length === 0) {
        list.innerHTML = '<p>Your cart is empty.</p>';
    } else {
        // clear old checkout button if present
        const old = panel.querySelector('.checkout-btn');
        if (old) old.remove();

        Promise.all(cart.map(item => fetch(`/products/api/${item.id}`).then(r=>r.json())))
            .then(products => {
                products.forEach((p, idx) => {
                    const qty = cart[idx].qty || 1;
                    const div = document.createElement('div');
                    div.className = 'cart-item';
                    div.innerHTML = `
                        <span>${p.name} x${qty}</span> - KES ${(p.price*qty).toFixed(2)}
                        <button onclick="removeFromCart(${p.id});toggleCart();toggleCart();">✕</button>
                    `;
                    list.appendChild(div);
                });
                const checkout = document.createElement('button');
                checkout.className = 'btn btn-primary checkout-btn';
                checkout.textContent = 'Checkout';
                checkout.onclick = () => {
                    // redirect with cart in localStorage or later
                    window.location.href = '/orders/checkout';
                };
                panel.appendChild(checkout);
            });
    }
    panel.style.display = 'block';
}

// Chat
function openChat() {
    const widget = document.getElementById('chat-widget');
    if (widget) {
        widget.style.display = 'flex';
    }
}

function closeChat() {
    const widget = document.getElementById('chat-widget');
    if (widget) {
        widget.style.display = 'none';
    }
}

function sendChat() {
    const input = document.getElementById('chat-input');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    const messagesDiv = document.getElementById('chat-messages');
    const msg = document.createElement('div');
    msg.className = 'message own';
    msg.innerHTML = '<div class="message-bubble">' + escapeHtml(message) + '</div>';
    messagesDiv.appendChild(msg);
    
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Send to server if user is authenticated
    if (document.querySelector('.navbar a[href*="logout"]')) {
        // User is logged in, send message
        fetch('/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                receiver_id: 1,  // Support team ID
                content: message
            })
        });
    }
}

// Search
function search() {
    const input = document.getElementById('search-input');
    if (!input) return;
    
    const query = input.value.trim();
    if (query) {
        window.location.href = '/products/catalog?search=' + encodeURIComponent(query);
    }
}

// Utility
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Enter key for search and chat
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') search();
        });
    }
    
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChat();
        });
    }
});
