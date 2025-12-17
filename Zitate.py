from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import os
import random
from functools import wraps
from supabase import create_client, Client

# ============ KONFIGURATION ============
ADMIN_PASSWORD = "admin123"  # ⚠️ HIER PASSWORT ÄNDERN!
SECRET_KEY = "dein-geheimer-schluessel-hier-aendern"  # ⚠️ WICHTIG: Ändern für Produktion!

# Supabase Konfiguration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "DEINE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "DEIN_SUPABASE_KEY")

# ============ FLASK APP SETUP ============
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Supabase Client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Fehler bei Supabase-Verbindung: {e}")
    supabase = None

# ============ HILFSFUNKTIONEN ============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'error': 'Nicht autorisiert'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============ ROUTEN ============
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password', '')
    
    if password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session.permanent = True
        return jsonify({'success': True, 'message': 'Erfolgreich eingeloggt!'})
    return jsonify({'success': False, 'message': 'Falsches Passwort!'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return jsonify({'success': True, 'message': 'Erfolgreich ausgeloggt!'})

@app.route('/api/check-auth')
def check_auth():
    return jsonify({'logged_in': session.get('logged_in', False)})

@app.route('/api/zitate', methods=['GET'])
def get_zitate():
    try:
        # Filter-Parameter
        gruppe = request.args.get('gruppe')
        datum_von = request.args.get('datum_von')
        datum_bis = request.args.get('datum_bis')
        
        # Basis-Query
        query = supabase.table('zitate').select('*')
        
        # Filter anwenden
        if gruppe and gruppe != 'alle':
            query = query.eq('gruppe', gruppe)
        if datum_von:
            query = query.gte('datum', datum_von)
        if datum_bis:
            query = query.lte('datum', datum_bis)
        
        # Sortierung
        query = query.order('datum', desc=True)
        
        response = query.execute()
        return jsonify({'success': True, 'zitate': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zitate/<int:id>', methods=['GET'])
def get_zitat(id):
    try:
        response = supabase.table('zitate').select('*').eq('id', id).execute()
        if response.data:
            return jsonify({'success': True, 'zitat': response.data[0]})
        return jsonify({'success': False, 'error': 'Zitat nicht gefunden'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zitate', methods=['POST'])
@login_required
def create_zitat():
    try:
        data = request.get_json()
        
        # Validierung
        if not data.get('text') or not data.get('autor'):
            return jsonify({'success': False, 'error': 'Text und Autor sind erforderlich'}), 400
        
        # Datum setzen
        datum = data.get('datum') or datetime.now().strftime('%Y-%m-%d')
        
        # Zitat erstellen
        zitat = {
            'text': data['text'],
            'autor': data['autor'],
            'gruppe': data.get('gruppe', 'Andere'),
            'datum': datum
        }
        
        response = supabase.table('zitate').insert(zitat).execute()
        return jsonify({'success': True, 'zitat': response.data[0]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zitate/<int:id>', methods=['PUT'])
@login_required
def update_zitat(id):
    try:
        data = request.get_json()
        
        updates = {}
        if 'text' in data:
            updates['text'] = data['text']
        if 'autor' in data:
            updates['autor'] = data['autor']
        if 'gruppe' in data:
            updates['gruppe'] = data['gruppe']
        if 'datum' in data:
            updates['datum'] = data['datum']
        
        response = supabase.table('zitate').update(updates).eq('id', id).execute()
        return jsonify({'success': True, 'zitat': response.data[0] if response.data else None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zitate/<int:id>', methods=['DELETE'])
@login_required
def delete_zitat(id):
    try:
        supabase.table('zitate').delete().eq('id', id).execute()
        return jsonify({'success': True, 'message': 'Zitat gelöscht'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zitat-des-tages')
def zitat_des_tages():
    try:
        response = supabase.table('zitate').select('*').execute()
        if response.data:
            # Zufälliges Zitat auswählen
            zitat = random.choice(response.data)
            return jsonify({'success': True, 'zitat': zitat})
        return jsonify({'success': False, 'error': 'Keine Zitate verfügbar'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ HTML TEMPLATE ============
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zitate-Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-card: #ffffff;
            --text-primary: #1a1a1a;
            --text-secondary: #6c757d;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --border: #e5e7eb;
            --shadow: rgba(0, 0, 0, 0.1);
            --glow: rgba(59, 130, 246, 0.4);
        }

        [data-theme="dark"] {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --accent: #3b82f6;
            --accent-hover: #60a5fa;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.5);
            --glow: rgba(59, 130, 246, 0.6);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: background 0.3s, color 0.3s;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            margin-bottom: 30px;
            animation: slideDown 0.5s ease;
        }

        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--accent), #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header-controls {
            display: flex;
            gap: 10px;
        }

        /* Buttons */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            background: var(--accent);
            color: white;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }

        .btn:hover {
            background: var(--accent-hover);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px var(--glow);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        .btn:active::before {
            width: 300px;
            height: 300px;
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }

        .btn-danger {
            background: #ef4444;
        }

        .btn-danger:hover {
            background: #dc2626;
        }

        /* Theme Toggle */
        .theme-toggle {
            width: 60px;
            height: 30px;
            background: var(--bg-secondary);
            border-radius: 15px;
            position: relative;
            cursor: pointer;
            border: 2px solid var(--border);
        }

        .theme-toggle::after {
            content: '🌙';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 22px;
            height: 22px;
            background: var(--accent);
            border-radius: 50%;
            transition: transform 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
        }

        [data-theme="dark"] .theme-toggle::after {
            content: '☀️';
            transform: translateX(30px);
        }

        /* Filter Section */
        .filter-section {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px var(--shadow);
            animation: fadeIn 0.5s ease;
        }

        .filter-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .form-group label {
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            padding: 10px;
            border: 2px solid var(--border);
            border-radius: 8px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--glow);
        }

        /* Quote Card */
        .quote-card {
            background: var(--bg-card);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px var(--shadow);
            border-left: 4px solid var(--accent);
            transition: all 0.3s;
            animation: fadeInUp 0.5s ease;
        }

        .quote-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px var(--glow);
        }

        .quote-text {
            font-size: 1.2rem;
            line-height: 1.6;
            margin-bottom: 15px;
            font-style: italic;
        }

        .quote-text::before {
            content: '"';
            font-size: 2rem;
            color: var(--accent);
            margin-right: 5px;
        }

        .quote-text::after {
            content: '"';
            font-size: 2rem;
            color: var(--accent);
            margin-left: 5px;
        }

        .quote-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
        }

        .quote-author {
            font-weight: 600;
            color: var(--text-primary);
        }

        .quote-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .badge-schueler {
            background: #10b981;
            color: white;
        }

        .badge-lehrer {
            background: #f59e0b;
            color: white;
        }

        .badge-andere {
            background: #6366f1;
            color: white;
        }

        .quote-actions {
            display: flex;
            gap: 10px;
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            animation: fadeIn 0.3s;
        }

        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: var(--bg-card);
            padding: 30px;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            animation: scaleIn 0.3s;
            box-shadow: 0 20px 60px var(--shadow);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .modal-header h2 {
            color: var(--text-primary);
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-secondary);
            transition: color 0.3s;
        }

        .close-btn:hover {
            color: var(--text-primary);
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes scaleIn {
            from {
                opacity: 0;
                transform: scale(0.9);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        /* Loading */
        .loading {
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
        }

        .spinner {
            border: 4px solid var(--border);
            border-top: 4px solid var(--accent);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }

            .filter-grid {
                grid-template-columns: 1fr;
            }
        }

        .quote-of-day {
            background: linear-gradient(135deg, var(--accent), #8b5cf6);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            animation: fadeIn 0.5s ease;
        }

        .quote-of-day h2 {
            margin-bottom: 20px;
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📚 Zitate-Manager</h1>
            <div class="header-controls">
                <div class="theme-toggle" onclick="toggleTheme()"></div>
                <button class="btn" id="loginBtn" onclick="showLoginModal()">Login</button>
                <button class="btn btn-danger hidden" id="logoutBtn" onclick="logout()">Logout</button>
                <button class="btn btn-secondary" onclick="showRandomQuote()">🎲 Zufälliges Zitat</button>
            </div>
        </div>

        <!-- Zitat des Tages -->
        <div class="quote-of-day" id="quoteOfDay">
            <h2>✨ Zitat des Tages ✨</h2>
            <div id="dailyQuoteContent"></div>
        </div>

        <!-- Admin Controls -->
        <div class="filter-section hidden" id="adminControls">
            <button class="btn" onclick="showAddModal()">➕ Neues Zitat hinzufügen</button>
        </div>

        <!-- Filter Section -->
        <div class="filter-section">
            <h3 style="margin-bottom: 15px;">🔍 Zitate filtern</h3>
            <div class="filter-grid">
                <div class="form-group">
                    <label>Gruppe</label>
                    <select id="filterGruppe" onchange="loadQuotes()">
                        <option value="alle">Alle</option>
                        <option value="Schüler">Schüler</option>
                        <option value="Lehrer">Lehrer</option>
                        <option value="Andere">Andere</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Von Datum</label>
                    <input type="date" id="filterDatumVon" onchange="loadQuotes()">
                </div>
                <div class="form-group">
                    <label>Bis Datum</label>
                    <input type="date" id="filterDatumBis" onchange="loadQuotes()">
                </div>
            </div>
            <button class="btn btn-secondary" onclick="resetFilters()">Filter zurücksetzen</button>
        </div>

        <!-- Quotes List -->
        <div id="quotesList"></div>
    </div>

    <!-- Login Modal -->
    <div class="modal" id="loginModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>🔐 Admin Login</h2>
                <button class="close-btn" onclick="closeModal('loginModal')">&times;</button>
            </div>
            <div class="form-group">
                <label>Passwort</label>
                <input type="password" id="loginPassword" onkeypress="if(event.key==='Enter') login()">
            </div>
            <button class="btn" onclick="login()" style="width: 100%; margin-top: 15px;">Login</button>
        </div>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal" id="quoteModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Neues Zitat</h2>
                <button class="close-btn" onclick="closeModal('quoteModal')">&times;</button>
            </div>
            <div class="form-group">
                <label>Zitat Text*</label>
                <textarea id="quoteText" rows="4" required></textarea>
            </div>
            <div class="form-group">
                <label>Autor*</label>
                <input type="text" id="quoteAuthor" required>
            </div>
            <div class="form-group">
                <label>Gruppe</label>
                <select id="quoteGruppe">
                    <option value="Schüler">Schüler</option>
                    <option value="Lehrer">Lehrer</option>
                    <option value="Andere">Andere</option>
                </select>
            </div>
            <div class="form-group">
                <label>Datum</label>
                <input type="date" id="quoteDatum">
            </div>
            <button class="btn" onclick="saveQuote()" style="width: 100%; margin-top: 15px;">Speichern</button>
        </div>
    </div>

    <!-- Random Quote Modal -->
    <div class="modal" id="randomQuoteModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>🎲 Zufälliges Zitat</h2>
                <button class="close-btn" onclick="closeModal('randomQuoteModal')">&times;</button>
            </div>
            <div id="randomQuoteContent"></div>
        </div>
    </div>

    <script>
        let isLoggedIn = false;
        let currentEditId = null;

        // Theme Toggle
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }

        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);

        // Check Auth Status
        async function checkAuth() {
            try {
                const response = await fetch('/api/check-auth');
                const data = await response.json();
                isLoggedIn = data.logged_in;
                updateUI();
            } catch (error) {
                console.error('Auth check failed:', error);
            }
        }

        // Update UI based on login status
        function updateUI() {
            document.getElementById('loginBtn').classList.toggle('hidden', isLoggedIn);
            document.getElementById('logoutBtn').classList.toggle('hidden', !isLoggedIn);
            document.getElementById('adminControls').classList.toggle('hidden', !isLoggedIn);
            loadQuotes();
        }

        // Login
        async function login() {
            const password = document.getElementById('loginPassword').value;
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password })
                });
                const data = await response.json();
                if (data.success) {
                    isLoggedIn = true;
                    closeModal('loginModal');
                    updateUI();
                    alert(data.message);
                } else {
                    alert(data.message);
                }
            } catch (error) {
                alert('Login fehlgeschlagen');
            }
        }

        // Logout
        async function logout() {
            try {
                await fetch('/api/logout', { method: 'POST' });
                isLoggedIn = false;
                updateUI();
                alert('Erfolgreich ausgeloggt');
            } catch (error) {
                alert('Logout fehlgeschlagen');
            }
        }

        // Load Quotes
        async function loadQuotes() {
            const gruppe = document.getElementById('filterGruppe').value;
            const datumVon = document.getElementById('filterDatumVon').value;
            const datumBis = document.getElementById('filterDatumBis').value;

            const params = new URLSearchParams();
            if (gruppe !== 'alle') params.append('gruppe', gruppe);
            if (datumVon) params.append('datum_von', datumVon);
            if (datumBis) params.append('datum_bis', datumBis);

            const quotesList = document.getElementById('quotesList');
            quotesList.innerHTML = '<div class="loading"><div class="spinner"></div>Lade Zitate...</div>';

            try {
                const response = await fetch(`/api/zitate?${params}`);
                const data = await response.json();

                if (data.success && data.zitate.length > 0) {
                    quotesList.innerHTML = data.zitate.map(quote => createQuoteCard(quote)).join('');
                } else {
                    quotesList.innerHTML = '<div class="loading">Keine Zitate gefunden</div>';
                }
            } catch (error) {
                quotesList.innerHTML = '<div class="loading">Fehler beim Laden der Zitate</div>';
            }
        }

        // Create Quote Card HTML
        function createQuoteCard(quote) {
            const badgeClass = {
                'Schüler': 'badge-schueler',
                'Lehrer': 'badge-lehrer',
                'Andere': 'badge-andere'
            }[quote.gruppe] || 'badge-andere';

            const actions = isLoggedIn ? `
                <div class="quote-actions">
                    <button class="btn btn-secondary" onclick="editQuote(${quote.id})">✏️ Bearbeiten</button>
                    <button class="btn btn-danger" onclick="deleteQuote(${quote.id})">🗑️ Löschen</button>
                </div>
            ` : '';

            return `
                <div class="quote-card">
                    <div class="quote-text">${quote.text}</div>
                    <div class="quote-meta">
                        <div>
                            <div class="quote-author">— ${quote.autor}</div>
                            <small style="color: var(--text-secondary);">${formatDate(quote.datum)}</small>
                        </div>
                        <span class="quote-badge ${badgeClass}">${quote.gruppe}</span>
                    </div>
                    ${actions}
                </div>
            `;
        }

        // Format Date
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString('de-DE', { year: 'numeric', month: 'long', day: 'numeric' });
        }

        // Show Add Modal
        function showAddModal() {
            currentEditId = null;
            document.getElementById('modalTitle').textContent = 'Neues Zitat';
            document.getElementById('quoteText').value = '';
            document.getElementById('quoteAuthor').value = '';
            document.getElementById('quoteGruppe').value = 'Andere';
            document.getElementById('quoteDatum').value = new Date().toISOString().split('T')[0];
            showModal('quoteModal');
        }

        // Edit Quote
        async function editQuote(id) {
            try {
                const response = await fetch(`/api/zitate/${id}`);
                const data = await response.json();
                if (data.success) {
                    currentEditId = id;
                    document.getElementById('modalTitle').textContent = 'Zitat bearbeiten';
                    document.getElementById('quoteText').value = data.zitat.text;
                    document.getElementById('quoteAuthor').value = data.zitat.autor;
                    document.getElementById('quoteGruppe').value = data.zitat.gruppe;
                    document.getElementById('quoteDatum').value = data.zitat.datum;
                    showModal('quoteModal');
                }
            } catch (error) {
                alert('Fehler beim Laden des Zitats');
            }
        }

        // Save Quote
        async function saveQuote() {
            const text = document.getElementById('quoteText').value;
            const autor = document.getElementById('quoteAuthor').value;
            const gruppe = document.getElementById('quoteGruppe').value;
            const datum = document.getElementById('quoteDatum').value;

            if (!text || !autor) {
                alert('Bitte Text und Autor ausfüllen');
                return;
            }

            const quoteData = { text, autor, gruppe, datum };

            try {
                const url = currentEditId ? `/api/zitate/${currentEditId}` : '/api/zitate';
                const method = currentEditId ? 'PUT' : 'POST';

                const response = await fetch(url, {
                    method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(quoteData)
                });

                const data = await response.json();
                if (data.success) {
                    closeModal('quoteModal');
                    loadQuotes();
                    alert(currentEditId ? 'Zitat aktualisiert' : 'Zitat hinzugefügt');
                } else {
                    alert('Fehler: ' + data.error);
                }
            } catch (error) {
                alert('Fehler beim Speichern');
            }
        }

        // Delete Quote
        async function deleteQuote(id) {
            if (!confirm('Zitat wirklich löschen?')) return;

            try {
                const response = await fetch(`/api/zitate/${id}`, { method: 'DELETE' });
                const data = await response.json();
                if (data.success) {
                    loadQuotes();
                    alert('Zitat gelöscht');
                }
            } catch (error) {
                alert('Fehler beim Löschen');
            }
        }

        // Load Quote of the Day
        async function loadQuoteOfDay() {
            try {
                const response = await fetch('/api/zitat-des-tages');
                const data = await response.json();
                if (data.success) {
                    const quote = data.zitat;
                    document.getElementById('dailyQuoteContent').innerHTML = `
                        <div class="quote-text" style="color: white; font-size: 1.3rem;">${quote.text}</div>
                        <div class="quote-author" style="color: rgba(255,255,255,0.9); margin-top: 15px; font-size: 1.1rem;">— ${quote.autor}</div>
                    `;
                }
            } catch (error) {
                document.getElementById('dailyQuoteContent').innerHTML = 'Kein Zitat verfügbar';
            }
        }

        // Show Random Quote
        async function showRandomQuote() {
            try {
                const response = await fetch('/api/zitat-des-tages');
                const data = await response.json();
                if (data.success) {
                    const quote = data.zitat;
                    const badgeClass = {
                        'Schüler': 'badge-schueler',
                        'Lehrer': 'badge-lehrer',
                        'Andere': 'badge-andere'
                    }[quote.gruppe] || 'badge-andere';

                    document.getElementById('randomQuoteContent').innerHTML = `
                        <div class="quote-text">${quote.text}</div>
                        <div class="quote-meta" style="justify-content: center;">
                            <div style="text-align: center;">
                                <div class="quote-author">— ${quote.autor}</div>
                                <small style="color: var(--text-secondary);">${formatDate(quote.datum)}</small>
                            </div>
                            <span class="quote-badge ${badgeClass}">${quote.gruppe}</span>
                        </div>
                    `;
                    showModal('randomQuoteModal');
                }
            } catch (error) {
                alert('Fehler beim Laden des Zitats');
            }
        }

        // Modal Functions
        function showModal(id) {
            document.getElementById(id).classList.add('active');
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }

        function showLoginModal() {
            document.getElementById('loginPassword').value = '';
            showModal('loginModal');
        }

        // Reset Filters
        function resetFilters() {
            document.getElementById('filterGruppe').value = 'alle';
            document.getElementById('filterDatumVon').value = '';
            document.getElementById('filterDatumBis').value = '';
            loadQuotes();
        }

        // Initialize
        checkAuth();
        loadQuoteOfDay();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
