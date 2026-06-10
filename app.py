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
# WORK PERMIT (4-Level Approval)
# ============================================
def page_wp():
    fc=st.session_state.get("facility","WTC");info=FACILITY_INFO.get(fc,{})
    st.markdown(f'## 🛡️ Permit-to-Work System — {info.get("full_name",fc)}')
    tab1,tab2=st.tabs(["📋 All Permits","➕ Raise Permit"])
    with tab1:
        # Date filter
        c1,c2=st.columns(2)
        with c1:start_d=st.date_input("From",date.today()-timedelta(days=60))
        with c2:end_d=st.date_input("To",date.today())
        wp=DB.get_all("work_permits",fc,200)
        if wp:
            df=pd.DataFrame(wp)
            c1,c2,c3,c4=st.columns(4)
            with c1:st.metric("Total",len(df))
            with c2:st.metric("Pending",len(df[df["status"]=="pending"]) if "status" in df.columns else 0)
            with c3:st.metric("Approved",len(df[df["status"]=="approved"]) if "status" in df.columns else 0)
            with c4:st.metric("Rejected",len(df[df["status"]=="rejected"]) if "status" in df.columns else 0)
            st.markdown("---")
            for i,row in df.iterrows():
                s=row.get("status","draft")
                badge=status_badge(s)
                with st.expander(f"{row.get('permit_number','')} — {row.get('title','')} — {badge}",expanded=(s=="pending")):
                    c1,c2,c3=st.columns([2,1,1])
                    with c1:
                        st.write(f"**Raised by:** {row.get('raised_by_name','')} ({row.get('raised_by_designation','')})")
                        st.write(f"**Type:** {row.get('permit_type','')} | **Dept:** {row.get('department','')}")
                        st.write(f"**Location:** {row.get('work_location','')}")
                        st.write(f"**Period:** {row.get('start_datetime','')} → {row.get('end_datetime','')}")
                        if row.get("review_l1_name"):st.success(f"✅ L1 Review: {row['review_l1_name']} — {row.get('review_l1_at','')}")
                        if row.get("review_l2_name"):st.success(f"✅ L2 Review: {row['review_l2_name']} — {row.get('review_l2_at','')}")
                        if row.get("approved_by_name"):st.success(f"✅ Approved: {row['approved_by_name']} — {row.get('approved_at','')}")
                        if row.get("rejected_reason"):st.error(f"❌ Rejected: {row.get('rejected_reason','')}")
                    with c2:
                        if s=="pending":
                            if st.button("✅ L1 Review",key=f"l1_{row['id']}"):
                                DB.update("work_permits",row["id"],{"status":"in_review","review_l1_name":"Vishwajeet Kamble","review_l1_at":datetime.now().isoformat()})
                                st.rerun()
                            if st.button("✅ L2 Review",key=f"l2_{row['id']}"):
                                DB.update("work_permits",row["id"],{"status":"in_review","review_l2_name":"Augustine Oleh","review_l2_at":datetime.now().isoformat()})
                                st.rerun()
                    with c3:
                        if s in ["pending","in_review"]:
                            if st.button("✅ Approve",key=f"app_{row['id']}"):
                                DB.update("work_permits",row["id"],{"status":"approved","approved_by_name":"David Effiong","approved_at":datetime.now().isoformat()})
                                st.rerun()
                            if st.button("❌ Reject",key=f"rej_{row['id']}"):
                                DB.update("work_permits",row["id"],{"status":"rejected","rejected_at":datetime.now().isoformat(),"rejected_reason":"Does not meet safety requirements"})
                                st.rerun()
        else:st.info("No work permits")
    with tab2:
        with st.form("wp_form"):
            st.markdown("### Raise New Work Permit")
            c1,c2=st.columns(2)
            with c1:
                title=st.text_input("Title*");ptype=st.selectbox("Permit Type",["General","Hot Work","Confined Space","Height Work","ELV Systems","Electrical","Energy Isolation"])
                dept=st.selectbox("Department*",[
    # Engineering (DEP-01)
    "Engineering — Civil & Structural",
    "Engineering — Electrical",
    "Engineering — HVAC",
    "Engineering — Plumbing",
    "Engineering — Vertical Transportation (Lifts)",
    "Engineering — Fire Fighting",
    "Engineering — Utilities & Energy",
    "Engineering — Fabrication & Foundry",
    "Engineering — Design & Specification",
    # Facility Management (DEP-02)
    "Facility Management — Hard Services (Building Fabric)",
    "Facility Management — Soft Services (Housekeeping)",
    "Facility Management — Soft Services (Waste Management)",
    "Facility Management — Soft Services (Front of House)",
    "Facility Management — Soft Services (Landscaping)",
    "Facility Management — Transport & Fleet",
    "Facility Management — First Aid & Clinical",
    "Facility Management — FM Operations & Helpdesk",
    "Facility Management — HSSE Safety & Compliance",
    "Facility Management — HSSE Risk & BCP",
    "Facility Management — HSSE Incident Investigation",
    "Facility Management — Fitout Works & Finishing",
    # Technology Group (DEP-03)
    "Technology Group — Network & Connectivity",
    "Technology Group — IT Service Desk",
    "Technology Group — ERP & Business Systems",
    "Technology Group — Cloud & Infrastructure",
    "Technology Group — Building Technology (BMS/CCTV/ACS)",
    "Technology Group — Software Development",
    "Technology Group — AI & Innovation",
    "Technology Group — Cybersecurity",
    # Security (DEP-04)
    "Security — Man Guarding Operations",
    "Security — Command Center (24/7)",
    "Security — Gatehouse & Access Control",
    "Security — Executive Protection",
    # Procurement (DEP-05)
    "Procurement — Strategic Sourcing",
    "Procurement — Contract Management",
    "Procurement — Purchase & Requisition",
    # Central Stores (DEP-06)
    "Central Stores — Inventory Management",
    "Central Stores — Goods Inwards & QA",
    "Central Stores — Critical Spares",
    # Sales & Marketing (DEP-08)
    "Sales & Marketing — Business Development",
    "Sales & Marketing — Bid & Tender Management",
    # External Contractors
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
                rname=st.text_input("Your Name*");rdesig=st.text_input("Your Designation")
            with c2:
                loc=st.text_input("Work Location*");cont=st.text_input("Contractor Company (if applicable)")
                sd=st.date_input("Start Date");st_time=st.time_input("Start Time",time(8,0))
                ed=st.date_input("End Date");et_time=st.time_input("End Time",time(17,0))
            desc=st.text_area("Description of Work")
            if st.form_submit_button("🛡️ Submit Permit",use_container_width=True):
                if title and loc and rname:
                    cnt=len(DB.get_all("work_permits",fc,1000))
                    DB.insert("work_permits",{"facility_code":fc,"permit_number":f"PTW-{fc}-{datetime.now().year}-{str(cnt+1).zfill(4)}","title":title,"permit_type":ptype,"department":dept,"raised_by_name":rname,"raised_by_designation":rdesig,"contractor_company":cont,"work_location":loc,"start_datetime":f"{sd}T{st_time}","end_datetime":f"{ed}T{et_time}","description":desc,"status":"pending","created_at":datetime.now().isoformat()})
                    st.success("Permit submitted for approval!");st.rerun()

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