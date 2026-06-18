"""
🏢 facilityXperience v3.0 — Enterprise Intelligent Facility Ecosystem
Churchgate Group | World-Class Facility Management Platform
SmartCheck Killer — AI-Powered Enterprise Grade
"""

import streamlit as st
from datetime import datetime, date, time, timedelta
import pandas as pd
import base64
from pathlib import Path
import os
import hashlib
import secrets
import json
import re
from dotenv import load_dotenv
from supabase import create_client
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

load_dotenv()

# ============================================
# SUPABASE
# ============================================
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Database configuration missing. Please set SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets or environment variables.")
    st.stop()

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Clear cache on startup
if "cache_cleared" not in st.session_state:
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.cache_cleared = True

supabase = init_supabase()

# ============================================
# BRAND
# ============================================
CHURCHGATE_RED = "#CC0000"
CHURCHGATE_DARK = "#1a1a1a"
CHURCHGATE_GREY = "#4a4a4a"
CHURCHGATE_LIGHT = "#f5f5f5"
CHURCHGATE_WHITE = "#ffffff"
CHURCHGATE_BG = "#e8e8e8"
CHURCHGATE_SIDEBAR = "#d5d5d5"

FACILITY_INFO = {
    "WTC": {"full_name": "World Trade Center", "city": "Abuja", "logo": "WTC-logo.jpg", "desc": "22-Floor Office Tower • 24-Floor Residential Tower • Recreation Center", "color": CHURCHGATE_RED, "clight": "#fce8e8"},
    "AGVL": {"full_name": "Agroline Ventures Limited", "city": "Abuja", "logo": "churchgate-logo.png", "desc": "Commercial/Retail Complex", "color": "#059669", "clight": "#ECFDF5"},
    "FCPL": {"full_name": "First Continental Properties Limited", "city": "Lagos", "logo": "churchgate-logo.png", "desc": "Commercial/Industrial Tower", "color": "#D97706", "clight": "#FFFBEB"},
    "RBPL": {"full_name": "RB Properties Limited", "city": "Lagos", "logo": "churchgate-logo.png", "desc": "Premium Commercial Plaza", "color": "#BE185D", "clight": "#FDF2F8"},
    "VDL": {"full_name": "Ocean Terrace", "city": "Lagos", "logo": "churchgate-logo.png", "desc": "Commercial/Industrial Centre", "color": "#7C3AED", "clight": "#F5F3FF"},
    "WAREHOUSES": {"full_name": "Warehouse Network", "city": "Lagos", "logo": "churchgate-logo.png", "desc": "Logistics & Storage Network", "color": "#475569", "clight": "#F1F5F9"},
}

st.set_page_config(page_title="facilityXperience | Churchgate Group", page_icon="churchgate-logo.png", layout="wide", initial_sidebar_state="expanded")

# ============================================
# SECURITY HELPERS
# ============================================
def safe_parse_permissions(perms):
    """Safely parse permissions from string or list using json.loads instead of eval"""
    if isinstance(perms, str):
        try:
            return json.loads(perms)
        except:
            return []
    return perms if isinstance(perms, list) else []

def validate_password_strength(password):
    """
    Fortune 500 password policy enforcement
    Returns (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password meets requirements"

def hash_password(password):
    """Hash password with PBKDF2-SHA256 and salt"""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return f"{salt}${pw_hash}"

def check_password(password, stored_hash):
    """Verify password against stored hash (supports both old SHA256 and new PBKDF2)"""
    if not stored_hash:
        return False
    # New format: salt$hash
    if '$' in stored_hash:
        try:
            salt, pw_hash = stored_hash.split('$', 1)
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == pw_hash
        except:
            return False
    # Legacy format: plain SHA256 hex digest
    if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
        return True
    # Legacy format: plain SHA256 digest
    if hashlib.sha256(password.encode()).digest() == stored_hash:
        return True
    return False

def check_login_rate_limit(email):
    """Rate limit login attempts: 5 failures in 15 minutes = locked"""
    try:
        recent_failures = supabase.table("login_attempts").select("*").eq("email", email).eq("success", False).gte("attempt_time", (datetime.now() - timedelta(minutes=15)).isoformat()).execute()
        if recent_failures.data and len(recent_failures.data) >= 5:
            return False, "Account temporarily locked due to multiple failed attempts. Please try again in 30 minutes or reset your password."
        return True, ""
    except:
        return True, ""

def log_login_attempt(email, success):
    """Log login attempt for rate limiting"""
    try:
        supabase.table("login_attempts").insert({
            "email": email,
            "success": success,
            "attempt_time": datetime.now().isoformat()
        }).execute()
    except:
        pass

def get_recent_failures_count(email):
    """Get count of recent failed login attempts"""
    try:
        recent = supabase.table("login_attempts").select("id", count="exact").eq("email", email).eq("success", False).gte("attempt_time", (datetime.now() - timedelta(minutes=15)).isoformat()).execute()
        return 5 - (recent.count or 0)
    except:
        return 5

# ============================================
# CSS
# ============================================
def inject_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        * {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background: {CHURCHGATE_BG}; }}
        .main > div {{ background: {CHURCHGATE_BG}; }}
        #MainMenu, header, footer {{ visibility: hidden; }}
        section[data-testid="stSidebar"] {{ background: #d5d5d5 !important; border-right:2px solid #CC0000 !important; }}
        section[data-testid="stSidebar"] * {{ color: #1a1a1a !important; font-size: 0.7rem !important; }}
        section[data-testid="stSidebar"] .stButton > button {{ background: #c0c0c0 !important; color: #1a1a1a !important; border: 1px solid #a0a0a0 !important; margin-bottom: 2px !important; }}
        section[data-testid="stSidebar"] button[kind="primary"] {{ background: #CC0000 !important; color: white !important; }}
        section[data-testid="stSidebar"] p {{ color: #333 !important; font-weight: 600 !important; }}
        
        [data-testid="collapsedControl"] {{
            position: fixed !important;
            top: 80px !important;
            left: 310px !important;
            z-index: 99999 !important;
            background: #CC0000 !important;
            border-radius: 0 8px 8px 0 !important;
            padding: 8px 5px !important;
            box-shadow: 0 2px 10px rgba(204,0,0,0.4) !important;
            cursor: pointer !important;
            width: 28px !important;
            height: 50px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            opacity: 1 !important;
            visibility: visible !important;
        }}
        [data-testid="collapsedControl"]:hover {{
            background: #aa0000 !important;
        }}
        [data-testid="collapsedControl"] svg {{
            fill: white !important;
            width: 16px !important;
            height: 16px !important;
        }}
        section[data-testid="stSidebar"] .stButton > button {{ background:#c0c0c0 !important; border:1px solid #a0a0a0 !important; border-radius:6px !important; font-size:0.7rem !important; padding:0.35rem 0.5rem !important; }}
        section[data-testid="stSidebar"] button[kind="primary"] {{ background:{CHURCHGATE_RED} !important; color:white !important; }}
        [data-testid="collapsedControl"] {{ position:fixed !important; top:80px !important; left:0 !important; z-index:99999 !important; background:#CC0000 !important; border-radius:0 8px 8px 0 !important; padding:8px 5px !important; box-shadow:0 2px 10px rgba(204,0,0,0.4) !important; cursor:pointer !important; width:28px !important; height:50px !important; display:flex !important; align-items:center !important; justify-content:center !important; opacity:1 !important; visibility:visible !important; }}
        [data-testid="collapsedControl"]:hover {{ background:#aa0000 !important; box-shadow:0 4px 20px rgba(204,0,0,0.6) !important; }}
        [data-testid="collapsedControl"] svg {{ fill:white !important; width:16px !important; height:16px !important; }}
        [data-testid="collapsedControl"] {{ display: none !important; }}
        button[kind="header"] {{ display: none !important; }}
        [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
        .st-emotion-cache-1rtdyqp {{ display: none !important; }}
        .fx-topnav {{ background:linear-gradient(105deg,{CHURCHGATE_DARK},#2a2a2a,{CHURCHGATE_DARK}); padding:0.5rem 1.5rem; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:9998; border-bottom:2px solid {CHURCHGATE_RED}; }}
        .fx-brand {{ font-size:1.05rem; font-weight:700; color:white; }} .fx-brand span {{ color:{CHURCHGATE_RED}; font-weight:800; }}
        .churchgate-header {{ background:white; padding:1.5rem; border-radius:8px; margin-bottom:1rem; border-left:4px solid {CHURCHGATE_RED}; box-shadow:0 1px 3px rgba(0,0,0,0.06); }}
        .fx-card {{ background:white; border-radius:8px; padding:1rem; border:1px solid #ccc; box-shadow:0 1px 3px rgba(0,0,0,0.06); text-align:center; }}
        .fx-card-label {{ font-size:0.6rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; color:{CHURCHGATE_GREY}; margin-bottom:0.3rem; }}
        .fx-card-value {{ font-size:1.6rem; font-weight:800; color:{CHURCHGATE_DARK}; line-height:1; }}
        .stButton > button {{ background:#6B7280 !important; color:white !important; border:none !important; border-radius:6px !important; font-weight:500 !important; }}
        .stButton > button:hover {{ background:#4B5563 !important; }}
        .fx-badge {{ display:inline-flex; align-items:center; gap:0.2rem; padding:0.2rem 0.6rem; border-radius:50px; font-size:0.65rem; font-weight:600; }}
        .badge-success {{ background:#ECFDF5; color:#065F46; }} .badge-warning {{ background:#FFFBEB; color:#92400E; }}
        .badge-critical {{ background:#FEF2F2; color:#991B1B; }} .badge-info {{ background:#EFF6FF; color:#1E40AF; }}
        .badge-pending {{ background:#FEF3C7; color:#92400E; }} .badge-approved {{ background:#ECFDF5; color:#065F46; }}
        [data-testid="stDataFrame"] {{ border-radius:8px !important; border:1px solid #ccc !important; font-size:0.7rem !important; }}
        [data-testid="stDataFrame"] th {{ background:{CHURCHGATE_LIGHT} !important; font-weight:600 !important; font-size:0.65rem !important; text-transform:uppercase !important; }}
        [data-testid="stMetric"] {{ background:white; padding:0.8rem !important; border-radius:8px !important; border:1px solid #ccc !important; }}
        hr {{ border-color:#ddd !important; margin:1rem 0 !important; }}
        .stTabs [data-baseweb="tab-list"] {{ gap:0.5rem; }}
        .stTabs [data-baseweb="tab"] {{ background:white; border-radius:6px 6px 0 0; padding:0.5rem 1rem; font-weight:500; }}
        .stTabs [aria-selected="true"] {{ background:{CHURCHGATE_RED} !important; color:white !important; }}
    </style>
    """, unsafe_allow_html=True)

# ============================================
# DATA ENGINE
# ============================================
class DB:
    @staticmethod
    def get_kpis(fc):
        try:
            wo=supabase.table("work_orders").select("id",count="exact").eq("facility_code",fc).eq("status","open").execute()
            vis=supabase.table("visitors").select("id",count="exact").eq("facility_code",fc).eq("visit_date",str(date.today())).execute()
            inc=supabase.table("incidents").select("id",count="exact").eq("facility_code",fc).eq("status","reported").execute()
            tix=supabase.table("tickets").select("id",count="exact").eq("facility_code",fc).in_("status",["open","in_progress"]).execute()
            ast=supabase.table("assets").select("id",count="exact").eq("facility_code",fc).execute()
            ppm=supabase.table("ppm_schedules").select("id",count="exact").eq("facility_code",fc).eq("status","scheduled").execute()
            wp=supabase.table("work_permits").select("id",count="exact").eq("facility_code",fc).eq("status","pending").execute()
            return {"open_wo":wo.count or 0,"visitors":vis.count or 0,"open_inc":inc.count or 0,"open_tix":tix.count or 0,"assets":ast.count or 0,"ppm_due":ppm.count or 0,"pending_permits":wp.count or 0}
        except: return {"open_wo":0,"visitors":0,"open_inc":0,"open_tix":0,"assets":0,"ppm_due":0,"pending_permits":0}

    @staticmethod
    def get_all(table, fc, limit=500):
        try:
            res=supabase.table(table).select("*").eq("facility_code",fc).order("created_at",desc=True).limit(limit).execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def get_assets(fc, limit=50000):
        try:
            all_data = []
            page_size = 1000
            offset = 0
            
            while offset < limit:
                res = supabase.table("assets").select("*").eq("facility_code", fc).range(offset, offset + page_size - 1).execute()
                if res.data and len(res.data) > 0:
                    all_data.extend(res.data)
                    offset += page_size
                    if len(res.data) < page_size:
                        break
                else:
                    break
            
            return all_data if all_data else []
        except Exception as e:
            st.error(f"Asset fetch error: {str(e)[:100]}")
            return []

    @staticmethod
    def get_categories():
        try:
            res=supabase.table("asset_categories").select("*").order("name").execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def insert(table, data):
        try:
            res = supabase.table(table).insert(data).execute()
            if res.data:
                return res.data[0]
            return None
        except Exception as e:
            st.error(f"Insert Error: {str(e)[:200]}")
            return None

    @staticmethod
    def update(table, id_val, data):
        try:
            supabase.table(table).update(data).eq("id",id_val).execute(); return True
        except: return False

    @staticmethod
    def get_users():
        try:
            res=supabase.table("app_users").select("*").order("name").limit(200).execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def get_locations(fc):
        try:
            res=supabase.table("helpdesk_locations").select("*").eq("facility_code",fc).order("location_name").execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def get_sub_locations(loc_id):
        try:
            res=supabase.table("helpdesk_sub_locations").select("*").eq("location_id",loc_id).order("sub_location_name").execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def get_helpdesk_categories():
        try:
            res = supabase.table("helpdesk_categories").select("*").eq("is_active", True).order("category_name").execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def get_tickets_filtered(fc, status=None, category=None, search=None, limit=100):
        try:
            query = supabase.table("tickets").select("*").eq("facility_code", fc)
            if status and status != "All":
                query = query.eq("status", status)
            if category:
                query = query.eq("category", category)
            if search:
                query = query.or_(f"title.ilike.%{search}%,description.ilike.%{search}%")
            res = query.order("created_at", desc=True).limit(limit).execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def get_ticket_comments(ticket_id):
        try:
            res = supabase.table("ticket_comments").select("*").eq("ticket_id", ticket_id).order("created_at").execute()
            return res.data if res.data else []
        except: return []

# ============================================
# HELPERS
# ============================================
def get_facility_logo(fc, h=60):
    info=FACILITY_INFO.get(fc,{})
    lf=info.get("logo","churchgate-logo.png")
    lp=Path(lf)
    if lp.exists():
        ext=lf.split(".")[-1].replace("jpg","jpeg")
        with open(lp,"rb") as f: b64=base64.b64encode(f.read()).decode()
        return f'<img src="data:image/{ext};base64,{b64}" height="{h}px" style="max-width:220px;object-fit:contain;">'
    return f'<span style="font-size:2.5rem;">🏢</span>'


def ask_facility_xpert(query, categories):
    """AI assistant using Groq (FREE, FAST, REAL LLM)"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        cat_list = ", ".join(categories[:10])
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": f"You are facilityXpert, the AI assistant for Churchgate Group's World Trade Center in Abuja, Nigeria. You help tenants and staff resolve facility issues quickly. Available departments: {cat_list}. For emergencies (fire, elevator stuck, major water leak, electrical hazard), ALWAYS tell them to raise an URGENT ticket or call the facility team. NEVER make up phone numbers or email addresses. If you don't know something, say so. Be concise, helpful, and professional. Give step-by-step solutions."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 300,
                "temperature": 0.5
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        
        # Fallback to knowledge base
        kb = supabase.table("knowledge_base").select("*").or_(f"question.ilike.%{query}%,tags.ilike.%{query}%").limit(3).execute()
        if kb.data:
            solutions = "\n\n".join([f"**{k.get('question')}**\n{k.get('answer','')}" for k in kb.data])
            return f"Here are solutions from our knowledge base:\n\n{solutions}"
        return None
    except:
        try:
            kb = supabase.table("knowledge_base").select("*").or_(f"question.ilike.%{query}%,tags.ilike.%{query}%").limit(3).execute()
            if kb.data:
                solutions = "\n\n".join([f"**{k.get('question')}**\n{k.get('answer','')}" for k in kb.data])
                return f"Here are solutions from our knowledge base:\n\n{solutions}"
        except:
            pass
        return None


def get_nav_logo():
    """Churchgate logo for top navigation - white version for dark background"""
    p = Path("churchgate-logo.png")
    if p.exists():
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{b64}" height="28px" style="display:inline-block;vertical-align:middle;">'
    return '<span style="font-weight:800;color:white;font-size:1rem;display:inline-block;vertical-align:middle;">CHURCHGATE</span>'


def check_auto_escalation(fc):
    """Auto-escalate overdue tickets"""
    try:
        tickets = supabase.table("tickets").select("*").eq("facility_code", fc).in_("status", ["open","in_progress","hold"]).execute()
        if not tickets.data:
            return
        
        now = datetime.now()
        
        for ticket in tickets.data:
            current_level = ticket.get("escalation_level", 1)
            if current_level >= 6:
                continue
            
            sla_deadline = ticket.get("sla_deadline")
            if not sla_deadline:
                continue
            
            try:
                sla_dt = pd.to_datetime(sla_deadline)
                if now > sla_dt:
                    next_level = current_level + 1
                    ticket_cat = ticket.get("category")
                    cat_id = None
                    cats = supabase.table("helpdesk_categories").select("id").eq("category_name", ticket_cat).execute()
                    if cats.data:
                        cat_id = cats.data[0]["id"]
                    
                    esc_config = supabase.table("ticket_escalation").select("*").eq("facility_code", fc).eq("level_number", next_level).eq("category_id", cat_id).execute()
                    supabase.table("tickets").update({"escalation_level": next_level}).eq("id", ticket["id"]).execute()
                    if esc_config.data:
                        for e in esc_config.data:
                            if e.get("escalate_to_email"):
                                send_email_notification(
                                    e["escalate_to_email"],
                                    f"🔺 ESCALATED L{current_level}→L{next_level}: Ticket {ticket.get('ticket_number','')}",
                                    f"""
                                    <div style="font-family:Arial;max-width:600px;border:1px solid #ddd;border-radius:8px;overflow:hidden;">
                                        <div style="background:#F59E0B;padding:20px;color:white;">
                                            <h2 style="margin:0;">⚠️ Ticket Escalated — Level {next_level}</h2>
                                            <p style="margin:5px 0 0 0;font-size:12px;">SLA Exceeded — Immediate Action Required</p>
                                        </div>
                                        <div style="padding:20px;">
                                            <table style="width:100%;border-collapse:collapse;font-size:13px;">
                                                <tr><td style="padding:8px;font-weight:bold;">Ticket:</td><td>{ticket.get('ticket_number','')}</td></tr>
                                                <tr><td style="padding:8px;font-weight:bold;">Title:</td><td>{ticket.get('title','')}</td></tr>
                                                <tr><td style="padding:8px;font-weight:bold;">Category:</td><td>{ticket.get('category','')}</td></tr>
                                                <tr><td style="padding:8px;font-weight:bold;">Escalated:</td><td>Level {current_level} → Level {next_level}</td></tr>
                                                <tr><td style="padding:8px;font-weight:bold;">SLA Deadline:</td><td>{ticket.get('sla_deadline','')}</td></tr>
                                            </table>
                                            <div style="margin-top:15px;background:#FFF3CD;padding:15px;border-radius:8px;">
                                                <p style="margin:0;color:#92400E;font-weight:bold;">⚡ Action Required: Please resolve or reassign immediately.</p>
                                            </div>
                                        </div>
                                    </div>
                                    """
                                )
            except:
                pass
    except:
        pass

def safe_text(text, default="N/A"):
    """Remove unicode characters that break PDFs"""
    if not text or str(text) == "None" or str(text) == "nan":
        return default
    replacements = {
        '\u2014': '-', '\u2013': '-', '\u2019': "'", '\u2018': "'",
        '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00a0': ' ',
        '\u2012': '-', '\u2015': '-', '\u2192': '>', '\u2794': '>',
        '\u2022': '*', '\u25cf': '*', '\u25cb': '-', '\u25a0': '-'
    }
    result = str(text)
    for k, v in replacements.items():
        result = result.replace(k, v)
    return result

def get_logo_base64():
    """Convert churchgate-logo.png to base64 for embedding in reports"""
    p = Path("churchgate-logo.png")
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def status_badge(s):
    badges={
        "active":'<span class="fx-badge badge-success">✅ Active</span>',
        "inactive":'<span class="fx-badge badge-critical">❌ Inactive</span>',
        "pending":'<span class="fx-badge badge-pending">⏳ Pending</span>',
        "approved":'<span class="fx-badge badge-approved">✅ Approved</span>',
        "rejected":'<span class="fx-badge badge-critical">❌ Rejected</span>',
        "open":'<span class="fx-badge badge-critical">🔴 Open</span>',
        "in_progress":'<span class="fx-badge badge-warning">🟡 In Progress</span>',
        "completed":'<span class="fx-badge badge-success">🟢 Completed</span>',
        "closed":'<span class="fx-badge badge-info">🔵 Closed</span>',
    }
    return badges.get(s,f'<span class="fx-badge badge-info">{s}</span>')

# ============================================
# TOP NAV
# ============================================
def topnav():
    cg = get_nav_logo()
    
    st.markdown(f"""
    <div class="fx-topnav">
        <div style="display:flex;align-items:center;gap:1rem;">
            <div style="display:flex;align-items:center;gap:0.6rem;">
                {cg}
                <div style="width:1px;height:24px;background:rgba(255,255,255,0.3);"></div>
                <span class="fx-brand">facility<span>X</span>perience</span>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:0.8rem;">
            <div style="display:flex;align-items:center;gap:0.3rem;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);border-radius:50px;padding:0.25rem 0.7rem;font-size:0.6rem;font-weight:600;color:#6EE7B7;">
                <div style="width:5px;height:5px;border-radius:50%;background:#10B981;animation:fxPulse 2s infinite;"></div>AI ACTIVE
            </div>
            <span style="color:rgba(255,255,255,0.5);font-size:0.65rem;font-family:monospace;" id="lt"></span>
            <div style="display:flex;align-items:center;gap:0.5rem;">
    <span style="color:rgba(255,255,255,0.7);font-size:0.7rem;">{st.session_state.get('user_name','User').split()[-1]}</span>
    <div style="width:32px;height:32px;border-radius:50%;background:{CHURCHGATE_RED};display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.75rem;border:2px solid rgba(255,255,255,0.2);cursor:pointer;" title="Click to logout" onclick="logout()">{st.session_state.get('user_name','User')[:2].upper()}</div>
</div>
    </div>
    <script>function t(){{var d=new Date();var wat=new Date(d.getTime()+3600000);document.getElementById('lt').textContent=wat.toLocaleTimeString('en-US',{{hour12:false}});}}t();setInterval(t,1000);</script>
    <style>@keyframes fxPulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}</style>
    """, unsafe_allow_html=True)


# ============================================
# SIDEBAR
# ============================================
def sidebar():
    with st.sidebar:
        user_perms = safe_parse_permissions(st.session_state.get("user", {}).get("extra_permissions", []))
        user_role = st.session_state.get("user_role", "staff")
        is_admin = user_role in ["admin", "approver"]
        user_home_facility = st.session_state.get("user", {}).get("home_facility", "WTC")
        
        sel = st.session_state.get("facility", "WTC")
        
        if is_admin:
            allowed_facilities = list(FACILITY_INFO.keys())
        else:
            allowed_facilities = [user_home_facility]
        
        cols = st.columns(3)
        for i, (k, v) in enumerate(FACILITY_INFO.items()):
            if k in allowed_facilities:
                with cols[i % 3]:
                    if st.button(k, key=f"f_{k}", use_container_width=True, type="primary" if k == sel else "secondary"):
                        st.session_state.facility = k
                        st.rerun()
        
        info = FACILITY_INFO.get(sel, {})
        st.markdown(f'<div style="background:{info.get("clight","#fce8e8")};border-left:3px solid {info.get("color",CHURCHGATE_RED)};border-radius:6px;padding:0.7rem;margin:0.7rem 0;font-size:0.7rem;"><b>{info.get("full_name",sel)}</b><br>📍 {info.get("city","")}</div>',unsafe_allow_html=True)
        
        all_nav = [
            ("🏠 COMMAND", [("🌐 Command Center", "cc"), ("📊 PPM Dashboard", "ppm")], ["Command Center", "PPM Dashboard"]),
            ("🏗️ ASSETS & PPM", [("📋 Asset Register", "ar"), ("🔧 PPM Activities", "ppma"), ("📅 52-Week Calendar", "cal"), ("✅ Checklist Status", "cs")], ["Asset Register", "PPM Activities", "52-Week Calendar", "Checklist Status"]),
            ("🔧 MAINTENANCE", [("📋 Work Orders", "wo"), ("🛡️ Work Permits", "wp")], ["Work Orders", "Raise Permit", "Authorize Permit", "Confirm Permit", "Approve Permit", "Work Permit Reports"]),
            ("🏢 FACILITY OPERATIONS", [("📊 Operations Dashboard", "fo"), ("✅ Observations/Alerts", "oa")], ["Facility Operations"]),
            ("👥 PEOPLE", [("🛂 Visitor Management", "vm"), ("👤 User Management", "up")], ["Visitor Management", "User Management"]),
            ("💬 SERVICES", [("🎫 Raise a Ticket", "rt"), ("💬 Helpdesk", "hd"), ("⭐ Feedback", "fb")], ["Raise Ticket", "Helpdesk", "Feedback"]),
            ("✅ COMPLIANCE", [("✅ Audit Checklist", "ac"), ("🚨 Incident Check", "ic"), ("🔄 HOTO Check", "hot")], ["Audit Checklist", "Incident Report", "HOTO Check"]),
            ("⚡ UTILITY", [("⚡ Utility Dashboard", "uc")], ["Utility Dashboard"]),
            ("📊 REPORTS", [("📊 Monthly MIS", "mis")], ["Monthly MIS"]),
        ]
        
        for section, items, required_perms in all_nav:
            can_see = is_admin or any(p in user_perms for p in required_perms) or len(user_perms) == 0
            if can_see:
                st.markdown(f'<p style="font-size:0.5rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#888;margin:0.5rem 0 0.1rem 0;">{section}</p>',unsafe_allow_html=True)
                for label, page_id in items:
                    if st.button(label, key=page_id, use_container_width=True):
                        st.session_state.page = page_id
                        st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True, type="primary"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.user_name = None
            st.query_params.clear()
            st.rerun()


# ============================================
# COMMAND CENTER
# ============================================
def page_cc():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    k=DB.get_kpis(fc)
    logo=get_facility_logo(fc,70)
    
    st.markdown(f"""
    <div class="churchgate-header">
        <div style="display:flex;align-items:center;gap:1.5rem;">
            <div style="flex-shrink:0;">{logo}</div>
            <div style="flex:1;">
                <h1 style="margin:0;font-weight:800;font-size:1.5rem;color:#1a1a1a;">{info.get("full_name",fc)}</h1>
                <p style="margin:0.2rem 0 0 0;color:#4a4a4a;font-size:0.8rem;">📍 {info.get("city","")} • {info.get("desc","")}</p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.6rem;color:#888;">LIVE DATA</div>
                <div style="font-size:1.1rem;font-weight:700;">{datetime.now().strftime("%H:%M:%S")}</div>
                <div style="font-size:0.6rem;color:#888;">{datetime.now().strftime("%A, %d %B %Y")}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    kpi=[("📋 Open WOs",k["open_wo"]),("🛂 Visitors",k["visitors"]),("🚨 Incidents",k["open_inc"]),("🎫 Tickets",k["open_tix"]),("🏗️ Assets",k["assets"]),("🔧 PPM Due",k["ppm_due"]),("🛡️ Permits",k["pending_permits"])]
    cols=st.columns(7)
    for i,(l,v) in enumerate(kpi):
        with cols[i]:st.markdown(f'<div class="fx-card"><div class="fx-card-label">{l}</div><div class="fx-card-value">{v}</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### 📋 Recent Work Permits")
        wp=DB.get_all("work_permits",fc,5)
        if wp:
            for w in wp:
                s=w.get("status","pending")
                status_colors = {"approved":"#10B981","pending":"#F59E0B","rejected":"#EF4444","submitted":"#3B82F6"}
                sc = status_colors.get(s,"#4a4a4a")
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:0.8rem;margin:0.4rem 0;border-left:4px solid {sc};box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <b>{w.get('permit_number','')}</b>
                        <span style="background:{sc};color:white;padding:2px 10px;border-radius:12px;font-size:0.7rem;font-weight:600;">{s.upper()}</span>
                    </div>
                    <div style="font-size:0.8rem;color:#666;margin-top:0.2rem;">{w.get('title','')[:80]}</div>
                    <div style="font-size:0.65rem;color:#888;">👤 {w.get('raised_by_name','N/A')} | 📅 {w.get('start_datetime','')[:10]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:st.info("No work permits")
    with c2:
        st.markdown("### 🎫 Recent Tickets")
        tix=DB.get_all("tickets",fc,5)
        if tix:
            for t in tix:
                status = t.get("status","open")
                colors = {"open":"#EF4444","in_progress":"#F59E0B","hold":"#3B82F6","closed":"#10B981","rejected":"#6B7280"}
                icons = {"open":"🔴","in_progress":"🟡","hold":"⏸️","closed":"🟢","rejected":"❌"}
                sc = colors.get(status,"#4a4a4a")
                si = icons.get(status,"📋")
                
                created = t.get("created_at","")
                age_str = ""
                if created and str(created) != "None":
                    try:
                        age = datetime.now() - pd.to_datetime(created)
                        age_str = f"{age.days}d {age.seconds//3600}h ago"
                    except: pass
                
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:0.8rem;margin:0.4rem 0;border-left:4px solid {sc};box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span><b>{si} {t.get('ticket_number','')}</b></span>
                        <span style="background:{sc};color:white;padding:2px 10px;border-radius:12px;font-size:0.65rem;font-weight:600;">{status.upper()}</span>
                    </div>
                    <div style="font-size:0.8rem;color:#1a1a1a;margin-top:0.3rem;">{t.get('title','')[:80]}</div>
                    <div style="font-size:0.65rem;color:#888;margin-top:0.2rem;">
                        👤 {t.get('requester_name','N/A')} | 🏷️ {t.get('category','')} | ⏱️ {age_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:st.info("No tickets")

def fix_date(val):
    """Convert DD-MM-YYYY to YYYY-MM-DD, return None if invalid"""
    if val is None or pd.isna(val) or str(val).strip() in ["", "NA", "na", "null", "None"]:
        return None
    val_str = str(val).strip()
    # Already in YYYY-MM-DD format
    if len(val_str) == 10 and val_str[4] == "-":
        return val_str
    # DD-MM-YYYY format
    parts = val_str.replace("/", "-").split("-")
    if len(parts) == 3:
        try:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year < 100:
                year += 2000
            return f"{year:04d}-{month:02d}-{day:02d}"
        except:
            return None
    return None


# ============================================
# ASSET COMMAND CENTER — FORTUNE 500 GRADE
# WORLD-CLASS AI-POWERED ASSET MANAGEMENT
# ============================================
def page_ar():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    
    st.markdown(f'## 🏗️ Asset Command Center — {info.get("full_name", fc)}')
    
    # Fetch all assets
    all_assets = DB.get_assets(fc, 50000)
    
    # Build dataframe
    if all_assets:
        df = pd.DataFrame(all_assets)
        # Get category names
        # Department is already in the assets table from SQL upload
        if "department" in df.columns:
            df["department"] = df["department"].fillna("N/A")
        else:
            df["department"] = "N/A"
    else:
        df = pd.DataFrame()
    
    today = date.today()
    
    # ============================================
    # MAIN NAVIGATION TABS
    # ============================================
    ar_tabs = st.tabs([
        "📊 Dashboard", 
        "📋 Asset Register", 
        "➕ Add Asset", 
        "📦 Bulk Upload",
        "📖 Readings", 
        "📅 PPM Calendar",
        "✅ Approvals",
        "📄 Reports",
        "⚙️ Settings"
    ])
    
    # ============================================
    # TAB 0: DASHBOARD
    # ============================================
    with ar_tabs[0]:
        if len(df) == 0:
            st.info("🏗️ No assets registered yet. Start by adding assets in the '➕ Add Asset' or '📦 Bulk Upload' tabs.")
        else:
            # Calculations
            total_assets = len(df)
            active_count = len(df[df["status"] == "active"]) if "status" in df.columns else 0
            inactive_count = len(df[df["status"] == "inactive"]) if "status" in df.columns else 0
            breakdown_count = len(df[df["status"] == "breakdown"]) if "status" in df.columns else 0
            
            critical_mask = df.get("priority", pd.Series(["low"] * len(df))).isin(["critical", "high"])
            critical_count = critical_mask.sum()
            non_critical_count = total_assets - critical_count
            
            critical_active = len(df[critical_mask & (df["status"] == "active")]) if "status" in df.columns else 0
            critical_breakdown = len(df[critical_mask & (df["status"] == "breakdown")]) if "status" in df.columns else 0
            non_critical_active = len(df[~critical_mask & (df["status"] == "active")]) if "status" in df.columns else 0
            non_critical_breakdown = len(df[~critical_mask & (df["status"] == "breakdown")]) if "status" in df.columns else 0
            
            # Health
            if "condition_rating" in df.columns:
                excellent_count = len(df[df["condition_rating"] >= 4.5])
                good_count = len(df[(df["condition_rating"] >= 3.5) & (df["condition_rating"] < 4.5)])
                average_count = len(df[(df["condition_rating"] >= 2.5) & (df["condition_rating"] < 3.5)])
                poor_count = len(df[df["condition_rating"] < 2.5])
            else:
                excellent_count = good_count = average_count = poor_count = 0
            
            # Financial
            total_value = df["purchase_cost"].fillna(0).sum() if "purchase_cost" in df.columns else 0
            dept_count = df["department"].nunique() if "department" in df.columns else 0
            
            # Warranty
            expired_count = expiring_30 = expiring_90 = expiring_180 = 0
            if "warranty_expiry" in df.columns:
                for _, row in df.iterrows():
                    try:
                        we = pd.to_datetime(row["warranty_expiry"])
                        days_left = (we.date() - today).days
                        if days_left < 0:
                            expired_count += 1
                        elif days_left <= 30:
                            expiring_30 += 1
                        elif days_left <= 90:
                            expiring_90 += 1
                        elif days_left <= 180:
                            expiring_180 += 1
                    except:
                        pass
            
            # ============================================
            # EXECUTIVE KPI ROW
            # ============================================
            st.markdown("### 🎯 Executive Asset Overview")
            
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-top:3px solid #CC0000;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Total Assets</div><div style="font-size:2.2rem;font-weight:800;color:#1a1a1a;">{total_assets}</div><div style="font-size:0.65rem;color:#888;">Across {dept_count} Depts</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-top:3px solid #10B981;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Active</div><div style="font-size:2.2rem;font-weight:800;color:#10B981;">{active_count}</div><div style="font-size:0.65rem;color:#888;">{round(active_count/total_assets*100) if total_assets > 0 else 0}% of total</div></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-top:3px solid #F59E0B;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Critical</div><div style="font-size:2.2rem;font-weight:800;color:#F59E0B;">{critical_count}</div><div style="font-size:0.65rem;color:#888;">{critical_active} Active</div></div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-top:3px solid #EF4444;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Breakdown</div><div style="font-size:2.2rem;font-weight:800;color:#EF4444;">{breakdown_count}</div><div style="font-size:0.65rem;color:#888;">{critical_breakdown} Critical</div></div>""", unsafe_allow_html=True)
            with c5:
                st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-top:3px solid #3B82F6;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Portfolio Value</div><div style="font-size:1.4rem;font-weight:800;color:#3B82F6;">₦{total_value:,.0f}</div><div style="font-size:0.65rem;color:#888;">Total</div></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Status Breakdown
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🔴 Critical Assets")
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem;">
                    <div style="background:#ECFDF5;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#10B981;">{critical_active}</div><div style="font-size:0.6rem;color:#666;">Active</div></div>
                    <div style="background:#FEF3C7;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#F59E0B;">{critical_count - critical_active - critical_breakdown}</div><div style="font-size:0.6rem;color:#666;">Inactive</div></div>
                    <div style="background:#FEF2F2;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#EF4444;">{critical_breakdown}</div><div style="font-size:0.6rem;color:#666;">Breakdown</div></div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("#### 🟢 Non-Critical Assets")
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem;">
                    <div style="background:#ECFDF5;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#10B981;">{non_critical_active}</div><div style="font-size:0.6rem;color:#666;">Active</div></div>
                    <div style="background:#FEF3C7;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#F59E0B;">{non_critical_count - non_critical_active - non_critical_breakdown}</div><div style="font-size:0.6rem;color:#666;">Inactive</div></div>
                    <div style="background:#FEF2F2;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#EF4444;">{non_critical_breakdown}</div><div style="font-size:0.6rem;color:#666;">Breakdown</div></div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Health Matrix
            st.markdown("### 🏥 Asset Health Matrix")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;border-left:4px solid #10B981;"><div style="font-weight:700;color:#10B981;">⭐ Excellent</div><div style="font-size:1.5rem;font-weight:800;">{excellent_count}</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;border-left:4px solid #3B82F6;"><div style="font-weight:700;color:#3B82F6;">👍 Good</div><div style="font-size:1.5rem;font-weight:800;">{good_count}</div></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;border-left:4px solid #F59E0B;"><div style="font-weight:700;color:#F59E0B;">⚠️ Average</div><div style="font-size:1.5rem;font-weight:800;">{average_count}</div></div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;border-left:4px solid #EF4444;"><div style="font-weight:700;color:#EF4444;">🔴 Poor</div><div style="font-size:1.5rem;font-weight:800;">{poor_count}</div></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Warranty & Financial
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 📋 Warranty Status")
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
                    <div style="background:#FEF2F2;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#EF4444;">{expired_count}</div><div style="font-size:0.6rem;">Expired</div></div>
                    <div style="background:#FFFBEB;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#F59E0B;">{expiring_30}</div><div style="font-size:0.6rem;">≤30 days</div></div>
                    <div style="background:#EFF6FF;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#3B82F6;">{expiring_90}</div><div style="font-size:0.6rem;">≤90 days</div></div>
                    <div style="background:#ECFDF5;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:1.2rem;font-weight:800;color:#10B981;">{expiring_180}</div><div style="font-size:0.6rem;">≤180 days</div></div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("### 💰 Financial Summary")
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:1rem;">
                    <table style="width:100%;font-size:0.8rem;">
                        <tr><td>📊 Portfolio Value</td><td style="text-align:right;font-weight:700;">₦{total_value:,.2f}</td></tr>
                        <tr><td>📈 Avg Asset Value</td><td style="text-align:right;font-weight:700;">₦{total_value/total_assets:,.2f}</td></tr>
                        <tr><td>🏢 Departments</td><td style="text-align:right;font-weight:700;">{dept_count}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            
            if critical_breakdown > 0:
                st.error(f"🚨 {critical_breakdown} critical assets in BREAKDOWN!")
            if expired_count > 0:
                st.warning(f"⚠️ {expired_count} assets with expired warranties!")
    
    # ============================================
    # TAB 1: ASSET REGISTER TABLE
    # ============================================
    with ar_tabs[1]:
        st.markdown("### 📋 Asset Register")
        
        if len(df) == 0:
            st.info("No assets registered yet. Add assets to see them here.")
        else:
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                # Create combined department — sub_division labels
                df["dept_display"] = df.apply(lambda row: f"{row['department']} — {row['sub_division']}" if pd.notna(row.get('sub_division')) and row.get('sub_division') != 'N/A' else row['department'], axis=1)
                dept_options = ["All"] + sorted(df["dept_display"].unique().tolist())
                dept_filter = st.selectbox("Department", dept_options, key="ar_dept")
            with c2:
                building_options = ["All"] + sorted(df["location_building"].unique().tolist())
                building_filter = st.selectbox("Building", building_options, key="ar_bldg_filter")
            with c3:
                status_filter = st.selectbox("Status", ["All", "active", "inactive", "breakdown"], key="ar_status")
            with c4:
                priority_filter = st.selectbox("Priority", ["All", "critical", "high", "medium", "low"], key="ar_pri")
            with c5:
                search = st.text_input("🔍 Search", placeholder="Name, code, location...", key="ar_search")
            
            display_df = df.copy()
            if dept_filter != "All":
                display_df = display_df[display_df["dept_display"] == dept_filter]
            if building_filter != "All" and "location_building" in display_df.columns:
                display_df = display_df[display_df["location_building"] == building_filter]
            if status_filter != "All" and "status" in display_df.columns:
                display_df = display_df[display_df["status"] == status_filter]
            if priority_filter != "All" and "priority" in display_df.columns:
                display_df = display_df[display_df["priority"] == priority_filter]
            if search:
                mask = False
                for col in ["name", "asset_tag", "location_building", "manufacturer", "model"]:
                    if col in display_df.columns:
                        mask = mask | display_df[col].astype(str).str.contains(search, case=False, na=False)
                display_df = display_df[mask]
            
            st.caption(f"Showing {len(display_df)} of {len(df)} assets")
            
            display_cols = [c for c in ["asset_tag", "name", "department", "location_building", "location_floor", "status", "priority", "manufacturer", "model", "serial_number", "condition_rating", "purchase_cost"] if c in display_df.columns]
            
            st.dataframe(display_df[display_cols], use_container_width=True, hide_index=True, height=500)
            
            csv = display_df.to_csv(index=False)
            st.download_button("📥 Export CSV", csv, f"assets_{fc}_{today}.csv", "text/csv", use_container_width=True)
    
    # ============================================
    # TAB 2: ADD ASSET — 6-STEP WIZARD
    # ============================================
    with ar_tabs[2]:
        st.markdown("### ➕ Register New Asset")
        
        if "add_asset_step" not in st.session_state:
            st.session_state.add_asset_step = 1
        
        steps = ["1. Asset Info", "2. Specifications", "3. Financial", "4. Assignment", "5. Maintenance", "6. Review"]
        step_cols = st.columns(6)
        for i, (col, name) in enumerate(zip(step_cols, steps)):
            with col:
                if i + 1 == st.session_state.add_asset_step:
                    st.markdown(f"""<div style="background:#CC0000;color:white;padding:0.5rem;border-radius:8px;text-align:center;font-weight:600;font-size:0.7rem;">{name}</div>""", unsafe_allow_html=True)
                elif i + 1 < st.session_state.add_asset_step:
                    st.markdown(f"""<div style="background:#10B981;color:white;padding:0.5rem;border-radius:8px;text-align:center;font-weight:600;font-size:0.7rem;">✅ {name}</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div style="background:#f5f5f5;color:#999;padding:0.5rem;border-radius:8px;text-align:center;font-size:0.7rem;">{name}</div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        cats = DB.get_categories()
        cat_names = sorted([c.get("name","") for c in cats]) if cats else ["MEP-ELECTRICAL", "MEP-HVAC", "MEP-PLUMBING", "ELV-FIRE ALARM", "CIVIL", "VERTICAL TRANSPORT"]
        
        # STEP 1
        if st.session_state.add_asset_step == 1:
            with st.form("add_step1"):
                c1, c2 = st.columns(2)
                with c1:
                    s1_name = st.text_input("Asset Name*", placeholder="e.g. DG 1 - CT-3 - DG Yard")
                    s1_code = st.text_input("Asset Code*", placeholder="e.g. WTC-DG-001")
                    s1_cat = st.selectbox("Category*", cat_names)
                    s1_parent = st.text_input("Parent Asset", placeholder="e.g. Diesel Generator Set")
                    s1_priority = st.selectbox("Priority*", ["critical", "high", "medium", "low"])
                    s1_ownership = st.selectbox("Ownership*", ["Churchgate Group", "Leased", "Tenant Owned", "Government"])
                with c2:
                    s1_dept = st.selectbox("Department*", cat_names)
                    s1_desc = st.text_area("Description*", height=100)
                    s1_status = st.selectbox("Status*", ["active", "inactive", "breakdown", "decommissioned"])
                    s1_health = st.selectbox("Health Condition", ["Excellent", "Good", "Average", "Poor"])
                    s1_vfreq = st.selectbox("Verification Frequency", ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])
                
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                with c1:
                    s1_bldg = st.selectbox("Building*", ["CT — Office Tower", "SAT — Residential Tower", "RC — Recreation Center", "IP — Intermediate Parking"])
                with c2:
                    s1_subloc = st.text_input("Sub Location", placeholder="e.g. DG Yard, Floor 13")
                with c3:
                    s1_region = st.text_input("City", value=info.get("city", "Abuja"))
                
                c1, c2 = st.columns(2)
                with c1:
                    s1_barcode = st.text_input("Barcode*")
                with c2:
                    s1_geo = st.text_input("Geo Location", placeholder="9.0486, 7.4732")
                
                if st.form_submit_button("Continue →", use_container_width=True, type="primary"):
                    if s1_name and s1_code and s1_desc and s1_bldg and s1_barcode:
                        st.session_state.s1 = {"name": s1_name, "asset_tag": s1_code, "department": s1_dept, "category_name": s1_cat, "parent_asset": s1_parent, "priority": s1_priority, "ownership": s1_ownership, "description": s1_desc, "status": s1_status, "health": s1_health, "verification_frequency": s1_vfreq, "location_building": s1_bldg, "location_floor": s1_subloc, "region": s1_region, "barcode": s1_barcode, "geo_location": s1_geo}
                        st.session_state.add_asset_step = 2
                        st.rerun()
                    else:
                        st.error("⚠️ Fill all required fields (*)")
        
        # STEP 2
        elif st.session_state.add_asset_step == 2:
            with st.form("add_step2"):
                st.markdown("#### 📐 Technical Specifications")
                c1, c2, c3 = st.columns(3)
                with c1:
                    s2_mfg = st.text_input("Manufacturer*", placeholder="Cummins, Perkins")
                    s2_serial = st.text_input("Serial Number*")
                    s2_model = st.text_input("Model")
                with c2:
                    s2_modelno = st.text_input("Model Number")
                    s2_capacity = st.text_input("Capacity", placeholder="500 KVA")
                    s2_weight = st.text_input("Gross Weight (kg)")
                with c3:
                    s2_dims = st.text_input("Dimensions", placeholder="200x150x100 cm")
                    s2_stdhrs = st.number_input("Standard Running Hours", value=0.0)
                    s2_tothrs = st.number_input("Total Operational Hours", value=0.0)
                
                c1, c2 = st.columns(2)
                with c1:
                    s2_sap = st.date_input("SAP Created Date", today)
                    s2_install = st.date_input("Installation Date", today)
                with c2:
                    s2_checklist = st.selectbox("Checklist Template", ["Standard MEP", "Standard HVAC", "Standard ELV", "Standard Civil"])
                    s2_ppm = st.selectbox("PPM Frequency", ["Weekly", "Monthly", "Quarterly", "Yearly"])
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("⬅️ Back", use_container_width=True):
                        st.session_state.add_asset_step = 1
                        st.rerun()
                with c2:
                    if st.form_submit_button("Continue →", use_container_width=True, type="primary"):
                        if s2_mfg and s2_serial:
                            st.session_state.s2 = {"manufacturer": s2_mfg, "serial_number": s2_serial, "model": s2_model, "model_no": s2_modelno, "capacity": s2_capacity, "gross_weight": s2_weight, "dimensions": s2_dims, "standard_running_hrs": s2_stdhrs, "total_operational_hrs": s2_tothrs, "sap_created_date": str(s2_sap), "installation_date": str(s2_install), "checklist_template": s2_checklist, "ppm_frequency": s2_ppm}
                            st.session_state.add_asset_step = 3
                            st.rerun()
                        else:
                            st.error("⚠️ Manufacturer and Serial Number required")
        
        # STEP 3
        elif st.session_state.add_asset_step == 3:
            with st.form("add_step3"):
                st.markdown("#### 💰 Financial Details")
                c1, c2, c3 = st.columns(3)
                with c1:
                    s3_price = st.number_input("Purchase Price (₦)*", min_value=0.0, step=10000.0)
                    s3_currency = st.selectbox("Currency", ["NGN", "USD", "EUR"])
                    s3_residual = st.number_input("Residual Value %", value=10.0)
                with c2:
                    s3_purchdate = st.date_input("Purchase Date", today)
                    s3_depmethod = st.selectbox("Depreciation", ["Straight Line", "Reducing Balance"])
                    s3_useful = st.number_input("Useful Life (Years)", value=10)
                with c3:
                    s3_invoice = st.text_input("Invoice No")
                    s3_invdate = st.date_input("Invoice Date", today)
                    s3_po = st.text_input("PO Number")
                    s3_podate = st.date_input("PO Date", today)
                
                st.markdown("#### 🛡️ Warranty")
                c1, c2, c3 = st.columns(3)
                with c1:
                    s3_warranty = st.selectbox("Warranty?", ["Yes", "No"])
                with c2:
                    s3_wstart = st.date_input("Warranty Start", today)
                with c3:
                    s3_wend = st.date_input("Warranty End", today + timedelta(days=365))
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("⬅️ Back", use_container_width=True):
                        st.session_state.add_asset_step = 2
                        st.rerun()
                with c2:
                    if st.form_submit_button("Continue →", use_container_width=True, type="primary"):
                        st.session_state.s3 = {"purchase_cost": s3_price, "currency": s3_currency, "residual_value": s3_residual, "purchase_date": str(s3_purchdate), "depreciation_method": s3_depmethod, "useful_life": s3_useful, "invoice_no": s3_invoice, "invoice_date": str(s3_invdate), "po_number": s3_po, "po_date": str(s3_podate), "warranty_applicable": s3_warranty == "Yes", "warranty_start": str(s3_wstart), "warranty_expiry": str(s3_wend)}
                        st.session_state.add_asset_step = 4
                        st.rerun()
        
        # STEP 4
        elif st.session_state.add_asset_step == 4:
            with st.form("add_step4"):
                st.markdown("#### 👤 Assignment")
                users = DB.get_users()
                user_names = [u.get("name","") for u in users]
                c1, c2 = st.columns(2)
                with c1:
                    s4_user = st.selectbox("Assigned User", ["None"] + user_names)
                    s4_adduser = st.selectbox("Additional User", ["None"] + user_names)
                with c2:
                    s4_vendor = st.selectbox("Vendor", ["None", "Clyde Engineering", "Gates and Shield", "TXB Enterprise", "Brainworks"])
                    s4_replaceyr = st.number_input("Replace Year", value=2030)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("⬅️ Back", use_container_width=True):
                        st.session_state.add_asset_step = 3
                        st.rerun()
                with c2:
                    if st.form_submit_button("Continue →", use_container_width=True, type="primary"):
                        st.session_state.s4 = {"assigned_to_name": s4_user if s4_user != "None" else None, "additional_user": s4_adduser if s4_adduser != "None" else None, "vendor": s4_vendor if s4_vendor != "None" else None, "plan_year_to_replace": s4_replaceyr}
                        st.session_state.add_asset_step = 5
                        st.rerun()
        
        # STEP 5
        elif st.session_state.add_asset_step == 5:
            with st.form("add_step5"):
                st.markdown("#### 🔧 Maintenance Setup")
                c1, c2 = st.columns(2)
                with c1:
                    s5_amc = st.selectbox("AMC?", ["Yes", "No"])
                    s5_amcprov = st.text_input("AMC Provider")
                    s5_amcstart = st.date_input("AMC Start", today)
                with c2:
                    s5_amccost = st.number_input("AMC Cost (₦/yr)", min_value=0.0, step=10000.0)
                    s5_amcend = st.date_input("AMC End", today + timedelta(days=365))
                    s5_team = st.selectbox("Maintenance Team", ["Engineering — Electrical", "Engineering — HVAC", "Engineering — Plumbing", "Facility Management — Hard Services"])
                
                s5_checklist = st.text_area("PPM Checklist Items (one per line)", placeholder="Check for dust\nCheck earth connection\nCheck fire suppression")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("⬅️ Back", use_container_width=True):
                        st.session_state.add_asset_step = 4
                        st.rerun()
                with c2:
                    if st.form_submit_button("Continue →", use_container_width=True, type="primary"):
                        st.session_state.s5 = {"amc_applicable": s5_amc == "Yes", "amc_provider": s5_amcprov, "amc_cost": s5_amccost, "amc_start": str(s5_amcstart), "amc_end": str(s5_amcend), "maintenance_team": s5_team, "ppm_checklist_items": s5_checklist}
                        st.session_state.add_asset_step = 6
                        st.rerun()
        
        # STEP 6 — REVIEW & SUBMIT
        elif st.session_state.add_asset_step == 6:
            s1 = st.session_state.get("s1", {})
            s2 = st.session_state.get("s2", {})
            s3 = st.session_state.get("s3", {})
            s4 = st.session_state.get("s4", {})
            s5 = st.session_state.get("s5", {})
            
            st.markdown("#### 📋 Review & Submit")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div style="background:white;border-radius:8px;padding:0.8rem;border:1px solid #ddd;font-size:0.75rem;"><b>🏗️ Asset:</b> {s1.get('name','N/A')}<br><b>Code:</b> {s1.get('asset_tag','N/A')}<br><b>Location:</b> {s1.get('location_building','N/A')}</div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div style="background:white;border-radius:8px;padding:0.8rem;border:1px solid #ddd;font-size:0.75rem;"><b>📐 Mfg:</b> {s2.get('manufacturer','N/A')}<br><b>Serial:</b> {s2.get('serial_number','N/A')}<br><b>Model:</b> {s2.get('model','N/A')}</div>""", unsafe_allow_html=True)
            
            st.markdown(f"""<div style="background:white;border-radius:8px;padding:0.8rem;border:1px solid #ddd;font-size:0.75rem;margin-top:0.5rem;"><b>💰 Price:</b> ₦{s3.get('purchase_cost',0):,.2f} | <b>Warranty:</b> {s3.get('warranty_start','N/A')} → {s3.get('warranty_expiry','N/A')}</div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("⬅️ Back", use_container_width=True, key="s6_back"):
                    st.session_state.add_asset_step = 5
                    st.rerun()
            with c2:
                if st.button("💾 Save Draft", use_container_width=True, key="s6_draft"):
                    st.info("Draft saving coming soon.")
            with c3:
                if st.button("✅ SUBMIT ASSET", use_container_width=True, type="primary", key="s6_submit"):
                    full_data = {**s1, **s2, **s3, **s4, **s5}
                    # Map department
                    raw_dept = full_data.get("department", "")
                    dept_mapping = {
                        "Engineering — Electrical": ("Engineering", "Electrical"),
                        "Engineering — Fire Fighting": ("Engineering", "Fire Fighting"),
                        "Engineering — HVAC": ("Engineering", "HVAC"),
                        "Engineering — Plumbing": ("Engineering", "Plumbing"),
                        "Engineering — Vertical Transportation": ("Engineering", "Vertical Transportation (Lifts)"),
                        "Facility Management — FM Operations": ("Facility Management", "FM Operations"),
                        "Facility Management — Fitout Works": ("Facility Management", "Fitout Works"),
                        "Facility Management — Front of House": ("Facility Management", "Front of House"),
                        "Facility Management — Hard Services": ("Facility Management", "Hard Services"),
                        "Facility Management — Soft Services": ("Facility Management", "Soft Services"),
                        "Security": ("Security", "Security"),
                        "Technology Group — Access Control": ("Technology Group", "Access Control"),
                        "Technology Group — Automation": ("Technology Group", "Automation"),
                        "Technology Group — BMS": ("Technology Group", "BMS"),
                        "Technology Group — CCTV": ("Technology Group", "CCTV"),
                        "Technology Group — Fire Alarm & Voice Evac": ("Technology Group", "Fire Alarm & Voice Evac"),
                        "Technology Group — Networks & Connectivity": ("Technology Group", "Networks & Connectivity"),
                        "Technology Group — MDTH (DSTV)": ("Technology Group", "MDTH (DSTV)"),
                    }
                    mapped_dept, mapped_sub = dept_mapping.get(raw_dept, (raw_dept, raw_dept))
                    full_data["department"] = mapped_dept
                    full_data["sub_division"] = mapped_sub
                    full_data["facility_code"] = fc
                    full_data["created_at"] = datetime.now().isoformat()
                    full_data["condition_rating"] = 5 if s1.get("health") == "Excellent" else 4 if s1.get("health") == "Good" else 3 if s1.get("health") == "Average" else 2
                    
                    # Get category_id from category_name
                    try:
                        cat_lookup = supabase.table("asset_categories").select("id").eq("name", s1.get("category_name", "")).execute()
                        if cat_lookup.data:
                            full_data["category_id"] = cat_lookup.data[0]["id"]
                    except:
                        pass
                    
                    result = DB.insert("assets", full_data)
                    if result:
                        st.success(f"✅ Asset '{s1.get('name','N/A')}' registered!")
                        st.balloons()
                        for k in ["s1","s2","s3","s4","s5","add_asset_step"]:
                            if k in st.session_state:
                                del st.session_state[k]
                        st.session_state.add_asset_step = 1
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Failed. Try again.")
    
    # ============================================
    # TAB 3: BULK UPLOAD
    # ============================================
    with ar_tabs[3]:
        st.markdown("### 📦 Bulk Asset Upload")
        
        template_cols = ["Asset Name", "Asset Code", "Department", "Category", "Parent Asset", "Status", "Priority", "Ownership", "Manufacturer", "Serial No", "Model", "Capacity", "Description", "Location", "Sub Location", "City", "Barcode", "Purchase Price", "Purchase Date", "Warranty Start", "Warranty End", "Verification Frequency", "Checklist Template", "PPM Frequency"]
        template_df = pd.DataFrame(columns=template_cols)
        
        st.download_button("📥 Download CSV Template", template_df.to_csv(index=False), "asset_upload_template.csv", "text/csv", use_container_width=True)
        
        st.markdown("---")
        uploaded = st.file_uploader("Upload filled CSV", type="csv")
        
        if uploaded:
            # Try to detect separator (tab or comma)
            try:
                bulk_df = pd.read_csv(uploaded, sep=None, engine='python', skiprows=1)
            except:
                bulk_df = pd.read_csv(uploaded, skiprows=1)
            
            # Remove completely empty rows
            bulk_df = bulk_df.dropna(how='all')
            
            # Filter out rows where Assetname is empty or NA
            if "Assetname" in bulk_df.columns:
                bulk_df = bulk_df[bulk_df["Assetname"].notna() & (bulk_df["Assetname"] != "") & (bulk_df["Assetname"] != "NA")]
            
            st.dataframe(bulk_df.head(10), use_container_width=True)
            st.caption(f"{len(bulk_df)} valid assets found (empty rows skipped)")
            
            if st.button(f"🚀 Upload {len(bulk_df)} Assets", use_container_width=True, type="primary"):
                success = 0
                for _, row in bulk_df.iterrows():
                    try:
                        raw_dept = str(row.get("Department", "")).strip()
                        
                        # Department mapping
                        dept_mapping = {
                            "Engineering — Electrical": ("Engineering", "Electrical"),
                            "Engineering — Fire Fighting": ("Engineering", "Fire Fighting"),
                            "Engineering — HVAC": ("Engineering", "HVAC"),
                            "Engineering — Plumbing": ("Engineering", "Plumbing"),
                            "Engineering — Vertical Transportation": ("Engineering", "Vertical Transportation (Lifts)"),
                            "Engineering — Vertical Transportation (Lifts)": ("Engineering", "Vertical Transportation (Lifts)"),
                            "Facility Management — FM Operations": ("Facility Management", "FM Operations"),
                            "Facility Management — Fitout Works": ("Facility Management", "Fitout Works"),
                            "Facility Management — Front of House": ("Facility Management", "Front of House"),
                            "Facility Management — Hard Services": ("Facility Management", "Hard Services"),
                            "Facility Management — Soft Services": ("Facility Management", "Soft Services"),
                            "Security": ("Security", "Security"),
                            "Technology Group — Access Control": ("Technology Group", "Access Control"),
                            "Technology Group — Automation": ("Technology Group", "Automation"),
                            "Technology Group — BMS": ("Technology Group", "BMS"),
                            "Technology Group — CCTV": ("Technology Group", "CCTV"),
                            "Technology Group — Fire Alarm & Voice Evac": ("Technology Group", "Fire Alarm & Voice Evac"),
                            "Technology Group — Networks & Connectivity": ("Technology Group", "Networks & Connectivity"),
                            "Technology Group — MDTH (DSTV)": ("Technology Group", "MDTH (DSTV)"),
                        }
                        
                        mapped_dept, mapped_sub = dept_mapping.get(raw_dept, (raw_dept, raw_dept))
                        
                        # Parse purchase price safely
                        purchase_price = 0
                        try:
                            pp = row.get("Purchase Price", 0)
                            if pd.notna(pp) and str(pp).strip() != "" and str(pp).strip() != "NA":
                                purchase_price = float(str(pp).replace(",", "").replace("₦", "").strip())
                        except:
                            pass
                        
                        asset_data = {
                            "facility_code": fc,
                            "name": str(row.get("Assetname", row.get("Asset Name", ""))).strip(),
                            "asset_tag": str(row.get("Asset Code", "")).strip() or f"AUTO-{fc}-{success+1}",
                            "department": mapped_dept,
                            "sub_division": mapped_sub,
                            "category_name": str(row.get("Category", "")).strip(),
                            "parent_asset": str(row.get("Parent Asset", "")).strip(),
                            "status": str(row.get("Status", "active")).strip().lower() or "active",
                            "priority": str(row.get("Priority", "medium")).strip().lower() or "medium",
                            "ownership": str(row.get("Ownership", "")).strip(),
                            "manufacturer": str(row.get("Manufacturer", "")).strip(),
                            "model": str(row.get("Model", "")).strip(),
                            "model_no": str(row.get("Model NO", "")).strip(),
                            "serial_number": str(row.get("Serial NO", row.get("Serial No", ""))).strip(),
                            "capacity": str(row.get("Capacity", "")).strip(),
                            "description": str(row.get("Description", "")).strip(),
                            "location_building": str(row.get("Location", "")).strip(),
                            "location_floor": str(row.get("Sub Location", "")).strip(),
                            "barcode": str(row.get("Barcode", "")).strip(),
                            "geo_location": str(row.get("Geo Location", "")).strip(),
                            "purchase_cost": purchase_price,
                            "purchase_date": fix_date(row.get("Purchase Date")),
                            "installation_date": fix_date(row.get("Installation Date")),
                            "warranty_start": fix_date(row.get("Warrenty Start Date", row.get("Warranty Start Date"))),
                            "warranty_expiry": fix_date(row.get("Warrenty End Date", row.get("Warranty End Date"))),
                            "sap_created_date": fix_date(row.get("SAP Created Date")),
                            "depreciation_method": str(row.get("Depreciation Method", "")).strip(),
                            "residual_value": str(row.get("Residual Value / Percentage", "")).strip(),
                            "invoice_no": str(row.get("Invioce NO", row.get("Invoice NO", ""))).strip(),
                            "po_number": str(row.get("PO Number", "")).strip(),
                            "vendor": str(row.get("Vendor", "")).strip(),
                            "assigned_user": str(row.get("Assigned User", "")).strip(),
                            "additional_user": str(row.get("Additional User", "")).strip(),
                            "checklist": str(row.get("Checklist", "")).strip(),
                            "ppm": str(row.get("PPM", "")).strip(),
                            "verification_frequency": str(row.get("Verification Frequency", "")).strip(),
                            "gross_weight": str(row.get("Gross Weight", "")).strip(),
                            "dimensions": str(row.get("Size and Dimensions", "")).strip(),
                            "health_condition": str(row.get("Health Condition", "")).strip(),
                            "region": str(row.get("Region", "")).strip(),
                            "city": str(row.get("City", "")).strip(),
                            "plan_year_to_replace": str(row.get("Plan Year to replace", "")).strip(),
                            "warranty_applicable": str(row.get("Warrenty Applicable", "")).strip(),
                            "standard_running_hrs": str(row.get("Standard Running Hrs", "")).strip(),
                            "total_operational_hrs": str(row.get("Total Operational Hrs", "")).strip(),
                            "currency": str(row.get("Currency", "")).strip() or "NGN",
                            "useful_life": str(row.get("Useful Life", "")).strip(),
                            "condition_rating": 5,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        # Remove None values that should be NULL in DB
                        # Only filter out truly empty values, keep name/asset_tag even if "NA"
                        keep_keys = ["name", "asset_tag", "facility_code", "status", "priority", "department", "condition_rating", "created_at"]
                        asset_data = {k: v for k, v in asset_data.items() if k in keep_keys or (v is not None and v != "" and str(v).strip() != "" and str(v).strip().lower() not in ["na", "none", "null"])}
                        
                        DB.insert("assets", asset_data)
                        success += 1
                        
                        # Progress update every 500 rows
                        if success % 500 == 0:
                            st.write(f"⏳ Uploaded {success} assets...")
                            
                    except Exception as e:
                        continue
                st.success(f"✅ {success} assets uploaded!")
                st.balloons()
                st.rerun()
    
    # ============================================
    # TAB 4: READINGS — AI-POWERED ASSET PERFORMANCE CENTER
    # ============================================
    with ar_tabs[4]:
        st.markdown("### 📖 Asset Readings — AI-Powered Performance Center")
        
        if len(df) == 0:
            st.info("No assets registered. Add assets to see readings.")
        else:
            # KPI Calculations
            total_assets_count = len(df)
            critical_assets_count = len(df[df["priority"].isin(["critical", "high"])]) if "priority" in df.columns else 0
            
            # Readings summary (placeholder until readings table is populated)
            total_readings = 0
            abnormal_readings = 0
            corrective_wos = 0
            total_downtime = 0
            
            try:
                readings_res = supabase.table("utility_readings").select("id", count="exact").eq("facility_code", fc).execute()
                total_readings = readings_res.count or 0
            except:
                pass
            
            # Executive KPI Row
            st.markdown("### 🎯 Performance KPIs")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;border-top:3px solid #3B82F6;box-shadow:0 2px 6px rgba(0,0,0,0.04);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Total Readings</div><div style="font-size:1.6rem;font-weight:800;color:#3B82F6;">{total_readings}</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;border-top:3px solid #EF4444;box-shadow:0 2px 6px rgba(0,0,0,0.04);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Abnormal</div><div style="font-size:1.6rem;font-weight:800;color:#EF4444;">{abnormal_readings}</div></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;border-top:3px solid #F59E0B;box-shadow:0 2px 6px rgba(0,0,0,0.04);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Critical Alerts</div><div style="font-size:1.6rem;font-weight:800;color:#F59E0B;">{critical_assets_count}</div></div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;border-top:3px solid #8B5CF6;box-shadow:0 2px 6px rgba(0,0,0,0.04);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Corrective WOs</div><div style="font-size:1.6rem;font-weight:800;color:#8B5CF6;">{corrective_wos}</div></div>""", unsafe_allow_html=True)
            with c5:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;border-top:3px solid #EC4899;box-shadow:0 2px 6px rgba(0,0,0,0.04);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Downtime (Hrs)</div><div style="font-size:1.6rem;font-weight:800;color:#EC4899;">{total_downtime}</div></div>""", unsafe_allow_html=True)
            with c6:
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;border-top:3px solid #10B981;box-shadow:0 2px 6px rgba(0,0,0,0.04);"><div style="font-size:0.6rem;color:#888;text-transform:uppercase;">Health Score</div><div style="font-size:1.6rem;font-weight:800;color:#10B981;">{round(total_assets_count/max(total_assets_count,1)*100)}%</div></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # AI Insights Banner
            if critical_assets_count > 10:
                st.warning(f"🤖 **AI Insight:** {critical_assets_count} critical assets require immediate attention. Recommend prioritizing PPM for these assets.")
            if abnormal_readings > 0:
                st.error(f"🤖 **AI Alert:** {abnormal_readings} abnormal readings detected. Predictive maintenance recommended.")
            if total_readings == 0:
                st.info("🤖 **AI Insight:** No readings recorded yet. Start recording utility readings to enable predictive analytics.")
            
            st.markdown("---")
            
            # Filters
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                reading_building = st.selectbox("🏢 Building", ["All"] + sorted(df["location_building"].unique().tolist()), key="read_bldg")
            with c2:
                reading_dept = st.selectbox("🏷️ Department", ["All"] + sorted(df["department"].unique().tolist()), key="read_dept")
            with c3:
                reading_priority = st.selectbox("⚠️ Priority", ["All", "critical", "high", "medium", "low"], key="read_pri")
            with c4:
                reading_search = st.text_input("🔍 Search Asset", key="read_search", placeholder="Name or code...")
            
            # Build readings dataframe
            readings_data = []
            for _, asset in df.iterrows():
                # Apply filters
                if reading_building != "All" and asset.get("location_building","") != reading_building:
                    continue
                if reading_dept != "All" and asset.get("department","") != reading_dept:
                    continue
                if reading_priority != "All" and asset.get("priority","") != reading_priority:
                    continue
                if reading_search:
                    name = str(asset.get("name","")).lower()
                    code = str(asset.get("asset_tag","")).lower()
                    if reading_search.lower() not in name and reading_search.lower() not in code:
                        continue
                
                # Calculate asset age
                asset_age = "N/A"
                if pd.notna(asset.get("installation_date")):
                    try:
                        inst_date = pd.to_datetime(asset["installation_date"])
                        age_days = (today - inst_date.date()).days
                        if age_days > 365:
                            asset_age = f"{age_days // 365} Years"
                        elif age_days > 30:
                            asset_age = f"{age_days // 30} Months"
                        else:
                            asset_age = f"{age_days} Days"
                    except:
                        pass
                
                readings_data.append({
                    "Asset ID": asset.get("asset_tag", "N/A"),
                    "Asset Name": asset.get("name", "N/A"),
                    "Department": asset.get("department", "N/A"),
                    "Sub-Division": asset.get("sub_division", "N/A"),
                    "Manufacturer": asset.get("manufacturer", "N/A"),
                    "Model": asset.get("model", "N/A"),
                    "Serial Number": asset.get("serial_number", "N/A"),
                    "Location": f"{asset.get('location_building','')}",
                    "Priority": asset.get("priority", "N/A").upper(),
                    "Condition": asset.get("condition_rating", "N/A"),
                    "Asset Age": asset_age,
                    "Running Hours": asset.get("total_operational_hrs", 0) if pd.notna(asset.get("total_operational_hrs")) else 0,
                    "PPM Frequency": asset.get("verification_frequency", "N/A"),
                    "Last PPM": "N/A",
                    "Breakdowns": 0,
                    "Downtime (Hrs)": 0,
                })
            
            rd_df = pd.DataFrame(readings_data)
            
            st.caption(f"📋 Showing {len(rd_df)} of {len(df)} assets")
            
            # Color-code condition column
            def highlight_condition(val):
                try:
                    v = float(val)
                    if v >= 4.5: return 'background-color:#ECFDF5;color:#059669;font-weight:600;'
                    elif v >= 3.5: return 'background-color:#EFF6FF;color:#2563EB;font-weight:600;'
                    elif v >= 2.5: return 'background-color:#FFFBEB;color:#D97706;font-weight:600;'
                    else: return 'background-color:#FEF2F2;color:#DC2626;font-weight:600;'
                except:
                    return ''
            
            def highlight_priority(val):
                if val in ["CRITICAL", "HIGH"]:
                    return 'background-color:#FEF2F2;color:#DC2626;font-weight:600;'
                return ''
            
            if len(rd_df) > 0:
                styled = rd_df.style
                if "Condition" in rd_df.columns:
                    styled = styled.map(highlight_condition, subset=["Condition"])
                if "Priority" in rd_df.columns:
                    styled = styled.map(highlight_priority, subset=["Priority"])
                
                st.dataframe(styled, use_container_width=True, hide_index=True, height=500)
            else:
                st.info("No assets match your filters.")
            
            st.markdown("---")
            
            # Charts & Analytics
            st.markdown("### 📊 Asset Performance Analytics")
            
            c1, c2 = st.columns(2)
            with c1:
                # Department distribution chart
                if "department" in rd_df.columns and len(rd_df) > 0:
                    dept_counts = rd_df["Department"].value_counts().head(10)
                    fig_dept = px.bar(
                        x=dept_counts.values, y=dept_counts.index, orientation='h',
                        title="Assets by Department", color=dept_counts.values,
                        color_continuous_scale="Reds", labels={"x":"Count","y":""}
                    )
                    fig_dept.update_layout(height=350)
                    st.plotly_chart(fig_dept, use_container_width=True)
            
            with c2:
                # Priority distribution
                if "Priority" in rd_df.columns and len(rd_df) > 0:
                    pri_counts = rd_df["Priority"].value_counts()
                    pri_colors = {"CRITICAL":"#EF4444","HIGH":"#F59E0B","MEDIUM":"#3B82F6","LOW":"#10B981"}
                    pie_colors = [pri_colors.get(p,"#999") for p in pri_counts.index]
                    fig_pri = px.pie(
                        values=pri_counts.values, names=pri_counts.index,
                        title="Priority Distribution", color_discrete_sequence=pie_colors
                    )
                    fig_pri.update_layout(height=350)
                    st.plotly_chart(fig_pri, use_container_width=True)
            
            # Export section
            st.markdown("---")
            st.markdown("### 📥 Export Data")
            c1, c2, c3 = st.columns(3)
            with c1:
                csv_data = rd_df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv_data, f"asset_readings_{fc}_{today}.csv", "text/csv", use_container_width=True)
            with c2:
                # HTML Export
                logo_b64 = get_logo_base64()
                html_report = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;margin:20px;color:#1a1a1a;font-size:11px}}.header{{background:#1a1a1a;color:white;padding:15px;border-radius:8px;display:flex;align-items:center;gap:10px;margin-bottom:15px}}.header h1{{margin:0;font-size:16px}}table{{width:100%;border-collapse:collapse;font-size:9px}}th{{background:#CC0000;color:white;padding:5px}}td{{padding:4px;border-bottom:1px solid #eee}}.footer{{text-align:center;font-size:8px;color:#999;margin-top:15px}}</style></head><body><div class="header">{f'<img src="data:image/png;base64,{logo_b64}" height="30">' if logo_b64 else ''}<div><h1>Asset Readings Report</h1><p style="font-size:10px;opacity:0.8;">{info.get('full_name',fc)} | {today.strftime('%d %B %Y')}</p></div></div><table><tr><th>Asset ID</th><th>Name</th><th>Department</th><th>Location</th><th>Priority</th><th>Condition</th><th>Age</th></tr>"""
                for _, r in rd_df.head(100).iterrows():
                    html_report += f"<tr><td>{r['Asset ID']}</td><td>{r['Asset Name']}</td><td>{r['Department']}</td><td>{r['Location']}</td><td>{r['Priority']}</td><td>{r['Condition']}</td><td>{r['Asset Age']}</td></tr>"
                html_report += "</table><div class='footer'>Churchgate Group | facilityXperience | Confidential</div></body></html>"
                st.download_button("📥 Download HTML Report", html_report, f"readings_report_{today}.html", "text/html", use_container_width=True)
            with c3:
                try:
                    from fpdf import FPDF
                    pdf = FPDF('L','mm','A4')
                    pdf.add_page()
                    logo_path = Path("churchgate-logo.png")
                    if logo_path.exists():
                        pdf.image(str(logo_path), x=14, y=8, h=8)
                    pdf.set_font('Helvetica','B',14)
                    pdf.set_text_color(204,0,0)
                    pdf.cell(260,8,safe_text(f'Asset Readings Report - {info.get("full_name",fc)}'),0,1)
                    pdf.set_font('Helvetica','',8)
                    pdf.set_text_color(0,0,0)
                    pdf.cell(260,5,safe_text(f'Generated: {today.strftime("%d %B %Y")} | Total Assets: {len(rd_df)}'),0,1)
                    pdf.ln(3)
                    pdf.set_font('Helvetica','B',6)
                    pdf.set_fill_color(204,0,0)
                    pdf.set_text_color(255,255,255)
                    headers = ['Asset ID','Name','Department','Location','Priority','Condition','Age']
                    widths = [25,45,35,40,20,20,20]
                    for h,w in zip(headers,widths):
                        pdf.cell(w,5,safe_text(h),1,0,'C',True)
                    pdf.ln()
                    pdf.set_font('Helvetica','',6)
                    pdf.set_text_color(26,26,26)
                    for _,r in rd_df.head(50).iterrows():
                        vals = [safe_text(str(r['Asset ID'])), safe_text(str(r['Asset Name'])), safe_text(str(r['Department'])), safe_text(str(r['Location'])), safe_text(str(r['Priority'])), safe_text(str(r['Condition'])), safe_text(str(r['Asset Age']))]
                        for v,w in zip(vals,widths):
                            pdf.cell(w,4,v[:int(w/2)],1,0)
                        pdf.ln()
                    pdf_file = f"/tmp/readings_report_{today}.pdf"
                    pdf.output(pdf_file)
                    with open(pdf_file,"rb") as f:
                        st.download_button("📥 Download PDF", f.read(), f"readings_report_{today}.pdf", "application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"PDF: {str(e)[:50]}")
    
    # ============================================
    # TAB 5: PPM CALENDAR — REDESIGNED
    # ============================================
    with ar_tabs[5]:
        st.markdown("### 📅 PPM Calendar — Financial Year View")
        
        today = date.today()
        if today.month >= 4:
            fy_start_year = today.year
        else:
            fy_start_year = today.year - 1
        
        if "cal_offset" not in st.session_state:
            st.session_state.cal_offset = 0
        if "selected_ppm_date" not in st.session_state:
            st.session_state.selected_ppm_date = None
        
        block_start_month = 4 + (st.session_state.cal_offset * 6)
        block_start_year = fy_start_year + (block_start_month - 1) // 12
        block_start_month = ((block_start_month - 1) % 12) + 1
        
        months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        months_full = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        
        # Role-based department filter
        user_depts = safe_parse_permissions(st.session_state.get("user", {}).get("department_permissions", []))
        user_role = st.session_state.get("user_role", "staff")
        is_admin = user_role in ["admin", "approver"]
        
        # ============================================
        # FILTERS
        # ============================================
        st.markdown("### 🔍 Filters")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            df["dept_full"] = df.apply(lambda row: f"{row['department']} — {row['sub_division']}" if pd.notna(row.get('sub_division')) and row.get('sub_division') not in ['', 'N/A', 'NA'] else row['department'], axis=1)
            if is_admin:
                dept_options = ["All"] + sorted(df["dept_full"].dropna().unique().tolist())
            else:
                dept_options = ["All"] + [d for d in sorted(df["dept_full"].dropna().unique().tolist()) if any(ud in d for ud in user_depts)] if user_depts else ["All"]
            cal_dept = st.selectbox("Department", dept_options, key="cal_dept_filter")
        with c2:
            cal_asset = st.selectbox("Asset", ["All"] + sorted(df["parent_asset"].dropna().unique().tolist()), key="cal_asset_filter")
        with c3:
            cal_sub = st.selectbox("Sub Asset", ["All"] + sorted(df["name"].dropna().unique().tolist())[:100], key="cal_sub_filter")
        with c4:
            cal_bldg = st.selectbox("Building", ["All"] + sorted(df["location_building"].dropna().unique().tolist()), key="cal_bldg_filter")
        
        st.markdown("---")
        
        # ============================================
        # NAVIGATION & LEGEND
        # ============================================
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("◀ PREV 6 MONTHS", key="cal_prev6", use_container_width=True):
                st.session_state.cal_offset -= 1
                st.rerun()
        with c2:
            end_idx = ((block_start_month - 1 + 5) % 12)
            st.markdown(f"#### 📅 FY {fy_start_year}/{fy_start_year+1} — {months_short[block_start_month-1]} to {months_short[end_idx]}")
        with c3:
            if st.button("NEXT 6 MONTHS ▶", key="cal_next6", use_container_width=True):
                st.session_state.cal_offset += 1
                st.rerun()
        
        # Legend
        st.markdown("""
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin:8px 0;">
        <span style="background:#FEF2F2;color:#DC2626;padding:4px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;">🔴 Overdue</span>
        <span style="background:#CC0000;color:white;padding:4px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;">📍 Today</span>
        <span style="background:#EFF6FF;color:#2563EB;padding:4px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;">📆 Upcoming</span>
        <span style="background:#ECFDF5;color:#059669;padding:4px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;">✅ Completed</span>
        <span style="background:#F5F3FF;color:#7C3AED;padding:4px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;">⏳ Pending</span>
        <span style="background:#FAFAFA;color:#999;padding:4px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;">⬜ No PPM</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ============================================
        # GET PPM DATA WITH FILTERS
        # ============================================
        ppm_schedules = DB.get_all("ppm_schedules", fc, 5000)
        ppm_df = pd.DataFrame(ppm_schedules) if ppm_schedules else pd.DataFrame()
        
        if len(ppm_df) > 0 and "next_due_date" in ppm_df.columns:
            ppm_df["due_date_dt"] = pd.to_datetime(ppm_df["next_due_date"], errors='coerce')
        
        # Apply filters to PPM data
        if cal_dept != "All" and "assigned_team" in ppm_df.columns:
            ppm_df = ppm_df[ppm_df["assigned_team"].str.contains(cal_dept.replace(" — "," "), case=False, na=False)]
        
        # Build lookup
        ppm_dates = {}
        if len(ppm_df) > 0 and "due_date_dt" in ppm_df.columns:
            for _, row in ppm_df.iterrows():
                d = row["due_date_dt"]
                if pd.notna(d):
                    dk = d.strftime("%Y-%m-%d")
                    if dk not in ppm_dates:
                        ppm_dates[dk] = []
                    ppm_dates[dk].append(row.to_dict())
        
        # ============================================
        # KPI CARDS
        # ============================================
        total_ppm = len(ppm_df)
        overdue_ppm = len(ppm_df[(ppm_df["due_date_dt"].dt.date < today) & (ppm_df["status"] != "completed")]) if len(ppm_df) > 0 else 0
        today_ppm = len(ppm_df[ppm_df["due_date_dt"].dt.date == today]) if len(ppm_df) > 0 else 0
        completed_ppm = len(ppm_df[ppm_df["status"] == "completed"]) if len(ppm_df) > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("📋 Total", total_ppm)
        with c2: st.metric("🔴 Overdue", overdue_ppm)
        with c3: st.metric("📍 Today", today_ppm)
        with c4: st.metric("✅ Completed", completed_ppm)
        
        st.markdown("---")
        
        # ============================================
        # 6-MONTH CALENDAR GRID
        # ============================================
        cal_html = """<style>
            .cal-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; font-family: 'Inter', sans-serif; }
            .cal-month { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; }
            .cal-hdr { padding: 8px 0; text-align: center; font-weight: 700; font-size: 14px; color: white; }
            .cal-hdr.cur { background: #CC0000; }
            .cal-hdr.reg { background: #1a1a1a; }
            .cal-tbl { width: 100%; border-collapse: collapse; }
            .cal-tbl th { background: #f9fafb; padding: 4px 0; text-align: center; font-size: 10px; color: #9ca3af; font-weight: 700; border-bottom: 2px solid #e5e7eb; }
            .cal-tbl td { text-align: center; padding: 0; height: 32px; cursor: pointer; border: 1px solid #f0f0f0; }
            .cal-tbl td a { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-decoration: none; font-size: 11px; font-weight: 600; color: #374151; border-radius: 4px; }
            .cal-tbl td:hover { outline: 2px solid #CC0000; outline-offset: -2px; z-index: 5; }
            .cal-tbl td.em { background: #fafafa; cursor: default; }
            .cal-tbl td.em:hover { outline: none; }
            .cal-tbl td.td { background: #CC0000; }
            .cal-tbl td.td a { color: white; font-weight: 800; }
            .cal-tbl td.ov { background: #FEF2F2; }
            .cal-tbl td.ov a { color: #DC2626; font-weight: 700; }
            .cal-tbl td.up { background: #EFF6FF; }
            .cal-tbl td.up a { color: #2563EB; font-weight: 700; }
            .cal-tbl td.cp { background: #ECFDF5; }
            .cal-tbl td.cp a { color: #059669; font-weight: 600; }
            .cal-tbl td.pn { background: #F5F3FF; }
            .cal-tbl td.pn a { color: #7C3AED; font-weight: 700; }
            .cal-tbl td.no { background: #fdfdfd; }
            .cal-tbl td.no a { color: #bbb; font-weight: 400; }
            .cal-badge { font-size: 9px; background: #CC0000; color: white; border-radius: 10px; padding: 0px 5px; min-width: 16px; text-align: center; line-height: 1.2; }
        </style><div class="cal-grid">"""
        
        for row_idx in range(2):
            for col_idx in range(3):
                mo = row_idx * 3 + col_idx
                dm = ((block_start_month - 1 + mo) % 12) + 1
                dy = block_start_year + ((block_start_month - 1 + mo) // 12)
                
                fd = date(dy, dm, 1)
                if dm == 12: ld = date(dy, 12, 31)
                else: ld = date(dy, dm + 1, 1) - timedelta(days=1)
                
                sw = fd.weekday()
                ic = (dm == today.month and dy == today.year)
                hc = "cur" if ic else "reg"
                
                cal_html += f'<div class="cal-month"><div class="cal-hdr {hc}">{months_short[dm-1]} {dy}</div><table class="cal-tbl"><tr><th>M</th><th>T</th><th>W</th><th>T</th><th>F</th><th>S</th><th>S</th></tr>'
                
                dc = 1
                for w in range(6):
                    cal_html += "<tr>"
                    for wd in range(7):
                        if (w == 0 and wd < sw) or dc > ld.day:
                            cal_html += '<td class="em"></td>'
                        else:
                            cd = date(dy, dm, dc)
                            dk = cd.strftime("%Y-%m-%d")
                            it = dk == today.strftime("%Y-%m-%d")
                            pt = ppm_dates.get(dk, [])
                            pc = len(pt)
                            
                            if it: cls = "td"
                            elif pc == 0: cls = "no"
                            else:
                                ov = any(p.get("status") not in ["completed","approved"] for p in pt)
                                ad = all(p.get("status") in ["completed","approved"] for p in pt)
                                pn = any(p.get("status") == "pending" for p in pt)
                                if ov: cls = "ov"
                                elif ad: cls = "cp"
                                elif pn: cls = "pn"
                                else: cls = "up"
                            
                            badge = f'<span class="cal-badge">{pc}</span>' if pc > 0 else ''
                            cal_html += f'<td class="{cls}"><a href="?ppm_d={dk}">{dc}{badge}</a></td>'
                            dc += 1
                    cal_html += "</tr>"
                    if dc > ld.day: break
                cal_html += "</table></div>"
        
        cal_html += "</div>"
        st.markdown(cal_html, unsafe_allow_html=True)
        
        # Handle click via URL param
        params = st.query_params
        if "ppm_d" in params:
            try:
                st.session_state.selected_ppm_date = datetime.strptime(params["ppm_d"], "%Y-%m-%d").date()
                # Don't clear params - let the page reload naturally
            except:
                pass
        
        st.markdown("---")
        
        # ============================================
        # PPM DETAILS FOR SELECTED DAY
        # ============================================
        if st.session_state.selected_ppm_date:
            sel = st.session_state.selected_ppm_date
            dks = sel.strftime("%Y-%m-%d")
            pps = ppm_dates.get(dks, [])
            
            if pps:
                st.markdown(f"### 📋 {len(pps)} PPMs — {sel.strftime('%d %B %Y')}")
                
                # Sub-filter for selected day
                c1, c2 = st.columns(2)
                with c1:
                    day_dept = st.selectbox("Quick Filter", ["All"] + list(set(p.get("assigned_team","") for p in pps)), key="day_dept_filter")
                with c2:
                    if st.button("🔧 EXECUTE PPMs", key="goto_ppma", use_container_width=True, type="primary"):
                        st.session_state.page = "ppma"
                        st.rerun()
                
                display_pps = pps
                if day_dept != "All":
                    display_pps = [p for p in pps if p.get("assigned_team","") == day_dept]
                
                for p in display_pps:
                    sts = p.get('status','scheduled')
                    sc = {"completed":"#10B981","scheduled":"#3B82F6","pending":"#F59E0B","overdue":"#EF4444","approved":"#059669"}.get(sts,"#3B82F6")
                    ic = {"completed":"✅","scheduled":"📆","pending":"⏳","overdue":"🔴","approved":"🟢"}.get(sts,"📋")
                    
                    st.markdown(f"""
                    <div style="background:white;border-left:4px solid {sc};border-radius:8px;padding:0.8rem;margin:0.3rem 0;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <b>{ic} {p.get('title','N/A')[:80]}</b>
                                <br><span style="font-size:0.7rem;color:#666;">👤 {p.get('assigned_team','N/A')} | 🔄 {p.get('frequency','N/A')}</span>
                            </div>
                            <span style="background:{sc};color:white;padding:3px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;">{sts.upper()}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"📅 **{sel.strftime('%d %B %Y')}** — No PPMs scheduled.")
            
            if st.button("❌ CLEAR SELECTION", key="clearppm", use_container_width=True):
                st.session_state.selected_ppm_date = None
                st.query_params.clear()
                st.rerun()
        else:
            st.info("👆 **Click any day** on the calendar to view scheduled PPMs.")
        
        
    
    # ============================================
    # TAB 6: APPROVALS
    # ============================================
    with ar_tabs[6]:
        st.markdown("### ✅ Approvals Dashboard")
        
        approval_subtabs = st.tabs(["📋 Pending", "🔄 Movement", "🗑️ Discard", "💰 Sales"])
        
        with approval_subtabs[0]:
            st.info("Pending approvals will appear here when assets require review.")
        
        with approval_subtabs[1]:
            with st.form("move_req"):
                st.markdown("**Request Asset Movement**")
                asset_sel = st.selectbox("Asset", df["name"].tolist() if len(df) > 0 else ["None"])
                move_from = st.text_input("From Location")
                move_to = st.text_input("To Location")
                reason = st.text_area("Reason")
                if st.form_submit_button("Submit Movement Request", use_container_width=True):
                    st.success("✅ Movement request submitted!")
        
        with approval_subtabs[2]:
            with st.form("discard_req"):
                st.markdown("**Request Asset Discard**")
                asset_disc = st.selectbox("Asset", df["name"].tolist() if len(df) > 0 else ["None"], key="disc_asset")
                disc_reason = st.text_area("Reason")
                disc_method = st.selectbox("Method", ["Scrap", "Sell", "Donate", "Recycle"])
                if st.form_submit_button("Submit Discard Request", use_container_width=True):
                    st.success("✅ Discard request submitted!")
        
        with approval_subtabs[3]:
            with st.form("sale_req"):
                st.markdown("**Request Asset Sale**")
                asset_sale = st.selectbox("Asset", df["name"].tolist() if len(df) > 0 else ["None"], key="sale_asset")
                sale_price = st.number_input("Sale Price (₦)", min_value=0.0, step=10000.0)
                buyer = st.text_input("Buyer")
                if st.form_submit_button("Submit Sale Request", use_container_width=True):
                    st.success("✅ Sale request submitted!")
    
    # ============================================
    # TAB 7: AI-POWERED REPORTS SUITE
    # ============================================
    with ar_tabs[7]:
        st.markdown("### 📄 AI-Powered Reports Suite")
        
        if len(df) == 0:
            st.info("No assets to generate reports for.")
        else:
            report_type = st.selectbox("📊 Select Report Type", [
                "📋 Asset Summary Report",
                "🏢 Department Breakdown",
                "💰 Financial Report", 
                "🛡️ Warranty & Lifecycle Report",
                "📈 PPM Compliance Report",
                "⚙️ Custom Report Builder"
            ])
            
            st.markdown("---")
            
            # ============================================
            # ASSET SUMMARY REPORT
            # ============================================
            if report_type == "📋 Asset Summary Report":
                st.markdown("### 📋 Asset Summary Report")
                
                total = len(df)
                active = len(df[df["status"]=="active"]) if "status" in df.columns else 0
                inactive = len(df[df["status"]=="inactive"]) if "status" in df.columns else 0
                breakdown = len(df[df["status"]=="breakdown"]) if "status" in df.columns else 0
                critical = len(df[df["priority"].isin(["critical","high"])]) if "priority" in df.columns else 0
                
                # KPI Cards
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: st.metric("📋 Total Assets", total)
                with c2: st.metric("✅ Active", active)
                with c3: st.metric("🔴 Critical", critical)
                with c4: st.metric("⚠️ Breakdown", breakdown)
                with c5: st.metric("💤 Inactive", inactive)
                
                st.markdown("---")
                
                # Charts
                c1, c2 = st.columns(2)
                with c1:
                    if "department" in df.columns:
                        dept_counts = df["department"].value_counts().head(10)
                        fig = px.bar(x=dept_counts.values, y=dept_counts.index, orientation='h', title="Assets by Department", color=dept_counts.values, color_continuous_scale="Reds")
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                with c2:
                    if "location_building" in df.columns:
                        bldg_counts = df["location_building"].value_counts().head(8)
                        fig2 = px.pie(values=bldg_counts.values, names=bldg_counts.index, title="Assets by Building")
                        fig2.update_layout(height=400)
                        st.plotly_chart(fig2, use_container_width=True)
                
                # AI Executive Summary
                st.markdown("---")
                st.markdown("### 🤖 AI Executive Summary")
                
                compliance = round(active/total*100,1) if total > 0 else 0
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                    <h4>Executive Overview — {info.get('full_name',fc)}</h4>
                    <p>📋 <b>{total}</b> total assets registered across <b>{df['department'].nunique() if 'department' in df.columns else 0}</b> departments.</p>
                    <p>✅ <b>{compliance}%</b> asset availability rate with <b>{critical}</b> critical assets requiring priority attention.</p>
                    <p>⚠️ <b>{breakdown}</b> assets currently in breakdown status requiring immediate corrective action.</p>
                    <p>🏢 Assets distributed across <b>{df['location_building'].nunique() if 'location_building' in df.columns else 0}</b> buildings/locations.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Export
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.download_button("📥 CSV", df.to_csv(index=False), f"asset_summary_{today}.csv", "text/csv", use_container_width=True)
                with c2:
                    logo_b64 = get_logo_base64()
                    html_export = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;margin:20px}}h1{{color:#CC0000}}table{{width:100%;border-collapse:collapse}}th{{background:#CC0000;color:white;padding:8px}}td{{padding:6px;border-bottom:1px solid #eee}}.kpi{{display:flex;gap:10px}}.kpi div{{flex:1;background:#f5f5f5;padding:10px;border-radius:8px;text-align:center;border-left:4px solid #CC0000}}</style></head><body><h1>Asset Summary Report</h1><p>{info.get('full_name',fc)} | {today}</p><div class="kpi"><div><b>Total</b><br>{total}</div><div><b>Active</b><br>{active}</div><div><b>Critical</b><br>{critical}</div><div><b>Breakdown</b><br>{breakdown}</div></div></body></html>"""
                    st.download_button("📥 HTML", html_export, f"asset_summary_{today}.html", "text/html", use_container_width=True)
                with c3:
                    st.download_button("📥 Print View", df.head(100).to_csv(index=False), f"asset_print_{today}.csv", "text/csv", use_container_width=True)
            
            # ============================================
            # DEPARTMENT BREAKDOWN
            # ============================================
            elif report_type == "🏢 Department Breakdown":
                st.markdown("### 🏢 Department Breakdown Report")
                
                if "department" in df.columns and "sub_division" in df.columns:
                    dept_summary = df.groupby(["department","sub_division"]).agg(
                        Count=("name","count"),
                        Active=("status", lambda x: (x=="active").sum()),
                        Critical=("priority", lambda x: x.isin(["critical","high"]).sum())
                    ).reset_index()
                    
                    st.dataframe(dept_summary, use_container_width=True, hide_index=True)
                    
                    # Chart
                    fig = px.bar(dept_summary, x="sub_division", y="Count", color="department", title="Assets by Department & Sub-Division", barmode="group")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.download_button("📥 Download CSV", dept_summary.to_csv(index=False), f"dept_breakdown_{today}.csv", "text/csv", use_container_width=True)
                else:
                    st.info("Department data not available.")
            
            # ============================================
            # FINANCIAL REPORT
            # ============================================
            elif report_type == "💰 Financial Report":
                st.markdown("### 💰 Financial Report")
                
                total_value = df["purchase_cost"].fillna(0).sum() if "purchase_cost" in df.columns else 0
                avg_value = total_value / len(df) if len(df) > 0 else 0
                
                # Calculate depreciation
                depreciated_value = total_value * 0.8  # Estimate
                net_book_value = total_value * 0.2  # Estimate
                
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("📊 Portfolio Value", f"₦{total_value:,.0f}")
                with c2: st.metric("📈 Avg Asset Value", f"₦{avg_value:,.0f}")
                with c3: st.metric("📉 Depreciated Value", f"₦{depreciated_value:,.0f}")
                with c4: st.metric("💰 Net Book Value", f"₦{net_book_value:,.0f}")
                
                st.markdown("---")
                
                # Value by department
                if "department" in df.columns and "purchase_cost" in df.columns:
                    dept_value = df.groupby("department")["purchase_cost"].sum().reset_index()
                    dept_value = dept_value.sort_values("purchase_cost", ascending=False)
                    
                    fig = px.bar(dept_value, x="department", y="purchase_cost", title="Asset Value by Department (₦)", color="purchase_cost", color_continuous_scale="Greens")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.download_button("📥 Download Financial Report CSV", df.to_csv(index=False), f"financial_report_{today}.csv", "text/csv", use_container_width=True)
            
            # ============================================
            # WARRANTY & LIFECYCLE REPORT
            # ============================================
            elif report_type == "🛡️ Warranty & Lifecycle Report":
                st.markdown("### 🛡️ Warranty & Lifecycle Report")
                
                expired = 0
                expiring_30 = 0
                expiring_90 = 0
                expiring_180 = 0
                
                warranty_data = []
                if "warranty_expiry" in df.columns:
                    for _, row in df.iterrows():
                        try:
                            we = pd.to_datetime(row["warranty_expiry"])
                            days_left = (we.date() - today).days
                            
                            if days_left < 0:
                                expired += 1
                                status = "Expired"
                            elif days_left <= 30:
                                expiring_30 += 1
                                status = "Expiring ≤30 days"
                            elif days_left <= 90:
                                expiring_90 += 1
                                status = "Expiring ≤90 days"
                            elif days_left <= 180:
                                expiring_180 += 1
                                status = "Expiring ≤180 days"
                            else:
                                status = "Active"
                            
                            warranty_data.append({
                                "Asset": row.get("name",""),
                                "Department": row.get("department",""),
                                "Warranty Start": str(row.get("warranty_start",""))[:10],
                                "Warranty End": str(row.get("warranty_expiry",""))[:10],
                                "Days Left": days_left,
                                "Status": status
                            })
                        except:
                            pass
                
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("🔴 Expired", expired)
                with c2: st.metric("🟡 ≤30 Days", expiring_30)
                with c3: st.metric("🔵 ≤90 Days", expiring_90)
                with c4: st.metric("🟢 ≤180 Days", expiring_180)
                
                if warranty_data:
                    wd = pd.DataFrame(warranty_data)
                    st.dataframe(wd, use_container_width=True, hide_index=True)
                    st.download_button("📥 Download Warranty Report", wd.to_csv(index=False), f"warranty_report_{today}.csv", "text/csv", use_container_width=True)
                else:
                    st.info("No warranty data available.")
            
            # ============================================
            # PPM COMPLIANCE REPORT
            # ============================================
            elif report_type == "📈 PPM Compliance Report":
                st.markdown("### 📈 PPM Compliance Report")
                
                ppm_schedules = DB.get_all("ppm_schedules", fc, 5000)
                
                if ppm_schedules:
                    ppm_df_rpt = pd.DataFrame(ppm_schedules)
                    
                    total_ppm = len(ppm_df_rpt)
                    completed_ppm = len(ppm_df_rpt[ppm_df_rpt["status"]=="completed"]) if "status" in ppm_df_rpt.columns else 0
                    overdue_ppm = len(ppm_df_rpt[(pd.to_datetime(ppm_df_rpt["next_due_date"], errors='coerce').dt.date < today) & (ppm_df_rpt["status"]!="completed")]) if "next_due_date" in ppm_df_rpt.columns else 0
                    
                    compliance_rate = round(completed_ppm/total_ppm*100,1) if total_ppm > 0 else 0
                    
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("📋 Total PPMs", total_ppm)
                    with c2: st.metric("✅ Completed", completed_ppm)
                    with c3: st.metric("🔴 Overdue", overdue_ppm)
                    with c4: st.metric("📈 Compliance", f"{compliance_rate}%")
                    
                    st.download_button("📥 Download PPM Report CSV", ppm_df_rpt.to_csv(index=False), f"ppm_compliance_{today}.csv", "text/csv", use_container_width=True)
                else:
                    st.info("No PPM schedules found.")
            
            # ============================================
            # CUSTOM REPORT BUILDER
            # ============================================
            elif report_type == "⚙️ Custom Report Builder":
                st.markdown("### ⚙️ Custom Report Builder")
                
                available_cols = [c for c in df.columns if c not in ["id","metadata","created_by","updated_at"]]
                selected_cols = st.multiselect("Select Columns", available_cols, default=["name","asset_tag","department","sub_division","location_building","status","priority"])
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    dept_filter_rpt = st.selectbox("Department", ["All"] + sorted(df["department"].unique().tolist()), key="rpt_dept")
                with c2:
                    bldg_filter_rpt = st.selectbox("Building", ["All"] + sorted(df["location_building"].unique().tolist()), key="rpt_bldg")
                with c3:
                    status_filter_rpt = st.selectbox("Status", ["All","active","inactive","breakdown"], key="rpt_status")
                
                filtered = df.copy()
                if dept_filter_rpt != "All": filtered = filtered[filtered["department"]==dept_filter_rpt]
                if bldg_filter_rpt != "All": filtered = filtered[filtered["location_building"]==bldg_filter_rpt]
                if status_filter_rpt != "All": filtered = filtered[filtered["status"]==status_filter_rpt]
                
                if selected_cols:
                    report_df = filtered[selected_cols]
                    st.dataframe(report_df, use_container_width=True, hide_index=True, height=400)
                    st.caption(f"📋 {len(report_df)} rows × {len(selected_cols)} columns")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button("📥 Download CSV", report_df.to_csv(index=False), f"custom_report_{today}.csv", "text/csv", use_container_width=True)
                    with c2:
                        # HTML export
                        logo_b64 = get_logo_base64()
                        html_custom = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;margin:20px;font-size:10px}}h1{{color:#CC0000}}table{{width:100%;border-collapse:collapse}}th{{background:#CC0000;color:white;padding:6px}}td{{padding:4px;border-bottom:1px solid #eee}}</style></head><body><h1>Custom Asset Report</h1><p>{info.get('full_name',fc)} | {today}</p><table><tr>{''.join(f'<th>{c}</th>' for c in selected_cols)}</tr>"""
                        for _, r in report_df.head(200).iterrows():
                            html_custom += "<tr>" + "".join(f"<td>{r[c]}</td>" for c in selected_cols) + "</tr>"
                        html_custom += "</table></body></html>"
                        st.download_button("📥 Download HTML", html_custom, f"custom_report_{today}.html", "text/html", use_container_width=True)
    
    # ============================================
    # TAB 8: SETTINGS
    # ============================================
    with ar_tabs[8]:
        st.markdown("### ⚙️ Settings")
        
        sett_tabs = st.tabs(["📍 Locations", "🏢 Departments", "🏷️ Categories", "🏭 Manufacturers"])
        
        with sett_tabs[0]:
            st.markdown("#### 📍 Locations")
            locs = DB.get_locations(fc)
            if locs:
                for l in locs:
                    st.markdown(f"**{l.get('location_code','')}** — {l.get('location_name','')}")
            with st.form("add_loc"):
                lc = st.text_input("Code", placeholder="CT")
                ln = st.text_input("Name", placeholder="CT — Office Tower")
                if st.form_submit_button("Add Location", use_container_width=True):
                    if lc and ln:
                        supabase.table("helpdesk_locations").insert({"facility_code": fc, "location_code": lc, "location_name": ln}).execute()
                        st.success("✅ Added!")
                        st.rerun()
        
        with sett_tabs[1]:
            st.markdown("#### 🏢 Departments")
            if len(df) > 0 and "department" in df.columns:
                for d in sorted(df["department"].unique()):
                    st.markdown(f"- {d}")
            else:
                st.info("No departments yet.")
        
        with sett_tabs[2]:
            st.markdown("#### 🏷️ Categories")
            cats_list = DB.get_categories()
            if cats_list:
                for c in cats_list:
                    st.markdown(f"- {c.get('name','N/A')}")
            else:
                st.info("No categories yet.")
        
        with sett_tabs[3]:
            st.markdown("#### 🏭 Manufacturers")
            if len(df) > 0 and "manufacturer" in df.columns:
                mfgs = df["manufacturer"].dropna().unique()
                for m in sorted(mfgs):
                    st.markdown(f"- {m}")
            else:
                st.info("No manufacturers yet.")

# ============================================
# WORK PERMIT — COMPLETE FIXED MODULE
# ============================================
def format_wat_time(dt_str):
    """Convert to Lagos WAT timezone"""
    try:
        from datetime import timezone, timedelta
        if not dt_str: return "N/A"
        dt = datetime.fromisoformat(str(dt_str).replace('Z', '+00:00'))
        wat = dt.astimezone(timezone(timedelta(hours=1)))
        return wat.strftime("%d-%b-%Y %I:%M %p") + " WAT"
    except:
        return str(dt_str)[:19] if dt_str else "N/A"

def send_email_notification(to_email, subject, body):
    """Send real email and log to database"""
    try:
        config = supabase.table("email_config").select("*").eq("is_active", True).single().execute()
        if config and config.data:
            cfg = config.data
            msg = MIMEMultipart()
            msg['From'] = f"facilityXperience <{cfg.get('sender_email', 'eetuk@churchgate.com')}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(cfg.get('smtp_host', 'smtp.gmail.com'), cfg.get('smtp_port', 587)) as server:
                server.starttls()
                server.login(cfg.get('sender_email', 'eetuk@churchgate.com'), cfg.get('sender_password', ''))
                server.send_message(msg)
            
            supabase.table("email_log").insert({
                "facility_code": "WTC", "email_to": to_email, "email_subject": subject,
                "email_body": body, "email_type": "work_permit", "status": "sent",
                "sent_at": datetime.now().isoformat()
            }).execute()
            return True
    except Exception as e:
        try:
            supabase.table("email_log").insert({
                "facility_code": "WTC", "email_to": to_email, "email_subject": subject,
                "email_body": f"{body}\n\n[Note: {str(e)}]", "email_type": "work_permit",
                "status": "queued", "sent_at": datetime.now().isoformat()
            }).execute()
        except: pass
    return False

def get_workflow_people(fc, level, department=None):
    """Get people for a workflow level, filtered by department"""
    try:
        query = supabase.table("workflow_config").select("*").eq("facility_code", fc).eq("workflow_type", "work_permit").eq("level_number", level).eq("is_active", True)
        res = query.execute()
        people = res.data if res.data else []
        if department and people:
            filtered = [p for p in people if "All Departments" in p.get("department_filter", []) or department in p.get("department_filter", [])]
            if filtered:
                return filtered
        return [p for p in people if "All Departments" in p.get("department_filter", [])] if people else []
    except: return []

def get_sub_locations_for_building(fc, building_code):
    """Get sub-locations for a building"""
    try:
        loc = supabase.table("helpdesk_locations").select("id").eq("facility_code", fc).eq("location_code", building_code).single().execute()
        if loc.data:
            res = supabase.table("helpdesk_sub_locations").select("sub_location_name").eq("location_id", loc.data["id"]).order("sub_location_name").execute()
            if res.data:
                return [s["sub_location_name"] for s in res.data]
    except: pass
    return [f"{building_code} / 0", f"{building_code} / 1"]

def page_wp():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    
    user_perms = safe_parse_permissions(st.session_state.get("user", {}).get("extra_permissions", []))
    user_role = st.session_state.get("user_role", "staff")
    is_admin = user_role in ["admin", "approver"]
    can_authorize = is_admin or "Authorize Permit" in user_perms or len(user_perms) == 0
    can_confirm = is_admin or "Confirm Permit" in user_perms or len(user_perms) == 0
    can_approve = is_admin or "Approve Permit" in user_perms or len(user_perms) == 0
    can_raise = is_admin or "Raise Permit" in user_perms or len(user_perms) == 0
    
    st.markdown(f'## 🛡️ Permit-to-Work System — {info.get("full_name", fc)}')
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Permits", "➕ Raise Permit", "📊 Reports", "⚙️ Workflow Config"])
    
    with tab1:
        st.markdown("### 📋 Work Permit Register")
        wp = DB.get_all("work_permits", fc, 500)
        
        if wp and len(wp) > 0:
            df = pd.DataFrame(wp)
            
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.metric("📋 Total", len(df))
            with c2: st.metric("⏳ Submitted", len(df[df["workflow_stage"] == "submitted"]) if "workflow_stage" in df.columns else 0)
            with c3: st.metric("🔐 Authorized", len(df[df["workflow_stage"] == "authorized"]) if "workflow_stage" in df.columns else 0)
            with c4: st.metric("✅ Confirmed", len(df[df["workflow_stage"] == "confirmed"]) if "workflow_stage" in df.columns else 0)
            with c5: st.metric("🟢 Approved", len(df[df["workflow_stage"] == "approved"]) if "workflow_stage" in df.columns else 0)
            
            st.markdown("---")
            
            for i, row in df.iterrows():
                stage = row.get("workflow_stage", "submitted")
                icons = {"submitted": "⏳", "authorized": "🔐", "confirmed": "✅", "approved": "🟢", "rejected": "❌"}
                icon = icons.get(stage, "📋")
                
                title = row.get('title', 'No Title')[:80]
                permit_no = row.get('permit_number', 'N/A')
                
                status_colors = {"submitted":"#F59E0B","authorized":"#3B82F6","confirmed":"#8B5CF6","approved":"#10B981","rejected":"#EF4444"}
                card_key = f"wp_card_{row['id']}"
                if card_key not in st.session_state:
                    st.session_state[card_key] = False
                
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:0.8rem;margin:0.4rem 0;border-left:4px solid {status_colors.get(stage,'#4a4a4a')};box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span><b>{icon} {permit_no}</b> — {title[:60]}</span>
                        <span style="background:{status_colors.get(stage,'#4a4a4a')};color:white;padding:2px 10px;border-radius:12px;font-size:0.65rem;font-weight:600;">{stage.upper()}</span>
                    </div>
                    <div style="font-size:0.7rem;color:#666;margin-top:0.2rem;">
                        👤 {row.get('raised_by_name','N/A')} | 📅 {format_wat_time(row.get('start_datetime',''))} | 📍 {row.get('work_location','')[:40]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([3,1])
                with c1:
                    pass
                with c2:
                    btn_text = "🔼 Hide Details" if st.session_state[card_key] else "📋 View Details"
                    if st.button(btn_text, key=f"toggle_{row['id']}", use_container_width=True):
                        st.session_state[card_key] = not st.session_state[card_key]
                        st.rerun()
                
                if st.session_state[card_key]:
                    with st.container():
                        st.markdown(f"""
                        <div style="background:#f9fafb;border-radius:10px;padding:1rem;margin:0.5rem 0;border:1px solid #e5e7eb;">
                            <p><b>👤 Raised by:</b> {row.get('raised_by_name','N/A')} ({row.get('raised_by_designation','')})</p>
                            <p><b>📅 Period:</b> {format_wat_time(row.get('start_datetime',''))} → {format_wat_time(row.get('end_datetime',''))}</p>
                            <p><b>📍 Location:</b> {row.get('work_location','')}</p>
                            <p><b>📝 Description:</b> {row.get('description','')[:200]}</p>
                            <p><b>🏢 Department:</b> {row.get('department','')}</p>
                            <hr>
                            <p><b>🔄 Audit Trail:</b></p>
                            <p style="font-size:0.75rem;">📤 Submitted: {format_wat_time(row.get('submitted_at',row.get('created_at','')))} by {row.get('raised_by_name','N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if row.get("authorized_at"):
                            st.caption(f"🔐 Authorized: {format_wat_time(row['authorized_at'])} by {row.get('authorized_by_name','')}")
                        if row.get("confirmed_at"):
                            st.caption(f"✅ Confirmed: {format_wat_time(row['confirmed_at'])} by {row.get('confirmed_by_name','')}")
                        if row.get("approved_at"):
                            st.caption(f"🟢 Approved: {format_wat_time(row['approved_at'])} by {row.get('approved_by_name','')}")
                        if stage == "rejected" and row.get("rejected_reason"):
                            st.error(f"❌ Rejected: {row.get('rejected_reason','')}")
                            st.info("📝 Requester can resubmit with corrections")
                        
                        st.markdown("**⚡ Actions:**")
                        now = datetime.now().isoformat()
                        dept = row.get("department", "")
                        
                        if can_authorize and stage == "submitted":
                            auth_comment = st.text_area("Authorization Comment", key=f"auth_cmt_{row['id']}", height=60)
                            if st.button("🔐 Authorize", key=f"auth_btn_{row['id']}", use_container_width=True):
                                if auth_comment:
                                    auth_name = st.session_state.get("user_name","Authorizer")
                                    DB.update("work_permits", row["id"], {"workflow_stage":"authorized","authorized_by_name":auth_name,"authorized_at":now})
                                    st.success("🔐 Authorized!")
                                    st.balloons()
                                    st.rerun()
                        
                        if can_confirm and stage == "authorized":
                            conf_comment = st.text_area("Confirmation Comment", key=f"conf_cmt_{row['id']}", height=60)
                            if st.button("✅ Confirm", key=f"conf_btn_{row['id']}", use_container_width=True):
                                if conf_comment:
                                    conf_name = st.session_state.get("user_name","Confirmer")
                                    DB.update("work_permits", row["id"], {"workflow_stage":"confirmed","confirmed_by_name":conf_name,"confirmed_at":now})
                                    st.success("✅ Confirmed!")
                                    st.balloons()
                                    st.rerun()
                        
                        if can_approve and stage in ["authorized","confirmed"]:
                            app_comment = st.text_area("Approval Comment", key=f"app_cmt_{row['id']}", height=60)
                            if st.button("🟢 Approve", key=f"app_btn_{row['id']}", use_container_width=True):
                                if app_comment:
                                    app_name = st.session_state.get("user_name","Approver")
                                    DB.update("work_permits", row["id"], {"workflow_stage":"approved","status":"approved","approved_by_name":app_name,"approved_at":now})
                                    st.success("🟢 Approved!")
                                    st.balloons()
                                    st.rerun()
                        
                        if stage not in ["rejected","approved"] and (is_admin or can_authorize or can_confirm or can_approve):
                            rej_comment = st.text_area("Rejection Reason", key=f"rej_cmt_{row['id']}", height=60)
                            if st.button("❌ Reject", key=f"rej_btn_{row['id']}", use_container_width=True):
                                if rej_comment:
                                    DB.update("work_permits", row["id"], {"workflow_stage":"rejected","status":"rejected","rejected_at":now,"rejected_reason":rej_comment})
                                    st.error("❌ Permit Rejected!")
                                    st.rerun()
                        
                        if stage == "rejected" and (is_admin or can_raise):
                            if st.button("🔄 Resubmit", key=f"resubmit_{row['id']}", use_container_width=True):
                                DB.update("work_permits", row["id"], {"workflow_stage":"submitted","status":"pending","submitted_at":now,"authorized_at":None,"authorized_by_name":None,"confirmed_at":None,"confirmed_by_name":None,"approved_at":None,"approved_by_name":None,"rejected_at":None,"rejected_reason":None})
                                st.success("🔄 Resubmitted!")
                                st.balloons()
                                st.rerun()
                
                st.markdown("---")
        else:
            st.info("📋 No work permits found. Raise your first permit in the '➕ Raise Permit' tab!")
    
    with tab2:
        st.markdown("### 📝 Raise New Work Permit")
        
        buildings = DB.get_locations(fc)
        
        building_options = {}
        for b in buildings:
            building_options[b.get("location_code", "")] = b.get("location_name", "")
        
        if not building_options:
            building_options = {"CT": "CT — Office Tower", "SAT": "SAT — Residential Tower", "RC": "RC — Recreation Center", "IP": "IP — Intermediate Parking"}
        
        st.markdown("**🏢 Select Building & Location**")
        c1, c2 = st.columns(2)
        with c1:
            selected_building = st.selectbox("Building*", 
                options=list(building_options.keys()),
                format_func=lambda x: building_options.get(x, x),
                key="wp_building")
        with c2:
            sub_locs = get_sub_locations_for_building(fc, selected_building)
            if not sub_locs or len(sub_locs) == 0:
                sub_locs = [f"{selected_building} / 0"]
            sub_location = st.selectbox("Sub-Location*", sub_locs, key="wp_subloc")
        
        full_location = f"{building_options.get(selected_building, selected_building)} → {sub_location}"
        st.caption(f"📍 Full Location: {full_location}")
        
        st.markdown("---")
        
        with st.form("wp_raise_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                permit_type = st.selectbox("Permit Type*", [
                    "General Work Permit", "Hot Work Permit", "Confined Space Entry Permit",
                    "Working at Height Permit", "Electrical/Mechanical/LOTO Permit",
                    "Energy Isolation Permit", "ELV Systems Work Permit", "Excavation Permit"
                ])
                dept = st.selectbox("Department*", [
                    "Engineering — Electrical", "Engineering — HVAC", "Engineering — Plumbing",
                    "Engineering — Vertical Transportation (Lifts)", "Engineering — Fire Fighting",
                    "Engineering — Civil & Structural", "Engineering — Utilities & Energy",
                    "Facility Management — Hard Services", "Facility Management — Soft Services (Housekeeping)",
                    "Facility Management — FM Operations & Helpdesk", "Facility Management — Fitout Works",
                    "Facility Management — HSSE Safety & Compliance",
                    "Technology Group — Network & Connectivity", "Technology Group — Building Technology",
                    "Security — Man Guarding Operations",
                    "Contractor — Clyde Engineering", "Contractor — Gates and Shield"
                ])
            with c2:
                document_no = st.text_input("Document No", value=f"IMS-WTC-WP-{datetime.now().strftime('%Y%m%d')}")
            
            st.markdown("---")
            st.markdown("**👤 Requester Details**")
            c1, c2, c3 = st.columns(3)
            with c1:
                rname = st.text_input("Requester Name*")
                rdesignation = st.text_input("Requester Designation*")
            with c2:
                rcontact = st.text_input("Requester Contact No*")
                powner = st.text_input("Process Owner Name*")
            with c3:
                pcontact = st.text_input("Process Owner Contact*")
                scoordinator = st.text_input("Site Coordinator*")
            
            st.markdown("---")
            st.markdown("**📅 Work Schedule**")
            c1, c2 = st.columns(2)
            with c1:
                sd = st.date_input("Proposed Start Date*", date.today())
                stime = st.time_input("Start Time*", time(8, 0))
            with c2:
                ed = st.date_input("Proposed End Date*", date.today())
                etime = st.time_input("End Time*", time(17, 0))
            
            workers = st.number_input("No. of Workers Expected*", min_value=1, max_value=100, value=2)
            workers_names = st.text_area("Workers Names* (one per line)", height=80, placeholder="Enter each worker's full name on a new line...")
            
            st.markdown("---")
            description = st.text_area("Brief Description of Work*", height=80, placeholder="Describe the work to be performed...")
            
            st.markdown("**🦺 PPE Required***")
            ppe_selected = st.multiselect("Select PPE", [
                "Hard Hat", "Face Shield", "Welder Gloves", "Electrical Gloves", "Body Harness",
                "Foot Protection", "Ear Plug/Earmuffs", "Chemical Goggles", "Safety Shoes",
                "Respirator", "Safety Glass", "Fall Protection"
            ])
            
            st.markdown("**🔧 Equipment Required***")
            equip_selected = st.multiselect("Select Equipment", [
                "Fire Extinguishers", "Warning Signs", "Walkie-talkie", "Ladder/Scaffold",
                "Fire Hoses", "Non-Sparking Tools", "Gas Detector", "Additional Lighting"
            ])
            
            with st.expander("📋 General Instructions to Contractors"):
                st.markdown("""
                1. ID card mandatory for all workers
                2. Safety Training daily at 9:30 AM
                3. Noisy works after 6:00 PM only
                4. Clear debris immediately after work
                5. Only service lifts for materials
                6. Smoking strictly prohibited
                7. No obstruction to fire escape routes
                8. Contractor liable for all injuries/damages
                """)
            
            st.markdown("---")
            
            submitted = st.form_submit_button("🛡️ Submit Work Permit", use_container_width=True, type="primary")
            
            if submitted:
                errors = []
                if not rname: errors.append("Requester Name")
                if not rdesignation: errors.append("Requester Designation")
                if not rcontact: errors.append("Requester Contact No")
                if not description: errors.append("Description of Work")
                if not sub_location or sub_location == "Select building first": errors.append("Sub-Location")
                
                if errors:
                    st.error(f"⚠️ Please fill: {', '.join(errors)}")
                else:
                    now = datetime.now().isoformat()
                    cnt = len(DB.get_all("work_permits", fc, 1000))
                    permit_number = f"PTW-{fc}-{datetime.now().year}-{str(cnt + 1).zfill(4)}"
                    
                    permit_data = {
                        "facility_code": fc, "permit_number": permit_number, "document_no": document_no,
                        "permit_type": permit_type, "department": dept, "title": description[:100],
                        "description": description, "raised_by_name": rname, "raised_by_designation": rdesignation,
                        "requester_contact": rcontact, "process_owner_name": powner,
                        "process_owner_contact": pcontact, "site_coordinator_name": scoordinator,
                        "workers_count": workers, "workers_names": workers_names,
                        "work_location": full_location,
                        "start_datetime": f"{sd}T{stime}", "end_datetime": f"{ed}T{etime}",
                        "ppe_required": ppe_selected, "equipment_required": equip_selected,
                        "status": "pending", "workflow_stage": "submitted", "submitted_at": now, "created_at": now
                    }
                    
                    DB.insert("work_permits", permit_data)
                    st.success(f"✅ Work Permit {permit_number} Submitted Successfully!")
                    st.balloons()
                    
                    authorizers = get_workflow_people(fc, 1, dept)
                    for a in authorizers:
                        send_email_notification(
                            a.get("person_email", ""),
                            f"📋 New Permit {permit_number} Requires Authorization",
                            f"<h3>New Work Permit Submitted</h3>"
                            f"<p><b>Permit:</b> {permit_number}</p>"
                            f"<p><b>Type:</b> {permit_type}</p>"
                            f"<p><b>Department:</b> {dept}</p>"
                            f"<p><b>Location:</b> {full_location}</p>"
                            f"<p><b>Raised by:</b> {rname} ({rdesignation})</p>"
                            f"<p><b>Description:</b> {description[:300]}</p>"
                        )
                    
                    st.rerun()
    
    with tab3:
        st.markdown("### 📊 Work Permit Analytics & Reports")
        wp_all = DB.get_all("work_permits", fc, 500)
        
        if wp_all and len(wp_all) > 0:
            df = pd.DataFrame(wp_all)
            
            total = len(df)
            approved_count = len(df[df["workflow_stage"] == "approved"]) if "workflow_stage" in df.columns else 0
            pending_count = len(df[df["workflow_stage"].isin(["submitted", "authorized", "confirmed"])]) if "workflow_stage" in df.columns else 0
            rejected_count = len(df[df["workflow_stage"] == "rejected"]) if "workflow_stage" in df.columns else 0
            
            lead_times = []
            delayed = 0
            if "submitted_at" in df.columns and "approved_at" in df.columns:
                approved_df = df[df["approved_at"].notna()]
                for _, r in approved_df.iterrows():
                    try:
                        s = pd.to_datetime(r["submitted_at"])
                        a = pd.to_datetime(r["approved_at"])
                        hrs = (a - s).total_seconds() / 3600
                        lead_times.append(hrs)
                        if hrs > 4: delayed += 1
                    except: pass
            
            avg_lead = sum(lead_times) / len(lead_times) if lead_times else 0
            dept_data = df["department"].value_counts().to_dict() if "department" in df.columns else {}
            stage_data = df["workflow_stage"].value_counts().to_dict() if "workflow_stage" in df.columns else {}
            
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.metric("📋 Total", total)
            with c2: st.metric("🟢 Approved", approved_count)
            with c3: st.metric("⏳ Pending", pending_count)
            with c4: st.metric("❌ Rejected", rejected_count)
            with c5: st.metric("⏱️ Avg Approval", f"{avg_lead:.1f} hrs")
            
            st.markdown("---")
            
            st.markdown("### 📅 Monthly Breakdown (Click to Filter)")
            
            if "report_month_filter" not in st.session_state:
                st.session_state.report_month_filter = None
            
            months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            months_full = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            
            cols = st.columns(6)
            for i in range(6):
                m_idx = i + 1
                count = len(df[pd.to_datetime(df["created_at"]).dt.month == m_idx]) if "created_at" in df.columns else 0
                is_active = st.session_state.report_month_filter == m_idx
                with cols[i]:
                    if st.button(f"{'🔴' if is_active else '📋'} {months_short[i]}: {count}", key=f"mbtn_{m_idx}", use_container_width=True):
                        st.session_state.report_month_filter = None if is_active else m_idx
                        st.rerun()
            
            cols2 = st.columns(6)
            for i in range(6):
                m_idx = i + 7
                count = len(df[pd.to_datetime(df["created_at"]).dt.month == m_idx]) if "created_at" in df.columns else 0
                is_active = st.session_state.report_month_filter == m_idx
                with cols2[i]:
                    if st.button(f"{'🔴' if is_active else '📋'} {months_short[i+6]}: {count}", key=f"mbtn_{m_idx}", use_container_width=True):
                        st.session_state.report_month_filter = None if is_active else m_idx
                        st.rerun()
            
            if st.session_state.report_month_filter:
                month_idx = st.session_state.report_month_filter
                filtered_df = df[pd.to_datetime(df["created_at"]).dt.month == month_idx] if "created_at" in df.columns else df
                st.markdown(f"### 📋 {months_full[month_idx-1]} Permits ({len(filtered_df)} records)")
                show_cols = [c for c in ["permit_number", "permit_type", "raised_by_name", "department", "work_location", "workflow_stage", "submitted_at"] if c in filtered_df.columns]
                st.dataframe(filtered_df[show_cols], use_container_width=True, hide_index=True)
                csv = filtered_df.to_csv(index=False)
                st.download_button(f"⬇️ Download {months_full[month_idx-1]} CSV", csv, f"permits_{months_full[month_idx-1]}.csv", "text/csv")
            
            st.markdown("---")
            
            st.markdown("### 📈 Analytics Summary")
            if "permit_type" in df.columns:
                st.markdown("**By Permit Type:**")
                for ptype, count in df["permit_type"].value_counts().items():
                    st.markdown(f"- {ptype}: **{count}**")
            if "department" in df.columns:
                st.markdown("**Top Departments:**")
                for dept, count in list(dept_data.items())[:5]:
                    st.markdown(f"- {dept}: **{count}**")
            
            st.markdown("---")
            
            st.markdown("### 📄 Generate Reports")
            report_format = st.radio("Select Format", ["📄 PDF Download", "🌐 HTML Preview & Download"], horizontal=True)
            
            if report_format == "🌐 HTML Preview & Download":
                logo_b64 = get_logo_base64()
                dept_rows = "".join([f"<tr><td>{d}</td><td>{c}</td></tr>" for d, c in list(dept_data.items())[:15]])
                stage_rows = "".join([f"<tr><td>{s.upper()}</td><td>{c}</td></tr>" for s, c in stage_data.items()])
                audit_rows = ""
                for _, row in df.iterrows():
                    stg = row.get('workflow_stage','')
                    bc = "badge-approved" if stg=="approved" else ("badge-rejected" if stg=="rejected" else "badge-pending")
                    audit_rows += f"""<tr><td>{row.get('permit_number','')}</td><td>{row.get('raised_by_name','')}</td><td>{row.get('department','')[:30]}</td><td>{format_wat_time(row.get('submitted_at',''))}</td><td>{format_wat_time(row.get('authorized_at',''))}</td><td>{format_wat_time(row.get('confirmed_at',''))}</td><td>{format_wat_time(row.get('approved_at',''))}</td><td><span class="{bc}">{stg.upper()}</span></td></tr>"""
                
                html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:'Inter',Arial,sans-serif;color:#1a1a1a;font-size:11px;margin:20px}}.header{{background:#1a1a1a;color:white;padding:20px;border-radius:10px;display:flex;align-items:center;gap:15px;margin-bottom:20px}}.header h1{{margin:0;font-size:18px}}.kpi-row{{display:flex;gap:10px;margin:15px 0}}.kpi-card{{flex:1;background:white;border:1px solid #ddd;border-radius:8px;padding:10px;text-align:center;border-left:4px solid #CC0000}}.kpi-card.green{{border-left-color:#10B981}}.kpi-val{{font-size:22px;font-weight:800}}.kpi-label{{font-size:9px;color:#666;text-transform:uppercase}}table{{width:100%;border-collapse:collapse;font-size:10px;margin:10px 0}}th{{background:#CC0000;color:white;padding:6px;text-align:left;font-size:9px}}td{{padding:5px;border-bottom:1px solid #eee}}.badge-approved{{background:#ECFDF5;color:#065F46;padding:2px 8px;border-radius:10px;font-weight:600}}.badge-pending{{background:#FFFBEB;color:#92400E;padding:2px 8px;border-radius:10px;font-weight:600}}.badge-rejected{{background:#FEF2F2;color:#991B1B;padding:2px 8px;border-radius:10px;font-weight:600}}.footer{{text-align:center;font-size:9px;color:#999;margin-top:20px;border-top:1px solid #ddd;padding-top:10px}}</style></head><body>
                <div class="header">{'<img src="data:image/png;base64,'+logo_b64+'" height="40">' if logo_b64 else ''}<div><h1>Work Permit Analytics Report</h1><p style="margin:3px 0 0 0;font-size:10px;opacity:0.8">{info.get('full_name',fc)} | {datetime.now().strftime('%d %B %Y, %I:%M %p WAT')}</p></div></div>
                <div class="kpi-row"><div class="kpi-card"><div class="kpi-val">{total}</div><div class="kpi-label">Total</div></div><div class="kpi-card green"><div class="kpi-val">{approved_count}</div><div class="kpi-label">Approved</div></div><div class="kpi-card"><div class="kpi-val">{pending_count}</div><div class="kpi-label">Pending</div></div><div class="kpi-card"><div class="kpi-val">{rejected_count}</div><div class="kpi-label">Rejected</div></div><div class="kpi-card green"><div class="kpi-val">{avg_lead:.1f}h</div><div class="kpi-label">Avg Lead</div></div></div>
                {f'<div style="background:#FFF3CD;border:1px solid #F59E0B;border-radius:8px;padding:10px;margin:10px 0"><b>DELAYED:</b> {delayed} permit(s) exceeded 4-hour target.</div>' if delayed>0 else ''}
                <h2>Department Breakdown</h2><table><tr><th>Department</th><th>Permits</th></tr>{dept_rows}</table>
                <h2>Stage Distribution</h2><table><tr><th>Stage</th><th>Count</th></tr>{stage_rows}</table>
                <h2>Audit Trail</h2><table><tr><th>Permit No</th><th>Raised By</th><th>Department</th><th>Submitted</th><th>Authorized</th><th>Confirmed</th><th>Approved</th><th>Status</th></tr>{audit_rows}</table>
                <div class="footer">Churchgate Group | facilityXperience | Confidential</div></body></html>"""
                
                st.components.v1.html(html, height=600, scrolling=True)
                st.download_button("📥 Download HTML Report", html, f"Work_Permit_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.html", "text/html", use_container_width=True, type="primary")
        
        else:
            st.info("📋 No work permits to report yet.")
    
    with tab4:
        if not is_admin:
            st.error("⛔ Admin access only")
            st.stop()
        st.markdown("### ⚙️ Workflow Configuration")
        st.caption("Manage who authorizes, confirms, and approves work permits")
        
        for level in [1, 2, 3]:
            level_names = {1: "Level 1 — Authorization (Team Lead/Supervisor)", 
                          2: "Level 2 — Confirmation (HSE Coordinator)", 
                          3: "Level 3 — Approval (Facility Manager)"}
            level_icons = {1: "🔐", 2: "✅", 3: "🟢"}
            
            st.markdown(f"**{level_icons[level]} {level_names[level]}**")
            people = get_workflow_people(fc, level)
            if people:
                for p in people:
                    dept_filter = p.get("department_filter", [])
                    if dept_filter == ["All Departments"] or not dept_filter:
                        dept_str = "All Departments"
                    else:
                        dept_str = ", ".join(dept_filter)
                    
                    st.markdown(f"""
                    <div style="background:white; border:1px solid #ddd; border-radius:8px; padding:0.6rem 1rem; margin:0.3rem 0; display:flex; align-items:center; gap:1rem;">
                        <div style="font-size:1.5rem;">👤</div>
                        <div style="flex:1;">
                            <div style="font-weight:600; font-size:0.85rem;">{p.get('person_name','')}</div>
                            <div style="font-size:0.7rem; color:#666;">📧 {p.get('person_email','')}</div>
                            <div style="font-size:0.65rem; color:#888;">🏢 {dept_str}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No people configured for this level")
            st.markdown("---")
        
        with st.form("wf_add_person"):
            st.markdown("### ➕ Add Person to Workflow")
            
            c1, c2 = st.columns(2)
            with c1:
                new_level = st.selectbox("Level", [1, 2, 3], 
                    format_func=lambda x: {1: "Level 1 — Authorization", 2: "Level 2 — Confirmation", 3: "Level 3 — Approval"}[x])
                new_name = st.text_input("Full Name*", placeholder="e.g. Francis Asuquo")
            with c2:
                new_email = st.text_input("Email Address*", placeholder="e.g. fasuquo@churchgate.com")
            
            all_departments = [
                "Engineering — Electrical", "Engineering — HVAC", "Engineering — Plumbing",
                "Engineering — Vertical Transportation (Lifts)", "Engineering — Fire Fighting",
                "Engineering — Civil & Structural", "Engineering — Utilities & Energy",
                "Engineering — Fabrication & Foundry", "Engineering — Design & Specification",
                "Facility Management — Hard Services", "Facility Management — Soft Services (Housekeeping)",
                "Facility Management — Soft Services (Waste Management)", 
                "Facility Management — Front of House & Reception",
                "Facility Management — Landscaping & Grounds", "Facility Management — Transport & Fleet",
                "Facility Management — First Aid & Clinical", "Facility Management — FM Operations & Helpdesk",
                "Facility Management — HSSE Safety & Compliance", "Facility Management — HSSE Risk & BCP",
                "Facility Management — HSSE Incident Investigation", "Facility Management — Fitout Works & Finishing",
                "Technology Group — Network & Connectivity", "Technology Group — IT Service Desk",
                "Technology Group — ERP & Business Systems", "Technology Group — Cloud & Infrastructure",
                "Technology Group — Building Technology (BMS/CCTV/ACS)", "Technology Group — Software Development",
                "Technology Group — AI & Innovation", "Technology Group — Cybersecurity",
                "Security — Man Guarding Operations", "Security — Command Center (24/7)",
                "Security — Gatehouse & Access Control", "Security — Executive Protection",
                "Procurement — Strategic Sourcing", "Procurement — Contract Management",
                "Central Stores — Inventory Management", "Central Stores — Critical Spares",
                "Sales & Marketing — Business Development", "Sales & Marketing — Bid & Tender Management",
                "Contractor — Clyde Engineering", "Contractor — Gates and Shield",
                "Contractor — TXB Enterprise Ltd", "Contractor — Brainworks", "Contractor — Metalplex",
                "Contractor — Berger Paints", "Contractor — ENI-AGIP General Services",
                "Vendor — Augkenos Options", "Vendor — Blue Group", "Vendor — T & T Synergy"
            ]
            
            new_depts = st.multiselect("Department Access (leave empty for All Departments)", 
                                       all_departments,
                                       placeholder="Choose departments or leave empty for All")
            
            if st.form_submit_button("➕ Add Person to Workflow", use_container_width=True, type="primary"):
                if new_name and new_email:
                    dept_filter = new_depts if new_depts else ["All Departments"]
                    DB.insert("workflow_config", {
                        "facility_code": fc,
                        "workflow_type": "work_permit",
                        "level_number": new_level,
                        "level_name": {1: "Authorizer", 2: "Confirmer", 3: "Approver"}[new_level],
                        "person_name": new_name,
                        "person_email": new_email,
                        "department_filter": dept_filter
                    })
                    st.success(f"✅ {new_name} added to Level {new_level}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ Name and Email are required")

# ============================================
# RAISE TICKET — AI-POWERED + MY TICKETS
# ============================================
def page_raise_ticket():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    
    st.markdown(f'## 🎫 Raise a Ticket — {info.get("full_name", fc)}')
    
    st.markdown("### 🤖 facilityXpert — AI Assistant")
    
    user_email = st.session_state.get("user", {}).get("email", "guest")
    
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []
    if "ai_conversation" not in st.session_state:
        st.session_state.ai_conversation = []
    
    if not st.session_state.ai_chat_history and user_email != "guest":
        try:
            saved = supabase.table("ai_chat_sessions").select("*").eq("user_email", user_email).order("updated_at", desc=True).limit(1).execute()
            if saved.data:
                msgs = saved.data[0].get("messages", [])
                if isinstance(msgs, str):
                    msgs = json.loads(msgs)
                st.session_state.ai_chat_history = msgs
                st.session_state.ai_conversation = msgs[-20:]
        except: pass
    
    for msg in st.session_state.ai_chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
    
    if st.session_state.ai_chat_history:
        if st.button("🗑️ Clear Chat History", key="clear_btn", use_container_width=True):
            st.session_state.ai_chat_history = []
            st.session_state.ai_conversation = []
            user_email = st.session_state.get("user", {}).get("email", "guest")
            try:
                supabase.table("ai_chat_sessions").delete().eq("user_email", user_email).execute()
            except: pass
            st.rerun()
    
    prompt = st.chat_input("Ask facilityXpert anything...", key="ai_chat_main")
    
    if prompt:
        st.session_state.ai_chat_history.append({"role": "user", "content": prompt})
        st.session_state.ai_conversation.append({"role": "user", "content": prompt})
        
        with st.spinner("🤖 Thinking..."):
            hc = DB.get_helpdesk_categories()
            cat_names_list = sorted(list(set(c.get("category_name", "") for c in hc)))
            
            try:
                api_key = st.secrets.get("GROQ_API_KEY", "")
                
                messages = [
                    {"role": "system", "content": f"""You are facilityXpert, the official AI assistant for Churchgate Group's World Trade Center in Abuja, Nigeria.

YOUR ROLE: Help tenants and staff resolve facility-related issues only.

FACILITY CONTEXT:
- World Trade Center Abuja: 22-floor Office Tower + 24-floor Residential Tower + Recreation Center
- Managed by Churchgate Group
- Departments: {cat_names_list}

GUARDRAILS - YOU MUST FOLLOW:
1. STAY ON TOPIC: Only discuss facility issues.
2. NO PERSONAL INFO: Never ask for or share personal information.
3. NO BIAS: Treat all users equally.
4. NO ADULT CONTENT: Shut down inappropriate content with: "I can only assist with facility-related questions."
5. NO FAKE INFO: Never invent ticket numbers, phone numbers, or emails.
6. EMERGENCIES: For fire, flood, elevator stuck, electrical hazards - instruct them to call facility emergency or visit reception immediately.
7. BE PROFESSIONAL: Clear, polite, professional language.

CRITICAL RULE - TICKET FORM IS ON THIS PAGE:
When a user needs to raise a ticket, ALWAYS say: "Please scroll down to the 'Raise New Ticket' form on this page and submit your request. Select the [category name] category."
NEVER tell them to visit a website or call a number. The ticket form is RIGHT HERE on this page.

RESPONSE FORMAT: Give practical step-by-step troubleshooting first. If unresolved, direct to the Raise New Ticket form below."""}
                ]
                messages.extend(st.session_state.ai_conversation[-15:])
                
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={"model": "llama-3.1-8b-instant", "messages": messages, "max_tokens": 300, "temperature": 0.5},
                    timeout=15
                )
                
                if response.status_code == 200:
                    ai_response = response.json()["choices"][0]["message"]["content"]
                else:
                    ai_response = None
            except:
                ai_response = None
                kb = supabase.table("knowledge_base").select("*").or_(f"question.ilike.%{prompt}%,tags.ilike.%{prompt}%").limit(3).execute()
                if kb.data:
                    ai_response = "Solutions from knowledge base:\n\n" + "\n\n".join([f"**{k.get('question')}**\n{k.get('answer','')}" for k in kb.data])
                else:
                    ai_response = "I couldn't find a solution. Please raise a ticket."
            
            st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_response})
            st.session_state.ai_conversation.append({"role": "assistant", "content": ai_response})
            
            try:
                supabase.table("ai_chat_sessions").upsert({
                    "user_email": user_email,
                    "session_id": f"{user_email}_{datetime.now().strftime('%Y%m%d')}",
                    "messages": st.session_state.ai_chat_history,
                    "updated_at": datetime.now().isoformat()
                }).execute()
            except: pass
            
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 Raise New Ticket")
    
    buildings = DB.get_locations(fc)
    building_options = {}
    for b in buildings:
        building_options[b.get("location_code", "")] = b.get("location_name", "")
    if not building_options:
        building_options = {"CT": "CT — Office Tower", "SAT": "SAT — Residential Tower", "RC": "RC — Recreation Center", "IP": "IP — Intermediate Parking"}
    
    c1, c2 = st.columns(2)
    with c1:
        selected_building = st.selectbox("Building*", options=list(building_options.keys()), format_func=lambda x: building_options.get(x, x), key="rt_building")
        sub_locs = get_sub_locations_for_building(fc, selected_building)
        if not sub_locs: sub_locs = [f"{selected_building} / 0"]
        sub_location = st.selectbox("Sub-Location*", sub_locs, key="rt_subloc")
    with c2:
        categories = DB.get_helpdesk_categories()
        cat_names = sorted(list(set(c.get("category_name", "") for c in categories)))
        category = st.selectbox("Category*", cat_names)
    
    full_location = f"{building_options.get(selected_building, selected_building)} → {sub_location}"
    
    with st.form("raise_ticket_form", clear_on_submit=True):
        title = st.text_input("Title*", placeholder="Brief description of the issue")
        description = st.text_area("Description*", height=100, placeholder="Describe the issue in detail...")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
            occupant = st.text_input("Occupant/Tenant (if applicable)")
        with c2:
            requester_name = st.text_input("Your Name*")
            requester_email = st.text_input("Your Email")
        with c3:
            requester_phone = st.text_input("Your Phone")
            image = st.file_uploader("Image (Optional)", type=["png", "jpg", "jpeg"])
        
        submitted = st.form_submit_button("🎫 Submit Ticket", use_container_width=True, type="primary")
        
        if submitted:
            if not title or not description or not requester_name:
                st.error("⚠️ Title, Description, and Name are required")
            else:
                cnt = len(DB.get_all("tickets", fc, 1000))
                ticket_number = f"TKT-{fc}-{datetime.now().strftime('%d%H%M%S')}"
                
                sla_hours = 4
                ticket_dept = ""
                for c in categories:
                    if c.get("category_name") == category:
                        sla_hours = c.get("sla_hours", 4)
                        ticket_dept = c.get("department", "")
                        break
                sla_deadline = (datetime.now() + timedelta(hours=sla_hours)).isoformat()
                
                DB.insert("tickets", {
                    "facility_code": fc, "ticket_number": ticket_number, "title": title,
                    "description": description, "category": category, "priority": priority,
                    "status": "open", "requester_name": requester_name,
                    "requester_email": requester_email, "requester_phone": requester_phone,
                    "occupant_name": occupant, "location_building": full_location,
                    "sla_deadline": sla_deadline, "escalation_level": 1,
                    "created_at": datetime.now().isoformat()
                })
                
                authorizers = get_workflow_people(fc, 1, ticket_dept)
                for a in authorizers:
                    send_email_notification(
                        a.get("person_email", ""),
                        f"🎫 New Ticket {ticket_number} — {category}",
                        f"<h3>New Helpdesk Ticket</h3>"
                        f"<p><b>Ticket:</b> {ticket_number}</p>"
                        f"<p><b>Category:</b> {category}</p>"
                        f"<p><b>Priority:</b> {priority}</p>"
                        f"<p><b>Location:</b> {full_location}</p>"
                        f"<p><b>Raised by:</b> {requester_name}</p>"
                        f"<p><b>Description:</b> {description[:300]}</p>"
                        f"<p>SLA Deadline: {sla_deadline}</p>"
                    )
                
                st.success(f"✅ Ticket {ticket_number} raised successfully!")
                st.balloons()
                time.sleep(1.5)
                
                ticket_cat_id = None
                for c in categories:
                    if c.get("category_name") == category:
                        ticket_cat_id = c["id"]
                        break
                
                esc_data = supabase.table("ticket_escalation").select("*").eq("facility_code", fc).eq("level_number", 1).eq("category_id", ticket_cat_id).execute()
                if esc_data.data:
                    for e in esc_data.data:
                        if e.get("escalate_to_email"):
                            send_email_notification(
                                e["escalate_to_email"],
                                f"🎫 New Ticket #{ticket_number} — {category}",
                                f"""
                                <div style="font-family:Arial;max-width:600px;margin:0 auto;border:1px solid #ddd;border-radius:8px;overflow:hidden;">
                                    <div style="background:#CC0000;padding:20px;color:white;">
                                        <h2 style="margin:0;">facilityXperience</h2>
                                        <p style="margin:5px 0 0 0;font-size:12px;opacity:0.9;">Churchgate Group — {info.get('full_name',fc)}</p>
                                    </div>
                                    <div style="padding:20px;">
                                        <h3 style="color:#1a1a1a;">New Helpdesk Ticket</h3>
                                        <table style="width:100%;border-collapse:collapse;font-size:13px;">
                                            <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold;">Ticket No:</td><td style="padding:8px;border-bottom:1px solid #eee;">{ticket_number}</td></tr>
                                            <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold;">Category:</td><td style="padding:8px;border-bottom:1px solid #eee;">{category}</td></tr>
                                            <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold;">Priority:</td><td style="padding:8px;border-bottom:1px solid #eee;"><span style="background:{'#EF4444' if priority=='critical' else '#F59E0B' if priority=='high' else '#3B82F6'};color:white;padding:2px 10px;border-radius:10px;font-size:11px;">{priority.upper()}</span></td></tr>
                                            <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold;">Location:</td><td style="padding:8px;border-bottom:1px solid #eee;">{full_location}</td></tr>
                                            <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold;">Raised by:</td><td style="padding:8px;border-bottom:1px solid #eee;">{requester_name}</td></tr>
                                            <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold;">SLA Deadline:</td><td style="padding:8px;border-bottom:1px solid #eee;">{sla_deadline[:16] if sla_deadline else 'N/A'}</td></tr>
                                        </table>
                                        <div style="background:#f5f5f5;padding:15px;border-radius:8px;margin-top:15px;">
                                            <p style="margin:0;font-weight:bold;">Description:</p>
                                            <p style="margin:5px 0 0 0;color:#666;">{description[:300]}</p>
                                        </div>
                                        <div style="margin-top:20px;padding:15px;background:#FFF3CD;border-radius:8px;">
                                            <p style="margin:0;font-weight:bold;color:#92400E;">⚡ Action Required:</p>
                                            <p style="margin:5px 0 0 0;color:#92400E;">Please review and take action on this ticket. SLA timer has started.</p>
                                        </div>
                                        <div style="margin-top:15px;text-align:center;">
                                            <a href="https://facilityxperience.streamlit.app" style="background:#CC0000;color:white;padding:10px 25px;text-decoration:none;border-radius:6px;font-weight:bold;">View in facilityXperience</a>
                                        </div>
                                    </div>
                                    <div style="background:#f9f9f9;padding:12px;text-align:center;font-size:10px;color:#999;">
                                        Churchgate Group | facilityXperience | This is an automated notification
                                    </div>
                                </div>
                                """
                            )
    
    st.markdown("---")
    st.markdown("### 📋 My Tickets")
    
    user_name = st.session_state.get('user_name', '')
    user_email_val = st.session_state.get('user', {}).get('email', '')
    
    my_tickets = supabase.table("tickets").select("*").eq("facility_code", fc).or_(f"requester_name.eq.{user_name},requester_email.eq.{user_email_val}").order("created_at", desc=True).limit(20).execute()
    if my_tickets.data:
        for t in my_tickets.data:
            status = t.get("status", "open")
            colors = {"open":"#EF4444","in_progress":"#F59E0B","hold":"#3B82F6","closed":"#10B981","rejected":"#6B7280"}
            icons = {"open":"🔴","in_progress":"🟡","hold":"⏸️","closed":"🟢","rejected":"❌"}
            sc = colors.get(status,"#4a4a4a")
            si = icons.get(status,"📋")
            
            created = t.get("created_at","")
            age_str = ""
            if created and str(created) != "None":
                try:
                    age = datetime.now() - pd.to_datetime(created)
                    age_str = f"{age.days}d {age.seconds//3600}h ago"
                except: pass
            
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:0.8rem;margin:0.4rem 0;border-left:4px solid {sc};box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span><b>{si} {t.get('ticket_number','')}</b></span>
                    <span style="background:{sc};color:white;padding:2px 10px;border-radius:12px;font-size:0.65rem;font-weight:600;">{status.upper()}</span>
                </div>
                <div style="font-size:0.8rem;color:#1a1a1a;margin-top:0.3rem;">{t.get('title','')[:80]}</div>
                <div style="font-size:0.65rem;color:#888;margin-top:0.2rem;">🏷️ {t.get('category','')} | 📍 {t.get('location_building','')[:30]} | ⏱️ {age_str}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if t.get("status") == "closed":
                if not t.get("satisfaction_rating"):
                    rating = st.slider("Rate your experience", 1, 5, 5, key=f"rate_{t['id']}")
                    if st.button("⭐ Submit Rating", key=f"submit_rate_{t['id']}"):
                        DB.update("tickets", t["id"], {"satisfaction_rating": rating})
                        st.success("Thank you!")
                        st.rerun()
                else:
                    st.markdown(f"**Your Rating:** {'⭐' * t.get('satisfaction_rating', 0)}")
    else:
        st.info("No tickets raised yet")

def page_helpdesk_queue():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    user_role = st.session_state.get("user_role", "staff")
    is_admin = user_role in ["admin", "approver"]
    
    st.markdown(f'## 💬 Helpdesk — {info.get("full_name", fc)}')
    
    categories = DB.get_helpdesk_categories()
    
    nav_tabs = ["🏠 Home", "📊 AI Analytics", "📄 Reports", "⏱️ Escalation", "⚙️ Settings"]
    tabs = st.tabs(nav_tabs)
    
    # ============================================
    # TAB 0: HOME — TICKET QUEUE (FULL)
    # ============================================
    with tabs[0]:
        statuses = ["All", "Open", "In Progress", "Hold", "Closed", "Rejected"]
        status_icons = {"All": "📋", "Open": "🔴", "In Progress": "🟡", "Hold": "⏸️", "Closed": "🟢", "Rejected": "❌"}
        status_colors = {"All": "#4a4a4a", "Open": "#EF4444", "In Progress": "#F59E0B", "Hold": "#3B82F6", "Closed": "#10B981", "Rejected": "#6B7280"}
        
        if "ticket_status_filter" not in st.session_state:
            st.session_state.ticket_status_filter = "All"
        
        # Status Filter Buttons with visual indicators
        cols = st.columns(6)
        for i, status in enumerate(statuses):
            with cols[i]:
                active = st.session_state.ticket_status_filter == status
                bg = status_colors[status] if active else "white"
                tc = "white" if active else "#1a1a1a"
                st.markdown(f"""<div style="background:{bg};border:2px solid {status_colors[status]};border-radius:12px;padding:0.6rem;text-align:center;color:{tc};font-weight:600;font-size:0.8rem;">{status_icons[status]} {status}</div>""", unsafe_allow_html=True)
                if st.button(f"{status}", key=f"st_{status}", use_container_width=True):
                    st.session_state.ticket_status_filter = status
                    st.rerun()
        
        st.markdown("---")
        
        # Search bar
        search = st.text_input("🔍 Search tickets", placeholder="Search by title, ID, or requester...", key="hd_search")
        
        status_filter = st.session_state.ticket_status_filter
        filter_status = status_filter.lower().replace(" in progress", "in_progress") if status_filter != "All" else None
        tickets = DB.get_tickets_filtered(fc, status=filter_status, search=search if search else None)
        
        # Department-based filtering (non-admin users see only their department tickets)
        user_depts = safe_parse_permissions(st.session_state.get("user", {}).get("department_permissions", []))
        can_see_all = user_role in ["admin", "approver", "confirmer"]
        if tickets and not can_see_all and user_depts:
            filtered = []
            for t in tickets:
                for c in categories:
                    if c.get("category_name") == t.get("category","") and c.get("department") in user_depts:
                        filtered.append(t)
                        break
            tickets = filtered
        
        if tickets:
            df = pd.DataFrame(tickets)
            
            # KPI Cards Row
            kpi_cols = st.columns(6)
            kpi_data = [
                ("📋 Total", len(df), "#4a4a4a"),
                ("🔴 Open", len(df[df["status"]=="open"]) if "status" in df.columns else 0, "#EF4444"),
                ("🟡 In Progress", len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0, "#F59E0B"),
                ("⏸️ Hold", len(df[df["status"]=="hold"]) if "status" in df.columns else 0, "#3B82F6"),
                ("🟢 Closed", len(df[df["status"]=="closed"]) if "status" in df.columns else 0, "#10B981"),
                ("❌ Rejected", len(df[df["status"]=="rejected"]) if "status" in df.columns else 0, "#6B7280")
            ]
            for i, (label, value, color) in enumerate(kpi_data):
                with kpi_cols[i]:
                    st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;border-left:4px solid {color};box-shadow:0 1px 3px rgba(0,0,0,0.06);"><div style="font-size:0.65rem;color:#888;">{label}</div><div style="font-size:1.6rem;font-weight:800;">{value}</div></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            
            if "open_ticket_detail" not in st.session_state:
                st.session_state.open_ticket_detail = None
            
            # Ticket Cards with Expandable Details
            for i, row in df.iterrows():
                status = row.get("status", "open")
                created = row.get("created_at", "")
                age_str = ""
                if created:
                    try:
                        created_dt = pd.to_datetime(created)
                        age = datetime.now() - created_dt
                        age_str = f"{age.days}d {age.seconds//3600}h"
                    except: pass
                
                sc = status_colors.get(status, "#4a4a4a")
                si = status_icons.get(status, "📋")
                ticket_id = row["id"]
                is_open = st.session_state.open_ticket_detail == ticket_id
                
                with st.container():
                    # Ticket Card Header
                    st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;margin:0.4rem 0;border-left:4px solid {sc};box-shadow:0 1px 3px rgba(0,0,0,0.04);"><div style="display:flex;justify-content:space-between;"><span><b>{si} {row.get('ticket_number','')}</b> — {row.get('requester_name','N/A')}</span><span style="font-size:0.7rem;color:#888;">⏱️ {age_str}</span></div><div style="margin-top:0.2rem;font-size:0.8rem;">{row.get('title','')[:100]}</div><div style="font-size:0.65rem;color:#888;">📍 {row.get('location_building','')[:40] if row.get('location_building') else 'N/A'} | 🏷️ {row.get('category','')} | L{row.get('escalation_level',1)}</div></div>""", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        new_comment = st.text_input("Quick Note", key=f"cmt_{row['id']}", placeholder="Add progress note...")
                    with c2:
                        btn_label = "🔼 Hide" if is_open else "📋 Details"
                        if st.button(btn_label, key=f"vdet_{row['id']}", use_container_width=True):
                            if is_open:
                                st.session_state.open_ticket_detail = None
                            else:
                                st.session_state.open_ticket_detail = ticket_id
                            st.rerun()
                    
                    # EXPANDED DETAIL VIEW
                    if is_open:
                        with st.container():
                            st.markdown(f"""<div style="background:#f9fafb;border-radius:10px;padding:1rem;margin:0.5rem 0;border:1px solid #e5e7eb;"><h4 style="margin:0;">{row.get('title','')}</h4><p style="color:#666;font-size:0.8rem;"><b>Ticket:</b> {row.get('ticket_number','')} | <b>Status:</b> {status.upper()} | <b>Level:</b> L{row.get('escalation_level',1)}</p><p style="font-size:0.8rem;"><b>Raised by:</b> {row.get('requester_name','N/A')} | <b>Category:</b> {row.get('category','')} | <b>Priority:</b> {row.get('priority','')}</p><p style="font-size:0.8rem;"><b>Location:</b> {row.get('location_building','')}</p><p style="font-size:0.8rem;"><b>Description:</b> {row.get('description','')}</p><p style="font-size:0.75rem;color:#888;"><b>SLA:</b> {format_wat_time(row.get('sla_deadline',''))}</p></div>""", unsafe_allow_html=True)
                            
                            # Progress Log / Comments
                            comments = DB.get_ticket_comments(ticket_id)
                            if comments:
                                st.caption("📝 Progress Log:")
                                for c in comments:
                                    st.caption(f"👤 {c.get('user_name','')} — {c.get('created_at','')[:16]}: {c.get('comment_text','')}")
                            
                            st.markdown("**⚡ Actions:**")
                            
                            if status in ["open", "in_progress", "hold"]:
                                # Action buttons row 1
                                ac1, ac2, ac3 = st.columns(3)
                                with ac1:
                                    if st.button("🔄 Update", key=f"det_upd_{ticket_id}", use_container_width=True):
                                        if new_comment:
                                            DB.insert("ticket_comments", {"ticket_id": ticket_id, "user_name": st.session_state.get("user_name","Staff"), "comment_text": new_comment})
                                            DB.update("tickets", ticket_id, {"status": "in_progress"})
                                            st.success("✅ Updated!")
                                            st.rerun()
                                with ac2:
                                    if st.button("⏸️ Hold", key=f"det_hold_{ticket_id}", use_container_width=True):
                                        DB.update("tickets", ticket_id, {"status": "hold"})
                                        st.success("⏸️ On Hold")
                                        st.rerun()
                                with ac3:
                                    if st.button("✅ Close", key=f"det_close_{ticket_id}", use_container_width=True):
                                        DB.update("tickets", ticket_id, {"status": "closed", "closed_at": datetime.now().isoformat()})
                                        if row.get("requester_email"):
                                            send_email_notification(row["requester_email"], f"✅ Ticket {row.get('ticket_number','')} Resolved", f"<h3>Ticket Resolved</h3><p>Your ticket has been resolved. Please rate your experience.</p>")
                                        st.success("✅ Closed!")
                                        st.balloons()
                                        st.rerun()
                                
                                # Action buttons row 2
                                ac4, ac5, ac6 = st.columns(3)
                                with ac4:
                                    if st.button("❌ Reject", key=f"det_rej_{ticket_id}", use_container_width=True):
                                        DB.update("tickets", ticket_id, {"status": "rejected"})
                                        st.error("Ticket rejected")
                                        st.rerun()
                                with ac5:
                                    if st.button("🔄 Re-Assign", key=f"det_reassign_{ticket_id}", use_container_width=True):
                                        st.session_state.reassign_ticket = ticket_id
                                        st.rerun()
                                with ac6:
                                    if st.button("ℹ️ More Info", key=f"det_more_{ticket_id}", use_container_width=True):
                                        st.session_state.more_info_ticket = ticket_id
                                        st.rerun()
                                
                                # Re-Assign Form
                                if "reassign_ticket" in st.session_state and st.session_state.reassign_ticket == ticket_id:
                                    all_users = DB.get_users()
                                    user_names = [u.get("name","") for u in all_users]
                                    reassign_to = st.selectbox("Re-assign to", user_names, key=f"reassign_{ticket_id}")
                                    c1, c2 = st.columns(2)
                                    with c1:
                                        if st.button("✅ Confirm Re-Assign", key=f"confirm_reassign_{ticket_id}", use_container_width=True):
                                            DB.update("tickets", ticket_id, {"assigned_to": reassign_to})
                                            DB.insert("ticket_comments", {"ticket_id": ticket_id, "user_name": st.session_state.get("user_name","Staff"), "comment_text": f"Re-assigned to {reassign_to}"})
                                            if row.get("requester_email"):
                                                send_email_notification(row["requester_email"], f"🔄 Ticket {row.get('ticket_number','')} Re-Assigned", f"<h3>Ticket Re-Assigned</h3><p>Your ticket has been re-assigned to {reassign_to}.</p>")
                                            st.success(f"✅ Re-assigned to {reassign_to}!")
                                            st.session_state.reassign_ticket = None
                                            st.rerun()
                                    with c2:
                                        if st.button("❌ Cancel", key=f"cancel_reassign_{ticket_id}", use_container_width=True):
                                            st.session_state.reassign_ticket = None
                                            st.rerun()
                                
                                # More Info Form
                                if "more_info_ticket" in st.session_state and st.session_state.more_info_ticket == ticket_id:
                                    more_info_note = st.text_area("Request more information", key=f"more_info_{ticket_id}", height=60, placeholder="What additional information do you need?")
                                    c1, c2 = st.columns(2)
                                    with c1:
                                        if st.button("📩 Request Info", key=f"send_more_{ticket_id}", use_container_width=True):
                                            if more_info_note:
                                                DB.insert("ticket_comments", {"ticket_id": ticket_id, "user_name": st.session_state.get("user_name","Staff"), "comment_text": f"INFO REQUESTED: {more_info_note}"})
                                                if row.get("requester_email"):
                                                    send_email_notification(row["requester_email"], f"ℹ️ More Info Requested - Ticket {row.get('ticket_number','')}", f"<h3>Additional Information Requested</h3><p><b>Ticket:</b> {row.get('ticket_number','')}</p><p><b>Request:</b> {more_info_note}</p><p>Please respond with the requested information.</p>")
                                                st.success("✅ Info request sent!")
                                                st.session_state.more_info_ticket = None
                                                st.rerun()
                                    with c2:
                                        if st.button("❌ Cancel", key=f"cancel_more_{ticket_id}", use_container_width=True):
                                            st.session_state.more_info_ticket = None
                                            st.rerun()
                                
                                # Escalate (Admin only)
                                if is_admin:
                                    esc_level = row.get("escalation_level", 1)
                                    if esc_level < 6:
                                        if st.button(f"🔺 Escalate L{esc_level}→L{esc_level+1}", key=f"det_esc_{ticket_id}", use_container_width=True):
                                            DB.update("tickets", ticket_id, {"escalation_level": esc_level + 1})
                                            st.success(f"🔺 Escalated to Level {esc_level + 1}!")
                                            st.rerun()
                            
                            # Re-Open closed tickets
                            if status == "closed":
                                if st.button("🔄 Re-Open", key=f"det_reopen_{ticket_id}", use_container_width=True):
                                    DB.update("tickets", ticket_id, {"status": "open"})
                                    st.success("🔄 Re-opened!")
                                    st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No tickets found matching your filters")
    
    # ============================================
    # TAB 1: AI-POWERED ANALYTICS (FULL)
    # ============================================
    with tabs[1]:
        st.markdown("### 📊 AI-Powered Helpdesk Analytics")
        
        all_tickets = DB.get_all("tickets", fc, 500)
        if all_tickets:
            df = pd.DataFrame(all_tickets)
            
            total = len(df)
            open_count = len(df[df["status"]=="open"]) if "status" in df.columns else 0
            in_progress = len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0
            hold_count = len(df[df["status"]=="hold"]) if "status" in df.columns else 0
            closed_count = len(df[df["status"]=="closed"]) if "status" in df.columns else 0
            rejected_count = len(df[df["status"]=="rejected"]) if "status" in df.columns else 0
            
            resolution_times = []
            if "created_at" in df.columns and "closed_at" in df.columns:
                for _, r in df.iterrows():
                    try:
                        closed_val = r.get("closed_at")
                        if closed_val and str(closed_val) != "None" and str(closed_val) != "nan" and str(closed_val) != "":
                            created = pd.to_datetime(r["created_at"])
                            closed = pd.to_datetime(closed_val)
                            hrs = (closed - created).total_seconds() / 3600
                            if hrs > 0:
                                resolution_times.append(hrs)
                    except: pass
            avg_resolution = round(sum(resolution_times) / len(resolution_times), 1) if resolution_times else 0
            avg_display = f"{avg_resolution}h" if avg_resolution > 0 else "N/A"
            
            sla_met = 0
            sla_exceeded = 0
            if "sla_deadline" in df.columns and "closed_at" in df.columns:
                for _, r in df.iterrows():
                    try:
                        closed_val = r.get("closed_at")
                        if closed_val and str(closed_val) != "None" and str(closed_val) != "nan" and r.get("sla_deadline"):
                            if pd.to_datetime(closed_val) <= pd.to_datetime(r["sla_deadline"]):
                                sla_met += 1
                            else:
                                sla_exceeded += 1
                    except: pass
            
            frt_met = 0
            if "created_at" in df.columns:
                for _, r in df.iterrows():
                    try:
                        if r.get("created_at"):
                            comments = DB.get_ticket_comments(r.get("id"))
                            if comments and len(comments) > 0:
                                first_comment = pd.to_datetime(comments[0].get("created_at"))
                                created = pd.to_datetime(r["created_at"])
                                if (first_comment - created).total_seconds() / 60 <= 30:
                                    frt_met += 1
                    except: pass
            
            priority_breakdown = df["priority"].value_counts().to_dict() if "priority" in df.columns else {}
            critical_high = priority_breakdown.get("critical", 0) + priority_breakdown.get("high", 0)
            backlog = open_count + in_progress + hold_count
            rate = round((closed_count/total)*100) if total > 0 else 0
            
            overdue = 0
            if "sla_deadline" in df.columns:
                now = datetime.now()
                for _, r in df.iterrows():
                    try:
                        if pd.to_datetime(r["sla_deadline"]) < now and r.get("status") not in ["closed","rejected"]:
                            overdue += 1
                    except: pass
            
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1: st.metric("📋 Total", total)
            with c2: st.metric("🔴 Open", open_count)
            with c3: st.metric("🟡 In Progress", in_progress)
            with c4: st.metric("⏸️ Hold", hold_count)
            with c5: st.metric("🟢 Closed", closed_count)
            with c6: st.metric("⏱️ Avg Resolution", avg_display)
            
            st.markdown("---")
            
            st.markdown("#### ⏱️ SLA Compliance")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("✅ SLA Met", sla_met)
                st.progress(sla_met / total if total > 0 else 0, text=f"{sla_met}/{total}")
            with c2:
                st.metric("⚠️ SLA Exceeded", sla_exceeded)
                st.progress(sla_exceeded / total if total > 0 else 0, text=f"{sla_exceeded}/{total}")
            
            st.markdown("---")
            
            c1, c2 = st.columns(2)
            with c1:
                if "category" in df.columns:
                    cat_counts = df["category"].value_counts().head(10)
                    fig = px.bar(x=cat_counts.index, y=cat_counts.values, title="📊 Tickets by Category", color=cat_counts.values, color_continuous_scale="Reds")
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
            with c2:
                if "status" in df.columns:
                    st_counts = df["status"].value_counts()
                    colors_map = {"open":"#EF4444","in_progress":"#F59E0B","hold":"#3B82F6","closed":"#10B981","rejected":"#6B7280"}
                    pie_colors = [colors_map.get(s,"#999") for s in st_counts.index]
                    fig2 = px.pie(values=st_counts.values, names=st_counts.index, title="📈 Status Distribution", color_discrete_sequence=pie_colors)
                    fig2.update_layout(height=350)
                    st.plotly_chart(fig2, use_container_width=True)
            
            if "created_at" in df.columns:
                df["month"] = pd.to_datetime(df["created_at"]).dt.month
                df["month_name"] = df["month"].apply(lambda x: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][x-1])
                monthly = df.groupby("month_name").size().reset_index(name="count")
                fig3 = px.line(monthly, x="month_name", y="count", title="📈 Monthly Ticket Volume", markers=True, line_shape="spline")
                fig3.update_layout(height=300)
                st.plotly_chart(fig3, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 🏢 Executive KPI Dashboard")
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("🔥 Critical/High", critical_high)
                st.caption("Urgent tickets")
            with c2:
                st.metric("📈 Resolution Rate", f"{rate}%")
                st.caption("Tickets resolved")
            with c3:
                st.metric("⏱️ First Response SLA", f"{frt_met}/{total}")
                st.caption("Acknowledged within 30m")
            with c4:
                st.metric("📋 Current Backlog", backlog)
                st.caption("Awaiting resolution")
            
            st.markdown("---")
            st.markdown("#### 📊 Department Performance")
            dept_performance = {}
            if "category" in df.columns:
                for _, r in df.iterrows():
                    cat = r.get("category","Unknown")
                    if cat not in dept_performance:
                        dept_performance[cat] = {"total": 0, "closed": 0}
                    dept_performance[cat]["total"] += 1
                    if r.get("status") == "closed":
                        dept_performance[cat]["closed"] += 1
            
            if dept_performance:
                dept_df = pd.DataFrame([
                    {"Department": k, "Total": v["total"], "Closed": v["closed"],
                     "Resolution Rate": f"{round((v['closed']/v['total'])*100)}%" if v['total'] > 0 else "0%"}
                    for k, v in dept_performance.items()
                ]).sort_values("Total", ascending=False)
                st.dataframe(dept_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("#### 🤖 AI Insights")
            
            c1, c2 = st.columns(2)
            with c1:
                if overdue > 0:
                    st.error(f"🔴 {overdue} tickets past SLA deadline")
                if open_count > 0:
                    st.warning(f"📋 {open_count} open tickets pending")
                if avg_resolution > 4:
                    st.info(f"⏱️ Avg resolution ({avg_display}) exceeds 4h target")
                else:
                    st.success(f"✅ Avg resolution ({avg_display}) within target")
            with c2:
                if "category" in df.columns and len(df["category"].value_counts()) > 0:
                    top_cat = df["category"].value_counts().index[0]
                    st.info(f"📈 Most reported: **{top_cat}**")
                if rate >= 80:
                    st.success(f"✅ Resolution rate {rate}% meets target")
                else:
                    st.warning(f"⚠️ Resolution rate {rate}% below 80% target")
        else:
            st.info("No ticket data available for analytics")
    
    # ============================================
    # TAB 2: PROFESSIONAL REPORTS (FULL)
    # ============================================
    with tabs[2]:
        st.markdown("### 📄 Helpdesk Reports")
        
        rpt_type = st.selectbox("Report Type", ["Monthly Report", "Customized Report", "Tickets Carry Forward"])
        
        all_tickets = DB.get_all("tickets", fc, 500)
        occupant_options = ["All Occupants", "Internal Team"] + sorted(list(set(
            t.get("occupant_name","") for t in all_tickets if t.get("occupant_name") and str(t.get("occupant_name")) != "None"
        )))
        cat_options = ["All"] + sorted(list(set(c.get("category_name","") for c in categories)))
        status_options = ["All", "open", "in_progress", "hold", "closed", "rejected"]
        
        rpt_month = "Custom"
        rpt_year = ""
        
        if rpt_type == "Monthly Report":
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                rpt_month = st.selectbox("Month", ["January","February","March","April","May","June","July","August","September","October","November","December"])
            with c2:
                rpt_year = st.selectbox("Year", [2024,2025,2026,2027])
            with c3:
                rpt_occupant = st.selectbox("Select Occupant", occupant_options)
            with c4:
                rpt_category = st.selectbox("Category", cat_options)
            rpt_status = st.selectbox("Select Status", status_options)
            
        elif rpt_type == "Customized Report":
            c1, c2 = st.columns(2)
            with c1:
                date_from = st.date_input("From", date.today().replace(day=1))
            with c2:
                date_to = st.date_input("To", date.today())
            c1, c2, c3 = st.columns(3)
            with c1:
                rpt_occupant = st.selectbox("Select Occupant", occupant_options, key="cust_occ")
            with c2:
                rpt_category = st.selectbox("Category", cat_options, key="cust_cat")
            with c3:
                rpt_status = st.selectbox("Select Status", status_options, key="cust_status")
            
        else:
            rpt_year = st.selectbox("Select Year", [2024,2025,2026,2027], key="tcf_year")
            c1, c2, c3 = st.columns(3)
            with c1:
                rpt_occupant = st.selectbox("Select Occupant", occupant_options, key="tcf_occ")
            with c2:
                rpt_category = st.selectbox("Category", cat_options, key="tcf_cat")
            with c3:
                rpt_status = st.selectbox("Select Status", status_options, key="tcf_status")
            rpt_month = "Carry Forward"
        
        if st.button("📊 Generate Report", use_container_width=True, type="primary"):
            if all_tickets:
                df = pd.DataFrame(all_tickets)
                
                if rpt_month not in ["Custom", "Carry Forward"]:
                    month_map = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
                    month_num = month_map.get(rpt_month, 0)
                    if month_num > 0 and "created_at" in df.columns:
                        df = df[pd.to_datetime(df["created_at"]).dt.month == month_num]
                    if rpt_year and "created_at" in df.columns:
                        df = df[pd.to_datetime(df["created_at"]).dt.year == rpt_year]
                
                if rpt_type == "Customized Report" and "created_at" in df.columns:
                    df = df[(pd.to_datetime(df["created_at"]).dt.date >= date_from) & (pd.to_datetime(df["created_at"]).dt.date <= date_to)]
                
                if rpt_type == "Tickets Carry Forward" and rpt_year and "created_at" in df.columns:
                    df = df[pd.to_datetime(df["created_at"]).dt.year <= rpt_year]
                
                if rpt_occupant != "All Occupants":
                    if rpt_occupant == "Internal Team":
                        external_companies = ["AGIP","Optiva","Heritage","Periscope","Maroto","Seplat","Handy","Aselsan","First E&P","Microsoft","Lighthouse","General Electric","Dell","Access Bank","TotalEnergies"]
                        df = df[~df["occupant_name"].str.contains('|'.join(external_companies), case=False, na=False)]
                    else:
                        df = df[df["occupant_name"] == rpt_occupant]
                
                if rpt_category != "All":
                    df = df[df["category"] == rpt_category]
                
                if rpt_status != "All":
                    df = df[df["status"] == rpt_status]
                
                if len(df) == 0:
                    st.warning("No tickets match your filters")
                else:
                    total = len(df)
                    open_count_rpt = len(df[df["status"]=="open"]) if "status" in df.columns else 0
                    in_progress_rpt = len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0
                    hold_count_rpt = len(df[df["status"]=="hold"]) if "status" in df.columns else 0
                    closed_count_rpt = len(df[df["status"]=="closed"]) if "status" in df.columns else 0
                    
                    resolution_times_rpt = []
                    if "created_at" in df.columns and "closed_at" in df.columns:
                        for _, r in df.iterrows():
                            try:
                                closed_val = r.get("closed_at")
                                if closed_val and str(closed_val) != "None" and str(closed_val) != "nan" and str(closed_val) != "":
                                    hrs = (pd.to_datetime(closed_val) - pd.to_datetime(r["created_at"])).total_seconds() / 3600
                                    if hrs > 0: resolution_times_rpt.append(hrs)
                            except: pass
                    avg_resolution_rpt = round(sum(resolution_times_rpt) / len(resolution_times_rpt), 1) if resolution_times_rpt else 0
                    avg_display_rpt = f"{avg_resolution_rpt}h" if avg_resolution_rpt > 0 else "N/A"
                    
                    st.success(f"✅ Report generated — {total} tickets")
                    
                    c1, c2, c3, c4, c5, c6 = st.columns(6)
                    with c1: st.metric("📋 Total", total)
                    with c2: st.metric("🔴 Open", open_count_rpt)
                    with c3: st.metric("🟡 In Progress", in_progress_rpt)
                    with c4: st.metric("⏸️ Hold", hold_count_rpt)
                    with c5: st.metric("🟢 Closed", closed_count_rpt)
                    with c6: st.metric("⏱️ Avg Resolution", avg_display_rpt)
                    
                    st.markdown("---")
                    st.markdown("### 📋 Detailed Ticket Report")
                    
                    table_data = []
                    for _, r in df.iterrows():
                        created = str(r.get('created_at',''))[:16] if r.get('created_at') and str(r.get('created_at')) != "None" else "—"
                        closed_val = r.get('closed_at')
                        closed = str(closed_val)[:16] if closed_val and str(closed_val) != "None" and str(closed_val) != "nan" else "Pending"
                        
                        age_str = "—"
                        if r.get('created_at') and str(r.get('created_at')) != "None":
                            try:
                                created_dt = pd.to_datetime(r['created_at'])
                                end_dt = pd.to_datetime(r['closed_at']) if r.get('closed_at') and str(r.get('closed_at')) != "None" and str(r.get('closed_at')) != "nan" else datetime.now()
                                age = end_dt - created_dt
                                age_str = f"{age.days}d {age.seconds//3600}h"
                            except: pass
                        
                        table_data.append({
                            "SNo": len(table_data) + 1,
                            "DateTime": created,
                            "Ticket No": safe_text(r.get('ticket_number',''),"—"),
                            "Location": safe_text(r.get('location_building',''),"—"),
                            "Category": safe_text(r.get('category',''),"—"),
                            "Title": safe_text(r.get('title',''),"—")[:50],
                            "Raised By": safe_text(r.get('requester_name',''),"—"),
                            "Priority": safe_text(r.get('priority',''),"—"),
                            "Status": safe_text(r.get('status',''),"—").upper(),
                            "Age": age_str,
                            "Closed": closed,
                            "Level": f"L{safe_text(r.get('escalation_level',1),'1')}"
                        })
                    
                    report_df = pd.DataFrame(table_data)
                    st.dataframe(report_df, use_container_width=True, hide_index=True, height=500)
                    
                    st.markdown("---")
                    st.markdown("### 📥 Download Reports")
                    
                    logo_b64 = get_logo_base64()
                    logo_html = f'<img src="data:image/png;base64,{logo_b64}" height="35">' if logo_b64 else ''
                    
                    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;margin:25px;color:#1a1a1a;font-size:11px}}.header{{background:#1a1a1a;color:white;padding:18px 20px;border-radius:10px;display:flex;align-items:center;gap:15px;margin-bottom:20px}}.header h1{{margin:0;font-size:19px}}.kpi-row{{display:flex;gap:8px;margin:15px 0}}.kpi{{flex:1;background:#f5f5f5;border-radius:8px;padding:10px;text-align:center;border-left:4px solid #CC0000}}.kpi.green{{border-left-color:#10B981}}.kpi-val{{font-size:22px;font-weight:bold;color:#CC0000}}.kpi-label{{font-size:9px;color:#666}}table{{width:100%;border-collapse:collapse;font-size:10px}}th{{background:#CC0000;color:white;padding:7px 5px;text-align:left;font-size:8px}}td{{padding:4px 5px;border-bottom:1px solid #ddd}}.footer{{margin-top:25px;font-size:9px;color:#999;text-align:center;border-top:1px solid #ddd;padding-top:12px}}</style></head><body><div class="header">{logo_html}<div><h1>Helpdesk Report - {rpt_month} {rpt_year}</h1><p style="font-size:10px;opacity:0.8">{safe_text(info.get('full_name',fc))} | {datetime.now().strftime('%d %B %Y, %I:%M %p WAT')}</p></div></div><div class="kpi-row"><div class="kpi"><div class="kpi-val">{total}</div><div class="kpi-label">Total</div></div><div class="kpi"><div class="kpi-val">{open_count_rpt}</div><div class="kpi-label">Open</div></div><div class="kpi"><div class="kpi-val">{in_progress_rpt}</div><div class="kpi-label">In Progress</div></div><div class="kpi green"><div class="kpi-val">{closed_count_rpt}</div><div class="kpi-label">Closed</div></div><div class="kpi"><div class="kpi-val">{avg_display_rpt}</div><div class="kpi-label">Avg Resolution</div></div></div><h2>Tickets</h2><table><tr><th>#</th><th>DateTime</th><th>Ticket</th><th>Location</th><th>Category</th><th>Title</th><th>By</th><th>Priority</th><th>Status</th><th>Age</th><th>Closed</th></tr>"""
                    
                    for _, r in report_df.iterrows():
                        html += f"<tr><td>{r['SNo']}</td><td>{r['DateTime']}</td><td>{r['Ticket No']}</td><td>{r['Location']}</td><td>{r['Category']}</td><td>{r['Title']}</td><td>{r['Raised By']}</td><td>{r['Priority']}</td><td>{r['Status']}</td><td>{r['Age']}</td><td>{r['Closed']}</td></tr>"
                    
                    html += f"</table><div class='footer'>Churchgate Group | facilityXperience | Confidential</div></body></html>"
                    
                    with st.expander("🌐 HTML Preview", expanded=True):
                        st.components.v1.html(html, height=500, scrolling=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button("📥 Download HTML", html, f"helpdesk_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html", "text/html", use_container_width=True)
                    with c2:
                        st.download_button("📥 Download CSV", df.to_csv(index=False), f"helpdesk_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv", use_container_width=True)
            else:
                st.info("No ticket data available")
    
    # ============================================
    # TAB 3: ESCALATION SETTINGS (FULL)
    # ============================================
    with tabs[3]:
        if not is_admin:
            st.error("⛔ Admin access only")
        else:
            st.markdown("### ⏱️ Escalation Configuration")
            st.caption("Configure 6-level escalation paths per category")
            
            dept_list = sorted(list(set(c.get("department","") for c in categories)))
            selected_dept = st.selectbox("Select Department", dept_list, key="esc_dept")
            
            dept_cats = [c for c in categories if c.get("department") == selected_dept]
            cat_names = [c.get("category_name","") for c in dept_cats]
            selected_cat = st.selectbox("Select Category", cat_names, key="esc_cat_detail")
            
            if selected_cat:
                cat_id = None
                for c in dept_cats:
                    if c.get("category_name") == selected_cat:
                        cat_id = c["id"]
                        break
                
                if cat_id:
                    all_users = DB.get_users()
                    user_options = [f"{u.get('name','')} ({u.get('email','')})" for u in all_users]
                    
                    existing = supabase.table("ticket_escalation").select("*").eq("facility_code", fc).eq("category_id", cat_id).order("level_number").execute()
                    
                    st.markdown("---")
                    st.markdown(f"#### 🔺 Escalation Levels for: **{selected_cat}**")
                    
                    for level in range(1, 7):
                        existing_users = []
                        existing_time = 30 if level <= 2 else 60 if level == 3 else 1440
                        existing_unit = "Mins"
                        
                        if existing.data:
                            for e in existing.data:
                                if e.get("level_number") == level:
                                    user_str = f"{e.get('escalate_to_name','')} ({e.get('escalate_to_email','')})"
                                    existing_users.append(user_str)
                                    existing_time = e.get("sla_minutes", 30)
                        
                        if existing_time >= 1440:
                            existing_time = existing_time // 1440
                            existing_unit = "Days"
                        elif existing_time >= 60:
                            existing_time = existing_time // 60
                            existing_unit = "Hours"
                        
                        level_colors = {1: "#3B82F6", 2: "#8B5CF6", 3: "#F59E0B", 4: "#EF4444", 5: "#991B1B", 6: "#1a1a1a"}
                        lc = level_colors.get(level, "#4a4a4a")
                        
                        st.markdown(f"""<div style="background:white;border-left:4px solid {lc};border-radius:8px;padding:0.8rem;margin:0.5rem 0;"><b style="color:{lc};">Level {level}</b></div>""", unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns([3, 1, 1])
                        with c1: 
                            st.multiselect(f"Assign Users", user_options, default=existing_users, key=f"esc_u_{level}_{cat_id}")
                        with c2: 
                            st.number_input(f"SLA Time", min_value=0, value=existing_time, key=f"esc_t_{level}_{cat_id}")
                        with c3: 
                            st.selectbox(f"Unit", ["Mins","Hours","Days"], index=["Mins","Hours","Days"].index(existing_unit), key=f"esc_ty_{level}_{cat_id}")
                    
                    st.markdown("---")
                    
                    if st.button("💾 Save Escalation Settings", use_container_width=True, type="primary", key="save_esc_btn"):
                        saved_count = 0
                        for level in range(1, 7):
                            time_val = st.session_state.get(f"esc_t_{level}_{cat_id}", 30)
                            time_type = st.session_state.get(f"esc_ty_{level}_{cat_id}", "Mins")
                            
                            if time_type == "Hours": time_val *= 60
                            elif time_type == "Days": time_val *= 1440
                            
                            users = st.session_state.get(f"esc_u_{level}_{cat_id}", [])
                            
                            try:
                                supabase.table("ticket_escalation").delete().eq("facility_code", fc).eq("category_id", cat_id).eq("level_number", level).execute()
                            except: pass
                            
                            for u in users:
                                if "(" in u and ")" in u:
                                    email = u.split("(")[-1].replace(")","").strip()
                                    name = u.split("(")[0].strip()
                                    try:
                                        supabase.table("ticket_escalation").insert({
                                            "facility_code": fc,
                                            "category_id": cat_id,
                                            "level_number": level,
                                            "level_name": f"Level {level}",
                                            "escalate_to_name": name,
                                            "escalate_to_email": email,
                                            "sla_minutes": int(time_val)
                                        }).execute()
                                        saved_count += 1
                                    except: pass
                        
                        st.success(f"✅ Escalation settings saved! {saved_count} entries configured across 6 levels.")
                        st.balloons()
    
    # ============================================
    # TAB 4: SETTINGS (FULL)
    # ============================================
    with tabs[4]:
        if not is_admin:
            st.error("⛔ Admin access only")
        else:
            st.markdown("### ⚙️ Helpdesk Settings")
            sett_tabs = st.tabs(["📍 Locations", "🏷️ Categories", "📊 Status"])
            
            with sett_tabs[0]:
                st.markdown("#### 📍 Location Details")
                
                locs = DB.get_locations(fc)
                loc_search = st.text_input("🔍 Search locations", key="loc_search_main")
                
                if locs:
                    table_data = []
                    for i, l in enumerate(locs):
                        loc_name = l.get("location_name","")
                        loc_code = l.get("location_code","")
                        
                        if loc_search and loc_search.lower() not in loc_name.lower() and loc_search.lower() not in loc_code.lower():
                            continue
                        
                        subs = DB.get_sub_locations(l["id"])
                        sub_count = len(subs) if subs else 0
                        
                        table_data.append({
                            "SNO": len(table_data) + 1,
                            "Location": loc_code,
                            "Full Name": loc_name,
                            "Sub Locations": f"{sub_count} subs",
                            "id": l["id"]
                        })
                    
                    if table_data:
                        page_size = 10
                        total_pages = max(1, (len(table_data) + page_size - 1) // page_size)
                        
                        if "loc_page" not in st.session_state:
                            st.session_state.loc_page = 1
                        
                        start = (st.session_state.loc_page - 1) * page_size
                        end = start + page_size
                        page_data = table_data[start:end]
                        
                        st.caption(f"Showing {start+1} to {min(end, len(table_data))} of {len(table_data)} entries")
                        
                        for row in page_data:
                            c1, c2, c3, c4, c5 = st.columns([0.5, 1.5, 2, 1.5, 1])
                            with c1: st.markdown(f"**{row['SNO']}**")
                            with c2: st.markdown(f"`{row['Location']}`")
                            with c3: st.markdown(row["Full Name"])
                            with c4: st.markdown(row["Sub Locations"])
                            with c5:
                                loc_id = row["id"]
                                if st.button("🔍 View", key=f"view_loc_{loc_id}", use_container_width=True):
                                    st.session_state.view_loc_id = loc_id
                                    st.rerun()
                            st.markdown("---")
                        
                        c1, c2, c3 = st.columns([1, 2, 1])
                        with c1:
                            if st.session_state.loc_page > 1:
                                if st.button("← Previous", key="loc_prev"):
                                    st.session_state.loc_page -= 1
                                    st.rerun()
                        with c2:
                            st.markdown(f"**Page {st.session_state.loc_page} of {total_pages}**")
                        with c3:
                            if st.session_state.loc_page < total_pages:
                                if st.button("Next →", key="loc_next"):
                                    st.session_state.loc_page += 1
                                    st.rerun()
                    
                    if "view_loc_id" in st.session_state and st.session_state.view_loc_id:
                        loc_id = st.session_state.view_loc_id
                        loc_info = next((l for l in locs if l["id"] == loc_id), None)
                        
                        if loc_info:
                            st.markdown("---")
                            st.markdown(f"#### 📍 Sublocations for **{loc_info.get('location_name','')}**")
                            
                            subs = DB.get_sub_locations(loc_id)
                            if subs:
                                for s in subs:
                                    c1, c2 = st.columns([4, 1])
                                    with c1: st.markdown(f"└ {s.get('sub_location_name','')}")
                                    with c2: 
                                        if st.button("🗑️", key=f"del_sub_{s['id']}", use_container_width=True):
                                            supabase.table("helpdesk_sub_locations").delete().eq("id", s["id"]).execute()
                                            st.rerun()
                            else:
                                st.info("No sub-locations yet")
                            
                            with st.form(f"add_sub_loc_{loc_id}"):
                                new_sub = st.text_input("SubLocation Name", key=f"new_sub_{loc_id}")
                                if st.form_submit_button("➕ Add", use_container_width=True):
                                    if new_sub:
                                        supabase.table("helpdesk_sub_locations").insert({"location_id": loc_id, "sub_location_name": new_sub}).execute()
                                        st.success("✅ Added!")
                                        st.rerun()
                            
                            if st.button("❌ Close View", key=f"close_view_loc_{loc_id}", use_container_width=True):
                                st.session_state.view_loc_id = None
                                st.rerun()
                
                st.markdown("---")
                with st.form("add_loc_form"):
                    st.markdown("**➕ Add New Location**")
                    c1, c2 = st.columns(2)
                    with c1:
                        new_loc_code = st.text_input("Location Code*", key="loc_code", placeholder="e.g. CT")
                        new_loc_name = st.text_input("Location Name*", key="loc_name", placeholder="e.g. CT — Office Tower")
                    with c2:
                        new_sub_name = st.text_input("Initial Sub-Location (optional)", key="sub_name", placeholder="e.g. Floor 1")
                    if st.form_submit_button("➕ Add Location", use_container_width=True):
                        if new_loc_code and new_loc_name:
                            res = supabase.table("helpdesk_locations").insert({
                                "facility_code": fc,
                                "location_code": new_loc_code,
                                "location_name": new_loc_name
                            }).execute()
                            if res.data and new_sub_name:
                                supabase.table("helpdesk_sub_locations").insert({
                                    "location_id": res.data[0]["id"],
                                    "sub_location_name": new_sub_name
                                }).execute()
                            st.success("✅ Location added!")
                            st.rerun()
                        else:
                            st.error("⚠️ Location Code and Name are required")
            
            with sett_tabs[1]:
                st.markdown("#### 🏷️ Category Details")
                
                cat_search = st.text_input("🔍 Search categories", key="cat_search_main")
                
                if categories:
                    table_data = []
                    for c in categories:
                        if cat_search and cat_search.lower() not in c.get("category_name","").lower() and cat_search.lower() not in c.get("department","").lower():
                            continue
                        
                        table_data.append({
                            "SNO": len(table_data) + 1,
                            "Department": c.get("department",""),
                            "Category": c.get("category_name",""),
                            "SLA": f"{c.get('sla_hours','4')}hrs",
                            "Active": "✅" if c.get("is_active") else "❌",
                            "id": c["id"]
                        })
                    
                    if table_data:
                        page_size = 10
                        total_pages = max(1, (len(table_data) + page_size - 1) // page_size)
                        
                        if "cat_page" not in st.session_state:
                            st.session_state.cat_page = 1
                        
                        start = (st.session_state.cat_page - 1) * page_size
                        end = start + page_size
                        page_data = table_data[start:end]
                        
                        st.caption(f"Showing {start+1} to {min(end, len(table_data))} of {len(table_data)} entries")
                        
                        for row in page_data:
                            c1, c2, c3, c4, c5 = st.columns([0.5, 2, 2.5, 1, 1])
                            with c1: st.markdown(f"**{row['SNO']}**")
                            with c2: st.markdown(row["Department"])
                            with c3: st.markdown(row["Category"])
                            with c4: st.markdown(row["SLA"])
                            with c5: st.markdown(row["Active"])
                            st.markdown("---")
                        
                        c1, c2, c3 = st.columns([1, 2, 1])
                        with c1:
                            if st.session_state.cat_page > 1:
                                if st.button("← Prev", key="cat_prev"):
                                    st.session_state.cat_page -= 1
                                    st.rerun()
                        with c2:
                            st.markdown(f"**Page {st.session_state.cat_page} of {total_pages}**")
                        with c3:
                            if st.session_state.cat_page < total_pages:
                                if st.button("Next →", key="cat_next"):
                                    st.session_state.cat_page += 1
                                    st.rerun()
                
                st.markdown("---")
                with st.form("add_cat_form"):
                    st.markdown("**➕ Add New Category**")
                    c1, c2, c3 = st.columns(3)
                    with c1: 
                        new_cat = st.text_input("Category Name*", key="cat_name")
                    with c2: 
                        dept_list_sett = sorted(list(set(c.get("department","") for c in categories)))
                        new_dept = st.selectbox("Department", dept_list_sett, key="cat_dept")
                    with c3: 
                        new_sla = st.number_input("SLA Hours", 1, 72, 4, key="cat_sla")
                    if st.form_submit_button("➕ Add Category", use_container_width=True):
                        if new_cat:
                            supabase.table("helpdesk_categories").insert({
                                "department": new_dept,
                                "category_name": new_cat,
                                "sla_hours": new_sla,
                                "is_active": True
                            }).execute()
                            st.success("✅ Category added!")
                            st.rerun()
                        else:
                            st.error("⚠️ Category name is required")
            
            with sett_tabs[2]:
                st.markdown("#### 📊 Status Configuration")
                
                status_configs = [
                    {"status": "open", "icon": "🔴", "color": "#EF4444", "description": "Newly created ticket, awaiting assignment"},
                    {"status": "in_progress", "icon": "🟡", "color": "#F59E0B", "description": "Ticket is being worked on"},
                    {"status": "hold", "icon": "⏸️", "color": "#3B82F6", "description": "Ticket is on hold pending external input"},
                    {"status": "closed", "icon": "🟢", "color": "#10B981", "description": "Ticket has been resolved"},
                    {"status": "rejected", "icon": "❌", "color": "#6B7280", "description": "Ticket has been rejected"},
                ]
                
                for s in status_configs:
                    st.markdown(f"""
                    <div style="background:white;border-radius:8px;padding:0.8rem;margin:0.3rem 0;border-left:4px solid {s['color']};display:flex;align-items:center;gap:1rem;">
                        <div style="font-size:1.5rem;">{s['icon']}</div>
                        <div style="flex:1;">
                            <div style="font-weight:600;">{s['status'].upper()}</div>
                            <div style="font-size:0.7rem;color:#888;">{s['description']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.info("Custom status management — contact system administrator for modifications.")

# ============================================
# VISITOR MANAGEMENT — WORLD CLASS SYSTEM (FULL)
# ============================================
def page_visitor():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    user_role = st.session_state.get("user_role", "staff")
    is_admin = user_role in ["admin", "approver", "authorizer", "confirmer"]
    
    st.markdown(f'## 🛂 Visitor Management — {info.get("full_name", fc)}')
    
    tabs = st.tabs(["📋 Dashboard", "➕ Register Visitor", "🛂 Gate Check", "📈 Analytics", "📄 Reports"])
    
    # ============================================
    # TAB 0: DASHBOARD
    # ============================================
    with tabs[0]:
        today = date.today()
        
        visitors_today = supabase.table("visitors").select("id", count="exact").eq("facility_code", fc).eq("visit_date", str(today)).execute()
        checked_in = supabase.table("visitors").select("id", count="exact").eq("facility_code", fc).eq("visit_date", str(today)).eq("status", "checked_in").execute()
        expected = supabase.table("visitors").select("id", count="exact").eq("facility_code", fc).eq("visit_date", str(today)).in_("status", ["expected","pre_registered"]).execute()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("📋 Total Today", visitors_today.count or 0)
        with c2: st.metric("✅ Checked In", checked_in.count or 0)
        with c3: st.metric("⏳ Expected", expected.count or 0)
        with c4: st.metric("🚪 Checked Out", 0)
        
        st.markdown("---")
        st.markdown("### 📋 Today's Visitors")
        
        visitors = supabase.table("visitors").select("*").eq("facility_code", fc).eq("visit_date", str(today)).order("expected_arrival").execute()
        
        if visitors.data:
            for v in visitors.data:
                status = v.get("status", "expected")
                colors = {"checked_in": "#10B981", "checked_out": "#6B7280", "expected": "#F59E0B", "pre_registered": "#3B82F6", "cancelled": "#EF4444"}
                sc = colors.get(status, "#4a4a4a")
                
                st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;margin:0.4rem 0;border-left:4px solid {sc};box-shadow:0 1px 3px rgba(0,0,0,0.04);"><div style="display:flex;justify-content:space-between;align-items:center;"><div><b>{v.get('full_name','')}</b><span style="font-size:0.7rem;color:#888;margin-left:0.5rem;">{v.get('company','')}</span></div><span style="background:{sc};color:white;padding:2px 10px;border-radius:12px;font-size:0.65rem;">{status.upper()}</span></div><div style="font-size:0.7rem;color:#666;margin-top:0.2rem;">🎯 {v.get('purpose_of_visit','')} | 👤 {v.get('host_name','')} | ⏰ {v.get('expected_arrival','')}</div><div style="font-size:0.65rem;color:#888;">📧 {v.get('email','N/A')} | 📱 {v.get('mobile','N/A')} | 🚗 {v.get('vehicle_plate','No vehicle')}</div></div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([1,1,1])
                with c1:
                    if status in ["expected", "pre_registered"]:
                        if st.button("✅ Check In", key=f"vin_{v['id']}", use_container_width=True):
                            supabase.table("visitors").update({"status": "checked_in", "actual_arrival": datetime.now().isoformat()}).eq("id", v["id"]).execute()
                            if v.get("host_email"):
                                send_email_notification(v["host_email"], f"✅ Guest Arrived: {v.get('full_name','')}",
                                    f"""<div style="font-family:Arial;max-width:400px;border:1px solid #10B981;border-radius:8px;overflow:hidden;"><div style="background:#10B981;padding:15px;color:white;"><h3>✅ Guest Has Arrived</h3><p style="margin:3px 0 0 0;font-size:11px;">{info.get('full_name',fc)}</p></div><div style="padding:15px;"><p>Dear {v.get('host_name','')},</p><p><b>{v.get('full_name','')}</b> from <b>{v.get('company','')}</b> has arrived and is waiting for you.</p><table style="width:100%;font-size:12px;"><tr><td style="padding:3px;"><b>🕐 Check-in:</b></td><td>{datetime.now().strftime('%I:%M %p')}</td></tr><tr><td style="padding:3px;"><b>📍 Location:</b></td><td>{v.get('gate_location','Main Gate')}</td></tr><tr><td style="padding:3px;"><b>🎯 Purpose:</b></td><td>{v.get('purpose_of_visit','')}</td></tr></table></div></div>""")
                            st.rerun()
                with c2:
                    if status == "checked_in":
                        if st.button("🚪 Check Out", key=f"vout_{v['id']}", use_container_width=True):
                            supabase.table("visitors").update({"status": "checked_out", "actual_departure": datetime.now().isoformat()}).eq("id", v["id"]).execute()
                            st.rerun()
                with c3:
                    if st.button("📋 Details", key=f"vdet_{v['id']}", use_container_width=True):
                        with st.expander("Visitor Details", expanded=True):
                            st.write(f"**Pass ID:** {v.get('pass_id','N/A')}")
                            st.write(f"**Access Code:** {v.get('access_code','N/A')}")
                            if v.get("qr_code_url"):
                                st.image(v["qr_code_url"], width=120)
                            st.write(f"**ID Type:** {v.get('identification_type','')} | **ID No:** {v.get('identification_number','')}")
                            st.write(f"**Access Level:** {v.get('access_level','')}")
                            if v.get("belongings"):
                                st.write(f"**Belongings:** {v.get('belongings','')}")
        else:
            st.info("No visitors today")
    
    # ============================================
    # TAB 1: REGISTER VISITOR
    # ============================================
    with tabs[1]:
        st.markdown("### ➕ Register Visitor")
        
        reg_mode = st.radio("Registration Mode", ["Single Visitor", "Bulk Registration (CSV)", "Quick Batch Entry"], horizontal=True)
        
        if reg_mode == "Single Visitor":
            c1, c2 = st.columns(2)
            with c1:
                visitor_type = st.selectbox("Visitor Type", ["Visitor", "Vendor", "Interview", "Contractor", "Delivery", "Guest"])
                pass_type = st.selectbox("Pass Type", ["One Time", "Recurring", "Multi-Day"])
            with c2:
                visit_date = st.date_input("Visit Date", today)
                access_level = st.selectbox("Access Level", ["Standard", "Restricted", "VIP", "Escort Required"])
            
            st.markdown("---")
            st.markdown("**👤 Personal Details**")
            c1, c2, c3 = st.columns(3)
            with c1:
                first_name = st.text_input("First Name*")
                email = st.text_input("Email")
            with c2:
                last_name = st.text_input("Last Name*")
                mobile = st.text_input("Mobile Number*")
            with c3:
                company = st.text_input("Company")
                whatsapp = st.text_input("WhatsApp Number")
            
            c1, c2 = st.columns(2)
            with c1:
                id_type = st.selectbox("ID Type", ["National ID", "Driver's License", "International Passport", "Company ID", "Voter's Card"])
                id_number = st.text_input("ID Number")
            with c2:
                vehicle = st.text_input("Vehicle Plate Number")
                gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
            
            st.markdown("---")
            st.markdown("**🏢 Visit Details**")
            c1, c2, c3 = st.columns(3)
            with c1:
                host_name = st.text_input("Host Name*")
                arrival_time = st.time_input("Expected Arrival", time(9, 0))
            with c2:
                host_email = st.text_input("Host Email*")
                departure_time = st.time_input("Expected Departure", time(17, 0))
            with c3:
                host_phone = st.text_input("Host Phone")
                purpose = st.text_area("Purpose of Visit", height=60)
            
            belongings_label = "Belongings/Equipment*" if visitor_type == "Contractor" else "Belongings/Equipment"
            belongings = st.text_area(belongings_label, placeholder="Laptop, tools, etc...")
            
            st.markdown("---")
            
            if st.button("🛂 Register Visitor", use_container_width=True, type="primary"):
                errors = []
                if not first_name: errors.append("First Name")
                if not last_name: errors.append("Last Name")
                if not gender: errors.append("Gender")
                if not host_name: errors.append("Host Name")
                if not host_email: errors.append("Host Email")
                if visitor_type == "Contractor" and not belongings: errors.append("Belongings/Equipment (required for Contractors)")
                
                if errors:
                    st.error(f"⚠️ Please fill all required fields: {', '.join(errors)}")
                else:
                    import random, string
                    pass_id = f"VIS-{fc}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
                    access_code_in = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    access_code_out = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    access_code = f"IN:{access_code_in}|OUT:{access_code_out}"
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=IN:{access_code_in}%7COUT:{access_code_out}"
                    
                    if fc == "WTC":
                        logo_b64 = base64.b64encode(open("WTC-logo.jpg","rb").read()).decode() if Path("WTC-logo.jpg").exists() else ""
                        logo_src = f"data:image/jpeg;base64,{logo_b64}"
                    else:
                        logo_b64 = get_logo_base64()
                        logo_src = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
                    
                    try:
                        supabase.table("visitors").insert({
                            "facility_code": fc, "visitor_type": visitor_type.lower(), "pass_id": pass_id,
                            "access_code": access_code, "access_code_in": access_code_in, "access_code_out": access_code_out,
                            "qr_code_url": qr_url,
                            "first_name": first_name, "last_name": last_name, "gender": gender,
                            "email": email, "mobile": mobile, "whatsapp_number": whatsapp or mobile,
                            "company": company, "identification_type": id_type, "identification_number": id_number,
                            "vehicle_plate": vehicle, "purpose_of_visit": purpose,
                            "host_name": host_name, "host_email": host_email, "host_phone": host_phone,
                            "visit_date": str(visit_date), "expected_arrival": str(arrival_time),
                            "expected_departure": str(departure_time),
                            "pass_type": pass_type.lower().replace(" ", "_"), "access_level": access_level.lower(),
                            "belongings": belongings, "status": "pre_registered",
                            "created_at": datetime.now().isoformat()
                        }).execute()
                    except Exception as e:
                        st.error(f"INSERT ERROR: {str(e)}")
                        st.stop()
                    
                    st.success(f"✅ Visitor registered! Pass ID: {pass_id}")
                    st.markdown(f"""
                    <div style="max-width:350px;margin:0 auto;background:white;border:2px solid #CC0000;border-radius:12px;overflow:hidden;text-align:center;">
                        <div style="background:#CC0000;color:white;padding:10px;font-weight:bold;font-size:0.9rem;">VISITOR ACCESS PASS</div>
                        <div style="padding:15px;">
                            {f'<img src="{logo_src}" height="25" style="margin-bottom:8px;">' if logo_src else ''}
                            <p style="font-weight:bold;margin:5px 0;">{first_name} {last_name}</p>
                            <p style="font-size:0.8rem;color:#666;">{company} | {visitor_type}</p>
                            <img src="{qr_url}" width="160" style="margin:10px 0;">
                            <div style="display:flex;justify-content:center;gap:20px;margin:8px 0;">
                                <div><b>🟢 IN:</b><br><span style="font-size:1.1rem;font-family:monospace;">{access_code_in}</span></div>
                                <div><b>🔴 OUT:</b><br><span style="font-size:1.1rem;font-family:monospace;">{access_code_out}</span></div>
                            </div>
                            <p style="font-size:0.7rem;color:#888;">{visit_date} | {arrival_time} - {departure_time}</p>
                            <p style="font-size:0.7rem;">Host: {host_name} | Pass ID: {pass_id}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if email:
                        send_email_notification(email, f"🛂 Your Access Pass - {info.get('full_name',fc)}",
                            f"""<div style="font-family:Arial;max-width:450px;margin:0 auto;border:2px solid #CC0000;border-radius:12px;overflow:hidden;"><div style="background:#CC0000;padding:15px;color:white;text-align:center;"><h2 style="margin:0;">VISITOR ACCESS PASS</h2><p style="margin:3px 0 0 0;font-size:11px;">{info.get('full_name',fc)}</p></div><div style="padding:20px;text-align:center;"><h3 style="margin:0 0 5px 0;">{first_name} {last_name}</h3><p style="color:#666;margin:0 0 10px 0;">{company}</p><img src="{qr_url}" width="180" style="border:1px solid #ddd;padding:5px;border-radius:8px;"><div style="display:flex;justify-content:center;gap:30px;margin:15px 0;"><div style="text-align:center;"><div style="font-size:10px;color:#888;">🟢 ENTRY CODE</div><div style="font-size:1.3rem;font-weight:bold;font-family:monospace;color:#10B981;">{access_code_in}</div></div><div style="text-align:center;"><div style="font-size:10px;color:#888;">🔴 EXIT CODE</div><div style="font-size:1.3rem;font-weight:bold;font-family:monospace;color:#EF4444;">{access_code_out}</div></div></div><table style="width:100%;font-size:11px;text-align:left;margin-top:10px;"><tr><td style="padding:4px;font-weight:bold;">📅 Date:</td><td>{visit_date}</td></tr><tr><td style="padding:4px;font-weight:bold;">⏰ Time:</td><td>{arrival_time} - {departure_time}</td></tr><tr><td style="padding:4px;font-weight:bold;">👤 Host:</td><td>{host_name}</td></tr><tr><td style="padding:4px;font-weight:bold;">🆔 Pass ID:</td><td>{pass_id}</td></tr></table><div style="margin-top:15px;padding:10px;background:#FFF3CD;border-radius:8px;font-size:10px;color:#92400E;">⚠️ Please present this QR code at the gate. Overstaying beyond your scheduled time will flag security.</div></div></div>""")
                    
                    if host_email:
                        send_email_notification(host_email, f"🛂 Visitor Expected: {first_name} {last_name}",
                            f"""<div style="font-family:Arial;max-width:500px;border:1px solid #ddd;border-radius:8px;overflow:hidden;"><div style="background:#CC0000;padding:15px;color:white;"><h3 style="margin:0;">📋 Visitor Pre-Registered</h3><p style="margin:3px 0 0 0;font-size:11px;">{info.get('full_name',fc)}</p></div><div style="padding:15px;"><p>Dear {host_name},</p><p><b>{first_name} {last_name}</b> from <b>{company}</b> is scheduled to visit you.</p><table style="width:100%;font-size:12px;border-collapse:collapse;"><tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">📅 Date</td><td style="padding:5px;border-bottom:1px solid #eee;">{visit_date}</td></tr><tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">⏰ Time</td><td style="padding:5px;border-bottom:1px solid #eee;">{arrival_time} - {departure_time}</td></tr><tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">🎯 Purpose</td><td style="padding:5px;border-bottom:1px solid #eee;">{purpose}</td></tr><tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">🆔 Pass ID</td><td style="padding:5px;border-bottom:1px solid #eee;">{pass_id}</td></tr><tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">🟢 Entry Code</td><td style="padding:5px;border-bottom:1px solid #eee;font-family:monospace;color:#10B981;">{access_code_in}</td></tr><tr><td style="padding:5px;font-weight:bold;">🚗 Vehicle</td><td style="padding:5px;">{vehicle or 'N/A'}</td></tr></table><div style="margin-top:12px;padding:10px;background:#f0f8ff;border-radius:6px;font-size:11px;">💡 <b>Forward this email</b> to your guest — it contains their access codes and QR pass for entry.</div></div></div>""")
                    
                    st.balloons()
                    st.rerun()
        
        elif reg_mode == "Bulk Registration (CSV)":
            st.markdown("#### 📋 Bulk Visitor Registration via CSV")
            st.caption("Upload a CSV file with columns: First Name, Last Name, Email, Mobile, Company")
            
            uploaded_file = st.file_uploader("Upload CSV", type="csv")
            
            if uploaded_file:
                csv_data = pd.read_csv(uploaded_file)
                st.dataframe(csv_data.head(10), use_container_width=True)
                st.caption(f"📋 {len(csv_data)} visitors found")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    bulk_visitor_type = st.selectbox("Visitor Type", ["Visitor", "Vendor", "Interview", "Contractor", "Delivery", "Guest"], key="bulk_vtype")
                    bulk_host = st.text_input("Host Name*", key="bulk_host")
                    bulk_date = st.date_input("Visit Date", today, key="bulk_date")
                with c2:
                    bulk_pass_type = st.selectbox("Pass Type", ["One Time", "Recurring", "Multi-Day"], key="bulk_pass")
                    bulk_purpose = st.text_input("Purpose of Visit*", key="bulk_purpose")
                    bulk_arrival = st.time_input("Arrival Time", time(9,0), key="bulk_arrival")
                with c3:
                    bulk_access_level = st.selectbox("Access Level", ["Standard", "Restricted", "VIP", "Escort Required"], key="bulk_access")
                    bulk_host_email = st.text_input("Host Email", key="bulk_email")
                    bulk_departure = st.time_input("Departure Time", time(17,0), key="bulk_departure")
                
                if st.button(f"🛂 Register {len(csv_data)} Visitors", use_container_width=True, type="primary"):
                    if bulk_host and bulk_purpose:
                        import random, string
                        success_count = 0
                        failed_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in csv_data.iterrows():
                            try:
                                first = str(row.get("First Name", "") or row.get("first_name", "") or row.get("FirstName", "")).strip()
                                last = str(row.get("Last Name", "") or row.get("last_name", "") or row.get("LastName", "")).strip()
                                email_csv = str(row.get("Email", "") or row.get("email", "")).strip()
                                mobile_csv = str(row.get("Mobile", "") or row.get("mobile", "") or row.get("Phone", "")).strip()
                                company_csv = str(row.get("Company", "") or row.get("company", "")).strip()
                                
                                if not first or not last:
                                    failed_count += 1
                                    continue
                                
                                pass_id = f"VIS-{fc}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}{''.join(random.choices(string.ascii_uppercase, k=2))}"
                                access_code_in = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                                access_code_out = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                                access_code = f"IN:{access_code_in}|OUT:{access_code_out}"
                                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=IN:{access_code_in}%7COUT:{access_code_out}"
                                
                                supabase.table("visitors").insert({
                                    "facility_code": fc,
                                    "visitor_type": bulk_visitor_type.lower(),
                                    "pass_id": pass_id,
                                    "access_code": access_code,
                                    "access_code_in": access_code_in,
                                    "access_code_out": access_code_out,
                                    "qr_code_url": qr_url,
                                    "first_name": first,
                                    "last_name": last,
                                    "gender": "Other",
                                    "email": email_csv,
                                    "mobile": mobile_csv,
                                    "whatsapp_number": mobile_csv,
                                    "company": company_csv,
                                    "identification_type": "Company ID",
                                    "identification_number": "",
                                    "vehicle_plate": "",
                                    "purpose_of_visit": bulk_purpose,
                                    "host_name": bulk_host,
                                    "host_email": bulk_host_email,
                                    "host_phone": "",
                                    "visit_date": str(bulk_date),
                                    "expected_arrival": str(bulk_arrival),
                                    "expected_departure": str(bulk_departure),
                                    "pass_type": bulk_pass_type.lower().replace(" ", "_"),
                                    "access_level": bulk_access_level.lower(),
                                    "belongings": "",
                                    "status": "pre_registered",
                                    "created_at": datetime.now().isoformat()
                                }).execute()
                                
                                success_count += 1
                            except Exception as e:
                                failed_count += 1
                                continue
                            
                            progress_bar.progress((idx + 1) / len(csv_data))
                            status_text.text(f"Processing: {idx + 1}/{len(csv_data)}")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        if success_count > 0:
                            st.success(f"✅ {success_count} visitors registered successfully!")
                            if failed_count > 0:
                                st.warning(f"⚠️ {failed_count} entries skipped due to missing names or errors")
                            st.balloons()
                            
                            if bulk_host_email:
                                send_email_notification(
                                    bulk_host_email,
                                    f"🛂 {success_count} Visitors Pre-Registered - {info.get('full_name', fc)}",
                                    f"""<div style="font-family:Arial;max-width:500px;border:1px solid #ddd;border-radius:8px;overflow:hidden;"><div style="background:#CC0000;padding:15px;color:white;"><h3 style="margin:0;">📋 Batch Visitor Registration</h3><p style="margin:3px 0 0 0;font-size:11px;">{info.get('full_name', fc)}</p></div><div style="padding:15px;"><p>Dear {bulk_host},</p><p><b>{success_count} visitors</b> have been pre-registered for <b>{bulk_date}</b>.</p><p><b>Purpose:</b> {bulk_purpose}</p><p><b>Time:</b> {bulk_arrival} - {bulk_departure}</p><p>Please ensure your guests have their access codes ready at the gate.</p></div></div>"""
                                )
                        else:
                            st.error(f"❌ Failed to register any visitors. Check CSV format (needs: First Name, Last Name columns)")
                    else:
                        st.error("⚠️ Host Name and Purpose are required")
        
        elif reg_mode == "Quick Batch Entry":
            st.markdown("#### 📝 Quick Batch Entry")
            st.caption("Enter visitor names (one per line) for quick registration")
            
            batch_names = st.text_area("Visitor Names", height=150, placeholder="John Doe\nJane Smith\nBob Johnson\n...")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                batch_visitor_type = st.selectbox("Visitor Type", ["Visitor", "Vendor", "Interview", "Contractor", "Delivery", "Guest"], key="batch_vtype")
                batch_host = st.text_input("Host Name*", key="batch_host")
                batch_date = st.date_input("Visit Date", today, key="batch_date")
            with c2:
                batch_pass_type = st.selectbox("Pass Type", ["One Time", "Recurring", "Multi-Day"], key="batch_pass")
                batch_purpose = st.text_input("Purpose of Visit*", key="batch_purpose")
                batch_arrival = st.time_input("Arrival Time", time(9,0), key="batch_arrival")
            with c3:
                batch_access_level = st.selectbox("Access Level", ["Standard", "Restricted", "VIP", "Escort Required"], key="batch_access")
                batch_host_email = st.text_input("Host Email", key="batch_email")
                batch_departure = st.time_input("Departure Time", time(17,0), key="batch_departure")
            
            if st.button("🛂 Register Batch", use_container_width=True, type="primary"):
                if batch_host and batch_purpose and batch_names:
                    import random, string
                    names = [n.strip() for n in batch_names.split("\n") if n.strip()]
                    success_count = 0
                    
                    for name in names:
                        try:
                            parts = name.split(" ", 1)
                            first = parts[0]
                            last = parts[1] if len(parts) > 1 else ""
                            
                            pass_id = f"VIS-{fc}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
                            access_code_in = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                            access_code_out = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                            access_code = f"IN:{access_code_in}|OUT:{access_code_out}"
                            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=IN:{access_code_in}%7COUT:{access_code_out}"
                            
                            supabase.table("visitors").insert({
                                "facility_code": fc,
                                "visitor_type": batch_visitor_type.lower(),
                                "pass_id": pass_id,
                                "access_code": access_code,
                                "access_code_in": access_code_in,
                                "access_code_out": access_code_out,
                                "qr_code_url": qr_url,
                                "first_name": first,
                                "last_name": last,
                                "gender": "Other",
                                "email": "",
                                "mobile": "",
                                "company": "",
                                "identification_type": "Company ID",
                                "identification_number": "",
                                "vehicle_plate": "",
                                "purpose_of_visit": batch_purpose,
                                "host_name": batch_host,
                                "host_email": batch_host_email,
                                "host_phone": "",
                                "visit_date": str(batch_date),
                                "expected_arrival": str(batch_arrival),
                                "expected_departure": str(batch_departure),
                                "pass_type": batch_pass_type.lower().replace(" ", "_"),
                                "access_level": batch_access_level.lower(),
                                "belongings": "",
                                "status": "pre_registered",
                                "created_at": datetime.now().isoformat()
                            }).execute()
                            
                            success_count += 1
                        except Exception as e:
                            st.warning(f"Failed to register {name}: {str(e)[:50]}")
                            continue
                    
                    if success_count > 0:
                        st.success(f"✅ {success_count} visitors registered!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to register any visitors")
                else:
                    st.error("⚠️ Host Name, Purpose, and Visitor Names are required")
    
    # ============================================
    # TAB 2: GATE CHECK CONSOLE (ADMIN/SECURITY ONLY)
    # ============================================
    with tabs[2]:
        if not is_admin:
            st.error("⛔ Access restricted to Security & Admin personnel only")
        else:
            st.markdown("### 🛂 Gate Check Console")
            
            gate_tabs = st.tabs(["🔍 Verify Entry", "📋 Today's Log", "🚨 Alerts", "📊 Live Feed"])
            
            with gate_tabs[0]:
                st.markdown("#### 🔍 Verify Visitor Access")
                
                verify_mode = st.radio("Verification Mode", ["🔢 Enter Code", "📷 Scan QR"], horizontal=True)
                
                if verify_mode == "🔢 Enter Code":
                    access_code = st.text_input("Enter Access Code", placeholder="Type IN or OUT code...", key="gate_manual_code")
                    
                    if access_code and len(access_code) >= 8:
                        visitor = supabase.table("visitors").select("*").eq("facility_code", fc).or_(f"access_code_in.eq.{access_code},access_code_out.eq.{access_code}").execute()
                        
                        if visitor.data and len(visitor.data) > 0:
                            v = visitor.data[0]
                            is_in_code = v.get("access_code_in") == access_code
                            status = v.get("status", "expected")
                            
                            if is_in_code and status in ["expected", "pre_registered"]:
                                action = "CHECK IN"
                                action_color = "#10B981"
                            elif not is_in_code and status == "checked_in":
                                action = "CHECK OUT"
                                action_color = "#EF4444"
                            elif is_in_code and status == "checked_in":
                                action = "ALREADY IN"
                                action_color = "#F59E0B"
                            elif not is_in_code and status in ["expected", "pre_registered"]:
                                action = "NOT CHECKED IN"
                                action_color = "#F59E0B"
                            else:
                                action = "COMPLETED"
                                action_color = "#6B7280"
                            
                            st.markdown(f"""
                            <div style="background:white;border-radius:12px;padding:1.5rem;border-left:5px solid {action_color};box-shadow:0 2px 8px rgba(0,0,0,0.1);margin:1rem 0;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <h3 style="margin:0;">{v.get('full_name','')}</h3>
                                        <p style="color:#666;margin:3px 0;">{v.get('company','')} | {v.get('visitor_type','').upper()}</p>
                                    </div>
                                    <div style="text-align:center;">
                                        <div style="font-size:1.5rem;font-weight:800;color:{action_color};">{action}</div>
                                        <div style="font-size:0.7rem;color:#888;">{status.upper()}</div>
                                    </div>
                                </div>
                                <hr>
                                <table style="width:100%;font-size:0.8rem;">
                                    <tr><td><b>Pass ID:</b></td><td>{v.get('pass_id','')}</td><td><b>Host:</b></td><td>{v.get('host_name','')}</td></tr>
                                    <tr><td><b>🟢 IN:</b></td><td style="font-family:monospace;">{v.get('access_code_in','')}</td><td><b>🔴 OUT:</b></td><td style="font-family:monospace;">{v.get('access_code_out','')}</td></tr>
                                    <tr><td><b>📅 Date:</b></td><td>{v.get('visit_date','')}</td><td><b>⏰ Time:</b></td><td>{v.get('expected_arrival','')} - {v.get('expected_departure','')}</td></tr>
                                    <tr><td><b>🎯 Purpose:</b></td><td colspan="3">{v.get('purpose_of_visit','')}</td></tr>
                                    <tr><td><b>🚗 Vehicle:</b></td><td>{v.get('vehicle_plate','N/A')}</td><td><b>📦 Items:</b></td><td>{v.get('belongings','None')[:30]}</td></tr>
                                </table>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c1, c2, c3, c4 = st.columns(4)
                            with c1:
                                if action == "CHECK IN":
                                    if st.button("✅ Confirm Check In", use_container_width=True, type="primary"):
                                        supabase.table("visitors").update({"status":"checked_in","actual_arrival":datetime.now().isoformat()}).eq("id",v["id"]).execute()
                                        supabase.table("visitor_gate_log").insert({"visitor_id":v["id"],"event_type":"check_in","gate_location":"Main Gate","scanned_by":st.session_state.get("user_name","Security"),"event_time":datetime.now().isoformat()}).execute()
                                        if v.get("host_email"):
                                            send_email_notification(v["host_email"], f"✅ Guest Arrived: {v.get('full_name','')}",
                                                f"""<div style="font-family:Arial;max-width:400px;border:1px solid #10B981;border-radius:8px;overflow:hidden;"><div style="background:#10B981;padding:15px;color:white;"><h3>✅ Guest Has Arrived</h3></div><div style="padding:15px;"><p>Dear {v.get('host_name','')},</p><p><b>{v.get('full_name','')}</b> from <b>{v.get('company','')}</b> has arrived.</p></div></div>""")
                                        st.success("✅ Checked In!")
                                        st.rerun()
                            with c2:
                                if action == "CHECK OUT":
                                    if st.button("🚪 Confirm Check Out", use_container_width=True):
                                        supabase.table("visitors").update({"status":"checked_out","actual_departure":datetime.now().isoformat()}).eq("id",v["id"]).execute()
                                        supabase.table("visitor_gate_log").insert({"visitor_id":v["id"],"event_type":"check_out","gate_location":"Main Gate","scanned_by":st.session_state.get("user_name","Security"),"event_time":datetime.now().isoformat()}).execute()
                                        st.success("🚪 Checked Out!")
                                        st.rerun()
                            with c3:
                                if st.button("📋 More Info", use_container_width=True):
                                    with st.expander("Full Details", expanded=True):
                                        st.json({
                                            "Name": v.get("full_name"),
                                            "Pass ID": v.get("pass_id"),
                                            "Access Level": v.get("access_level"),
                                            "ID Type": v.get("identification_type"),
                                            "ID Number": v.get("identification_number"),
                                        })
                            with c4:
                                if st.button("🚩 Flag/Deny", use_container_width=True):
                                    supabase.table("visitors").update({"status":"cancelled","security_flag":True}).eq("id",v["id"]).execute()
                                    st.error("🚩 Entry Denied & Flagged")
                                    st.rerun()
                            
                            if status == "checked_in" and v.get("expected_departure"):
                                try:
                                    dep_time = datetime.strptime(str(v.get("visit_date")) + " " + str(v.get("expected_departure")), "%Y-%m-%d %H:%M:%S")
                                    if datetime.now() > dep_time:
                                        st.error(f"🚨 OVERSTAY ALERT: Guest was expected to leave by {v.get('expected_departure')}")
                                except: pass
                        else:
                            st.error("❌ Invalid access code")
                
                elif verify_mode == "📷 Scan QR":
                    st.info("📷 QR Scanner — Use a QR code scanner and paste the data below:")
                    qr_data = st.text_input("QR Data", placeholder="Paste scanned QR code data here...")
                    if qr_data:
                        if "IN:" in qr_data and "OUT:" in qr_data:
                            parts = qr_data.replace("IN:","").replace("OUT:","").split("|")
                            if len(parts) >= 2:
                                st.success(f"✅ QR Scanned: IN Code = {parts[0].strip()}")
            
            with gate_tabs[1]:
                st.markdown("#### 📋 Today's Visitor Log")
                
                today_str = str(date.today())
                today_visitors = supabase.table("visitors").select("*").eq("facility_code", fc).eq("visit_date", today_str).order("expected_arrival").execute()
                
                if today_visitors.data:
                    tv = today_visitors.data
                    c1, c2, c3, c4, c5 = st.columns(5)
                    with c1: st.metric("📋 Total", len(tv))
                    with c2: st.metric("✅ Checked In", len([v for v in tv if v.get("status")=="checked_in"]))
                    with c3: st.metric("⏳ Expected", len([v for v in tv if v.get("status") in ["expected","pre_registered"]]))
                    with c4: st.metric("🚪 Checked Out", len([v for v in tv if v.get("status")=="checked_out"]))
                    with c5: st.metric("🚩 Flagged", len([v for v in tv if v.get("security_flag")]))
                    
                    st.markdown("---")
                    
                    vtype_filter = st.selectbox("Filter by Type", ["All", "Visitor", "Vendor", "Interview", "Contractor", "Delivery"], key="gate_type_filter")
                    filtered = tv if vtype_filter == "All" else [v for v in tv if v.get("visitor_type") == vtype_filter.lower()]
                    
                    if filtered:
                        for v in filtered:
                            status = v.get("status","expected")
                            colors = {"checked_in":"#10B981","checked_out":"#6B7280","expected":"#F59E0B","cancelled":"#EF4444"}
                            sc = colors.get(status,"#4a4a4a")
                            
                            overstay = False
                            if status == "checked_in" and v.get("expected_departure"):
                                try:
                                    dep = datetime.strptime(f"{v.get('visit_date')} {v.get('expected_departure')}", "%Y-%m-%d %H:%M:%S")
                                    if datetime.now() > dep:
                                        overstay = True
                                except: pass
                            
                            st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;margin:0.3rem 0;border-left:4px solid {sc};box-shadow:0 1px 3px rgba(0,0,0,0.04);"><div style="display:flex;justify-content:space-between;align-items:center;"><div><b>{v.get('full_name','')}</b><span style="font-size:0.65rem;color:#888;margin-left:0.5rem;">{v.get('visitor_type','').upper()}</span></div><div><span style="background:{sc};color:white;padding:2px 10px;border-radius:12px;font-size:0.65rem;">{status.upper()}</span>{f' <span style="background:#EF4444;color:white;padding:2px 8px;border-radius:12px;font-size:0.6rem;">⚠️ OVERSTAY</span>' if overstay else ''}</div></div><div style="font-size:0.7rem;color:#666;margin-top:0.2rem;">{v.get('company','') or 'N/A'} | 🎯 {v.get('purpose_of_visit','') or 'N/A'} | 👤 {v.get('host_name','')}</div></div>""", unsafe_allow_html=True)
                    else:
                        st.info(f"No {vtype_filter} visitors today")
            
            with gate_tabs[2]:
                st.markdown("#### 🚨 Security Alerts")
                
                all_active = supabase.table("visitors").select("*").eq("facility_code", fc).eq("status", "checked_in").execute()
                
                overstays = []
                if all_active.data:
                    for v in all_active.data:
                        if v.get("expected_departure"):
                            try:
                                dep = datetime.strptime(f"{v.get('visit_date')} {v.get('expected_departure')}", "%Y-%m-%d %H:%M:%S")
                                if datetime.now() > dep:
                                    overstays.append(v)
                            except: pass
                
                if overstays:
                    st.error(f"🚨 {len(overstays)} OVERSTAY ALERTS")
                    for v in overstays:
                        st.markdown(f"""
                        <div style="background:#FEF2F2;border:1px solid #EF4444;border-radius:8px;padding:1rem;margin:0.5rem 0;">
                            <b>⚠️ {v.get('full_name','')}</b> — {v.get('company','')}
                            <br>Expected departure: {v.get('expected_departure','')}
                            <br>Host: {v.get('host_name','')} | Pass: {v.get('pass_id','')}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ No overstay alerts")
                
                flagged = supabase.table("visitors").select("*").eq("facility_code", fc).eq("security_flag", True).order("created_at", desc=True).limit(20).execute()
                if flagged.data:
                    st.markdown("---")
                    st.markdown("#### 🚩 Flagged Visitors")
                    for v in flagged.data:
                        st.markdown(f"🚩 {v.get('full_name','')} — {v.get('company','')} | Status: {v.get('status','').upper()}")
            
            with gate_tabs[3]:
                st.markdown("#### 📊 Activity Log")
                st.caption("Today's gate activity — check-ins and check-outs")
                
                today_str = str(date.today())
                
                # Get TODAY'S activity only
                today_logs = supabase.table("visitor_gate_log").select("*, visitors(full_name, company)").gte("event_time", f"{today_str}T00:00:00").order("event_time", desc=True).execute()
                
                if today_logs.data:
                    # Show summary stats
                    checkins_today = len([l for l in today_logs.data if l.get("event_type") == "check_in"])
                    checkouts_today = len([l for l in today_logs.data if l.get("event_type") == "check_out"])
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("📋 Total Events", len(today_logs.data))
                    with c2: st.metric("✅ Check-ins", checkins_today)
                    with c3: st.metric("🚪 Check-outs", checkouts_today)
                    
                    st.markdown("---")
                    
                    # Currently on-site (checked in but not checked out today)
                    active_visitors = supabase.table("visitors").select("*").eq("facility_code", fc).eq("visit_date", today_str).eq("status", "checked_in").execute()
                    
                    if active_visitors.data:
                        st.markdown(f"### 🟢 Currently On-Site ({len(active_visitors.data)} people)")
                        for v in active_visitors.data:
                            checkin_time = ""
                            checkin_log = [l for l in today_logs.data if l.get("visitor_id") == v.get("id") and l.get("event_type") == "check_in"]
                            if checkin_log:
                                try:
                                    checkin_time = pd.to_datetime(checkin_log[0].get("event_time")).strftime("%I:%M %p")
                                except: pass
                            
                            st.markdown(f"""
                            <div style="background:#ECFDF5;border-left:4px solid #10B981;border-radius:8px;padding:0.6rem;margin:0.3rem 0;">
                                <b>{v.get('full_name','')}</b> — {v.get('company','') or 'N/A'}
                                <br><span style="font-size:0.7rem;color:#666;">🕐 In since: {checkin_time or 'N/A'} | 👤 Host: {v.get('host_name','')}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No visitors currently on-site")
                    
                    st.markdown("---")
                    st.markdown("### 📋 Recent Activity")
                    
                    for log in today_logs.data[:20]:
                        icon = "✅" if log.get("event_type") == "check_in" else "🚪" if log.get("event_type") == "check_out" else "🚩"
                        v_info = log.get("visitors", {})
                        name = v_info.get("full_name","Unknown") if v_info else "Unknown"
                        company = v_info.get("company","") if v_info else ""
                        
                        try:
                            event_time = pd.to_datetime(log.get("event_time")).strftime("%I:%M %p")
                        except:
                            event_time = str(log.get("event_time",""))
                        
                        st.markdown(f"{icon} **{name}** ({company}) — {log.get('event_type','').upper()} at {event_time} by {log.get('scanned_by','')}")
                else:
                    st.info("No gate activity recorded today")
    
    # ============================================
    # TAB 3: ANALYTICS
    # ============================================
    with tabs[3]:
        st.markdown("### 📈 Visitor Analytics")
        
        all_visitors = supabase.table("visitors").select("*").eq("facility_code", fc).order("visit_date", desc=True).limit(500).execute()
        
        if all_visitors.data:
            df = pd.DataFrame(all_visitors.data)
            
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Records", len(df))
            with c2: st.metric("This Month", len(df[pd.to_datetime(df["visit_date"]).dt.month == today.month]) if "visit_date" in df.columns else 0)
            with c3: st.metric("Avg Daily", round(len(df)/max((datetime.now() - pd.to_datetime(df["visit_date"].min())).days if "visit_date" in df.columns else 1, 1)))
            with c4: st.metric("Checked In Rate", f"{round(len(df[df['status']=='checked_in'])/len(df)*100) if len(df)>0 else 0}%")
            
            st.markdown("---")
            
            c1, c2 = st.columns(2)
            with c1:
                if "visitor_type" in df.columns:
                    type_counts = df["visitor_type"].value_counts()
                    fig = px.pie(values=type_counts.values, names=type_counts.index, title="By Visitor Type")
                    st.plotly_chart(fig, use_container_width=True)
            with c2:
                if "visit_date" in df.columns:
                    df["month"] = pd.to_datetime(df["visit_date"]).dt.month
                    monthly = df.groupby("month").size().reset_index(name="count")
                    fig2 = px.bar(monthly, x="month", y="count", title="Monthly Volume")
                    st.plotly_chart(fig2, use_container_width=True)
    
    # ============================================
    # TAB 4: REPORTS
    # ============================================
    with tabs[4]:
        st.markdown("### 📄 Visitor Reports")
        
        rpt_month = st.selectbox("Month", ["January","February","March","April","May","June","July","August","September","October","November","December"], key="vis_rpt_m")
        rpt_year = st.selectbox("Year", [2024,2025,2026,2027], key="vis_rpt_y")
        
        if st.button("📊 Generate Report", use_container_width=True):
            visitors = supabase.table("visitors").select("*").eq("facility_code", fc).order("visit_date", desc=True).limit(500).execute()
            if visitors.data:
                df = pd.DataFrame(visitors.data)
                st.success(f"✅ Report for {rpt_month} {rpt_year} — {len(df)} records")
                
                display_cols = [c for c in ["full_name","company","visitor_type","host_name","purpose_of_visit","visit_date","expected_arrival","status","vehicle_plate"] if c in df.columns]
                st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
                
                csv = df.to_csv(index=False)
                st.download_button("📥 CSV", csv, f"visitors_{rpt_month}_{rpt_year}.csv", "text/csv", use_container_width=True)

# ============================================
# USER MANAGEMENT — FULL ADMIN MODULE (FULL)
# ============================================
def page_users():
    st.markdown("## 👥 User Management")
    
    tabs = st.tabs(["📋 User Directory", "➕ Add User", "✏️ Edit User"])
    
    with tabs[0]:
        users = DB.get_users()
        if users:
            df = pd.DataFrame(users)
            c1, c2, c3 = st.columns(3)
            with c1:
                role_filter = st.selectbox("Filter by Role", ["All", "admin", "approver", "confirmer", "authorizer", "staff", "tenant", "contractor", "vendor"], key="user_role_filter")
            with c2:
                search = st.text_input("Search by name or email", key="user_search")
            with c3:
                st.metric("Total Users", len(df))
            
            if role_filter != "All" and "role" in df.columns:
                df = df[df["role"] == role_filter]
            if search:
                df = df[df["name"].str.contains(search, case=False) | df["email"].str.contains(search, case=False)]
            
            st.markdown("---")
            
            for i, row in df.iterrows():
                role = row.get("role", "staff")
                badges = {"admin":"🔴 Admin","approver":"🟢 Approver","confirmer":"✅ Confirmer","authorizer":"🔐 Authorizer","staff":"👤 Staff","tenant":"🏢 Tenant","contractor":"🔧 Contractor","vendor":"📦 Vendor"}
                badge = badges.get(role, "👤 User")
                
                with st.expander(f"{row.get('name','N/A')} — {row.get('email','')} — {badge}"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"**Employee ID:** {row.get('employee_id','N/A')}")
                        st.write(f"**Designation:** {row.get('designation','N/A')}")
                        st.write(f"**Level:** {row.get('level_hierarchy','N/A')} | **Reports to:** {row.get('reporting_to','N/A')}")
                        st.write(f"**Mobile:** {row.get('mobile','N/A')}")
                        depts = safe_parse_permissions(row.get("department_permissions", []))
                        st.write(f"**Departments:** {', '.join(depts) if depts else 'All'}")
                        perms = safe_parse_permissions(row.get("extra_permissions", []))
                        st.write(f"**Module Permissions:** {', '.join(perms) if perms else 'None'}")
                    with c2:
                        if st.button("✏️ Edit", key=f"edit_usr_{row['id']}", use_container_width=True):
                            st.session_state.edit_user_id = row["id"]
                            st.rerun()
                        if st.button("🔄 Reset PW", key=f"reset_pw_{row['id']}", use_container_width=True):
                            st.session_state.reset_user_id = row["id"]
                            st.rerun()
                        if role != "admin":
                            if st.button("🗑️ Deactivate", key=f"deact_{row['id']}", use_container_width=True):
                                DB.update("app_users", row["id"], {"is_active": False})
                                st.warning("User deactivated")
                                st.rerun()
        else:
            st.info("No users found")
    
    with tabs[1]:
        with st.form("add_user_form"):
            st.markdown("### ➕ Add New User")
            st.markdown("**👤 Personal Details**")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_name = st.text_input("Full Name*", key="add_name")
                new_emp_id = st.text_input("Employee ID*", key="add_emp")
            with c2:
                new_email = st.text_input("Email*", key="add_email")
                new_mobile = st.text_input("Mobile Number", key="add_mob")
            with c3:
                new_designation = st.text_input("Designation*", key="add_desig")
                new_level = st.selectbox("Level/Hierarchy", ["L1", "L2", "L3", "L4", "L5", "L6"], key="add_level")
            new_reporting = st.text_input("Reporting To", key="add_report")
            
            st.markdown("---")
            st.markdown("**🔐 Role & Permissions**")
            c1, c2 = st.columns(2)
            with c1:
                new_role = st.selectbox("Role*", ["staff","authorizer","confirmer","approver","admin","tenant","contractor","vendor"],
                    format_func=lambda x: {"staff":"👤 Staff","authorizer":"🔐 Authorizer","confirmer":"✅ Confirmer","approver":"🟢 Approver","admin":"🔴 Admin","tenant":"🏢 Tenant","contractor":"🔧 Contractor","vendor":"📦 Vendor"}[x], key="add_role")
                new_facility = st.selectbox("Home Facility", ["WTC", "AGVL", "FCPL", "RBPL", "VDL", "WAREHOUSES"], key="add_fac")
            with c2:
                new_password = st.text_input("Password*", type="password", key="add_pw")
                new_alias = st.text_input("Alias (optional)", key="add_alias")
            
            st.markdown("---")
            st.markdown("**🏢 Department Permissions**")
            all_depts_add = [
                "Engineering — Electrical", "Engineering — HVAC", "Engineering — Plumbing",
                "Engineering — Vertical Transportation (Lifts)", "Engineering — Fire Fighting",
                "Facility Management — Hard Services", "Facility Management — Soft Services (Housekeeping)",
                "Facility Management — FM Operations & Helpdesk", "Facility Management — Fitout Works",
                "Facility Management — HSSE Safety & Compliance",
                "Technology Group — Network & Connectivity", "Technology Group — Building Technology",
                "Technology Group — IT Service Desk", "Technology Group — Cybersecurity",
                "Security — Man Guarding Operations",
                "Contractor — Clyde Engineering", "Contractor — Gates and Shield"
            ]
            new_depts = st.multiselect("Select Departments (leave empty for All)", all_depts_add, key="add_depts")
            
            submitted = st.form_submit_button("➕ Create User", use_container_width=True, type="primary")
            if submitted:
                if new_name and new_emp_id and new_email and new_designation and new_password:
                    pw_valid, pw_msg = validate_password_strength(new_password)
                    if not pw_valid:
                        st.error(f"⚠️ {pw_msg}")
                        st.stop()
                    
                    pw_hash = hash_password(new_password)
                    DB.insert("app_users", {
                        "name": new_name, "employee_id": new_emp_id, "email": new_email,
                        "mobile": new_mobile, "designation": new_designation,
                        "level_hierarchy": new_level, "reporting_to": new_reporting,
                        "role": new_role, "department_permissions": new_depts if new_depts else ["All"],
                        "password_hash": pw_hash, "alias_name": new_alias,
                        "home_facility": new_facility, "is_active": True
                    })
                    st.success(f"✅ User {new_name} created!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ Please fill all required fields")
    
    with tabs[2]:
        user_id = st.session_state.get("edit_user_id")
        reset_id = st.session_state.get("reset_user_id")
        
        if reset_id:
            st.markdown("### 🔄 Reset Password")
            with st.form("reset_pw_form"):
                new_pw = st.text_input("New Password*", type="password")
                confirm_pw = st.text_input("Confirm Password*", type="password")
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("✅ Reset", use_container_width=True, type="primary"):
                        if new_pw and new_pw == confirm_pw:
                            pw_valid, pw_msg = validate_password_strength(new_pw)
                            if not pw_valid:
                                st.error(f"⚠️ {pw_msg}")
                            else:
                                pw_hash = hash_password(new_pw)
                                DB.update("app_users", reset_id, {"password_hash": pw_hash})
                                st.success("Password reset!")
                                st.session_state.reset_user_id = None
                                st.rerun()
                with c2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.reset_user_id = None
                        st.rerun()
        
        elif user_id:
            users = DB.get_users()
            user = next((u for u in users if u["id"] == user_id), None)
            
            if user:
                st.markdown(f"### ✏️ Edit: {user.get('name','')}")
                
                with st.form("edit_user_form"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        edit_name = st.text_input("Full Name*", value=user.get("name",""))
                        edit_emp = st.text_input("Employee ID*", value=user.get("employee_id",""))
                    with c2:
                        edit_email = st.text_input("Email*", value=user.get("email",""))
                        edit_mobile = st.text_input("Mobile", value=user.get("mobile","") or "")
                    with c3:
                        edit_desig = st.text_input("Designation*", value=user.get("designation",""))
                        levels = ["L1","L2","L3","L4","L5","L6"]
                        cl = user.get("level_hierarchy","L2")
                        edit_level = st.selectbox("Level", levels, index=levels.index(cl) if cl in levels else 1)
                    
                    edit_report = st.text_input("Reporting To", value=user.get("reporting_to","") or "")
                    
                    cr = user.get("role","staff")
                    roles = ["staff","authorizer","confirmer","approver","admin","tenant","contractor","vendor"]
                    rn = {"staff":"👤 Staff","authorizer":"🔐 Authorizer","confirmer":"✅ Confirmer","approver":"🟢 Approver","admin":"🔴 Admin","tenant":"🏢 Tenant","contractor":"🔧 Contractor","vendor":"📦 Vendor"}
                    edit_role = st.selectbox("Role*", roles, format_func=lambda x: rn[x], index=roles.index(cr) if cr in roles else 0)
                    
                    st.markdown("---")
                    st.markdown("**📋 Module Permissions**")
                    
                    module_groups = {
                        "Dashboards": ["Command Center", "PPM Dashboard", "Facility Operations"],
                        "Work Permit": ["Raise Permit", "Authorize Permit", "Confirm Permit", "Approve Permit", "Work Permit Reports"],
                        "People": ["Visitor Management", "User Management"],
                        "Services": ["Raise Ticket", "Helpdesk", "Feedback"],
                        "Compliance": ["Audit Checklist", "Incident Report", "HOTO Check"],
                        "Utility": ["Utility Dashboard"],
                    }
                    
                    existing_perms = safe_parse_permissions(user.get("extra_permissions", []))
                    
                    for group, modules in module_groups.items():
                        with st.expander(f"📁 {group}"):
                            cols = st.columns(2)
                            for i, mod in enumerate(modules):
                                with cols[i % 2]:
                                    checked = mod in existing_perms
                                    st.checkbox(mod, value=checked, key=f"edit_mod_{group}_{mod}")
                    
                    st.markdown("---")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary"):
                            selected = []
                            for group, modules in module_groups.items():
                                for mod in modules:
                                    if st.session_state.get(f"edit_mod_{group}_{mod}", False):
                                        selected.append(mod)
                            DB.update("app_users", user_id, {
                                "name": edit_name, "employee_id": edit_emp, "email": edit_email,
                                "mobile": edit_mobile, "designation": edit_desig,
                                "level_hierarchy": edit_level, "reporting_to": edit_report,
                                "role": edit_role,
                                "extra_permissions": selected
                            })
                            st.success("✅ User updated!")
                            st.balloons()
                            st.session_state.edit_user_id = None
                            st.rerun()
                    with c2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.edit_user_id = None
                            st.rerun()
            else:
                st.error("User not found")
                if st.button("🔙 Back"):
                    st.session_state.edit_user_id = None
                    st.rerun()
        else:
            st.info("👆 Click ✏️ Edit on a user in the Directory tab to edit them here")

# ============================================
# FACILITY OPERATIONS DASHBOARD (FULL)
# ============================================
def page_fo():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🏢 Facility Operations Dashboard — {info.get("full_name",fc)}')
    k=DB.get_kpis(fc)
    c1,c2,c3,c4=st.columns(4)
    with c1:st.metric("Open WOs",k["open_wo"])
    with c2:st.metric("PPM Due",k["ppm_due"])
    with c3:st.metric("Open Incidents",k["open_inc"])
    with c4:st.metric("Open Tickets",k["open_tix"])
    st.markdown("---")
    st.markdown("### 🔧 MEP Checks")
    mep=DB.get_all("mep_checks",fc,10)
    if mep:st.dataframe(pd.DataFrame(mep),use_container_width=True,hide_index=True)
    else:st.info("No MEP checks recorded")
    with st.form("mep_f"):
        c1,c2=st.columns(2)
        with c1:
            ct=st.selectbox("Check Type",["Mechanical","Electrical","Plumbing","Housekeeping","Fire Safety"])
            zone=st.text_input("Zone");floor=st.text_input("Floor")
        with c2:
            score=st.slider("Score",0.0,100.0,95.0);inspector=st.text_input("Inspector")
        findings=st.text_area("Findings")
        if st.form_submit_button("✅ Submit MEP Check"):
            DB.insert("mep_checks",{"facility_code":fc,"check_type":ct,"zone":zone,"floor":floor,"overall_score":score,"findings":[findings],"check_date":str(date.today()),"status":"completed"})
            st.success("Submitted!");st.rerun()

# ============================================
# OBSERVATIONS & ALERTS (FULL)
# ============================================
def page_oa():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ✅ Observations & Alerts — {info.get("full_name",fc)}')
    inc=DB.get_all("incidents",fc,30)
    if inc:
        for i in inc:
            sev=i.get("severity","low")
            badge="badge-critical" if sev in ["critical","high"] else "badge-warning" if sev=="medium" else "badge-info"
            with st.expander(f"{i.get('incident_number','')} — {i.get('title','')} — {sev.upper()}"):
                st.write(f"**Type:** {i.get('type','')} | **Status:** {i.get('status','')}")
                st.write(f"**Description:** {i.get('description','')}")
                if i.get("immediate_actions"):st.write(f"**Actions:** {i['immediate_actions']}")
    else:st.success("✅ No open alerts")

# ============================================
# AUDIT CHECKLIST (FULL)
# ============================================
def page_ac():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ✅ Audit Framework — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 View Audits","➕ Start Audit"])
    with tab1:
        audits=DB.get_all("audits",fc,20)
        if audits:st.dataframe(pd.DataFrame(audits),use_container_width=True,hide_index=True)
        else:st.info("No audits")
    with tab2:
        with st.form("audit_f"):
            title=st.text_input("Audit Title*");atype=st.selectbox("Type",["Internal","External","Safety","Quality","ISO"])
            items=["Fire extinguishers accessible","Emergency exits clear","Electrical panels labeled","PPE available","Housekeeping standards met","First aid kits stocked","Safety signage visible","Waste management compliant"]
            results={}
            st.markdown("**Checklist Items:**")
            for item in items:results[item]=st.selectbox(item,["Pass","Fail","N/A"],key=f"aud_{item[:15]}")
            if st.form_submit_button("✅ Submit Audit",use_container_width=True):
                if title:
                    passed=sum(1 for v in results.values() if v=="Pass")
                    total=sum(1 for v in results.values() if v!="N/A")
                    score=round((passed/total)*100,1) if total>0 else 100
                    cnt=len(DB.get_all("audits",fc,1000))
                    DB.insert("audits",{"facility_code":fc,"audit_number":f"AUD-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"type":atype,"overall_score":score,"status":"completed","findings":results,"audit_date":str(date.today()),"created_at":datetime.now().isoformat()})
                    st.success(f"Score: {score}%");st.rerun()

# ============================================
# VOICE OF CUSTOMER — FEEDBACK SYSTEM (FULL)
# ============================================
def page_feedback():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    user_role = st.session_state.get("user_role", "staff")
    is_admin = user_role in ["admin", "approver"]
    
    st.markdown(f'## ⭐ Voice of Customer — {info.get("full_name", fc)}')
    
    tabs = st.tabs(["📝 Take Survey", "📊 Feedback Dashboard", "📈 AI Analytics", "⚙️ Survey Admin"])
    
    with tabs[0]:
        survey = supabase.table("feedback_surveys").select("*").eq("facility_code", fc).eq("is_active", True).execute()
        
        if not survey.data or len(survey.data) == 0:
            st.info("📝 No active survey at this time. Check back during survey period.")
        else:
            s = survey.data[0]
            st.markdown(f"### 📝 {s.get('title','')}")
            st.caption(s.get('description',''))
            
            questions = supabase.table("feedback_questions").select("*").eq("survey_id", s["id"]).order("question_number").execute()
            
            if questions.data:
                with st.form("feedback_form"):
                    st.markdown("---")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        resp_name = st.text_input("Your Name", value=st.session_state.get("user_name",""))
                        resp_company = st.text_input("Company")
                    with c2:
                        resp_email = st.text_input("Your Email", value=st.session_state.get("user",{}).get("email",""))
                        anon = st.checkbox("Submit anonymously")
                    
                    st.markdown("---")
                    st.markdown("### Rate Your Experience")
                    st.caption("4 = Excellent | 3 = Good | 2 = Average | 1 = Below Average")
                    
                    scores = {}
                    for q in questions.data:
                        qnum = q.get("question_number")
                        qtype = q.get("question_type","rating")
                        
                        if qtype == "rating":
                            st.markdown(f"**{qnum}. {q.get('question_text','')}**")
                            st.caption(f"Category: {q.get('category','')}")
                            score = st.select_slider(
                                f"Rating for Q{qnum}",
                                options=[1, 2, 3, 4],
                                value=3,
                                format_func=lambda x: f"{'⭐'*x} {['','Below Average','Average','Good','Excellent'][x]}",
                                key=f"q_{q['id']}"
                            )
                            scores[q["id"]] = {"score": score}
                        else:
                            st.markdown(f"**{qnum}. {q.get('question_text','')}**")
                            text_answer = st.text_area(f"Your answer for Q{qnum}", key=f"q_{q['id']}", height=80)
                            scores[q["id"]] = {"text": text_answer}
                        
                        st.markdown("---")
                    
                    submitted = st.form_submit_button("📩 Submit Feedback", use_container_width=True, type="primary")
                    
                    if submitted:
                        if resp_email or anon:
                            res = supabase.table("feedback_responses").insert({
                                "survey_id": s["id"],
                                "respondent_email": resp_email if not anon else None,
                                "respondent_name": resp_name if not anon else "Anonymous",
                                "company": resp_company,
                                "facility_code": fc,
                                "is_anonymous": anon,
                                "submitted_at": datetime.now().isoformat()
                            }).execute()
                            
                            if res.data:
                                resp_id = res.data[0]["id"]
                                for qid, data in scores.items():
                                    supabase.table("feedback_scores").insert({
                                        "response_id": resp_id,
                                        "question_id": qid,
                                        "score": data.get("score"),
                                        "text_answer": data.get("text")
                                    }).execute()
                                
                                st.success("✅ Thank you for your feedback! Your response has been recorded.")
                                st.balloons()
                                st.rerun()
                        else:
                            st.error("Please enter your email or submit anonymously")
    
    with tabs[1]:
        st.markdown("### 📊 Feedback Dashboard")
        
        survey = supabase.table("feedback_surveys").select("*").eq("facility_code", fc).order("created_at", desc=True).limit(1).execute()
        
        if survey.data:
            s = survey.data[0]
            responses = supabase.table("feedback_responses").select("id", count="exact").eq("survey_id", s["id"]).execute()
            questions = supabase.table("feedback_questions").select("*").eq("survey_id", s["id"]).order("question_number").execute()
            
            total_responses = responses.count or 0
            
            st.markdown(f"**Survey:** {s.get('title','')}")
            st.metric("Total Responses", total_responses)
            
            if total_responses > 0 and questions.data:
                st.markdown("---")
                st.markdown("### 📈 Category Scores")
                
                for q in questions.data:
                    if q.get("question_type") == "rating":
                        scores_data = supabase.table("feedback_scores").select("score").eq("question_id", q["id"]).execute()
                        if scores_data.data:
                            avg_score = sum(sc["score"] for sc in scores_data.data) / len(scores_data.data)
                            stars = "⭐" * round(avg_score)
                            st.markdown(f"**{q.get('question_number')}. {q.get('category','')}**")
                            st.markdown(f"{stars} **{avg_score:.1f}/4**")
                            st.progress(avg_score / 4)
        else:
            st.info("No survey data yet")
    
    with tabs[2]:
        st.markdown("### 🤖 AI-Powered Feedback Analytics")
        
        survey = supabase.table("feedback_surveys").select("*").eq("facility_code", fc).order("created_at", desc=True).limit(1).execute()
        
        if survey.data:
            s = survey.data[0]
            questions = supabase.table("feedback_questions").select("*").eq("survey_id", s["id"]).order("question_number").execute()
            
            if questions.data:
                categories_list = []
                avg_scores = []
                
                for q in questions.data:
                    if q.get("question_type") == "rating":
                        scores_data = supabase.table("feedback_scores").select("score").eq("question_id", q["id"]).execute()
                        if scores_data.data:
                            avg = sum(sc["score"] for sc in scores_data.data) / len(scores_data.data)
                            categories_list.append(q.get("category",""))
                            avg_scores.append(round(avg, 1))
                
                if categories_list:
                    fig = px.bar(x=categories_list, y=avg_scores, title="Satisfaction by Category", 
                                labels={"x":"","y":"Score"}, color=avg_scores, 
                                color_continuous_scale=["#EF4444","#F59E0B","#3B82F6","#10B981"],
                                range_color=[1,4])
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("### 🤖 AI Recommendations")
                    best = categories_list[avg_scores.index(max(avg_scores))]
                    worst = categories_list[avg_scores.index(min(avg_scores))]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"🌟 **Strength:** {best} ({max(avg_scores)}/4)")
                        st.caption("Continue investing in this area")
                    with col2:
                        st.error(f"⚠️ **Needs Attention:** {worst} ({min(avg_scores)}/4)")
                        st.caption("Priority improvement area")
                    
                    if min(avg_scores) < 2.5:
                        st.warning(f"🚨 **Retention Risk:** Low satisfaction in {worst} may impact tenant retention.")
                    
                    if max(avg_scores) >= 3.5:
                        st.info(f"💡 **Marketing Opportunity:** High satisfaction in {best} can be leveraged.")
        else:
            st.info("No data for analytics")
    
    with tabs[3]:
        if not is_admin:
            st.error("⛔ Admin access only")
        else:
            st.markdown("### ⚙️ Survey Administration")
            
            surveys = supabase.table("feedback_surveys").select("*").eq("facility_code", fc).order("created_at", desc=True).execute()
            
            if surveys.data:
                st.markdown("**Existing Surveys:**")
                for s in surveys.data:
                    status_badge = "🟢 Active" if s.get("is_active") else "⚪ Inactive"
                    st.markdown(f"- **{s.get('title','')}** — {status_badge} | {s.get('start_date','')} to {s.get('end_date','')}")
            
            st.markdown("---")
            
            with st.form("survey_admin"):
                st.markdown("**Manage Survey**")
                
                survey_options = {s.get("title",""): s["id"] for s in surveys.data} if surveys.data else {}
                selected_survey = st.selectbox("Select Survey", list(survey_options.keys())) if survey_options else None
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("🟢 Activate Survey", use_container_width=True):
                        if selected_survey:
                            supabase.table("feedback_surveys").update({"is_active": False}).eq("facility_code", fc).execute()
                            supabase.table("feedback_surveys").update({"is_active": True}).eq("id", survey_options[selected_survey]).execute()
                            st.success(f"✅ {selected_survey} activated!")
                            st.rerun()
                with c2:
                    if st.form_submit_button("⚪ Deactivate All", use_container_width=True):
                        supabase.table("feedback_surveys").update({"is_active": False}).eq("facility_code", fc).execute()
                        st.success("All surveys deactivated")
                        st.rerun()
            
            st.markdown("---")
            st.markdown("### 📧 Broadcast Survey to Tenants")
            
            tenants = supabase.table("organizations").select("*").eq("is_active", True).execute()
            
            if tenants.data:
                tenant_options = {}
                for t in tenants.data:
                    tenant_options[f"{t.get('name','')} ({t.get('primary_contact_email','')})"] = t
                
                selected_tenants = st.multiselect(
                    "Choose tenants",
                    list(tenant_options.keys()),
                    default=list(tenant_options.keys()),
                    key="broadcast_tenants"
                )
                
                st.caption(f"📋 {len(selected_tenants)} of {len(tenant_options)} tenants selected")
                
                if st.button("📧 Send Survey to Selected Tenants", use_container_width=True):
                    if selected_survey and survey_options:
                        survey_link = f"https://facilityxperience.streamlit.app/?survey={survey_options[selected_survey]}"
                        sent_count = 0
                        
                        for name in selected_tenants:
                            t = tenant_options[name]
                            if t.get("primary_contact_email"):
                                send_email_notification(
                                    t["primary_contact_email"],
                                    f"📝 Tenant Satisfaction Survey — {info.get('full_name',fc)}",
                                    f"""
                                    <div style="font-family:Arial;max-width:600px;border:1px solid #ddd;border-radius:8px;overflow:hidden;">
                                        <div style="background:#CC0000;padding:20px;color:white;">
                                            <h2 style="margin:0;">We Value Your Feedback</h2>
                                            <p style="margin:5px 0 0 0;font-size:12px;">{info.get('full_name',fc)} — Tenant Satisfaction Survey</p>
                                        </div>
                                        <div style="padding:20px;">
                                            <p>Dear {t.get('name','Valued Tenant')},</p>
                                            <p>We invite you to participate in our tenant satisfaction survey. Your feedback helps us improve our services.</p>
                                            <p><b>Time to complete:</b> Less than 5 minutes</p>
                                            <div style="text-align:center;margin:25px 0;">
                                                <a href="{survey_link}" style="background:#CC0000;color:white;padding:12px 30px;text-decoration:none;border-radius:6px;font-weight:bold;">Take Survey Now</a>
                                            </div>
                                            <p style="font-size:11px;color:#888;">Your responses are confidential.</p>
                                        </div>
                                    </div>
                                    """
                                )
                                sent_count += 1
                        
                        st.success(f"✅ Survey sent to {sent_count} tenants!")
                        st.balloons()
                    else:
                        st.error("Please select a survey first")
            else:
                st.info("No tenants found in the database")

# ============================================
# UTILITY DASHBOARD (FULL)
# ============================================
def page_uc():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ⚡ Utility Dashboard — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📊 Dashboard","➕ Record Reading"])
    with tab1:
        readings=DB.get_all("utility_readings",fc,20)
        if readings:
            df=pd.DataFrame(readings)
            st.metric("Total Readings",len(df))
            st.dataframe(df,use_container_width=True,hide_index=True)
        else:st.info("No utility readings")
    with tab2:
        with st.form("util_f"):
            c1,c2=st.columns(2)
            with c1:
                mtype=st.selectbox("Utility Type",["Electricity","Water","Diesel","Gas"])
                mname=st.text_input("Meter Name*");mvalue=st.number_input("Reading Value*",min_value=0.0,step=0.1)
            with c2:
                rdate=st.date_input("Reading Date",date.today());rtime=st.time_input("Reading Time",datetime.now().time())
                rtype=st.selectbox("Reading Type",["Manual","Automated"])
            notes=st.text_area("Notes")
            if st.form_submit_button("📝 Record Reading",use_container_width=True):
                DB.insert("utility_readings",{"facility_code":fc,"utility_type":mtype,"meter_id":None,"meter_name":mname,"reading_date":str(rdate),"reading_time":str(rtime),"reading_value":mvalue,"reading_type":rtype.lower(),"notes":notes,"created_at":datetime.now().isoformat()})
                st.success("Reading recorded!");st.rerun()

# ============================================
# PPM COMMAND CENTER — FORTUNE 500 GRADE
# WORLD-CLASS PLANNED PREVENTIVE MAINTENANCE
# ============================================
def page_ppm():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    
    st.markdown(f'## 📊 PPM Command Center — {info.get("full_name", fc)}')
    
    # Fetch ALL PPM data
    ppm_all = DB.get_all("ppm_schedules", fc, 500)
    
    if not ppm_all:
        st.warning("No PPM schedules configured for this facility. Please set up PPM schedules in the database.")
        return
    
    df = pd.DataFrame(ppm_all)
    
    # ============================================
    # DATA PREPARATION
    # ============================================
    today = date.today()
    now = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = today.replace(day=1)
    
    # Parse dates
    if "next_due_date" in df.columns:
        df["due_date_parsed"] = pd.to_datetime(df["next_due_date"], errors='coerce')
    if "last_completed_date" in df.columns:
        df["completed_date_parsed"] = pd.to_datetime(df["last_completed_date"], errors='coerce')
    
    # Status classifications
    overdue_mask = (df["due_date_parsed"] < pd.Timestamp(today)) & (df["status"] != "completed")
    due_today_mask = (df["due_date_parsed"] == pd.Timestamp(today)) & (df["status"] != "completed")
    due_this_week_mask = (df["due_date_parsed"] >= pd.Timestamp(today)) & (df["due_date_parsed"] <= pd.Timestamp(week_end)) & (df["status"] != "completed")
    due_this_month_mask = (df["due_date_parsed"] >= pd.Timestamp(today)) & (df["due_date_parsed"] <= pd.Timestamp(today + timedelta(days=30))) & (df["status"] != "completed")
    completed_mask = df["status"] == "completed"
    critical_mask = df.get("is_critical", pd.Series([False] * len(df))) == True
    
    # Counts
    total_schedules = len(df)
    overdue_count = overdue_mask.sum()
    due_today_count = due_today_mask.sum()
    due_week_count = due_this_week_mask.sum()
    due_month_count = due_this_month_mask.sum()
    completed_count = completed_mask.sum()
    critical_count = critical_mask.sum()
    critical_overdue = (overdue_mask & critical_mask).sum()
    
    # Compliance rate
    compliance_rate = round((completed_count / total_schedules * 100), 1) if total_schedules > 0 else 0
    
    # ============================================
    # EXECUTIVE KPI ROW
    # ============================================
    st.markdown("---")
    st.markdown("### 🎯 Executive KPIs")
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        color = "#EF4444" if overdue_count > 0 else "#10B981"
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-left:4px solid {color};box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.65rem;color:#888;text-transform:uppercase;letter-spacing:1px;">🔴 Overdue</div><div style="font-size:2rem;font-weight:800;color:{color};">{overdue_count}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-left:4px solid #F59E0B;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.65rem;color:#888;text-transform:uppercase;letter-spacing:1px;">📅 Due Today</div><div style="font-size:2rem;font-weight:800;color:#F59E0B;">{due_today_count}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-left:4px solid #3B82F6;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.65rem;color:#888;text-transform:uppercase;letter-spacing:1px;">📆 This Week</div><div style="font-size:2rem;font-weight:800;color:#3B82F6;">{due_week_count}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-left:4px solid #8B5CF6;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.65rem;color:#888;text-transform:uppercase;letter-spacing:1px;">✅ Completed</div><div style="font-size:2rem;font-weight:800;color:#8B5CF6;">{completed_count}</div></div>""", unsafe_allow_html=True)
    with c5:
        compliance_color = "#10B981" if compliance_rate >= 90 else "#F59E0B" if compliance_rate >= 70 else "#EF4444"
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-left:4px solid {compliance_color};box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.65rem;color:#888;text-transform:uppercase;letter-spacing:1px;">📈 Compliance</div><div style="font-size:2rem;font-weight:800;color:{compliance_color};">{compliance_rate}%</div></div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:1rem;text-align:center;border-left:4px solid #1a1a1a;box-shadow:0 2px 8px rgba(0,0,0,0.06);"><div style="font-size:0.65rem;color:#888;text-transform:uppercase;letter-spacing:1px;">🏗️ Total</div><div style="font-size:2rem;font-weight:800;color:#1a1a1a;">{total_schedules}</div></div>""", unsafe_allow_html=True)
    
    # ============================================
    # ALERT BANNERS
    # ============================================
    if critical_overdue > 0:
        st.error(f"🚨 **CRITICAL ALERT:** {critical_overdue} critical PPM tasks are OVERDUE! Immediate action required.")
    elif overdue_count > 0:
        st.warning(f"⚠️ **ATTENTION:** {overdue_count} PPM tasks are past due. Review and reschedule.")
    
    if compliance_rate < 70:
        st.error(f"📉 **COMPLIANCE RISK:** PPM compliance at {compliance_rate}% — below 70% threshold. Escalation recommended.")
    
    # ============================================
    # COMPLIANCE GAUGE + CHARTS
    # ============================================
    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown("### 📊 Compliance Gauge")
        
        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=compliance_rate,
            title={'text': "PPM Compliance Rate", 'font': {'size': 14}},
            delta={'reference': 90, 'increasing': {'color': "#10B981"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#CC0000" if compliance_rate < 70 else "#F59E0B" if compliance_rate < 90 else "#10B981"},
                'bgcolor': "white",
                'steps': [
                    {'range': [0, 70], 'color': '#FEE2E2'},
                    {'range': [70, 90], 'color': '#FFFBEB'},
                    {'range': [90, 100], 'color': '#ECFDF5'}
                ],
                'threshold': {
                    'line': {'color': "#CC0000", 'width': 3},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with c2:
        st.markdown("### 📅 PPM by Frequency")
        
        if "frequency" in df.columns:
            freq_counts = df["frequency"].value_counts()
            fig_freq = px.pie(
                values=freq_counts.values, 
                names=freq_counts.index,
                color_discrete_sequence=["#CC0000", "#F59E0B", "#3B82F6", "#10B981", "#8B5CF6", "#EC4899"],
                hole=0.4
            )
            fig_freq.update_layout(height=300, showlegend=True)
            fig_freq.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_freq, use_container_width=True)
    
    # ============================================
    # STATUS DISTRIBUTION CHART
    # ============================================
    st.markdown("---")
    st.markdown("### 📊 Workload Distribution")
    
    c1, c2 = st.columns(2)
    with c1:
        # By assigned team
        if "assigned_team" in df.columns:
            team_counts = df["assigned_team"].value_counts().head(8)
            fig_team = px.bar(
                x=team_counts.values, 
                y=team_counts.index, 
                orientation='h',
                title="PPM Tasks by Team",
                color=team_counts.values,
                color_continuous_scale="Reds",
                labels={"x": "Tasks", "y": ""}
            )
            fig_team.update_layout(height=350)
            st.plotly_chart(fig_team, use_container_width=True)
    
    with c2:
        # By priority
        if "priority" in df.columns:
            priority_counts = df["priority"].value_counts()
            colors_priority = {"critical": "#EF4444", "high": "#F59E0B", "medium": "#3B82F6", "low": "#10B981"}
            pie_colors = [colors_priority.get(p, "#999") for p in priority_counts.index]
            fig_priority = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                title="Tasks by Priority",
                color_discrete_sequence=pie_colors
            )
            fig_priority.update_layout(height=350)
            st.plotly_chart(fig_priority, use_container_width=True)
    
    # ============================================
    # CRITICAL OVERDUE — IMMEDIATE ATTENTION
    # ============================================
    if critical_overdue > 0:
        st.markdown("---")
        st.markdown("### 🚨 Critical Overdue — Immediate Action Required")
        
        critical_overdue_df = df[overdue_mask & critical_mask].sort_values("due_date_parsed")
        
        for _, row in critical_overdue_df.iterrows():
            days_overdue = (today - row["due_date_parsed"].date()).days if pd.notna(row.get("due_date_parsed")) else 0
            st.markdown(f"""
            <div style="background:#FEF2F2;border-left:4px solid #EF4444;border-radius:8px;padding:0.8rem;margin:0.3rem 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <b>🔴 {row.get('title','')}</b>
                        <br><span style="font-size:0.75rem;color:#991B1B;">{row.get('asset_name','') or row.get('equipment','')} | Due: {row.get('next_due_date','')} | {days_overdue} days overdue</span>
                    </div>
                    <span style="background:#EF4444;color:white;padding:3px 12px;border-radius:20px;font-size:0.7rem;font-weight:600;">CRITICAL</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================
    # TASK VIEW TABS
    # ============================================
    st.markdown("---")
    st.markdown("### 📋 PPM Task Views")
    
    task_tabs = st.tabs(["🔴 Overdue", "📅 Due Today", "📆 This Week", "📆 This Month", "✅ Completed", "📋 All Tasks"])
    
    # --- OVERDUE TAB ---
    with task_tabs[0]:
        overdue_df = df[overdue_mask].sort_values("due_date_parsed")
        if len(overdue_df) > 0:
            st.caption(f"🔴 {len(overdue_df)} overdue tasks")
            for _, row in overdue_df.iterrows():
                days_overdue = (today - row["due_date_parsed"].date()).days if pd.notna(row.get("due_date_parsed")) else 0
                is_critical = row.get("is_critical", False)
                border_color = "#EF4444" if is_critical else "#F59E0B"
                bg_color = "#FEF2F2" if is_critical else "#FFFBEB"
                
                with st.expander(f"{'🔴' if is_critical else '🟡'} {row.get('title','')} — {days_overdue}d overdue | Due: {row.get('next_due_date','')}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**Asset:** {row.get('asset_name','N/A')}")
                        st.write(f"**Frequency:** {row.get('frequency','N/A')}")
                    with c2:
                        st.write(f"**Team:** {row.get('assigned_team','N/A')}")
                        st.write(f"**Priority:** {row.get('priority','N/A').upper()}")
                    with c3:
                        st.write(f"**Status:** {row.get('status','N/A').upper()}")
                        st.write(f"**Last Done:** {row.get('last_completed_date','Never')}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Mark Complete", key=f"ppm_overdue_{row['id']}", use_container_width=True):
                            DB.update("ppm_schedules", row["id"], {"status": "completed", "last_completed_date": str(today)})
                            st.success("✅ Completed!")
                            st.rerun()
                    with c2:
                        new_due = st.date_input("Reschedule to", today + timedelta(days=7), key=f"reschedule_{row['id']}")
                        if st.button("📅 Reschedule", key=f"ppm_reschedule_{row['id']}", use_container_width=True):
                            DB.update("ppm_schedules", row["id"], {"next_due_date": str(new_due)})
                            st.success("📅 Rescheduled!")
                            st.rerun()
        else:
            st.success("🎉 No overdue tasks! All PPMs on track.")
    
    # --- DUE TODAY TAB ---
    with task_tabs[1]:
        today_df = df[due_today_mask].sort_values("due_date_parsed")
        if len(today_df) > 0:
            st.caption(f"📅 {len(today_df)} tasks due today")
            for _, row in today_df.iterrows():
                is_critical = row.get("is_critical", False)
                icon = "🔴" if is_critical else "📅"
                
                with st.expander(f"{icon} {row.get('title','')} — {row.get('frequency','')} | {row.get('assigned_team','N/A')}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**Asset:** {row.get('asset_name','N/A')}")
                        st.write(f"**Location:** {row.get('location','N/A')}")
                    with c2:
                        st.write(f"**Team:** {row.get('assigned_team','N/A')}")
                        st.write(f"**Priority:** {row.get('priority','N/A').upper()}")
                    with c3:
                        st.write(f"**Last Done:** {row.get('last_completed_date','Never')}")
                    
                    if st.button("✅ Mark Complete", key=f"ppm_today_{row['id']}", use_container_width=True):
                        DB.update("ppm_schedules", row["id"], {"status": "completed", "last_completed_date": str(today)})
                        st.success("✅ Completed!")
                        st.rerun()
        else:
            st.success("✅ No tasks due today.")
    
    # --- THIS WEEK TAB ---
    with task_tabs[2]:
        week_df = df[due_this_week_mask].sort_values("due_date_parsed")
        if len(week_df) > 0:
            st.caption(f"📆 {len(week_df)} tasks due this week ({week_start.strftime('%d %b')} - {week_end.strftime('%d %b')})")
            for _, row in week_df.iterrows():
                days_left = (row["due_date_parsed"].date() - today).days if pd.notna(row.get("due_date_parsed")) else 0
                days_label = f"{days_left}d left" if days_left >= 0 else f"{-days_left}d overdue"
                
                st.markdown(f"""
                <div style="background:white;border-radius:8px;padding:0.7rem;margin:0.2rem 0;border-left:3px solid #3B82F6;display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <b>{row.get('title','')}</b>
                        <br><span style="font-size:0.7rem;color:#666;">{row.get('assigned_team','')} | Due: {row.get('next_due_date','')}</span>
                    </div>
                    <span style="font-size:0.7rem;color:#3B82F6;font-weight:600;">{days_label}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No tasks due this week.")
    
    # --- THIS MONTH TAB ---
    with task_tabs[3]:
        month_df = df[due_this_month_mask].sort_values("due_date_parsed")
        if len(month_df) > 0:
            st.caption(f"📆 {len(month_df)} tasks due in the next 30 days")
            st.dataframe(
                month_df[[c for c in ["title", "assigned_team", "frequency", "priority", "next_due_date", "status"] if c in month_df.columns]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No tasks due this month.")
    
    # --- COMPLETED TAB ---
    with task_tabs[4]:
        completed_df = df[completed_mask].sort_values("completed_date_parsed", ascending=False) if "completed_date_parsed" in df.columns else df[completed_mask]
        if len(completed_df) > 0:
            st.caption(f"✅ {len(completed_df)} completed tasks")
            st.dataframe(
                completed_df[[c for c in ["title", "assigned_team", "frequency", "last_completed_date", "next_due_date"] if c in completed_df.columns]].head(20),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No completed tasks recorded.")
    
    # --- ALL TASKS TAB ---
    with task_tabs[5]:
        st.caption(f"📋 All {total_schedules} PPM schedules")
        
        # Search/filter
        search_ppm = st.text_input("🔍 Search PPM tasks", key="ppm_search_all")
        
        display_df = df
        if search_ppm:
            display_df = df[df["title"].str.contains(search_ppm, case=False, na=False)]
        
        st.dataframe(
            display_df[[c for c in ["title", "assigned_team", "frequency", "priority", "next_due_date", "last_completed_date", "status"] if c in display_df.columns]],
            use_container_width=True,
            hide_index=True,
            height=400
        )
    
    # ============================================
    # MANAGEMENT INSIGHTS
    # ============================================
    st.markdown("---")
    st.markdown("### 🤖 Management Insights")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if compliance_rate >= 90:
            st.success(f"✅ **Excellent:** {compliance_rate}% PPM compliance — on track for audit readiness.")
        elif compliance_rate >= 70:
            st.warning(f"⚠️ **Attention Needed:** {compliance_rate}% compliance — below 90% target. Focus on overdue tasks.")
        else:
            st.error(f"🚨 **Critical:** {compliance_rate}% compliance — immediate management intervention required.")
    
    with c2:
        if overdue_count == 0:
            st.success("✅ **Zero Overdue:** All PPM tasks are on schedule.")
        elif overdue_count <= 5:
            st.warning(f"⚠️ **Minor Backlog:** {overdue_count} tasks overdue. Address within 48 hours.")
        else:
            st.error(f"🚨 **Significant Backlog:** {overdue_count} overdue tasks. Resource allocation review needed.")
    
    with c3:
        if critical_count > 0 and critical_overdue == 0:
            st.success(f"✅ **Critical Tasks Protected:** All {critical_count} critical PPMs are on schedule.")
        elif critical_overdue > 0:
            st.error(f"🚨 **Risk Exposure:** {critical_overdue} critical tasks overdue. Potential equipment failure risk.")

# ============================================
# 52-WEEK CALENDAR (FULL)
# ============================================
def page_cal():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📅 52-Week Calendar — {info.get("full_name",fc)}')
    today=date.today()
    weeks=[]
    for w in range(1,53):
        week_start=today+timedelta(weeks=w-today.isocalendar()[1])
        weeks.append({"Week":w,"Start":week_start.strftime("%d %b"),"Status":"Upcoming" if w>today.isocalendar()[1] else "Current" if w==today.isocalendar()[1] else "Past"})
    df=pd.DataFrame(weeks)
    st.dataframe(df,use_container_width=True,hide_index=True,height=400)
    st.caption(f"📅 Current Week: {today.isocalendar()[1]} | {today.strftime('%d %B %Y')}")

# ============================================
# CHECKLIST STATUS — CONSOLIDATED DASHBOARD
# FORTUNE 500 GRADE — ASSET → SUB-ASSET DRILLDOWN
# ============================================
def page_cs():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    today = date.today()
    
    st.markdown(f'## ✅ Checklist Status — {info.get("full_name", fc)}')
    
    all_assets = DB.get_assets(fc, 50000)
    
    if not all_assets:
        st.info("No assets registered.")
        return
    
    df = pd.DataFrame(all_assets)
    
    # Clean up checklist values
    df["checklist_clean"] = df["checklist"].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() not in ["", "NA", "na", "APPLICABLE", "NOTAPPLICABLE", "None"] else None)
    
    # Get templates
    templates = supabase.table("ppm_checklist_templates").select("*").execute()
    template_names = [t.get("template_name","") for t in templates.data] if templates.data else []
    
    # ============================================
    # FILTERS — ASSET → SUB-ASSET DRILLDOWN
    # ============================================
    st.markdown("### 🔍 Filter Assets")
    
    # Create department — sub_division labels
    df["dept_full"] = df.apply(lambda row: f"{row['department']} — {row['sub_division']}" if pd.notna(row.get('sub_division')) and row.get('sub_division') not in ['', 'N/A', 'NA'] else row['department'], axis=1)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        departments = ["All"] + sorted(df["dept_full"].dropna().unique().tolist())
        sel_dept = st.selectbox("Select Department", departments, key="cs_dept")
    
    # Filter by department
    if sel_dept != "All":
        dept_df = df[df["dept_full"] == sel_dept]
    else:
        dept_df = df.copy()
    
    with c2:
        # Asset = parent_asset
        asset_list = ["All"] + sorted(dept_df["parent_asset"].dropna().unique().tolist())
        sel_asset = st.selectbox("Select Asset", asset_list, key="cs_asset")
    
    # Filter by asset (parent)
    if sel_asset != "All":
        asset_df = dept_df[dept_df["parent_asset"] == sel_asset]
    else:
        asset_df = dept_df.copy()
    
    with c3:
        # Sub-Asset = name
        sub_list = ["All"] + sorted(asset_df["name"].dropna().unique().tolist())
        sel_sub = st.selectbox("Select Sub Asset", sub_list, key="cs_sub")
    
    with c4:
        bldg_list = ["All"] + sorted(df["location_building"].dropna().unique().tolist())
        sel_bldg = st.selectbox("Building", bldg_list, key="cs_bldg")
    
    # Date range
    c1, c2 = st.columns(2)
    with c1:
        from_date = st.date_input("From Date", today - timedelta(days=30), key="cs_from")
    with c2:
        to_date = st.date_input("To Date", today, key="cs_to")
    
    # Apply all filters
    filtered = df.copy()
    if sel_dept != "All": filtered = filtered[filtered["dept_full"] == sel_dept]
    if sel_asset != "All": filtered = filtered[filtered["parent_asset"] == sel_asset]
    if sel_sub != "All": filtered = filtered[filtered["name"] == sel_sub]
    if sel_bldg != "All": filtered = filtered[filtered["location_building"] == sel_bldg]
    
    total_filtered = len(filtered)
    enrolled_count = len(filtered[filtered["checklist_clean"].notna()])
    not_enrolled = total_filtered - enrolled_count
    
    st.markdown("---")
    
    # ============================================
    # CHECKLIST TYPE TABS
    # ============================================
    st.markdown("### 📋 Checklist Reports")
    
    checklist_tabs = st.tabs(["📅 Scheduled PPM", "📋 Daily Checklist", "⏰ Hourly Checklist", "📊 Summary", "📋 Consolidated Report"])
    
    # ============================================
    # TAB 0: SCHEDULED PPM
    # ============================================
    with checklist_tabs[0]:
        st.markdown("#### 📅 Scheduled PPM Checklist Status")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📋 Total", total_filtered)
        with c2: st.metric("⏳ Pending", not_enrolled)
        with c3: st.metric("✅ Enrolled", enrolled_count)
        
        st.markdown("---")
        
        # Search bar
        cs_search_main = st.text_input("🔍 Search Asset or Sub-Asset", key="cs_search_main", placeholder="Type to filter assets...")
        
        # Apply search filter
        if cs_search_main:
            mask = filtered["parent_asset"].str.contains(cs_search_main, case=False, na=False) | filtered["name"].str.contains(cs_search_main, case=False, na=False)
            display_filtered = filtered[mask]
        else:
            display_filtered = filtered.copy()
        
        total_display = len(display_filtered)
        
        # Pagination
        page_size = 20
        if "cs_page_scheduled" not in st.session_state:
            st.session_state.cs_page_scheduled = 1
        
        total_pages = max(1, (total_display + page_size - 1) // page_size)
        start = (st.session_state.cs_page_scheduled - 1) * page_size
        end = min(start + page_size, total_display)
        
        page_data = display_filtered.iloc[start:end]
        
        # Pagination controls
        c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 1, 1])
        with c1:
            if st.button("◀◀", key="cs_first"): st.session_state.cs_page_scheduled = 1; st.rerun()
        with c2:
            if st.button("◀", key="cs_prev") and st.session_state.cs_page_scheduled > 1:
                st.session_state.cs_page_scheduled -= 1; st.rerun()
        with c3:
            st.markdown(f"**Page {st.session_state.cs_page_scheduled} of {total_pages}**")
        with c4:
            if st.button("▶", key="cs_next") and st.session_state.cs_page_scheduled < total_pages:
                st.session_state.cs_page_scheduled += 1; st.rerun()
        with c5:
            if st.button("▶▶", key="cs_last"): st.session_state.cs_page_scheduled = total_pages; st.rerun()
        
        st.caption(f"Showing {start+1}–{end} of {total_display} assets")
        
        for _, asset in page_data.iterrows():
            enrolled = pd.notna(asset.get("checklist_clean"))
            border = "#10B981" if enrolled else "#e5e7eb"
            bg = "#ECFDF5" if enrolled else "#fafafa"
            badge = "✅ Enrolled" if enrolled else "⚠️ Not Enrolled"
            badge_bg = "#10B981" if enrolled else "#F59E0B"
            checklist_name = asset.get("checklist_clean") if enrolled else "Not Enrolled"
            
            st.markdown(f"""
            <div style="background:{bg};border-left:3px solid {border};border-radius:6px;padding:0.5rem;margin:0.2rem 0;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <b>{asset.get('parent_asset','N/A')}</b> → {asset.get('name','N/A')[:60]}
                    <br><span style="font-size:0.65rem;color:#666;">📋 {checklist_name} | 📅 {asset.get('ppm_frequency', asset.get('verification_frequency', 'N/A'))}</span>
                </div>
                <span style="background:{badge_bg};color:white;padding:2px 10px;border-radius:12px;font-size:0.6rem;font-weight:600;">{badge}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================
    # TAB 1: DAILY CHECKLIST
    # ============================================
    with checklist_tabs[1]:
        st.markdown("#### 📋 Daily Checklist Status")
        
        daily_assets = filtered[filtered["verification_frequency"].isin(["Daily","daily"])] if "verification_frequency" in filtered.columns else pd.DataFrame()
        
        c1, c2 = st.columns(2)
        with c1: st.metric("📋 Total Daily", len(daily_assets))
        with c2: st.metric("⏳ Pending Today", len(daily_assets))
        
        st.markdown("---")
        
        if len(daily_assets) > 0:
            for _, asset in daily_assets.head(20).iterrows():
                st.markdown(f"""
                <div style="background:white;border-left:3px solid #3B82F6;border-radius:6px;padding:0.5rem;margin:0.2rem 0;">
                    <b>{asset.get('parent_asset','N/A')}</b> → {asset.get('name','N/A')[:60]}
                    <br><span style="font-size:0.65rem;color:#666;">📍 {asset.get('location_building','')} | 📅 Daily</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No daily checklist assets found.")
    
    # ============================================
    # TAB 2: HOURLY CHECKLIST
    # ============================================
    with checklist_tabs[2]:
        st.markdown("#### ⏰ Hourly Checklist Status")
        
        hourly_assets = filtered[filtered["verification_frequency"].isin(["Hourly","hourly","Bi-Weekly"])] if "verification_frequency" in filtered.columns else pd.DataFrame()
        
        c1, c2 = st.columns(2)
        with c1: st.metric("📋 Total Hourly/Bi-Weekly", len(hourly_assets))
        with c2: st.metric("⏳ Pending", len(hourly_assets))
        
        st.markdown("---")
        
        if len(hourly_assets) > 0:
            for _, asset in hourly_assets.head(20).iterrows():
                st.markdown(f"""
                <div style="background:white;border-left:3px solid #8B5CF6;border-radius:6px;padding:0.5rem;margin:0.2rem 0;">
                    <b>{asset.get('parent_asset','N/A')}</b> → {asset.get('name','N/A')[:60]}
                    <br><span style="font-size:0.65rem;color:#666;">📍 {asset.get('location_building','')} | ⏰ {asset.get('verification_frequency','N/A')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hourly checklist assets found.")
    
    # ============================================
    # TAB 3: SUMMARY + BULK ENROLLMENT
    # ============================================
    with checklist_tabs[3]:
        st.markdown("#### 📊 Checklist Summary")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div style="background:white;border-radius:10px;padding:1rem;text-align:center;border-top:3px solid #CC0000;"><div style="font-size:0.6rem;color:#888;">Total Assets</div><div style="font-size:1.8rem;font-weight:800;">{total_filtered}</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="background:white;border-radius:10px;padding:1rem;text-align:center;border-top:3px solid #10B981;"><div style="font-size:0.6rem;color:#888;">✅ Enrolled</div><div style="font-size:1.8rem;font-weight:800;color:#10B981;">{enrolled_count}</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div style="background:white;border-radius:10px;padding:1rem;text-align:center;border-top:3px solid #F59E0B;"><div style="font-size:0.6rem;color:#888;">⏳ Pending</div><div style="font-size:1.8rem;font-weight:800;color:#F59E0B;">{not_enrolled}</div></div>""", unsafe_allow_html=True)
        with c4:
            rate = round(enrolled_count/total_filtered*100,1) if total_filtered > 0 else 0
            st.markdown(f"""<div style="background:white;border-radius:10px;padding:1rem;text-align:center;border-top:3px solid #3B82F6;"><div style="font-size:0.6rem;color:#888;">Enrollment Rate</div><div style="font-size:1.8rem;font-weight:800;color:#3B82F6;">{rate}%</div></div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Template reference
        st.markdown("### 📋 Available International Standard Templates")
        if templates.data:
            for t in templates.data:
                items_count = 0
                try:
                    items_res = supabase.table("ppm_checklist_items").select("id", count="exact").eq("template_id", t["id"]).execute()
                    items_count = items_res.count or 0
                except: pass
                
                st.markdown(f"""
                <div style="background:white;border-radius:8px;padding:0.6rem;margin:0.2rem 0;border-left:4px solid #3B82F6;">
                    <b>{t.get('template_name','')}</b> — {t.get('international_standard','')}
                    <br><span style="font-size:0.65rem;color:#666;">📋 {items_count} items | 🏷️ {t.get('asset_category','')}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Bulk enrollment
        st.markdown("---")
        st.markdown("### 📦 Bulk Enrollment")
        st.caption("Enroll all currently filtered assets with a checklist template.")
        
        with st.form("cs_bulk_enroll"):
            c1, c2, c3 = st.columns(3)
            with c1:
                bulk_template = st.selectbox("Checklist Template", template_names, key="cs_bulk_tpl")
            with c2:
                bulk_freq = st.selectbox("PPM Frequency", ["Daily","Weekly","Bi-Weekly","Monthly","Quarterly","Half-Yearly","Yearly"], key="cs_bulk_freq")
            with c3:
                overwrite_existing = st.checkbox("Overwrite existing", value=True, key="cs_bulk_overwrite")
            
            st.caption(f"📋 {len(filtered)} assets will be enrolled with **{bulk_template}** at **{bulk_freq}** frequency")
            
            if st.form_submit_button("🚀 ENROLL ASSETS", use_container_width=True, type="primary"):
                if bulk_template:
                    count = 0
                    skipped = 0
                    for _, asset in filtered.iterrows():
                        is_enrolled = pd.notna(asset.get("checklist_clean"))
                        if is_enrolled and not overwrite_existing:
                            skipped += 1
                            continue
                        DB.update("assets", asset["id"], {
                            "checklist": bulk_template,
                            "ppm_frequency": bulk_freq,
                            "checklist_template": bulk_template
                        })
                        
                        # Also create PPM schedule record for calendar
                        # Get template schedule dates
                        template_dates = None
                        tpl_res = supabase.table("ppm_checklist_templates").select("schedule_dates").eq("template_name", bulk_template).single().execute()
                        if tpl_res.data and tpl_res.data.get("schedule_dates"):
                            template_dates = tpl_res.data["schedule_dates"].split(",")
                        
                        if template_dates:
                            for d in template_dates:
                                d = d.strip()
                                try:
                                    parsed_date = datetime.strptime(d, "%d-%m-%Y").strftime("%Y-%m-%d")
                                except:
                                    try:
                                        parsed_date = datetime.strptime(d, "%Y-%m-%d").strftime("%Y-%m-%d")
                                    except:
                                        parsed_date = str(date.today())
                                
                                supabase.table("ppm_schedules").insert({
                                    "facility_code": fc,
                                    "asset_id": asset.get("id"),
                                    "title": f"{asset.get('name','PPM')} - {bulk_template}",
                                    "frequency": bulk_freq,
                                    "status": "scheduled",
                                    "assigned_team": asset.get("department", ""),
                                    "next_due_date": parsed_date,
                                    "created_at": datetime.now().isoformat()
                                }).execute()
                        else:
                            supabase.table("ppm_schedules").insert({
                                "facility_code": fc,
                                "asset_id": asset.get("id"),
                                "title": f"{asset.get('name','PPM')} - {bulk_template}",
                                "frequency": bulk_freq,
                                "status": "scheduled",
                                "assigned_team": asset.get("department", ""),
                                "next_due_date": str(date.today()),
                                "created_at": datetime.now().isoformat()
                            }).execute()
                        
                        count += 1
                    
                    msg = f"✅ {count} assets enrolled with {bulk_template}!"
                    if skipped > 0:
                        msg += f" ({skipped} skipped — already enrolled)"
                    st.success(msg)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ Please select a template")
    
    # ============================================
    # TAB 4: CONSOLIDATED REPORT
    # ============================================
    with checklist_tabs[4]:
        st.markdown("#### 📋 Consolidated Checklist Report")
        
        # Build consolidated data
        consolidated = []
        for _, asset in filtered.iterrows():
            enrolled = pd.notna(asset.get("checklist_clean"))
            
            consolidated.append({
                "SNO": len(consolidated) + 1,
                "Asset": asset.get("parent_asset", "N/A"),
                "Sub Asset": asset.get("name", "N/A"),
                "Checklist Name": asset.get("checklist_clean") if enrolled else "Not Enrolled",
                "Frequency": asset.get("ppm_frequency", asset.get("verification_frequency", "N/A")),
                "Date": str(today),
                "Status": "Enrolled" if enrolled else "Pending"
            })
        
        cons_df = pd.DataFrame(consolidated)
        
        # Filters
        c1, c2, c3 = st.columns(3)
        with c1:
            cons_status = st.selectbox("Status", ["All", "Enrolled", "Pending"], key="cons_status")
        with c2:
            cons_freq = st.selectbox("Frequency", ["All", "Daily", "Weekly", "Bi-Weekly", "Monthly", "Quarterly", "Half-Yearly", "Yearly"], key="cons_freq")
        with c3:
            cons_search = st.text_input("🔍 Search Asset or Checklist", key="cons_search", placeholder="Search...")
        
        display_cons = cons_df.copy()
        if cons_status != "All":
            display_cons = display_cons[display_cons["Status"] == cons_status]
        if cons_freq != "All":
            display_cons = display_cons[display_cons["Frequency"] == cons_freq]
        if cons_search:
            mask = display_cons["Asset"].str.contains(cons_search, case=False, na=False) | display_cons["Sub Asset"].str.contains(cons_search, case=False, na=False) | display_cons["Checklist Name"].str.contains(cons_search, case=False, na=False)
            display_cons = display_cons[mask]
        
        # Counts
        if len(display_cons) > 0:
            enrolled_total = len(display_cons[display_cons["Status"] == "Enrolled"])
            pending_total = len(display_cons[display_cons["Status"] == "Pending"])
        else:
            enrolled_total = 0
            pending_total = 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📋 Total", len(display_cons))
        with c2: st.metric("⏳ Pending", pending_total)
        with c3: st.metric("✅ Enrolled", enrolled_total)
        
        st.markdown("---")
        
        # Pagination
        page_size = 25
        if "cons_page" not in st.session_state:
            st.session_state.cons_page = 1
        
        total_pages_cons = max(1, (len(display_cons) + page_size - 1) // page_size)
        start_cons = (st.session_state.cons_page - 1) * page_size
        end_cons = min(start_cons + page_size, len(display_cons))
        
        page_data_cons = display_cons.iloc[start_cons:end_cons]
        
        c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 1, 1])
        with c1:
            if st.button("◀◀", key="cons_first"): st.session_state.cons_page = 1; st.rerun()
        with c2:
            if st.button("◀", key="cons_prev") and st.session_state.cons_page > 1:
                st.session_state.cons_page -= 1; st.rerun()
        with c3:
            st.markdown(f"**Page {st.session_state.cons_page} of {total_pages_cons}**")
        with c4:
            if st.button("▶", key="cons_next") and st.session_state.cons_page < total_pages_cons:
                st.session_state.cons_page += 1; st.rerun()
        with c5:
            if st.button("▶▶", key="cons_last"): st.session_state.cons_page = total_pages_cons; st.rerun()
        
        st.caption(f"Showing {start_cons+1}–{end_cons} of {len(display_cons)} records")
        
        if len(page_data_cons) > 0:
            for _, row in page_data_cons.iterrows():
                is_enrolled_row = row["Status"] == "Enrolled"
                border = "#10B981" if is_enrolled_row else "#F59E0B"
                bg = "#ECFDF5" if is_enrolled_row else "#FFFBEB"
                badge = "✅ Enrolled" if is_enrolled_row else "⏳ Pending"
                badge_bg = "#10B981" if is_enrolled_row else "#F59E0B"
                
                st.markdown(f"""
                <div style="background:{bg};border-left:3px solid {border};border-radius:6px;padding:0.5rem;margin:0.2rem 0;display:flex;justify-content:space-between;align-items:center;">
                    <div style="flex:1;">
                        <b>#{row['SNO']} {row['Asset']}</b>
                        <br><span style="font-size:0.65rem;color:#666;">└ {row['Sub Asset'][:80]}</span>
                        <br><span style="font-size:0.6rem;color:#888;">📋 {row['Checklist Name']} | 📅 {row['Frequency']} | {row['Date']}</span>
                    </div>
                    <span style="background:{badge_bg};color:white;padding:3px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;white-space:nowrap;">{badge}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No records match your filters.")
        
        # Export
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download CSV", display_cons.to_csv(index=False), f"consolidated_checklist_{today}.csv", "text/csv", use_container_width=True)
        with c2:
            st.download_button("📥 Download HTML", display_cons.to_html(index=False), f"consolidated_checklist_{today}.html", "text/html", use_container_width=True)


# ============================================
# INCIDENT CHECK (FULL)
# ============================================
def page_ic():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🚨 Incident Intelligence — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 View Incidents","➕ Report Incident"])
    with tab1:
        inc=DB.get_all("incidents",fc,50)
        if inc:st.dataframe(pd.DataFrame(inc),use_container_width=True,hide_index=True)
        else:st.success("✅ No incidents reported")
    with tab2:
        with st.form("inc_form"):
            st.markdown("### Report New Incident")
            c1,c2=st.columns(2)
            with c1:
                title=st.text_input("Title*");dept=st.selectbox("Department*",[
    "Engineering — Civil & Structural","Engineering — Electrical","Engineering — HVAC",
    "Engineering — Plumbing","Engineering — Vertical Transportation (Lifts)",
    "Engineering — Fire Fighting","Engineering — Utilities & Energy",
    "Facility Management — Hard Services","Facility Management — Soft Services (Housekeeping)",
    "Facility Management — FM Operations & Helpdesk","Facility Management — HSSE Safety & Compliance",
    "Technology Group — Network & Connectivity","Technology Group — Building Technology",
    "Security — Man Guarding Operations",
    "Contractor — Clyde Engineering","Contractor — Gates and Shield"
])
                itype=st.selectbox("Incident Type",["Safety","Security","Environmental","Equipment Failure","Fire","Water Leak","Power Outage","Other"])
                sev=st.selectbox("Severity",["low","medium","high","critical"])
                pri=st.selectbox("Priority",["low","medium","high","critical"])
            with c2:
                loc_b=st.text_input("Building");loc_f=st.text_input("Floor");loc_z=st.text_input("Zone")
                idate=st.date_input("Incident Date",date.today());itime=st.time_input("Incident Time",datetime.now().time())
                cat=st.selectbox("Category",["Property Damage","Injury","Near Miss","Environmental","Equipment","Other"])
            desc=st.text_area("Description*");actions=st.text_area("Immediate Actions Taken")
            root=st.text_area("Root Cause Analysis (if known)")
            if st.form_submit_button("🚨 Report Incident",use_container_width=True):
                if title and desc:
                    cnt=len(DB.get_all("incidents",fc,1000))
                    DB.insert("incidents",{"facility_code":fc,"incident_number":f"INC-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"department":dept,"type":itype,"severity":sev,"priority":pri,"category":cat,"location_building":loc_b,"location_floor":loc_f,"location_zone":loc_z,"incident_date":str(idate),"incident_time":str(itime),"description":desc,"immediate_actions":actions,"root_cause":root,"status":"reported","reported_at":datetime.now().isoformat(),"reported_by_name":st.session_state.get("user_name","Staff")})
                    st.success("Incident reported!");st.rerun()


# ============================================
# WORK ORDERS (STUB)
# ============================================
def page_wo():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📋 Work Orders — {info.get("full_name",fc)}')
    st.info("🚧 Work Orders module — full deployment in progress.")

# ============================================
# HOTO CHECK (STUB)
# ============================================
def page_hot():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🔄 HOTO Check — {info.get("full_name",fc)}')
    st.info("🚧 HOTO (Handover-Takeover) module — full deployment in progress.")

# ============================================
# MONTHLY MIS (STUB)
# ============================================
def page_mis():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📊 Monthly MIS — {info.get("full_name",fc)}')
    st.info("🚧 Monthly MIS Reports module — full deployment in progress.")


# ============================================
# PPM ACTIVITIES — FORTUNE 500 EXECUTION CENTER
# CUSTOM CHECKLISTS • DAILY/HOURLY/SCHEDULED
# ROLE-BASED • DEPARTMENT-FILTERED • AI-POWERED
# ============================================
def page_ppm_activities():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    user_role = st.session_state.get("user_role", "staff")
    user_name = st.session_state.get("user_name", "Team Member")
    user_depts = safe_parse_permissions(st.session_state.get("user", {}).get("department_permissions", []))
    is_admin = user_role in ["admin", "approver"]
    
    st.markdown(f'## 🔧 PPM Execution Center — {info.get("full_name", fc)}')
    
    all_assets = DB.get_assets(fc, 50000)
    
    if not all_assets:
        st.info("No assets registered.")
        return
    
    df = pd.DataFrame(all_assets)
    df["checklist_clean"] = df["checklist"].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() not in ["", "NA", "na", "APPLICABLE", "NOTAPPLICABLE", "None"] else None)
    df["dept_full"] = df.apply(lambda row: f"{row['department']} — {row['sub_division']}" if pd.notna(row.get('sub_division')) and row.get('sub_division') not in ['', 'N/A', 'NA'] else row['department'], axis=1)
    
    # Role-based department restriction
    if is_admin:
        allowed_depts = sorted(df["dept_full"].dropna().unique().tolist())
    elif user_depts and len(user_depts) > 0 and user_depts != ["All"]:
        allowed_depts = [d for d in sorted(df["dept_full"].dropna().unique().tolist()) if any(ud in d for ud in user_depts)]
        if not allowed_depts: allowed_depts = sorted(df["dept_full"].dropna().unique().tolist())
    else:
        allowed_depts = sorted(df["dept_full"].dropna().unique().tolist())
    
    # Get custom checklists from database
    custom_checklists = supabase.table("ppm_checklist_templates").select("*").execute()
    checklist_options = ["Standard Template"] + [c.get("template_name","") for c in custom_checklists.data] if custom_checklists.data else ["Standard Template"]
    
    # ============================================
    # MAIN TABS
    # ============================================
    tabs = st.tabs(["🔧 Execute PPM", "📋 Daily Checklist", "⏰ Hourly Checklist", "📊 My Submissions", "⏳ Pending Approval", "⚙️ Checklist Builder", "📋 Manage Schedules"])

    
    # ============================================
    # TAB 0: EXECUTE PPM (SCHEDULED)
    # ============================================
    with tabs[0]:
        st.markdown("### 🔧 Execute Scheduled PPM")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            sel_dept = st.selectbox("Select Department*", ["Select..."] + allowed_depts, key="ppm_dept")
        
        if sel_dept != "Select...":
            dept_df = df[df["dept_full"] == sel_dept]
            
            with c2:
                asset_list = ["Select..."] + sorted(dept_df["parent_asset"].dropna().unique().tolist())
                sel_asset = st.selectbox("Select Asset*", asset_list, key="ppm_asset")
            
            if sel_asset != "Select...":
                asset_df = dept_df[dept_df["parent_asset"] == sel_asset]
                
                with c3:
                    sub_list = ["Select..."] + sorted(asset_df["name"].dropna().unique().tolist())
                    sel_sub = st.selectbox("Select Sub Asset*", sub_list, key="ppm_sub")
                
                if sel_sub != "Select...":
                    selected_asset = asset_df[asset_df["name"] == sel_sub].iloc[0]
                    
                    with c4:
                        st.markdown(f"""
                        <div style="background:#EFF6FF;border-radius:8px;padding:0.6rem;text-align:center;border:1px solid #BFDBFE;margin-top:0.5rem;">
                            <div style="font-size:0.6rem;color:#2563EB;">📋 Frequency</div>
                            <div style="font-weight:700;font-size:0.8rem;">{selected_asset.get('ppm_frequency', selected_asset.get('verification_frequency', 'Monthly'))}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Asset details card
                    st.markdown(f"""
                    <div style="background:white;border-radius:10px;padding:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:1rem;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <h4 style="margin:0;">{sel_asset}</h4>
                                <p style="margin:0;color:#666;font-size:0.8rem;">{sel_sub[:80]}</p>
                            </div>
                            <div style="text-align:right;">
                                <span style="background:#3B82F6;color:white;padding:3px 10px;border-radius:12px;font-size:0.6rem;">{selected_asset.get('dept_full','')}</span>
                                <br><span style="font-size:0.6rem;color:#888;">📍 {selected_asset.get('location_building','')}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # ============================================
                    # DYNAMIC CHECKLIST — CUSTOMIZABLE
                    # ============================================
                    st.markdown("### 📝 PPM Checklist")
                    
                    # Select checklist template
                    sel_checklist = st.selectbox("Select Checklist Template", checklist_options, key="ppm_checklist_template")
                    
                    # Build checklist items
                    checklist_items = []
                    
                    if sel_checklist == "Standard Template":
                        checklist_items = [
                            {"item_number": 1, "description": "Safety Precautions & Pre-Checks", "check_type": "section", "options": None},
                            {"item_number": 2, "description": "LOTO (Lock-Out/Tag-Out): Power isolated and locked out", "check_type": "yes_no", "options": None},
                            {"item_number": 3, "description": "PPE: Appropriate PPE worn (gloves, safety glasses)", "check_type": "yes_no", "options": None},
                            {"item_number": 4, "description": "Work Area Assessment: Area clear of obstructions", "check_type": "status", "options": ["Clear", "Not Clear"]},
                            {"item_number": 5, "description": "Permits: All necessary work permits obtained", "check_type": "yes_no", "options": None},
                            {"item_number": 6, "description": "Visual Inspection - Unit casing for damage, cleanliness", "check_type": "yes_no", "options": None},
                            {"item_number": 7, "description": "Air Filter(s) - Inspect for cleanliness and damage", "check_type": "status", "options": ["Clean", "Dirty", "Replaced"]},
                            {"item_number": 8, "description": "Fan & Motor - Check for unusual noise, vibration", "check_type": "status", "options": ["Normal", "Abnormal"]},
                            {"item_number": 9, "description": "Condensate Drain - Inspect drain pan", "check_type": "status", "options": ["Good", "Damage", "Dirty"]},
                            {"item_number": 10, "description": "Electrical - Check wiring for damage, loose connections", "check_type": "yes_no", "options": None},
                            {"item_number": 11, "description": "Measure air-on temperature (°C)", "check_type": "reading", "options": None},
                            {"item_number": 12, "description": "Measure air-off temperature (°C)", "check_type": "reading", "options": None},
                            {"item_number": 13, "description": "Record voltage parameters - RY", "check_type": "reading", "options": None},
                            {"item_number": 14, "description": "Record voltage parameters - YB", "check_type": "reading", "options": None},
                            {"item_number": 15, "description": "Record voltage parameters - BR", "check_type": "reading", "options": None},
                            {"item_number": 16, "description": "Record Amps parameters - R", "check_type": "reading", "options": None},
                            {"item_number": 17, "description": "Record Amps parameters - Y", "check_type": "reading", "options": None},
                            {"item_number": 18, "description": "Record Amps parameters - B", "check_type": "reading", "options": None},
                            {"item_number": 19, "description": "Check earthing connections of the panel", "check_type": "status", "options": ["Tight", "Loose"]},
                            {"item_number": 20, "description": "Check BMS integration units", "check_type": "yes_no", "options": None},
                            {"item_number": 21, "description": "Replace defective indication lamps", "check_type": "yes_no", "options": None},
                            {"item_number": 22, "description": "Observations / abnormality If any", "check_type": "text", "options": None},
                        ]
                    else:
                        # Load from database
                        matched = None
                        for c in custom_checklists.data if custom_checklists.data else []:
                            if c.get("template_name") == sel_checklist:
                                matched = c
                                break
                        if matched:
                            items_res = supabase.table("ppm_checklist_items").select("*").eq("template_id", matched["id"]).order("sort_order").execute()
                            if items_res.data:
                                for item in items_res.data:
                                    opts = item.get("expected_value","").split("/") if item.get("expected_value") else None
                                    checklist_items.append({
                                        "item_number": item.get("item_number"),
                                        "description": item.get("description"),
                                        "check_type": item.get("check_type", "yes_no"),
                                        "options": opts if len(opts) > 1 else None
                                    })
                    
                    # ============================================
                    # RENDER DYNAMIC CHECKLIST
                    # ============================================
                    with st.form("ppm_execution_form", clear_on_submit=True):
                        checklist_results = []
                        has_issues = False
                        
                        for item in checklist_items:
                            item_num = item.get("item_number", len(checklist_results)+1)
                            item_type = item.get("check_type", "yes_no")
                            item_desc = item.get("description", "")
                            item_opts = item.get("options")
                            
                            # Section headers
                            if item_type == "section":
                                st.markdown(f"### {item_desc}")
                                continue
                            
                            st.markdown(f"**{item_num}. {item_desc}**")
                            
                            c1, c2 = st.columns([1, 2])
                            
                            if item_type == "yes_no":
                                with c1:
                                    result = st.selectbox("Status", ["Yes", "No"], key=f"yn_{item_num}")
                                with c2:
                                    comment = st.text_input("Comment", key=f"cmt_{item_num}", placeholder="Optional note...")
                                if result == "No": has_issues = True
                                checklist_results.append({"item_number": item_num, "description": item_desc, "result": result, "actual_value": comment, "risk_level": "None"})
                            
                            elif item_type == "status" and item_opts:
                                with c1:
                                    result = st.selectbox("Status", item_opts, key=f"st_{item_num}")
                                with c2:
                                    comment = st.text_input("Comment", key=f"cmt_{item_num}", placeholder="Optional note...")
                                if result in ["Damage", "Dirty", "Abnormal", "Loose", "Not Clear", "Fault"]: has_issues = True
                                checklist_results.append({"item_number": item_num, "description": item_desc, "result": result, "actual_value": comment, "risk_level": "None"})
                            
                            elif item_type == "reading":
                                with c1:
                                    reading = st.text_input("Reading", key=f"rd_{item_num}", placeholder="Enter value...")
                                with c2:
                                    unit = st.text_input("Unit", key=f"un_{item_num}", placeholder="°C, V, A...")
                                checklist_results.append({"item_number": item_num, "description": item_desc, "result": "Reading", "actual_value": f"{reading} {unit}".strip(), "risk_level": "None"})
                            
                            elif item_type == "text":
                                with c1:
                                    text_val = st.text_area("Observation", key=f"txt_{item_num}", height=60)
                                checklist_results.append({"item_number": item_num, "description": item_desc, "result": "Noted", "actual_value": text_val, "risk_level": "None"})
                            
                            else:
                                with c1:
                                    result = st.selectbox("Status", ["Pass", "Fail", "N/A"], key=f"df_{item_num}")
                                with c2:
                                    comment = st.text_input("Comment", key=f"cmt_{item_num}", placeholder="Optional note...")
                                if result == "Fail": has_issues = True
                                checklist_results.append({"item_number": item_num, "description": item_desc, "result": result, "actual_value": comment, "risk_level": "None"})
                            
                            st.markdown("---")
                        
                        # Mitigation section
                        if has_issues:
                            st.markdown("### 🚨 Mitigation Plan (Required)")
                            mitigation_plan = st.text_area("Describe mitigation actions*", height=80, placeholder="Required when items fail...")
                            c1, c2 = st.columns(2)
                            with c1: mitigation_deadline = st.date_input("Mitigation Deadline", date.today() + timedelta(days=7))
                            with c2: st.markdown("<br>", unsafe_allow_html=True)
                        else:
                            mitigation_plan, mitigation_deadline = "", None
                        
                        # Photo evidence
                        st.markdown("### 📸 Photo Evidence (Required)")
                        uploaded_photos = st.file_uploader("Upload photos", type=["png","jpg","jpeg"], accept_multiple_files=True, key="ppm_photos")
                        
                        # Schedule
                        st.markdown("### 📅 Schedule")
                        c1, c2, c3 = st.columns(3)
                        with c1: execution_date = st.date_input("Execution Date", date.today())
                        with c2: execution_time = st.time_input("Execution Time", datetime.now().time())
                        with c3:
                            is_early = st.checkbox("Early Execution (requires approval)")
                            ppm_type = st.selectbox("PPM Type", ["Scheduled PPM", "Daily Checklist", "Hourly Checklist"], key="ppm_type_select")
                        
                        early_reason = ""
                        if is_early:
                            early_reason = st.text_area("Reason for Early Execution*", height=60)
                        
                        execution_comments = st.text_area("Execution Notes", height=60)
                        
                        submitted = st.form_submit_button("✅ SUBMIT PPM EXECUTION", use_container_width=True, type="primary")
                        
                        if submitted:
                            errors = []
                            if not uploaded_photos: errors.append("Photo evidence is required")
                            if has_issues and not mitigation_plan: errors.append("Mitigation plan required")
                            if is_early and not early_reason: errors.append("Reason required for early execution")
                            
                            if errors:
                                for e in errors: st.error(f"⚠️ {e}")
                            else:
                                exec_data = {
                                    "facility_code": fc,
                                    "executed_by_name": user_name,
                                    "execution_date": str(execution_date),
                                    "status": "submitted",
                                    "created_at": datetime.now().isoformat()
                                }
                                
                                exec_result = supabase.table("ppm_executions").insert(exec_data).execute()
                                if exec_result.data:
                                    exec_result = exec_result.data[0]
                                else:
                                    exec_result = None
                                
                                if exec_result:
                                    execution_id = exec_result["id"]
                                    for item_result in checklist_results:
                                        supabase.table("ppm_execution_items").insert({
                                            "execution_id": execution_id,
                                            "item_number": int(item_result.get("item_number", 1)),
                                            "description": str(item_result.get("description", "N/A")),
                                            "result": str(item_result.get("result", "pass")),
                                            "actual_value": str(item_result.get("actual_value", "")),
                                            "created_at": datetime.now().isoformat()
                                        }).execute()
                                    
                                    supabase.table("ppm_approvals").insert({
                                        "execution_id": execution_id,
                                        "approval_level": "team_lead",
                                        "status": "pending",
                                        "created_at": datetime.now().isoformat()
                                    }).execute()
                                    supabase.table("ppm_approvals").insert({
                                        "execution_id": execution_id,
                                        "approval_level": "manager",
                                        "status": "pending",
                                        "created_at": datetime.now().isoformat()
                                    }).execute()


                                    
                                    st.success("✅ PPM Execution submitted!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to submit.")
    
    # ============================================
    # TAB 1: DAILY CHECKLIST
    # ============================================
    with tabs[1]:
        st.markdown("### 📋 Daily Checklist Execution")
        
        daily_assets = df[df["verification_frequency"].isin(["Daily","daily"])] if "verification_frequency" in df.columns else pd.DataFrame()
        
        if len(daily_assets) == 0:
            st.info("No daily checklist assets found. Assets with 'Daily' verification frequency will appear here.")
        else:
            c1, c2 = st.columns(2)
            with c1: st.metric("📋 Daily Assets", len(daily_assets))
            with c2: st.metric("⏳ Pending Today", len(daily_assets))
            
            st.markdown("---")
            
            sel_daily_dept = st.selectbox("Department", ["All"] + sorted(daily_assets["dept_full"].dropna().unique().tolist()), key="daily_dept")
            
            display_daily = daily_assets.copy()
            if sel_daily_dept != "All":
                display_daily = display_daily[display_daily["dept_full"] == sel_daily_dept]
            
            for _, asset in display_daily.head(20).iterrows():
                st.markdown(f"""
                <div style="background:white;border-left:3px solid #3B82F6;border-radius:6px;padding:0.5rem;margin:0.2rem 0;display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <b>{asset.get('parent_asset','N/A')}</b> — {asset.get('name','N/A')[:50]}
                        <br><span style="font-size:0.6rem;color:#666;">📍 {asset.get('location_building','')} | 📅 Daily</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.info("👆 Go to 'Execute PPM' tab, select this asset, and choose 'Daily Checklist' as PPM Type.")
    
    # ============================================
    # TAB 2: HOURLY CHECKLIST
    # ============================================
    with tabs[2]:
        st.markdown("### ⏰ Hourly Checklist Execution")
        
        hourly_assets = df[df["verification_frequency"].isin(["Hourly","hourly","Bi-Weekly"])] if "verification_frequency" in df.columns else pd.DataFrame()
        
        if len(hourly_assets) == 0:
            st.info("No hourly checklist assets found.")
        else:
            c1, c2 = st.columns(2)
            with c1: st.metric("⏰ Hourly Assets", len(hourly_assets))
            with c2: st.metric("⏳ Pending", len(hourly_assets))
            
            st.markdown("---")
            
            for _, asset in hourly_assets.head(20).iterrows():
                st.markdown(f"""
                <div style="background:white;border-left:3px solid #8B5CF6;border-radius:6px;padding:0.5rem;margin:0.2rem 0;display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <b>{asset.get('parent_asset','N/A')}</b> — {asset.get('name','N/A')[:50]}
                        <br><span style="font-size:0.6rem;color:#666;">📍 {asset.get('location_building','')} | ⏰ {asset.get('verification_frequency','')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ============================================
    # TAB 3: MY SUBMISSIONS
    # ============================================
    with tabs[3]:
        st.markdown("### 📊 My Submitted PPMs")
        
        my_executions = supabase.table("ppm_executions").select("*").eq("facility_code", fc).eq("executed_by_name", user_name).order("created_at", desc=True).limit(50).execute()
        
        if my_executions.data and len(my_executions.data) > 0:
            for ex in my_executions.data:
                status = ex.get("status", "submitted")
                sc = {"submitted": "#3B82F6", "confirmed": "#F59E0B", "approved": "#10B981", "rejected": "#EF4444"}.get(status, "#3B82F6")
                icon = {"submitted": "📤", "confirmed": "✅", "approved": "🟢", "rejected": "❌"}.get(status, "📋")
                ppm_type = ex.get("ppm_type", "Scheduled PPM")
                
                st.markdown(f"""
                <div style="background:white;border-left:5px solid {sc};border-radius:10px;padding:1rem;margin:0.5rem 0;box-shadow:0 2px 8px rgba(0,0,0,0.04);cursor:pointer;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div style="font-size:1rem;font-weight:700;color:#1a1a1a;">{icon} {ex.get('execution_date','')} — {ppm_type}</div>
                            <div style="font-size:0.75rem;color:#666;margin-top:0.2rem;">🏢 {ex.get('building','N/A')} | ⏰ {ex.get('execution_time','')}</div>
                        </div>
                        <span style="background:{sc};color:white;padding:5px 16px;border-radius:20px;font-size:0.7rem;font-weight:700;">{status.upper()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No PPM submissions yet.")
    
    # ============================================
    # TAB 4: PENDING APPROVAL — TWO LEVELS
    # ============================================
    with tabs[4]:
        st.markdown("### ⏳ Approval Center")
        
        if user_role not in ["admin", "approver", "authorizer", "confirmer"]:
            st.info("This section is for Team Leads and Managers.")
        else:
            approval_tabs = st.tabs(["🔐 Team Lead Confirmation", "🟢 Manager Approval"])
            
            # ============================================
            # TEAM LEAD CONFIRMATION
            # ============================================
            with approval_tabs[0]:
                st.markdown("#### 🔐 Pending Team Lead Confirmation")
                
                pending = supabase.table("ppm_executions").select("*").eq("facility_code", fc).eq("status", "submitted").order("created_at", desc=True).execute()
                
                if pending.data and len(pending.data) > 0:
                    for ex in pending.data:
                        sc = "#3B82F6"
                        ppm_type = ex.get("ppm_type", "Scheduled PPM")
                        
                        st.markdown(f"""
                        <div style="background:white;border-left:5px solid {sc};border-radius:10px;padding:1rem;margin:0.5rem 0;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div>
                                    <div style="font-size:1rem;font-weight:700;">📋 {ex.get('execution_date','')} — {ppm_type}</div>
                                    <div style="font-size:0.75rem;color:#666;">👤 {ex.get('executed_by_name','')} | 🏢 {ex.get('building','N/A')}</div>
                                </div>
                                <span style="background:{sc};color:white;padding:5px 16px;border-radius:20px;font-size:0.7rem;font-weight:700;">SUBMITTED</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if ex.get("general_comments"):
                            st.caption(f"📝 {ex.get('general_comments','')}")
                        if ex.get("is_early_execution"):
                            st.warning(f"⚠️ Early Execution — {ex.get('early_execution_reason','')}")
                        if ex.get("mitigation_plan"):
                            st.error(f"🚨 Mitigation: {ex.get('mitigation_plan','')}")
                        
                        items = supabase.table("ppm_execution_items").select("*").eq("execution_id", ex["id"]).order("item_number").execute()
                        if items.data:
                            with st.expander("📋 View Checklist Results"):
                                for item in items.data:
                                    res = item.get("result","")
                                    if res in ["Pass","Yes","Clear","Good","Normal","Tight","Ok"]:
                                        icon = "✅"
                                    elif res in ["Fail","No","Damage","Dirty","Abnormal","Loose","Not Ok"]:
                                        icon = "❌"
                                    else:
                                        icon = "📝"
                                    st.markdown(f"{icon} **{item.get('item_number')}.** {item.get('description')} — *{item.get('actual_value', res)}*")
                        
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        with c1:
                            confirm_comment = st.text_area("Confirmation Comment*", key=f"tl_confirm_{ex['id']}", height=60)
                            if st.button("✅ CONFIRM & SEND TO MANAGER", key=f"tl_btn_confirm_{ex['id']}", use_container_width=True, type="primary"):
                                if confirm_comment:
                                    supabase.table("ppm_executions").update({"status":"confirmed"}).eq("id", ex["id"]).execute()
                                    supabase.table("ppm_approvals").update({"status":"approved","comments":confirm_comment,"approver_name":user_name,"action_date":datetime.now().isoformat()}).eq("execution_id", ex["id"]).eq("approval_level","team_lead").execute()
                                    st.success("✅ Confirmed! Sent to Manager for final approval."); st.rerun()
                                else: st.error("⚠️ Comment required")
                        with c2:
                            reject_comment = st.text_area("Rejection Reason*", key=f"tl_reject_{ex['id']}", height=60)
                            if st.button("❌ REJECT", key=f"tl_btn_reject_{ex['id']}", use_container_width=True):
                                if reject_comment:
                                    supabase.table("ppm_executions").update({"status":"rejected"}).eq("id", ex["id"]).execute()
                                    supabase.table("ppm_approvals").update({"status":"rejected","comments":reject_comment,"approver_name":user_name,"action_date":datetime.now().isoformat()}).eq("execution_id", ex["id"]).eq("approval_level","team_lead").execute()
                                    st.error("❌ Rejected"); st.rerun()
                                else: st.error("⚠️ Reason required")
                else:
                    st.success("✅ No submissions waiting for Team Lead confirmation.")
            
            # ============================================
            # MANAGER APPROVAL
            # ============================================
            with approval_tabs[1]:
                st.markdown("#### 🟢 Pending Manager Approval")
                
                if user_role not in ["admin", "approver"]:
                    st.info("This section is for Managers/HOD only.")
                else:
                    pending_mgr = supabase.table("ppm_executions").select("*").eq("facility_code", fc).eq("status", "confirmed").order("created_at", desc=True).execute()
                    
                    if pending_mgr.data and len(pending_mgr.data) > 0:
                        for ex in pending_mgr.data:
                            sc = "#F59E0B"
                            ppm_type = ex.get("ppm_type", "Scheduled PPM")
                            
                            st.markdown(f"""
                            <div style="background:white;border-left:5px solid {sc};border-radius:10px;padding:1rem;margin:0.5rem 0;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <div style="font-size:1rem;font-weight:700;">📋 {ex.get('execution_date','')} — {ppm_type}</div>
                                        <div style="font-size:0.75rem;color:#666;">👤 {ex.get('executed_by_name','')} | 🏢 {ex.get('building','N/A')}</div>
                                    </div>
                                    <span style="background:{sc};color:white;padding:5px 16px;border-radius:20px;font-size:0.7rem;font-weight:700;">AWAITING MANAGER</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show Team Lead confirmation
                            tl_approval = supabase.table("ppm_approvals").select("*").eq("execution_id", ex["id"]).eq("approval_level","team_lead").single().execute()
                            if tl_approval.data:
                                st.caption(f"✅ Team Lead: {tl_approval.data.get('approver_name','N/A')} — {tl_approval.data.get('comments','')}")
                            
                            if ex.get("mitigation_plan"):
                                st.error(f"🚨 Mitigation: {ex.get('mitigation_plan','')}")
                            
                            items = supabase.table("ppm_execution_items").select("*").eq("execution_id", ex["id"]).order("item_number").execute()
                            if items.data:
                                with st.expander("📋 View Checklist Results"):
                                    for item in items.data:
                                        res = item.get("result","")
                                        if res in ["Pass","Yes","Clear","Good","Normal","Tight","Ok"]:
                                            icon = "✅"
                                        elif res in ["Fail","No","Damage","Dirty","Abnormal","Loose","Not Ok"]:
                                            icon = "❌"
                                        else:
                                            icon = "📝"
                                        st.markdown(f"{icon} **{item.get('item_number')}.** {item.get('description')} — *{item.get('actual_value', res)}*")
                            
                            st.markdown("---")
                            c1, c2 = st.columns(2)
                            with c1:
                                mgr_comment = st.text_area("Approval Comment*", key=f"mgr_approve_{ex['id']}", height=60)
                                if st.button("🟢 FINAL APPROVE", key=f"mgr_btn_approve_{ex['id']}", use_container_width=True, type="primary"):
                                    if mgr_comment:
                                        supabase.table("ppm_executions").update({"status":"approved"}).eq("id", ex["id"]).execute()
                                        supabase.table("ppm_approvals").update({"status":"approved","comments":mgr_comment,"approver_name":user_name,"action_date":datetime.now().isoformat()}).eq("execution_id", ex["id"]).eq("approval_level","manager").execute()
                                        st.success("🟢 Fully Approved!"); st.balloons(); st.rerun()
                                    else: st.error("⚠️ Comment required")
                            with c2:
                                mgr_reject = st.text_area("Rejection Reason*", key=f"mgr_reject_{ex['id']}", height=60)
                                if st.button("❌ REJECT", key=f"mgr_btn_reject_{ex['id']}", use_container_width=True):
                                    if mgr_reject:
                                        supabase.table("ppm_executions").update({"status":"rejected"}).eq("id", ex["id"]).execute()
                                        supabase.table("ppm_approvals").update({"status":"rejected","comments":mgr_reject,"approver_name":user_name,"action_date":datetime.now().isoformat()}).eq("execution_id", ex["id"]).eq("approval_level","manager").execute()
                                        st.error("❌ Rejected"); st.rerun()
                                    else: st.error("⚠️ Reason required")
                    else:
                        st.success("✅ No submissions waiting for Manager approval.")
    
    # ============================================
    # TAB 5: CHECKLIST BUILDER (ADMIN) — INTERACTIVE
    # ============================================
    with tabs[5]:
        st.markdown("### ⚙️ Interactive Checklist Builder")
        
        if not is_admin:
            st.error("⛔ Admin access only")
        else:
            builder_tabs = st.tabs(["📋 Create Template", "✏️ Edit Template", "📅 Schedule Settings"])
            
            # ============================================
            # SUB-TAB: CREATE TEMPLATE
            # ============================================
            with builder_tabs[0]:
                st.markdown("#### ➕ Create New Checklist Template")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    template_name = st.text_input("Report Name*", placeholder="e.g. Automated Motor Monthly Checklist", key="tpl_name")
                with c2:
                    period = st.selectbox("Period*", ["Daily", "Weekly", "Bi-Weekly", "Monthly", "Quarterly", "Half-Yearly", "Yearly"], key="tpl_period")
                with c3:
                    image_required = st.selectbox("Image Option*", ["Yes", "No"], key="tpl_image")
                
                c1, c2 = st.columns(2)
                with c1:
                    perform_time = st.number_input("Perform Time (in Minutes)*", min_value=0, value=30, key="tpl_time")
                    buffer_days = st.number_input("Buffer Days*", min_value=0, value=0, key="tpl_buffer")
                with c2:
                    asset_category = st.selectbox("Asset Category", sorted(df["dept_full"].dropna().unique().tolist()), key="tpl_cat")
                    standard_ref = st.text_input("Standard Reference", placeholder="e.g. ISO 8100, NFPA 25, Custom", key="tpl_std")
                
                st.markdown("---")
                st.markdown("### 📅 Schedule Dates")
                
                date_mode = st.radio("Date Selection Mode", ["📅 Manual Multi-Date Picker", "🔄 Auto-Generate by Period"], horizontal=True, key="date_mode")
                
                if date_mode == "📅 Manual Multi-Date Picker":
                    st.caption("Click dates on the calendar to add/remove them.")
                    
                    # Store selected dates in session state
                    if "manual_selected_dates" not in st.session_state:
                        st.session_state.manual_selected_dates = []
                    
                    # Date picker to add a single date
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        pick_date = st.date_input("Pick a date to add", date.today(), key="tpl_pick_date")
                    with c2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("➕ Add Date", key="btn_add_date", use_container_width=True):
                            date_str = pick_date.strftime("%d-%m-%Y")
                            if date_str not in st.session_state.manual_selected_dates:
                                st.session_state.manual_selected_dates.append(date_str)
                                st.session_state.manual_selected_dates.sort()
                                st.rerun()
                    with c3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️ Clear All", key="btn_clear_dates", use_container_width=True):
                            st.session_state.manual_selected_dates = []
                            st.rerun()
                    
                    # Show selected dates
                    if st.session_state.manual_selected_dates:
                        st.markdown("**Selected Dates:**")
                        
                        # Display as a simple list with remove buttons
                        cols_per_row = 4
                        for i in range(0, len(st.session_state.manual_selected_dates), cols_per_row):
                            row_dates = st.session_state.manual_selected_dates[i:i+cols_per_row]
                            dcols = st.columns(cols_per_row)
                            for j, d in enumerate(row_dates):
                                with dcols[j]:
                                    st.markdown(f"""
                                    <div style="background:#EFF6FF;border:2px solid #3B82F6;border-radius:8px;padding:0.4rem;text-align:center;font-size:0.7rem;font-weight:600;color:#2563EB;">
                                        📅 {d}
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Remove date
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            remove_date = st.selectbox("Remove a date", ["Select..."] + st.session_state.manual_selected_dates, key="tpl_remove_date")
                        with c2:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if remove_date != "Select...":
                                if st.button(f"🗑️ Remove", key="btn_remove_date", use_container_width=True):
                                    st.session_state.manual_selected_dates.remove(remove_date)
                                    st.rerun()
                        
                        dates_string = ",".join(st.session_state.manual_selected_dates)
                        st.caption(f"📅 {len(st.session_state.manual_selected_dates)} dates selected")
                
                else:
                    if "generated_dates" not in st.session_state:
                        st.session_state.generated_dates = []
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        start_date = st.date_input("Start Date", date.today(), key="tpl_start_date")
                        end_date = st.date_input("End Schedule Date", date.today() + timedelta(days=365), key="tpl_end_date")
                    
                    with c2:
                        if st.button("🔄 Generate Dates", key="btn_gen_dates", use_container_width=True):
                            selected_period = period
                            dates_list = []
                            current = start_date
                            while current <= end_date:
                                dates_list.append(current.strftime("%d-%m-%Y"))
                                if selected_period == "Daily":
                                    current = current + timedelta(days=1)
                                elif selected_period == "Weekly":
                                    current = current + timedelta(days=7)
                                elif selected_period == "Bi-Weekly":
                                    current = current + timedelta(days=14)
                                elif selected_period == "Monthly":
                                    if current.month == 12:
                                        current = date(current.year + 1, 1, min(current.day, 28))
                                    else:
                                        current = date(current.year, current.month + 1, min(current.day, 28))
                                elif selected_period == "Quarterly":
                                    nm = current.month + 3
                                    if nm > 12:
                                        current = date(current.year + 1, nm - 12, min(current.day, 28))
                                    else:
                                        current = date(current.year, nm, min(current.day, 28))
                                elif selected_period == "Half-Yearly":
                                    nm = current.month + 6
                                    if nm > 12:
                                        current = date(current.year + 1, nm - 12, min(current.day, 28))
                                    else:
                                        current = date(current.year, nm, min(current.day, 28))
                                elif selected_period == "Yearly":
                                    current = date(current.year + 1, current.month, min(current.day, 28))
                            st.session_state.generated_dates = dates_list
                            st.rerun()
                    
                    if st.session_state.generated_dates:
                        selected_dates = st.multiselect("Select Dates*", st.session_state.generated_dates, default=st.session_state.generated_dates[:3] if len(st.session_state.generated_dates) >= 3 else st.session_state.generated_dates, key="tpl_auto_selected")
                        dates_string = ",".join(selected_dates)
                        st.caption(f"📅 {len(selected_dates)} dates selected")
                    else:
                        dates_string = ""
                        st.caption("Click 'Generate Dates' to auto-generate schedule dates.")
                
                st.markdown("---")
                st.markdown("### 📝 Checklist Items")
                st.caption("Add items one by one. Set the answer type and threshold options for each.")
                
                # Initialize session state for builder items
                if "checklist_builder_items" not in st.session_state:
                    st.session_state.checklist_builder_items = [
                        {"sno": 1, "description": "", "answer_type": "yes_no", "threshold": "Yes/No"}
                    ]
                
                # Display current items as a table
                item_data = []
                for item in st.session_state.checklist_builder_items:
                    if item["description"].strip():
                        item_data.append({
                            "SNO": item["sno"],
                            "Description": item["description"],
                            "Answer Type": item["answer_type"],
                            "Threshold / Options": item["threshold"]
                        })
                
                if len(item_data) > 0:
                    items_df = pd.DataFrame(item_data)
                    st.dataframe(items_df, use_container_width=True, hide_index=True, height=200)
                
                # ============================================
                # ADD ITEM SECTION (OUTSIDE FORM)
                # ============================================
                st.markdown("**➕ Add Checklist Item**")
                c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
                with c1:
                    new_sno = st.number_input("SNO", min_value=1, value=len(st.session_state.checklist_builder_items)+1, key="new_sno")
                with c2:
                    new_desc = st.text_input("Description", key="new_desc", placeholder="e.g. Check damages on Rollers/Conveyor Belt")
                with c3:
                    answer_type = st.selectbox("Answer Type", ["yes_no", "pass_fail", "status", "reading", "text", "section"], key="new_type")
                with c4:
                    if answer_type == "yes_no":
                        threshold = st.text_input("Options", value="Yes/No", key="new_thresh", help="Use / separator")
                    elif answer_type == "pass_fail":
                        threshold = st.text_input("Options", value="Pass/Fail/NA", key="new_thresh")
                    elif answer_type == "status":
                        threshold = st.text_input("Options", value="Normal/Abnormal", key="new_thresh", help="e.g., High/Low, Clean/Dirty, Tight/Loose, Good/Damage")
                    elif answer_type == "reading":
                        threshold = st.text_input("Unit", value="°C", key="new_thresh", placeholder="e.g., °C, V, A, Bar")
                    else:
                        threshold = st.text_input("Options", value="", key="new_thresh")
                
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    if st.button("➕ Add Item", key="btn_add_item", use_container_width=True):
                        if new_desc:
                            st.session_state.checklist_builder_items.append({
                                "sno": new_sno,
                                "description": new_desc,
                                "answer_type": answer_type,
                                "threshold": threshold
                            })
                            st.rerun()
                with c2:
                    if st.button("🗑️ Clear All", key="btn_clear_all", use_container_width=True):
                        st.session_state.checklist_builder_items = [{"sno": 1, "description": "", "answer_type": "yes_no", "threshold": "Yes/No"}]
                        st.rerun()
                with c3:
                    if st.button("🗑️ Remove Last", key="btn_remove_last", use_container_width=True) and len(st.session_state.checklist_builder_items) > 1:
                        st.session_state.checklist_builder_items.pop()
                        st.rerun()
                
                # ============================================
                # IMPORT OPTIONS
                # ============================================
                st.markdown("---")
                st.markdown("### 📥 Import Checklist Items")
                
                import_mode = st.radio("Import Method", ["📋 Quick Paste", "📁 Upload File"], horizontal=True, key="import_mode")
                
                if import_mode == "📋 Quick Paste":
                    st.caption("Paste from Excel. Detects Tab or multiple spaces as column separator.")
                    
                    quick_paste = st.text_area("Paste items here", height=200, key="quick_paste_builder",
                        placeholder="1\tCheck damages on Rollers/Conveyor Belt\tYes/No\n2\tCheck Sensors/Photocells Sensitivity Status\tHigh/Low\n3\tCheck Moving Parts Lubrications\tYes/No\n4\tCheck Backup Batteries Status\tOk/Not Ok\n5\tCheck Mis-alignment/Knocks/Loose Bracket\tYes/No")
                    
                    if quick_paste:
                        import re
                        lines = [l.strip() for l in quick_paste.strip().split("\n") if l.strip()]
                        
                        # Smart separator detection
                        tab_count = sum(1 for l in lines if "\t" in l)
                        separator = "tab" if tab_count > len(lines) * 0.5 else "spaces"
                        
                        st.caption(f"📋 {len(lines)} items | Separator: {separator}")
                        
                        # Preview
                        preview_rows = []
                        for i, line in enumerate(lines[:10]):
                            if separator == "tab":
                                parts = [p.strip() for p in line.split("\t") if p.strip()]
                            else:
                                parts = re.split(r'\s{2,}', line)
                                parts = [p.strip() for p in parts if p.strip()]
                            
                            if len(parts) >= 2:
                                sno, desc = parts[0], parts[1]
                                status = parts[2] if len(parts) > 2 else "Yes/No"
                            elif len(parts) == 1:
                                sno, desc = str(i+1), parts[0]
                                status = "Yes/No"
                            else:
                                continue
                            preview_rows.append({"SNO": sno, "Description": desc[:100], "Status": status})
                        
                        if preview_rows:
                            st.caption("👁️ Preview:")
                            st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            default_type_paste = st.selectbox("Default Answer Type", ["yes_no", "status", "pass_fail", "reading", "text"], key="paste_type")
                        with c2:
                            default_thresh_paste = st.text_input("Default Options", value="Yes/No", key="paste_thresh")
                        
                        if st.button(f"📋 Import {len(lines)} Items", key="btn_parse", use_container_width=True, type="primary"):
                            imported = 0
                            for i, line in enumerate(lines):
                                if separator == "tab":
                                    parts = [p.strip() for p in line.split("\t") if p.strip()]
                                else:
                                    parts = re.split(r'\s{2,}', line)
                                    parts = [p.strip() for p in parts if p.strip()]
                                
                                if len(parts) >= 2:
                                    desc = parts[1]
                                    status = parts[2] if len(parts) > 2 else default_thresh_paste
                                elif len(parts) == 1:
                                    desc = parts[0]
                                    status = default_thresh_paste
                                else:
                                    continue
                                
                                if desc:
                                    st.session_state.checklist_builder_items.append({
                                        "sno": len(st.session_state.checklist_builder_items) + 1,
                                        "description": desc,
                                        "answer_type": default_type_paste,
                                        "threshold": status if status else default_thresh_paste
                                    })
                                    imported += 1
                            st.success(f"✅ {imported} items imported!")
                            st.rerun()
                
                else:
                    st.caption("📁 Upload CSV or Excel file with columns: SNO, Description, Status")
                    uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"], key="checklist_upload")
                    
                    if uploaded_file:
                        try:
                            if uploaded_file.name.endswith(".csv"):
                                import_df = pd.read_csv(uploaded_file, encoding='latin-1')
                            else:
                                import_df = pd.read_excel(uploaded_file)
                            
                            st.dataframe(import_df.head(10), use_container_width=True)
                            st.caption(f"📋 {len(import_df)} rows found")
                            
                            cols = import_df.columns.tolist()
                            c1, c2 = st.columns(2)
                            with c1:
                                desc_col = st.selectbox("Description Column", cols, key="map_desc")
                            with c2:
                                status_col = st.selectbox("Status Column (optional)", ["--None--"] + cols, key="map_status")
                            
                            default_type_upload = st.selectbox("Default Answer Type", ["yes_no", "status", "pass_fail", "reading", "text"], key="upload_type")
                            
                            if st.button(f"📋 Import {len(import_df)} Items", key="btn_upload_import", use_container_width=True, type="primary"):
                                count = 0
                                for _, row in import_df.iterrows():
                                    desc = str(row[desc_col])
                                    status = str(row[status_col]) if status_col != "--None--" else "Yes/No"
                                    if desc and desc != "nan":
                                        st.session_state.checklist_builder_items.append({
                                            "sno": len(st.session_state.checklist_builder_items) + 1,
                                            "description": desc,
                                            "answer_type": default_type_upload,
                                            "threshold": status if status != "nan" else "Yes/No"
                                        })
                                        count += 1
                                st.success(f"✅ {count} items imported!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # ============================================
                # SUBMIT FORM (SEPARATE)
                # ============================================
                st.markdown("---")
                
                with st.form("create_template_submit"):
                    st.markdown("### 💾 Save Template")
                    
                    if st.form_submit_button("💾 CREATE CHECKLIST TEMPLATE", use_container_width=True, type="primary"):
                        if template_name and len(st.session_state.checklist_builder_items) > 0:
                            valid_items = [i for i in st.session_state.checklist_builder_items if i["description"].strip()]
                            
                            if len(valid_items) == 0:
                                st.error("⚠️ Add at least one checklist item with a description")
                            else:
                                template_result = supabase.table("ppm_checklist_templates").insert({
                                    "template_name": template_name,
                                    "asset_category": asset_category,
                                    "international_standard": standard_ref,
                                    "description": f"Period: {period} | Time: {perform_time}min | Buffer: {buffer_days}days | Image: {image_required}",
                                    "schedule_dates": dates_string if dates_string else None,
                                    "is_active": True
                                }).execute()
                                
                                if template_result.data:
                                    template_id = template_result.data[0]["id"]
                                    
                                    for item in valid_items:
                                        supabase.table("ppm_checklist_items").insert({
                                            "template_id": template_id,
                                            "item_number": item["sno"],
                                            "description": item["description"],
                                            "check_type": item["answer_type"],
                                            "expected_value": item["threshold"],
                                            "sort_order": item["sno"]
                                        }).execute()
                                    
                                    st.session_state.checklist_builder_items = [{"sno": 1, "description": "", "answer_type": "yes_no", "threshold": "Yes/No"}]
                                    st.success(f"✅ Template '{template_name}' created with {len(valid_items)} items!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to create template")
                        else:
                            st.error("⚠️ Template name and at least one item are required")
            
            # ============================================
            # SUB-TAB: EDIT TEMPLATE
            # ============================================
            with builder_tabs[1]:
                st.markdown("#### ✏️ Edit Existing Template")
                
                all_templates = supabase.table("ppm_checklist_templates").select("*").order("created_at", desc=True).execute()
                
                if all_templates.data and len(all_templates.data) > 0:
                    template_names_list = [t.get("template_name","") for t in all_templates.data]
                    edit_template_name = st.selectbox("Select Template to Edit", template_names_list, key="edit_template")
                    
                    if edit_template_name:
                        edit_template = next((t for t in all_templates.data if t.get("template_name") == edit_template_name), None)
                        
                        if edit_template:
                            st.markdown(f"**Template:** {edit_template.get('template_name')} | **Standard:** {edit_template.get('international_standard','Custom')}")
                            
                            # Editable fields
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                new_name = st.text_input("Report Name", value=edit_template.get("template_name",""), key="edit_tpl_name")
                            with c2:
                                desc_parts = edit_template.get("description","").split("|")
                                period_val = desc_parts[0].replace("Period:","").strip() if len(desc_parts) > 0 else "Monthly"
                                new_period = st.selectbox("Period", ["Daily","Weekly","Bi-Weekly","Monthly","Quarterly","Half-Yearly","Yearly"], 
                                    index=["Daily","Weekly","Bi-Weekly","Monthly","Quarterly","Half-Yearly","Yearly"].index(period_val) if period_val in ["Daily","Weekly","Bi-Weekly","Monthly","Quarterly","Half-Yearly","Yearly"] else 3, key="edit_period")
                            with c3:
                                new_image = st.selectbox("Image Option", ["Yes","No"], key="edit_image")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                time_val = desc_parts[1].replace("Time:","").replace("min","").strip() if len(desc_parts) > 1 else "30"
                                new_time = st.number_input("Perform Time (min)", value=int(time_val) if time_val.isdigit() else 30, key="edit_time")
                            with c2:
                                buf_val = desc_parts[2].replace("Buffer:","").replace("days","").strip() if len(desc_parts) > 2 else "0"
                                new_buffer = st.number_input("Buffer Days", value=int(buf_val) if buf_val.isdigit() else 0, key="edit_buffer")
                            
                            new_standard = st.text_input("Standard Reference", value=edit_template.get("international_standard",""), key="edit_std")
                            
                            st.markdown("---")
                            
                            # Edit dates
                            st.markdown("### 📅 Schedule Dates")
                            existing_dates = edit_template.get("schedule_dates","")
                            existing_dates_list = existing_dates.split(",") if existing_dates else []
                            
                            date_edit_mode = st.radio("Date Mode", ["📅 Manual Entry", "🔄 Auto-Generate"], horizontal=True, key="edit_date_mode")
                            
                            if date_edit_mode == "📅 Manual Entry":
                                edit_manual = st.text_area("Enter dates (comma-separated, DD-MM-YYYY)", 
                                    value=existing_dates, height=80, key="edit_manual_dates",
                                    placeholder="29-06-2026,29-07-2026,29-08-2026")
                                new_dates_string = edit_manual
                            else:
                                if "edit_generated_dates" not in st.session_state:
                                    st.session_state.edit_generated_dates = existing_dates_list
                                
                                c1, c2 = st.columns(2)
                                with c1:
                                    edit_start = st.date_input("Start Date", date.today(), key="edit_start")
                                with c2:
                                    edit_end = st.date_input("End Date", date.today() + timedelta(days=365), key="edit_end")
                                
                                if st.button("🔄 Generate Dates", key="edit_gen_dates", use_container_width=True):
                                    dates_list = []
                                    current = edit_start
                                    while current <= edit_end:
                                        dates_list.append(current.strftime("%d-%m-%Y"))
                                        if new_period == "Monthly":
                                            current = date(current.year, current.month+1, min(current.day,28)) if current.month < 12 else date(current.year+1,1,min(current.day,28))
                                        elif new_period == "Quarterly":
                                            nm = current.month+3
                                            current = date(current.year+1,nm-12,min(current.day,28)) if nm > 12 else date(current.year,nm,min(current.day,28))
                                        elif new_period == "Weekly":
                                            current += timedelta(days=7)
                                        elif new_period == "Bi-Weekly":
                                            current += timedelta(days=14)
                                        elif new_period == "Half-Yearly":
                                            nm = current.month+6
                                            current = date(current.year+1,nm-12,min(current.day,28)) if nm > 12 else date(current.year,nm,min(current.day,28))
                                        elif new_period == "Yearly":
                                            current = date(current.year+1,current.month,min(current.day,28))
                                        else:
                                            current += timedelta(days=1)
                                    st.session_state.edit_generated_dates = dates_list
                                    st.rerun()
                                
                                if st.session_state.edit_generated_dates:
                                    selected = st.multiselect("Select Dates", st.session_state.edit_generated_dates, default=st.session_state.edit_generated_dates, key="edit_multi_dates")
                                    new_dates_string = ",".join(selected)
                                    st.caption(f"📅 {len(selected)} dates selected")
                                else:
                                    new_dates_string = existing_dates
                            
                            st.markdown("---")
                            
                            # Edit checklist items
                            st.markdown("### 📝 Checklist Items")
                            
                            existing_items = supabase.table("ppm_checklist_items").select("*").eq("template_id", edit_template["id"]).order("sort_order").execute()
                            
                            if existing_items.data:
                                st.markdown("**Current Items (click to edit):**")
                                for item in existing_items.data:
                                    c1, c2, c3, c4 = st.columns([1, 4, 2, 2])
                                    with c1:
                                        new_sno = st.text_input("SNO", value=str(item.get("item_number","")), key=f"edit_sno_{item['id']}", label_visibility="collapsed")
                                    with c2:
                                        new_desc = st.text_input("Desc", value=item.get("description",""), key=f"edit_desc_{item['id']}", label_visibility="collapsed")
                                    with c3:
                                        new_type = st.selectbox("Type", ["yes_no","pass_fail","status","reading","text","section"], 
                                            index=["yes_no","pass_fail","status","reading","text","section"].index(item.get("check_type","yes_no")) if item.get("check_type","yes_no") in ["yes_no","pass_fail","status","reading","text","section"] else 0,
                                            key=f"edit_type_{item['id']}", label_visibility="collapsed")
                                    with c4:
                                        new_thresh = st.text_input("Options", value=item.get("expected_value","") or "", key=f"edit_thresh_{item['id']}", label_visibility="collapsed")
                                
                                st.markdown("---")
                            
                            # Add new item to existing template
                            st.markdown("**➕ Add New Item:**")
                            c1, c2, c3, c4 = st.columns([1, 4, 2, 2])
                            with c1:
                                add_sno = st.number_input("SNO", min_value=1, value=len(existing_items.data)+1 if existing_items.data else 1, key="edit_add_sno")
                            with c2:
                                add_desc = st.text_input("Description", key="edit_add_desc", placeholder="New checklist item...")
                            with c3:
                                add_type = st.selectbox("Type", ["yes_no","pass_fail","status","reading","text"], key="edit_add_type")
                            with c4:
                                add_thresh = st.text_input("Options", value="Yes/No", key="edit_add_thresh")
                            
                            if st.button("➕ Add Item to Template", key="edit_btn_add", use_container_width=True):
                                if add_desc.strip():
                                    supabase.table("ppm_checklist_items").insert({
                                        "template_id": edit_template["id"],
                                        "item_number": int(add_sno),
                                        "description": add_desc.strip(),
                                        "check_type": add_type,
                                        "expected_value": add_thresh,
                                        "sort_order": int(add_sno)
                                    }).execute()
                                    st.success("✅ Item added!")
                                    st.rerun()
                            
                            st.markdown("---")
                            
                            # Save all changes
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("💾 SAVE ALL CHANGES", use_container_width=True, type="primary"):
                                    # Update template
                                    supabase.table("ppm_checklist_templates").update({
                                        "template_name": new_name,
                                        "international_standard": new_standard,
                                        "description": f"Period: {new_period} | Time: {new_time}min | Buffer: {new_buffer}days | Image: {new_image}",
                                        "schedule_dates": new_dates_string if new_dates_string else None
                                    }).eq("id", edit_template["id"]).execute()
                                    
                                    # Update existing items
                                    for item in existing_items.data:
                                        supabase.table("ppm_checklist_items").update({
                                            "item_number": int(st.session_state.get(f"edit_sno_{item['id']}", item.get("item_number",1)) or 1),
                                            "description": st.session_state.get(f"edit_desc_{item['id']}", item.get("description","")),
                                            "check_type": st.session_state.get(f"edit_type_{item['id']}", item.get("check_type","yes_no")),
                                            "expected_value": st.session_state.get(f"edit_thresh_{item['id']}", item.get("expected_value","") or "")
                                        }).eq("id", item["id"]).execute()
                                    
                                    st.success("✅ Template updated!")
                                    st.balloons()
                                    st.rerun()
                            with c2:
                                if st.button("🗑️ DELETE TEMPLATE", use_container_width=True):
                                    supabase.table("ppm_checklist_items").delete().eq("template_id", edit_template["id"]).execute()
                                    supabase.table("ppm_checklist_templates").delete().eq("id", edit_template["id"]).execute()
                                    st.warning("✅ Template deleted!")
                                    st.rerun()
                else:
                    st.info("No templates created yet.")
            
            # ============================================
            # SUB-TAB: SCHEDULE SETTINGS
            # ============================================
            with builder_tabs[2]:
                st.markdown("#### 📅 Schedule Settings")
                st.info("Schedule dates are managed when enrolling assets in the Checklist Status page. Use the Bulk Enrollment feature to set frequency and dates.")
                
                if st.button("📋 GO TO CHECKLIST STATUS", use_container_width=True, type="primary"):
                    st.session_state.page = "cs"
                    st.rerun()

    # ============================================
    # TAB 6: MANAGE ENROLLED PPM SCHEDULES (ADMIN ONLY)
    # ============================================
    with tabs[6]:
        st.markdown("### 📋 Manage Enrolled PPM Schedules")
        
        if not is_admin:
            st.error("⛔ Admin access only")
        else:
            all_schedules = supabase.table("ppm_schedules").select("*").eq("facility_code", fc).order("next_due_date", desc=False).execute()
            
            if all_schedules.data and len(all_schedules.data) > 0:
                sched_df = pd.DataFrame(all_schedules.data)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    filter_status = st.selectbox("Status", ["All", "scheduled", "completed", "overdue"], key="mgmt_status")
                with c2:
                    filter_freq = st.selectbox("Frequency", ["All", "Daily", "Weekly", "Bi-Weekly", "Monthly", "Quarterly", "Half-Yearly", "Yearly"], key="mgmt_freq")
                with c3:
                    search_sched = st.text_input("🔍 Search by title", key="mgmt_search", placeholder="Asset name...")
                
                display_sched = sched_df.copy()
                if filter_status != "All":
                    display_sched = display_sched[display_sched["status"] == filter_status]
                if filter_freq != "All":
                    display_sched = display_sched[display_sched["frequency"] == filter_freq]
                if search_sched:
                    display_sched = display_sched[display_sched["title"].str.contains(search_sched, case=False, na=False)]
                
                st.caption(f"📋 Showing {len(display_sched)} of {len(sched_df)} schedules")
                
                page_size = 15
                if "mgmt_page" not in st.session_state:
                    st.session_state.mgmt_page = 1
                
                total_pages = max(1, (len(display_sched) + page_size - 1) // page_size)
                start = (st.session_state.mgmt_page - 1) * page_size
                end = min(start + page_size, len(display_sched))
                
                c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 1, 1])
                with c1:
                    if st.button("◀◀", key="mgmt_first"): st.session_state.mgmt_page = 1; st.rerun()
                with c2:
                    if st.button("◀", key="mgmt_prev") and st.session_state.mgmt_page > 1:
                        st.session_state.mgmt_page -= 1; st.rerun()
                with c3:
                    st.markdown(f"**Page {st.session_state.mgmt_page} of {total_pages}**")
                with c4:
                    if st.button("▶", key="mgmt_next") and st.session_state.mgmt_page < total_pages:
                        st.session_state.mgmt_page += 1; st.rerun()
                with c5:
                    if st.button("▶▶", key="mgmt_last"): st.session_state.mgmt_page = total_pages; st.rerun()
                
                page_data = display_sched.iloc[start:end]
                
                for _, sched in page_data.iterrows():
                    status = sched.get("status", "scheduled")
                    sc = {"scheduled": "#3B82F6", "completed": "#10B981", "overdue": "#EF4444"}.get(status, "#3B82F6")
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="background:white;border-left:5px solid {sc};border-radius:8px;padding:0.8rem;margin:0.3rem 0;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div>
                                    <b>{sched.get('title','N/A')[:80]}</b>
                                    <br><span style="font-size:0.7rem;color:#666;">📅 Due: {sched.get('next_due_date','')} | 🔄 {sched.get('frequency','')} | 👤 {sched.get('assigned_team','')}</span>
                                </div>
                                <span style="background:{sc};color:white;padding:3px 12px;border-radius:15px;font-size:0.65rem;font-weight:700;">{status.upper()}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                       # Toggle edit mode with a button instead of expander
                        edit_key = f"edit_open_{sched['id']}"
                        if edit_key not in st.session_state:
                            st.session_state[edit_key] = False
                        
                        if not st.session_state[edit_key]:
                            if st.button("✏️ EDIT SCHEDULE", key=f"btn_open_edit_{sched['id']}", use_container_width=True):
                                st.session_state[edit_key] = True
                                st.rerun()
                        else:
                            st.markdown(f"""
                            <div style="background:#FFFBEB;border-left:5px solid #F59E0B;border-radius:8px;padding:1rem;margin:0.5rem 0;">
                                <b>✏️ Editing:</b> {sched.get('title','N/A')[:100]}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Get current dates
                            current_dates_str = ""
                            all_asset_schedules = supabase.table("ppm_schedules").select("next_due_date").eq("asset_id", sched.get("asset_id")).order("next_due_date").execute()
                            if all_asset_schedules.data:
                                current_dates = [d.get("next_due_date","")[:10] for d in all_asset_schedules.data if d.get("next_due_date")]
                                current_dates_str = ",".join(current_dates)
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                new_freq = st.selectbox("Frequency", ["Daily","Weekly","Bi-Weekly","Monthly","Quarterly","Half-Yearly","Yearly"],
                                    index=["Daily","Weekly","Bi-Weekly","Monthly","Quarterly","Half-Yearly","Yearly"].index(sched.get("frequency","Monthly")) if sched.get("frequency","Monthly") in ["Daily","Weekly","Bi-Weekly","Monthly","Quarterly","Half-Yearly","Yearly"] else 3,
                                    key=f"edit_freq_{sched['id']}")
                            with c2:
                                new_status = st.selectbox("Status", ["scheduled","completed","overdue"],
                                    index=["scheduled","completed","overdue"].index(sched.get("status","scheduled")) if sched.get("status","scheduled") in ["scheduled","completed","overdue"] else 0,
                                    key=f"edit_status_{sched['id']}")
                            
                            st.markdown("---")
                            st.markdown("### 📅 Edit Schedule Dates")
                            
                            date_edit_mode = st.radio("Date Mode", ["📅 Manual Entry", "🔄 Auto-Generate"], horizontal=True, key=f"edit_dmode_{sched['id']}")
                            
                            if date_edit_mode == "📅 Manual Entry":
                                edit_dates = st.text_area("Enter dates (comma-separated, YYYY-MM-DD)", 
                                    value=current_dates_str, height=80, key=f"edit_dates_{sched['id']}",
                                    placeholder="2026-06-29,2026-07-29,2026-08-29")
                                new_dates_list = [d.strip() for d in edit_dates.split(",") if d.strip()]
                            else:
                                if f"edit_gen_{sched['id']}" not in st.session_state:
                                    st.session_state[f"edit_gen_{sched['id']}"] = []
                                
                                c1, c2 = st.columns(2)
                                with c1:
                                    gen_start = st.date_input("Start Date", date.today(), key=f"gen_start_{sched['id']}")
                                with c2:
                                    gen_end = st.date_input("End Date", date.today() + timedelta(days=365), key=f"gen_end_{sched['id']}")
                                
                                if st.button("🔄 Generate Dates", key=f"gen_btn_{sched['id']}", use_container_width=True):
                                    dates_list = []
                                    current = gen_start
                                    while current <= gen_end:
                                        dates_list.append(current.strftime("%Y-%m-%d"))
                                        if new_freq == "Monthly":
                                            current = date(current.year, current.month+1, min(current.day,28)) if current.month < 12 else date(current.year+1,1,min(current.day,28))
                                        elif new_freq == "Quarterly":
                                            nm = current.month+3
                                            current = date(current.year+1,nm-12,min(current.day,28)) if nm > 12 else date(current.year,nm,min(current.day,28))
                                        elif new_freq == "Weekly":
                                            current += timedelta(days=7)
                                        elif new_freq == "Bi-Weekly":
                                            current += timedelta(days=14)
                                        elif new_freq == "Half-Yearly":
                                            nm = current.month+6
                                            current = date(current.year+1,nm-12,min(current.day,28)) if nm > 12 else date(current.year,nm,min(current.day,28))
                                        elif new_freq == "Yearly":
                                            current = date(current.year+1,current.month,min(current.day,28))
                                        else:
                                            current += timedelta(days=1)
                                    st.session_state[f"edit_gen_{sched['id']}"] = dates_list
                                    st.rerun()
                                
                                if st.session_state[f"edit_gen_{sched['id']}"]:
                                    selected = st.multiselect("Select Dates", st.session_state[f"edit_gen_{sched['id']}"], 
                                        default=st.session_state[f"edit_gen_{sched['id']}"][:min(5, len(st.session_state[f"edit_gen_{sched['id']}"]))],
                                        key=f"gen_sel_{sched['id']}")
                                    new_dates_list = selected
                                    st.caption(f"📅 {len(selected)} dates selected")
                                else:
                                    new_dates_list = []
                            
                            st.markdown("---")
                            
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                if st.button("💾 UPDATE ALL", key=f"btn_update_{sched['id']}", use_container_width=True, type="primary"):
                                    if new_dates_list:
                                        supabase.table("ppm_schedules").delete().eq("asset_id", sched.get("asset_id")).execute()
                                        for d in new_dates_list:
                                            supabase.table("ppm_schedules").insert({
                                                "facility_code": fc,
                                                "asset_id": sched.get("asset_id"),
                                                "title": sched.get("title",""),
                                                "frequency": new_freq,
                                                "status": new_status,
                                                "assigned_team": sched.get("assigned_team",""),
                                                "next_due_date": d,
                                                "created_at": datetime.now().isoformat()
                                            }).execute()
                                        st.success(f"✅ Updated with {len(new_dates_list)} dates!")
                                        st.session_state[edit_key] = False
                                        st.rerun()
                                    else:
                                        st.error("⚠️ Select at least one date")
                            with c2:
                                if st.button("🗑️ DELETE ALL", key=f"btn_delete_{sched['id']}", use_container_width=True):
                                    supabase.table("ppm_schedules").delete().eq("asset_id", sched.get("asset_id")).execute()
                                    st.warning(f"🗑️ All schedules deleted!")
                                    st.session_state[edit_key] = False
                                    st.rerun()
                            with c3:
                                if st.button("❌ CANCEL", key=f"btn_cancel_{sched['id']}", use_container_width=True):
                                    st.session_state[edit_key] = False
                                    st.rerun()
            else:
                st.info("No PPM schedules found.")

# ============================================
# ROUTER
# ============================================
ROUTER={
    "cc":page_cc,"ar":page_ar,"cal":page_cal,"cs":page_cs,"ppm":page_ppm,
    "wo":page_wo,"wp":page_wp,"fo":page_fo,"oa":page_oa,
    "vm": page_visitor,"up":page_users,"rt":page_raise_ticket,"hd":page_helpdesk_queue,"fb": page_feedback,
    "ac":page_ac,"ic":page_ic,"hot":page_hot,"uc":page_uc,"mis":page_mis,
    "ppma": page_ppm_activities,  # <-- ADD THIS LINE
}

# ============================================
# LOGIN PAGE
# ============================================
def login_page():
    bg_path = Path("WTC Abuja 7 (1).jpg")
    bg_base64 = ""
    if bg_path.exists():
        with open(bg_path, "rb") as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    
    if bg_base64:
        st.markdown(f"""<style>.stApp {{background: url(data:image/jpeg;base64,{bg_base64}) center/cover no-repeat fixed;}}</style>""", unsafe_allow_html=True)
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        st.markdown(f"""<div style="background:white;border-radius:16px;padding:2rem;box-shadow:0 20px 50px rgba(0,0,0,0.3);text-align:center;"><div style="display:flex;align-items:center;justify-content:center;gap:0.5rem;margin-bottom:0.3rem;">{get_nav_logo()}<div style="width:1px;height:22px;background:#ddd;"></div><span style="font-weight:800;color:#1a1a1a;font-size:1.1rem;">facility<span style="color:#CC0000;">X</span>perience</span></div><p style="color:#888;font-size:0.8rem;">Churchgate Group</p></div>""", unsafe_allow_html=True)
        
        email = st.text_input("📧 Email", placeholder="e.g. eetuk@churchgate.com", key="fx_em")
        password = st.text_input("🔑 Password", type="password", key="fx_pw")
        
        if st.button("🚀 Sign In", use_container_width=True, type="primary", key="fx_btn"):
            if email and password:
                can_attempt, rate_msg = check_login_rate_limit(email)
                if not can_attempt:
                    st.error(f"🚫 {rate_msg}")
                    st.stop()
                
                res = supabase.table("app_users").select("*").eq("email", email).eq("is_active", True).single().execute()
                if res.data and check_password(password, res.data.get("password_hash", "")):
                    log_login_attempt(email, True)
                    st.session_state.authenticated = True
                    st.session_state.user = res.data
                    st.session_state.user_name = res.data.get("name", "")
                    st.session_state.user_role = res.data.get("role", "staff")
                    supabase.table("app_users").update({"last_login": datetime.now().isoformat()}).eq("id", res.data["id"]).execute()
                    st.query_params["auth"] = "true"
                    st.query_params["user_key"] = res.data.get("email", "")
                    st.rerun()
                else:
                    log_login_attempt(email, False)
                    remaining = get_recent_failures_count(email)
                    st.error(f"Invalid email or password. {remaining} attempts remaining before lockout.")
            else:
                st.error("Please enter email and password")

def forgot_password_page():
    st.markdown("""<style>#MainMenu,header,footer{visibility:hidden;}section[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)
    
    _, col, _ = st.columns([0.3, 0.4, 0.3])
    with col:
        st.markdown(f"""<div style="background:white;border-radius:16px;padding:2rem;box-shadow:0 10px 30px rgba(0,0,0,0.2);text-align:center;"><div style="display:flex;align-items:center;justify-content:center;gap:0.5rem;margin-bottom:0.5rem;">{get_nav_logo()}<div style="width:1px;height:22px;background:#ddd;"></div><span style="font-weight:800;color:#1a1a1a;font-size:1.1rem;">facility<span style="color:#CC0000;">X</span>perience</span></div><p style="color:#888;font-size:0.8rem;">Churchgate Group</p>""", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("🔑 Forgot Password")
        st.caption("Enter your email to receive a reset link")
        
        email = st.text_input("Email", placeholder="e.g. fasuquo@churchgate.com")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📩 Send Reset Link", use_container_width=True, type="primary"):
                if email:
                    res = supabase.table("app_users").select("*").eq("email", email).single().execute()
                    if res.data:
                        token = secrets.token_urlsafe(32)
                        expiry = (datetime.now() + timedelta(hours=1)).isoformat()
                        DB.update("app_users", res.data["id"], {"reset_token": token, "reset_token_expiry": expiry})
                        reset_url = "https://facilityxperience.streamlit.app/reset?token=" + token
                        send_email_notification(email, "🔑 facilityXperience - Password Reset",
                            f"<h3>Password Reset Request</h3><p>Click below to reset your password:</p><p><a href='{reset_url}'>Reset Password</a></p><p>This link expires in 1 hour.</p>")
                        st.success(f"✅ Reset link sent to {email}")
                    else:
                        st.error("Email not found")
        with c2:
            if st.button("🔙 Back to Login", use_container_width=True):
                st.session_state.show_forgot = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def reset_password_page(token):
    st.markdown("""<style>#MainMenu,header,footer{visibility:hidden;}section[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)
    
    res = supabase.table("app_users").select("*").eq("reset_token", token).single().execute()
    if not res.data:
        st.error("Invalid or expired reset link")
        if st.button("Back to Login"):
            st.query_params.clear()
            st.rerun()
        return
    
    user = res.data
    expiry = user.get("reset_token_expiry")
    if expiry and datetime.now().isoformat() > expiry:
        st.error("Reset link has expired")
        if st.button("Request New Link"):
            st.query_params.clear()
            st.session_state.show_forgot = True
            st.rerun()
        return
    
    _, col, _ = st.columns([0.3, 0.4, 0.3])
    with col:
        st.markdown(f"""<div style="background:white;border-radius:16px;padding:2rem;box-shadow:0 10px 30px rgba(0,0,0,0.2);text-align:center;"><div style="display:flex;align-items:center;justify-content:center;gap:0.5rem;margin-bottom:0.5rem;">{get_nav_logo()}<span style="font-weight:800;color:#1a1a1a;">facility<span style="color:#CC0000;">X</span>perience</span></div></div>""", unsafe_allow_html=True)
        st.subheader("🔐 Reset Your Password")
        
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm Password", type="password")
        
        if st.button("✅ Reset Password", use_container_width=True, type="primary"):
            if new_pw and new_pw == confirm_pw:
                pw_valid, pw_msg = validate_password_strength(new_pw)
                if not pw_valid:
                    st.error(f"⚠️ {pw_msg}")
                else:
                    pw_hash = hash_password(new_pw)
                    DB.update("app_users", user["id"], {
                        "password_hash": pw_hash,
                        "reset_token": None,
                        "reset_token_expiry": None
                    })
                    st.success("✅ Password reset successfully!")
                    st.query_params.clear()
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("Passwords don't match")
        
        if st.button("🔙 Back to Login", use_container_width=True):
            st.query_params.clear()
            st.rerun()

# ============================================
# MAIN
# ============================================
def main():
    inject_css()
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "show_forgot" not in st.session_state:
        st.session_state.show_forgot = False
    
    params = st.query_params
    if params.get("auth") == "true" and not st.session_state.authenticated:
        st.session_state.authenticated = True
        if "user_key" in params:
            try:
                res = supabase.table("app_users").select("*").eq("email", params.get("user_key")).eq("is_active", True).single().execute()
                if res.data:
                    st.session_state.user = res.data
                    st.session_state.user_name = res.data.get("name", "")
                    st.session_state.user_role = res.data.get("role", "staff")
            except: pass
    
    if not st.session_state.authenticated:
        if st.session_state.show_forgot:
            forgot_password_page()
        else:
            token = params.get("token")
            if token:
                reset_password_page(token)
            else:
                login_page()
        st.stop()
    
    if "facility" not in st.session_state:
        st.session_state.facility = "WTC"
    if "page" not in st.session_state:
        st.session_state.page = "cc"
    
    fc = st.session_state.get("facility", "WTC")
    if fc == "WTC":
        wm_path = Path("WTC-logo.jpg")
        if not wm_path.exists():
            wm_path = Path("wtc-logo.jpg")
        wm_ext = "jpeg"
    else:
        wm_path = Path("churchgate-logo.png")
        wm_ext = "png"
    
    if wm_path.exists():
        with open(wm_path, "rb") as f:
            wm_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp::after {{content:'';position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:70vw;height:70vh;background-image:url(data:image/{wm_ext};base64,{wm_b64});background-size:contain;background-repeat:no-repeat;background-position:center;opacity:0.10;z-index:0;pointer-events:none;}}</style>""", unsafe_allow_html=True)
    
    check_auto_escalation(fc)
    topnav()
    
    user = st.session_state.get("user", {})
    user_name = user.get("name", "User")
    designation = user.get("designation", "")
    emp_id = user.get("employee_id", "")
    from datetime import timezone, timedelta
    wat = datetime.now(timezone(timedelta(hours=1)))
    hour = wat.hour
    greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"
    
    st.markdown(f"""<div style="background:white;padding:0.8rem 1.5rem;border-radius:8px;margin:0.5rem 1rem 1.5rem 1rem;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 3px rgba(0,0,0,0.06);"><div style="display:flex;align-items:center;gap:1rem;"><div style="width:42px;height:42px;border-radius:50%;background:{CHURCHGATE_RED};display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:1rem;">{user_name[:2].upper()}</div><div><div style="font-weight:700;font-size:1rem;color:#1a1a1a;">👋 {greeting}, {user_name}!</div><div style="font-size:0.75rem;color:#666;">{designation} • ID: {emp_id}</div></div></div><div style="font-size:0.7rem;color:#888;text-align:right;"><div>{wat.strftime('%A, %d %B %Y')}</div><div>{wat.strftime('%I:%M %p')} WAT</div></div></div>""", unsafe_allow_html=True)
    
    user_perms = safe_parse_permissions(st.session_state.get("user", {}).get("extra_permissions", []))
    user_role = st.session_state.get("user_role", "staff")
    
    page = st.session_state.page
    sidebar()
    ROUTER.get(page, page_cc)()

if __name__ == "__main__":
    main()