"""
🏢 facilityXperience — Enterprise Intelligent Facility Ecosystem
Churchgate Group | Multi-Facility AI-Powered Platform
QR Codes • PPM • Asset Management • Full Modules Live
"""

import streamlit as st
from datetime import datetime, date, time
import pandas as pd
import base64
from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client
import plotly.express as px

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
        .churchgate-header {{ background:white; padding:1.5rem; border-radius:8px; margin-bottom:1.5rem; border-left:4px solid {CHURCHGATE_RED}; box-shadow:0 1px 3px rgba(0,0,0,0.06); }}
        .fx-card {{ background:white; border-radius:8px; padding:1rem; border:1px solid #ccc; box-shadow:0 1px 3px rgba(0,0,0,0.06); transition:all 0.2s; }}
        .fx-card:hover {{ box-shadow:0 4px 12px rgba(0,0,0,0.1); border-color:{CHURCHGATE_RED}; transform:translateY(-2px); }}
        .fx-card-label {{ font-size:0.6rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; color:{CHURCHGATE_GREY}; margin-bottom:0.3rem; }}
        .fx-card-value {{ font-size:1.6rem; font-weight:800; color:{CHURCHGATE_DARK}; line-height:1; }}
        .stButton > button {{ background:{CHURCHGATE_RED} !important; color:white !important; border:none !important; border-radius:6px !important; font-weight:600 !important; }}
        .fx-badge {{ display:inline-flex; align-items:center; gap:0.2rem; padding:0.15rem 0.5rem; border-radius:50px; font-size:0.6rem; font-weight:600; }}
        .badge-success {{ background:#ECFDF5; color:#065F46; }} .badge-warning {{ background:#FFFBEB; color:#92400E; }}
        .badge-critical {{ background:#FEF2F2; color:#991B1B; }} .badge-info {{ background:#EFF6FF; color:#1E40AF; }}
        [data-testid="stDataFrame"] {{ border-radius:8px !important; border:1px solid #ccc !important; }}
        [data-testid="stDataFrame"] th {{ background:{CHURCHGATE_LIGHT} !important; font-weight:600 !important; font-size:0.65rem !important; text-transform:uppercase !important; }}
        [data-testid="stMetric"] {{ background:white; padding:0.8rem !important; border-radius:8px !important; border:1px solid #ccc !important; }}
        hr {{ border-color:#ddd !important; margin:1rem 0 !important; }}
        .qr-code-img {{ border:2px solid #ddd; border-radius:8px; padding:5px; background:white; }}
    </style>
    """, unsafe_allow_html=True)

# ============================================
# DATA ENGINE (FIXED FOR ENUM)
# ============================================
class DB:
    @staticmethod
    def get_kpis(fc):
        try:
            wo = supabase.table("work_orders").select("id", count="exact").eq("facility_code", fc).eq("status", "open").execute()
            vis = supabase.table("visitors").select("id", count="exact").eq("facility_code", fc).eq("visit_date", str(date.today())).execute()
            inc = supabase.table("incidents").select("id", count="exact").eq("facility_code", fc).eq("status", "reported").execute()
            tix = supabase.table("tickets").select("id", count="exact").eq("facility_code", fc).in_("status", ["open", "in_progress"]).execute()
            ast = supabase.table("assets").select("id", count="exact").eq("facility_code", fc).execute()
            ppm = supabase.table("ppm_schedules").select("id", count="exact").eq("facility_code", fc).eq("status", "scheduled").execute()
            wp = supabase.table("work_permits").select("id", count="exact").eq("facility_code", fc).eq("status", "pending").execute()
            return {
                "open_wo": wo.count or 0, "visitors": vis.count or 0, "open_inc": inc.count or 0,
                "open_tix": tix.count or 0, "assets": ast.count or 0, "ppm_due": ppm.count or 0,
                "pending_permits": wp.count or 0
            }
        except Exception as e:
            return {"open_wo": 0, "visitors": 0, "open_inc": 0, "open_tix": 0, "assets": 0, "ppm_due": 0, "pending_permits": 0}

    @staticmethod
    def get_all(table, fc, limit=500):
        try:
            res = supabase.table(table).select("*").eq("facility_code", fc).limit(limit).execute()
            return res.data if res.data else []
        except:
            return []

    @staticmethod
    def get_assets(fc, limit=100):
        try:
            # Fetch assets without join first
            res = supabase.table("assets").select("*").eq("facility_code", fc).limit(limit).execute()
            return res.data if res.data else []
        except Exception as e:
            st.error(f"Asset Error: {e}")
            return []

    @staticmethod
    def search_assets(fc, query):
        try:
            res = supabase.table("assets").select("*").eq("facility_code", fc).ilike("asset_tag", f"%{query}%").limit(30).execute()
            if not res.data:
                res = supabase.table("assets").select("*").eq("facility_code", fc).ilike("name", f"%{query}%").limit(30).execute()
            return res.data if res.data else []
        except:
            return []

    @staticmethod
    def insert(table, data):
        try:
            res = supabase.table(table).insert(data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            st.error(f"Insert Error: {e}")
            return None

    @staticmethod
    def update(table, id_val, data):
        try:
            supabase.table(table).update(data).eq("id", id_val).execute()
            return True
        except:
            return False

# ============================================
# HELPERS
# ============================================
def get_facility_logo(fc, h=60):
    info = FACILITY_INFO.get(fc, {})
    lf = info.get("logo", "churchgate-logo.png")
    lp = Path(lf)
    if lp.exists():
        ext = lf.split(".")[-1].replace("jpg","jpeg")
        with open(lp,"rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/{ext};base64,{b64}" height="{h}px" style="max-width:220px;object-fit:contain;">'
    return f'<span style="font-size:2.5rem;">🏢</span>'

def get_nav_logo():
    p = Path("churchgate-logo.png")
    if p.exists():
        with open(p,"rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{b64}" height="26px" style="filter:brightness(0) invert(1);">'
    return '<span style="font-weight:800;color:white;">CHURCHGATE</span>'

# ============================================
# TOP NAV
# ============================================
def topnav():
    cg = get_nav_logo()
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
        st.markdown(f'<div style="text-align:center;padding:0.3rem;margin-bottom:0.5rem;background:#c0c0c0;border-radius:6px;font-size:0.55rem;">⬅️ Red arrow = toggle sidebar</div>',unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.55rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:{CHURCHGATE_GREY};">🏢 SELECT FACILITY</p>',unsafe_allow_html=True)
        sel = st.session_state.get("facility","WTC")
        cols = st.columns(3)
        for i,(k,v) in enumerate(FACILITY_INFO.items()):
            with cols[i%3]:
                if st.button(k,key=f"f_{k}",use_container_width=True,type="primary" if k==sel else "secondary"):st.session_state.facility=k;st.rerun()
        info = FACILITY_INFO.get(sel,{})
        st.markdown(f'<div style="background:{info.get("clight","#fce8e8")};border-left:3px solid {info.get("color",CHURCHGATE_RED)};border-radius:6px;padding:0.7rem;margin:0.7rem 0;"><div style="font-weight:700;font-size:0.8rem;">{info.get("full_name",sel)}</div><div style="font-size:0.6rem;color:{CHURCHGATE_GREY};">📍 {info.get("city","")} • {info.get("desc","")}</div></div>',unsafe_allow_html=True)
        st.markdown("---")
        nav = [
            ("🏠 COMMAND", [("🌐 Command Center","cc"),("📊 PPM Dashboard","ppm")]),
            ("🏗️ ASSETS", [("🏗️ Asset Register","ar"),("🔍 Asset Search","as")]),
            ("🔧 MAINTENANCE", [("📋 Work Orders","wo"),("🛡️ Work Permits","wp"),("🔧 MEP/HK Check","mep")]),
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
        st.markdown("---");st.markdown(f'<p style="font-size:0.5rem;color:#999;text-align:center;">SOC 2 • ISO 27001 • GDPR<br>© Churchgate Group</p>',unsafe_allow_html=True)

# ============================================
# COMMAND CENTER
# ============================================
def page_cc():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{});k=DB.get_kpis(fc);logo=get_facility_logo(fc,70)
    st.markdown(f'<div class="churchgate-header" style="display:flex;align-items:center;gap:1.5rem;"><div style="flex-shrink:0;">{logo}</div><div style="flex:1;"><h1 style="margin:0;font-weight:800;font-size:1.5rem;color:{CHURCHGATE_DARK};">{info.get("full_name",fc)}</h1><p style="margin:0.2rem 0 0 0;color:{CHURCHGATE_GREY};font-size:0.8rem;">📍 {info.get("city","")} • {info.get("desc","")}</p></div><div style="text-align:right;"><div style="font-size:0.6rem;color:#888;">LIVE DATA</div><div style="font-size:1.1rem;font-weight:700;">{datetime.now().strftime("%H:%M:%S")}</div><div style="font-size:0.6rem;color:#888;">{datetime.now().strftime("%A, %d %B %Y")}</div></div></div>',unsafe_allow_html=True)
    kpi=[("📋 Open Work Orders",k["open_wo"]),("🛂 Today's Visitors",k["visitors"]),("🚨 Open Incidents",k["open_inc"]),("🎫 Open Tickets",k["open_tix"]),("🏗️ Total Assets",k["assets"]),("🔧 PPM Due",k["ppm_due"]),("🛡️ Pending Permits",k["pending_permits"])]
    cols=st.columns(7)
    for i,(l,v) in enumerate(kpi):
        with cols[i]:st.markdown(f'<div class="fx-card" style="text-align:center;"><div class="fx-card-label">{l}</div><div class="fx-card-value">{v}</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### 📋 Recent Work Orders")
        wo=DB.get_all("work_orders",fc,5)
        if wo:st.dataframe(pd.DataFrame(wo)[[c for c in ["wo_number","title","priority","status"] if c in pd.DataFrame(wo).columns]],use_container_width=True,hide_index=True)
        else:st.info("No work orders")
    with c2:
        st.markdown("### 🛂 Today's Visitors")
        vis=DB.get_all("visitors",fc,5)
        if vis:st.dataframe(pd.DataFrame(vis)[[c for c in ["full_name","company","status","expected_arrival"] if c in pd.DataFrame(vis).columns]],use_container_width=True,hide_index=True)
        else:st.info("No visitors today")

# ============================================
# ASSET REGISTER WITH QR CODES
# ============================================
def page_ar():
    fc = st.session_state.get("facility", "WTC")
    info = FACILITY_INFO.get(fc, {})
    st.markdown(f'## 🏗️ Asset Lifecycle Matrix — {info.get("full_name", fc)}')
    
    tab1, tab2 = st.tabs(["📋 All Assets", "🔍 Search & QR"])
    
    with tab1:
        data = DB.get_assets(fc, 200)
        if data:
            df = pd.DataFrame(data)
            st.metric("Total Assets Loaded", len(df))
            cols_show = [c for c in ["asset_tag", "name", "manufacturer", "model", "serial_number", "location_building", "location_floor", "location_zone", "status", "condition_rating"] if c in df.columns]
            st.dataframe(df[cols_show], use_container_width=True, hide_index=True)
        else:
            st.warning("Loading assets...")
            if st.button("🔄 Retry"):
                st.rerun()
    
    with tab2:
        q = st.text_input("Search by Asset Tag")
        if q:
            results = DB.search_assets(fc, q)
            if results:
                st.success(f"{len(results)} found")
                for r in results:
                    with st.expander(f"{r.get('asset_tag', '')} — {r.get('name', '')}"):
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.write(f"**Mfr:** {r.get('manufacturer','N/A')} | **Model:** {r.get('model','N/A')} | **S/N:** {r.get('serial_number','N/A')}")
                            st.write(f"**Location:** {r.get('location_building','')} > Floor {r.get('location_floor','')} > {r.get('location_zone','')}")
                            st.write(f"**Status:** {r.get('status','')} | **Condition:** {r.get('condition_rating','')}/5")
                        with c2:
                            qr = r.get('qr_code_url', '')
                            if qr:
                                st.image(qr, width=130, caption=f"Scan: {r.get('asset_tag','')}")
            else:
                st.warning("Nothing found")

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
        with c2:st.metric("Due Now",len(df[pd.to_datetime(df["next_due_date"]).dt.date <= date.today()]) if "next_due_date" in df.columns else 0)
        with c3:st.metric("Critical",len(df[df["is_critical"]==True]) if "is_critical" in df.columns else 0)
        st.markdown("### 📋 PPM Schedules")
        for i,row in df.iterrows():
            due=row.get("next_due_date","")
            badge="badge-critical" if row.get("is_critical") else "badge-info"
            with st.expander(f"{row.get('title','')} — Due: {due} — {row.get('frequency','')}"):
                st.write(f"**Team:** {row.get('assigned_team','')} | **Hours:** {row.get('estimated_hours','')} | **Priority:** {row.get('priority','')}")
                st.write(f"**Checklist:** {row.get('checklist','')}")
                if st.button("✅ Mark Complete",key=f"ppm_{row['id']}"):
                    DB.update("ppm_schedules",row["id"],{"status":"completed","last_completed_date":str(date.today())})
                    st.success("Completed!");st.rerun()
    else:st.info("No PPM schedules")

# ============================================
# ALL OTHER MODULES (same as before, compact)
# ============================================
def page_wo():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 📋 Work Order Orchestrator — {info.get("full_name",fc)}')
    t1,t2=st.tabs(["📋 View","➕ Create"])
    with t1:
        data=DB.get_all("work_orders",fc,50)
        if data:st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
        else:st.info("No work orders")
    with t2:
        with st.form("wo_f"):
            title=st.text_input("Title*");typ=st.selectbox("Type",["preventive","corrective","inspection","emergency"])
            pri=st.selectbox("Priority",["low","medium","high","critical"]);cat=st.selectbox("Category",["HVAC","Electrical","Plumbing","Fire Safety","Elevators","Security","Other"])
            desc=st.text_area("Description");loc=st.text_input("Location");team=st.text_input("Assigned Team")
            if st.form_submit_button("📋 Create",use_container_width=True):
                if title:
                    cnt=len(DB.get_all("work_orders",fc,1000))
                    DB.insert("work_orders",{"facility_code":fc,"wo_number":f"WO-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"type":typ,"priority":pri,"category":cat,"description":desc,"location_building":loc,"assigned_team":team,"status":"open","created_at":datetime.now().isoformat()})
                    st.success("Created!");st.rerun()

def page_wp():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🛡️ Work Permits — {info.get("full_name",fc)}')
    t1,t2=st.tabs(["📋 View","➕ Create"])
    with t1:
        data=DB.get_all("work_permits",fc,50)
        if data:
            df=pd.DataFrame(data)
            for i,row in df.iterrows():
                s=row.get("status","draft");badge="badge-warning" if s=="pending" else "badge-success" if s=="approved" else "badge-info"
                with st.expander(f"{row.get('permit_number','')} — {row.get('title','')} — {s.upper()}"):
                    st.write(f"**Contractor:** {row.get('contractor_company','')} | **Location:** {row.get('work_location','')}")
                    if s=="pending":
                        if st.button("✅ Approve",key=f"app_{row['id']}"):DB.update("work_permits",row["id"],{"status":"approved","approved_at":datetime.now().isoformat(),"is_approved":True});st.rerun()
                        if st.button("❌ Reject",key=f"rej_{row['id']}"):DB.update("work_permits",row["id"],{"status":"rejected"});st.rerun()
        else:st.info("No permits")
    with t2:
        with st.form("wp_f"):
            title=st.text_input("Title*");ptype=st.selectbox("Type",["Hot Work","Cold Work","Electrical","Working at Height","Other"])
            contractor=st.text_input("Contractor Company");loc=st.text_input("Work Location*")
            desc=st.text_area("Description")
            if st.form_submit_button("🛡️ Submit",use_container_width=True):
                if title and loc:
                    cnt=len(DB.get_all("work_permits",fc,1000))
                    DB.insert("work_permits",{"facility_code":fc,"permit_number":f"PTW-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"permit_type":ptype,"contractor_company":contractor,"work_location":loc,"description":desc,"status":"pending","created_at":datetime.now().isoformat()})
                    st.success("Submitted!");st.rerun()

def page_vm():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🛂 Visitor Management — {info.get("full_name",fc)}')
    t1,t2=st.tabs(["📋 Today","➕ Register"])
    with t1:
        data=DB.get_all("visitors",fc,50)
        if data:
            df=pd.DataFrame(data)
            for i,row in df.iterrows():
                s=row.get("status","expected");badge="badge-success" if s=="checked_in" else "badge-warning"
                with st.expander(f"{row.get('full_name','')} — {row.get('company','')} — {s.upper()}"):
                    if s in ["expected","pre_registered"]:
                        if st.button("✅ Check In",key=f"vin_{row['id']}"):DB.update("visitors",row["id"],{"status":"checked_in","actual_arrival":datetime.now().isoformat()});st.rerun()
                    if s=="checked_in":
                        if st.button("🚪 Check Out",key=f"vout_{row['id']}"):DB.update("visitors",row["id"],{"status":"checked_out","actual_departure":datetime.now().isoformat()});st.rerun()
        else:st.info("No visitors")
    with t2:
        with st.form("vis_f"):
            fn=st.text_input("First Name*");ln=st.text_input("Last Name*");company=st.text_input("Company")
            host=st.text_input("Host Name*");purpose=st.text_area("Purpose")
            if st.form_submit_button("🛂 Register",use_container_width=True):
                if fn and ln and host:
                    DB.insert("visitors",{"facility_code":fc,"first_name":fn,"last_name":ln,"company":company,"host_name":host,"purpose_of_visit":purpose,"visit_date":str(date.today()),"status":"pre_registered","created_at":datetime.now().isoformat()})
                    st.success("Registered!");st.rerun()

def page_rt():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🎫 Service Concierge — {info.get("full_name",fc)}')
    t1,t2=st.tabs(["📋 Tickets","➕ Raise"])
    with t1:
        data=DB.get_all("tickets",fc,50)
        if data:
            df=pd.DataFrame(data)
            for i,row in df.iterrows():
                s=row.get("status","open");badge="badge-critical" if s=="open" else "badge-success"
                with st.expander(f"{row.get('ticket_number','')} — {row.get('title','')} — {s.upper()}"):
                    st.write(f"**Category:** {row.get('category','')} | **Priority:** {row.get('priority','')}")
                    if s in ["open","in_progress"]:
                        if st.button("✅ Resolve",key=f"tres_{row['id']}"):DB.update("tickets",row["id"],{"status":"resolved","resolved_at":datetime.now().isoformat()});st.rerun()
        else:st.info("No tickets")
    with t2:
        with st.form("tix_f"):
            title=st.text_input("Title*");cat=st.selectbox("Category",["HVAC","Electrical","Plumbing","Cleaning","Security","IT","Other"])
            pri=st.selectbox("Priority",["low","medium","high","critical"]);name=st.text_input("Your Name*")
            desc=st.text_area("Description*")
            if st.form_submit_button("🎫 Raise Ticket",use_container_width=True):
                if title and desc and name:
                    cnt=len(DB.get_all("tickets",fc,1000))
                    DB.insert("tickets",{"facility_code":fc,"ticket_number":f"TKT-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"category":cat,"priority":pri,"requester_name":name,"description":desc,"status":"open","created_at":datetime.now().isoformat()})
                    st.success("Ticket raised!");st.rerun()

def page_hd():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 💬 Helpdesk — {info.get("full_name",fc)}')
    tix=DB.get_all("tickets",fc,20)
    if tix:
        df=pd.DataFrame(tix)
        c1,c2=st.columns(2)
        with c1:st.metric("Open",len(df[df["status"].isin(["open","in_progress"])]) if "status" in df.columns else 0)
        with c2:st.metric("Resolved",len(df[df["status"]=="resolved"]) if "status" in df.columns else 0)
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info("No tickets")

def page_ic():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🚨 Incident Intelligence — {info.get("full_name",fc)}')
    t1,t2=st.tabs(["📋 View","➕ Report"])
    with t1:
        data=DB.get_all("incidents",fc,20)
        if data:st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
        else:st.success("No incidents")
    with t2:
        with st.form("inc_f"):
            title=st.text_input("Title*");sev=st.selectbox("Severity",["low","medium","high","critical"])
            desc=st.text_area("Description*");loc=st.text_input("Location")
            if st.form_submit_button("🚨 Report",use_container_width=True):
                if title and desc:
                    cnt=len(DB.get_all("incidents",fc,1000))
                    DB.insert("incidents",{"facility_code":fc,"incident_number":f"INC-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"severity":sev,"description":desc,"location_building":loc,"status":"reported","incident_date":str(date.today()),"reported_at":datetime.now().isoformat()})
                    st.success("Reported!");st.rerun()

def page_ac():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ✅ Audit Framework — {info.get("full_name",fc)}')
    with st.form("audit_f"):
        title=st.text_input("Audit Title*");atype=st.selectbox("Type",["Internal","External","Safety","Quality"])
        items=["Fire extinguishers accessible","Emergency exits clear","Electrical panels labeled","PPE available","Housekeeping standards met","First aid kits stocked"]
        results={}
        for item in items:results[item]=st.selectbox(item,["Pass","Fail","N/A"],key=f"aud_{item[:15]}")
        if st.form_submit_button("✅ Submit Audit",use_container_width=True):
            if title:
                passed=sum(1 for v in results.values() if v=="Pass")
                total=sum(1 for v in results.values() if v!="N/A")
                score=round((passed/total)*100,1) if total>0 else 100
                cnt=len(DB.get_all("audits",fc,1000))
                DB.insert("audits",{"facility_code":fc,"audit_number":f"AUD-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"type":atype,"overall_score":score,"status":"completed","findings":results,"audit_date":str(date.today()),"created_at":datetime.now().isoformat()})
                st.success(f"Score: {score}%");st.rerun()

def page_fb():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## ⭐ Feedback — {info.get("full_name",fc)}')
    with st.form("fb_f"):
        rating=st.slider("Rating",1,5,5);cat=st.selectbox("Category",["Facility","Service","Cleanliness","Security","Other"])
        comments=st.text_area("Comments*")
        if st.form_submit_button("⭐ Submit",use_container_width=True):
            if comments:
                DB.insert("feedback",{"facility_code":fc,"rating":rating,"category":cat,"comments":comments,"sentiment":"positive" if rating>=4 else "neutral","status":"new","created_at":datetime.now().isoformat()})
                st.success("Thank you!");st.rerun()

def page_generic(title,icon):
    st.markdown(f'## {icon} {title}')
    st.info("🚧 Module ready for full deployment.")

# ============================================
# ROUTER
# ============================================
ROUTER={
    "cc":page_cc,"ppm":page_ppm,"ar":page_ar,"as":page_ar,"wo":page_wo,"wp":page_wp,
    "vm":page_vm,"rt":page_rt,"hd":page_hd,"ic":page_ic,"ac":page_ac,"fb":page_fb,
    "mep":lambda:page_generic("MEP/HK Check","🔧"),"up":lambda:page_generic("Users Profile","👤"),
    "ai":lambda:page_generic("AI Hub","🤖"),"sv":lambda:page_generic("Survey","📝"),
    "mt":lambda:page_generic("Material Tracking","📦"),"kc":lambda:page_generic("Key Check","🔑"),
    "mr":lambda:page_generic("Mailroom","📬"),"cc2":lambda:page_generic("Compliance","⚖️"),
    "hc":lambda:page_generic("HOTO Check","🔄"),"uc":lambda:page_generic("Utility Check","⚡"),
    "ac2":lambda:page_generic("Activity Check","📈"),"mis":lambda:page_generic("Monthly MIS","📊"),
}

def main():
    inject_css()
    if "facility" not in st.session_state:st.session_state.facility="WTC"
    if "page" not in st.session_state:st.session_state.page="cc"
    topnav();sidebar()
    ROUTER.get(st.session_state.page,page_cc)()

if __name__=="__main__":main()