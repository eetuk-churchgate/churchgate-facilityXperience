"""
🏢 facilityXperience v3.0 — Enterprise Intelligent Facility Ecosystem
Churchgate Group | World-Class Facility Management Platform
SmartCheck Killer — AI-Powered Enterprise Grade
"""

import streamlit as st
from datetime import datetime, date, time, timedelta
import pandas as pd
import time
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
        section[data-testid="stSidebar"] {{ background: {CHURCHGATE_SIDEBAR} !important; border-right:1px solid #c0c0c0 !important; }}
        section[data-testid="stSidebar"] * {{ color: {CHURCHGATE_DARK} !important; }}
        section[data-testid="stSidebar"] .stButton > button {{ background:#c0c0c0 !important; border:1px solid #a0a0a0 !important; border-radius:6px !important; font-size:0.7rem !important; padding:0.35rem 0.5rem !important; }}
        section[data-testid="stSidebar"] button[kind="primary"] {{ background:{CHURCHGATE_RED} !important; color:white !important; }}
        [data-testid="collapsedControl"] {{ position:fixed !important; top:70px !important; left:0 !important; z-index:99999 !important; background:{CHURCHGATE_RED} !important; border-radius:0 6px 6px 0 !important; width:24px !important; height:40px !important; }}
        [data-testid="collapsedControl"] svg {{ fill:white !important; }}
        .fx-topnav {{ background:linear-gradient(105deg,{CHURCHGATE_DARK},#2a2a2a,{CHURCHGATE_DARK}); padding:0.5rem 1.5rem; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:9998; border-bottom:2px solid {CHURCHGATE_RED}; }}
        .fx-brand {{ font-size:1.05rem; font-weight:700; color:white; }} .fx-brand span {{ color:{CHURCHGATE_RED}; font-weight:800; }}
        .churchgate-header {{ background:white; padding:1.5rem; border-radius:8px; margin-bottom:1rem; border-left:4px solid {CHURCHGATE_RED}; box-shadow:0 1px 3px rgba(0,0,0,0.06); }}
        .fx-card {{ background:white; border-radius:8px; padding:1rem; border:1px solid #ccc; box-shadow:0 1px 3px rgba(0,0,0,0.06); text-align:center; }}
        .fx-card-label {{ font-size:0.6rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; color:{CHURCHGATE_GREY}; margin-bottom:0.3rem; }}
        .fx-card-value {{ font-size:1.6rem; font-weight:800; color:{CHURCHGATE_DARK}; line-height:1; }}
        .stButton > button {{ background:{CHURCHGATE_RED} !important; color:white !important; border:none !important; border-radius:6px !important; font-weight:600 !important; }}
        .stButton > button:hover {{ background:#aa0000 !important; }}
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
    """Smart assistant - Knowledge Base powered with AI enhancement"""
    # PRIMARY: Knowledge base search
    kb = supabase.table("knowledge_base").select("*").or_(f"question.ilike.%{query}%,tags.ilike.%{query}%").limit(5).execute()
    
    if kb.data:
        solutions = []
        for k in kb.data:
            solutions.append(f"**{k.get('question','')}**\n{k.get('answer','')}\n_Department: {k.get('department','')} | Priority: {k.get('priority','')}_")
        return "\n\n---\n\n".join(solutions)
    
    # SECONDARY: Try Hugging Face
    try:
        import requests
        api_key = st.secrets.get("HF_API_KEY", "")
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-base",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "inputs": f"Answer as a facility manager: {query}",
                "options": {"wait_for_model": True}
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "").strip()
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
                with st.expander(f"{w.get('permit_number','')} — {w.get('title','')} — {s.upper()}"):
                    st.write(f"**Raised by:** {w.get('raised_by_name','')} | **Type:** {w.get('permit_type','')}")
                    if w.get("review_l1_name"):st.write(f"✅ L1: {w['review_l1_name']} at {w.get('review_l1_at','')}")
                    if w.get("review_l2_name"):st.write(f"✅ L2: {w['review_l2_name']} at {w.get('review_l2_at','')}")
                    if w.get("approved_by_name"):st.write(f"✅ Approved: {w['approved_by_name']} at {w.get('approved_at','')}")
        else:st.info("No work permits")
    with c2:
        st.markdown("### 🎫 Recent Tickets")
        tix=DB.get_all("tickets",fc,5)
        if tix:st.dataframe(pd.DataFrame(tix)[[c for c in ["ticket_number","title","status","requester_name"] if c in pd.DataFrame(tix).columns]],use_container_width=True,hide_index=True)
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
                
                with st.expander(f"{icon} {permit_no} — {title} | {stage.upper()}", expanded=(stage == "submitted")):
                    c1, c2 = st.columns([3, 1])
                    
                    with c1:
                        st.markdown(f"**👤 Raised by:** {row.get('raised_by_name', 'N/A')} ({row.get('raised_by_designation', '')})")
                        st.markdown(f"**📅 Period:** {format_wat_time(row.get('start_datetime', ''))} → {format_wat_time(row.get('end_datetime', ''))}")
                        st.markdown(f"**📍 Location:** {row.get('work_location', '')}")
                        st.markdown(f"**📝 Description:** {row.get('description', '')[:200]}")
                        st.markdown(f"**🏢 Department:** {row.get('department', '')}")
                        
                        st.markdown("---")
                        st.markdown("**🔄 Audit Trail:**")
                        st.caption(f"📤 Submitted: {format_wat_time(row.get('submitted_at', row.get('created_at', '')))} by {row.get('raised_by_name', 'N/A')}")
                        if row.get("authorized_at"):
                            st.caption(f"🔐 Authorized: {format_wat_time(row['authorized_at'])} by {row.get('authorized_by_name', '')}")
                        if row.get("confirmed_at"):
                            st.caption(f"✅ Confirmed: {format_wat_time(row['confirmed_at'])} by {row.get('confirmed_by_name', '')}")
                        if row.get("approved_at"):
                            st.caption(f"🟢 Approved: {format_wat_time(row['approved_at'])} by {row.get('approved_by_name', '')}")
                        if stage == "rejected" and row.get("rejected_reason"):
                            st.error(f"❌ Rejected: {row.get('rejected_reason', '')}")
                            st.info("📝 Requester can resubmit with corrections")
                    
                    with c2:
                        st.markdown("**⚡ Actions:**")
                        now = datetime.now().isoformat()
                        dept = row.get("department", "")
                        
                        if can_authorize and stage == "submitted":
                            auth_comment = st.text_area("Authorization Comment", key=f"auth_cmt_{row['id']}", height=60, placeholder="Enter reason for authorization...")
                            if st.button("🔐 Authorize", key=f"auth_btn_{row['id']}", use_container_width=True, type="primary"):
                                if auth_comment:
                                    auth_name = st.session_state.get("user_name", "Authorizer")
                                    DB.update("work_permits", row["id"], {"workflow_stage": "authorized", "authorized_by_name": auth_name, "authorized_at": now})
                                    confirmers = get_workflow_people(fc, 2)
                                    for c in confirmers:
                                        send_email_notification(c.get("person_email", ""), f"🔐 Permit {permit_no} Requires Confirmation", f"<h3>Permit Authorized</h3><p><b>{permit_no}</b> authorized by {auth_name}.</p><p><b>Comment:</b> {auth_comment}</p>")
                                    st.success(f"🔐 Authorized!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Please add a comment before authorizing")
                        
                        if can_confirm and stage == "authorized":
                            conf_comment = st.text_area("Confirmation Comment", key=f"conf_cmt_{row['id']}", height=60, placeholder="Enter confirmation notes...")
                            if st.button("✅ Confirm", key=f"conf_btn_{row['id']}", use_container_width=True, type="primary"):
                                if conf_comment:
                                    conf_name = st.session_state.get("user_name", "Confirmer")
                                    DB.update("work_permits", row["id"], {"workflow_stage": "confirmed", "confirmed_by_name": conf_name, "confirmed_at": now})
                                    approvers = get_workflow_people(fc, 3)
                                    for a in approvers:
                                        send_email_notification(a.get("person_email", ""), f"✅ Permit {permit_no} Requires Approval", f"<h3>Permit Confirmed</h3><p><b>{permit_no}</b> confirmed by {conf_name}.</p><p><b>Comment:</b> {conf_comment}</p>")
                                    st.success(f"✅ Confirmed!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Please add a comment before confirming")
                        
                        if can_approve and stage in ["authorized", "confirmed"]:
                            app_comment = st.text_area("Approval Comment", key=f"app_cmt_{row['id']}", height=60, placeholder="Enter approval notes...")
                            if st.button("🟢 Approve", key=f"app_btn_{row['id']}", use_container_width=True, type="primary"):
                                if app_comment:
                                    app_name = st.session_state.get("user_name", "Approver")
                                    DB.update("work_permits", row["id"], {"workflow_stage": "approved", "status": "approved", "approved_by_name": app_name, "approved_at": now})
                                    send_email_notification(row.get("requester_contact", ""), f"🟢 Permit {permit_no} APPROVED", f"<h3>Permit Approved!</h3><p>Your permit <b>{permit_no}</b> has been <b>APPROVED</b> by {app_name}.</p><p><b>Comment:</b> {app_comment}</p>")
                                    st.success(f"🟢 Approved!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Please add a comment before approving")

                        
                        if stage not in ["rejected", "approved"] and (is_admin or can_authorize or can_confirm or can_approve):
                            rej_comment = st.text_area("Rejection Reason", key=f"rej_cmt_{row['id']}", height=60, placeholder="Enter reason for rejection...")
                            if st.button("❌ Reject", key=f"rej_btn_{row['id']}", use_container_width=True):
                                if rej_comment:
                                    rej_name = st.session_state.get("user_name", "Reviewer")
                                    DB.update("work_permits", row["id"], {
                                        "workflow_stage": "rejected", 
                                        "status": "rejected", 
                                        "rejected_at": now, 
                                        "rejected_by": rej_name,
                                        "rejected_reason": rej_comment
                                    })
                                    st.error(f"❌ Permit Rejected! Email sent to requester.")
                                    st.rerun()
                                else:
                                    st.error("Please provide a reason for rejection")
                        
                        if stage == "rejected" and (is_admin or can_raise):
                            if st.button("🔄 Resubmit Permit", key=f"resubmit_{row['id']}", use_container_width=True, type="primary"):
                                DB.update("work_permits", row["id"], {
                                    "workflow_stage": "submitted",
                                    "status": "pending",
                                    "submitted_at": now,
                                    "authorized_at": None,
                                    "authorized_by_name": None,
                                    "confirmed_at": None,
                                    "confirmed_by_name": None,
                                    "approved_at": None,
                                    "approved_by_name": None,
                                    "rejected_at": None,
                                    "rejected_reason": None
                                })
                                st.success("🔄 Permit resubmitted for approval!")
                                st.balloons()
                                st.rerun()
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
                        
                        class WorkPermitPDF(FPDF):
                            def header(self):
                                logo_path = Path("churchgate-logo.png")
                                if logo_path.exists():
                                    self.image(str(logo_path), x=14, y=8, h=12)
                                self.set_text_color(255, 255, 255)
                                self.set_fill_color(26, 26, 26)
                                self.rect(10, 22, 277, 14, 'F')
                                self.set_fill_color(204, 0, 0)
                                self.rect(10, 22, 4, 14, 'F')
                                self.set_font('Helvetica', 'B', 12)
                                self.set_xy(18, 24)
                                self.cell(260, 5, 'Work Permit Analytics Report', 0, 0, 'L')
                                self.set_font('Helvetica', '', 8)
                                self.set_xy(18, 29)
                                self.cell(260, 5, f'{info.get("full_name", fc)} | {datetime.now().strftime("%d %B %Y, %I:%M %p WAT")}', 0, 0, 'L')
                                self.set_y(40)
                            
                            def footer(self):
                                self.set_y(-18)
                                self.set_font('Helvetica', 'I', 7)
                                self.set_text_color(150, 150, 150)
                                self.cell(0, 8, f'Page {self.page_no()}/{{nb}} | Churchgate Group | Confidential', 0, 0, 'C')
                        
                        pdf = WorkPermitPDF('L', 'mm', 'A4')
                        pdf.alias_nb_pages()
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=22)
                        
                        # KPIs
                        pdf.set_font('Helvetica', 'B', 11)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 7, 'Key Performance Indicators', 0, 1)
                        pdf.ln(2)
                        
                        kpis = [
                            ("Total", str(total), 204, 0, 0),
                            ("Approved", str(approved_count), 16, 185, 129),
                            ("Pending", str(pending_count), 245, 158, 11),
                            ("Rejected", str(rejected_count), 100, 100, 100),
                            ("Avg Lead Time", f"{avg_lead:.1f} hrs", 37, 99, 235),
                        ]
                        xs = pdf.get_x()
                        ys = pdf.get_y()
                        for i, (label, value, r, g, b) in enumerate(kpis):
                            x = xs + (i * 55)
                            pdf.set_fill_color(245, 245, 245)
                            pdf.set_draw_color(r, g, b)
                            pdf.rect(x, ys, 50, 18, 'DF')
                            pdf.set_fill_color(r, g, b)
                            pdf.rect(x, ys, 3, 18, 'F')
                            pdf.set_xy(x + 5, ys + 2)
                            pdf.set_font('Helvetica', '', 6)
                            pdf.set_text_color(100, 100, 100)
                            pdf.cell(42, 4, label.upper(), 0, 0, 'C')
                            pdf.set_xy(x + 5, ys + 8)
                            pdf.set_font('Helvetica', 'B', 13)
                            pdf.set_text_color(r, g, b)
                            pdf.cell(42, 7, value, 0, 0, 'C')
                        pdf.set_y(ys + 24)
                        pdf.ln(4)
                        
                        if delayed > 0:
                            pdf.set_fill_color(255, 243, 205)
                            pdf.set_font('Helvetica', 'B', 8)
                            pdf.set_text_color(146, 76, 14)
                            pdf.cell(0, 7, f'  WARNING: {delayed} permit(s) exceeded 4-hour target', 1, 1, 'L', True)
                            pdf.ln(3)
                        
                        # Department Table
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 7, 'Department Breakdown', 0, 1)
                        pdf.set_font('Helvetica', 'B', 7)
                        pdf.set_fill_color(204, 0, 0)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(170, 5.5, '  Department', 1, 0, 'L', True)
                        pdf.cell(30, 5.5, 'Permits', 1, 0, 'C', True)
                        pdf.ln()
                        pdf.set_font('Helvetica', '', 7)
                        pdf.set_text_color(26, 26, 26)
                        for dept, count in list(dept_data.items())[:15]:
                            sd = dept.replace('\u2014','-').replace('\u2019',"'")[:65]
                            pdf.cell(170, 5, f'  {sd}', 1, 0, 'L')
                            pdf.cell(30, 5, str(count), 1, 0, 'C')
                            pdf.ln()
                        pdf.ln(3)
                        
                        # Stage Distribution
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 7, 'Workflow Stage Distribution', 0, 1)
                        pdf.set_font('Helvetica', 'B', 7)
                        pdf.set_fill_color(204, 0, 0)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(100, 5.5, '  Stage', 1, 0, 'L', True)
                        pdf.cell(30, 5.5, 'Count', 1, 0, 'C', True)
                        pdf.ln()
                        pdf.set_font('Helvetica', '', 7)
                        pdf.set_text_color(26, 26, 26)
                        for stage, count in stage_data.items():
                            pdf.cell(100, 5, f'  {stage.upper()}', 1, 0, 'L')
                            pdf.cell(30, 5, str(count), 1, 0, 'C')
                            pdf.ln()
                        pdf.ln(3)
                        
                        # Audit Trail
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 7, 'Complete Audit Trail', 0, 1)
                        pdf.set_font('Helvetica', 'B', 6)
                        pdf.set_fill_color(204, 0, 0)
                        pdf.set_text_color(255, 255, 255)
                        cw = [35, 28, 42, 36, 36, 36, 36, 22]
                        for h, w in zip(['Permit No','Raised By','Department','Submitted','Authorized','Confirmed','Approved','Status'], cw):
                            pdf.cell(w, 5.5, f' {h}', 1, 0, 'L', True)
                        pdf.ln()
                        pdf.set_font('Helvetica', '', 5.5)
                        for _, row in df.iterrows():
                            stg = row.get('workflow_stage','')
                            if stg == 'approved': pdf.set_text_color(6,95,70)
                            elif stg == 'rejected': pdf.set_text_color(153,27,27)
                            else: pdf.set_text_color(26,26,26)
                            vals = [
                                str(row.get('permit_number',''))[:16],
                                str(row.get('raised_by_name',''))[:13],
                                str(row.get('department','')).replace('\u2014','-')[:20],
                                str(format_wat_time(row.get('submitted_at','')))[:16],
                                str(format_wat_time(row.get('authorized_at','')))[:16],
                                str(format_wat_time(row.get('confirmed_at','')))[:16],
                                str(format_wat_time(row.get('approved_at','')))[:16],
                                stg.upper()[:7],
                            ]
                            for v, w in zip(vals, cw):
                                pdf.cell(w, 4.5, f' {v}', 1, 0, 'L')
                            pdf.ln()
                        
                        pdf_file = f"/tmp/wp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        pdf.output(pdf_file)
                        with open(pdf_file, "rb") as f:
                            pdf_bytes = f.read()
                        st.success("✅ PDF Generated!")
                        st.download_button("📥 Download PDF", pdf_bytes, f"Work_Permit_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", "application/pdf", use_container_width=True, type="primary")
                    except Exception as e:
                        st.error(f"PDF Error: {e}")
            
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
    
    # AI SMART SEARCH
    st.markdown("### 🤖 facilityXpert — Smart Issue Resolution")
    st.caption("Describe your issue and let AI suggest solutions before raising a ticket")
    
    c1, c2 = st.columns([4, 1])
    with c1:
        ai_query = st.text_input("What's the issue?", placeholder="e.g. My AC is blowing hot air, internet is slow, water leaking...", key="ai_search", label_visibility="collapsed")
    with c2:
        ask_ai = st.button("🤖 Ask AI", use_container_width=True, type="primary")
    
    if ask_ai and ai_query:
        with st.spinner("🤖 facilityXpert is thinking..."):
            kb = supabase.table("knowledge_base").select("*").or_(f"question.ilike.%{ai_query}%,tags.ilike.%{ai_query}%").limit(5).execute()
            hc = DB.get_helpdesk_categories()
            cat_names_list = sorted(list(set(c.get("category_name", "") for c in hc)))
            ai_response = ask_facility_xpert(ai_query, cat_names_list)
            st.write(f"Debug: {ai_response}")
        
        if ai_response:
            st.markdown("### 🤖 facilityXpert AI Says:")
            st.info(ai_response)
        
        if kb.data:
            st.success(f"💡 Also found {len(kb.data)} matching solutions in our knowledge base:")
            for k in kb.data:
                with st.expander(f"🔧 {k.get('question','')} — {k.get('category','')}"):
                    st.markdown(f"**Solution:** {k.get('answer','')}")
                    st.caption(f"Priority: {k.get('priority','')} | Department: {k.get('department','')}")
                    if st.button(f"✅ This solved my issue", key=f"solved_{k['id']}"):
                        st.success("Great! Issue resolved without a ticket. 🎉")
                        st.balloons()
        
        if not ai_response and not kb.data:
            st.warning("No solutions found. Please raise a ticket below.")
    
    elif ask_ai and not ai_query:
        st.warning("Please describe your issue first")
    
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
    
    with st.form("raise_ticket_form"):
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
                st.info(f"📧 Notification sent to {len(authorizers)} team member(s)")
                st.balloons()
                st.rerun()
    
    # MY TICKETS WITH RATINGS
    st.markdown("---")
    st.markdown("### 📋 My Tickets")
    
    my_tickets = supabase.table("tickets").select("*").eq("facility_code", fc).ilike("requester_name", f"%{st.session_state.get('user_name', '')}%").order("created_at", desc=True).limit(20).execute()
    if my_tickets.data:
        for t in my_tickets.data:
            status = t.get("status", "open")
            badges = {"open": "🔴", "in_progress": "🟡", "hold": "⏸️", "closed": "🟢", "rejected": "❌"}
            with st.expander(f"{badges.get(status,'📋')} {t.get('ticket_number','')} — {t.get('title','')[:60]} — {status.upper()}"):
                st.write(f"**Category:** {t.get('category','')} | **Priority:** {t.get('priority','')}")
                st.write(f"**Location:** {t.get('location_building','')}")
                st.write(f"**Description:** {t.get('description','')}")
                
                if t.get("status") == "closed":
                    st.success("✅ Resolved")
                    # Star rating
                    if not t.get("satisfaction_rating"):
                        rating = st.slider("Rate your experience", 1, 5, 5, key=f"rate_{t['id']}")
                        feedback = st.text_area("Additional feedback (optional)", key=f"fb_{t['id']}")
                        if st.button("⭐ Submit Rating", key=f"submit_rate_{t['id']}"):
                            DB.update("tickets", t["id"], {"satisfaction_rating": rating, "satisfaction_feedback": feedback})
                            st.success("Thank you for your feedback!")
                            st.rerun()
                    else:
                        st.markdown(f"**Your Rating:** {'⭐' * t.get('satisfaction_rating', 0)}")
                elif t.get("status") == "in_progress":
                    st.info("🟡 Team is working on this")
                elif t.get("status") == "open":
                    st.warning("🔴 Awaiting assignment")
    else:
        st.info("No tickets raised yet")


# ============================================
# HELPDESK QUEUE + ANALYTICS
# ============================================
def page_helpdesk_queue():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    user_role = st.session_state.get("user_role", "staff")
    is_admin = user_role in ["admin", "approver"]
    
    st.markdown(f'## 💬 Helpdesk Queue — {info.get("full_name", fc)}')
    
    categories = DB.get_helpdesk_categories()
    
    # TABS: Queue + Analytics
    tabs = st.tabs(["📋 Ticket Queue", "📊 Analytics & Reports"])
    
    # ============================================
    # TAB 1: TICKET QUEUE
    # ============================================
    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        with c1:
            status_filter = st.selectbox("Status", ["All", "open", "in_progress", "hold", "closed", "rejected"], key="hd_status")
        with c2:
            cat_names = ["All"] + sorted(list(set(c.get("category_name", "") for c in categories)))
            cat_filter = st.selectbox("Category", cat_names, key="hd_cat")
        with c3:
            search = st.text_input("🔍 Search", placeholder="Search tickets...", key="hd_search")
        
        tickets = DB.get_tickets_filtered(
            fc, 
            status=status_filter if status_filter != "All" else None,
            category=cat_filter if cat_filter != "All" else None,
            search=search if search else None
        )
        
        # Department filter
        user_depts = st.session_state.get("user", {}).get("department_permissions", [])
        if isinstance(user_depts, str):
            try: user_depts = eval(user_depts)
            except: user_depts = []
        can_see_all = user_role in ["admin", "approver", "confirmer"]
        
        if tickets and not can_see_all and user_depts:
            filtered = []
            for t in tickets:
                ticket_cat = t.get("category", "")
                for c in categories:
                    if c.get("category_name") == ticket_cat and c.get("department") in user_depts:
                        filtered.append(t)
                        break
            tickets = filtered
        
        if tickets:
            df = pd.DataFrame(tickets)
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.metric("🔴 Open", len(df[df["status"] == "open"]) if "status" in df.columns else 0)
            with c2: st.metric("🟡 In Progress", len(df[df["status"] == "in_progress"]) if "status" in df.columns else 0)
            with c3: st.metric("⏸️ Hold", len(df[df["status"] == "hold"]) if "status" in df.columns else 0)
            with c4: st.metric("🟢 Closed", len(df[df["status"] == "closed"]) if "status" in df.columns else 0)
            with c5: st.metric("📋 Total", len(df))
            
            st.markdown("---")
            
            for i, row in df.iterrows():
                status = row.get("status", "open")
                badges = {"open": "🔴", "in_progress": "🟡", "hold": "⏸️", "closed": "🟢", "rejected": "❌"}
                badge = badges.get(status, "📋")
                
                created = row.get("created_at", "")
                age_str = ""
                if created:
                    try:
                        created_dt = pd.to_datetime(created)
                        age = datetime.now() - created_dt
                        age_str = f"{age.days}d {age.seconds//3600}h"
                    except: pass
                
                with st.expander(f"{badge} {row.get('ticket_number','')} — {row.get('title','')[:80]} | ⏱️ {age_str}"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**Raised by:** {row.get('requester_name','N/A')} | **Category:** {row.get('category','')}")
                        st.markdown(f"**Priority:** {row.get('priority','')} | **SLA:** {row.get('sla_deadline','')}")
                        st.markdown(f"**Location:** {row.get('location_building','')}")
                        st.markdown(f"**Description:** {row.get('description','')}")
                        
                        if row.get("satisfaction_rating"):
                            st.markdown(f"**Rating:** {'⭐' * row.get('satisfaction_rating', 0)}")
                        
                        comments = DB.get_ticket_comments(row["id"])
                        if comments:
                            st.markdown("**📝 Progress:**")
                            for c in comments:
                                st.caption(f"{c.get('user_name','')}: {c.get('comment_text','')}")
                    
                    with c2:
                        st.markdown("**⚡ Actions:**")
                        
                        if status in ["open", "in_progress", "hold"]:
                            new_comment = st.text_area("Note", key=f"cmt_{row['id']}", height=50)
                            
                            if st.button("🔄 Update", key=f"upd_{row['id']}", use_container_width=True):
                                if new_comment:
                                    DB.insert("ticket_comments", {"ticket_id": row["id"], "user_name": st.session_state.get("user_name", "Staff"), "comment_text": new_comment})
                                    DB.update("tickets", row["id"], {"status": "in_progress"})
                                    st.rerun()
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("⏸️ Hold", key=f"hold_{row['id']}", use_container_width=True):
                                    DB.update("tickets", row["id"], {"status": "hold"})
                                    st.rerun()
                            with c2:
                                if st.button("✅ Close", key=f"close_{row['id']}", use_container_width=True):
                                    DB.update("tickets", row["id"], {"status": "closed", "closed_at": datetime.now().isoformat()})
                                    # Email requester
                                    if row.get("requester_email"):
                                        send_email_notification(
                                            row["requester_email"],
                                            f"✅ Ticket {row.get('ticket_number','')} Resolved",
                                            f"<h3>Your Ticket Has Been Resolved</h3>"
                                            f"<p><b>Ticket:</b> {row.get('ticket_number','')}</p>"
                                            f"<p><b>Issue:</b> {row.get('title','')}</p>"
                                            f"<p>Your ticket has been marked as resolved. Please rate your experience.</p>"
                                        )
                                    st.success("Closed! Email sent to requester.")
                                    st.rerun()
                            
                            if is_admin:
                                esc_level = row.get("escalation_level", 1)
                                if esc_level < 6:
                                    if st.button(f"🔺 Escalate L{esc_level}→L{esc_level+1}", key=f"esc_{row['id']}", use_container_width=True):
                                        DB.update("tickets", row["id"], {"escalation_level": esc_level + 1})
                                        st.success(f"Escalated!")
                                        st.rerun()
                        
                        if status == "closed":
                            if st.button("🔄 Re-Open", key=f"reopen_{row['id']}", use_container_width=True):
                                DB.update("tickets", row["id"], {"status": "open"})
                                st.rerun()
        else:
            st.info("No tickets found")
    
    # ============================================
    # TAB 2: ANALYTICS & REPORTS
    # ============================================
    with tabs[1]:
        st.markdown("### 📊 Helpdesk Analytics")
        
        all_tickets = DB.get_all("tickets", fc, 500)
        if all_tickets:
            df = pd.DataFrame(all_tickets)
            
            # Summary KPIs
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Tickets", len(df))
            with c2: st.metric("Open", len(df[df["status"] == "open"]) if "status" in df.columns else 0)
            with c3: st.metric("Avg Resolution", f"{len(df[df['status']=='closed']) if 'status' in df.columns else 0}")
            with c4: st.metric("Satisfaction", f"{df['satisfaction_rating'].mean():.1f}⭐" if "satisfaction_rating" in df.columns and df["satisfaction_rating"].notna().any() else "N/A")
            
            st.markdown("---")
            
            # Category breakdown chart
            if "category" in df.columns:
                cat_counts = df["category"].value_counts().head(10)
                fig = px.bar(x=cat_counts.index, y=cat_counts.values, title="Tickets by Category", labels={"x": "Category", "y": "Count"}, color=cat_counts.values, color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            
            # Status pie chart
            if "status" in df.columns:
                status_counts = df["status"].value_counts()
                fig2 = px.pie(values=status_counts.values, names=status_counts.index, title="Tickets by Status", color_discrete_sequence=["#EF4444", "#F59E0B", "#3B82F6", "#10B981", "#6B7280"])
                st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # Export Report
            st.markdown("### 📄 Export Report")
            if st.button("📊 Generate Analytics Report", use_container_width=True, type="primary"):
                # Build HTML report
                total = len(df)
                open_count = len(df[df["status"] == "open"]) if "status" in df.columns else 0
                closed_count = len(df[df["status"] == "closed"]) if "status" in df.columns else 0
                avg_rating = df["satisfaction_rating"].mean() if "satisfaction_rating" in df.columns and df["satisfaction_rating"].notna().any() else 0
                
                html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;margin:20px;color:#1a1a1a}}h1{{color:#CC0000;border-bottom:3px solid #CC0000}}h2{{color:#333;margin-top:20px}}table{{width:100%;border-collapse:collapse;margin:15px 0;font-size:11px}}th{{background:#CC0000;color:white;padding:8px}}td{{padding:6px;border-bottom:1px solid #ddd}}.kpi{{display:inline-block;width:22%;background:#f5f5f5;border-radius:8px;padding:15px;margin:10px 1%;text-align:center}}.kpi-val{{font-size:28px;font-weight:bold;color:#CC0000}}.footer{{margin-top:30px;font-size:10px;color:#999;text-align:center}}</style></head><body><h1>facilityXperience — Helpdesk Analytics</h1><p>{info.get('full_name',fc)} | {datetime.now().strftime('%d %B %Y, %I:%M %p WAT')}</p><div class="kpi"><div class="kpi-val">{total}</div>Total Tickets</div><div class="kpi"><div class="kpi-val">{open_count}</div>Open</div><div class="kpi"><div class="kpi-val">{closed_count}</div>Closed</div><div class="kpi"><div class="kpi-val">{avg_rating:.1f}⭐</div>Avg Rating</div><h2>Recent Tickets</h2><table><tr><th>Ticket No</th><th>Title</th><th>Category</th><th>Status</th><th>Raised By</th><th>Date</th></tr>"""
                
                for _, row in df.head(20).iterrows():
                    html += f"<tr><td>{row.get('ticket_number','')}</td><td>{row.get('title','')[:60]}</td><td>{row.get('category','')}</td><td><b>{row.get('status','').upper()}</b></td><td>{row.get('requester_name','')}</td><td>{row.get('created_at','')[:10]}</td></tr>"
                
                html += "</table><div class='footer'>© Churchgate Group | facilityXperience AI-Powered Analytics</div></body></html>"
                
                st.components.v1.html(html, height=500, scrolling=True)
                st.download_button("📥 Download HTML Report", html, f"helpdesk_report_{datetime.now().strftime('%Y%m%d')}.html", "text/html", use_container_width=True)
        else:
            st.info("No ticket data available for analytics")
    
    # Settings (Admin)
    if is_admin:
        st.markdown("---")
        with st.expander("⚙️ Helpdesk Settings"):
            subtabs = st.tabs(["Categories", "Escalation"])
            with subtabs[0]:
                for c in categories:
                    st.markdown(f"- **{c.get('category_name','')}** — {c.get('department','')} ({c.get('sla_hours','4')}hrs)")
            with subtabs[1]:
                st.markdown("Escalation config available in Work Permit → Workflow Config")

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
# VISITOR MANAGEMENT
# ============================================
def page_vm():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🛂 Visitor Experience Portal — {info.get("full_name",fc)}')
    tab1,tab2,tab3=st.tabs(["📋 Today's Visitors","➕ Register Visitor","📊 Reports"])
    with tab1:
        vis=DB.get_all("visitors",fc,50)
        if vis:
            df=pd.DataFrame(vis)
            c1,c2=st.columns(2)
            with c1:st.metric("Expected Today",len(df))
            with c2:st.metric("Checked In",len(df[df["status"]=="checked_in"]) if "status" in df.columns else 0)
            for i,row in df.iterrows():
                s=row.get("status","expected")
                badge="badge-success" if s=="checked_in" else "badge-warning" if s in ["expected","pre_registered"] else "badge-info"
                with st.expander(f"{row.get('full_name','')} — {row.get('company','')} — {s.upper()}"):
                    st.write(f"**Host:** {row.get('host_name','')} | **Purpose:** {row.get('purpose_of_visit','')}")
                    st.write(f"**Arrival:** {row.get('expected_arrival','')} | **Departure:** {row.get('expected_departure','')}")
                    if s in ["expected","pre_registered"]:
                        if st.button("✅ Check In",key=f"vin_{row['id']}"):DB.update("visitors",row["id"],{"status":"checked_in","actual_arrival":datetime.now().isoformat()});st.rerun()
                    if s=="checked_in":
                        if st.button("🚪 Check Out",key=f"vout_{row['id']}"):DB.update("visitors",row["id"],{"status":"checked_out","actual_departure":datetime.now().isoformat()});st.rerun()
        else:st.info("No visitors today")
    with tab2:
        with st.form("vis_form"):
            st.markdown("### Register Visitor")
            vtype=st.radio("Type",["Visitor","Vendor","Interview"],horizontal=True)
            c1,c2=st.columns(2)
            with c1:
                fn=st.text_input("First Name*");ln=st.text_input("Last Name*")
                mobile=st.text_input("Mobile Number*");email=st.text_input("Email")
                company=st.text_input("Company Name");coming_from=st.text_input("Coming From")
            with c2:
                host=st.text_input("Whom to Meet*");purpose=st.text_input("Purpose of Visit")
                vdate=st.date_input("Visiting Date*",date.today());vtime=st.time_input("Visiting Time",time(9,0))
                vehicle=st.text_input("Vehicle Details");belongings=st.text_area("Belongings/Tools/Remarks")
            if st.form_submit_button("🛂 Register",use_container_width=True):
                if fn and ln and mobile and host:
                    DB.insert("visitors",{"facility_code":fc,"visitor_type":vtype.lower(),"first_name":fn,"last_name":ln,"mobile":mobile,"email":email,"company":company,"coming_from":coming_from,"host_name":host,"purpose_of_visit":purpose,"visit_date":str(vdate),"expected_arrival":str(vtime),"vehicle_details":vehicle,"belongings":belongings,"status":"pre_registered","category":vtype.lower(),"created_at":datetime.now().isoformat()})
                    st.success("Registered!");st.rerun()
    with tab3:
        st.markdown("### Visitor Reports")
        yr=st.selectbox("Year",[2024,2025,2026,2027])
        mn=st.selectbox("Month",["January","February","March","April","May","June","July","August","September","October","November","December"])
        st.info(f"📊 Report for {mn} {yr} — Pulling live data from database")
        vis_all=DB.get_all("visitors",fc,200)
        if vis_all:st.dataframe(pd.DataFrame(vis_all)[[c for c in ["full_name","company","host_name","purpose_of_visit","status","actual_arrival","actual_departure"] if c in pd.DataFrame(vis_all).columns]],use_container_width=True,hide_index=True)

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
# FEEDBACK
# ============================================
def page_fb():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ⭐ Voice of Customer — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 Feedback","✍️ Submit"])
    with tab1:
        fb=DB.get_all("feedback",fc,20)
        if fb:
            for f in fb:st.write(f"**{'⭐'*f.get('rating',0)}** — {f.get('title','')} — {f.get('comments','')}")
        else:st.info("No feedback yet")
    with tab2:
        with st.form("fb_f"):
            rating=st.slider("Rating",1,5,5);title=st.text_input("Title")
            cat=st.selectbox("Category",["Facility","Service","Cleanliness","Security","Other"])
            comments=st.text_area("Comments*")
            if st.form_submit_button("⭐ Submit",use_container_width=True):
                if comments:
                    DB.insert("feedback",{"facility_code":fc,"rating":rating,"title":title,"category":cat,"comments":comments,"sentiment":"positive" if rating>=4 else "neutral","status":"new","created_at":datetime.now().isoformat()})
                    st.success("Thank you!");st.rerun()

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
    "vm":page_vm,"up":page_users,"rt":page_raise_ticket,"hd":page_helpdesk_queue,"fb":page_fb,
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