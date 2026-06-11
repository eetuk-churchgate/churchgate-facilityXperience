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
from dotenv import load_dotenv
from supabase import create_client
import plotly.express as px
import plotly.graph_objects as go

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

def get_nav_logo():
    p=Path("churchgate-logo.png")
    if p.exists():
        with open(p,"rb") as f: b64=base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{b64}" height="26px" style="filter:brightness(0) invert(1);">'
    return '<span style="font-weight:800;color:white;">CHURCHGATE</span>'

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
    cg=get_nav_logo()
    st.markdown(f"""
    <div class="fx-topnav">
        <div style="display:flex;align-items:center;gap:0.8rem;">{cg}<div style="width:1px;height:22px;background:linear-gradient(180deg,transparent,rgba(204,0,0,0.6),transparent);"></div><span class="fx-brand">facility<span>X</span>perience</span></div>
        <div style="display:flex;align-items:center;gap:0.8rem;"><div style="display:flex;align-items:center;gap:0.3rem;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);border-radius:50px;padding:0.25rem 0.7rem;font-size:0.6rem;font-weight:600;color:#6EE7B7;"><div style="width:5px;height:5px;border-radius:50%;background:#10B981;animation:fxPulse 2s infinite;"></div>AI ACTIVE</div><span style="color:rgba(255,255,255,0.5);font-size:0.65rem;" id="lt"></span><div style="width:32px;height:32px;border-radius:50%;background:{CHURCHGATE_RED};display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.75rem;">EE</div></div>
    </div>
    <script>function t(){{document.getElementById('lt').textContent=new Date().toLocaleTimeString('en-US',{{hour12:false}});}}t();setInterval(t,1000);</script>
    <style>@keyframes fxPulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}</style>
    """, unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
def sidebar():
    with st.sidebar:
        sel=st.session_state.get("facility","WTC")
        cols=st.columns(3)
        for i,(k,v) in enumerate(FACILITY_INFO.items()):
            with cols[i%3]:
                if st.button(k,key=f"f_{k}",use_container_width=True,type="primary" if k==sel else "secondary"):st.session_state.facility=k;st.rerun()
        info=FACILITY_INFO.get(sel,{})
        st.markdown(f'<div style="background:{info.get("clight","#fce8e8")};border-left:3px solid {info.get("color",CHURCHGATE_RED)};border-radius:6px;padding:0.7rem;margin:0.7rem 0;font-size:0.7rem;"><b>{info.get("full_name",sel)}</b><br>📍 {info.get("city","")}</div>',unsafe_allow_html=True)
        nav=[
            ("🏠 COMMAND",[("🌐 Command Center","cc")]),
            ("🏗️ ASSETS & PPM",[("📋 Asset Register","ar"),("📅 52-Week Calendar","cal"),("✅ Checklist Status","cs"),("📊 PPM Dashboard","ppm")]),
            ("🔧 MAINTENANCE",[("📋 Work Orders","wo"),("🛡️ Work Permits","wp")]),
            ("🏢 FACILITY OPERATIONS",[("📊 Operations Dashboard","fo"),("✅ Observations/Alerts","oa")]),
            ("👥 PEOPLE",[("🛂 Visitor Management","vm"),("👤 Users Profile","up")]),
            ("💬 SERVICES",[("🎫 Raise a Ticket","rt"),("💬 Helpdesk","hd"),("⭐ Feedback","fb")]),
            ("✅ COMPLIANCE",[("✅ Audit Checklist","ac"),("🚨 Incident Check","ic"),("🔄 HOTO Check","hot")]),
            ("⚡ UTILITY",[("⚡ Utility Dashboard","uc")]),
            ("📊 REPORTS",[("📊 Monthly MIS","mis")]),
        ]
        for s,items in nav:
            st.markdown(f'<p style="font-size:0.5rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#888;margin:0.5rem 0 0.1rem 0;">{s}</p>',unsafe_allow_html=True)
            for l,p in items:
                if st.button(l,key=p,use_container_width=True):st.session_state.page=p;st.rerun()

# ============================================
# COMMAND CENTER
# ============================================
def page_cc():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{});k=DB.get_kpis(fc);logo=get_facility_logo(fc,70)
    st.markdown(f'<div class="churchgate-header" style="display:flex;align-items:center;gap:1.5rem;"><div style="flex-shrink:0;">{logo}</div><div style="flex:1;"><h1 style="margin:0;font-weight:800;font-size:1.5rem;color:{CHURCHGATE_DARK};">{info.get("full_name",fc)}</h1><p style="margin:0.2rem 0 0 0;color:{CHURCHGATE_GREY};font-size:0.8rem;">📍 {info.get("city","")} • {info.get("desc","")}</p></div><div style="text-align:right;"><div style="font-size:0.6rem;color:#888;">LIVE DATA</div><div style="font-size:1.1rem;font-weight:700;">{datetime.now().strftime("%H:%M:%S")}</div></div></div>',unsafe_allow_html=True)
    kpi=[("📋 Open WOs",k["open_wo"]),("🛂 Visitors Today",k["visitors"]),("🚨 Incidents",k["open_inc"]),("🎫 Open Tickets",k["open_tix"]),("🏗️ Assets",k["assets"]),("🔧 PPM Due",k["ppm_due"]),("🛡️ Pending Permits",k["pending_permits"])]
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
            msg['From'] = cfg.get('sender_email', 'eetuk@churchgate.com')
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
    """Get people for a workflow level"""
    try:
        query = supabase.table("workflow_config").select("*").eq("facility_code", fc).eq("workflow_type", "work_permit").eq("level_number", level).eq("is_active", True)
        res = query.execute()
        people = res.data if res.data else []
        if department and people:
            filtered = [p for p in people if not p.get("department_filter") or p["department_filter"] == [] or p["department_filter"] == ["All Departments"] or department in p["department_filter"]]
            return filtered if filtered else people
        return people
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
                        st.caption(f"📤 Submitted: {format_wat_time(row.get('submitted_at', row.get('created_at', '')))}")
                        if row.get("authorized_at"): 
                            st.caption(f"🔐 Authorized: {format_wat_time(row['authorized_at'])} by {row.get('authorized_by_name', '')}")
                        if row.get("confirmed_at"): 
                            st.caption(f"✅ Confirmed: {format_wat_time(row['confirmed_at'])} by {row.get('confirmed_by_name', '')}")
                        if row.get("approved_at"): 
                            st.caption(f"🟢 Approved: {format_wat_time(row['approved_at'])} by {row.get('approved_by_name', '')}")
                    
                    with c2:
                        st.markdown("**⚡ Actions:**")
                        now = datetime.now().isoformat()
                        dept = row.get("department", "")
                        
                        if stage == "submitted":
                            authorizers = get_workflow_people(fc, 1, dept)
                            if authorizers:
                                auth_names = [a.get("person_name", "Unknown") for a in authorizers]
                                selected_auth = st.selectbox("Select Authorizer", auth_names, key=f"auth_sel_{row['id']}")
                                if st.button("🔐 Authorize", key=f"auth_btn_{row['id']}", use_container_width=True, type="primary"):
                                    DB.update("work_permits", row["id"], {
                                        "workflow_stage": "authorized",
                                        "authorized_by_name": selected_auth,
                                        "authorized_at": now
                                    })
                                    # Notify confirmers
                                    confirmers = get_workflow_people(fc, 2)
                                    for c in confirmers:
                                        send_email_notification(c.get("person_email", ""), 
                                            f"🔐 Permit {permit_no} Requires Confirmation",
                                            f"<h3>Permit Authorized</h3><p><b>{permit_no}</b> authorized by {selected_auth}.</p><p>Please confirm.</p>")
                                    st.success(f"🔐 Authorized by {selected_auth}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.warning("No authorizers configured for this department")
                        
                        if stage == "authorized":
                            confirmers = get_workflow_people(fc, 2)
                            if confirmers:
                                conf_names = [c.get("person_name", "Unknown") for c in confirmers]
                                selected_conf = st.selectbox("Select Confirmer", conf_names, key=f"conf_sel_{row['id']}")
                                if st.button("✅ Confirm", key=f"conf_btn_{row['id']}", use_container_width=True, type="primary"):
                                    DB.update("work_permits", row["id"], {
                                        "workflow_stage": "confirmed",
                                        "confirmed_by_name": selected_conf,
                                        "confirmed_at": now
                                    })
                                    approvers = get_workflow_people(fc, 3)
                                    for a in approvers:
                                        send_email_notification(a.get("person_email", ""),
                                            f"✅ Permit {permit_no} Requires Approval",
                                            f"<h3>Permit Confirmed</h3><p><b>{permit_no}</b> confirmed by {selected_conf}.</p><p>Please approve.</p>")
                                    st.success(f"✅ Confirmed by {selected_conf}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.warning("No confirmers configured")
                        
                        if stage in ["authorized", "confirmed"]:
                            approvers = get_workflow_people(fc, 3)
                            if approvers:
                                app_names = [a.get("person_name", "Unknown") for a in approvers]
                                selected_app = st.selectbox("Select Approver", app_names, key=f"app_sel_{row['id']}")
                                if st.button("🟢 Approve", key=f"app_btn_{row['id']}", use_container_width=True, type="primary"):
                                    DB.update("work_permits", row["id"], {
                                        "workflow_stage": "approved",
                                        "status": "approved",
                                        "approved_by_name": selected_app,
                                        "approved_at": now
                                    })
                                    send_email_notification(row.get("requester_contact", ""),
                                        f"🟢 Permit {permit_no} APPROVED",
                                        f"<h3>Permit Approved!</h3><p>Your permit <b>{permit_no}</b> has been <b>APPROVED</b> by {selected_app}.</p><p>You may now proceed with work.</p>")
                                    st.success(f"🟢 Approved by {selected_app}!")
                                    st.balloons()
                                    st.rerun()
                            else:
                                st.warning("No approvers configured")
                        
                        if stage != "rejected":
                            if st.button("❌ Reject", key=f"rej_btn_{row['id']}", use_container_width=True):
                                DB.update("work_permits", row["id"], {
                                    "workflow_stage": "rejected",
                                    "status": "rejected",
                                    "rejected_at": now
                                })
                                st.error("Permit Rejected")
                                st.rerun()
        else:
            st.info("📋 No work permits found. Raise your first permit in the '➕ Raise Permit' tab!")
            st.markdown("---")
            st.markdown("**Debug Info:**")
            st.code(f"Facility: {fc}\nTable: work_permits\nCheck Supabase for data.")
    
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
            
            st.markdown("---")
            description = st.text_area("Brief Description of Work*", height=80, placeholder="Describe the work to be performed...")
            
            st.markdown("**🦺 PPE Required**")
            ppe_selected = st.multiselect("Select PPE", [
                "Hard Hat", "Face Shield", "Welder Gloves", "Electrical Gloves", "Body Harness",
                "Foot Protection", "Ear Plug/Earmuffs", "Chemical Goggles", "Safety Shoes",
                "Respirator", "Safety Glass", "Fall Protection"
            ])
            
            st.markdown("**🔧 Equipment Required**")
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
                    st.error(f"⚠️ Please fill all required fields: {', '.join(errors)}")
                else:
                    now = datetime.now().isoformat()
                    cnt = len(DB.get_all("work_permits", fc, 1000))
                    permit_number = f"PTW-{fc}-{datetime.now().year}-{str(cnt + 1).zfill(4)}"
                    
                    permit_data = {
                        "facility_code": fc,
                        "permit_number": permit_number,
                        "document_no": document_no,
                        "permit_type": permit_type,
                        "department": dept,
                        "title": description[:100],
                        "description": description,
                        "raised_by_name": rname,
                        "raised_by_designation": rdesignation,
                        "requester_contact": rcontact,
                        "process_owner_name": powner,
                        "process_owner_contact": pcontact,
                        "site_coordinator_name": scoordinator,
                        "workers_count": workers,
                        "work_location": full_location,
                        "start_datetime": f"{sd}T{stime}",
                        "end_datetime": f"{ed}T{etime}",
                        "ppe_required": ppe_selected,
                        "equipment_required": equip_selected,
                        "status": "pending",
                        "workflow_stage": "submitted",
                        "submitted_at": now,
                        "created_at": now
                    }
                    
                    result = DB.insert("work_permits", permit_data)
                    
                    if result:
                        # Notify authorizers
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
                                f"<p>Please review and authorize at your earliest convenience.</p>"
                            )
                        
                        st.success(f"✅ Work Permit {permit_number} Submitted Successfully!")
                        st.info(f"📧 Authorization requests sent to {len(authorizers)} team lead(s)")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to submit permit. Please try again.")
    
    # ============================================
    # TAB 3: REPORTS (FULLY FUNCTIONAL)
    # ============================================
    with tab3:
        st.markdown("### 📊 Work Permit Analytics & Reports")
        wp_all = DB.get_all("work_permits", fc, 500)
        
        if wp_all and len(wp_all) > 0:
            df = pd.DataFrame(wp_all)
            
            # KPI Row
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.metric("📋 Total", len(df))
            with c2: st.metric("🟢 Approved", len(df[df["workflow_stage"] == "approved"]) if "workflow_stage" in df.columns else 0)
            with c3: st.metric("⏳ Pending", len(df[df["workflow_stage"].isin(["submitted", "authorized", "confirmed"])]) if "workflow_stage" in df.columns else 0)
            with c4: st.metric("❌ Rejected", len(df[df["workflow_stage"] == "rejected"]) if "workflow_stage" in df.columns else 0)
            
            # Average approval time
            if "submitted_at" in df.columns and "approved_at" in df.columns:
                approved = df[df["approved_at"].notna()]
                if len(approved) > 0:
                    times = []
                    for _, r in approved.iterrows():
                        try:
                            s = pd.to_datetime(r["submitted_at"])
                            a = pd.to_datetime(r["approved_at"])
                            times.append((a - s).total_seconds() / 3600)
                        except: pass
                    if times:
                        avg_time = sum(times) / len(times)
                        with c5: st.metric("⏱️ Avg Approval", f"{avg_time:.1f} hrs")
            
            st.markdown("---")
            
            # ============================================
            # CLICKABLE MONTHLY BREAKDOWN
            # ============================================
            st.markdown("### 📅 Monthly Breakdown (Click to Filter)")
            
            # Initialize month filter in session state
            if "report_month_filter" not in st.session_state:
                st.session_state.report_month_filter = None
            
            months = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
            months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            
            # Row 1: Jan - Jun
            cols = st.columns(6)
            for i in range(6):
                m_idx = i + 1
                month_df = df[pd.to_datetime(df["created_at"]).dt.month == m_idx] if "created_at" in df.columns else pd.DataFrame()
                count = len(month_df)
                
                with cols[i]:
                    # Make it clickable
                    is_active = st.session_state.report_month_filter == m_idx
                    card_style = f"background: {CHURCHGATE_RED}; color: white;" if is_active else "background: white;"
                    
                    st.markdown(f"""
                    <div style="{card_style} border-radius: 10px; padding: 0.8rem; text-align: center; 
                         border: 2px solid {'#aa0000' if is_active else '#ddd'}; cursor: pointer; margin-bottom: 0.3rem;"
                         onclick="console.log('clicked')">
                        <div style="font-size: 0.7rem; font-weight: 600;">{months_short[i]}</div>
                        <div style="font-size: 1.8rem; font-weight: 800;">{count}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"{'🔴' if is_active else '📋'} {months_short[i]}", key=f"month_btn_{m_idx}", use_container_width=True):
                        if st.session_state.report_month_filter == m_idx:
                            st.session_state.report_month_filter = None  # Deselect
                        else:
                            st.session_state.report_month_filter = m_idx  # Select
                        st.rerun()
            
            # Row 2: Jul - Dec
            cols2 = st.columns(6)
            for i in range(6):
                m_idx = i + 7
                month_df = df[pd.to_datetime(df["created_at"]).dt.month == m_idx] if "created_at" in df.columns else pd.DataFrame()
                count = len(month_df)
                
                with cols2[i]:
                    is_active = st.session_state.report_month_filter == m_idx
                    card_style = f"background: {CHURCHGATE_RED}; color: white;" if is_active else "background: white;"
                    
                    st.markdown(f"""
                    <div style="{card_style} border-radius: 10px; padding: 0.8rem; text-align: center; 
                         border: 2px solid {'#aa0000' if is_active else '#ddd'}; margin-bottom: 0.3rem;">
                        <div style="font-size: 0.7rem; font-weight: 600;">{months_short[i+6]}</div>
                        <div style="font-size: 1.8rem; font-weight: 800;">{count}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"{'🔴' if is_active else '📋'} {months_short[i+6]}", key=f"month_btn_{m_idx}", use_container_width=True):
                        if st.session_state.report_month_filter == m_idx:
                            st.session_state.report_month_filter = None
                        else:
                            st.session_state.report_month_filter = m_idx
                        st.rerun()
            
            st.markdown("---")
            
            # ============================================
            # FILTERED VIEW
            # ============================================
            if st.session_state.report_month_filter:
                month_idx = st.session_state.report_month_filter
                filtered_df = df[pd.to_datetime(df["created_at"]).dt.month == month_idx] if "created_at" in df.columns else df
                st.markdown(f"### 📋 {months[month_idx-1]} Permits ({len(filtered_df)} records)")
                
                show_cols = [c for c in ["permit_number", "permit_type", "raised_by_name", "department", 
                                          "work_location", "workflow_stage", "submitted_at", 
                                          "authorized_at", "approved_at"] if c in filtered_df.columns]
                st.dataframe(filtered_df[show_cols], use_container_width=True, hide_index=True)
                
                # Download filtered month
                csv = filtered_df.to_csv(index=False)
                st.download_button(f"⬇️ Download {months[month_idx-1]} CSV", csv, 
                                   f"permits_{months[month_idx-1]}_{datetime.now().year}.csv", "text/csv")
            else:
                st.info("👆 Click a month above to filter permits")
            
            st.markdown("---")
            
            # ============================================
            # ANALYTICS SUMMARY
            # ============================================
            st.markdown("### 📈 Analytics Summary")
            
            # By Permit Type
            if "permit_type" in df.columns:
                type_counts = df["permit_type"].value_counts()
                st.markdown("**By Permit Type:**")
                cols = st.columns(len(type_counts) if len(type_counts) <= 4 else 4)
                for i, (ptype, count) in enumerate(type_counts.items()):
                    with cols[i % 4]:
                        st.metric(ptype[:25], count)
            
            # By Department  
            if "department" in df.columns:
                dept_counts = df["department"].value_counts().head(5)
                st.markdown("**Top 5 Departments:**")
                for dept, count in dept_counts.items():
                    st.markdown(f"- {dept}: **{count}** permits")
            
            # By Stage
            if "workflow_stage" in df.columns:
                stage_counts = df["workflow_stage"].value_counts()
                st.markdown("**By Workflow Stage:**")
                for stage, count in stage_counts.items():
                    st.markdown(f"- {stage.upper()}: **{count}** permits")
            
            st.markdown("---")
            
            # ============================================
            # PDF & HTML REPORT GENERATION
            # ============================================
            st.markdown("### 📄 Generate Reports")
            
            # Build report data (shared between both formats)
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
            
            # Report format selector
            report_format = st.radio("Select Report Format", ["📄 PDF Download", "🌐 HTML Preview & Download"], horizontal=True)
            
            if report_format == "📄 PDF Download":
                # ============================================
                # PDF REPORT
                # ============================================
                if st.button("📊 Generate PDF Report", use_container_width=True, type="primary"):
                    try:
                        from fpdf import FPDF
                        
                        class WorkPermitPDF(FPDF):
                            def header(self):
                                self.set_fill_color(26, 26, 26)
                                self.rect(10, 10, 277, 22, 'F')
                                self.set_fill_color(204, 0, 0)
                                self.rect(10, 10, 4, 22, 'F')
                                self.set_text_color(255, 255, 255)
                                self.set_font('Helvetica', 'B', 16)
                                self.set_xy(18, 12)
                                self.cell(260, 8, 'facilityXperience - Work Permit Report', 0, 0, 'L')
                                self.set_font('Helvetica', '', 9)
                                self.set_xy(18, 20)
                                self.cell(260, 8, f'{info.get("full_name", fc)} | Generated: {datetime.now().strftime("%d %B %Y, %I:%M %p WAT")}', 0, 0, 'L')
                                self.set_y(38)
                            
                            def footer(self):
                                self.set_y(-20)
                                self.set_font('Helvetica', 'I', 7)
                                self.set_text_color(150, 150, 150)
                                self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Churchgate Group | facilityXperience | Confidential', 0, 0, 'C')
                        
                        pdf = WorkPermitPDF('L', 'mm', 'A4')
                        pdf.alias_nb_pages()
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=25)
                        
                        # KPI Section
                        pdf.set_font('Helvetica', 'B', 13)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 10, 'Key Performance Indicators', 0, 1)
                        pdf.ln(3)
                        
                        kpis = [
                            ("Total Permits", str(total), 204, 0, 0),
                            ("Approved", str(approved_count), 16, 185, 129),
                            ("Pending", str(pending_count), 245, 158, 11),
                            ("Rejected", str(rejected_count), 100, 100, 100),
                            ("Avg Lead Time", f"{avg_lead:.1f} hrs", 37, 99, 235),
                        ]
                        
                        x_start = pdf.get_x()
                        y_start = pdf.get_y()
                        for i, (label, value, r, g, b) in enumerate(kpis):
                            x = x_start + (i * 55)
                            pdf.set_xy(x, y_start)
                            pdf.set_fill_color(245, 245, 245)
                            pdf.set_draw_color(r, g, b)
                            pdf.rect(x, y_start, 50, 22, 'DF')
                            pdf.set_fill_color(r, g, b)
                            pdf.rect(x, y_start, 3, 22, 'F')
                            pdf.set_xy(x + 6, y_start + 2)
                            pdf.set_font('Helvetica', '', 7)
                            pdf.set_text_color(100, 100, 100)
                            pdf.cell(40, 5, label.upper(), 0, 0, 'C')
                            pdf.set_xy(x + 6, y_start + 9)
                            pdf.set_font('Helvetica', 'B', 16)
                            pdf.set_text_color(r, g, b)
                            pdf.cell(40, 8, value, 0, 0, 'C')
                        
                        pdf.set_y(y_start + 28)
                        pdf.ln(5)
                        
                        if delayed > 0:
                            pdf.set_fill_color(255, 243, 205)
                            pdf.set_draw_color(245, 158, 11)
                            pdf.set_font('Helvetica', 'B', 9)
                            pdf.set_text_color(146, 76, 14)
                            pdf.cell(0, 10, f'  WARNING: {delayed} permit(s) exceeded 4-hour approval target.', 1, 1, 'L', True)
                            pdf.ln(5)
                        
                        # Department Breakdown
                        pdf.set_font('Helvetica', 'B', 12)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 10, 'Department Breakdown', 0, 1)
                        pdf.set_font('Helvetica', 'B', 8)
                        pdf.set_fill_color(204, 0, 0)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(170, 7, '  Department', 1, 0, 'L', True)
                        pdf.cell(30, 7, 'Permits', 1, 0, 'C', True)
                        pdf.cell(0, 7, '', 0, 1)
                        pdf.set_font('Helvetica', '', 8)
                        pdf.set_text_color(26, 26, 26)
                        for dept, count in list(dept_data.items())[:15]:
                            safe_dept = dept.replace('\u2014','-').replace('\u2019',"'").replace('\u201c','"').replace('\u201d','"')[:70]
                            pdf.cell(170, 6, f'  {safe_dept}', 1, 0, 'L')
                            pdf.cell(30, 6, str(count), 1, 0, 'C')
                            pdf.cell(0, 6, '', 0, 1)
                        pdf.ln(5)
                        
                        # Stage Distribution
                        pdf.set_font('Helvetica', 'B', 12)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 10, 'Workflow Stage Distribution', 0, 1)
                        pdf.set_font('Helvetica', 'B', 8)
                        pdf.set_fill_color(204, 0, 0)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(100, 7, '  Stage', 1, 0, 'L', True)
                        pdf.cell(30, 7, 'Count', 1, 0, 'C', True)
                        pdf.cell(0, 7, '', 0, 1)
                        pdf.set_font('Helvetica', '', 8)
                        pdf.set_text_color(26, 26, 26)
                        for stage, count in stage_data.items():
                            safe_stage = stage.replace('\u2014','-').upper()
                            pdf.cell(100, 6, f'  {safe_stage}', 1, 0, 'L')
                            pdf.cell(30, 6, str(count), 1, 0, 'C')
                            pdf.cell(0, 6, '', 0, 1)
                        pdf.ln(5)
                        
                        # Audit Trail
                        pdf.set_font('Helvetica', 'B', 12)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 10, 'Complete Audit Trail', 0, 1)
                        pdf.set_font('Helvetica', 'B', 7)
                        pdf.set_fill_color(204, 0, 0)
                        pdf.set_text_color(255, 255, 255)
                        col_widths = [38, 30, 45, 38, 38, 38, 38, 22]
                        headers = ['Permit No', 'Raised By', 'Department', 'Submitted', 'Authorized', 'Confirmed', 'Approved', 'Status']
                        for header, width in zip(headers, col_widths):
                            pdf.cell(width, 7, f' {header}', 1, 0, 'L', True)
                        pdf.ln()
                        pdf.set_font('Helvetica', '', 6.5)
                        for _, row in df.iterrows():
                            stage = row.get('workflow_stage', '')
                            if stage == 'approved': pdf.set_text_color(6, 95, 70)
                            elif stage == 'rejected': pdf.set_text_color(153, 27, 27)
                            else: pdf.set_text_color(26, 26, 26)
                            values = [
                                str(row.get('permit_number', ''))[:18],
                                str(row.get('raised_by_name', ''))[:14],
                                str(row.get('department', '')).replace('\u2014','-')[:22],
                                str(format_wat_time(row.get('submitted_at', '')))[:16],
                                str(format_wat_time(row.get('authorized_at', '')))[:16],
                                str(format_wat_time(row.get('confirmed_at', '')))[:16],
                                str(format_wat_time(row.get('approved_at', '')))[:16],
                                stage.upper()[:8],
                            ]
                            for value, width in zip(values, col_widths):
                                pdf.cell(width, 5.5, f' {value}', 1, 0, 'L')
                            pdf.ln()
                        
                        pdf_file = f"/tmp/work_permit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        pdf.output(pdf_file)
                        
                        with open(pdf_file, "rb") as f:
                            pdf_bytes = f.read()
                        
                        st.success("✅ PDF Report Generated Successfully!")
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"Work_Permit_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
                    except Exception as e:
                        st.error(f"PDF generation error: {str(e)}")
                        st.info("Falling back to HTML format...")
            
            else:
                # ============================================
                # HTML REPORT PREVIEW & DOWNLOAD
                # ============================================
                st.markdown("### 🌐 HTML Report Preview")
                
                # Build HTML
                dept_rows = "".join([f"<tr><td>{d}</td><td>{c}</td></tr>" for d, c in list(dept_data.items())[:15]])
                stage_rows = "".join([f"<tr><td>{s.upper()}</td><td>{c}</td></tr>" for s, c in stage_data.items()])
                
                audit_rows = ""
                for _, row in df.iterrows():
                    stage = row.get('workflow_stage','')
                    badge_class = "badge-approved" if stage=="approved" else ("badge-rejected" if stage=="rejected" else "badge-pending")
                    audit_rows += f"""
                    <tr>
                        <td>{row.get('permit_number','')}</td>
                        <td>{row.get('raised_by_name','')}</td>
                        <td>{row.get('department','')[:30]}</td>
                        <td>{format_wat_time(row.get('submitted_at',''))}</td>
                        <td>{format_wat_time(row.get('authorized_at',''))}</td>
                        <td>{format_wat_time(row.get('confirmed_at',''))}</td>
                        <td>{format_wat_time(row.get('approved_at',''))}</td>
                        <td><span class="{badge_class}">{stage.upper()}</span></td>
                    </tr>"""
                
                html_report = f"""
                <!DOCTYPE html>
                <html><head><meta charset="UTF-8">
                <style>
                    body{{font-family:'Inter',Arial,sans-serif;color:#1a1a1a;font-size:11px;margin:20px}}
                    .header{{background:linear-gradient(105deg,#1a1a1a,#2a2a2a);color:white;padding:20px;border-radius:10px;margin-bottom:20px}}
                    .header h1{{margin:0;font-size:22px}}.header span{{color:#CC0000}}
                    .kpi-row{{display:flex;gap:12px;margin:15px 0}}
                    .kpi-card{{flex:1;background:white;border:1px solid #ddd;border-radius:8px;padding:12px;text-align:center;border-left:4px solid #CC0000}}
                    .kpi-card.green{{border-left-color:#10B981}}.kpi-card.orange{{border-left-color:#F59E0B}}
                    .kpi-value{{font-size:26px;font-weight:800}}.kpi-label{{font-size:10px;color:#666;text-transform:uppercase}}
                    .section{{background:white;border:1px solid #ddd;border-radius:8px;padding:15px;margin:15px 0}}
                    .section h2{{font-size:16px;color:#CC0000;margin-top:0;border-bottom:2px solid #CC0000;padding-bottom:8px}}
                    table{{width:100%;border-collapse:collapse;font-size:10px;margin:10px 0}}
                    th{{background:#CC0000;color:white;padding:8px 6px;text-align:left;font-size:9px;text-transform:uppercase}}
                    td{{padding:6px;border-bottom:1px solid #eee}}tr:nth-child(even){{background:#fafafa}}
                    .badge-approved{{background:#ECFDF5;color:#065F46;padding:3px 8px;border-radius:12px;font-weight:600}}
                    .badge-pending{{background:#FFFBEB;color:#92400E;padding:3px 8px;border-radius:12px;font-weight:600}}
                    .badge-rejected{{background:#FEF2F2;color:#991B1B;padding:3px 8px;border-radius:12px;font-weight:600}}
                    .alert-box{{background:#FFF3CD;border:1px solid #F59E0B;border-radius:8px;padding:12px;margin:10px 0}}
                    .footer{{text-align:center;font-size:9px;color:#999;margin-top:25px;border-top:1px solid #ddd;padding-top:12px}}
                </style></head><body>
                <div class="header"><h1>facility<span>X</span>perience</h1><p style="margin:5px 0 0 0">Work Permit Analytics Report</p><p style="margin:3px 0 0 0;font-size:10px;opacity:0.8">{info.get('full_name',fc)} | {datetime.now().strftime('%d %B %Y, %I:%M %p WAT')}</p></div>
                <div class="kpi-row">
                    <div class="kpi-card"><div class="kpi-value">{total}</div><div class="kpi-label">Total Permits</div></div>
                    <div class="kpi-card green"><div class="kpi-value">{approved_count}</div><div class="kpi-label">Approved</div></div>
                    <div class="kpi-card orange"><div class="kpi-value">{pending_count}</div><div class="kpi-label">Pending</div></div>
                    <div class="kpi-card"><div class="kpi-value">{rejected_count}</div><div class="kpi-label">Rejected</div></div>
                    <div class="kpi-card green"><div class="kpi-value">{avg_lead:.1f} hrs</div><div class="kpi-label">Avg Lead Time</div></div>
                </div>
                {f'<div class="alert-box"><b>DELAYED PERMITS:</b> {delayed} permit(s) exceeded 4-hour approval target.</div>' if delayed > 0 else ''}
                <div class="section"><h2>Department Breakdown</h2><table><tr><th>Department</th><th>Permits</th></tr>{dept_rows}</table></div>
                <div class="section"><h2>Workflow Stage Distribution</h2><table><tr><th>Stage</th><th>Count</th></tr>{stage_rows}</table></div>
                <div class="section"><h2>Complete Audit Trail</h2><table><tr><th>Permit No</th><th>Raised By</th><th>Department</th><th>Submitted</th><th>Authorized</th><th>Confirmed</th><th>Approved</th><th>Status</th></tr>{audit_rows}</table></div>
                <div class="footer"><p>Churchgate Group | facilityXperience Enterprise | Confidential</p><p>Auto-generated report. For queries contact facility management.</p></div>
                </body></html>"""
                
                # Preview
                st.components.v1.html(html_report, height=600, scrolling=True)
                
                # Download button
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_report,
                    file_name=f"Work_Permit_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    use_container_width=True,
                    type="primary"
                )
                st.caption("💡 Open the downloaded HTML file in any browser. Use Print → Save as PDF to convert.")

            
            # Quick CSV download
            st.markdown("---")
            csv_all = df.to_csv(index=False)
            st.download_button("⬇️ Download Full CSV Report", csv_all, 
                              f"work_permits_full_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        else:
            st.info("📋 No work permits to report yet. Raise your first permit to see analytics here.")
    
    # ============================================
    # TAB 4: WORKFLOW CONFIG (MULTI-SELECT)
    # ============================================
    with tab4:
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
# TICKETS + HELPDESK
# ============================================
def page_rt():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🎫 Service Concierge — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["🎫 Raise Ticket","📋 View Tickets"])
    with tab1:
        locs=DB.get_locations(fc)
        loc_names=["Choose one"]+[l.get("location_name","") for l in locs]
        cats=[
    {"department":"Engineering — Electrical","category":"Electrical"},
    {"department":"Engineering — HVAC","category":"HVAC"},
    {"department":"Engineering — Plumbing","category":"Plumbing"},
    {"department":"Engineering — Fire Fighting","category":"Fire Safety"},
    {"department":"Engineering — Vertical Transportation","category":"Elevators/Lifts"},
    {"department":"Facility Management — Hard Services","category":"Building Fabric"},
    {"department":"Facility Management — Soft Services","category":"Cleaning/Housekeeping"},
    {"department":"Facility Management — HSSE","category":"Safety"},
    {"department":"Technology Group — Network","category":"Internet/Voice"},
    {"department":"Technology Group — Building Technology","category":"Access Control/CCTV/BMS"},
    {"department":"Technology Group — IT Service Desk","category":"IT Support"},
    {"department":"Security","category":"Security"},
    {"department":"Facility Management — FM Operations","category":"General Maintenance"},
    {"department":"Facility Management — Fitout","category":"Finishing/Fitout"},
    {"department":"Facility Management — Transport","category":"Parking/Fleet"},
]
        with st.form("tix_form"):
            c1,c2=st.columns(2)
            with c1:
                loc_sel=st.selectbox("Location*",loc_names)
                cat_sel=st.selectbox("Category*",[c["category"] for c in cats])
            with c2:
                title=st.text_input("Title*")
                rname=st.text_input("Your Name*")
            desc=st.text_area("Description*")
            img=st.file_uploader("Image (Optional)",type=["png","jpg","jpeg"])
            if st.form_submit_button("🎫 Raise Ticket",use_container_width=True):
                if title and desc and rname and loc_sel!="Choose one":
                    cnt=len(DB.get_all("tickets",fc,1000))
                    DB.insert("tickets",{"facility_code":fc,"ticket_number":f"TKT-{fc}-{datetime.now().strftime('%d%H%M%S')}","title":title,"category":cat_sel,"requester_name":rname,"description":desc,"location_building":loc_sel,"status":"open","created_at":datetime.now().isoformat()})
                    st.success("Ticket raised!");st.rerun()
                else:st.error("Please fill all required fields")
    with tab2:
        tix=DB.get_all("tickets",fc,50)
        if tix:
            df=pd.DataFrame(tix)
            tabs=st.tabs(["All","Open","In Progress","Hold","Closed","Completed","Rejected"])
            statuses=["All","open","in_progress","hold","closed","completed","rejected"]
            for idx,tab in enumerate(tabs):
                with tab:
                    if statuses[idx]=="All":d=df
                    else:d=df[df["status"]==statuses[idx]] if "status" in df.columns else df
                    st.metric("Count",len(d))
                    for i,row in d.iterrows():
                        s=row.get("status","open")
                        age=datetime.now()-pd.to_datetime(row.get("created_at",datetime.now())) if row.get("created_at") else timedelta(0)
                        age_str=f"{age.days} Days {age.seconds//3600} Hrs {(age.seconds%3600)//60} Mins"
                        with st.expander(f"{row.get('ticket_number','')} — {row.get('title','')} — {s.upper()} | Age: {age_str}"):
                            st.write(f"**Raised by:** {row.get('requester_name','')} | **Location:** {row.get('location_building','')}")
                            st.write(f"**Category:** {row.get('category','')} | **Description:** {row.get('description','')}")
                            c1,c2,c3=st.columns(3)
                            with c1:
                                if s in ["open","in_progress"]:
                                    if st.button("🔄 In Progress",key=f"prog_{row['id']}"):DB.update("tickets",row["id"],{"status":"in_progress"});st.rerun()
                                    if st.button("⏸️ Hold",key=f"hold_{row['id']}"):DB.update("tickets",row["id"],{"status":"hold"});st.rerun()
                            with c2:
                                if s!="closed":
                                    if st.button("✅ Close",key=f"close_{row['id']}"):DB.update("tickets",row["id"],{"status":"closed","closed_at":datetime.now().isoformat()});st.rerun()
                            with c3:
                                if st.button("❌ Reject",key=f"rej_{row['id']}"):DB.update("tickets",row["id"],{"status":"rejected"});st.rerun()

def page_hd():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 💬 Helpdesk Dashboard — {info.get("full_name",fc)}')
    tix=DB.get_all("tickets",fc,100)
    if tix:
        df=pd.DataFrame(tix)
        c1,c2,c3,c4=st.columns(4)
        with c1:st.metric("🔴 Open",len(df[df["status"]=="open"]) if "status" in df.columns else 0)
        with c2:st.metric("🟡 In Progress",len(df[df["status"]=="in_progress"]) if "status" in df.columns else 0)
        with c3:st.metric("⏸️ Hold",len(df[df["status"]=="hold"]) if "status" in df.columns else 0)
        with c4:st.metric("🟢 Closed",len(df[df["status"]=="closed"]) if "status" in df.columns else 0)
        st.dataframe(df[[c for c in ["ticket_number","title","category","status","requester_name","location_building","created_at"] if c in df.columns]],use_container_width=True,hide_index=True)

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
# USERS PROFILE
# ============================================
def page_up():
    st.markdown("## 👤 Users Profile")
    users=DB.get_users()
    if users:
        st.metric("Total Users",len(users))
        st.dataframe(pd.DataFrame(users)[[c for c in ["name","email","designation","mobile","employee_id"] if c in pd.DataFrame(users).columns]],use_container_width=True,hide_index=True,height=500)
    else:st.info("No users found")

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
    "vm":page_vm,"up":page_up,"rt":page_rt,"hd":page_hd,"fb":page_fb,
    "ac":page_ac,"ic":page_ic,"hot":page_generic,"uc":page_uc,"mis":page_generic,
}

def main():
    inject_css()
    if "facility" not in st.session_state:st.session_state.facility="WTC"
    if "page" not in st.session_state:st.session_state.page="cc"
    topnav();sidebar()
    ROUTER.get(st.session_state.page,page_cc)()

if __name__=="__main__":main()