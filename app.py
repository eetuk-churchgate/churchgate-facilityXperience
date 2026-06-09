"""
🏢 facilityXperience — Enterprise Intelligent Facility Ecosystem
Churchgate Group | Multi-Facility AI-Powered Orchestration Platform
AI-Powered Enterprise Grade
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import base64
from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# ============================================
# SUPABASE CONNECTION
# ============================================
SUPABASE_URL = os.getenv("SUPABASE_URL", st.secrets.get("SUPABASE_URL", "https://qxqdrlvhztkkckbvgxng.supabase.co"))
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", st.secrets.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4cWRybHZoenRra2NrYnZneG5nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5OTUyODgsImV4cCI6MjA5NjU3MTI4OH0.Q62njynXLnsLCNvwnKM7DQDrS5-UO4chDRj3XApeke8"))

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ============================================
# CHURCHGATE BRAND COLORS
# ============================================
CHURCHGATE_RED = "#CC0000"
CHURCHGATE_DARK = "#1a1a1a"
CHURCHGATE_GREY = "#4a4a4a"
CHURCHGATE_LIGHT = "#f5f5f5"
CHURCHGATE_WHITE = "#ffffff"
CHURCHGATE_BG = "#e8e8e8"
CHURCHGATE_SIDEBAR = "#d5d5d5"

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="facilityXperience | Churchgate Group",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# FACILITY CONFIG
# ============================================
FACILITY_INFO = {
    "WTC": {
        "full_name": "World Trade Center",
        "city": "Abuja",
        "logo_file": "wtc-logo.jpg",
        "description": "22-Floor Office Tower • 24-Floor Residential Tower • Recreation Center",
        "color": CHURCHGATE_RED,
        "color_light": "#fce8e8",
    },
    "AGVL": {
        "full_name": "Agroline Ventures Limited",
        "city": "Abuja",
        "logo_file": "churchgate-logo.png",
        "description": "Commercial/Retail Complex",
        "color": "#059669",
        "color_light": "#ECFDF5",
    },
    "FCPL": {
        "full_name": "First Continental Properties Limited",
        "city": "Lagos",
        "logo_file": "churchgate-logo.png",
        "description": "Commercial/Industrial Tower",
        "color": "#D97706",
        "color_light": "#FFFBEB",
    },
    "RBPL": {
        "full_name": "RB Properties Limited",
        "city": "Lagos",
        "logo_file": "churchgate-logo.png",
        "description": "Premium Commercial Plaza",
        "color": "#BE185D",
        "color_light": "#FDF2F8",
    },
    "VDL": {
        "full_name": "Ocean Terrace",
        "city": "Lagos",
        "logo_file": "churchgate-logo.png",
        "description": "Commercial/Industrial Centre",
        "color": "#7C3AED",
        "color_light": "#F5F3FF",
    },
    "WAREHOUSES": {
        "full_name": "Warehouse Network",
        "city": "Lagos",
        "logo_file": "churchgate-logo.png",
        "description": "Logistics & Storage Network",
        "color": "#475569",
        "color_light": "#F1F5F9",
    },
}

# ============================================
# CUSTOM CSS — CHURCHGATE BRANDED
# ============================================
def inject_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        * {{ font-family: 'Inter', sans-serif; }}
        
        /* GLOBAL BACKGROUNDS */
        .stApp {{ background: {CHURCHGATE_BG}; }}
        .main > div {{ background: {CHURCHGATE_BG}; }}
        
        /* HIDE STREAMLIT DEFAULTS */
        #MainMenu {{ visibility: hidden; }}
        header {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        
        /* SIDEBAR — CHURCHGATE STYLE */
        section[data-testid="stSidebar"] {{ 
            background-color: {CHURCHGATE_SIDEBAR} !important; 
            border-right: 1px solid #c0c0c0 !important;
        }}
        section[data-testid="stSidebar"] * {{ color: {CHURCHGATE_DARK} !important; }}
        section[data-testid="stSidebar"] .stButton > button {{ 
            background-color: #c0c0c0 !important; 
            border: 1px solid #a0a0a0 !important; 
            color: {CHURCHGATE_DARK} !important;
            border-radius: 6px !important;
            font-size: 0.75rem !important;
            padding: 0.4rem 0.6rem !important;
            transition: all 0.2s !important;
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: #b0b0b0 !important;
            border-color: {CHURCHGATE_RED} !important;
        }}
        section[data-testid="stSidebar"] button[kind="primary"] {{
            background: {CHURCHGATE_RED} !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
        }}
        
        /* FIX SIDEBAR TOGGLE FOR ALL BROWSERS */
        [data-testid="collapsedControl"] {{
            position: fixed !important;
            top: 70px !important;
            left: 0 !important;
            z-index: 99999 !important;
            background: {CHURCHGATE_RED} !important;
            border-radius: 0 6px 6px 0 !important;
            padding: 6px 4px !important;
            box-shadow: 0 2px 10px rgba(204,0,0,0.4) !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 24px !important;
            height: 40px !important;
        }}
        [data-testid="collapsedControl"] svg {{
            fill: white !important;
            width: 14px !important;
            height: 14px !important;
        }}
        [data-testid="collapsedControl"]:hover {{
            background: #aa0000 !important;
            box-shadow: 0 4px 20px rgba(204,0,0,0.6) !important;
        }}
        
        /* TOP NAV */
        .fx-topnav {{
            background: linear-gradient(105deg, {CHURCHGATE_DARK} 0%, #2a2a2a 50%, {CHURCHGATE_DARK} 100%);
            padding: 0.5rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 9998;
            border-bottom: 2px solid {CHURCHGATE_RED};
            box-shadow: 0 2px 15px rgba(0,0,0,0.3);
        }}
        .fx-brand-name {{ font-size: 1.05rem; font-weight: 700; color: white; letter-spacing: -0.3px; }}
        .fx-brand-name span {{ color: {CHURCHGATE_RED}; font-weight: 800; }}
        .fx-brand-sep {{ width:1px; height:22px; background:linear-gradient(180deg,transparent,rgba(204,0,0,0.6),transparent); }}
        
        .fx-ai-indicator {{
            display: flex; align-items: center; gap: 0.3rem;
            background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3);
            border-radius: 50px; padding: 0.25rem 0.7rem;
            font-size: 0.6rem; font-weight: 600; color: #6EE7B7;
        }}
        .fx-ai-dot {{
            width: 5px; height: 5px; border-radius: 50%; background: #10B981;
            animation: fxPulse 2s infinite;
        }}
        @keyframes fxPulse {{
            0%,100% {{ opacity:1; }}
            50% {{ opacity:0.4; }}
        }}
        
        /* CARDS */
        .fx-card {{
            background: {CHURCHGATE_WHITE};
            border-radius: 8px; padding: 1rem;
            border: 1px solid #cccccc;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            transition: all 0.2s;
        }}
        .fx-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: {CHURCHGATE_RED};
            transform: translateY(-2px);
        }}
        .fx-card-label {{
            font-size: 0.6rem; font-weight: 600; text-transform: uppercase;
            letter-spacing: 1px; color: {CHURCHGATE_GREY}; margin-bottom: 0.3rem;
        }}
        .fx-card-value {{ font-size: 1.6rem; font-weight: 800; color: {CHURCHGATE_DARK}; line-height: 1; }}
        .fx-card-subtitle {{ font-size: 0.65rem; color: #888; margin-top: 0.2rem; }}
        
        /* HEADER */
        .churchgate-header {{
            background: {CHURCHGATE_WHITE};
            padding: 1.5rem 2rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border-left: 4px solid {CHURCHGATE_RED};
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }}
        
        /* BUTTONS */
        .stButton > button {{
            background: {CHURCHGATE_RED} !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
        }}
        .stButton > button:hover {{
            background: #aa0000 !important;
            box-shadow: 0 2px 8px rgba(204,0,0,0.3) !important;
        }}
        
        /* AI PANEL */
        .fx-ai-panel {{
            background: linear-gradient(135deg, {CHURCHGATE_DARK}, #2a2a2a);
            border-radius: 8px; padding: 1.5rem; color: white;
            border: 1px solid rgba(204,0,0,0.3);
        }}
        
        /* ACTIVITY FEED */
        .fx-timeline-item {{
            display: flex; gap: 0.5rem; padding: 0.45rem 0;
            border-bottom: 1px solid #e0e0e0; align-items: flex-start;
            font-size: 0.7rem;
        }}
        .fx-timeline-dot {{
            width: 6px; height: 6px; border-radius: 50%; margin-top: 4px; flex-shrink: 0;
        }}
        
        /* TABLES */
        [data-testid="stDataFrame"] {{
            border-radius: 8px !important;
            border: 1px solid #cccccc !important;
            overflow: hidden !important;
        }}
        [data-testid="stDataFrame"] th {{
            background: {CHURCHGATE_LIGHT} !important;
            font-weight: 600 !important; font-size: 0.65rem !important;
            text-transform: uppercase !important; letter-spacing: 0.5px !important;
            color: {CHURCHGATE_GREY} !important; padding: 0.5rem 0.7rem !important;
        }}
        [data-testid="stDataFrame"] td {{
            font-size: 0.7rem !important; padding: 0.4rem 0.7rem !important;
        }}
        
        /* ANIMATIONS */
        @keyframes fxSlideUp {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .fx-animate-up {{ animation: fxSlideUp 0.35s ease-out forwards; }}
        .fx-stagger-1 {{ animation-delay: 0.03s; opacity: 0; }}
        .fx-stagger-2 {{ animation-delay: 0.06s; opacity: 0; }}
        .fx-stagger-3 {{ animation-delay: 0.09s; opacity: 0; }}
        .fx-stagger-4 {{ animation-delay: 0.12s; opacity: 0; }}
        .fx-stagger-5 {{ animation-delay: 0.15s; opacity: 0; }}
        .fx-stagger-6 {{ animation-delay: 0.18s; opacity: 0; }}
        .fx-stagger-7 {{ animation-delay: 0.21s; opacity: 0; }}
        .fx-stagger-8 {{ animation-delay: 0.24s; opacity: 0; }}
        
        /* BADGES */
        .fx-badge {{
            display: inline-flex; align-items: center; gap: 0.2rem;
            padding: 0.15rem 0.5rem; border-radius: 50px;
            font-size: 0.6rem; font-weight: 600;
        }}
        .fx-badge-success {{ background: #ECFDF5; color: #065F46; }}
        .fx-badge-warning {{ background: #FFFBEB; color: #92400E; }}
        .fx-badge-critical {{ background: #FEF2F2; color: #991B1B; }}
        .fx-badge-info {{ background: #EFF6FF; color: #1E40AF; }}
        
        /* METRICS */
        [data-testid="stMetric"] {{
            background: {CHURCHGATE_WHITE};
            padding: 0.8rem !important;
            border-radius: 8px !important;
            border: 1px solid #cccccc !important;
        }}
        [data-testid="stMetric"] label {{ color: {CHURCHGATE_GREY} !important; }}
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {CHURCHGATE_DARK} !important; font-weight: 800 !important; }}
    </style>
    """, unsafe_allow_html=True)

# ============================================
# DATA ENGINE
# ============================================
class FacilityDataEngine:
    
    @staticmethod
    def get_facilities():
        try:
            res = supabase.table("facilities").select("*").order("name").execute()
            return res.data if res.data else []
        except:
            return []
    
    @staticmethod
    def get_kpis(facility_code):
        try:
            wo_open = supabase.table("work_orders").select("id", count="exact").eq("facility_code", facility_code).eq("status", "open").execute()
            wo_all = supabase.table("work_orders").select("id", count="exact").eq("facility_code", facility_code).execute()
            today = str(datetime.now().date())
            visitors = supabase.table("visitors").select("id", count="exact").eq("facility_code", facility_code).eq("visit_date", today).execute()
            incidents_open = supabase.table("incidents").select("id", count="exact").eq("facility_code", facility_code).eq("status", "reported").execute()
            incidents_all = supabase.table("incidents").select("id", count="exact").eq("facility_code", facility_code).execute()
            tickets_open = supabase.table("tickets").select("id", count="exact").eq("facility_code", facility_code).in_("status", ["open","in_progress"]).execute()
            tickets_all = supabase.table("tickets").select("id", count="exact").eq("facility_code", facility_code).execute()
            assets = supabase.table("assets").select("id", count="exact").eq("facility_code", facility_code).execute()
            
            return {
                "open_work_orders": wo_open.count or 0,
                "total_work_orders": wo_all.count or 0,
                "active_visitors": visitors.count or 0,
                "open_incidents": incidents_open.count or 0,
                "total_incidents": incidents_all.count or 0,
                "open_tickets": tickets_open.count or 0,
                "total_tickets": tickets_all.count or 0,
                "total_assets": assets.count or 0,
            }
        except:
            return {"open_work_orders":0,"total_work_orders":0,"active_visitors":0,"open_incidents":0,"total_incidents":0,"open_tickets":0,"total_tickets":0,"total_assets":0}
    
    @staticmethod
    def get_work_orders(facility_code, limit=10):
        try:
            res = supabase.table("work_orders").select("*").eq("facility_code", facility_code).order("created_at", desc=True).limit(limit).execute()
            return res.data if res.data else []
        except:
            return []
    
    @staticmethod
    def get_visitors_today(facility_code):
        try:
            res = supabase.table("visitors").select("*").eq("facility_code", facility_code).eq("visit_date", str(datetime.now().date())).order("expected_arrival").execute()
            return res.data if res.data else []
        except:
            return []
    
    @staticmethod
    def get_tickets(facility_code, limit=10):
        try:
            res = supabase.table("tickets").select("*").eq("facility_code", facility_code).order("created_at", desc=True).limit(limit).execute()
            return res.data if res.data else []
        except:
            return []
    
    @staticmethod
    def get_incidents(facility_code, limit=10):
        try:
            res = supabase.table("incidents").select("*").eq("facility_code", facility_code).order("created_at", desc=True).limit(limit).execute()
            return res.data if res.data else []
        except:
            return []
    
    @staticmethod
    def get_assets(facility_code, limit=20):
        try:
            res = supabase.table("assets").select("*, asset_categories(name, icon)").eq("facility_code", facility_code).limit(limit).execute()
            return res.data if res.data else []
        except:
            return []

# ============================================
# LOGO HELPER
# ============================================
def get_logo_html(facility_code, height=50):
    """Return HTML for facility logo"""
    info = FACILITY_INFO.get(facility_code, {})
    logo_file = info.get("logo_file", "churchgate-logo.png")
    logo_path = Path(logo_file)
    
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = logo_file.split(".")[-1]
        return f'<img src="data:image/{ext};base64,{b64}" height="{height}px" style="max-width:200px;object-fit:contain;">'
    return f'<span style="font-size:2rem;">🏢</span>'

def get_topnav_churchgate_logo():
    """Churchgate logo for top nav"""
    logo_path = Path("churchgate-logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{b64}" height="26px" style="filter:brightness(0) invert(1);">'
    return '<span style="font-weight:800;color:white;font-size:0.9rem;">CHURCHGATE</span>'

# ============================================
# TOP NAVIGATION
# ============================================
def render_topnav():
    cg_logo = get_topnav_churchgate_logo()
    
    st.markdown(f"""
    <div class="fx-topnav">
        <div style="display:flex;align-items:center;gap:0.8rem;">
            {cg_logo}
            <div class="fx-brand-sep"></div>
            <span class="fx-brand-name">facility<span>X</span>perience</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.8rem;">
            <div class="fx-ai-indicator"><div class="fx-ai-dot"></div>AI ACTIVE</div>
            <span style="color:rgba(255,255,255,0.5);font-size:0.65rem;" id="live-time"></span>
            <div style="width:32px;height:32px;border-radius:50%;background:{CHURCHGATE_RED};display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.75rem;border:2px solid rgba(255,255,255,0.3);">AO</div>
        </div>
    </div>
    <script>
        function tick(){{document.getElementById('live-time').textContent=new Date().toLocaleTimeString('en-US',{{hour12:false}});}}
        tick();setInterval(tick,1000);
    </script>
    """, unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:0.3rem;margin-bottom:0.5rem;background:#c0c0c0;border-radius:6px;font-size:0.55rem;color:{CHURCHGATE_DARK};">
            ⬅️ Toggle sidebar with the <b>red arrow</b> at top-left
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<p style="font-size:0.55rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:{CHURCHGATE_GREY};">🏢 SELECT FACILITY</p>', unsafe_allow_html=True)
        
        facilities = FacilityDataEngine.get_facilities()
        if not facilities:
            facilities = [{"code": k, "name": v["full_name"]} for k, v in FACILITY_INFO.items()]
        
        selected = st.session_state.get("selected_facility", "WTC")
        
        cols = st.columns(3)
        for idx, fac in enumerate(facilities):
            code = fac.get("code", "")
            with cols[idx % 3]:
                is_active = code == selected
                if st.button(code, key=f"fac_{code}", use_container_width=True,
                           type="primary" if is_active else "secondary",
                           help=FACILITY_INFO.get(code, {}).get("full_name", code)):
                    st.session_state.selected_facility = code
                    st.rerun()
        
        # Active facility info
        info = FACILITY_INFO.get(selected, {})
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{info.get('color_light','#fce8e8')},{CHURCHGATE_SIDEBAR});border-left:3px solid {info.get('color',CHURCHGATE_RED)};border-radius:6px;padding:0.7rem;margin:0.7rem 0;">
            <div style="font-weight:700;font-size:0.8rem;color:{CHURCHGATE_DARK};">{info.get('full_name',selected)}</div>
            <div style="font-size:0.6rem;color:{CHURCHGATE_GREY};">📍 {info.get('city','')} • {info.get('description','')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        nav_sections = [
            ("🏠 UNIFIED COMMAND", [("🌐 360° Command Center", "command_center")]),
            ("🔧 ASSETS & MAINTENANCE", [
                ("🏗️ Asset Lifecycle Matrix", "asset_matrix"),
                ("📋 Work Order Orchestrator", "work_orders"),
                ("🛡️ Permit-to-Work System", "work_permits"),
                ("🔧 MEP Quality Assurance", "mep_qa"),
            ]),
            ("👥 PEOPLE & ACCESS", [
                ("🛂 Visitor Experience Portal", "visitor_portal"),
                ("👤 Identity & Access Hub", "identity_hub"),
            ]),
            ("💬 SERVICE EXPERIENCE", [
                ("🎫 Service Concierge", "tickets"),
                ("💬 AI Experience Hub", "ai_hub"),
                ("⭐ Voice of Customer", "feedback"),
            ]),
            ("📦 OPERATIONS", [
                ("📦 Material Orchestrator", "materials"),
                ("🔑 Digital Access Vault", "keys"),
                ("📬 Mail & Package Logistics", "mailroom"),
            ]),
            ("✅ COMPLIANCE & RISK", [
                ("✅ Audit Framework", "audits"),
                ("⚖️ Compliance Center", "compliance"),
                ("🚨 Incident Intelligence", "incidents"),
                ("🔄 HOTO Protocol", "hoto"),
            ]),
            ("⚡ SUSTAINABILITY", [
                ("⚡ Energy Optimizer", "energy"),
                ("📈 Activity Matrix", "activity"),
            ]),
        ]
        
        for section, items in nav_sections:
            st.markdown(f'<p style="font-size:0.5rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#888;margin:0.5rem 0 0.15rem 0;">{section}</p>', unsafe_allow_html=True)
            for label, page_id in items:
                if st.button(label, key=page_id, use_container_width=True):
                    st.session_state.current_page = page_id
                    st.rerun()
        
        st.markdown("---")
        st.markdown(f'<p style="font-size:0.5rem;color:#999;text-align:center;">SOC 2 • ISO 27001 • GDPR<br>© Churchgate Group</p>', unsafe_allow_html=True)

# ============================================
# COMMAND CENTER
# ============================================
def render_command_center():
    fac_code = st.session_state.get("selected_facility", "WTC")
    info = FACILITY_INFO.get(fac_code, {})
    kpis = FacilityDataEngine.get_kpis(fac_code)
    logo_html = get_logo_html(fac_code, 70)
    
    # Header
    st.markdown(f"""
    <div class="churchgate-header" style="display:flex;align-items:center;gap:1.5rem;">
        <div style="flex-shrink:0;">{logo_html}</div>
        <div style="flex:1;">
            <h1 style="margin:0;font-weight:800;font-size:1.6rem;color:{CHURCHGATE_DARK};">{info.get('full_name',fac_code)}</h1>
            <p style="margin:0.2rem 0 0 0;color:{CHURCHGATE_GREY};font-size:0.8rem;">
                📍 {info.get('city','')} • {info.get('description','')}
            </p>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.6rem;color:#888;">LIVE DATA</div>
            <div style="font-size:1.1rem;font-weight:700;color:{CHURCHGATE_DARK};">{datetime.now().strftime('%H:%M:%S')}</div>
            <div style="font-size:0.6rem;color:#888;">{datetime.now().strftime('%A, %d %B %Y')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Row 1
    kpi_data = [
        ("📋 Open Work Orders", kpis["open_work_orders"], f"of {kpis['total_work_orders']} total"),
        ("🛂 Today's Visitors", kpis["active_visitors"], "Expected & checked in"),
        ("🚨 Open Incidents", kpis["open_incidents"], f"of {kpis['total_incidents']} total"),
        ("🎫 Open Tickets", kpis["open_tickets"], f"of {kpis['total_tickets']} total"),
    ]
    
    cols = st.columns(4)
    for idx, (label, value, subtitle) in enumerate(kpi_data):
        with cols[idx]:
            st.markdown(f"""
            <div class="fx-card fx-animate-up fx-stagger-{idx+1}">
                <div class="fx-card-label">{label}</div>
                <div class="fx-card-value">{value}</div>
                <div class="fx-card-subtitle">{subtitle}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # KPI Row 2
    wo_all = FacilityDataEngine.get_work_orders(fac_code, 20)
    vis_all = FacilityDataEngine.get_visitors_today(fac_code)
    tickets_all = FacilityDataEngine.get_tickets(fac_code, 20)
    
    kpi_row2 = [
        ("🏗️ Total Assets", kpis["total_assets"], "Registered & tracked"),
        ("📋 Recent Work Orders", len(wo_all), "Last 20 records"),
        ("🛂 Visitors Today", len(vis_all), "All statuses"),
        ("🎫 Total Tickets", len(tickets_all), "Last 20 records"),
    ]
    
    cols2 = st.columns(4)
    for idx, (label, value, subtitle) in enumerate(kpi_row2):
        with cols2[idx]:
            st.markdown(f"""
            <div class="fx-card fx-animate-up fx-stagger-{idx+5}">
                <div class="fx-card-label">{label}</div>
                <div class="fx-card-value" style="font-size:1.5rem;">{value}</div>
                <div class="fx-card-subtitle">{subtitle}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # AI Insights + Activity
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.markdown(f"""
        <div class="fx-ai-panel" style="margin-top:1rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.8rem;">
                <span style="font-size:1.3rem;">🤖</span>
                <div>
                    <h3 style="margin:0;font-weight:700;font-size:0.9rem;">FacilityGPT Insights</h3>
                    <p style="margin:0;font-size:0.6rem;color:#aaa;">AI analysis for {info.get('full_name',fac_code)}</p>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
                <div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:0.6rem;">
                    <div style="font-size:0.55rem;color:#F59E0B;font-weight:600;">🔧 PREDICTIVE MAINTENANCE</div>
                    <p style="margin:0.2rem 0 0 0;font-size:0.65rem;color:#ccc;">HVAC Chiller A shows early degradation patterns. Schedule preventive maintenance.</p>
                </div>
                <div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:0.6rem;">
                    <div style="font-size:0.55rem;color:#10B981;font-weight:600;">⚡ ENERGY OPTIMIZATION</div>
                    <p style="margin:0.2rem 0 0 0;font-size:0.65rem;color:#ccc;">8.3% energy savings possible through optimized HVAC scheduling.</p>
                </div>
                <div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:0.6rem;">
                    <div style="font-size:0.55rem;color:#3B82F6;font-weight:600;">🛂 VISITOR PATTERN</div>
                    <p style="margin:0.2rem 0 0 0;font-size:0.65rem;color:#ccc;">+15% visitor traffic predicted tomorrow. Adjust front desk staffing.</p>
                </div>
                <div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:0.6rem;">
                    <div style="font-size:0.55rem;color:#EF4444;font-weight:600;">✅ COMPLIANCE ALERT</div>
                    <p style="margin:0.2rem 0 0 0;font-size:0.65rem;color:#ccc;">Fire safety recertification due in 6 days.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_r:
        st.markdown(f'<div style="background:{CHURCHGATE_WHITE};border-radius:8px;padding:1rem;margin-top:1rem;border:1px solid #cccccc;"><h3 style="font-size:0.8rem;font-weight:700;color:{CHURCHGATE_DARK};">🔄 Live Activity</h3>', unsafe_allow_html=True)
        activities = [
            ("#10B981", "🛂 Visitor checked in — Floor 12", "2 min ago"),
            ("#3B82F6", "🔧 Work Order completed", "4 min ago"),
            ("#10B981", "✅ MEP inspection passed — Zone A", "11 min ago"),
            ("#F59E0B", "⚡ Energy spike detected — Wing C", "23 min ago"),
            ("#3B82F6", "📋 Audit checklist submitted", "31 min ago"),
            ("#EF4444", "🚨 Minor incident — resolved", "45 min ago"),
        ]
        for dot_color, text, time in activities:
            st.markdown(f"""
            <div class="fx-timeline-item">
                <div class="fx-timeline-dot" style="background:{dot_color};"></div>
                <div><div style="color:{CHURCHGATE_DARK};">{text}</div><div style="font-size:0.55rem;color:#999;">{time}</div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tables
    st.markdown("---")
    st.markdown(f"### 📋 Recent Work Orders")
    wo_data = FacilityDataEngine.get_work_orders(fac_code, 5)
    if wo_data:
        df = pd.DataFrame(wo_data)
        show_cols = [c for c in ["wo_number", "title", "type", "priority", "status", "category"] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No work orders found.")
    
    st.markdown(f"### 🛂 Today's Visitors")
    vis_data = FacilityDataEngine.get_visitors_today(fac_code)
    if vis_data:
        df = pd.DataFrame(vis_data)
        show_cols = [c for c in ["full_name", "company", "purpose_of_visit", "host_name", "status", "expected_arrival"] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No visitors today.")

# ============================================
# MODULE PAGES
# ============================================
def render_work_orders():
    fac_code = st.session_state.get("selected_facility", "WTC")
    info = FACILITY_INFO.get(fac_code, {})
    st.markdown(f"## 📋 Work Order Orchestrator — {info.get('full_name',fac_code)}")
    wo = FacilityDataEngine.get_work_orders(fac_code, 50)
    if wo:
        df = pd.DataFrame(wo)
        c1,c2,c3,c4=st.columns(4)
        with c1: st.metric("Total", len(df))
        with c2: st.metric("Open", len(df[df.get("status","")=="open"]) if "status" in df.columns else 0)
        with c3: st.metric("In Progress", len(df[df.get("status","")=="in_progress"]) if "status" in df.columns else 0)
        with c4: st.metric("Completed", len(df[df.get("status","")=="completed"]) if "status" in df.columns else 0)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No work orders.")

def render_visitor_portal():
    fac_code = st.session_state.get("selected_facility", "WTC")
    info = FACILITY_INFO.get(fac_code, {})
    st.markdown(f"## 🛂 Visitor Experience Portal — {info.get('full_name',fac_code)}")
    vis = FacilityDataEngine.get_visitors_today(fac_code)
    if vis:
        df = pd.DataFrame(vis)
        c1,c2,c3=st.columns(3)
        with c1: st.metric("Expected Today", len(df))
        with c2: st.metric("Checked In", len(df[df.get("status","")=="checked_in"]) if "status" in df.columns else 0)
        with c3: st.metric("Pending", len(df[df.get("status","").isin(["expected","pre_registered"])]) if "status" in df.columns else 0)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No visitors today.")

def render_tickets():
    fac_code = st.session_state.get("selected_facility", "WTC")
    info = FACILITY_INFO.get(fac_code, {})
    st.markdown(f"## 🎫 Service Concierge — {info.get('full_name',fac_code)}")
    tix = FacilityDataEngine.get_tickets(fac_code, 50)
    if tix:
        df = pd.DataFrame(tix)
        c1,c2=st.columns(2)
        with c1: st.metric("Open", len(df[df.get("status","").isin(["open","in_progress"])]) if "status" in df.columns else 0)
        with c2: st.metric("Resolved", len(df[df.get("status","")=="resolved"]) if "status" in df.columns else 0)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No tickets.")

def render_incidents():
    fac_code = st.session_state.get("selected_facility", "WTC")
    info = FACILITY_INFO.get(fac_code, {})
    st.markdown(f"## 🚨 Incident Intelligence — {info.get('full_name',fac_code)}")
    inc = FacilityDataEngine.get_incidents(fac_code, 50)
    if inc:
        df = pd.DataFrame(inc)
        c1,c2=st.columns(2)
        with c1: st.metric("Total", len(df))
        with c2: st.metric("Open", len(df[df.get("status","")=="reported"]) if "status" in df.columns else 0)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No incidents reported.")

def render_asset_matrix():
    fac_code = st.session_state.get("selected_facility", "WTC")
    info = FACILITY_INFO.get(fac_code, {})
    st.markdown(f"## 🏗️ Asset Lifecycle Matrix — {info.get('full_name',fac_code)}")
    assets = FacilityDataEngine.get_assets(fac_code, 50)
    if assets:
        df = pd.DataFrame(assets)
        st.metric("Total Assets", len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No assets registered.")

def render_ai_hub():
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{CHURCHGATE_DARK},#2a2a2a);border-radius:8px;padding:1.5rem;margin-bottom:1.5rem;border:1px solid rgba(204,0,0,0.2);">
        <div style="display:flex;align-items:center;gap:1rem;">
            <span style="font-size:2rem;">🤖</span>
            <div>
                <h2 style="margin:0;color:white;font-weight:800;">AI Experience Hub</h2>
                <p style="margin:0;color:#aaa;font-size:0.8rem;">Powered by FacilityGPT</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### 💬 FacilityGPT Concierge")
        ui = st.chat_input("Ask FacilityGPT...")
        if ui:
            st.chat_message("user").write(ui)
            st.chat_message("assistant").write(f"Query received: '{ui}'. Full LLM integration in progress.")
        else:
            st.info("💡 Ask about work orders, visitors, incidents, or energy optimization.")
    with c2:
        st.markdown("### ⚡ Quick Actions")
        for a in ["📋 Create Work Order","🚨 Report Incident","🛂 Register Visitor","📊 Generate Report","✅ Start Audit"]:
            st.button(a, use_container_width=True)

def render_generic(title, icon):
    st.markdown(f"## {icon} {title}")
    st.info("🚧 Database ready. Full UI in development.")

# ============================================
# ROUTER
# ============================================
PAGE_ROUTER = {
    "command_center": render_command_center,
    "work_orders": render_work_orders,
    "visitor_portal": render_visitor_portal,
    "tickets": render_tickets,
    "incidents": render_incidents,
    "asset_matrix": render_asset_matrix,
    "ai_hub": render_ai_hub,
    "work_permits": lambda: render_generic("Permit-to-Work System","🛡️"),
    "mep_qa": lambda: render_generic("MEP Quality Assurance","🔧"),
    "identity_hub": lambda: render_generic("Identity & Access Hub","👤"),
    "feedback": lambda: render_generic("Voice of Customer","⭐"),
    "materials": lambda: render_generic("Material Orchestrator","📦"),
    "keys": lambda: render_generic("Digital Access Vault","🔑"),
    "mailroom": lambda: render_generic("Mail & Package Logistics","📬"),
    "audits": lambda: render_generic("Audit Framework","✅"),
    "compliance": lambda: render_generic("Compliance Center","⚖️"),
    "hoto": lambda: render_generic("HOTO Protocol","🔄"),
    "energy": lambda: render_generic("Energy Optimizer","⚡"),
    "activity": lambda: render_generic("Activity Matrix","📈"),
}

# ============================================
# MAIN
# ============================================
def main():
    inject_css()
    if "selected_facility" not in st.session_state:
        st.session_state.selected_facility = "WTC"
    if "current_page" not in st.session_state:
        st.session_state.current_page = "command_center"
    
    render_topnav()
    render_sidebar()
    
    current = st.session_state.current_page
    PAGE_ROUTER.get(current, render_command_center)()

if __name__ == "__main__":
    main()