"""
🏢 facilityXperience — Enterprise Intelligent Facility Ecosystem
Churchgate Group | All Modules Live | AI-Powered Enterprise Grade
"""

import streamlit as st
from datetime import datetime, date, time
import pandas as pd
import base64
from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client

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
    "WTC": {"full_name": "World Trade Center", "city": "Abuja", "logo": "wtc-logo.jpg", "desc": "22-Floor Office Tower • 24-Floor Residential Tower • Recreation Center", "color": CHURCHGATE_RED, "clight": "#fce8e8"},
    "AGVL": {"full_name": "Agroline Ventures Limited", "city": "Abuja", "logo": "churchgate-logo.png", "desc": "Commercial/Retail Complex", "color": "#059669", "clight": "#ECFDF5"},
    "FCPL": {"full_name": "First Continental Properties Limited", "city": "Lagos", "logo": "churchgate-logo.png", "desc": "Commercial/Industrial Tower", "color": "#D97706", "clight": "#FFFBEB"},
    "RBPL": {"full_name": "RB Properties Limited", "city": "Lagos", "logo": "churchgate-logo.png", "desc": "Premium Commercial Plaza", "color": "#BE185D", "clight": "#FDF2F8"},
    "VDL": {"full_name": "Ocean Terrace", "city": "Lagos", "logo": "churchgate-logo.png", "desc": "Commercial/Industrial Centre", "color": "#7C3AED", "clight": "#F5F3FF"},
    "WAREHOUSES": {"full_name": "Warehouse Network", "city": "Lagos", "logo": "churchgate-logo.png", "desc": "Logistics & Storage Network", "color": "#475569", "clight": "#F1F5F9"},
}

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="facilityXperience | Churchgate Group", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")

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
        section[data-testid="stSidebar"] .stButton > button {{ background:#c0c0c0 !important; border:1px solid #a0a0a0 !important; color:{CHURCHGATE_DARK} !important; border-radius:6px !important; font-size:0.7rem !important; padding:0.35rem 0.5rem !important; }}
        section[data-testid="stSidebar"] button[kind="primary"] {{ background:{CHURCHGATE_RED} !important; color:white !important; border:none !important; font-weight:700 !important; }}
        
        [data-testid="collapsedControl"] {{ position:fixed !important; top:70px !important; left:0 !important; z-index:99999 !important; background:{CHURCHGATE_RED} !important; border-radius:0 6px 6px 0 !important; padding:6px 4px !important; box-shadow:0 2px 10px rgba(204,0,0,0.4) !important; width:24px !important; height:40px !important; }}
        [data-testid="collapsedControl"] svg {{ fill:white !important; width:14px !important; height:14px !important; }}
        
        .fx-topnav {{ background:linear-gradient(105deg,{CHURCHGATE_DARK},#2a2a2a,{CHURCHGATE_DARK}); padding:0.5rem 1.5rem; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:9998; border-bottom:2px solid {CHURCHGATE_RED}; box-shadow:0 2px 15px rgba(0,0,0,0.3); }}
        .fx-brand {{ font-size:1.05rem; font-weight:700; color:white; }}
        .fx-brand span {{ color:{CHURCHGATE_RED}; font-weight:800; }}
        
        .churchgate-header {{ background:white; padding:1.5rem; border-radius:8px; margin-bottom:1.5rem; border-left:4px solid {CHURCHGATE_RED}; box-shadow:0 1px 3px rgba(0,0,0,0.06); }}
        .fx-card {{ background:white; border-radius:8px; padding:1rem; border:1px solid #ccc; box-shadow:0 1px 3px rgba(0,0,0,0.06); transition:all 0.2s; }}
        .fx-card:hover {{ box-shadow:0 4px 12px rgba(0,0,0,0.1); border-color:{CHURCHGATE_RED}; transform:translateY(-2px); }}
        .fx-card-label {{ font-size:0.6rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; color:{CHURCHGATE_GREY}; margin-bottom:0.3rem; }}
        .fx-card-value {{ font-size:1.6rem; font-weight:800; color:{CHURCHGATE_DARK}; line-height:1; }}
        .fx-card-subtitle {{ font-size:0.65rem; color:#888; }}
        
        .stButton > button {{ background:{CHURCHGATE_RED} !important; color:white !important; border:none !important; border-radius:6px !important; font-weight:600 !important; }}
        .stButton > button:hover {{ background:#aa0000 !important; }}
        
        .fx-ai-panel {{ background:linear-gradient(135deg,{CHURCHGATE_DARK},#2a2a2a); border-radius:8px; padding:1.5rem; color:white; border:1px solid rgba(204,0,0,0.3); }}
        
        .fx-timeline {{ display:flex; gap:0.5rem; padding:0.4rem 0; border-bottom:1px solid #e0e0e0; font-size:0.7rem; }}
        .fx-dot {{ width:6px; height:6px; border-radius:50%; margin-top:4px; flex-shrink:0; }}
        
        .fx-badge {{ display:inline-flex; align-items:center; gap:0.2rem; padding:0.15rem 0.5rem; border-radius:50px; font-size:0.6rem; font-weight:600; }}
        .badge-success {{ background:#ECFDF5; color:#065F46; }} .badge-warning {{ background:#FFFBEB; color:#92400E; }}
        .badge-critical {{ background:#FEF2F2; color:#991B1B; }} .badge-info {{ background:#EFF6FF; color:#1E40AF; }}
        .badge-pending {{ background:#FEF3C7; color:#92400E; }} .badge-approved {{ background:#ECFDF5; color:#065F46; }}
        
        [data-testid="stDataFrame"] {{ border-radius:8px !important; border:1px solid #ccc !important; }}
        [data-testid="stDataFrame"] th {{ background:{CHURCHGATE_LIGHT} !important; font-weight:600 !important; font-size:0.65rem !important; text-transform:uppercase !important; color:{CHURCHGATE_GREY} !important; padding:0.5rem !important; }}
        [data-testid="stDataFrame"] td {{ font-size:0.7rem !important; padding:0.4rem 0.5rem !important; }}
        
        [data-testid="stMetric"] {{ background:white; padding:0.8rem !important; border-radius:8px !important; border:1px solid #ccc !important; }}
        
        @keyframes fxSlideUp {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:translateY(0); }} }}
        .fx-animate-up {{ animation:fxSlideUp 0.35s ease-out forwards; }}
        .fx-s1 {{ animation-delay:0.03s; opacity:0; }} .fx-s2 {{ animation-delay:0.06s; opacity:0; }}
        .fx-s3 {{ animation-delay:0.09s; opacity:0; }} .fx-s4 {{ animation-delay:0.12s; opacity:0; }}
        .fx-s5 {{ animation-delay:0.15s; opacity:0; }} .fx-s6 {{ animation-delay:0.18s; opacity:0; }}
        
        hr {{ border-color:#ddd !important; margin:1rem 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

# ============================================
# LOGO HELPERS
# ============================================
def get_facility_logo(facility_code, height=60):
    info = FACILITY_INFO.get(facility_code, {})
    logo_file = info.get("logo", "churchgate-logo.png")
    logo_path = Path(logo_file)
    if logo_path.exists():
        ext = logo_file.split(".")[-1].replace("jpg", "jpeg")
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/{ext};base64,{b64}" height="{height}px" style="max-width:220px;object-fit:contain;">'
    return f'<span style="font-size:2.5rem;">🏢</span>'

def get_churchgate_logo_nav():
    p = Path("churchgate-logo.png")
    if p.exists():
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{b64}" height="26px" style="filter:brightness(0) invert(1);">'
    return '<span style="font-weight:800;color:white;">CHURCHGATE</span>'

# ============================================
# DATA ENGINE
# ============================================
class DB:
    @staticmethod
    def get_kpis(fc):
        try:
            wo = supabase.table("work_orders").select("id",count="exact").eq("facility_code",fc).eq("status","open").execute()
            wo_all = supabase.table("work_orders").select("id",count="exact").eq("facility_code",fc).execute()
            vis = supabase.table("visitors").select("id",count="exact").eq("facility_code",fc).eq("visit_date",str(date.today())).execute()
            inc = supabase.table("incidents").select("id",count="exact").eq("facility_code",fc).eq("status","reported").execute()
            inc_all = supabase.table("incidents").select("id",count="exact").eq("facility_code",fc).execute()
            tix = supabase.table("tickets").select("id",count="exact").eq("facility_code",fc).in_("status",["open","in_progress"]).execute()
            tix_all = supabase.table("tickets").select("id",count="exact").eq("facility_code",fc).execute()
            ast = supabase.table("assets").select("id",count="exact").eq("facility_code",fc).execute()
            wp = supabase.table("work_permits").select("id",count="exact").eq("facility_code",fc).eq("status","pending").execute()
            return {"open_wo":wo.count or 0,"total_wo":wo_all.count or 0,"visitors":vis.count or 0,"open_inc":inc.count or 0,"total_inc":inc_all.count or 0,"open_tix":tix.count or 0,"total_tix":tix_all.count or 0,"assets":ast.count or 0,"pending_permits":wp.count or 0}
        except: return {"open_wo":0,"total_wo":0,"visitors":0,"open_inc":0,"total_inc":0,"open_tix":0,"total_tix":0,"assets":0,"pending_permits":0}

    @staticmethod
    def get_all(table, fc, limit=100):
        try:
            res = supabase.table(table).select("*").eq("facility_code",fc).order("created_at",desc=True).limit(limit).execute()
            return res.data or []
        except: return []

    @staticmethod
    def insert(table, data):
        try:
            res = supabase.table(table).insert(data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            st.error(f"Insert error: {e}")
            return None

    @staticmethod
    def update(table, id_val, data):
        try:
            supabase.table(table).update(data).eq("id",id_val).execute()
            return True
        except: return False

# ============================================
# TOP NAV
# ============================================
def topnav():
    cg = get_churchgate_logo_nav()
    st.markdown(f"""
    <div class="fx-topnav">
        <div style="display:flex;align-items:center;gap:0.8rem;">{cg}<div style="width:1px;height:22px;background:linear-gradient(180deg,transparent,rgba(204,0,0,0.6),transparent);"></div><span class="fx-brand">facility<span>X</span>perience</span></div>
        <div style="display:flex;align-items:center;gap:0.8rem;"><div style="display:flex;align-items:center;gap:0.3rem;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);border-radius:50px;padding:0.25rem 0.7rem;font-size:0.6rem;font-weight:600;color:#6EE7B7;"><div style="width:5px;height:5px;border-radius:50%;background:#10B981;animation:fxPulse 2s infinite;"></div>AI ACTIVE</div><span style="color:rgba(255,255,255,0.5);font-size:0.65rem;" id="lt"></span><div style="width:32px;height:32px;border-radius:50%;background:{CHURCHGATE_RED};display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.75rem;border:2px solid rgba(255,255,255,0.3);">AO</div></div>
    </div>
    <script>function t(){{document.getElementById('lt').textContent=new Date().toLocaleTimeString('en-US',{{hour12:false}});}}t();setInterval(t,1000);</script>
    <style>@keyframes fxPulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}</style>
    """, unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
def sidebar():
    with st.sidebar:
        st.markdown(f'<div style="text-align:center;padding:0.3rem;margin-bottom:0.5rem;background:#c0c0c0;border-radius:6px;font-size:0.55rem;">⬅️ Red arrow at top-left = toggle sidebar</div>',unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.55rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:{CHURCHGATE_GREY};">🏢 SELECT FACILITY</p>',unsafe_allow_html=True)
        sel = st.session_state.get("facility","WTC")
        cols = st.columns(3)
        for i,(k,v) in enumerate(FACILITY_INFO.items()):
            with cols[i%3]:
                if st.button(k,key=f"f_{k}",use_container_width=True,type="primary" if k==sel else "secondary",help=v["full_name"]):
                    st.session_state.facility=k;st.rerun()
        info = FACILITY_INFO.get(sel,{})
        st.markdown(f'<div style="background:{info.get("clight","#fce8e8")};border-left:3px solid {info.get("color",CHURCHGATE_RED)};border-radius:6px;padding:0.7rem;margin:0.7rem 0;"><div style="font-weight:700;font-size:0.8rem;">{info.get("full_name",sel)}</div><div style="font-size:0.6rem;color:{CHURCHGATE_GREY};">📍 {info.get("city","")} • {info.get("desc","")}</div></div>',unsafe_allow_html=True)
        st.markdown("---")
        nav = [
            ("🏠 COMMAND", [("🌐 Command Center","cc")]),
            ("🔧 MAINTENANCE", [("📋 Work Orders","wo"),("🛡️ Work Permits","wp"),("🏗️ Asset Register","ar"),("🔧 MEP/HK Check","mep")]),
            ("👥 PEOPLE", [("🛂 Visitor Management","vm"),("👤 Users Profile","up")]),
            ("💬 SERVICES", [("🎫 Raise a Ticket","rt"),("💬 Helpdesk","hd"),("💬 AI Hub","ai"),("⭐ Feedback","fb"),("📝 Survey","sv")]),
            ("📦 OPERATIONS", [("📦 Material Tracking","mt"),("🔑 Key Check","kc"),("📬 Mailroom","mr")]),
            ("✅ COMPLIANCE", [("✅ Audit Checklist","ac"),("⚖️ Compliance","cc2"),("🚨 Incident Check","ic"),("🔄 HOTO Check","hc")]),
            ("⚡ SUSTAINABILITY", [("⚡ Utility Check","uc"),("📈 Activity Check","ac2")]),
            ("📊 REPORTS", [("📊 Monthly MIS","mis")]),
        ]
        for s,items in nav:
            st.markdown(f'<p style="font-size:0.5rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#888;margin:0.5rem 0 0.1rem 0;">{s}</p>',unsafe_allow_html=True)
            for l,p in items:
                if st.button(l,key=p,use_container_width=True):st.session_state.page=p;st.rerun()
        st.markdown("---")
        st.markdown(f'<p style="font-size:0.5rem;color:#999;text-align:center;">SOC 2 • ISO 27001 • GDPR<br>© Churchgate Group</p>',unsafe_allow_html=True)

# ============================================
# COMMAND CENTER
# ============================================
def page_command_center():
    fc = st.session_state.get("facility","WTC")
    info = FACILITY_INFO.get(fc,{})
    k = DB.get_kpis(fc)
    logo = get_facility_logo(fc,70)
    st.markdown(f'<div class="churchgate-header" style="display:flex;align-items:center;gap:1.5rem;"><div style="flex-shrink:0;">{logo}</div><div style="flex:1;"><h1 style="margin:0;font-weight:800;font-size:1.5rem;color:{CHURCHGATE_DARK};">{info.get("full_name",fc)}</h1><p style="margin:0.2rem 0 0 0;color:{CHURCHGATE_GREY};font-size:0.8rem;">📍 {info.get("city","")} • {info.get("desc","")}</p></div><div style="text-align:right;"><div style="font-size:0.6rem;color:#888;">LIVE DATA</div><div style="font-size:1.1rem;font-weight:700;">{datetime.now().strftime("%H:%M:%S")}</div><div style="font-size:0.6rem;color:#888;">{datetime.now().strftime("%A, %d %B %Y")}</div></div></div>',unsafe_allow_html=True)
    
    kpi = [("📋 Open Work Orders",k["open_wo"],f"of {k['total_wo']} total"),("🛂 Today's Visitors",k["visitors"],"Expected & checked in"),("🚨 Open Incidents",k["open_inc"],f"of {k['total_inc']} total"),("🎫 Open Tickets",k["open_tix"],f"of {k['total_tix']} total")]
    cols=st.columns(4)
    for i,(l,v,s) in enumerate(kpi):
        with cols[i]:st.markdown(f'<div class="fx-card fx-animate-up fx-s{i+1}"><div class="fx-card-label">{l}</div><div class="fx-card-value">{v}</div><div class="fx-card-subtitle">{s}</div></div>',unsafe_allow_html=True)
    
    wo=DB.get_all("work_orders",fc,20);vis=DB.get_all("visitors",fc,20);tix=DB.get_all("tickets",fc,20)
    kpi2=[("🏗️ Total Assets",k["assets"],"Registered"),("📋 Recent WOs",len(wo),"Last 20"),("🛂 Visitors Today",len(vis),"All"),("🛡️ Pending Permits",k["pending_permits"],"Awaiting approval")]
    cols2=st.columns(4)
    for i,(l,v,s) in enumerate(kpi2):
        with cols2[i]:st.markdown(f'<div class="fx-card fx-animate-up fx-s{i+5}"><div class="fx-card-label">{l}</div><div class="fx-card-value" style="font-size:1.5rem;">{v}</div><div class="fx-card-subtitle">{s}</div></div>',unsafe_allow_html=True)
    
    cl,cr=st.columns([2,1])
    with cl:
        st.markdown(f'<div class="fx-ai-panel" style="margin-top:1rem;"><div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.8rem;"><span style="font-size:1.3rem;">🤖</span><div><h3 style="margin:0;font-weight:700;font-size:0.9rem;">FacilityGPT Insights</h3><p style="margin:0;font-size:0.6rem;color:#aaa;">AI analysis for {info.get("full_name",fc)}</p></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;"><div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:0.6rem;"><div style="font-size:0.55rem;color:#F59E0B;font-weight:600;">🔧 MAINTENANCE</div><p style="margin:0.2rem 0 0 0;font-size:0.65rem;color:#ccc;">HVAC Chiller A due for preventive maintenance.</p></div><div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:0.6rem;"><div style="font-size:0.55rem;color:#10B981;font-weight:600;">⚡ ENERGY</div><p style="margin:0.2rem 0 0 0;font-size:0.65rem;color:#ccc;">8.3% savings possible through HVAC optimization.</p></div><div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:0.6rem;"><div style="font-size:0.55rem;color:#3B82F6;font-weight:600;">🛂 VISITORS</div><p style="margin:0.2rem 0 0 0;font-size:0.65rem;color:#ccc;">+15% traffic predicted tomorrow.</p></div><div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:0.6rem;"><div style="font-size:0.55rem;color:#EF4444;font-weight:600;">✅ COMPLIANCE</div><p style="margin:0.2rem 0 0 0;font-size:0.65rem;color:#ccc;">Fire recertification due in 6 days.</p></div></div></div>',unsafe_allow_html=True)
    with cr:
        st.markdown(f'<div style="background:white;border-radius:8px;padding:1rem;margin-top:1rem;border:1px solid #ccc;"><h3 style="font-size:0.8rem;font-weight:700;">🔄 Live Activity</h3>',unsafe_allow_html=True)
        acts=[("#10B981","🛂 Visitor checked in","2m ago"),("#3B82F6","🔧 WO completed","4m ago"),("#10B981","✅ MEP passed","11m ago"),("#F59E0B","⚡ Energy spike","23m ago"),("#EF4444","🚨 Incident resolved","45m ago")]
        for dc,tx,tm in acts:st.markdown(f'<div class="fx-timeline"><div class="fx-dot" style="background:{dc};"></div><div><div>{tx}</div><div style="font-size:0.55rem;color:#999;">{tm}</div></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📋 Recent Work Orders")
    if wo:st.dataframe(pd.DataFrame(wo)[[c for c in ["wo_number","title","priority","status","category"] if c in pd.DataFrame(wo).columns]],use_container_width=True,hide_index=True)
    else:st.info("No work orders")
    st.markdown("### 🛂 Today's Visitors")
    if vis:st.dataframe(pd.DataFrame(vis)[[c for c in ["full_name","company","purpose_of_visit","status"] if c in pd.DataFrame(vis).columns]],use_container_width=True,hide_index=True)
    else:st.info("No visitors today")

# ============================================
# WORK ORDERS
# ============================================
def page_work_orders():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📋 Work Order Orchestrator — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 View Work Orders","➕ Create Work Order"])
    with tab1:
        data=DB.get_all("work_orders",fc,50)
        if data:
            df=pd.DataFrame(data)
            c1,c2,c3,c4=st.columns(4)
            with c1:st.metric("Total",len(df))
            with c2:st.metric("Open",len(df[df["status"]=="open"]) if "status" in df.columns else 0)
            with c3:st.metric("In Progress",len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0)
            with c4:st.metric("Completed",len(df[df["status"]=="completed"]) if "status" in df.columns else 0)
            st.dataframe(df,use_container_width=True,hide_index=True)
        else:st.info("No work orders found.")
    with tab2:
        with st.form("wo_form"):
            st.markdown("### Create New Work Order")
            c1,c2=st.columns(2)
            with c1:
                title=st.text_input("Title*")
                wo_type=st.selectbox("Type*",["preventive","corrective","inspection","emergency","other"])
                priority=st.selectbox("Priority",["low","medium","high","critical"])
                category=st.selectbox("Category",["HVAC","Electrical","Plumbing","Fire Safety","Elevators","Security","Cleaning","Generators","IT","Other"])
            with c2:
                desc=st.text_area("Description")
                location=st.text_input("Location (Building/Floor)")
                assigned=st.text_input("Assigned Team/Person")
            if st.form_submit_button("📋 Create Work Order",use_container_width=True):
                if title:
                    cnt=len(DB.get_all("work_orders",fc,1000))
                    DB.insert("work_orders",{"facility_code":fc,"wo_number":f"WO-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"type":wo_type,"priority":priority,"category":category,"description":desc,"location_building":location,"assigned_team":assigned,"status":"open","created_at":datetime.now().isoformat()})
                    st.success("✅ Work Order created!")
                    st.rerun()
                else:st.error("Title is required")

# ============================================
# WORK PERMITS
# ============================================
def page_work_permits():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🛡️ Permit-to-Work System — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 View Permits","➕ Create Permit"])
    with tab1:
        data=DB.get_all("work_permits",fc,50)
        if data:
            df=pd.DataFrame(data)
            c1,c2,c3=st.columns(3)
            with c1:st.metric("Total",len(df))
            with c2:st.metric("Pending Approval",len(df[df["status"]=="pending"]) if "status" in df.columns else 0)
            with c3:st.metric("Approved",len(df[df["status"]=="approved"]) if "status" in df.columns else 0)
            for i,row in df.iterrows():
                status=row.get("status","draft")
                badge="badge-pending" if status=="pending" else "badge-approved" if status=="approved" else "badge-info"
                with st.expander(f"{row.get('permit_number','')} — {row.get('title','')} — {status.upper()}"):
                    c1,c2=st.columns([3,1])
                    with c1:
                        st.write(f"**Type:** {row.get('permit_type','')} | **Contractor:** {row.get('contractor_company','')} | **Location:** {row.get('work_location','')}")
                        st.write(f"**Start:** {row.get('start_datetime','')} | **End:** {row.get('end_datetime','')}")
                        st.write(f"**Description:** {row.get('description','')}")
                    with c2:
                        if status=="pending":
                            if st.button("✅ Approve",key=f"app_{row['id']}"):
                                DB.update("work_permits",row["id"],{"status":"approved","approved_at":datetime.now().isoformat(),"is_approved":True})
                                st.success("Permit Approved!");st.rerun()
                            if st.button("❌ Reject",key=f"rej_{row['id']}"):
                                DB.update("work_permits",row["id"],{"status":"rejected"})
                                st.warning("Permit Rejected");st.rerun()
                        if status=="approved" and not row.get("closed_at"):
                            if st.button("🔒 Close Permit",key=f"cls_{row['id']}"):
                                DB.update("work_permits",row["id"],{"status":"closed","closed_at":datetime.now().isoformat()})
                                st.success("Permit Closed");st.rerun()
        else:st.info("No work permits found.")
    with tab2:
        with st.form("wp_form"):
            st.markdown("### Create New Work Permit")
            c1,c2=st.columns(2)
            with c1:
                title=st.text_input("Title*")
                ptype=st.selectbox("Permit Type*",["Hot Work","Cold Work","Electrical","Confined Space","Working at Height","Excavation","Other"])
                contractor=st.text_input("Contractor Company")
                cname=st.text_input("Contractor Name")
            with c2:
                loc=st.text_input("Work Location*")
                sd=st.date_input("Start Date")
                st_time=st.time_input("Start Time",time(8,0))
                ed=st.date_input("End Date")
                et_time=st.time_input("End Time",time(17,0))
            desc=st.text_area("Description of Work")
            hazards=st.multiselect("Hazards Identified",["Fire","Electrical","Fall","Chemical","Confined Space","Heavy Lifting","Noise","Other"])
            ppe=st.multiselect("PPE Required",["Hard Hat","Safety Glasses","Gloves","Steel-toe Boots","Hi-Vis Vest","Respirator","Harness"])
            if st.form_submit_button("🛡️ Submit Permit for Approval",use_container_width=True):
                if title and loc:
                    cnt=len(DB.get_all("work_permits",fc,1000))
                    DB.insert("work_permits",{"facility_code":fc,"permit_number":f"PTW-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"permit_type":ptype,"contractor_company":contractor,"contractor_name":cname,"work_location":loc,"start_datetime":f"{sd}T{st_time}","end_datetime":f"{ed}T{et_time}","description":desc,"hazards_identified":hazards,"ppe_required":ppe,"status":"pending","created_at":datetime.now().isoformat()})
                    st.success("✅ Permit submitted for approval!")
                    st.rerun()
                else:st.error("Title and Location required")

# ============================================
# VISITOR MANAGEMENT
# ============================================
def page_visitor_management():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🛂 Visitor Experience Portal — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 Today's Visitors","➕ Register Visitor"])
    with tab1:
        data=DB.get_all("visitors",fc,50)
        if data:
            df=pd.DataFrame(data)
            c1,c2,c3=st.columns(3)
            with c1:st.metric("Expected",len(df))
            with c2:st.metric("Checked In",len(df[df["status"]=="checked_in"]) if "status" in df.columns else 0)
            with c3:st.metric("Pending",len(df[df["status"].isin(["expected","pre_registered"])]) if "status" in df.columns else 0)
            for i,row in df.iterrows():
                s=row.get("status","expected")
                badge="badge-success" if s=="checked_in" else "badge-pending" if s in ["expected","pre_registered"] else "badge-info"
                with st.expander(f"{row.get('full_name','')} — {row.get('company','')} — {s.upper()}"):
                    st.write(f"**Host:** {row.get('host_name','')} | **Purpose:** {row.get('purpose_of_visit','')}")
                    st.write(f"**Arrival:** {row.get('expected_arrival','')} | **Departure:** {row.get('expected_departure','')}")
                    if s in ["expected","pre_registered"]:
                        if st.button("✅ Check In",key=f"vin_{row['id']}"):
                            DB.update("visitors",row["id"],{"status":"checked_in","actual_arrival":datetime.now().isoformat()})
                            st.success("Checked in!");st.rerun()
                    if s=="checked_in":
                        if st.button("🚪 Check Out",key=f"vout_{row['id']}"):
                            DB.update("visitors",row["id"],{"status":"checked_out","actual_departure":datetime.now().isoformat()})
                            st.success("Checked out!");st.rerun()
        else:st.info("No visitors today.")
    with tab2:
        with st.form("vis_form"):
            st.markdown("### Register New Visitor")
            c1,c2=st.columns(2)
            with c1:
                fn=st.text_input("First Name*")
                ln=st.text_input("Last Name*")
                email=st.text_input("Email")
                phone=st.text_input("Phone")
            with c2:
                company=st.text_input("Company")
                host=st.text_input("Host Name*")
                dept=st.text_input("Host Department")
                purpose=st.text_area("Purpose of Visit")
            c3,c4=st.columns(2)
            with c3:
                vd=st.date_input("Visit Date",date.today())
                atime=st.time_input("Expected Arrival",time(9,0))
            with c4:
                dtime=st.time_input("Expected Departure",time(17,0))
                access=st.selectbox("Access Level",["standard","restricted","VIP"])
            if st.form_submit_button("🛂 Register Visitor",use_container_width=True):
                if fn and ln and host:
                    DB.insert("visitors",{"facility_code":fc,"first_name":fn,"last_name":ln,"email":email,"phone":phone,"company":company,"host_name":host,"host_department":dept,"purpose_of_visit":purpose,"visit_date":str(vd),"expected_arrival":str(atime),"expected_departure":str(dtime),"access_level":access,"status":"pre_registered","pre_registered":True,"created_at":datetime.now().isoformat()})
                    st.success("✅ Visitor registered!");st.rerun()
                else:st.error("First Name, Last Name, and Host are required")

# ============================================
# RAISE A TICKET / HELPDESK
# ============================================
def page_raise_ticket():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🎫 Service Concierge — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["🎫 View Tickets","➕ Raise New Ticket"])
    with tab1:
        data=DB.get_all("tickets",fc,50)
        if data:
            df=pd.DataFrame(data)
            c1,c2=st.columns(2)
            with c1:st.metric("Open",len(df[df["status"].isin(["open","in_progress"])]) if "status" in df.columns else 0)
            with c2:st.metric("Resolved",len(df[df["status"]=="resolved"]) if "status" in df.columns else 0)
            for i,row in df.iterrows():
                s=row.get("status","open")
                badge="badge-critical" if s=="open" else "badge-warning" if s=="in_progress" else "badge-success"
                with st.expander(f"{row.get('ticket_number','')} — {row.get('title','')} — {s.upper()}"):
                    st.write(f"**Category:** {row.get('category','')} | **Priority:** {row.get('priority','')}")
                    st.write(f"**Requester:** {row.get('requester_name','')} | **Assigned:** {row.get('assigned_team','')}")
                    st.write(f"**Description:** {row.get('description','')}")
                    if s in ["open","in_progress"]:
                        if st.button("✅ Resolve",key=f"tres_{row['id']}"):
                            DB.update("tickets",row["id"],{"status":"resolved","resolved_at":datetime.now().isoformat()})
                            st.success("Ticket resolved!");st.rerun()
        else:st.info("No tickets found.")
    with tab2:
        with st.form("tix_form"):
            st.markdown("### Raise a New Ticket")
            c1,c2=st.columns(2)
            with c1:
                title=st.text_input("Title*")
                cat=st.selectbox("Category",["HVAC","Electrical","Plumbing","Cleaning","Security","IT/Internet","Parking","Pest Control","Other"])
                priority=st.selectbox("Priority",["low","medium","high","critical"])
            with c2:
                req_name=st.text_input("Your Name*")
                req_email=st.text_input("Your Email")
                req_phone=st.text_input("Your Phone")
                loc=st.text_input("Location (Building/Floor)")
            desc=st.text_area("Description*")
            if st.form_submit_button("🎫 Raise Ticket",use_container_width=True):
                if title and desc and req_name:
                    cnt=len(DB.get_all("tickets",fc,1000))
                    DB.insert("tickets",{"facility_code":fc,"ticket_number":f"TKT-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"type":"service_request","category":cat,"priority":priority,"requester_name":req_name,"requester_email":req_email,"requester_phone":req_phone,"location_building":loc,"description":desc,"status":"open","created_at":datetime.now().isoformat()})
                    st.success("✅ Ticket raised!");st.rerun()
                else:st.error("Title, Description, and Name are required")

# ============================================
# HELPDESK DASHBOARD
# ============================================
def page_helpdesk():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 💬 Helpdesk Dashboard — {info.get("full_name",fc)}')
    tix=DB.get_all("tickets",fc,50)
    wo=DB.get_all("work_orders",fc,50)
    if tix:
        df=pd.DataFrame(tix)
        st.markdown("### 📊 Ticket Overview")
        c1,c2,c3,c4=st.columns(4)
        with c1:st.metric("🔴 Open",len(df[df["status"]=="open"]) if "status" in df.columns else 0)
        with c2:st.metric("🟡 In Progress",len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0)
        with c3:st.metric("🟢 Resolved",len(df[df["status"]=="resolved"]) if "status" in df.columns else 0)
        with c4:st.metric("📋 Total",len(df))
        st.markdown("### Recent Tickets")
        st.dataframe(df[[c for c in ["ticket_number","title","category","priority","status","requester_name","created_at"] if c in df.columns]].head(10),use_container_width=True,hide_index=True)
    else:st.info("No tickets in helpdesk.")
    st.markdown("---")
    st.markdown("### 🔧 Linked Work Orders")
    if wo:
        df2=pd.DataFrame(wo)
        st.dataframe(df2[[c for c in ["wo_number","title","status","priority"] if c in df2.columns]].head(10),use_container_width=True,hide_index=True)
    else:st.info("No work orders linked.")

# ============================================
# INCIDENT CHECK
# ============================================
def page_incident_check():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🚨 Incident Intelligence — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 View Incidents","➕ Report Incident"])
    with tab1:
        data=DB.get_all("incidents",fc,50)
        if data:
            df=pd.DataFrame(data)
            c1,c2=st.columns(2)
            with c1:st.metric("Total",len(df))
            with c2:st.metric("Open",len(df[df["status"]=="reported"]) if "status" in df.columns else 0)
            for i,row in df.iterrows():
                sev=row.get("severity","low")
                bcol="badge-critical" if sev in ["critical","high"] else "badge-warning" if sev=="medium" else "badge-info"
                with st.expander(f"{row.get('incident_number','')} — {row.get('title','')} — {sev.upper()}"):
                    st.write(f"**Type:** {row.get('type','')} | **Date:** {row.get('incident_date','')}")
                    st.write(f"**Location:** {row.get('location_building','')} Floor {row.get('location_floor','')}")
                    st.write(f"**Description:** {row.get('description','')}")
                    st.write(f"**Immediate Actions:** {row.get('immediate_actions','')}")
                    if row.get("status")=="reported":
                        if st.button("🔍 Under Investigation",key=f"inv_{row['id']}"):
                            DB.update("incidents",row["id"],{"status":"investigating"})
                            st.rerun()
                        if st.button("✅ Resolve",key=f"ires_{row['id']}"):
                            DB.update("incidents",row["id"],{"status":"resolved","closed_at":datetime.now().isoformat()})
                            st.success("Incident resolved!");st.rerun()
        else:st.success("✅ No incidents reported.")
    with tab2:
        with st.form("inc_form"):
            st.markdown("### Report New Incident")
            c1,c2=st.columns(2)
            with c1:
                title=st.text_input("Title*")
                itype=st.selectbox("Type*",["Safety","Security","Environmental","Equipment Failure","Fire","Water Leak","Power Outage","Other"])
                sev=st.selectbox("Severity",["low","medium","high","critical"])
            with c2:
                loc_b=st.text_input("Building")
                loc_f=st.text_input("Floor")
                loc_z=st.text_input("Zone/Area")
                idate=st.date_input("Incident Date",date.today())
                itime=st.time_input("Incident Time",datetime.now().time())
            desc=st.text_area("Description*")
            actions=st.text_area("Immediate Actions Taken")
            injuries=st.checkbox("Injuries reported?")
            damage=st.checkbox("Property damage?")
            if st.form_submit_button("🚨 Report Incident",use_container_width=True):
                if title and desc:
                    cnt=len(DB.get_all("incidents",fc,1000))
                    DB.insert("incidents",{"facility_code":fc,"incident_number":f"INC-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"type":itype,"severity":sev,"location_building":loc_b,"location_floor":loc_f,"location_zone":loc_z,"incident_date":str(idate),"incident_time":str(itime),"description":desc,"immediate_actions":actions,"injuries":injuries,"property_damage":damage,"status":"reported","reported_at":datetime.now().isoformat()})
                    st.success("🚨 Incident reported!");st.rerun()
                else:st.error("Title and Description required")

# ============================================
# AUDIT CHECKLIST
# ============================================
def page_audit_checklist():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ✅ Audit Framework — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 Audits","➕ Start New Audit"])
    with tab1:
        data=DB.get_all("audits",fc,50)
        if data:
            df=pd.DataFrame(data)
            st.metric("Total Audits",len(df))
            for i,row in df.iterrows():
                with st.expander(f"{row.get('audit_number','')} — {row.get('title','')} — Score: {row.get('overall_score','N/A')}"):
                    st.write(f"**Type:** {row.get('type','')} | **Date:** {row.get('audit_date','')} | **Status:** {row.get('status','')}")
                    st.write(f"**Findings:** {row.get('non_conformities',0)} NCs | {row.get('observations',0)} Observations | {row.get('opportunities_for_improvement',0)} OFIs")
        else:st.info("No audits found.")
    with tab2:
        with st.form("audit_form"):
            st.markdown("### Start New Audit")
            title=st.text_input("Audit Title*")
            c1,c2=st.columns(2)
            with c1:
                atype=st.selectbox("Audit Type",["Internal","External","Regulatory","ISO","Safety","Quality"])
                adate=st.date_input("Audit Date",date.today())
            with c2:
                auditor=st.text_input("Auditor Name")
                dept=st.text_input("Department/Scope")
            items=["Fire extinguishers accessible and inspected","Emergency exits clear","Electrical panels labeled","PPE available and in good condition","Housekeeping standards met","Waste management compliant","First aid kits stocked","Safety signage visible"]
            results={}
            st.markdown("**Checklist Items:**")
            for item in items:
                results[item]=st.selectbox(item,["Pass","Fail","N/A"],key=f"aud_{item[:20]}")
            if st.form_submit_button("✅ Submit Audit",use_container_width=True):
                if title:
                    cnt=len(DB.get_all("audits",fc,1000))
                    passed=sum(1 for v in results.values() if v=="Pass")
                    total=sum(1 for v in results.values() if v!="N/A")
                    score=round((passed/total)*100,1) if total>0 else 100
                    DB.insert("audits",{"facility_code":fc,"audit_number":f"AUD-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"type":atype,"audit_date":str(adate),"auditor_id":None,"overall_score":score,"status":"completed","findings":results,"non_conformities":sum(1 for v in results.values() if v=="Fail"),"observations":0,"opportunities_for_improvement":0,"created_at":datetime.now().isoformat()})
                    st.success(f"✅ Audit submitted! Score: {score}%");st.rerun()
                else:st.error("Title required")

# ============================================
# FEEDBACK CHECK
# ============================================
def page_feedback():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ⭐ Voice of Customer — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 Feedback Received","✍️ Submit Feedback"])
    with tab1:
        data=DB.get_all("feedback",fc,50)
        if data:
            df=pd.DataFrame(data)
            st.metric("Total Feedback",len(df))
            for i,row in df.iterrows():
                stars="⭐"*row.get("rating",0)
                with st.expander(f"{stars} — {row.get('title','')} — {row.get('category','')}"):
                    st.write(f"**Comments:** {row.get('comments','')}")
                    st.write(f"**Sentiment:** {row.get('sentiment','')} | **Status:** {row.get('status','')}")
        else:st.info("No feedback yet.")
    with tab2:
        with st.form("fb_form"):
            st.markdown("### Share Your Feedback")
            rating=st.slider("Rating",1,5,5)
            title=st.text_input("Title")
            cat=st.selectbox("Category",["Facility Condition","Service Response","Cleanliness","Security","Parking","Amenities","Staff","Other"])
            comments=st.text_area("Comments*")
            anon=st.checkbox("Submit anonymously")
            if st.form_submit_button("⭐ Submit Feedback",use_container_width=True):
                if comments:
                    sentiment="positive" if rating>=4 else "neutral" if rating==3 else "negative"
                    DB.insert("feedback",{"facility_code":fc,"category":cat,"rating":rating,"title":title,"comments":comments,"sentiment":sentiment,"is_anonymous":anon,"status":"new","created_at":datetime.now().isoformat()})
                    st.success("✅ Feedback submitted! Thank you.");st.rerun()
                else:st.error("Comments required")

# ============================================
# GENERIC DATA PAGES
# ============================================
def page_asset_register():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🏗️ Asset Lifecycle Matrix — {info.get("full_name",fc)}')
    data=DB.get_all("assets",fc,50)
    if data:
        df=pd.DataFrame(data)
        st.metric("Total Assets",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No assets registered.")

def page_mep_check():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🔧 MEP/HK Quality Assurance — {info.get("full_name",fc)}')
    data=DB.get_all("mep_checks",fc,30)
    if data:
        df=pd.DataFrame(data)
        st.metric("Total Checks",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No MEP checks recorded.")

def page_material_tracking():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📦 Material Orchestrator — {info.get("full_name",fc)}')
    data=DB.get_all("materials",fc,30)
    if data:
        df=pd.DataFrame(data)
        st.metric("Total Materials",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No materials tracked.")

def page_key_check():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🔑 Digital Access Vault — {info.get("full_name",fc)}')
    data=DB.get_all("key_registry",fc,30)
    if data:
        df=pd.DataFrame(data)
        st.metric("Total Keys",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No keys registered.")

def page_mailroom():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📬 Mail & Package Logistics — {info.get("full_name",fc)}')
    data=DB.get_all("mail_items",fc,30)
    if data:
        df=pd.DataFrame(data)
        st.metric("Total Items",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No mail items.")

def page_compliance():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ⚖️ Compliance Center — {info.get("full_name",fc)}')
    data=DB.get_all("compliance_items",fc,30)
    if data:
        df=pd.DataFrame(data)
        st.metric("Compliance Items",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No compliance items.")

def page_hoto():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🔄 HOTO Protocol — {info.get("full_name",fc)}')
    data=DB.get_all("hoto_records",fc,30)
    if data:
        df=pd.DataFrame(data)
        st.metric("HOTO Records",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No HOTO records.")

def page_utility():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ⚡ Energy & Utilities — {info.get("full_name",fc)}')
    data=DB.get_all("utility_readings",fc,30)
    if data:
        df=pd.DataFrame(data)
        st.metric("Total Readings",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No utility readings.")

def page_survey():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📝 Pulse & Engagement Analytics — {info.get("full_name",fc)}')
    data=DB.get_all("surveys",fc,20)
    if data:
        df=pd.DataFrame(data)
        st.metric("Total Surveys",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No surveys.")

def page_activity():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📈 Activity Check — {info.get("full_name",fc)}')
    data=DB.get_all("activity_logs",fc,30)
    if data:
        df=pd.DataFrame(data)
        st.metric("Activity Logs",len(df))
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No activity logs.")

def page_mis():
    fc=st.session_state.get("facility","WTC")
    info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📊 Monthly MIS — {info.get("full_name",fc)}')
    st.info("📊 Monthly Management Information System reports will be generated here with full analytics.")

def page_users():
    fc=st.session_state.get("facility","WTC")
    st.markdown(f"## 👤 Users Profile — {FACILITY_INFO.get(fc,{}).get('full_name',fc)}")
    st.info("User management module ready for implementation.")

def page_ai_hub():
    st.markdown(f'<div style="background:linear-gradient(135deg,{CHURCHGATE_DARK},#2a2a2a);border-radius:8px;padding:1.5rem;margin-bottom:1.5rem;border:1px solid rgba(204,0,0,0.2);"><div style="display:flex;align-items:center;gap:1rem;"><span style="font-size:2rem;">🤖</span><div><h2 style="margin:0;color:white;font-weight:800;">AI Experience Hub</h2><p style="margin:0;color:#aaa;font-size:0.8rem;">Powered by FacilityGPT</p></div></div></div>',unsafe_allow_html=True)
    c1,c2=st.columns([2,1])
    with c1:
        st.markdown("### 💬 FacilityGPT Concierge")
        ui=st.chat_input("Ask FacilityGPT...")
        if ui:
            st.chat_message("user").write(ui)
            st.chat_message("assistant").write(f"Query received: '{ui}'. Full LLM integration in progress for real-time facility intelligence.")
        else:st.info("💡 Ask about work orders, visitors, incidents, energy optimization, or compliance status.")
    with c2:
        st.markdown("### ⚡ Quick Actions")
        for a in ["📋 Create Work Order","🚨 Report Incident","🛂 Register Visitor","📊 Generate Report"]:st.button(a,use_container_width=True)

# ============================================
# ROUTER
# ============================================
ROUTER = {
    "cc":page_command_center,"wo":page_work_orders,"wp":page_work_permits,"ar":page_asset_register,
    "mep":page_mep_check,"vm":page_visitor_management,"up":page_users,"rt":page_raise_ticket,
    "hd":page_helpdesk,"ai":page_ai_hub,"fb":page_feedback,"sv":page_survey,
    "mt":page_material_tracking,"kc":page_key_check,"mr":page_mailroom,
    "ac":page_audit_checklist,"cc2":page_compliance,"ic":page_incident_check,"hc":page_hoto,
    "uc":page_utility,"ac2":page_activity,"mis":page_mis,
}

# ============================================
# MAIN
# ============================================
def main():
    inject_css()
    if "facility" not in st.session_state:st.session_state.facility="WTC"
    if "page" not in st.session_state:st.session_state.page="cc"
    topnav()
    sidebar()
    ROUTER.get(st.session_state.page,page_command_center)()

if __name__=="__main__":
    main()