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
from dotenv import load_dotenv
from supabase import create_client
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# ============================================
# SUPABASE
# ============================================
SUPABASE_URL = os.getenv("SUPABASE_URL", st.secrets.get("SUPABASE_URL", "https://qxqdrlvhztkkckbvgxng.supabase.co"))
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", st.secrets.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4cWRybHZoenRra2NrYnZneG5nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5OTUyODgsImV4cCI6MjA5NjU3MTI4OH0.Q62njynXLnsLCNvwnKM7DQDrS5-UO4chDRj3XApeke8"))

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

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
        
        /* MOVE COLLAPSE BUTTON OUTSIDE SIDEBAR */
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
    def get_assets(fc, limit=500):
        try:
            res=supabase.table("assets").select("*, asset_categories(name,code)").eq("facility_code",fc).limit(limit).execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def get_categories():
        try:
            res=supabase.table("asset_categories").select("*").order("name").execute()
            return res.data if res.data else []
        except: return []

    @staticmethod
    def insert(table, data):
        try:
            res=supabase.table(table).insert(data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            st.error(f"Error: {e}"); return None

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
        import requests
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
    # Fallback if logo missing
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
        # Get user info FIRST
        user_perms = st.session_state.get("user", {}).get("extra_permissions", [])
        if isinstance(user_perms, str):
            try: user_perms = eval(user_perms)
            except: user_perms = []
        user_role = st.session_state.get("user_role", "staff")
        is_admin = user_role in ["admin", "approver"]
        user_home_facility = st.session_state.get("user", {}).get("home_facility", "WTC")
        
        sel = st.session_state.get("facility", "WTC")
        
        # Facility selector - restricted for non-admin
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
        
        # Role-based navigation
        all_nav = [
            ("🏠 COMMAND", [("🌐 Command Center", "cc"), ("📊 PPM Dashboard", "ppm")], ["Command Center", "PPM Dashboard"]),
            ("🏗️ ASSETS & PPM", [("📋 Asset Register", "ar"), ("📅 52-Week Calendar", "cal"), ("✅ Checklist Status", "cs")], ["Asset Register", "52-Week Calendar", "Checklist Status"]),
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

# ============================================
# ASSET REGISTER (SmartCheck Style)
# ============================================
def page_ar():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📋 Asset Register — {info.get("full_name",fc)}')
    cats=DB.get_categories()
    cat_names=["All Departments"]+sorted(list(set(c.get("name","") for c in cats)))
    all_assets=DB.get_assets(fc,500)
    col1,col2=st.columns(2)
    with col1:selected_dept=st.selectbox("Select Department",cat_names)
    with col2:
        asset_types=["All Assets"]
        if all_assets and selected_dept!="All Departments":
            asset_types+=sorted(list(set(a.get("name","") for a in all_assets if a.get("asset_categories",{}).get("name","")==selected_dept)))
        elif all_assets:asset_types+=sorted(list(set(a.get("name","") for a in all_assets)))
        selected_asset=st.selectbox("Select Asset",asset_types)
    if all_assets:
        df=pd.DataFrame(all_assets)
        df["department"]=df["asset_categories"].apply(lambda x: x.get("name","") if isinstance(x,dict) else "")
        if selected_dept!="All Departments":df=df[df["department"]==selected_dept]
        if selected_asset!="All Assets":df=df[df["name"]==selected_asset]
        st.metric("Assets Found",len(df))
        st.dataframe(df[[c for c in ["asset_tag","name","department","manufacturer","model","serial_number","location_building","location_floor","status","condition_rating"] if c in df.columns]],use_container_width=True,hide_index=True,height=500)

# ============================================
# WORK PERMIT — COMPLETE FIXED MODULE
# ============================================
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
            # Only return people whose department_filter includes this department
            filtered = [p for p in people if "All Departments" in p.get("department_filter", []) or department in p.get("department_filter", [])]
            if filtered:
                return filtered
        # Fallback: return people with "All Departments" only
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
    
    user_perms = st.session_state.get("user", {}).get("extra_permissions", [])
    if isinstance(user_perms, str):
        try: user_perms = eval(user_perms)
        except: user_perms = []
    user_role = st.session_state.get("user_role", "staff")
    is_admin = user_role in ["admin", "approver"]
    can_authorize = is_admin or "Authorize Permit" in user_perms or len(user_perms) == 0
    can_confirm = is_admin or "Confirm Permit" in user_perms or len(user_perms) == 0
    can_approve = is_admin or "Approve Permit" in user_perms or len(user_perms) == 0
    can_raise = is_admin or "Raise Permit" in user_perms or len(user_perms) == 0
    
    st.markdown(f'## 🛡️ Permit-to-Work System — {info.get("full_name", fc)}')
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Permits", "➕ Raise Permit", "📊 Reports", "⚙️ Workflow Config"])
    
    # ============================================
    # TAB 1: ALL PERMITS
    # ============================================
    with tab1:
        st.markdown("### 📋 Work Permit Register")
        
        # Fetch permits - no date filter that could hide results
        wp = DB.get_all("work_permits", fc, 500)
        
        if wp and len(wp) > 0:
            df = pd.DataFrame(wp)
            
            # KPI Cards
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.metric("📋 Total", len(df))
            with c2: st.metric("⏳ Submitted", len(df[df["workflow_stage"] == "submitted"]) if "workflow_stage" in df.columns else 0)
            with c3: st.metric("🔐 Authorized", len(df[df["workflow_stage"] == "authorized"]) if "workflow_stage" in df.columns else 0)
            with c4: st.metric("✅ Confirmed", len(df[df["workflow_stage"] == "confirmed"]) if "workflow_stage" in df.columns else 0)
            with c5: st.metric("🟢 Approved", len(df[df["workflow_stage"] == "approved"]) if "workflow_stage" in df.columns else 0)
            
            st.markdown("---")
            
            # Display each permit
            for i, row in df.iterrows():
                stage = row.get("workflow_stage", "submitted")
                icons = {"submitted": "⏳", "authorized": "🔐", "confirmed": "✅", "approved": "🟢", "rejected": "❌"}
                icon = icons.get(stage, "📋")
                
                title = row.get('title', 'No Title')[:80]
                permit_no = row.get('permit_number', 'N/A')
                
                status_colors = {"submitted":"#F59E0B","authorized":"#3B82F6","confirmed":"#8B5CF6","approved":"#10B981","rejected":"#EF4444"}
                # Custom card with inline expand
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
            st.info("📋 No work permits found. Raise your first permit in the '➕ Raise Permit' tab!")
    
    # ============================================
    # TAB 2: RAISE PERMIT
    # ============================================
    with tab2:
        st.markdown("### 📝 Raise New Work Permit")
        
        # Get buildings
        buildings = DB.get_locations(fc)
        
        # Build proper display mapping
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
            # Dynamic sub-locations based on selected building
            sub_locs = get_sub_locations_for_building(fc, selected_building)
            if not sub_locs or len(sub_locs) == 0:
                sub_locs = [f"{selected_building} / 0"]
            sub_location = st.selectbox("Sub-Location*", sub_locs, key="wp_subloc")
        
        full_location = f"{building_options.get(selected_building, selected_building)} → {sub_location}"
        st.caption(f"📍 Full Location: {full_location}")
        
        st.markdown("---")
        
        # THE FORM STARTS HERE
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
            
            full_location = f"{building_options.get(selected_building, selected_building)} → {sub_location}"
            
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
    
    # ============================================
    # TAB 3: REPORTS
    # ============================================
    with tab3:
        st.markdown("### 📊 Work Permit Analytics & Reports")
        wp_all = DB.get_all("work_permits", fc, 500)
        
        if wp_all and len(wp_all) > 0:
            df = pd.DataFrame(wp_all)
            
            # SHARED METRICS (used by both PDF and HTML)
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
            
            # KPI Row
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.metric("📋 Total", total)
            with c2: st.metric("🟢 Approved", approved_count)
            with c3: st.metric("⏳ Pending", pending_count)
            with c4: st.metric("❌ Rejected", rejected_count)
            with c5: st.metric("⏱️ Avg Approval", f"{avg_lead:.1f} hrs")
            
            st.markdown("---")
            
            # ============================================
            # CLICKABLE MONTHLY BREAKDOWN
            # ============================================
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
            
            # ============================================
            # ANALYTICS SUMMARY
            # ============================================
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
            
            # ============================================
            # PDF & HTML REPORT GENERATION
            # ============================================
            st.markdown("### 📄 Generate Reports")
            report_format = st.radio("Select Format", ["📄 PDF Download", "🌐 HTML Preview & Download"], horizontal=True)
            
            if report_format == "📄 PDF Download":
                if st.button("📊 Generate PDF Report", use_container_width=True, type="primary"):
                    try:
                        from fpdf import FPDF
                        
                        class FullPDF(FPDF):
                            def header(self):
                                logo_path = Path("churchgate-logo.png")
                                if logo_path.exists():
                                    self.image(str(logo_path), x=14, y=8, h=10)
                                self.set_text_color(255,255,255)
                                self.set_fill_color(26,26,26)
                                self.rect(10,22,277,14,'F')
                                self.set_fill_color(204,0,0)
                                self.rect(10,22,4,14,'F')
                                self.set_font('Helvetica','B',11)
                                self.set_xy(18,24)
                                self.cell(260,5,f'Helpdesk Report - {rpt_month} {rpt_year}',0,0,'L')
                                self.set_font('Helvetica','',8)
                                self.set_xy(18,29)
                                self.cell(260,5,f'{safe_text(info.get("full_name",fc))} | {total} tickets',0,0,'L')
                                self.set_y(40)
                            def footer(self):
                                self.set_y(-18)
                                self.set_font('Helvetica','I',7)
                                self.set_text_color(150,150,150)
                                self.cell(0,8,f'Page {{nb}} | Churchgate Group | Confidential',0,0,'C')
                        
                        pdf = FullPDF('L','mm','A4')
                        pdf.alias_nb_pages()
                        pdf.add_page()
                        
                        kpis = [("Total",str(total),204,0,0),("Open",str(open_count),239,68,68),("In Progress",str(in_progress),245,158,11),("Closed",str(closed_count),16,185,129),("Avg Resolution",avg_display,37,99,235)]
                        xs,ys = pdf.get_x(),pdf.get_y()
                        for i,(l,v,r,g,b) in enumerate(kpis):
                            x = xs + (i*55)
                            pdf.set_fill_color(245,245,245)
                            pdf.set_draw_color(r,g,b)
                            pdf.rect(x,ys,50,15,'DF')
                            pdf.set_fill_color(r,g,b)
                            pdf.rect(x,ys,3,15,'F')
                            pdf.set_xy(x+5,ys+2)
                            pdf.set_font('Helvetica','',6)
                            pdf.set_text_color(100,100,100)
                            pdf.cell(42,4,l.upper(),0,0,'C')
                            pdf.set_xy(x+5,ys+7)
                            pdf.set_font('Helvetica','B',12)
                            pdf.set_text_color(r,g,b)
                            pdf.cell(42,6,v,0,0,'C')
                        pdf.set_y(ys+20)
                        pdf.ln(4)
                        
                        pdf.set_font('Helvetica','B',6)
                        pdf.set_fill_color(204,0,0)
                        pdf.set_text_color(255,255,255)
                        cw = [8,24,32,30,28,38,26,16,14,16,20,10]
                        headers = ['#','DateTime','Ticket No','Location','Category','Title','Raised By','Priority','Status','Age','Closed','Lvl']
                        for h,w in zip(headers,cw):
                            pdf.cell(w,5.5,f' {h}',1,0,'L',True)
                        pdf.ln()
                        pdf.set_font('Helvetica','',5.5)
                        pdf.set_text_color(26,26,26)
                        for _,r in report_df.iterrows():
                            vals = [
                                safe_text(str(r['SNo']),''), safe_text(str(r['DateTime']),''),
                                safe_text(str(r['Ticket No']),''), safe_text(str(r['Location']),''),
                                safe_text(str(r['Category']),''), safe_text(str(r['Title']),''),
                                safe_text(str(r['Raised By']),''), safe_text(str(r['Priority']),''),
                                safe_text(str(r['Status']),''), safe_text(str(r['Age']),''),
                                safe_text(str(r['Closed']),''), safe_text(str(r['Level']),''),
                            ]
                            for v,w in zip(vals,cw):
                                pdf.cell(w,4.5,f' {v[:w-2]}',1,0)
                            pdf.ln()
                        
                        pdf_file = f"/tmp/hd_report.pdf"
                        pdf.output(pdf_file)
                        with open(pdf_file,"rb") as f:
                            st.download_button("📥 PDF",f.read(),"helpdesk_report.pdf","application/pdf",use_container_width=True)
                    except Exception as e:
                        st.error(f"PDF: {str(e)[:60]}")
            
            else:
                # HTML Report
                st.markdown("### 🌐 HTML Report Preview")
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
    
    # ============================================
    # TAB 4: WORKFLOW CONFIG (MULTI-SELECT)
    # ============================================
    with tab4:
        if not is_admin:
            st.error("⛔ Admin access only")
            st.stop()
        st.markdown("### ⚙️ Workflow Configuration")
        st.caption("Manage who authorizes, confirms, and approves work permits")
        
        # Show current config in nice cards
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
        
        # Add Person Form with Multi-Select Departments
        with st.form("wf_add_person"):
            st.markdown("### ➕ Add Person to Workflow")
            
            c1, c2 = st.columns(2)
            with c1:
                new_level = st.selectbox("Level", [1, 2, 3], 
                    format_func=lambda x: {1: "Level 1 — Authorization", 2: "Level 2 — Confirmation", 3: "Level 3 — Approval"}[x])
                new_name = st.text_input("Full Name*", placeholder="e.g. Francis Asuquo")
            with c2:
                new_email = st.text_input("Email Address*", placeholder="e.g. fasuquo@churchgate.com")
            
            # Multi-select departments like PPE selector
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
    
    
    # AI SMART CHAT — FULL DUPLEX WITH MEMORY
    st.markdown("### 🤖 facilityXpert — AI Assistant")
    
    user_email = st.session_state.get("user", {}).get("email", "guest")
    
    # Load or create chat session
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []
    if "ai_conversation" not in st.session_state:
        st.session_state.ai_conversation = []
    
    # Try to load last session from DB
    if not st.session_state.ai_chat_history and user_email != "guest":
        try:
            saved = supabase.table("ai_chat_sessions").select("*").eq("user_email", user_email).order("updated_at", desc=True).limit(1).execute()
            if saved.data:
                msgs = saved.data[0].get("messages", [])
                if isinstance(msgs, str):
                    msgs = eval(msgs)
                st.session_state.ai_chat_history = msgs
                st.session_state.ai_conversation = msgs[-20:]
        except: pass
    
    # Display chat history
    for msg in st.session_state.ai_chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
    
    # Clear chat button — always visible
    if st.session_state.ai_chat_history:
        if st.button("🗑️ Clear Chat History", key="clear_btn", use_container_width=True):
            st.session_state.ai_chat_history = []
            st.session_state.ai_conversation = []
            user_email = st.session_state.get("user", {}).get("email", "guest")
            try:
                supabase.table("ai_chat_sessions").delete().eq("user_email", user_email).execute()
            except: pass
            st.rerun()
    
    
    
    # Chat input
    prompt = st.chat_input("Ask facilityXpert anything...", key="ai_chat_main")
    
    if prompt:
        st.session_state.ai_chat_history.append({"role": "user", "content": prompt})
        st.session_state.ai_conversation.append({"role": "user", "content": prompt})
        
        with st.spinner("🤖 Thinking..."):
            hc = DB.get_helpdesk_categories()
            cat_names_list = sorted(list(set(c.get("category_name", "") for c in hc)))
            
            try:
                import requests
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
                
                # Check if AI wants to create a ticket
                if ai_response and ("TICKET:" in ai_response.upper() or "I've created a ticket" in ai_response or "created a ticket" in ai_response):
                    try:
                        cnt = len(DB.get_all("tickets", fc, 1000))
                        ticket_number = f"TKT-{fc}-{datetime.now().strftime('%d%H%M%S')}"
                        
                        DB.insert("tickets", {
                            "facility_code": fc,
                            "ticket_number": ticket_number,
                            "title": prompt[:100],
                            "description": prompt,
                            "category": "Internet Outage",
                            "priority": "medium",
                            "status": "open",
                            "requester_name": st.session_state.get("user_name", "AI User"),
                            "requester_email": st.session_state.get("user", {}).get("email", ""),
                            "location_building": "AI Assisted",
                            "sla_deadline": (datetime.now() + timedelta(hours=4)).isoformat(),
                            "escalation_level": 1,
                            "created_at": datetime.now().isoformat()
                        })
                        
                        ai_response = ai_response.replace("WTCABJ-001234", ticket_number)
                        ai_response += f"\n\n✅ Real ticket: {ticket_number}"
                    except:
                        pass
            except:
                ai_response = None
                kb = supabase.table("knowledge_base").select("*").or_(f"question.ilike.%{prompt}%,tags.ilike.%{prompt}%").limit(3).execute()
                if kb.data:
                    ai_response = "Solutions from knowledge base:\n\n" + "\n\n".join([f"**{k.get('question')}**\n{k.get('answer','')}" for k in kb.data])
                else:
                    ai_response = "I couldn't find a solution. Please raise a ticket."
            
            st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_response})
            st.session_state.ai_conversation.append({"role": "assistant", "content": ai_response})
            
            # Save to database
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
                
                # Send email to department authorizers
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
                
                # Send email to escalation Level 1
                # Get category_id for this ticket
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
    
    # MY TICKETS WITH RATINGS
    st.markdown("---")
    st.markdown("### 📋 My Tickets")
    
    user_name = st.session_state.get('user_name', '')
    user_email = st.session_state.get('user', {}).get('email', '')
    
    my_tickets = supabase.table("tickets").select("*").eq("facility_code", fc).or_(f"requester_name.eq.{user_name},requester_email.eq.{user_email}").order("created_at", desc=True).limit(20).execute()
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
            
            # Rating for closed tickets
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


# ============================================
# HELPDESK — WORLD CLASS TICKET SYSTEM v2.0
# FINAL VERSION — GREY BUTTONS + COLLAPSIBLE LOCATIONS
# ============================================

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
    # TAB 0: HOME — TICKET QUEUE
    # ============================================
    with tabs[0]:
        statuses = ["All", "Open", "In Progress", "Hold", "Closed", "Rejected"]
        status_icons = {"All": "📋", "Open": "🔴", "In Progress": "🟡", "Hold": "⏸️", "Closed": "🟢", "Rejected": "❌"}
        status_colors = {"All": "#4a4a4a", "Open": "#EF4444", "In Progress": "#F59E0B", "Hold": "#3B82F6", "Closed": "#10B981", "Rejected": "#6B7280"}
        
        if "ticket_status_filter" not in st.session_state:
            st.session_state.ticket_status_filter = "All"
        
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
        search = st.text_input("🔍 Search tickets", placeholder="Search by title, ID, or requester...", key="hd_search")
        
        status_filter = st.session_state.ticket_status_filter
        filter_status = status_filter.lower().replace(" in progress", "in_progress") if status_filter != "All" else None
        tickets = DB.get_tickets_filtered(fc, status=filter_status, search=search if search else None)
        
        user_depts = st.session_state.get("user", {}).get("department_permissions", [])
        if isinstance(user_depts, str):
            try: user_depts = eval(user_depts)
            except: user_depts = []
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
            kpi_cols = st.columns(6)
            kpi_data = [("📋 Total", len(df), "#4a4a4a"),("🔴 Open", len(df[df["status"]=="open"]) if "status" in df.columns else 0, "#EF4444"),("🟡 In Progress", len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0, "#F59E0B"),("⏸️ Hold", len(df[df["status"]=="hold"]) if "status" in df.columns else 0, "#3B82F6"),("🟢 Closed", len(df[df["status"]=="closed"]) if "status" in df.columns else 0, "#10B981"),("❌ Rejected", len(df[df["status"]=="rejected"]) if "status" in df.columns else 0, "#6B7280")]
            for i, (label, value, color) in enumerate(kpi_data):
                with kpi_cols[i]:
                    st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;text-align:center;border-left:4px solid {color};box-shadow:0 1px 3px rgba(0,0,0,0.06);"><div style="font-size:0.65rem;color:#888;">{label}</div><div style="font-size:1.6rem;font-weight:800;">{value}</div></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            
            if "open_ticket_detail" not in st.session_state:
                st.session_state.open_ticket_detail = None
            
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
                    st.markdown(f"""<div style="background:white;border-radius:10px;padding:0.8rem;margin:0.4rem 0;border-left:4px solid {sc};box-shadow:0 1px 3px rgba(0,0,0,0.04);"><div style="display:flex;justify-content:space-between;"><span><b>{si} {row.get('ticket_number','')}</b> — {row.get('requester_name','N/A')}</span><span style="font-size:0.7rem;color:#888;">⏱️ {age_str}</span></div><div style="margin-top:0.2rem;font-size:0.8rem;">{row.get('title','')[:100]}</div><div style="font-size:0.65rem;color:#888;">📍 {row.get('location_building','')} | 🏷️ {row.get('category','')} | L{row.get('escalation_level',1)}</div></div>""", unsafe_allow_html=True)
                    
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
                    
                    if is_open:
                        with st.container():
                            st.markdown(f"""<div style="background:#f9fafb;border-radius:10px;padding:1rem;margin:0.5rem 0;border:1px solid #e5e7eb;"><h4 style="margin:0;">{row.get('title','')}</h4><p style="color:#666;font-size:0.8rem;"><b>Ticket:</b> {row.get('ticket_number','')} | <b>Status:</b> {status.upper()} | <b>Level:</b> L{row.get('escalation_level',1)}</p><p style="font-size:0.8rem;"><b>Raised by:</b> {row.get('requester_name','N/A')} | <b>Category:</b> {row.get('category','')} | <b>Priority:</b> {row.get('priority','')}</p><p style="font-size:0.8rem;"><b>Location:</b> {row.get('location_building','')}</p><p style="font-size:0.8rem;"><b>Description:</b> {row.get('description','')}</p><p style="font-size:0.75rem;color:#888;"><b>SLA:</b> {format_wat_time(row.get('sla_deadline',''))}</p></div>""", unsafe_allow_html=True)
                            
                            comments = DB.get_ticket_comments(ticket_id)
                            if comments:
                                st.caption("📝 Progress Log:")
                                for c in comments:
                                    st.caption(f"👤 {c.get('user_name','')} — {c.get('created_at','')[:16]}: {c.get('comment_text','')}")
                            
                            st.markdown("**⚡ Actions:**")
                            ac1, ac2, ac3 = st.columns(3)
                            
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
                                        st.rerun()
                                with ac3:
                                    if st.button("✅ Close", key=f"det_close_{ticket_id}", use_container_width=True):
                                        DB.update("tickets", ticket_id, {"status": "closed", "closed_at": datetime.now().isoformat()})
                                        if row.get("requester_email"):
                                            send_email_notification(row["requester_email"], f"✅ Ticket {row.get('ticket_number','')} Resolved", f"<h3>Ticket Resolved</h3><p>Please rate your experience.</p>")
                                        st.success("✅ Closed!")
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
                                
                                # Re-Assign form
                                if "reassign_ticket" in st.session_state and st.session_state.reassign_ticket == ticket_id:
                                    all_users = DB.get_users()
                                    user_names = [u.get("name","") for u in all_users]
                                    reassign_to = st.selectbox("Re-assign to", user_names, key=f"reassign_{ticket_id}")
                                    c1, c2 = st.columns(2)
                                    with c1:
                                        if st.button("✅ Confirm Re-Assign", key=f"confirm_reassign_{ticket_id}", use_container_width=True):
                                            DB.update("tickets", ticket_id, {"assigned_to": reassign_to})
                                            DB.insert("ticket_comments", {"ticket_id": ticket_id, "user_name": st.session_state.get("user_name","Staff"), "comment_text": f"Re-assigned to {reassign_to}"})
                                            send_email_notification(row.get("requester_email",""), f"🔄 Ticket {row.get('ticket_number','')} Re-Assigned", f"<h3>Ticket Re-Assigned</h3><p>Your ticket has been re-assigned to {reassign_to}.</p>")
                                            st.success(f"✅ Re-assigned to {reassign_to}!")
                                            st.session_state.reassign_ticket = None
                                            st.rerun()
                                    with c2:
                                        if st.button("❌ Cancel", key=f"cancel_reassign_{ticket_id}", use_container_width=True):
                                            st.session_state.reassign_ticket = None
                                            st.rerun()
                                
                                # More Info form
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
                                
                                # Escalate
                                if is_admin:
                                    esc_level = row.get("escalation_level", 1)
                                    if esc_level < 6:
                                        if st.button(f"🔺 Escalate L{esc_level}→L{esc_level+1}", key=f"det_esc_{ticket_id}", use_container_width=True):
                                            DB.update("tickets", ticket_id, {"escalation_level": esc_level + 1})
                                            st.success(f"🔺 Escalated!")
                                            st.rerun()
                            
                            if status == "closed":
                                if st.button("🔄 Re-Open", key=f"det_reopen_{ticket_id}", use_container_width=True):
                                    DB.update("tickets", ticket_id, {"status": "open"})
                                    st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No tickets found")
    
    # ============================================
    # TAB 1: AI-POWERED ANALYTICS
    # ============================================
    with tabs[1]:
        st.markdown("### 📊 AI-Powered Helpdesk Analytics")
        
        all_tickets = DB.get_all("tickets", fc, 500)
        if all_tickets:
            df = pd.DataFrame(all_tickets)
            
            # METRICS
            total = len(df)
            open_count = len(df[df["status"]=="open"]) if "status" in df.columns else 0
            in_progress = len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0
            hold_count = len(df[df["status"]=="hold"]) if "status" in df.columns else 0
            closed_count = len(df[df["status"]=="closed"]) if "status" in df.columns else 0
            rejected_count = len(df[df["status"]=="rejected"]) if "status" in df.columns else 0
            
            # Resolution time
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
            
            # SLA
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
            
            # First Response Time
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
            
            # Priority breakdown
            priority_breakdown = df["priority"].value_counts().to_dict() if "priority" in df.columns else {}
            critical_high = priority_breakdown.get("critical", 0) + priority_breakdown.get("high", 0)
            backlog = open_count + in_progress + hold_count
            
            # KPI ROW
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1: st.metric("📋 Total", total)
            with c2: st.metric("🔴 Open", open_count)
            with c3: st.metric("🟡 In Progress", in_progress)
            with c4: st.metric("⏸️ Hold", hold_count)
            with c5: st.metric("🟢 Closed", closed_count)
            with c6: st.metric("⏱️ Avg Resolution", avg_display)
            
            st.markdown("---")
            
            # SLA COMPLIANCE
            st.markdown("#### ⏱️ SLA Compliance")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("✅ SLA Met", sla_met)
                st.progress(sla_met / total if total > 0 else 0, text=f"{sla_met}/{total}")
            with c2:
                st.metric("⚠️ SLA Exceeded", sla_exceeded)
                st.progress(sla_exceeded / total if total > 0 else 0, text=f"{sla_exceeded}/{total}")
            
            st.markdown("---")
            
            # CHARTS
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
            
            # MONTHLY TREND
            if "created_at" in df.columns:
                df["month"] = pd.to_datetime(df["created_at"]).dt.month
                df["month_name"] = df["month"].apply(lambda x: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][x-1])
                monthly = df.groupby("month_name").size().reset_index(name="count")
                fig3 = px.line(monthly, x="month_name", y="count", title="📈 Monthly Ticket Volume", markers=True, line_shape="spline")
                fig3.update_layout(height=300)
                st.plotly_chart(fig3, use_container_width=True)
            
            # EXECUTIVE KPI DASHBOARD
            st.markdown("---")
            st.markdown("#### 🏢 Executive KPI Dashboard")
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("🔥 Critical/High", critical_high)
                st.caption("Urgent tickets")
            with c2:
                rate = round((closed_count/total)*100) if total > 0 else 0
                st.metric("📈 Resolution Rate", f"{rate}%")
                st.caption("Tickets resolved")
            with c3:
                st.metric("⏱️ First Response SLA", f"{frt_met}/{total}")
                st.caption("Acknowledged within 30m")
            with c4:
                st.metric("📋 Current Backlog", backlog)
                st.caption("Awaiting resolution")
            
            # Department Performance
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
            
            # AI INSIGHTS
            st.markdown("---")
            st.markdown("#### 🤖 AI Insights")
            overdue = 0
            if "sla_deadline" in df.columns:
                now = datetime.now()
                for _, r in df.iterrows():
                    try:
                        if pd.to_datetime(r["sla_deadline"]) < now and r.get("status") not in ["closed","rejected"]:
                            overdue += 1
                    except: pass
            
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
    # TAB 2: PROFESSIONAL REPORTS
    # ============================================
    with tabs[2]:
        st.markdown("### 📄 Helpdesk Reports")
        
        rpt_type = st.selectbox("Report Type", ["Monthly Report", "Customized Report", "Tickets Carry Forward"])
        
        all_tickets = DB.get_all("tickets", fc, 500)
        all_users = DB.get_users()
        occupant_options = ["All Occupants", "Internal Team"] + sorted(list(set(
            t.get("occupant_name","") for t in all_tickets if t.get("occupant_name") and str(t.get("occupant_name")) != "None"
        )))
        categories = DB.get_helpdesk_categories()
        cat_options = ["All"] + sorted(list(set(c.get("category_name","") for c in categories)))
        status_options = ["All", "open", "in_progress", "hold", "closed", "rejected"]
        
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
            
            rpt_month = "Custom"
            rpt_year = ""
            
        else:  # Tickets Carry Forward
            rpt_year = st.selectbox("Select Year", [2024,2025,2026,2027], key="tcf_year")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                rpt_occupant = st.selectbox("Select Occupant", occupant_options, key="tcf_occ")
            with c2:
                rpt_category = st.selectbox("Category", cat_options, key="tcf_cat")
            with c3:
                rpt_status = st.selectbox("Select Status", status_options, key="tcf_status")
            
            rpt_month = "Carry Forward"
        
        if st.button("📊 Generate Report", use_container_width=True):
            if all_tickets:
                df = pd.DataFrame(all_tickets)
                
                # Apply filters
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
                    open_count = len(df[df["status"]=="open"]) if "status" in df.columns else 0
                    in_progress = len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0
                    hold_count = len(df[df["status"]=="hold"]) if "status" in df.columns else 0
                    closed_count = len(df[df["status"]=="closed"]) if "status" in df.columns else 0
                    
                    resolution_times = []
                    if "created_at" in df.columns and "closed_at" in df.columns:
                        for _, r in df.iterrows():
                            try:
                                closed_val = r.get("closed_at")
                                if closed_val and str(closed_val) != "None" and str(closed_val) != "nan" and str(closed_val) != "":
                                    hrs = (pd.to_datetime(closed_val) - pd.to_datetime(r["created_at"])).total_seconds() / 3600
                                    if hrs > 0: resolution_times.append(hrs)
                            except: pass
                    avg_resolution = round(sum(resolution_times) / len(resolution_times), 1) if resolution_times else 0
                    avg_display = f"{avg_resolution}h" if avg_resolution > 0 else "N/A"
                    
                    st.success(f"✅ Report generated — {total} tickets")
                    
                    c1, c2, c3, c4, c5, c6 = st.columns(6)
                    with c1: st.metric("📋 Total", total)
                    with c2: st.metric("🔴 Open", open_count)
                    with c3: st.metric("🟡 In Progress", in_progress)
                    with c4: st.metric("⏸️ Hold", hold_count)
                    with c5: st.metric("🟢 Closed", closed_count)
                    with c6: st.metric("⏱️ Avg Resolution", avg_display)
                    
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
                    
                    # Downloads
                    st.markdown("---")
                    st.markdown("### 📥 Download Reports")
                    
                    logo_b64 = get_logo_base64()
                    logo_html = f'<img src="data:image/png;base64,{logo_b64}" height="35">' if logo_b64 else ''
                    
                    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;margin:25px;color:#1a1a1a;font-size:11px}}.header{{background:#1a1a1a;color:white;padding:18px 20px;border-radius:10px;display:flex;align-items:center;gap:15px;margin-bottom:20px}}.header h1{{margin:0;font-size:19px}}.kpi-row{{display:flex;gap:8px;margin:15px 0}}.kpi{{flex:1;background:#f5f5f5;border-radius:8px;padding:10px;text-align:center;border-left:4px solid #CC0000}}.kpi.green{{border-left-color:#10B981}}.kpi-val{{font-size:22px;font-weight:bold;color:#CC0000}}.kpi-label{{font-size:9px;color:#666}}table{{width:100%;border-collapse:collapse;font-size:10px}}th{{background:#CC0000;color:white;padding:7px 5px;text-align:left;font-size:8px}}td{{padding:4px 5px;border-bottom:1px solid #ddd}}.footer{{margin-top:25px;font-size:9px;color:#999;text-align:center;border-top:1px solid #ddd;padding-top:12px}}</style></head><body><div class="header">{logo_html}<div><h1>Helpdesk Report - {rpt_month} {rpt_year}</h1><p style="font-size:10px;opacity:0.8">{safe_text(info.get('full_name',fc))} | {datetime.now().strftime('%d %B %Y, %I:%M %p WAT')}</p></div></div><div class="kpi-row"><div class="kpi"><div class="kpi-val">{total}</div><div class="kpi-label">Total</div></div><div class="kpi"><div class="kpi-val">{open_count}</div><div class="kpi-label">Open</div></div><div class="kpi"><div class="kpi-val">{in_progress}</div><div class="kpi-label">In Progress</div></div><div class="kpi green"><div class="kpi-val">{closed_count}</div><div class="kpi-label">Closed</div></div><div class="kpi"><div class="kpi-val">{avg_display}</div><div class="kpi-label">Avg Resolution</div></div></div><h2>Tickets</h2><table><tr><th>#</th><th>DateTime</th><th>Ticket</th><th>Location</th><th>Category</th><th>Title</th><th>By</th><th>Priority</th><th>Status</th><th>Age</th><th>Closed</th></tr>"""
                    
                    for _, r in report_df.iterrows():
                        html += f"<tr><td>{r['SNo']}</td><td>{r['DateTime']}</td><td>{r['Ticket No']}</td><td>{r['Location']}</td><td>{r['Category']}</td><td>{r['Title']}</td><td>{r['Raised By']}</td><td>{r['Priority']}</td><td>{r['Status']}</td><td>{r['Age']}</td><td>{r['Closed']}</td></tr>"
                    
                    html += f"</table><div class='footer'>Churchgate Group | facilityXperience | Confidential</div></body></html>"
                    
                    with st.expander("🌐 HTML Preview", expanded=True):
                        st.components.v1.html(html, height=500, scrolling=True)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.download_button("📥 HTML", html, f"helpdesk_report.html", "text/html", use_container_width=True)
                    with c2:
                        st.download_button("📥 CSV", df.to_csv(index=False), f"helpdesk_report.csv", "text/csv", use_container_width=True)
                    with c3:
                        try:
                            from fpdf import FPDF
                            pdf = FPDF('L','mm','A4')
                            pdf.add_page()
                            logo_path = Path("churchgate-logo.png")
                            if logo_path.exists():
                                pdf.image(str(logo_path), x=14, y=8, h=10)
                            pdf.set_font('Helvetica','B',14)
                            pdf.set_text_color(204,0,0)
                            pdf.set_xy(14,22)
                            pdf.cell(260,8,f'Helpdesk Report - {rpt_month} {rpt_year}',0,1)
                            pdf.set_font('Helvetica','',9)
                            pdf.set_text_color(0,0,0)
                            pdf.set_xy(14,30)
                            pdf.cell(260,6,f'{safe_text(info.get("full_name",fc))} | Total: {total} tickets',0,1)
                            pdf.ln(5)
                            pdf.set_font('Helvetica','B',7)
                            pdf.set_fill_color(204,0,0)
                            pdf.set_text_color(255,255,255)
                            cw = [8,24,28,24,24,28,22,14,14,18,18,12]
                            for h,w in zip(['#','DateTime','Ticket','Location','Category','Title','By','Priority','Status','Age','Closed','Lvl'],cw):
                                pdf.cell(w,5.5,f' {h}',1,0,'L',True)
                            pdf.ln()
                            pdf.set_font('Helvetica','',6)
                            pdf.set_text_color(26,26,26)
                            for _,r in report_df.head(40).iterrows():
                                vals = [safe_text(str(r[c]),'')[:w-2] for c,w in zip(['SNo','DateTime','Ticket No','Location','Category','Title','Raised By','Priority','Status','Age','Closed','Level'],cw)]
                                for v,w in zip(vals,cw):
                                    pdf.cell(w,4.5,f' {v}',1,0)
                                pdf.ln()
                            pdf_file = f"/tmp/hd_report.pdf"
                            pdf.output(pdf_file)
                            with open(pdf_file,"rb") as f:
                                st.download_button("📥 PDF",f.read(),"helpdesk_report.pdf","application/pdf",use_container_width=True)
                        except Exception as e:
                            st.error(f"PDF: {str(e)[:60]}")
            else:
                st.info("No ticket data available")
    
    # ============================================
    # TAB 3: ESCALATION SETTINGS
    # ============================================
    with tabs[3]:
        if not is_admin:
            st.error("⛔ Admin access only")
        else:
            st.markdown("### ⏱️ Escalation Configuration")
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
                    
                    # Get existing escalation data
                    existing = supabase.table("ticket_escalation").select("*").eq("facility_code", fc).eq("category_id", cat_id).order("level_number").execute()
                    
                    # Build form with pre-selected values
                    for level in range(1, 7):
                        # Get existing users for this level
                        existing_users = []
                        existing_time = 30 if level <= 2 else 60 if level == 3 else 1440
                        existing_unit = "Mins"
                        
                        if existing.data:
                            for e in existing.data:
                                if e.get("level_number") == level:
                                    user_str = f"{e.get('escalate_to_name','')} ({e.get('escalate_to_email','')})"
                                    existing_users.append(user_str)
                                    existing_time = e.get("sla_minutes", 30)
                        
                        # Convert time to display unit
                        if existing_time >= 1440:
                            existing_time = existing_time // 1440
                            existing_unit = "Days"
                        elif existing_time >= 60:
                            existing_time = existing_time // 60
                            existing_unit = "Hours"
                        
                        st.markdown(f"**Level {level}**")
                        c1, c2, c3 = st.columns([3, 1, 1])
                        with c1: 
                            st.multiselect(f"Users L{level}", user_options, default=existing_users, key=f"esc_u_{level}_{cat_id}")
                        with c2: 
                            st.number_input(f"Time", min_value=0, value=existing_time, key=f"esc_t_{level}_{cat_id}")
                        with c3: 
                            st.selectbox(f"Unit", ["Mins","Hours","Days"], index=["Mins","Hours","Days"].index(existing_unit), key=f"esc_ty_{level}_{cat_id}")
                        st.markdown("---")
                    
                    if st.button("💾 Save Escalation Settings", use_container_width=True, key="save_esc_btn"):
                        saved_count = 0
                        for level in range(1, 7):
                            time_val = st.session_state.get(f"esc_t_{level}_{cat_id}", 30)
                            time_type = st.session_state.get(f"esc_ty_{level}_{cat_id}", "Mins")
                            if time_type == "Hours": time_val *= 60
                            elif time_type == "Days": time_val *= 1440
                            users = st.session_state.get(f"esc_u_{level}_{cat_id}", [])
                            
                            # Delete existing
                            try:
                                supabase.table("ticket_escalation").delete().eq("facility_code", fc).eq("category_id", cat_id).eq("level_number", level).execute()
                            except: pass
                            
                            # Insert new
                            for u in users:
                                if "(" in u and ")" in u:
                                    email = u.split("(")[-1].replace(")","").strip()
                                    name = u.split("(")[0].strip()
                                    try:
                                        supabase.table("ticket_escalation").insert({
                                            "facility_code": fc, "category_id": cat_id, "level_number": level,
                                            "level_name": f"Level {level}", "escalate_to_name": name,
                                            "escalate_to_email": email, "sla_minutes": time_val
                                        }).execute()
                                        saved_count += 1
                                    except: pass
                        
                        st.success(f"✅ Escalation saved! {saved_count} entries configured.")
                        st.balloons()
    
    # ============================================
    # TAB 4: SETTINGS
    # ============================================
    with tabs[4]:
        if not is_admin:
            st.error("⛔ Admin access only")
        else:
            st.markdown("### ⚙️ Helpdesk Settings")
            sett_tabs = st.tabs(["📍 Locations", "🏷️ Categories", "📊 Status"])
            
            # ============================================
            # LOCATIONS TABLE
            # ============================================
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
                            "Location": f"{loc_code}",
                            "Sub Locations": f"{sub_count} subs",
                            "View": "🔍 View",
                            "Action": "✏️ Edit"
                        })
                    
                    if table_data:
                        # Pagination
                        page_size = 10
                        total_pages = max(1, (len(table_data) + page_size - 1) // page_size)
                        
                        if "loc_page" not in st.session_state:
                            st.session_state.loc_page = 1
                        
                        start = (st.session_state.loc_page - 1) * page_size
                        end = start + page_size
                        page_data = table_data[start:end]
                        
                        st.caption(f"Showing {start+1} to {min(end, len(table_data))} of {len(table_data)} entries")
                        
                        # Table
                        for row in page_data:
                            c1, c2, c3, c4, c5 = st.columns([0.5, 2, 1.5, 1, 1])
                            with c1: st.markdown(f"**{row['SNO']}**")
                            with c2: st.markdown(row["Location"])
                            with c3: st.markdown(row["Sub Locations"])
                            with c4:
                                loc_id = None
                                for l in locs:
                                    if l.get("location_code") == row["Location"]:
                                        loc_id = l["id"]
                                        break
                                if loc_id:
                                    if st.button("🔍 View", key=f"view_loc_{loc_id}", use_container_width=True):
                                        st.session_state.view_loc_id = loc_id
                                        st.rerun()
                            with c5:
                                if st.button("✏️ Edit", key=f"edit_loc_{loc_id}", use_container_width=True):
                                    st.session_state.edit_loc_id = loc_id
                                    st.rerun()
                            st.markdown("---")
                        
                        # Pagination controls
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
                    
                    # VIEW SUB LOCATIONS
                    if "view_loc_id" in st.session_state and st.session_state.view_loc_id:
                        loc_id = st.session_state.view_loc_id
                        loc_info = next((l for l in locs if l["id"] == loc_id), None)
                        
                        if loc_info:
                            st.markdown("---")
                            st.markdown(f"#### 📍 Sublocations for {loc_info.get('location_name','')}")
                            
                            subs = DB.get_sub_locations(loc_id)
                            if subs:
                                for s in subs:
                                    c1, c2 = st.columns([4, 1])
                                    with c1: st.markdown(f"└ {s.get('sub_location_name','')}")
                                    with c2: 
                                        if st.button("✏️", key=f"edit_sub_{s['id']}", use_container_width=True):
                                            pass
                            else:
                                st.info("No sub-locations")
                            
                            with st.form(f"add_sub_loc_{loc_id}"):
                                new_sub = st.text_input("Add SubLocation", key=f"new_sub_{loc_id}")
                                if st.form_submit_button("➕ Add SubLocation"):
                                    if new_sub:
                                        supabase.table("helpdesk_sub_locations").insert({"location_id": loc_id, "sub_location_name": new_sub}).execute()
                                        st.success("✅ Added!")
                                        st.rerun()
                            
                            if st.button("❌ Close View", key=f"close_view_loc_{loc_id}"):
                                st.session_state.view_loc_id = None
                                st.rerun()
                
                # ADD NEW LOCATION
                st.markdown("---")
                with st.form("add_loc_form"):
                    st.markdown("**➕ Add New Location**")
                    c1, c2 = st.columns(2)
                    with c1:
                        new_loc_code = st.text_input("Location Code", key="loc_code")
                        new_loc_name = st.text_input("Location Name", key="loc_name")
                    with c2:
                        new_sub_name = st.text_input("Initial Sub-Location (optional)", key="sub_name")
                    if st.form_submit_button("➕ Add Location"):
                        if new_loc_code and new_loc_name:
                            res = supabase.table("helpdesk_locations").insert({"facility_code":fc,"location_code":new_loc_code,"location_name":new_loc_name}).execute()
                            if res.data and new_sub_name:
                                supabase.table("helpdesk_sub_locations").insert({"location_id":res.data[0]["id"],"sub_location_name":new_sub_name}).execute()
                            st.success("✅ Added!")
                            st.rerun()
            
            # ============================================
            # CATEGORIES TABLE
            # ============================================
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
                            "SLA": f"{c.get('sla_hours','4')}hrs"
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
                            c1, c2, c3, c4, c5, c6 = st.columns([0.5, 2, 2, 1, 1, 1])
                            with c1: st.markdown(f"**{row['SNO']}**")
                            with c2: st.markdown(row["Department"])
                            with c3: st.markdown(row["Category"])
                            with c4: st.markdown(row["SLA"])
                            with c5: st.button("✏️", key=f"edit_cat_{row['SNO']}", use_container_width=True)
                            with c6: st.button("🔍", key=f"view_cat_{row['SNO']}", use_container_width=True)
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
                    with c1: new_cat = st.text_input("Category Name", key="cat_name")
                    with c2: new_dept = st.selectbox("Department", sorted(list(set(c.get("department","") for c in categories))), key="cat_dept")
                    with c3: new_sla = st.number_input("SLA Hours", 1, 72, 4, key="cat_sla")
                    if st.form_submit_button("➕ Add Category"):
                        if new_cat:
                            supabase.table("helpdesk_categories").insert({"department":new_dept,"category_name":new_cat,"sla_hours":new_sla}).execute()
                            st.success("✅ Added!")
                            st.rerun()
            
            # ============================================
            # STATUS
            # ============================================
            with sett_tabs[2]:
                st.markdown("#### 📊 Status Configuration")
                st.info("Default statuses: Open, In Progress, Hold, Closed, Rejected")
                st.caption("Custom status management coming soon.")

# ============================================
# INCIDENT CHECK
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
    "Engineering — Civil & Structural",
    "Engineering — Electrical",
    "Engineering — HVAC",
    "Engineering — Plumbing",
    "Engineering — Vertical Transportation (Lifts)",
    "Engineering — Fire Fighting",
    "Engineering — Utilities & Energy",
    "Engineering — Fabrication & Foundry",
    "Engineering — Design & Specification",
    "Facility Management — Hard Services",
    "Facility Management — Soft Services (Housekeeping)",
    "Facility Management — Soft Services (Waste Management)",
    "Facility Management — Front of House & Reception",
    "Facility Management — Landscaping & Grounds",
    "Facility Management — Transport & Fleet",
    "Facility Management — First Aid & Clinical",
    "Facility Management — FM Operations & Helpdesk",
    "Facility Management — HSSE Safety & Compliance",
    "Facility Management — HSSE Risk & BCP",
    "Facility Management — HSSE Incident Investigation",
    "Facility Management — Fitout Works & Finishing",
    "Technology Group — Network & Connectivity",
    "Technology Group — IT Service Desk",
    "Technology Group — ERP & Business Systems",
    "Technology Group — Cloud & Infrastructure",
    "Technology Group — Building Technology (BMS/CCTV/ACS)",
    "Technology Group — Software Development",
    "Technology Group — AI & Innovation",
    "Technology Group — Cybersecurity",
    "Security — Man Guarding Operations",
    "Security — Command Center (24/7)",
    "Security — Gatehouse & Access Control",
    "Security — Executive Protection",
    "Procurement — Strategic Sourcing",
    "Procurement — Contract Management",
    "Procurement — Purchase & Requisition",
    "Central Stores — Inventory Management",
    "Central Stores — Goods Inwards & QA",
    "Central Stores — Critical Spares",
    "Sales & Marketing — Business Development",
    "Sales & Marketing — Bid & Tender Management",
    "Contractor — Clyde Engineering",
    "Contractor — Gates and Shield",
    "Contractor — TXB Enterprise Ltd",
    "Contractor — Brainworks",
    "Contractor — Metalplex",
    "Contractor — Berger Paints",
    "Contractor — ENI-AGIP General Services",
    "Vendor — Augkenos Options",
    "Vendor — Blue Group",
    "Vendor — T & T Synergy",
    "Vendor — Regal Krees Engineering",
    "Vendor — Jotbofs Technologies",
    "Vendor — 21st Century Evolution",
    "Vendor — HICL S&P Contractor"
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
# VISITOR MANAGEMENT — WORLD CLASS SYSTEM
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
        
        # Stats
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
                
                # Quick actions
                c1, c2, c3 = st.columns([1,1,1])
                with c1:
                    if status in ["expected", "pre_registered"]:
                        if st.button("✅ Check In", key=f"vin_{v['id']}", use_container_width=True):
                            supabase.table("visitors").update({"status": "checked_in", "actual_arrival": datetime.now().isoformat()}).eq("id", v["id"]).execute()
                            # Notify host
                            if v.get("host_email"):
                                send_email_notification(v["host_email"], f"✅ Guest Arrived: {v.get('full_name','')}",
                                    f"""
                                    <div style="font-family:Arial;max-width:400px;border:1px solid #10B981;border-radius:8px;overflow:hidden;">
                                        <div style="background:#10B981;padding:15px;color:white;">
                                            <h3 style="margin:0;">✅ Guest Has Arrived</h3>
                                            <p style="margin:3px 0 0 0;font-size:11px;">{info.get('full_name',fc)}</p>
                                        </div>
                                        <div style="padding:15px;">
                                            <p>Dear {v.get('host_name','')},</p>
                                            <p><b>{v.get('full_name','')}</b> from <b>{v.get('company','')}</b> has arrived and is waiting for you.</p>
                                            <table style="width:100%;font-size:12px;">
                                                <tr><td style="padding:3px;"><b>🕐 Check-in:</b></td><td>{datetime.now().strftime('%I:%M %p')}</td></tr>
                                                <tr><td style="padding:3px;"><b>📍 Location:</b></td><td>{v.get('gate_location','Main Gate')}</td></tr>
                                                <tr><td style="padding:3px;"><b>🎯 Purpose:</b></td><td>{v.get('purpose_of_visit','')}</td></tr>
                                            </table>
                                            <div style="margin-top:12px;text-align:center;">
                                                <a href="https://facilityxperience.streamlit.app" style="background:#CC0000;color:white;padding:8px 20px;text-decoration:none;border-radius:6px;font-size:12px;">View in facilityXperience</a>
                                            </div>
                                        </div>
                                    </div>
                                    """)
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
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            st.markdown("---")
            st.markdown("**🏢 Visit Details**")
            c1, c2, c3 = st.columns(3)
            with c1:
                host_name = st.text_input("Host Name*")
                arrival_time = st.time_input("Expected Arrival", time(9, 0))
            with c2:
                host_email = st.text_input("Host Email")
                departure_time = st.time_input("Expected Departure", time(17, 0))
            with c3:
                host_phone = st.text_input("Host Phone")
                purpose = st.text_area("Purpose of Visit", height=60)
            
            belongings = st.text_area("Belongings/Equipment", placeholder="Laptop, tools, etc...")
            
            st.markdown("---")
            
            if st.button("🛂 Register Visitor", use_container_width=True, type="primary"):
                if first_name and last_name and host_name:
                    import random, string
                    pass_id = f"VIS-{fc}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
                    access_code_in = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    access_code_out = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    access_code = f"IN:{access_code_in}|OUT:{access_code_out}"
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=IN:{access_code_in}%7COUT:{access_code_out}"
                    
                    # Get logo for pass
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
                    
                    # Show generated pass
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
                    
                    # Send rich email to visitor
                    if email:
                        send_email_notification(email, f"🛂 Your Access Pass - {info.get('full_name',fc)}",
                            f"""
                            <div style="font-family:Arial;max-width:450px;margin:0 auto;border:2px solid #CC0000;border-radius:12px;overflow:hidden;">
                                <div style="background:#CC0000;padding:15px;color:white;text-align:center;">
                                    {f'<img src="{logo_src}" height="30" style="margin-bottom:8px;"><br>' if logo_src else ''}
                                    <h2 style="margin:0;">VISITOR ACCESS PASS</h2>
                                    <p style="margin:3px 0 0 0;font-size:11px;opacity:0.9;">{info.get('full_name',fc)}</p>
                                </div>
                                <div style="padding:20px;text-align:center;">
                                    <h3 style="margin:0 0 5px 0;">{first_name} {last_name}</h3>
                                    <p style="color:#666;margin:0 0 10px 0;">{company}</p>
                                    <img src="{qr_url}" width="180" style="border:1px solid #ddd;padding:5px;border-radius:8px;">
                                    <div style="display:flex;justify-content:center;gap:30px;margin:15px 0;">
                                        <div style="text-align:center;">
                                            <div style="font-size:10px;color:#888;">🟢 ENTRY CODE</div>
                                            <div style="font-size:1.3rem;font-weight:bold;font-family:monospace;color:#10B981;">{access_code_in}</div>
                                        </div>
                                        <div style="text-align:center;">
                                            <div style="font-size:10px;color:#888;">🔴 EXIT CODE</div>
                                            <div style="font-size:1.3rem;font-weight:bold;font-family:monospace;color:#EF4444;">{access_code_out}</div>
                                        </div>
                                    </div>
                                    <table style="width:100%;font-size:11px;text-align:left;margin-top:10px;">
                                        <tr><td style="padding:4px;font-weight:bold;">📅 Date:</td><td>{visit_date}</td></tr>
                                        <tr><td style="padding:4px;font-weight:bold;">⏰ Time:</td><td>{arrival_time} - {departure_time}</td></tr>
                                        <tr><td style="padding:4px;font-weight:bold;">👤 Host:</td><td>{host_name}</td></tr>
                                        <tr><td style="padding:4px;font-weight:bold;">🆔 Pass ID:</td><td>{pass_id}</td></tr>
                                    </table>
                                    <div style="margin-top:15px;padding:10px;background:#FFF3CD;border-radius:8px;font-size:10px;color:#92400E;">
                                        ⚠️ Please present this QR code at the gate. Overstaying beyond your scheduled time will flag security.
                                    </div>
                                </div>
                                <div style="background:#f9f9f9;padding:10px;text-align:center;font-size:9px;color:#999;">
                                    Churchgate Group | facilityXperience | Auto-generated Pass
                                </div>
                            </div>
                            """)
                    
                    # Send rich email to host
                    if host_email:
                        send_email_notification(host_email, f"🛂 Visitor Expected: {first_name} {last_name}",
                            f"""
                            <div style="font-family:Arial;max-width:500px;border:1px solid #ddd;border-radius:8px;overflow:hidden;">
                                <div style="background:#CC0000;padding:15px;color:white;">
                                    <h3 style="margin:0;">📋 Visitor Pre-Registered</h3>
                                    <p style="margin:3px 0 0 0;font-size:11px;opacity:0.9;">{info.get('full_name',fc)}</p>
                                </div>
                                <div style="padding:15px;">
                                    <p>Dear {host_name},</p>
                                    <p><b>{first_name} {last_name}</b> from <b>{company}</b> is scheduled to visit you.</p>
                                    <table style="width:100%;font-size:12px;border-collapse:collapse;">
                                        <tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">📅 Date</td><td style="padding:5px;border-bottom:1px solid #eee;">{visit_date}</td></tr>
                                        <tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">⏰ Time</td><td style="padding:5px;border-bottom:1px solid #eee;">{arrival_time} - {departure_time}</td></tr>
                                        <tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">🎯 Purpose</td><td style="padding:5px;border-bottom:1px solid #eee;">{purpose}</td></tr>
                                        <tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">🆔 Pass ID</td><td style="padding:5px;border-bottom:1px solid #eee;">{pass_id}</td></tr>
                                        <tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">🟢 Entry Code</td><td style="padding:5px;border-bottom:1px solid #eee;font-family:monospace;color:#10B981;">{access_code_in}</td></tr>
                                        <tr><td style="padding:5px;border-bottom:1px solid #eee;font-weight:bold;">🔴 Exit Code</td><td style="padding:5px;border-bottom:1px solid #eee;font-family:monospace;color:#EF4444;">{access_code_out}</td></tr>
                                        <tr><td style="padding:5px;font-weight:bold;">🚗 Vehicle</td><td style="padding:5px;">{vehicle or 'N/A'}</td></tr>
                                    </table>
                                    <div style="margin-top:12px;padding:10px;background:#f0f8ff;border-radius:6px;font-size:11px;">
                                        💡 <b>Forward this email</b> to your guest — it contains their access codes and QR pass for entry.
                                    </div>
                                    <p style="font-size:10px;color:#888;margin-top:10px;">You'll be notified when your guest arrives at the gate.</p>
                                </div>
                            </div>
                            """)
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ First Name, Last Name, and Host Name are required")
        
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
                    bulk_host = st.text_input("Host Name*")
                    bulk_date = st.date_input("Visit Date", today)
                with c2:
                    bulk_purpose = st.text_input("Purpose of Visit*")
                    bulk_arrival = st.time_input("Arrival Time", time(9,0))
                with c3:
                    bulk_email = st.text_input("Host Email")
                    bulk_departure = st.time_input("Departure Time", time(17,0))
                
                if st.button(f"🛂 Register {len(csv_data)} Visitors", use_container_width=True, type="primary"):
                    if bulk_host and bulk_purpose:
                        import random, string
                        count = 0
                        for _, row in csv_data.iterrows():
                            first = str(row.get("First Name","") or row.get("first_name",""))
                            last = str(row.get("Last Name","") or row.get("last_name",""))
                            if first and last:
                                pass_id = f"VIS-{fc}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits,k=4))}"
                                access_code_in = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                                access_code_out = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    access_code = f"IN:{access_code_in}|OUT:{access_code_out}"
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=IN:{access_code_in}%7COUT:{access_code_out}"
                    
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
                        st.error(f"Insert error: {str(e)}")
                        st.stop()
        
        elif reg_mode == "Quick Batch Entry":
            st.markdown("#### 📝 Quick Batch Entry")
            st.caption("Enter visitor names (one per line) for quick registration")
            
            batch_names = st.text_area("Visitor Names", height=150, placeholder="John Doe\nJane Smith\nBob Johnson\n...")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                batch_host = st.text_input("Host Name*", key="batch_host")
                batch_date = st.date_input("Visit Date", today, key="batch_date")
            with c2:
                batch_purpose = st.text_input("Purpose of Visit*", key="batch_purpose")
                batch_arrival = st.time_input("Arrival Time", time(9,0), key="batch_arrival")
            with c3:
                batch_email = st.text_input("Host Email", key="batch_email")
                batch_departure = st.time_input("Departure Time", time(17,0), key="batch_departure")
            
            if st.button("🛂 Register Batch", use_container_width=True, type="primary"):
                if batch_host and batch_purpose and batch_names:
                    import random, string
                    names = [n.strip() for n in batch_names.split("\n") if n.strip()]
                    count = 0
                    for name in names:
                        parts = name.split(" ", 1)
                        first = parts[0]
                        last = parts[1] if len(parts) > 1 else ""
                        
                        pass_id = f"VIS-{fc}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits,k=4))}"
                        access_code_in = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                        access_code_out = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                        
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
                    
                    st.success(f"✅ {count} visitors registered!")
                    st.balloons()
                    st.rerun()

            else:
                st.error("⚠️ First Name, Last Name, and Host Name are required")
    
    # ============================================
    # TAB 2: GATE CHECK CONSOLE (ADMIN/SECURITY ONLY)
    # ============================================
    with tabs[2]:
        if not is_admin:
            st.error("⛔ Access restricted to Security & Admin personnel only")
        else:
            st.markdown("### 🛂 Gate Check Console")
            
            gate_tabs = st.tabs(["🔍 Verify Entry", "📋 Today's Log", "🚨 Alerts", "📊 Live Feed"])
            
            # ============================================
            # GATE TAB 0: VERIFY ENTRY
            # ============================================
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
                                        supabase.table("visitor_gate_log").insert({"visitor_id":v["id"],"event_type":"check_in","gate_location":"Main Gate","scanned_by":st.session_state.get("user_name","Security")}).execute()
                                        if v.get("host_email"):
                                            send_email_notification(v["host_email"], f"✅ Guest Arrived: {v.get('full_name','')}",
                                                f"""<div style="font-family:Arial;max-width:400px;border:1px solid #10B981;border-radius:8px;overflow:hidden;"><div style="background:#10B981;padding:15px;color:white;"><h3>✅ Guest Has Arrived</h3></div><div style="padding:15px;"><p>Dear {v.get('host_name','')},</p><p><b>{v.get('full_name','')}</b> from <b>{v.get('company','')}</b> has arrived.</p></div></div>""")
                                        st.success("✅ Checked In!")
                                        st.rerun()
                            with c2:
                                if action == "CHECK OUT":
                                    if st.button("🚪 Confirm Check Out", use_container_width=True):
                                        supabase.table("visitors").update({"status":"checked_out","actual_departure":datetime.now().isoformat()}).eq("id",v["id"]).execute()
                                        supabase.table("visitor_gate_log").insert({"visitor_id":v["id"],"event_type":"check_out","gate_location":"Main Gate","scanned_by":st.session_state.get("user_name","Security")}).execute()
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
                                            "Security Flag": v.get("security_flag"),
                                            "NDA Signed": v.get("nda_signed"),
                                            "Safety Briefing": v.get("safety_briefing"),
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
            
            # ============================================
            # GATE TAB 1: TODAY'S LOG
            # ============================================
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
            
            # ============================================
            # GATE TAB 2: ALERTS
            # ============================================
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
            
            # ============================================
            # GATE TAB 3: LIVE FEED
            # ============================================
            with gate_tabs[3]:
                st.markdown("#### 📊 Live Activity Feed")
                
                recent_logs = supabase.table("visitor_gate_log").select("*, visitors(full_name, company)").order("event_time", desc=True).limit(30).execute()
                
                if recent_logs.data:
                    for log in recent_logs.data:
                        icon = "✅" if log.get("event_type") == "check_in" else "🚪" if log.get("event_type") == "check_out" else "🚩"
                        v_info = log.get("visitors", {})
                        name = v_info.get("full_name","Unknown") if v_info else "Unknown"
                        company = v_info.get("company","") if v_info else ""
                        st.markdown(f"{icon} **{name}** ({company}) — {log.get('event_type','').upper()} at {log.get('event_time','')} by {log.get('scanned_by','')}")
                else:
                    st.info("No activity yet")
    
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
                
                st.dataframe(df[[c for c in ["full_name","company","visitor_type","host_name","purpose_of_visit","visit_date","expected_arrival","status","vehicle_plate"] if c in df.columns]], use_container_width=True, hide_index=True)
                
                csv = df.to_csv(index=False)
                st.download_button("📥 CSV", csv, f"visitors_{rpt_month}_{rpt_year}.csv", "text/csv", use_container_width=True)

# ============================================
# USER MANAGEMENT — FULL ADMIN MODULE
# ============================================
def page_users():
    st.markdown("## 👥 User Management")
    
    tabs = st.tabs(["📋 User Directory", "➕ Add User", "✏️ Edit User"])
    
    # ============================================
    # TAB 0: USER DIRECTORY
    # ============================================
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
                        depts = row.get("department_permissions", [])
                        if isinstance(depts, str):
                            try: depts = eval(depts)
                            except: depts = [depts]
                        st.write(f"**Departments:** {', '.join(depts) if depts else 'All'}")
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
    
    # ============================================
    # TAB 1: ADD USER
    # ============================================
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
            all_depts = [
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
            new_depts = st.multiselect("Select Departments (leave empty for All)", all_depts, key="add_depts")
            
            submitted = st.form_submit_button("➕ Create User", use_container_width=True, type="primary")
            if submitted:
                if new_name and new_emp_id and new_email and new_designation and new_password:
                    import hashlib
                    pw_hash = hashlib.sha256(new_password.encode()).hexdigest()
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
    
    # ============================================
    # TAB 2: EDIT USER
    # ============================================
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
                            import hashlib
                            pw_hash = hashlib.sha256(new_pw.encode()).hexdigest()
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
                    
                    existing_perms = user.get("extra_permissions", [])
                    if isinstance(existing_perms, str):
                        try: existing_perms = eval(existing_perms)
                        except: existing_perms = []
                    
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
# GENERIC PAGES
# ============================================
def page_generic(title,icon=""):
    st.markdown(f'## {icon} {title}')
    st.info("🚧 Module structure ready. Full deployment in progress.")

# ============================================
# FACILITY OPERATIONS DASHBOARD
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
# OBSERVATIONS & ALERTS
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
# AUDIT CHECKLIST
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
# VOICE OF CUSTOMER — FEEDBACK SYSTEM
# ============================================
def page_feedback():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    user_role = st.session_state.get("user_role", "staff")
    is_admin = user_role in ["admin", "approver"]
    
    st.markdown(f'## ⭐ Voice of Customer — {info.get("full_name", fc)}')
    
    tabs = st.tabs(["📝 Take Survey", "📊 Feedback Dashboard", "📈 AI Analytics", "⚙️ Survey Admin"])
    
    # ============================================
    # TAB 0: TAKE SURVEY
    # ============================================
    with tabs[0]:
        # Get active survey
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
                    
                    # Respondent info
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
                            emoji_map = {4: "😍", 3: "🙂", 2: "😐", 1: "😞"}
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
                            # Create response
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
    
    # ============================================
    # TAB 1: FEEDBACK DASHBOARD
    # ============================================
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
                        scores = supabase.table("feedback_scores").select("score").eq("question_id", q["id"]).execute()
                        if scores.data:
                            avg_score = sum(sc["score"] for sc in scores.data) / len(scores.data)
                            stars = "⭐" * round(avg_score)
                            st.markdown(f"**{q.get('question_number')}. {q.get('category','')}**")
                            st.markdown(f"{stars} **{avg_score:.1f}/4**")
                            st.progress(avg_score / 4)
        else:
            st.info("No survey data yet")
    
    # ============================================
    # TAB 2: AI ANALYTICS
    # ============================================
    with tabs[2]:
        st.markdown("### 🤖 AI-Powered Feedback Analytics")
        
        survey = supabase.table("feedback_surveys").select("*").eq("facility_code", fc).order("created_at", desc=True).limit(1).execute()
        
        if survey.data:
            s = survey.data[0]
            questions = supabase.table("feedback_questions").select("*").eq("survey_id", s["id"]).order("question_number").execute()
            
            if questions.data:
                categories = []
                avg_scores = []
                
                for q in questions.data:
                    if q.get("question_type") == "rating":
                        scores = supabase.table("feedback_scores").select("score").eq("question_id", q["id"]).execute()
                        if scores.data:
                            avg = sum(sc["score"] for sc in scores.data) / len(scores.data)
                            categories.append(q.get("category",""))
                            avg_scores.append(round(avg, 1))
                
                if categories:
                    # Bar chart
                    fig = px.bar(x=categories, y=avg_scores, title="Satisfaction by Category", 
                                labels={"x":"","y":"Score"}, color=avg_scores, 
                                color_continuous_scale=["#EF4444","#F59E0B","#3B82F6","#10B981"],
                                range_color=[1,4])
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # AI Insights
                    st.markdown("### 🤖 AI Recommendations")
                    best = categories[avg_scores.index(max(avg_scores))]
                    worst = categories[avg_scores.index(min(avg_scores))]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"🌟 **Strength:** {best} ({max(avg_scores)}/4)")
                        st.caption("Continue investing in this area")
                    with col2:
                        st.error(f"⚠️ **Needs Attention:** {worst} ({min(avg_scores)}/4)")
                        st.caption("Priority improvement area")
                    
                    if min(avg_scores) < 2.5:
                        st.warning(f"🚨 **Retention Risk:** Low satisfaction in {worst} may impact tenant retention. Recommend immediate action plan.")
                    
                    if max(avg_scores) >= 3.5:
                        st.info(f"💡 **Marketing Opportunity:** High satisfaction in {best} can be leveraged in marketing materials.")
        else:
            st.info("No data for analytics")
    
    # ============================================
    # TAB 3: SURVEY ADMIN (ADMIN ONLY)
    # ============================================
    with tabs[3]:
        if not is_admin:
            st.error("⛔ Admin access only")
        else:
            st.markdown("### ⚙️ Survey Administration")
            
            # Current surveys
            surveys = supabase.table("feedback_surveys").select("*").eq("facility_code", fc).order("created_at", desc=True).execute()
            
            if surveys.data:
                st.markdown("**Existing Surveys:**")
                for s in surveys.data:
                    status_badge = "🟢 Active" if s.get("is_active") else "⚪ Inactive"
                    st.markdown(f"- **{s.get('title','')}** — {status_badge} | {s.get('start_date','')} to {s.get('end_date','')}")
            
            st.markdown("---")
            
            # Activate/Deactivate survey
            with st.form("survey_admin"):
                st.markdown("**Manage Survey**")
                
                survey_options = {s.get("title",""): s["id"] for s in surveys.data} if surveys.data else {}
                selected_survey = st.selectbox("Select Survey", list(survey_options.keys())) if survey_options else None
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("🟢 Activate Survey", use_container_width=True):
                        if selected_survey:
                            # Deactivate all others
                            supabase.table("feedback_surveys").update({"is_active": False}).eq("facility_code", fc).execute()
                            # Activate selected
                            supabase.table("feedback_surveys").update({"is_active": True}).eq("id", survey_options[selected_survey]).execute()
                            st.success(f"✅ {selected_survey} activated!")
                            st.rerun()
                with c2:
                    if st.form_submit_button("⚪ Deactivate All", use_container_width=True):
                        supabase.table("feedback_surveys").update({"is_active": False}).eq("facility_code", fc).execute()
                        st.success("All surveys deactivated")
                        st.rerun()
            
            st.markdown("---")
            
            # Broadcast email to tenants
            st.markdown("### 📧 Broadcast Survey to Tenants")
            
            # Get all tenants
            tenants = supabase.table("organizations").select("*").eq("type", "tenant").eq("is_active", True).execute()
            
            if tenants.data:
                # Show tenant list with checkboxes
                st.markdown("**Select tenants to receive the survey:**")
                
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
                                            <p>We invite you to participate in our half-yearly tenant satisfaction survey. Your feedback helps us improve our services.</p>
                                            <p><b>Time to complete:</b> Less than 5 minutes</p>
                                            <div style="text-align:center;margin:25px 0;">
                                                <a href="{survey_link}" style="background:#CC0000;color:white;padding:12px 30px;text-decoration:none;border-radius:6px;font-weight:bold;">Take Survey Now</a>
                                            </div>
                                            <p style="font-size:11px;color:#888;">Your responses are confidential and will be used to enhance your workplace experience.</p>
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
# UTILITY DASHBOARD
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
# PPM DASHBOARD
# ============================================
def page_ppm():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📊 PPM Dashboard — {info.get("full_name",fc)}')
    ppm=DB.get_all("ppm_schedules",fc,50)
    if ppm:
        df=pd.DataFrame(ppm)
        c1,c2,c3=st.columns(3)
        with c1:st.metric("Total Schedules",len(df))
        with c2:st.metric("Due This Week",len(df[pd.to_datetime(df["next_due_date"]).dt.date<=date.today()+timedelta(days=7)]) if "next_due_date" in df.columns else 0)
        with c3:st.metric("Critical",len(df[df["is_critical"]==True]) if "is_critical" in df.columns else 0)
        for i,row in df.iterrows():
            with st.expander(f"{row.get('title','')} — Due: {row.get('next_due_date','')} — {row.get('frequency','')}"):
                st.write(f"**Team:** {row.get('assigned_team','')} | **Priority:** {row.get('priority','')}")
                if st.button("✅ Mark Complete",key=f"ppm_{row['id']}"):DB.update("ppm_schedules",row["id"],{"status":"completed","last_completed_date":str(date.today())});st.rerun()
    else:st.info("No PPM schedules")

# ============================================
# 52-WEEK CALENDAR
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
# CHECKLIST STATUS
# ============================================
def page_cs():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ✅ Checklist Status — {info.get("full_name",fc)}')
    cats=DB.get_categories()
    cat_names=sorted(list(set(c.get("name","") for c in cats)))
    dept=st.selectbox("Select Department",cat_names)
    assets=DB.get_assets(fc,200)
    if assets:
        df=pd.DataFrame(assets)
        df["department"]=df["asset_categories"].apply(lambda x: x.get("name","") if isinstance(x,dict) else "")
        df=df[df["department"]==dept] if dept else df
        st.dataframe(df[[c for c in ["asset_tag","name","status","condition_rating","location_building","location_floor"] if c in df.columns]],use_container_width=True,hide_index=True)

# ============================================
# COMPLETE ROUTER (REPLACE PREVIOUS ROUTER)
# ============================================
ROUTER={
    "cc":page_cc,"ar":page_ar,"cal":page_cal,"cs":page_cs,"ppm":page_ppm,
    "wo":page_generic,"wp":page_wp,"fo":page_fo,"oa":page_oa,
    "vm": page_visitor,"up":page_users,"rt":page_raise_ticket,"hd":page_helpdesk_queue,"fb": page_feedback,
    "ac":page_ac,"ic":page_ic,"hot":page_generic,"uc":page_uc,"mis":page_generic,
}


# ============================================
# LOGIN PAGE
# ============================================
def check_password(password, stored_hash):
    """Verify password"""
    if not stored_hash:
        return False
    # Try hex digest
    if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
        return True
    # Try digest
    if hashlib.sha256(password.encode()).digest() == stored_hash:
        return True
    return False

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
                res = supabase.table("app_users").select("*").eq("email", email).eq("is_active", True).single().execute()
                if res.data and check_password(password, res.data.get("password_hash", "")):
                    st.session_state.authenticated = True
                    st.session_state.user = res.data
                    st.session_state.user_name = res.data.get("name", "")
                    st.session_state.user_role = res.data.get("role", "staff")
                    supabase.table("app_users").update({"last_login": datetime.now().isoformat()}).eq("id", res.data["id"]).execute()
                    # Set query params for session persistence
                    st.query_params["auth"] = "true"
                    st.query_params["user_key"] = res.data.get("email", "")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            else:
                st.error("Please enter email and password")
        
        if st.button("🔑 Forgot Password?", use_container_width=True, key="fx_fg"):
            st.session_state.show_forgot = True
            st.rerun()

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
                        
                        # Get the app URL from Streamlit
                        reset_url = "https://facilityxperience.streamlit.app/reset?token=" + token
                        
                        send_email_notification(
                            email,
                            "🔑 facilityXperience - Password Reset",
                            f"<h3>Password Reset Request</h3>"
                            f"<p>You requested a password reset for your facilityXperience account.</p>"
                            f"<p><b>Click the link below to reset your password:</b></p>"
                            f"<p><a href='{reset_url}' style='background:#CC0000;color:white;padding:10px 20px;text-decoration:none;border-radius:6px;'>Reset Password</a></p>"
                            f"<p>This link expires in 1 hour.</p>"
                            f"<p>If you didn't request this, ignore this email.</p>"
                        )
                        
                        st.success(f"✅ Reset link sent to {email}")
                        st.info("📧 Check your inbox and spam folder")
                    else:
                        st.error("Email not found")
                else:
                    st.error("Please enter your email")
        with c2:
            if st.button("🔙 Back to Login", use_container_width=True):
                st.session_state.show_forgot = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def reset_password_page(token):
    """Handle password reset with token"""
    st.markdown("""<style>#MainMenu,header,footer{visibility:hidden;}section[data-testid="stSidebar"]{display:none;}</style>""", unsafe_allow_html=True)
    
    # Verify token
    res = supabase.table("app_users").select("*").eq("reset_token", token).single().execute()
    if not res.data:
        st.error("Invalid or expired reset link")
        if st.button("Back to Login"):
            st.query_params.clear()
            st.session_state.show_forgot = False
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
        st.markdown(f"""<div style="background:white;border-radius:16px;padding:2rem;box-shadow:0 10px 30px rgba(0,0,0,0.2);text-align:center;"><div style="display:flex;align-items:center;justify-content:center;gap:0.5rem;margin-bottom:0.5rem;">{get_nav_logo()}<div style="width:1px;height:22px;background:#ddd;"></div><span style="font-weight:800;color:#1a1a1a;font-size:1.1rem;">facility<span style="color:#CC0000;">X</span>perience</span></div><p style="color:#888;font-size:0.8rem;">Churchgate Group</p></div>""", unsafe_allow_html=True)
        st.subheader("🔐 Reset Your Password")
        st.caption(f"Resetting password for: {user.get('email','')}")
        
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm Password", type="password")
        
        if st.button("✅ Reset Password", use_container_width=True, type="primary"):
            if new_pw and new_pw == confirm_pw:
                if len(new_pw) >= 8:
                    import hashlib
                    pw_hash = hashlib.sha256(new_pw.encode()).hexdigest()
                    DB.update("app_users", user["id"], {
                        "password_hash": pw_hash,
                        "reset_token": None,
                        "reset_token_expiry": None
                    })
                    st.success("✅ Password reset successfully!")
                    st.info("Redirecting to login...")
                    st.query_params.clear()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Password must be at least 8 characters")
            else:
                st.error("Passwords don't match")
        
        if st.button("🔙 Back to Login", use_container_width=True):
            st.query_params.clear()
            st.rerun()

def main():
    inject_css()
    
    
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "show_forgot" not in st.session_state:
        st.session_state.show_forgot = False
    
    # Check URL params for auto-login (persists across refreshes)
    params = st.query_params
    if params.get("auth") == "true" and not st.session_state.authenticated:
        # Restore session from query param
        st.session_state.authenticated = True
        # Try to restore user from stored key
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
            # Check for reset token in URL
            params = st.query_params
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
    
    # Watermark
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
    
    
    # Greeting
    user = st.session_state.get("user", {})
    user_name = user.get("name", "User")
    designation = user.get("designation", "")
    emp_id = user.get("employee_id", "")
    from datetime import timezone, timedelta
    wat = datetime.now(timezone(timedelta(hours=1)))
    hour = wat.hour
    greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"
    
    st.markdown(f"""<div style="background:white;padding:0.8rem 1.5rem;border-radius:8px;margin:0.5rem 1rem 1.5rem 1rem;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 3px rgba(0,0,0,0.06);"><div style="display:flex;align-items:center;gap:1rem;"><div style="width:42px;height:42px;border-radius:50%;background:{CHURCHGATE_RED};display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:1rem;">{user_name[:2].upper()}</div><div><div style="font-weight:700;font-size:1rem;color:#1a1a1a;">👋 {greeting}, {user_name}!</div><div style="font-size:0.75rem;color:#666;">{designation} • ID: {emp_id}</div></div></div><div style="font-size:0.7rem;color:#888;text-align:right;"><div>{wat.strftime('%A, %d %B %Y')}</div><div>{wat.strftime('%I:%M %p')} WAT</div></div></div>""", unsafe_allow_html=True)
    
    user_perms = st.session_state.get("user", {}).get("extra_permissions", [])
    if isinstance(user_perms, str):
        try: user_perms = eval(user_perms)
        except: user_perms = []
    user_role = st.session_state.get("user_role", "staff")
    is_admin = user_role in ["admin", "approver"]
    
    page = st.session_state.page
    page_perms = {
        "cc": "Command Center", "ppm": "PPM Dashboard",
        "ar": "Asset Register", "cal": "52-Week Calendar", "cs": "Checklist Status",
       "wo": "Work Orders", "wp": "Raise Permit",
        "fo": "Facility Operations", "oa": "Facility Operations",
        "vm": "Visitor Management", "up": "User Management",
        "rt": "Raise Ticket", "hd": "Helpdesk", "fb": "Feedback",
        "ac": "Audit Checklist", "ic": "Incident Report", "hot": "HOTO Check",
        "uc": "Utility Dashboard", "mis": "Monthly MIS",
    }
    
    sidebar()
    ROUTER.get(page, page_cc)()

if __name__ == "__main__":
    main()