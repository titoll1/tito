"""
𝙀𝙈𝙋𝙄𝙍𝙀
============================================================
Made with ❤️ by Krishu X Cheats
Copyright © 2026 Krishu X Cheats. All Rights Reserved.

FEATURES:
- Ticket Creation with Category Selection
- Auto Channel Creation
- Admin & User Mention on Creation
- Claim Ticket System
- Close Ticket System
- Delete Ticket System
- Category Management (Add/Delete)
- Dashboard Control Panel
- Beautiful UI
- Fully Customizable
============================================================
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View, Select
import json
import os
import asyncio
import traceback
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import threading
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
import re
import uuid
from dotenv import load_dotenv

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", 0))
TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID") or "1555278636926500976")
TICKET_PANEL_CHANNEL_ID = int(os.getenv("TICKET_PANEL_CHANNEL_ID") or "1555278704836476929")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID") or "1558293072411107421")
AUTO_WORK_ROLE_ID = int(os.getenv("AUTO_WORK_ROLE_ID") or "1557801133454397520")
WORK_REVIEW_CHANNEL_ID = int(os.getenv("WORK_REVIEW_CHANNEL_ID") or os.getenv("LOG_CHANNEL_ID") or "0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT") or "5000")

# Shown above the panel in the message body (outside the embed).
# Real notifications are allowed only when a brand-new canonical panel is created.
TICKET_PANEL_PING_CONTENT = "||@everyone @here ||"
TICKET_PANEL_EMBED_TITLE = "📩 مركز الدعم الفني والمساعدة | Support & Help Center"

if not TOKEN:
    raise ValueError("❌ TOKEN not found in environment variables!")

# =========================================================
# FLASK DASHBOARD SETUP
# =========================================================

app = Flask(__name__)
app.secret_key = os.urandom(24)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎫 𝙀𝙈𝙋𝙄𝙍𝙀 Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }
        
        .header h1 {
            font-size: 3em;
            background: linear-gradient(135deg, #f093fb, #f5576c, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #aaa;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card .number {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #f093fb, #f5576c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-card .label {
            color: #aaa;
            margin-top: 5px;
        }
        
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .config-card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .config-card h3 {
            margin-bottom: 15px;
            color: #4facfe;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .config-card label {
            display: block;
            margin: 10px 0 5px;
            color: #ccc;
            font-size: 0.9em;
        }
        
        .config-card input, .config-card select, .config-card textarea {
            width: 100%;
            padding: 10px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 0.95em;
        }
        
        .config-card input:focus, .config-card select:focus, .config-card textarea:focus {
            outline: none;
            border-color: #4facfe;
        }
        
        .config-card textarea {
            min-height: 60px;
            resize: vertical;
            font-family: inherit;
        }
        
        .btn {
            padding: 10px 25px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 15px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #4facfe, #00f2fe);
            color: #fff;
        }
        
        .btn-primary:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(79, 172, 254, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #43e97b, #38f9d7);
            color: #fff;
        }
        
        .btn-success:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(67, 233, 123, 0.4);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f5576c, #ff6b6b);
            color: #fff;
        }
        
        .btn-danger:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(245, 87, 108, 0.4);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #f093fb, #f5576c);
            color: #fff;
        }
        
        .btn-warning:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(240, 147, 251, 0.4);
        }
        
        .category-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 10px 0;
        }
        
        .category-tag {
            background: rgba(79, 172, 254, 0.2);
            border: 1px solid rgba(79, 172, 254, 0.3);
            padding: 8px 15px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .category-tag .remove {
            color: #f5576c;
            cursor: pointer;
            font-weight: bold;
        }
        
        .category-tag .remove:hover {
            color: #ff6b6b;
        }
        
        .logs {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            max-height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #0f0;
        }
        
        .logs .log-entry {
            padding: 3px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .logs .log-entry .time {
            color: #888;
        }
        
        .logs .log-entry .event {
            color: #4facfe;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-online {
            background: rgba(67, 233, 123, 0.2);
            color: #43e97b;
        }
        
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        
        @media (max-width: 768px) {
            .config-grid {
                grid-template-columns: 1fr;
            }
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎫 𝙀𝙈𝙋𝙄𝙍𝙀</h1>
            <p>Complete Ticket Management System</p>
            <div style="margin-top: 15px;">
                <span class="status-badge status-online">🟢 Bot Online</span>
                <span class="status-badge status-online" style="margin-left: 10px;">📊 {{ servers }} Servers</span>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="number">{{ total_tickets }}</div>
                <div class="label">Total Tickets</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ open_tickets }}</div>
                <div class="label">Open Tickets</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ closed_tickets }}</div>
                <div class="label">Closed Tickets</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ total_servers }}</div>
                <div class="label">Total Servers</div>
            </div>
        </div>
        
        <div class="config-grid">
            <!-- Category Management -->
            <div class="config-card">
                <h3>📂 Category Management</h3>
                <label>Add Category</label>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="category_name" placeholder="Category Name" style="flex: 1;">
                    <button class="btn btn-success" onclick="addCategory()">Add</button>
                </div>
                
                <label style="margin-top: 15px;">Current Categories</label>
                <div class="category-list" id="categoryList">
                    {% for cat in categories %}
                    <div class="category-tag">
                        {{ cat }}
                        <span class="remove" onclick="removeCategory('{{ cat }}')">✕</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <!-- Ticket Settings -->
            <div class="config-card">
                <h3>⚙️ Ticket Settings</h3>
                <form id="ticketForm">
                    <label>Ticket Channel Name Format</label>
                    <input type="text" id="ticket_format" value="{{ config.ticket_format or 'ticket-{user}' }}" placeholder="ticket-{user}">
                    
                    <label>Ticket Category ID</label>
                    <input type="text" id="ticket_category" value="{{ config.ticket_category or '' }}" placeholder="Category ID or Name">
                    
                    <label>Support Role ID</label>
                    <input type="text" id="support_role" value="{{ config.support_role or '' }}" placeholder="Role ID">
                    
                    <label>Ticket Message</label>
                    <textarea id="ticket_message" placeholder="Welcome to your ticket! Support will be with you shortly.">{{ config.ticket_message or 'Welcome to your ticket! Support will be with you shortly.' }}</textarea>
                    
                    <div class="btn-group">
                        <button type="submit" class="btn btn-primary" onclick="saveSettings()">Save Settings</button>
                        <button type="button" class="btn btn-warning" onclick="createPanel()">Create Ticket Panel</button>
                    </div>
                </form>
            </div>
            
            <!-- Activity Logs -->
            <div class="config-card">
                <h3>📋 Recent Activity</h3>
                <div class="logs" id="logs">
                    {% for log in logs[:10] %}
                    <div class="log-entry">
                        <span class="time">[{{ log.time }}]</span>
                        <span class="event">{{ log.event }}</span>
                        <span>{{ log.message }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div style="text-align: center; padding: 20px; color: #666; font-size: 0.9em;">
            Made with ❤️ by Krishu X Cheats | © 2026 All Rights Reserved
        </div>
    </div>
    
    <script>
        function addCategory() {
            const name = document.getElementById('category_name').value;
            if (!name) return alert('Please enter a category name');
            
            fetch('/api/category/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('❌ ' + data.error);
                }
            });
        }
        
        function removeCategory(name) {
            if (!confirm(`Remove category "${name}"?`)) return;
            
            fetch('/api/category/remove', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('❌ ' + data.error);
                }
            });
        }
        
        function saveSettings() {
            const data = {
                ticket_format: document.getElementById('ticket_format').value,
                ticket_category: document.getElementById('ticket_category').value,
                support_role: document.getElementById('support_role').value,
                ticket_message: document.getElementById('ticket_message').value
            };
            
            fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Settings saved successfully!');
                } else {
                    alert('❌ ' + data.error);
                }
            });
        }
        
        function createPanel() {
            fetch('/api/panel/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Ticket panel created successfully in current channel!');
                } else {
                    alert('❌ ' + data.error);
                }
            });
        }
        
        // Auto-refresh logs
        setInterval(() => {
            fetch('/api/logs')
                .then(response => response.json())
                .then(data => {
                    const logsDiv = document.getElementById('logs');
                    if (logsDiv) {
                        logsDiv.innerHTML = data.logs.map(log => 
                            `<div class="log-entry">
                                <span class="time">[${log.time}]</span>
                                <span class="event">${log.event}</span>
                                <span>${log.message}</span>
                            </div>`
                        ).join('');
                    }
                })
                .catch(() => {});
        }, 30000);
    </script>
</body>
</html>
"""

# =========================================================
# DATA MANAGEMENT
# =========================================================

CONFIG_FILE = "ticket_config.json"
DATA_FILE = "ticket_data.json"
LOGS_FILE = "ticket_logs.json"
WORK_REQUESTS_FILE = "work_requests.json"

def load_json(file_path, default):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except:
        return False

DEFAULT_CONFIG = {
    "categories": ["Support", "Work"],
    "ticket_format": "ticket-{user}",
    "ticket_category": str(TICKET_CATEGORY_ID) if TICKET_CATEGORY_ID else "",
    "support_role": "",
    "ticket_message": "Welcome to your ticket! Support will be with you shortly."
}

# =========================================================
# FLASK ROUTES
# =========================================================

@app.route('/')
def dashboard():
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    data = load_json(DATA_FILE, {"total": 0, "open": 0, "closed": 0})
    logs = load_json(LOGS_FILE, [])
    
    server_count = len(bot.guilds) if hasattr(bot, 'guilds') else 0
    
    return render_template_string(
        DASHBOARD_HTML,
        config=config,
        categories=config.get("categories", []),
        total_tickets=data.get("total", 0),
        open_tickets=data.get("open", 0),
        closed_tickets=data.get("closed", 0),
        total_servers=server_count,
        servers=server_count,
        logs=logs[-10:] if logs else []
    )

@app.route('/api/category/add', methods=['POST'])
def api_add_category():
    try:
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({"success": False, "error": "Category name is required"})
        
        config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        if name in config.get("categories", []):
            return jsonify({"success": False, "error": "Category already exists"})
        
        config["categories"].append(name)
        save_json(CONFIG_FILE, config)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/category/remove', methods=['POST'])
def api_remove_category():
    try:
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({"success": False, "error": "Category name is required"})
        
        config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        if name not in config.get("categories", []):
            return jsonify({"success": False, "error": "Category not found"})
        
        config["categories"].remove(name)
        save_json(CONFIG_FILE, config)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/settings', methods=['POST'])
def api_settings():
    try:
        data = request.json
        config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        
        for key, value in data.items():
            config[key] = value
        
        save_json(CONFIG_FILE, config)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/panel/create', methods=['POST'])
def api_create_panel():
    try:
        current_bot = globals().get("bot")
        if not current_bot or not current_bot.is_ready() or not current_bot.loop.is_running():
            return jsonify({"success": False, "error": "Bot is not online yet"}), 503
        cog = current_bot.get_cog("TicketBot")
        if cog is None:
            return jsonify({"success": False, "error": "TicketBot cog is not loaded"}), 503
        future = asyncio.run_coroutine_threadsafe(cog.publish_panel(), current_bot.loop)
        message = future.result(timeout=20)
        return jsonify({"success": True, "message": f"Panel published in channel {TICKET_PANEL_CHANNEL_ID}", "message_id": message.id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def api_logs():
    logs = load_json(LOGS_FILE, [])
    return jsonify({"logs": logs[-20:]})

# =========================================================
# DISCORD UI COMPONENTS
# =========================================================

# Persistent WORK application records and locks.
_work_request_lock = asyncio.Lock()
_pending_support_uploads = {}  # user_id -> {guild_id, name, age, problem, started_at}

def load_work_requests():
    data = load_json(WORK_REQUESTS_FILE, {"requests": {}})
    if not isinstance(data, dict) or not isinstance(data.get("requests"), dict):
        return {"requests": {}}
    return data

def save_work_requests(data):
    return save_json(WORK_REQUESTS_FILE, data)

def has_work_staff_permission(interaction: discord.Interaction) -> bool:
    """One configured staff role can review both WORK and SUPPORT applications."""
    guild = interaction.guild
    if guild is None:
        return False
    if getattr(interaction.user, "guild_permissions", None) and interaction.user.guild_permissions.administrator:
        return True
    if not ADMIN_ROLE_ID:
        return False
    role = guild.get_role(ADMIN_ROLE_ID)
    return bool(role and role in getattr(interaction.user, "roles", []))


async def ensure_private_review_channel(guild: discord.Guild, channel: discord.TextChannel) -> bool:
    """Secure the configured review channel for the one authorized staff role and the bot."""
    me = guild.me
    if me is None or not me.guild_permissions.manage_channels:
        return False
    staff_role = guild.get_role(ADMIN_ROLE_ID) if ADMIN_ROLE_ID else None
    if staff_role is None:
        return False
    try:
        await channel.set_permissions(
            guild.default_role,
            view_channel=False,
            send_messages=False,
            read_message_history=False,
            reason="Keep Empire application review private",
        )
        await channel.set_permissions(
            staff_role,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            embed_links=True,
            attach_files=True,
            reason="Allow authorized staff to review applications",
        )
        await channel.set_permissions(
            me,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            embed_links=True,
            attach_files=True,
            reason="Allow the bot to deliver application reviews",
        )
        return True
    except (discord.Forbidden, discord.HTTPException):
        return False

def active_work_request_for_user(guild: discord.Guild, user_id: int, data=None, category="Work"):
    """Return an active application/ticket for this user and category; repair stale records."""
    data = data or load_work_requests()
    changed = False
    for request_id, item in data["requests"].items():
        if int(item.get("user_id", 0) or 0) != int(user_id):
            continue
        if int(item.get("guild_id", 0) or 0) != int(guild.id):
            continue
        item_category = str(item.get("category", "Work")).lower()
        if item_category != str(category or "Work").lower():
            continue
        status = item.get("status")
        if status in ("PENDING", "PROCESSING"):
            return request_id, item, changed
        if status == "ACCEPTED":
            channel_id = int(item.get("ticket_channel_id", 0) or 0)
            if channel_id and guild.get_channel(channel_id):
                return request_id, item, changed
            item["status"] = "CLOSED"
            changed = True
    if changed:
        save_work_requests(data)
    return None, None, changed


def find_user_active_ticket_or_request(guild: discord.Guild, user_id: int):
    """Find any open ticket or pending application for this user, across all categories.

    Open Discord channels are checked first, so this also works after bot restarts
    without relying only on in-memory state. Pending applications are persisted in
    work_requests.json and therefore survive restarts too.
    """
    marker = f"Created by ID: {int(user_id)}"
    for channel in guild.text_channels:
        topic = channel.topic or ""
        if marker in topic and "Ticket #" in topic and "Category:" in topic:
            return "ticket", channel

    data = load_work_requests()
    changed = False
    for request_id, item in data["requests"].items():
        if int(item.get("user_id", 0) or 0) != int(user_id):
            continue
        if int(item.get("guild_id", 0) or 0) != int(guild.id):
            continue
        status = item.get("status")
        if status in ("PENDING", "PROCESSING"):
            return "request", (request_id, item)
        if status == "ACCEPTED":
            channel_id = int(item.get("ticket_channel_id", 0) or 0)
            if channel_id and guild.get_channel(channel_id):
                return "ticket", guild.get_channel(channel_id)
            item["status"] = "CLOSED"
            item["closed_at"] = datetime.now().isoformat(timespec="seconds")
            changed = True
    if changed:
        save_work_requests(data)
    return None, None


def active_ticket_message(guild: discord.Guild, user_id: int):
    """Build a clear duplicate-ticket message for active tickets, requests, or image uploads."""
    pending_upload = _pending_support_uploads.get(int(user_id))
    if pending_upload and int(pending_upload.get("guild_id", 0) or 0) == int(guild.id):
        return "عندك طلب SUPPORT لسه مستني رفع الصورة في الخاص. كمّل رفع الصورة أو اكتب إلغاء قبل ما تبدأ طلب جديد."
    kind, value = find_user_active_ticket_or_request(guild, user_id)
    if kind == "ticket":
        return f"عندك تكت مفتوحة بالفعل: {value.mention} — لازم تقفلها الأول قبل ما تفتح تكت جديدة."
    if kind == "request":
        request_id, item = value
        category = str(item.get("category", "Ticket")).upper()
        return f"عندك طلب {category} قيد المراجعة بالفعل (رقم الطلب: `{request_id}`). استنى قرار الإدارة الأول."
    return None

async def get_work_review_channel(guild: discord.Guild):
    channel_id = WORK_REVIEW_CHANNEL_ID
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    configured = config.get("work_review_channel")
    if configured and str(configured).isdigit():
        channel_id = int(configured)
    if not channel_id:
        return None
    channel = guild.get_channel(channel_id)
    if channel is None:
        try:
            channel = await guild.fetch_channel(channel_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None
    return channel if isinstance(channel, discord.TextChannel) else None

async def create_approved_work_ticket(guild: discord.Guild, request_id: str, item: dict):
    """Create a private category ticket only after an authorized ACCEPT action."""
    category = str(item.get("category", "Work")).title()
    user_id = int(item["user_id"])
    member = guild.get_member(user_id)
    if member is None:
        member = await guild.fetch_member(user_id)

    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    category_value = str(config.get("ticket_category") or TICKET_CATEGORY_ID or "").strip()
    ticket_category = None
    if category_value.isdigit():
        candidate = guild.get_channel(int(category_value))
        if isinstance(candidate, discord.CategoryChannel):
            ticket_category = candidate
    else:
        ticket_category = next((cat for cat in guild.categories if cat.name.lower() == category_value.lower()), None)
    if ticket_category is None:
        ticket_category = next((cat for cat in guild.categories if "ticket" in cat.name.lower()), None)
    if ticket_category is None:
        ticket_category = await guild.create_category("🎫 Tickets")

    async with _ticket_number_lock:
        stats = load_json(DATA_FILE, {"total": 0, "open": 0, "closed": 0})
        number = await next_ticket_number(guild)
        stats["total"] = number
        stats["open"] = int(stats.get("open", 0) or 0) + 1
        stats["closed"] = int(stats.get("closed", 0) or 0)
        if not save_json(DATA_FILE, stats):
            raise RuntimeError("تعذر حفظ رقم التكت التسلسلي")

    overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    if guild.me:
        overwrites[guild.me] = discord.PermissionOverwrite(
            view_channel=True, send_messages=True, read_message_history=True,
            manage_channels=True, manage_messages=True, embed_links=True, attach_files=True
        )
    overwrites[member] = discord.PermissionOverwrite(
        view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True
    )
    role_ids = {ADMIN_ROLE_ID} if ADMIN_ROLE_ID else set()
    for role_id in role_ids:
        role = guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )

    channel = await ticket_category.create_text_channel(
        name=f"ticket-{number:03d}",
        overwrites=overwrites,
        topic=(f"Ticket #{number} | Created by ID: {user_id} | Category: {category} | "
               f"Application request ID: {request_id}" +
               (f" | Work request ID: {request_id} | Work approval: accepted" if category.lower() == "work" else "")),
    )
    title_map = {
        "work": "💼 WORK Ticket",
        "support": "🛟 SUPPORT Ticket",
    }
    embed = discord.Embed(
        title=f"{title_map.get(category.lower(), category + ' Ticket')} — #{number:03d}",
        description="تمت الموافقة على طلبك من الإدارة. تقدر تبدأ المحادثة هنا.",
        color=discord.Color.green(), timestamp=datetime.now()
    )
    embed.add_field(name="👤 صاحب الطلب", value=member.mention, inline=False)
    embed.add_field(name="الاسم", value=discord.utils.escape_markdown(str(item.get("name", "—")))[:1024], inline=True)
    embed.add_field(name="السن", value=str(item.get("age", "—"))[:100], inline=True)
    if category.lower() == "work":
        embed.add_field(name="رقم الكاش / المحفظة", value=f"||{str(item.get('wallet', '—'))[:100]}||", inline=False)
    elif category.lower() == "support":
        raw_images = item.get("images", [])
        image_urls = []
        if isinstance(raw_images, list):
            for image in raw_images:
                image_url = str(image.get("url", "")).strip() if isinstance(image, dict) else str(image).strip()
                if image_url and image_url not in image_urls:
                    image_urls.append(image_url)
        legacy_image = str(item.get("image_url", "")).strip()
        if legacy_image and legacy_image not in image_urls:
            image_urls.insert(0, legacy_image)
        embed.add_field(name="عدد الصور", value=str(len(image_urls)), inline=True)
        embed.add_field(name="تفاصيل المشكلة", value=str(item.get("problem", "—"))[:500], inline=False)
    embed.add_field(name="رقم الطلب", value=request_id, inline=True)
    embed.set_footer(text=f"𝙀𝙈𝙋𝙄𝙍𝙀 • {category.upper()}")
    admin_role = guild.get_role(ADMIN_ROLE_ID) if ADMIN_ROLE_ID else None
    await channel.send(
        content=(
            f"{member.mention} ✅ تم قبول التكت بتاعتك من الإدارة، تقدر تبدأ دلوقتي. "
            f"{admin_role.mention if admin_role else ''}"
        ).strip(),
        embed=embed, view=TicketView(),
        allowed_mentions=discord.AllowedMentions(users=True, roles=True)
    )
    if category.lower() == "support":
        raw_images = item.get("images", [])
        image_urls = []
        if isinstance(raw_images, list):
            for image in raw_images:
                image_url = str(image.get("url", "")).strip() if isinstance(image, dict) else str(image).strip()
                if image_url and image_url not in image_urls:
                    image_urls.append(image_url)
        legacy_image = str(item.get("image_url", "")).strip()
        if legacy_image and legacy_image not in image_urls:
            image_urls.insert(0, legacy_image)
        for image_index, image_url in enumerate(image_urls[:20], start=1):
            image_embed = discord.Embed(
                title=f"🖼️ صورة المشكلة {image_index}/{len(image_urls[:20])}",
                color=discord.Color.blurple()
            )
            image_embed.set_image(url=str(image_url))
            await channel.send(embed=image_embed)
    return channel, number

class WorkReviewView(View):
    """Persistent admin-only accept/reject controls for one WORK request."""
    def __init__(self, request_id: str, disabled: bool = False, prefix: str = "work"):
        super().__init__(timeout=None)
        self.prefix = prefix
        accept = Button(label="ACCEPT", style=discord.ButtonStyle.success, emoji="✅",
                        custom_id=f"empire_{prefix}_accept:{request_id}", disabled=disabled)
        reject = Button(label="REJECT", style=discord.ButtonStyle.danger, emoji="❌",
                        custom_id=f"empire_{prefix}_reject:{request_id}", disabled=disabled)
        accept.callback = self.accept_callback
        reject.callback = self.reject_callback
        self.add_item(accept)
        self.add_item(reject)
        self.request_id = request_id

    async def accept_callback(self, interaction: discord.Interaction):
        if not has_work_staff_permission(interaction):
            await interaction.response.send_message("❌ الموافقة متاحة للإدارة المصرح لها فقط.", ephemeral=True)
            return
        async with _work_request_lock:
            data = load_work_requests()
            item = data["requests"].get(self.request_id)
            if not item or item.get("status") != "PENDING":
                await interaction.response.send_message("ℹ️ الطلب ده اتحسم بالفعل أو مش موجود.", ephemeral=True)
                return
            item["status"] = "PROCESSING"
            item["reviewed_by"] = interaction.user.id
            item["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
            save_work_requests(data)
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            existing_channel = next((
                ch for ch in interaction.guild.text_channels
                if (f"Application request ID: {self.request_id}" in (ch.topic or "")
                    or f"Work request ID: {self.request_id}" in (ch.topic or ""))
            ), None)
            if existing_channel is not None:
                channel = existing_channel
                match = re.search(r"Ticket #(\d+)", channel.topic or "")
                number = int(match.group(1)) if match else 0
            else:
                channel, number = await create_approved_work_ticket(interaction.guild, self.request_id, item)
        except Exception as exc:
            async with _work_request_lock:
                data = load_work_requests()
                current = data["requests"].get(self.request_id)
                if current and current.get("status") == "PROCESSING":
                    current["status"] = "PENDING"
                    current.pop("reviewed_by", None)
                    current.pop("reviewed_at", None)
                    save_work_requests(data)
            await interaction.followup.send(f"❌ فشل إنشاء التكت، الطلب رجع للانتظار. التفاصيل: {exc}", ephemeral=True)
            return
        async with _work_request_lock:
            data = load_work_requests()
            current = data["requests"].get(self.request_id)
            if current:
                current["status"] = "ACCEPTED"
                current["ticket_channel_id"] = channel.id
                current["ticket_number"] = number
                current["reviewed_by"] = interaction.user.id
                current["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
                save_work_requests(data)
        role_note = ""
        if str(item.get("category", "")).lower() == "work" and AUTO_WORK_ROLE_ID:
            try:
                member = interaction.guild.get_member(int(item["user_id"]))
                if member is None:
                    member = await interaction.guild.fetch_member(int(item["user_id"]))
                role = interaction.guild.get_role(AUTO_WORK_ROLE_ID)
                if role is None:
                    role_note = " ⚠️ الرتبة غير موجودة."
                elif role not in member.roles:
                    await member.add_roles(role, reason="WORK request accepted")
            except (discord.Forbidden, discord.HTTPException, discord.NotFound) as exc:
                role_note = " ⚠️ تعذر إعطاء الرتبة تلقائيًا؛ راجع صلاحيات البوت وترتيب الرتبة."
                print(f"[AUTO WORK ROLE ERROR] {type(exc).__name__}: {exc}")
        try:
            old_embed = interaction.message.embeds[0] if interaction.message.embeds else discord.Embed(title="WORK request")
            updated = discord.Embed.from_dict(old_embed.to_dict())
            category_label = str(item.get("category", "Work")).upper()
            updated.add_field(name="الحالة", value=f"✅ ACCEPTED بواسطة {interaction.user.mention} • {channel.mention}", inline=False)
            await interaction.message.edit(embed=updated, view=WorkReviewView(self.request_id, disabled=True, prefix=self.prefix))
        except discord.HTTPException:
            pass
        try:
            user = interaction.guild.get_member(int(item["user_id"]))
            if user:
                await user.send(
                    f"✅ {user.mention} تم قبول طلب {str(item.get('category', 'Work')).upper()} من الإدارة.\n"
                    f"تم فتح التكت: {channel.mention}"
                )
        except (discord.Forbidden, discord.HTTPException):
            pass
        await interaction.followup.send(f"✅ تمت الموافقة وإنشاء {channel.mention}.{role_note}", ephemeral=True)

    async def reject_callback(self, interaction: discord.Interaction):
        if not has_work_staff_permission(interaction):
            await interaction.response.send_message("❌ الرفض متاح للإدارة المصرح لها فقط.", ephemeral=True)
            return
        async with _work_request_lock:
            data = load_work_requests()
            item = data["requests"].get(self.request_id)
            if not item or item.get("status") != "PENDING":
                await interaction.response.send_message("ℹ️ الطلب ده اتحسم بالفعل أو مش موجود.", ephemeral=True)
                return
            item["status"] = "REJECTED"
            item["reviewed_by"] = interaction.user.id
            item["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
            save_work_requests(data)
        if interaction.message.embeds:
            updated = discord.Embed.from_dict(interaction.message.embeds[0].to_dict())
        else:
            updated = discord.Embed(title="WORK request")
        updated.add_field(name="الحالة", value=f"❌ REJECTED بواسطة {interaction.user.mention}", inline=False)
        await interaction.response.edit_message(embed=updated, view=WorkReviewView(self.request_id, disabled=True, prefix=self.prefix))
        try:
            user = interaction.guild.get_member(int(item["user_id"]))
            if user:
                await user.send(f"❌ تم رفض طلب {str(item.get('category', 'Work')).upper()} الخاص بك من الإدارة.")
        except (discord.Forbidden, discord.HTTPException):
            pass

class WorkRequestModal(discord.ui.Modal, title="WORK Application | طلب عمل"):
    name_input = discord.ui.TextInput(label="الاسم | Name", placeholder="اكتب اسمك", min_length=2, max_length=80)
    age_input = discord.ui.TextInput(label="السن | Age", placeholder="اكتب عمرك بالأرقام", min_length=1, max_length=3)
    wallet_input = discord.ui.TextInput(label="رقم الكاش أو المحفظة", placeholder="اكتب رقم الكاش أو المحفظة", min_length=11, max_length=11)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("❌ الفورم متاح داخل السيرفر فقط.", ephemeral=True)
            return
        age_text = str(self.age_input.value).strip()
        if not age_text.isdigit() or not 10 <= int(age_text) <= 100:
            await interaction.response.send_message("❌ اكتب سن صحيح بالأرقام من 10 إلى 100.", ephemeral=True)
            return
        wallet_text = str(self.wallet_input.value).strip()
        if not re.fullmatch(r"(?:010|011|012|015)\d{8}", wallet_text):
            await interaction.response.send_message(
                "❌ رقم الكاش لازم يبدأ بـ 010 أو 011 أو 012 أو 015 ويكون 11 رقمًا كاملًا.",
                ephemeral=True
            )
            return
        review_channel = await get_work_review_channel(interaction.guild)
        if review_channel is None:
            await interaction.response.send_message(
                "❌ قناة مراجعة طلبات WORK غير مضبوطة. أضف WORK_REVIEW_CHANNEL_ID إلى ملف .env أو اضبط LOG_CHANNEL_ID على قناة إدارية خاصة.",
                ephemeral=True
            )
            return
        if not await ensure_private_review_channel(interaction.guild, review_channel):
            await interaction.response.send_message(
                "❌ مقدرتش أخفي قناة المراجعة تلقائيًا. تأكد إن ADMIN_ROLE_ID صحيح وإن البوت عنده Manage Channels، وإن رتبة البوت أعلى من رتبة الإدارة.",
                ephemeral=True
            )
            return
        request_id = uuid.uuid4().hex[:12]
        async with _work_request_lock:
            data = load_work_requests()
            duplicate_message = active_ticket_message(interaction.guild, interaction.user.id)
            if duplicate_message:
                await interaction.response.send_message("⏳ " + duplicate_message, ephemeral=True)
                return
            item = {
                "request_id": request_id, "guild_id": interaction.guild.id, "user_id": interaction.user.id,
                "category": "Work", "username": str(interaction.user), "name": str(self.name_input.value).strip(),
                "age": int(age_text), "wallet": wallet_text,
                "status": "PENDING", "created_at": datetime.now().isoformat(timespec="seconds"),
                "review_channel_id": review_channel.id, "review_message_id": None,
            }
            data["requests"][request_id] = item
            if not save_work_requests(data):
                await interaction.response.send_message("❌ تعذر حفظ الطلب. حاول مرة أخرى لاحقًا.", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True, thinking=True)
            embed = discord.Embed(title="💼 طلب WORK جديد", color=discord.Color.orange(), timestamp=datetime.now())
            embed.add_field(name="مقدم الطلب", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
            embed.add_field(name="الاسم", value=discord.utils.escape_markdown(item["name"])[:1024], inline=True)
            embed.add_field(name="السن", value=str(item["age"]), inline=True)
            embed.add_field(name="رقم الكاش / المحفظة", value=f"||{item['wallet']}||", inline=False)
            embed.add_field(name="رقم الطلب", value=f"`{request_id}`", inline=True)
            embed.add_field(name="الحالة", value="🟠 PENDING — في انتظار موافقة الإدارة", inline=False)
            embed.set_footer(text="𝙀𝙈𝙋𝙄𝙍𝙀 • WORK Review")
            try:
                review_message = await review_channel.send(
                    embed=embed, view=WorkReviewView(request_id),
                    allowed_mentions=discord.AllowedMentions.none()
                )
            except Exception as exc:
                data = load_work_requests()
                if request_id in data["requests"]:
                    data["requests"][request_id]["status"] = "FAILED"
                    data["requests"][request_id]["error"] = str(exc)[:300]
                    save_work_requests(data)
                await interaction.followup.send("❌ تعذر إرسال الطلب لقناة الإدارة. راجع صلاحيات البوت والقناة.", ephemeral=True)
                return
            data = load_work_requests()
            if request_id in data["requests"]:
                data["requests"][request_id]["review_message_id"] = review_message.id
                save_work_requests(data)
        await interaction.followup.send("✅ تم استلام طلبك وإرساله للإدارة. لن تُفتح التكت إلا بعد موافقة مسؤول مخوّل.", ephemeral=True)

async def submit_review_application(interaction: discord.Interaction, category: str, fields: dict):
    """Persist a Support application and send it to the private staff review channel."""
    if interaction.guild is None:
        await interaction.response.send_message("❌ الفورم متاح داخل السيرفر فقط.", ephemeral=True)
        return
    guild = interaction.guild
    review_channel = await get_work_review_channel(guild)
    if review_channel is None:
        await interaction.response.send_message(
            "❌ قناة مراجعة الطلبات غير مضبوطة. اضبط WORK_REVIEW_CHANNEL_ID أو LOG_CHANNEL_ID في ملف .env.",
            ephemeral=True
        )
        return
    if not await ensure_private_review_channel(guild, review_channel):
        await interaction.response.send_message(
            "❌ مقدرتش أخفي قناة المراجعة تلقائيًا. تأكد من ADMIN_ROLE_ID وصلاحية Manage Channels للبوت.",
            ephemeral=True
        )
        return

    request_id = uuid.uuid4().hex[:12]
    async with _work_request_lock:
        data = load_work_requests()
        duplicate_message = active_ticket_message(guild, interaction.user.id)
        if duplicate_message:
            await interaction.response.send_message("⏳ " + duplicate_message, ephemeral=True)
            return

        item = {
            "request_id": request_id, "guild_id": guild.id, "user_id": interaction.user.id,
            "category": category.title(), "username": str(interaction.user), "name": fields["name"],
            "age": int(fields["age"]), "status": "PENDING",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "review_channel_id": review_channel.id, "review_message_id": None,
            **{k: v for k, v in fields.items() if k not in ("name", "age")},
        }
        data["requests"][request_id] = item
        if not save_work_requests(data):
            await interaction.response.send_message("❌ تعذر حفظ الطلب. حاول مرة أخرى لاحقًا.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        category_title = {"support": "الدعم الفني", "shop": "طلبات الشوب"}.get(category.lower(), category.title())
        embed = discord.Embed(
            title=f"📨 طلب {category_title} جديد | {category.upper()}",
            color=discord.Color.orange(), timestamp=datetime.now()
        )
        embed.add_field(name="مقدم الطلب", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
        embed.add_field(name="الاسم | Name", value=discord.utils.escape_markdown(item["name"])[:1024], inline=True)
        embed.add_field(name="السن | Age", value=str(item["age"]), inline=True)
        if category.lower() == "support":
            if item.get("image_url"):
                embed.add_field(name="رابط الصورة | Image URL", value=str(item["image_url"])[:1024], inline=False)
            else:
                embed.add_field(name="رابط الصورة | Image URL", value="غير مرفق", inline=False)
            embed.add_field(name="المشكلة | Problem Details", value=str(item.get("problem", "—"))[:500], inline=False)
        elif category.lower() == "shop":
            embed.add_field(name="🛍️ المطلوب من المتجر | Requested Item", value=str(item.get("item", "—"))[:1000], inline=False)
        embed.add_field(name="رقم الطلب", value=f"`{request_id}`", inline=True)
        embed.add_field(name="الحالة", value="🟠 PENDING — في انتظار موافقة الإدارة", inline=False)
        embed.set_footer(text=f"𝙀𝙈𝙋𝙄𝙍𝙀 • {category.upper()} Review")
        try:
            review_message = await review_channel.send(
                embed=embed, view=WorkReviewView(request_id, prefix="application"),
                allowed_mentions=discord.AllowedMentions.none()
            )
        except Exception as exc:
            data = load_work_requests()
            if request_id in data["requests"]:
                data["requests"][request_id]["status"] = "FAILED"
                data["requests"][request_id]["error"] = str(exc)[:300]
                save_work_requests(data)
            await interaction.followup.send("❌ تعذر إرسال الطلب لقناة الإدارة. راجع صلاحيات البوت والقناة.", ephemeral=True)
            return
        data = load_work_requests()
        if request_id in data["requests"]:
            data["requests"][request_id]["review_message_id"] = review_message.id
            save_work_requests(data)
    await interaction.followup.send(
        f"✅ تم استلام طلب {category.upper()} وإرساله للإدارة. لن تُفتح التكت إلا بعد موافقة مسؤول مخوّل.",
        ephemeral=True
    )


class ShopRequestModal(discord.ui.Modal, title="Shop Application | طلب شراء"):
    name_input = discord.ui.TextInput(label="الاسم | Name", placeholder="اكتب اسمك", min_length=2, max_length=80)
    item_input = discord.ui.TextInput(label="المطلوب من الشوب | Requested Item", placeholder="اكتب المنتج أو الخدمة المطلوبة", style=discord.TextStyle.paragraph, min_length=1, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("❌ الفورم متاح داخل السيرفر فقط.", ephemeral=True)
            return
        await submit_review_application(
            interaction,
            "Shop",
            {"name": str(self.name_input.value).strip(), "age": 0, "item": str(self.item_input.value).strip()}
        )


class SupportRequestModal(discord.ui.Modal, title="Support Application | الدعم الفني"):
    name_input = discord.ui.TextInput(label="الاسم | Name", placeholder="اكتب اسمك", min_length=2, max_length=80)
    age_input = discord.ui.TextInput(label="السن | Age", placeholder="اكتب عمرك بالأرقام", min_length=1, max_length=3)
    image_url_input = discord.ui.TextInput(label="رابط الصورة | Image URL", placeholder="https://... (اختياري)", required=False, max_length=1000)
    problem_input = discord.ui.TextInput(label="مشكلتك | Your problem", style=discord.TextStyle.paragraph, placeholder="اشرح المشكلة بالتفصيل", min_length=1, max_length=500)

    async def on_submit(self, interaction: discord.Interaction):
        age = str(self.age_input.value).strip()
        if not age.isdigit() or not 10 <= int(age) <= 100:
            await interaction.response.send_message("❌ اكتب سن صحيح بالأرقام من 10 إلى 100.", ephemeral=True)
            return
        if interaction.guild is None:
            await interaction.response.send_message("❌ الفورم متاح داخل السيرفر فقط.", ephemeral=True)
            return
        await submit_review_application(
            interaction,
            "Support",
            {
                "name": str(self.name_input.value).strip(),
                "age": int(age),
                "problem": str(self.problem_input.value).strip(),
                "images": [],
                "image_url": str(self.image_url_input.value).strip(),
            },
        )
        _pending_support_uploads[interaction.user.id] = {
            "guild_id": interaction.guild.id,
            "request_id": None,
            "images": [],
            "started_at": datetime.now().isoformat(timespec="seconds"),
        }
        try:
            await interaction.user.send("📎 ابعت صورة المشكلة هنا كمرفق اختياريًا، وهتتضاف لطلب Support عند الإدارة.")
        except (discord.Forbidden, discord.HTTPException):
            pass



async def next_ticket_number(guild: discord.Guild) -> int:
    """Return the next global ticket number without reusing existing numbers."""
    data = load_json(DATA_FILE, {"total": 0, "open": 0, "closed": 0})
    highest = int(data.get("total", 0) or 0)
    for channel in guild.text_channels:
        match = re.fullmatch(r"ticket-(\d+)", channel.name.lower())
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


# A single lock prevents two users receiving the same sequence number at once.
_ticket_number_lock = asyncio.Lock()

async def create_ticket(interaction: discord.Interaction, category: str):
    """Create a ticket with a permanent, monotonically increasing number."""
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    if guild is None:
        await interaction.followup.send("❌ لا يمكن فتح تذكرة خارج السيرفر.", ephemeral=True)
        return

    async with _work_request_lock:
        duplicate_message = active_ticket_message(guild, interaction.user.id)
    if duplicate_message:
        await interaction.followup.send("⏳ " + duplicate_message, ephemeral=True)
        return

    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    category_id = str(config.get("ticket_category") or TICKET_CATEGORY_ID or "").strip()
    ticket_category = None
    if category_id.isdigit():
        candidate = guild.get_channel(int(category_id))
        if isinstance(candidate, discord.CategoryChannel):
            ticket_category = candidate
    else:
        for cat in guild.categories:
            if cat.name.lower() == category_id.lower():
                ticket_category = cat
                break
    if ticket_category is None:
        ticket_category = next((cat for cat in guild.categories if "ticket" in cat.name.lower()), None)
    if ticket_category is None:
        ticket_category = await guild.create_category("🎫 Tickets")

    # Save the next number before creating the channel. Closed/deleted tickets
    # never reduce this counter, so the sequence remains 001, 002, 003...
    async with _ticket_number_lock:
        data = load_json(DATA_FILE, {"total": 0, "open": 0, "closed": 0})
        ticket_number = await next_ticket_number(guild)
        data["total"] = ticket_number
        data["open"] = int(data.get("open", 0) or 0) + 1
        data["closed"] = int(data.get("closed", 0) or 0)
        save_json(DATA_FILE, data)

    channel_name = f"ticket-{ticket_number:03d}"
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
    }
    if guild.me:
        overwrites[guild.me] = discord.PermissionOverwrite(
            view_channel=True, send_messages=True, read_message_history=True,
            manage_channels=True, manage_messages=True, embed_links=True, attach_files=True
        )
    overwrites[interaction.user] = discord.PermissionOverwrite(
        view_channel=(category.lower() != "support"),
        send_messages=(category.lower() != "support"),
        read_message_history=True
    )
    support_role_id = str(config.get("support_role", ""))
    if support_role_id.isdigit():
        role = guild.get_role(int(support_role_id))
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    if ADMIN_ROLE_ID:
        role = guild.get_role(ADMIN_ROLE_ID)
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    try:
        channel = await ticket_category.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            topic=(
                f"Ticket #{ticket_number} | Created by ID: {interaction.user.id} | "
                f"Category: {category}"
                + (" | Support approval: pending" if category.lower() == "support" else "")
            ),
        )
    except Exception as exc:
        # Do not reuse a number even if Discord fails to create the channel.
        data = load_json(DATA_FILE, {"total": ticket_number, "open": 0, "closed": 0})
        data["open"] = max(0, int(data.get("open", 0) or 0) - 1)
        save_json(DATA_FILE, data)
        await interaction.followup.send(f"❌ فشل إنشاء التذكرة: {exc}", ephemeral=True)
        return

    logs = load_json(LOGS_FILE, [])
    logs.append({"time": datetime.now().strftime("%H:%M:%S"), "event": "🎫 TICKET", "message": f"{interaction.user} created {category} ticket #{ticket_number} ({channel_name})"})
    save_json(LOGS_FILE, logs)

    if category.lower() == "support":
        ticket_description = (
            "🛟 تم استلام طلب الدعم. الإدارة ستراجعه الآن وتقرر القبول أو الرفض.\n\n"
            "🛟 Support request received. Staff will review it and decide whether to accept or reject it."
        )
    else:
        ticket_description = config.get("ticket_message", "Welcome to your ticket! Support will be with you shortly.")

    embed = discord.Embed(
        title=f"🎫 {category} Ticket — #{ticket_number:03d}",
        description=ticket_description,
        color=discord.Color.blue(), timestamp=datetime.now()
    )
    embed.add_field(name="👤 Created By", value=interaction.user.mention, inline=True)
    embed.add_field(name="📂 Category", value=category, inline=True)
    embed.add_field(name="🔢 Ticket Number", value=f"#{ticket_number:03d}", inline=True)
    embed.set_footer(text="𝙀𝙈𝙋𝙄𝙍𝙀")
    admin_role = guild.get_role(ADMIN_ROLE_ID) if ADMIN_ROLE_ID else None
    mentions = f"{admin_role.mention if admin_role else ''}".strip()
    await channel.send(mentions, embed=embed, view=SupportTicketView() if category.lower() == "support" else TicketView())
    await interaction.followup.send(f"✅ تم إنشاء تذكرتك رقم **#{ticket_number:03d}**: {channel.mention}", ephemeral=True)

class TicketCreateButton(Button):
    def __init__(self, label: str, category: str, emoji: str, style=discord.ButtonStyle.primary):
        super().__init__(label=label, emoji=emoji, style=style, custom_id=f"hertz_ticket_create:{category.lower()}")
        self.category = category

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("❌ فتح التكتات متاح داخل السيرفر فقط.", ephemeral=True)
            return
        async with _work_request_lock:
            duplicate_message = active_ticket_message(interaction.guild, interaction.user.id)
        if duplicate_message:
            await interaction.response.send_message("⏳ " + duplicate_message, ephemeral=True)
            return

        if self.category.lower() == "work":
            if interaction.guild is None:
                await interaction.response.send_message("❌ الفورم متاح داخل السيرفر فقط.", ephemeral=True)
                return
            async with _work_request_lock:
                data = load_work_requests()
                existing_id, existing, _ = active_work_request_for_user(interaction.guild, interaction.user.id, data)
                if existing:
                    if existing.get("status") == "ACCEPTED":
                        channel = interaction.guild.get_channel(int(existing.get("ticket_channel_id", 0) or 0))
                        message = f"عندك تكت WORK مفتوحة بالفعل: {channel.mention}" if channel else "عندك تكت WORK مفتوحة بالفعل."
                    else:
                        message = f"عندك طلب WORK قيد المراجعة بالفعل (رقم الطلب: `{existing_id}`)."
                    await interaction.response.send_message("⏳ " + message, ephemeral=True)
                    return
            await interaction.response.send_modal(WorkRequestModal())
            return
        if self.category.lower() == "support":
            if interaction.guild is None:
                await interaction.response.send_message("❌ الفورم متاح داخل السيرفر فقط.", ephemeral=True)
                return
            async with _work_request_lock:
                data = load_work_requests()
                existing_id, existing, _ = active_work_request_for_user(interaction.guild, interaction.user.id, data, category="Support")
                if existing:
                    if existing.get("status") == "ACCEPTED":
                        channel = interaction.guild.get_channel(int(existing.get("ticket_channel_id", 0) or 0))
                        msg = f"عندك تكت SUPPORT مفتوحة بالفعل: {channel.mention}" if channel else "عندك تكت SUPPORT مفتوحة بالفعل."
                    else:
                        msg = f"عندك طلب SUPPORT قيد المراجعة بالفعل (رقم الطلب: `{existing_id}`)."
                    await interaction.response.send_message("⏳ " + msg, ephemeral=True)
                    return
            await interaction.response.send_modal(SupportRequestModal())
            return
        if self.category.lower() == "shop":
            await interaction.response.send_modal(ShopRequestModal())
            return
        await create_ticket(interaction, self.category)

async def mark_work_ticket_closed(channel):
    topic = getattr(channel, "topic", "") or ""
    if "Application request ID:" not in topic and not any(
        f"Category: {name}" in topic for name in ("Work", "Support")
    ):
        return
    async with _work_request_lock:
        data = load_work_requests()
        changed = False
        for item in data["requests"].values():
            if int(item.get("ticket_channel_id", 0) or 0) == getattr(channel, "id", 0) and item.get("status") == "ACCEPTED":
                item["status"] = "CLOSED"
                item["closed_at"] = datetime.now().isoformat(timespec="seconds")
                changed = True
        if changed:
            save_work_requests(data)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="krishux_ticket_close")
    async def close_button(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("❌ القناة غير صالحة.", ephemeral=True)
            return

        is_admin = bool(interaction.user.guild_permissions.administrator)
        if ADMIN_ROLE_ID:
            role = interaction.guild.get_role(ADMIN_ROLE_ID)
            is_admin = is_admin or bool(role and role in interaction.user.roles)

        topic = channel.topic or ""
        owner_match = re.search(r"Created by ID: (\d+)", topic)
        is_owner = bool(owner_match and int(owner_match.group(1)) == interaction.user.id)
        if not is_owner and interaction.message and interaction.message.embeds:
            for field in interaction.message.embeds[0].fields:
                if field.name in ("👤 Created By", "👤 صاحب الطلب", "👤 مقدم الطلب") and interaction.user.mention in field.value:
                    is_owner = True
                    break

        if not (is_admin or is_owner):
            await interaction.response.send_message("❌ الإغلاق متاح لصاحب التكت والأدمن فقط.", ephemeral=True)
            return

        data = load_json(DATA_FILE, {"total": 0, "open": 0, "closed": 0})
        data["open"] = max(0, int(data.get("open", 0) or 0) - 1)
        data["closed"] = int(data.get("closed", 0) or 0) + 1
        save_json(DATA_FILE, data)
        logs = load_json(LOGS_FILE, [])
        logs.append({"time": datetime.now().strftime("%H:%M:%S"), "event": "🔒 CLOSE", "message": f"{interaction.user.name} closed ticket {channel.name}"})
        save_json(LOGS_FILE, logs)

        await interaction.response.send_message("🔒 جاري إغلاق التكت...", ephemeral=True)
        try:
            await channel.delete(reason=f"Ticket closed by {interaction.user.name}")
            await mark_work_ticket_closed(channel)
        except discord.HTTPException:
            pass

class SupportTicketView(TicketView):
    """Ticket controls with the approval button shown only for Support tickets."""
    @discord.ui.button(label="Accept Support", style=discord.ButtonStyle.primary, emoji="✅", custom_id="empire_ticket_support_accept")
    async def accept_support_button(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        topic = channel.topic or ""
        if "Category: Support" not in topic:
            await interaction.response.send_message("❌ زر القبول مخصص لتذاكر Support فقط.", ephemeral=True)
            return

        # Only administrators/support staff may accept a support ticket.
        config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        support_role_id = str(config.get("support_role", ""))
        has_permission = bool(interaction.guild and interaction.user.guild_permissions.administrator)
        if interaction.guild and ADMIN_ROLE_ID:
            role = interaction.guild.get_role(ADMIN_ROLE_ID)
            if role and role in getattr(interaction.user, "roles", []):
                has_permission = True
        if interaction.guild and not has_permission and support_role_id.isdigit():
            role = interaction.guild.get_role(int(support_role_id))
            if role and role in getattr(interaction.user, "roles", []):
                has_permission = True
        if not has_permission:
            await interaction.response.send_message("❌ القبول متاح للإدارة وفريق الدعم فقط.", ephemeral=True)
            return

        if "Support approval: pending" in topic:
            await interaction.response.send_message("⏳ العضو لازم يرسل اسمه ومشكلته أولاً قبل قبول التذكرة.", ephemeral=True)
            return
        if "Support approval: accepted" in topic:
            await interaction.response.send_message("ℹ️ تم قبول تذكرة الدعم دي بالفعل.", ephemeral=True)
            return
        if "Support approval: submitted" not in topic:
            await interaction.response.send_message("❌ حالة التذكرة غير معروفة. راجع بيانات القناة.", ephemeral=True)
            return

        match = re.search(r"Created by ID: (\d+)", topic)
        if not match:
            await interaction.response.send_message("❌ مش قادر أحدد صاحب التذكرة من بيانات القناة.", ephemeral=True)
            return
        creator = interaction.guild.get_member(int(match.group(1)))
        if creator is None:
            try:
                creator = await interaction.guild.fetch_member(int(match.group(1)))
            except discord.HTTPException:
                creator = None
        if creator is None:
            await interaction.response.send_message("❌ صاحب التذكرة مش موجود في السيرفر حالياً.", ephemeral=True)
            return

        try:
            await channel.set_permissions(
                creator, view_channel=True, read_message_history=True, send_messages=True,
                attach_files=True, embed_links=True
            )
            await channel.edit(topic=topic.replace("Support approval: submitted", "Support approval: accepted"))
        except discord.HTTPException as exc:
            await interaction.response.send_message(f"❌ مقدرتش أفتح المحادثة: {exc}", ephemeral=True)
            return

        logs = load_json(LOGS_FILE, [])
        logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": "✅ SUPPORT ACCEPTED",
            "message": f"{interaction.user} accepted support ticket {channel.name}"
        })
        save_json(LOGS_FILE, logs)
        await interaction.response.send_message(
            f"✅ تم قبول التذكرة بواسطة {interaction.user.mention}. المحادثة مفتوحة الآن، {creator.mention} تقدر ترد على فريق الدعم.",
            allowed_mentions=discord.AllowedMentions(users=True)
        )

    @discord.ui.button(label="Reject Support", style=discord.ButtonStyle.danger, emoji="❌", custom_id="empire_ticket_support_reject")
    async def reject_support_button(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        topic = getattr(channel, "topic", "") or ""
        if "Category: Support" not in topic:
            await interaction.response.send_message("❌ زر الرفض مخصص لتذاكر Support فقط.", ephemeral=True)
            return

        config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        support_role_id = str(config.get("support_role", ""))
        has_permission = bool(interaction.guild and interaction.user.guild_permissions.administrator)
        if interaction.guild and ADMIN_ROLE_ID:
            role = interaction.guild.get_role(ADMIN_ROLE_ID)
            if role and role in getattr(interaction.user, "roles", []):
                has_permission = True
        if interaction.guild and not has_permission and support_role_id.isdigit():
            role = interaction.guild.get_role(int(support_role_id))
            if role and role in getattr(interaction.user, "roles", []):
                has_permission = True
        if not has_permission:
            await interaction.response.send_message("❌ الرفض متاح للإدارة وفريق الدعم فقط.", ephemeral=True)
            return

        if "Support approval: accepted" in topic:
            await interaction.response.send_message("❌ التذكرة اتقبلت بالفعل؛ لا يمكن رفضها بعد القبول.", ephemeral=True)
            return
        match = re.search(r"Created by ID: (\d+)", topic)
        creator = None
        if match and interaction.guild:
            creator = interaction.guild.get_member(int(match.group(1)))
            if creator is None:
                try:
                    creator = await interaction.guild.fetch_member(int(match.group(1)))
                except discord.HTTPException:
                    creator = None

        await interaction.response.send_message("❌ تم رفض طلب الدعم، وسيتم إغلاق التذكرة.", ephemeral=True)
        if creator:
            try:
                await creator.send(f"❌ تم رفض طلب الدعم الخاص بك في السيرفر **{interaction.guild.name}** من الإدارة.")
            except discord.HTTPException:
                pass
        logs = load_json(LOGS_FILE, [])
        logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": "❌ SUPPORT REJECTED",
            "message": f"{interaction.user} rejected support ticket {channel.name}"
        })
        save_json(LOGS_FILE, logs)
        try:
            await channel.delete(reason=f"Support ticket rejected by {interaction.user}")
            await mark_work_ticket_closed(channel)
        except discord.HTTPException:
            pass


class TicketPanelView(View):
    """Three persistent buttons displayed directly underneath the support panel."""
    def __init__(self, categories=None):
        super().__init__(timeout=None)
        self.add_item(TicketCreateButton("Support", "Support", "<:support:1514388149466435604>", discord.ButtonStyle.success))
        self.add_item(TicketCreateButton("Work", "Work", "<:work:1514387049778643037>", discord.ButtonStyle.success))
        self.add_item(TicketCreateButton("Shop", "Shop", "<:shop:1514386602858778696>", discord.ButtonStyle.success))

# =========================================================
# DISCORD BOT
# =========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=["!", "krishu "], intents=intents, help_command=None)

class TicketBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        self.data = load_json(DATA_FILE, {"total": 0, "open": 0, "closed": 0})
        self.logs = load_json(LOGS_FILE, [])
        self._panel_publish_lock = asyncio.Lock()
        self.auto_save_task.start()
    
    def save_data(self):
        save_json(DATA_FILE, self.data)
        save_json(LOGS_FILE, self.logs)
    
    def add_log(self, event: str, message: str):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": event,
            "message": message
        })
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        save_json(LOGS_FILE, self.logs)
    
    @tasks.loop(minutes=5)
    async def auto_save_task(self):
        self.save_data()
    
    async def publish_panel(self):
        """Create the panel once, then update the same message and remove duplicates."""
        async with self._panel_publish_lock:
            channel = self.bot.get_channel(TICKET_PANEL_CHANNEL_ID)
            if channel is None:
                channel = await self.bot.fetch_channel(TICKET_PANEL_CHANNEL_ID)
            if not isinstance(channel, discord.TextChannel):
                raise RuntimeError(f"Panel ID {TICKET_PANEL_CHANNEL_ID} is not a text channel")
            if self.bot.user is None:
                raise RuntimeError("Bot user is not ready yet")

            config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
            config["categories"] = ["Support", "Work"]

            embed = discord.Embed(
                title=TICKET_PANEL_EMBED_TITLE,
                description=(
                    "🇪🇬 **[ AR ]**\n"
                    "📩 **مركز الدعم الفني والمساعدة**\n\n"
                    "أهلاً بيك! اختار القسم المناسب من الأزرار تحت.\n\n"
                    "📌 **قبل ما تفتح تذكرة:**\n"
                    "• اختار Support للمساعدة الفنية أو Work لطلبات العمل.\n"
                    "• اشرح طلبك بوضوح عشان نقدر نساعدك بسرعة.\n"
                    "• ممنوع فتح طلب أو تذكرة مكررة؛ الطلبات النشطة المكررة هتترفض تلقائيًا.\n"
                    "• طلبات Support وWork بتروح للمراجعة، والتذكرة بتتفتح بعد موافقة الإدارة.\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n\n"
                    "🇺🇸 **[ EN ]**\n"
                    "📩 **Support & Help Center**\n\n"
                    "Choose Support for technical help or Work for work-related requests.\n"
                    "Duplicate active requests are blocked automatically. Requests are reviewed by staff before a ticket is opened.\n\n"
                    "👇 **اختار القسم | Choose a section below**"
                ),
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_image(url="https://raw.githubusercontent.com/hertz100k/hertz/main/ola.gif")
            embed.set_footer(text="𝙀𝙈𝙋𝙄𝙍𝙀 • One official panel")
            view = TicketPanelView(["Support", "Work"])

            # First try the saved message ID; if it no longer exists, search recent history.
            panel_message = None
            saved_id = config.get("panel_message_id")
            if str(saved_id or "").isdigit():
                try:
                    candidate = await channel.fetch_message(int(saved_id))
                    if candidate.author.id == self.bot.user.id:
                        panel_message = candidate
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    panel_message = None

            matches = []
            try:
                # Scan the complete dedicated panel channel so old copies beyond the
                # last 500 messages are cleaned too.
                async for old_message in channel.history(limit=None, oldest_first=True):
                    if old_message.author.id != self.bot.user.id:
                        continue
                    is_panel = any(
                        (item.title or "") == TICKET_PANEL_EMBED_TITLE
                        for item in old_message.embeds
                    )
                    if is_panel:
                        matches.append(old_message)
            except (discord.Forbidden, discord.HTTPException) as exc:
                raise RuntimeError(
                    "البوت محتاج صلاحية View Channel وRead Message History وManage Messages "
                    "في قناة اللوحة عشان ينظف النسخ المكررة بأمان."
                ) from exc

            if panel_message is None and matches:
                panel_message = matches[0]

            if panel_message is not None:
                # Keep the requested text visible outside the embed, but disallow
                # notifications on edits/restarts so publishing/cleaning never pings twice.
                panel_message = await panel_message.edit(
                    content=TICKET_PANEL_PING_CONTENT,
                    embed=embed,
                    view=view,
                    allowed_mentions=discord.AllowedMentions.none()
                )
            else:
                # Only a genuinely new canonical panel sends @everyone/@here.
                # The command and on_ready share publish_panel(), so they cannot create
                # parallel panels; every later run edits the saved/canonical message.
                panel_message = await channel.send(
                    content=TICKET_PANEL_PING_CONTENT,
                    embed=embed,
                    view=view,
                    allowed_mentions=discord.AllowedMentions(everyone=True, users=False, roles=False)
                )

            # Remove every other copy we found, keeping the one canonical panel.
            for duplicate in matches:
                if duplicate.id != panel_message.id:
                    try:
                        await duplicate.delete()
                    except (discord.Forbidden, discord.HTTPException):
                        pass

            config["panel_message_id"] = panel_message.id
            save_json(CONFIG_FILE, config)
            return panel_message

    @commands.command(
        name="ticket_panel",
        aliases=["ticketpanel", "ticket_panel_clean", "ticket_clean", "clean_panel"],
    )
    @commands.has_permissions(administrator=True)
    async def create_panel(self, ctx):
        """Create/update the single canonical ticket panel and remove duplicate copies."""
        try:
            message = await self.publish_panel()
            await ctx.send(f"✅ Ticket panel posted in <#{TICKET_PANEL_CHANNEL_ID}>. Message ID: `{message.id}`", delete_after=8)
        except Exception as e:
            await ctx.send(f"❌ Could not post the panel: {e}", delete_after=10)
    
    @commands.command(name="ticket_stats")
    async def ticket_stats(self, ctx):
        """Show ticket statistics"""
        data = load_json(DATA_FILE, {"total": 0, "open": 0, "closed": 0})
        
        embed = discord.Embed(
            title="📊 Ticket Statistics",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📝 Total Tickets", value=str(data.get("total", 0)), inline=True)
        embed.add_field(name="🟢 Open Tickets", value=str(data.get("open", 0)), inline=True)
        embed.add_field(name="🔴 Closed Tickets", value=str(data.get("closed", 0)), inline=True)
        embed.set_footer(text="𝙀𝙈𝙋𝙄𝙍𝙀")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ticket_help")
    async def ticket_help(self, ctx):
        """Show ticket help"""
        embed = discord.Embed(
            title="🎫 𝙀𝙈𝙋𝙄𝙍𝙀",
            description="Complete ticket management system",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📋 Commands",
            value=(
                "`!ticket_panel` - Create ticket panel (Admin)\n"
                "`!ticket_stats` - Show ticket statistics\n"
                "`!ticket_help` - Show this help\n"
                "`!ticket_dashboard` - Get dashboard link"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎫 Ticket Features",
            value=(
                "• Select category to create ticket\n"
                "• Auto channel creation\n"
                "• Claim ticket system\n"
                "• Close ticket system\n"
                "• Delete ticket system\n"
                "• Full logging"
            ),
            inline=False
        )
        
        embed.set_footer(text="𝙀𝙈𝙋𝙄𝙍𝙀")
        await ctx.send(embed=embed)
    
    @commands.command(name="ticket_dashboard")
    @commands.has_permissions(administrator=True)
    async def ticket_dashboard(self, ctx):
        """Get dashboard link"""
        embed = discord.Embed(
            title="📊 Ticket Bot Dashboard",
            description=f"Access the dashboard at: http://localhost:{DASHBOARD_PORT}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="💡 Tip", value="Use the dashboard to manage categories and settings.", inline=False)
        embed.set_footer(text="𝙀𝙈𝙋𝙄𝙍𝙀")
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle support image uploads in DM; keep the legacy pending-ticket listener for older tickets."""
        if message.author.bot:
            return

        # Discord modals cannot provide a native local-file picker, so collect up to 20 images in DM.
        # The member sends images in one or more messages, then sends "تم" to submit the application.
        if message.guild is None:
            pending = _pending_support_uploads.get(message.author.id)
            if not pending:
                return

            command_text = message.content.strip().lower()
            if command_text in {"إلغاء", "الغاء", "cancel"}:
                _pending_support_uploads.pop(message.author.id, None)
                await message.channel.send("تم إلغاء طلب الدعم. تقدر تبدأ من جديد من لوحة التكتات.")
                return

            if message.attachments:
                # Attach optional images to the already-created Support review request.
                guild = self.bot.get_guild(int(pending.get("guild_id", 0)))
                request = None
                request_id = None
                if guild:
                    data = load_work_requests()
                    for candidate_id, candidate in data["requests"].items():
                        if (int(candidate.get("guild_id", 0) or 0) == guild.id
                                and int(candidate.get("user_id", 0) or 0) == message.author.id
                                and candidate.get("category") == "Support"
                                and candidate.get("status") == "PENDING"):
                            request_id, request = candidate_id, candidate
                            break
                current_images = pending.setdefault("images", [])
                accepted = 0
                for attachment in message.attachments:
                    is_image = (
                        (attachment.content_type or "").lower().startswith("image/")
                        or attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))
                    )
                    if not is_image:
                        continue
                    if len(current_images) >= 20:
                        break
                    if not any(existing.get("url") == attachment.url for existing in current_images):
                        current_images.append({"url": attachment.url, "filename": attachment.filename})
                        accepted += 1
                if request is not None and accepted:
                    request_images = request.setdefault("images", [])
                    for image in current_images:
                        if image not in request_images and len(request_images) < 20:
                            request_images.append(image)
                    request["image_url"] = request_images[0]["url"] if request_images else ""
                    data["requests"][request_id] = request
                    save_work_requests(data)
                    try:
                        review_channel = await get_work_review_channel(guild)
                        review_message = await review_channel.fetch_message(int(request.get("review_message_id", 0)))
                        updated = discord.Embed.from_dict(review_message.embeds[0].to_dict()) if review_message.embeds else discord.Embed(title="Support request")
                        updated.set_image(url=request_images[0]["url"])
                        await review_message.edit(embed=updated)
                        for image in request_images[1:]:
                            await review_channel.send(content=f"🖼️ صورة إضافية لطلب Support `{request_id}`: {image['url']}")
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException, ValueError):
                        pass
                count = len(current_images)
                if count >= 20:
                    await message.channel.send("✅ وصلت لـ20 صورة (الحد الأقصى). ابعت `تم` لوحدها لإرسال الطلب للإدارة، أو `إلغاء` للإلغاء.")
                elif accepted:
                    await message.channel.send(f"✅ استلمت {accepted} صورة. الإجمالي دلوقتي {count}/20. ابعت صور إضافية لو محتاج، وبعد ما تخلص ابعت `تم` لوحدها.")
                else:
                    await message.channel.send("⚠️ المرفقات اللي وصلت مش صور مدعومة. ابعت PNG أو JPG أو WEBP أو GIF، والحد الأقصى 20 صورة.")
                return

            if command_text not in {"تم", "done", "submit", "إرسال", "ارسل"}:
                await message.channel.send("📎 ابعت الصور كمرفقات من زر +، وبعد ما تخلص ابعت `تم` لوحدها. تقدر تبعت لحد 20 صورة، أو `إلغاء` لإلغاء الطلب.")
                return

            images = pending.get("images", [])
            if not images:
                await message.channel.send("⚠️ لازم تبعت صورة واحدة على الأقل قبل ما تكتب `تم`.")
                return

            guild = self.bot.get_guild(int(pending["guild_id"]))
            if guild is None:
                _pending_support_uploads.pop(message.author.id, None)
                await message.channel.send("❌ مش قادر أوصل للسيرفر. جرّب تقديم الطلب مرة تانية.")
                return
            review_channel = await get_work_review_channel(guild)
            if review_channel is None:
                await message.channel.send("❌ قناة مراجعة الإدارة مش مضبوطة. بلّغ الإدارة لإصلاح إعداداتها.")
                return
            if not await ensure_private_review_channel(guild, review_channel):
                await message.channel.send("❌ مقدرتش أخفي قناة المراجعة تلقائيًا. الإدارة لازم تضبط ADMIN_ROLE_ID وتدي البوت صلاحية Manage Channels.")
                return

            async with _work_request_lock:
                # Check existing requests without counting this in-progress DM upload as a duplicate.
                kind, active_value = find_user_active_ticket_or_request(guild, message.author.id)
                if kind:
                    _pending_support_uploads.pop(message.author.id, None)
                    await message.channel.send("⏳ عندك بالفعل طلب قيد المراجعة أو تكت مفتوحة. لازم تنتظر قرار الإدارة أو تقفل التكت الحالية الأول.")
                    return

                request_id = uuid.uuid4().hex[:12]
                item = {
                    "request_id": request_id, "guild_id": guild.id, "user_id": message.author.id,
                    "category": "Support", "username": str(message.author),
                    "name": pending["name"], "age": int(pending["age"]),
                    "problem": str(pending["problem"])[:500], "images": images[:20],
                    "image_url": images[0]["url"], "status": "PENDING",
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "review_channel_id": review_channel.id, "review_message_id": None,
                }
                data = load_work_requests()
                data["requests"][request_id] = item
                if not save_work_requests(data):
                    await message.channel.send("❌ تعذر حفظ الطلب. حاول مرة أخرى لاحقًا.")
                    return

                embed = discord.Embed(title="🛟 طلب SUPPORT جديد", color=discord.Color.orange(), timestamp=datetime.now())
                embed.add_field(name="مقدم الطلب", value=f"<@{message.author.id}> (`{message.author.id}`)", inline=False)
                embed.add_field(name="الاسم", value=discord.utils.escape_markdown(item["name"])[:1024], inline=True)
                embed.add_field(name="السن", value=str(item["age"]), inline=True)
                embed.add_field(name="المشكلة", value=item["problem"][:500], inline=False)
                embed.add_field(name="عدد الصور", value=f"{len(images[:20])}/20", inline=True)
                embed.add_field(name="رقم الطلب", value=f"`{request_id}`", inline=True)
                embed.add_field(name="الحالة", value="🟠 في انتظار موافقة الإدارة", inline=False)
                embed.set_image(url=images[0]["url"])
                embed.set_footer(text="𝙀𝙈𝙋𝙄𝙍𝙀 • SUPPORT Review")
                try:
                    review_message = await review_channel.send(
                        embed=embed, view=WorkReviewView(request_id, prefix="application"),
                        allowed_mentions=discord.AllowedMentions.none()
                    )
                    # Send the remaining image previews to the same private review channel.
                    for image_index, image_info in enumerate(images[1:20], start=2):
                        image_embed = discord.Embed(
                            title=f"🖼️ صورة طلب SUPPORT {request_id} ({image_index}/{len(images[:20])})",
                            color=discord.Color.blurple()
                        )
                        image_embed.set_image(url=image_info["url"])
                        await review_channel.send(embed=image_embed)
                except Exception as exc:
                    data = load_work_requests()
                    if request_id in data["requests"]:
                        data["requests"][request_id]["status"] = "FAILED"
                        data["requests"][request_id]["error"] = str(exc)[:300]
                        save_work_requests(data)
                    await message.channel.send("❌ تعذر إرسال الطلب للإدارة. راجع صلاحيات البوت وقناة المراجعة.")
                    print(f"Failed to send support application {request_id}: {exc}")
                    return
                data = load_work_requests()
                if request_id in data["requests"]:
                    data["requests"][request_id]["review_message_id"] = review_message.id
                    save_work_requests(data)
                _pending_support_uploads.pop(message.author.id, None)
            await message.channel.send("✅ استلمنا بياناتك و" + str(len(images[:20])) + " صورة وبعتنا طلبك للإدارة. التكت هتتفتح لصاحبها فقط بعد الموافقة.")
            return

        if not isinstance(message.channel, discord.TextChannel):
            return
        topic = message.channel.topic or ""
        if "Category: Support" not in topic or "Support approval: pending" not in topic:
            return

        match = re.search(r"Created by ID: (\d+)", topic)
        if not match or message.author.id != int(match.group(1)):
            return

        # Mark as submitted first so rapid follow-up messages cannot be treated as additional intake.
        submitted_topic = topic.replace("Support approval: pending", "Support approval: submitted")
        try:
            await message.channel.edit(topic=submitted_topic)
            await message.channel.set_permissions(
                message.author, view_channel=True, read_message_history=True,
                send_messages=False, attach_files=False, embed_links=False
            )
        except discord.HTTPException:
            # If permissions cannot be changed, still notify staff that manual review is needed.
            pass

        submission = discord.Embed(
            title="📨 تم استلام طلب الدعم — في انتظار القبول",
            description=(
                f"تم استلام الرسالة الأولى من {message.author.mention}.\n"
                "الإدارة، راجعوا وصف المشكلة والمرفقات بالأعلى ثم اضغطوا **Accept Support** لفتح المحادثة.\n\n"
                "The user's initial issue message has been submitted. Staff: review it and click **Accept Support** to enable chat."
            ),
            color=discord.Color.orange(), timestamp=datetime.now()
        )
        submission.set_footer(text="𝙀𝙈𝙋𝙄𝙍𝙀 • Support Approval")
        await message.channel.send(embed=submission)

        config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        staff_mentions = []
        if ADMIN_ROLE_ID:
            role = message.guild.get_role(ADMIN_ROLE_ID) if message.guild else None
            if role:
                staff_mentions.append(role.mention)
        support_role_id = str(config.get("support_role", ""))
        if message.guild and support_role_id.isdigit():
            role = message.guild.get_role(int(support_role_id))
            if role and role.mention not in staff_mentions:
                staff_mentions.append(role.mention)
        if staff_mentions:
            await message.channel.send(
                " ".join(staff_mentions) + " — في تذكرة Support جديدة محتاجة مراجعة وقبول.",
                allowed_mentions=discord.AllowedMentions(roles=True)
            )

    @commands.Cog.listener()
    async def on_ready(self):
        self.add_log("🚀 START", "Bot is online and ready!")
        try:
            message = await self.publish_panel()
            print(f"✅ Official ticket panel is ready: channel={TICKET_PANEL_CHANNEL_ID}, message={message.id}")
        except Exception as exc:
            print(f"⚠️ Could not verify/publish ticket panel: {exc}")

# =========================================================
# MAIN BOT
# =========================================================

class KrishuXBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=["!", "krishu "], intents=intents, help_command=None)
        self.initialized = False

    async def setup_hook(self):
        print("🔄 Setting up bot...")

        # Re-register persistent buttons so existing panels/tickets still work after restart.
        self.add_view(TicketPanelView())
        self.add_view(TicketView())
        self.add_view(SupportTicketView())
        # Restore pending WORK review buttons after a bot restart.
        requests_data = load_work_requests()
        changed = False
        for request_id, request in requests_data["requests"].items():
            if request.get("status") == "PROCESSING":
                request["status"] = "PENDING"
                changed = True
            if request.get("status") == "PENDING":
                prefix = "work" if str(request.get("category", "Work")).lower() == "work" else "application"
                self.add_view(WorkReviewView(request_id, prefix=prefix))
        if changed:
            save_work_requests(requests_data)
        
        try:
            await self.add_cog(TicketBot(self))
            print("✅ TicketBot cog loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load cog: {e}")
            traceback.print_exc()
        
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
        
        self.initialized = True
        self.update_activity_task.start()
        print("✅ Bot setup complete!")

    async def on_ready(self):
        global bot_name
        if not self.initialized:
            return
        
        server_count = len(self.guilds)
        bot_name = f"{self.user.name}"
        
        print("\n" + "="*60)
        print(f"🎫 𝙀𝙈𝙋𝙄𝙍𝙀")
        print("="*60)
        print(f"✅ Bot: {bot_name}")
        print(f"📊 Servers: {server_count}")
        print(f"📝 Commands: {len(self.tree.get_commands())}")
        print(f"🌐 Dashboard: http://localhost:{DASHBOARD_PORT}")
        print("="*60)
        
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{server_count} servers | !ticket_help"
        )
        await self.change_presence(activity=activity)

    @tasks.loop(minutes=5)
    async def update_activity_task(self):
        try:
            if self.initialized:
                server_count = len(self.guilds)
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{server_count} servers | !ticket_help"
                )
                await self.change_presence(activity=activity)
        except Exception as e:
            print(f"⚠️ Activity update error: {e}")

    @update_activity_task.before_loop
    async def before_update_activity_task(self):
        await self.wait_until_ready()

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    try:
        # Start Flask in background
        def run_flask():
            app.run(host='0.0.0.0', port=DASHBOARD_PORT, debug=False, use_reloader=False)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        print(f"🚀 Dashboard started on http://localhost:{DASHBOARD_PORT}")
        
        # Run bot
        bot = KrishuXBot()
        bot.run(TOKEN)
        
    except discord.errors.LoginFailure:
        print("❌ Invalid Discord token")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
