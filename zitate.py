from flask import Flask, render_template_string, request, jsonify, session
from datetime import datetime, date
import random
import secrets
import os
from supabase import create_client, Client

# ============= KONFIGURATION =============
ADMIN_PASSWORD = "mbg"  # HIER PASSWORT ÄNDERN
SUPABASE_URL = os.environ.get("https://znrkghgtfpygiawzivpt.supabase.co", "")
SUPABASE_KEY = os.environ.get("sb_publishable_-R_iKeuuppOByIUu2y9U-g_yPlQFyOj", "")
# =========================================

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Supabase Client initialisieren
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Fehler beim Verbinden mit Supabase: {e}")
    supabase = None

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Klassenzitate</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><defs><linearGradient id='grad' x1='0%' y1='0%' x2='100%' y2='100%'><stop offset='0%' style='stop-color:%237c3aed;stop-opacity:1' /><stop offset='100%' style='stop-color:%23a78bfa;stop-opacity:1' /></linearGradient></defs><rect width='100' height='100' rx='20' fill='url(%23grad)'/><text x='50' y='68' font-size='50' font-weight='bold' text-anchor='middle' fill='white' font-family='Arial'>K</text></svg>">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            color: #e2e8f0;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 50%, rgba(124, 58, 237, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        .container {
            position: relative;
            z-index: 1;
        }

        /* Header */
        .header {
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
            background: rgba(15, 23, 42, 0.8);
            border-bottom: 1px solid rgba(124, 58, 237, 0.2);
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #7c3aed, #a78bfa);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            font-weight: bold;
            color: white;
        }

        .logo-text {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #a78bfa, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .theme-toggle {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(124, 58, 237, 0.3);
            width: 40px;
            height: 40px;
            border-radius: 10px;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #a78bfa;
        }

        .theme-toggle:hover {
            background: rgba(124, 58, 237, 0.3);
            transform: scale(1.05);
        }

        .btn {
            padding: 0.65rem 1.25rem;
            border: none;
            border-radius: 10px;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: linear-gradient(135deg, #7c3aed, #a78bfa);
            color: white;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6);
        }

        .btn-secondary {
            background: rgba(30, 41, 59, 0.5);
            color: #e2e8f0;
            border: 1px solid rgba(124, 58, 237, 0.3);
        }

        .btn-secondary:hover {
            background: rgba(124, 58, 237, 0.3);
        }

        /* Main Content */
        .main-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .controls {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid rgba(124, 58, 237, 0.2);
        }

        .filter-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .input-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #94a3b8;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .input-group input,
        .input-group select {
            width: 100%;
            padding: 0.65rem;
            border: 1px solid rgba(124, 58, 237, 0.3);
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.6);
            color: #e2e8f0;
            font-size: 0.95rem;
            transition: all 0.3s;
        }

        .input-group input:focus,
        .input-group select:focus {
            outline: none;
            border-color: #7c3aed;
            box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
        }

        .button-group {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }

        /* Quote Cards Grid */
        .quotes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
        }

        .quote-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
            backdrop-filter: blur(10px);
            padding: 1.75rem;
            border-radius: 20px;
            border: 2px solid transparent;
            position: relative;
            transition: all 0.3s;
            overflow: hidden;
        }

        .quote-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 20px;
            padding: 2px;
            background: linear-gradient(135deg, #7c3aed, #3b82f6, #06b6d4);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .quote-card:hover::before {
            opacity: 1;
        }

        .quote-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(124, 58, 237, 0.3);
        }

        .quote-marks {
            position: absolute;
            right: 1.5rem;
            top: 1.5rem;
            font-size: 4rem;
            color: rgba(124, 58, 237, 0.15);
            font-family: Georgia, serif;
            line-height: 1;
        }

        .quote-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.9rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .badge-lehrer {
            background: rgba(124, 58, 237, 0.3);
            color: #c4b5fd;
            border: 1px solid rgba(124, 58, 237, 0.5);
        }

        .badge-lehrer::before {
            content: '▶';
            margin-right: 0.2rem;
        }

        .badge-schüler {
            background: rgba(6, 182, 212, 0.3);
            color: #67e8f9;
            border: 1px solid rgba(6, 182, 212, 0.5);
        }

        .badge-schüler::before {
            content: '▶';
            margin-right: 0.2rem;
        }

        .badge-andere {
            background: rgba(59, 130, 246, 0.3);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.5);
        }

        .badge-andere::before {
            content: '▶';
            margin-right: 0.2rem;
        }

        .quote-text {
            font-size: 1.1rem;
            line-height: 1.7;
            margin-bottom: 1.25rem;
            font-style: italic;
            color: #f1f5f9;
            position: relative;
            z-index: 1;
        }

        .quote-author {
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        }

        .quote-date {
            color: #64748b;
            font-size: 0.85rem;
        }

        .admin-controls {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(124, 58, 237, 0.2);
        }

        .btn-small {
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
        }

        .btn-edit {
            background: rgba(59, 130, 246, 0.3);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.5);
        }

        .btn-delete {
            background: rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.5);
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            backdrop-filter: blur(5px);
        }

        .modal.active {
            display: flex;
            justify-content: center;
            align-items: center;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal-content {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
            backdrop-filter: blur(20px);
            padding: 2rem;
            border-radius: 20px;
            max-width: 500px;
            width: 90%;
            border: 2px solid rgba(124, 58, 237, 0.3);
            animation: slideUp 0.3s ease;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        }

        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .modal h2 {
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #a78bfa, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.5rem;
        }

        .form-group {
            margin-bottom: 1.25rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #94a3b8;
            font-weight: 500;
            font-size: 0.9rem;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid rgba(124, 58, 237, 0.3);
            border-radius: 10px;
            background: rgba(15, 23, 42, 0.6);
            color: #e2e8f0;
            font-size: 1rem;
            transition: all 0.3s;
        }

        .form-group textarea {
            resize: vertical;
            min-height: 100px;
            font-family: inherit;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #7c3aed;
            box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
        }

        .modal-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .modal-buttons .btn {
            flex: 1;
        }

        /* Alerts */
        .alert {
            padding: 1rem 1.25rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            animation: slideIn 0.3s ease;
            border-left: 4px solid;
        }

        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        .alert-success {
            background: rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
            border-color: #10b981;
        }

        .alert-error {
            background: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
            border-color: #ef4444;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 1rem;
            }

            .filter-group {
                grid-template-columns: 1fr;
            }

            .quotes-grid {
                grid-template-columns: 1fr;
            }

            .button-group {
                flex-direction: column;
            }

            .button-group .btn {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">K</div>
                <div class="logo-text">Klassenzitate</div>
            </div>
            <div class="header-controls">
                <button class="theme-toggle" onclick="toggleTheme()" title="Theme wechseln">◐</button>
                {% if session.get('admin') %}
                    <button class="btn btn-primary" onclick="showAddModal()">+ Neues Zitat</button>
                    <button class="btn btn-secondary" onclick="logout()">Logout</button>
                {% else %}
                    <button class="btn btn-primary" onclick="showLoginModal()">Admin-Login</button>
                {% endif %}
            </div>
        </div>

        <div class="main-content">
            <div id="alert-container"></div>

            <div class="controls">
                <div class="filter-group">
                    <div class="input-group">
                        <label>Von Datum</label>
                        <input type="date" id="filterDateFrom">
                    </div>
                    <div class="input-group">
                        <label>Bis Datum</label>
                        <input type="date" id="filterDateTo">
                    </div>
                    <div class="input-group">
                        <label>Gruppe</label>
                        <select id="filterGroup">
                            <option value="">Alle</option>
                            <option value="Schüler">Schüler</option>
                            <option value="Lehrer">Lehrer</option>
                            <option value="Andere">Andere</option>
                        </select>
                    </div>
                </div>
                <div class="button-group">
                    <button class="btn btn-primary" onclick="applyFilters()">Filter anwenden</button>
                    <button class="btn btn-secondary" onclick="resetFilters()">Filter zurücksetzen</button>
                    <button class="btn btn-primary" onclick="showRandomQuote()">Zufälliges Zitat</button>
                </div>
            </div>

            <div class="quotes-grid" id="quotesGrid"></div>
        </div>
    </div>

    <!-- Login Modal -->
    <div class="modal" id="loginModal">
        <div class="modal-content">
            <h2>Admin Login</h2>
            <div class="form-group">
                <label>Passwort</label>
                <input type="password" id="loginPassword" onkeypress="if(event.key==='Enter') login()" placeholder="Passwort eingeben...">
            </div>
            <div class="modal-buttons">
                <button class="btn btn-primary" onclick="login()">Login</button>
                <button class="btn btn-secondary" onclick="closeModal('loginModal')">Abbrechen</button>
            </div>
        </div>
    </div>

    <!-- Add/Edit Quote Modal -->
    <div class="modal" id="quoteModal">
        <div class="modal-content">
            <h2 id="quoteModalTitle">Neues Zitat</h2>
            <form id="quoteForm">
                <input type="hidden" id="quoteId">
                <div class="form-group">
                    <label>Zitat</label>
                    <textarea id="quoteText" required placeholder="Zitat eingeben..."></textarea>
                </div>
                <div class="form-group">
                    <label>Autor</label>
                    <input type="text" id="quoteAuthor" required placeholder="Name des Autors...">
                </div>
                <div class="form-group">
                    <label>Gruppe</label>
                    <select id="quoteGroup" required>
                        <option value="Schüler">Schüler</option>
                        <option value="Lehrer">Lehrer</option>
                        <option value="Andere">Andere</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Datum</label>
                    <input type="date" id="quoteDate">
                </div>
                <div class="modal-buttons">
                    <button type="submit" class="btn btn-primary">Speichern</button>
                    <button type="button" class="btn btn-secondary" onclick="closeModal('quoteModal')">Abbrechen</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Random Quote Modal -->
    <div class="modal" id="randomModal">
        <div class="modal-content">
            <h2>Zufälliges Zitat</h2>
            <div id="randomQuoteContent"></div>
            <div class="modal-buttons">
                <button class="btn btn-primary" onclick="showRandomQuote()">Neues Zitat</button>
                <button class="btn btn-secondary" onclick="closeModal('randomModal')">Schließen</button>
            </div>
        </div>
    </div>

    <script>
        let quotes = [];
        const isAdmin = {{ 'true' if session.get('admin') else 'false' }};

        // Theme Toggle
        function toggleTheme() {
            showAlert('Theme-Wechsel aktuell nicht verfügbar', 'error');
        }

        // Show Alert
        function showAlert(message, type) {
            const container = document.getElementById('alert-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            container.appendChild(alert);
            setTimeout(() => alert.remove(), 4000);
        }

        // Modal Functions
        function showModal(modalId) {
            document.getElementById(modalId).classList.add('active');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }

        function showLoginModal() {
            document.getElementById('loginPassword').value = '';
            showModal('loginModal');
        }

        function showAddModal() {
            document.getElementById('quoteModalTitle').textContent = 'Neues Zitat';
            document.getElementById('quoteId').value = '';
            document.getElementById('quoteForm').reset();
            document.getElementById('quoteDate').value = new Date().toISOString().split('T')[0];
            showModal('quoteModal');
        }

        function showEditModal(quote) {
            document.getElementById('quoteModalTitle').textContent = 'Zitat bearbeiten';
            document.getElementById('quoteId').value = quote.id;
            document.getElementById('quoteText').value = quote.text;
            document.getElementById('quoteAuthor').value = quote.author;
            document.getElementById('quoteGroup').value = quote.group_name;
            document.getElementById('quoteDate').value = quote.date;
            showModal('quoteModal');
        }

        // Login
        async function login() {
            const password = document.getElementById('loginPassword').value;
            const response = await fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password})
            });
            const data = await response.json();
            if (data.success) {
                location.reload();
            } else {
                showAlert('Falsches Passwort', 'error');
            }
        }

        // Logout
        async function logout() {
            await fetch('/logout');
            location.reload();
        }

        // Load Quotes
        async function loadQuotes() {
            try {
                const response = await fetch('/api/quotes');
                quotes = await response.json();
                renderQuotes(quotes);
            } catch (error) {
                showAlert('Fehler beim Laden der Zitate', 'error');
            }
        }

        // Render Quotes
        function renderQuotes(quotesToRender) {
            const grid = document.getElementById('quotesGrid');
            grid.innerHTML = '';
            
            if (quotesToRender.length === 0) {
                grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #64748b;">Keine Zitate gefunden.</p>';
                return;
            }
            
            quotesToRender.forEach(quote => {
                const card = document.createElement('div');
                card.className = 'quote-card';
                
                const badgeClass = `badge-${quote.group_name.toLowerCase()}`;
                
                card.innerHTML = `
                    <div class="quote-marks">"</div>
                    <span class="quote-badge ${badgeClass}">${quote.group_name}</span>
                    <div class="quote-text">"${quote.text}"</div>
                    <div class="quote-author">— ${quote.author}</div>
                    <div class="quote-date">${formatDate(quote.date)}</div>
                    ${isAdmin ? `
                        <div class="admin-controls">
                            <button class="btn btn-small btn-edit" onclick='editQuote(${JSON.stringify(quote).replace(/'/g, "&#39;")})'>Bearbeiten</button>
                            <button class="btn btn-small btn-delete" onclick="deleteQuote(${quote.id})">Löschen</button>
                        </div>
                    ` : ''}
                `;
                grid.appendChild(card);
            });
        }

        // Format Date
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            const months = ['Jan.', 'Feb.', 'Mär.', 'Apr.', 'Mai', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Okt.', 'Nov.', 'Dez.'];
            return `${date.getDate()}. ${months[date.getMonth()]} ${date.getFullYear()}`;
        }

        // Random Quote
        function showRandomQuote() {
            if (quotes.length === 0) {
                showAlert('Keine Zitate verfügbar', 'error');
                return;
            }
            const quote = quotes[Math.floor(Math.random() * quotes.length)];
            const badgeClass = `badge-${quote.group_name.toLowerCase()}`;
            
            document.getElementById('randomQuoteContent').innerHTML = `
                <span class="quote-badge ${badgeClass}">${quote.group_name}</span>
                <div class="quote-text">"${quote.text}"</div>
                <div class="quote-author">— ${quote.author}</div>
                <div class="quote-date">${formatDate(quote.date)}</div>
            `;
            showModal('randomModal');
        }

        // Filters
        function applyFilters() {
            const dateFrom = document.getElementById('filterDateFrom').value;
            const dateTo = document.getElementById('filterDateTo').value;
            const group = document.getElementById('filterGroup').value;
            
            let filtered = quotes;
            
            if (dateFrom) {
                filtered = filtered.filter(q => q.date >= dateFrom);
            }
            if (dateTo) {
                filtered = filtered.filter(q => q.date <= dateTo);
            }
            if (group) {
                filtered = filtered.filter(q => q.group_name === group);
            }
            
            renderQuotes(filtered);
        }

        function resetFilters() {
            document.getElementById('filterDateFrom').value = '';
            document.getElementById('filterDateTo').value = '';
            document.getElementById('filterGroup').value = '';
            renderQuotes(quotes);
        }

        // CRUD Operations
        document.getElementById('quoteForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('quoteId').value;
            const quote = {
                text: document.getElementById('quoteText').value,
                author: document.getElementById('quoteAuthor').value,
                group_name: document.getElementById('quoteGroup').value,
                date: document.getElementById('quoteDate').value || new Date().toISOString().split('T')[0]
            };
            
            try {
                const url = id ? `/api/quotes/${id}` : '/api/quotes';
                const method = id ? 'PUT' : 'POST';
                
                const response = await fetch(url, {
                    method,
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(quote)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showAlert(id ? 'Zitat aktualisiert' : 'Zitat hinzugefügt', 'success');
                    closeModal('quoteModal');
                    loadQuotes();
                } else {
                    showAlert(`Fehler: ${JSON.stringify(data)}`, 'error');
                }
            } catch (error) {
                showAlert('Fehler beim Speichern', 'error');
                console.error(error);
            }
        });

        function editQuote(quote) {
            showEditModal(quote);
        }

        async function deleteQuote(id) {
            if (!confirm('Zitat wirklich löschen?')) return;
            
            try {
                const response = await fetch(`/api/quotes/${id}`, {method: 'DELETE'});
                if (response.ok) {
                    showAlert('Zitat gelöscht', 'success');
                    loadQuotes();
                } else {
                    showAlert('Fehler beim Löschen', 'error');
                }
            } catch (error) {
                showAlert('Fehler beim Löschen', 'error');
            }
        }

        // Close modal on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            });
        });

        // Initial load
        loadQuotes();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('password') == ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return jsonify({'success': True})

@app.route('/api/quotes', methods=['GET'])
def get_quotes():
    try:
        response = supabase.table('quotes').select('*').order('date', desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quotes', methods=['POST'])
def add_quote():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        quote = {
            'text': data['text'],
            'author': data['author'],
            'group_name': data['group_name'],
            'date': data.get('date', date.today().isoformat())
        }
        response = supabase.table('quotes').insert(quote).execute()
        return jsonify(response.data[0]), 201
    except Exception as e:
        return jsonify({'error': str(e), 'message': str(e)}), 500

@app.route('/api/quotes/<int:quote_id>', methods=['PUT'])
def update_quote(quote_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        quote = {
            'text': data['text'],
            'author': data['author'],
            'group_name': data['group_name'],
            'date': data.get('date')
        }
        response = supabase.table('quotes').update(quote).eq('id', quote_id).execute()
        return jsonify(response.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quotes/<int:quote_id>', methods=['DELETE'])
def delete_quote(quote_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        supabase.table('quotes').delete().eq('id', quote_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
