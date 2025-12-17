from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from datetime import datetime, date
import random
import secrets
import os

# ============= KONFIGURATION =============
ADMIN_PASSWORD = "admin123"  # HIER PASSWORT ÄNDERN
# =========================================

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-Memory Speicher für Zitate
quotes_db = [
    {
        "id": 1,
        "text": "Das Leben ist wie ein Fahrrad. Man muss sich vorwärts bewegen, um das Gleichgewicht zu halten.",
        "author": "Albert Einstein",
        "group": "Andere",
        "date": "2024-01-15"
    },
    {
        "id": 2,
        "text": "Die Mathematik ist das Alphabet, mit dem Gott die Welt geschrieben hat.",
        "author": "Galileo Galilei",
        "group": "Lehrer",
        "date": "2024-02-20"
    },
    {
        "id": 3,
        "text": "Hausaufgaben sind der Beweis dafür, dass auch zu Hause gelitten werden kann.",
        "author": "Max Musterschüler",
        "group": "Schüler",
        "date": "2024-03-10"
    }
]
next_id = 4

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zitate Sammlung</title>
    <style>
        :root {
            --bg-primary: #f5f7fa;
            --bg-secondary: #ffffff;
            --text-primary: #2c3e50;
            --text-secondary: #7f8c8d;
            --accent: #3498db;
            --accent-hover: #2980b9;
            --border: #e1e8ed;
            --shadow: rgba(0, 0, 0, 0.1);
            --glow: rgba(52, 152, 219, 0.5);
        }

        [data-theme="dark"] {
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --text-primary: #eee;
            --text-secondary: #aaa;
            --accent: #0f3460;
            --accent-hover: #533483;
            --border: #2a2a3e;
            --shadow: rgba(0, 0, 0, 0.5);
            --glow: rgba(83, 52, 131, 0.8);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: background 0.3s, color 0.3s;
            min-height: 100vh;
        }

        .header {
            background: var(--bg-secondary);
            padding: 1.5rem 2rem;
            box-shadow: 0 2px 10px var(--shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            animation: slideDown 0.5s ease;
        }

        @keyframes slideDown {
            from { transform: translateY(-100%); }
            to { transform: translateY(0); }
        }

        .header h1 {
            font-size: 2rem;
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 2s ease-in-out infinite;
        }

        @keyframes glow {
            0%, 100% { filter: drop-shadow(0 0 10px var(--glow)); }
            50% { filter: drop-shadow(0 0 20px var(--glow)); }
        }

        .header-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            color: white;
            box-shadow: 0 4px 15px var(--glow);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--glow);
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 2px solid var(--border);
        }

        .btn-secondary:hover {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        .theme-toggle {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            transition: transform 0.3s;
        }

        .theme-toggle:hover {
            transform: rotate(180deg);
        }

        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        .controls {
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px var(--shadow);
            animation: fadeIn 0.5s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .filter-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .input-group {
            display: flex;
            flex-direction: column;
        }

        .input-group label {
            margin-bottom: 0.5rem;
            color: var(--text-secondary);
            font-weight: 600;
        }

        .input-group input,
        .input-group select {
            padding: 0.75rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            background: var(--bg-primary);
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s;
        }

        .input-group input:focus,
        .input-group select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--glow);
        }

        .button-group {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }

        .quote-of-day {
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 8px 25px var(--glow);
            animation: fadeIn 0.8s ease;
        }

        .quote-of-day h2 {
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }

        .quote-of-day .quote-text {
            font-size: 1.2rem;
            font-style: italic;
            margin-bottom: 0.5rem;
        }

        .quotes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .quote-card {
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px var(--shadow);
            transition: all 0.3s;
            animation: fadeIn 0.5s ease;
            border: 2px solid transparent;
        }

        .quote-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px var(--glow);
            border-color: var(--accent);
        }

        .quote-text {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            line-height: 1.6;
        }

        .quote-author {
            color: var(--text-secondary);
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .quote-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }

        .quote-group {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .group-schueler { background: #e74c3c; color: white; }
        .group-lehrer { background: #2ecc71; color: white; }
        .group-andere { background: #f39c12; color: white; }

        .quote-date {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .admin-controls {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .btn-small {
            padding: 0.4rem 0.8rem;
            font-size: 0.85rem;
        }

        .btn-edit {
            background: #3498db;
            color: white;
        }

        .btn-delete {
            background: #e74c3c;
            color: white;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        }

        .modal.active {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px var(--shadow);
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .modal h2 {
            margin-bottom: 1.5rem;
            color: var(--accent);
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-secondary);
            font-weight: 600;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            background: var(--bg-primary);
            color: var(--text-primary);
            font-size: 1rem;
        }

        .form-group textarea {
            resize: vertical;
            min-height: 100px;
        }

        .modal-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            animation: fadeIn 0.3s ease;
        }

        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

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
        }
    </style>
</head>
<body data-theme="light">
    <div class="header">
        <h1>✨ Zitate Sammlung</h1>
        <div class="header-controls">
            <button class="theme-toggle" onclick="toggleTheme()">🌙</button>
            {% if session.get('admin') %}
                <button class="btn btn-primary" onclick="showAddModal()">+ Neues Zitat</button>
                <button class="btn btn-secondary" onclick="logout()">Logout</button>
            {% else %}
                <button class="btn btn-primary" onclick="showLoginModal()">Login</button>
            {% endif %}
        </div>
    </div>

    <div class="container">
        <div id="alert-container"></div>

        <div class="quote-of-day" id="quoteOfDay"></div>

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
                <button class="btn btn-primary" onclick="showRandomQuote()">🎲 Zufälliges Zitat</button>
            </div>
        </div>

        <div class="quotes-grid" id="quotesGrid"></div>
    </div>

    <!-- Login Modal -->
    <div class="modal" id="loginModal">
        <div class="modal-content">
            <h2>Admin Login</h2>
            <div class="form-group">
                <label>Passwort</label>
                <input type="password" id="loginPassword" onkeypress="if(event.key==='Enter') login()">
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
                    <label>Zitat *</label>
                    <textarea id="quoteText" required></textarea>
                </div>
                <div class="form-group">
                    <label>Autor *</label>
                    <input type="text" id="quoteAuthor" required>
                </div>
                <div class="form-group">
                    <label>Gruppe *</label>
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
            <h2>🎲 Zufälliges Zitat</h2>
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
            const body = document.body;
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            body.setAttribute('data-theme', newTheme);
            document.querySelector('.theme-toggle').textContent = newTheme === 'light' ? '🌙' : '☀️';
            localStorage.setItem('theme', newTheme);
        }

        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
        document.querySelector('.theme-toggle').textContent = savedTheme === 'light' ? '🌙' : '☀️';

        // Show Alert
        function showAlert(message, type) {
            const container = document.getElementById('alert-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            container.appendChild(alert);
            setTimeout(() => alert.remove(), 3000);
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
            document.getElementById('quoteGroup').value = quote.group;
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
            const response = await fetch('/api/quotes');
            quotes = await response.json();
            renderQuotes(quotes);
            showQuoteOfDay();
        }

        // Render Quotes
        function renderQuotes(quotesToRender) {
            const grid = document.getElementById('quotesGrid');
            grid.innerHTML = '';
            
            quotesToRender.forEach(quote => {
                const card = document.createElement('div');
                card.className = 'quote-card';
                card.innerHTML = `
                    <div class="quote-text">"${quote.text}"</div>
                    <div class="quote-author">— ${quote.author}</div>
                    <div class="quote-meta">
                        <span class="quote-group group-${quote.group.toLowerCase()}">${quote.group}</span>
                        <span class="quote-date">${formatDate(quote.date)}</span>
                    </div>
                    ${isAdmin ? `
                        <div class="admin-controls">
                            <button class="btn btn-small btn-edit" onclick='editQuote(${JSON.stringify(quote)})'>Bearbeiten</button>
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
            return date.toLocaleDateString('de-DE', {day: '2-digit', month: '2-digit', year: 'numeric'});
        }

        // Quote of the Day
        function showQuoteOfDay() {
            if (quotes.length === 0) return;
            const today = new Date().toDateString();
            let seed = 0;
            for (let i = 0; i < today.length; i++) {
                seed += today.charCodeAt(i);
            }
            const index = seed % quotes.length;
            const quote = quotes[index];
            
            document.getElementById('quoteOfDay').innerHTML = `
                <h2>🌟 Zitat des Tages</h2>
                <div class="quote-text">"${quote.text}"</div>
                <div class="quote-author">— ${quote.author}</div>
            `;
        }

        // Random Quote
        function showRandomQuote() {
            if (quotes.length === 0) {
                showAlert('Keine Zitate verfügbar', 'error');
                return;
            }
            const quote = quotes[Math.floor(Math.random() * quotes.length)];
            document.getElementById('randomQuoteContent').innerHTML = `
                <div class="quote-text">"${quote.text}"</div>
                <div class="quote-author">— ${quote.author}</div>
                <div class="quote-meta" style="margin-top: 1rem;">
                    <span class="quote-group group-${quote.group.toLowerCase()}">${quote.group}</span>
                    <span class="quote-date">${formatDate(quote.date)}</span>
                </div>
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
                filtered = filtered.filter(q => q.group === group);
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
                group: document.getElementById('quoteGroup').value,
                date: document.getElementById('quoteDate').value || new Date().toISOString().split('T')[0]
            };
            
            const url = id ? `/api/quotes/${id}` : '/api/quotes';
            const method = id ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(quote)
            });
            
            if (response.ok) {
                showAlert(id ? 'Zitat aktualisiert' : 'Zitat hinzugefügt', 'success');
                closeModal('quoteModal');
                loadQuotes();
            } else {
                showAlert('Fehler beim Speichern', 'error');
            }
        });

        function editQuote(quote) {
            showEditModal(quote);
        }

        async function deleteQuote(id) {
            if (!confirm('Zitat wirklich löschen?')) return;
            
            const response = await fetch(`/api/quotes/${id}`, {method: 'DELETE'});
            if (response.ok) {
                showAlert('Zitat gelöscht', 'success');
                loadQuotes();
            } else {
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
    return jsonify(quotes_db)

@app.route('/api/quotes', methods=['POST'])
def add_quote():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    global next_id
    data = request.json
    quote = {
        'id': next_id,
        'text': data['text'],
        'author': data['author'],
        'group': data['group'],
        'date': data.get('date', date.today().isoformat())
    }
    quotes_db.append(quote)
    next_id += 1
    return jsonify(quote), 201

@app.route('/api/quotes/<int:quote_id>', methods=['PUT'])
def update_quote(quote_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    for quote in quotes_db:
        if quote['id'] == quote_id:
            quote['text'] = data['text']
            quote['author'] = data['author']
            quote['group'] = data['group']
            quote['date'] = data.get('date', quote['date'])
            return jsonify(quote)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/quotes/<int:quote_id>', methods=['DELETE'])
def delete_quote(quote_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    global quotes_db
    quotes_db = [q for q in quotes_db if q['id'] != quote_id]
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
