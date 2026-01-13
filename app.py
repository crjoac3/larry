import streamlit as st
import pandas as pd
import os
import datetime
import json

# --- CONFIGURATION & STYLES ---
st.set_page_config(page_title="WestWorld Inventory Portal (v2.2)", layout="wide", page_icon="🌐")

# --- THEME CONFIGURATION ---
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

def get_theme_css(theme):
    if theme == 'dark':
        return """
<style>
    /* WestWorld Dark Theme */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
        border: 1px solid #4b5563;
    }
    .stSelectbox > div > div > div {
        background-color: #262730;
        color: #ffffff;
    }
    div[data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00e5ff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #374151;
    }
    .stButton > button {
        background-color: #00e5ff;
        color: #000000;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #00b8cc;
        transform: scale(1.02);
    }
</style>
"""
    else:
        # Premium Light Theme
        return """
<style>
    /* Premium Light Theme - Force Text Colors */
    .stApp {
        background-color: #ffffff;
        color: #000000 !important;
    }
    
    /* Text Visibility Fixes */
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: #000000;
    }
    
    /* Specific overrides for sidebar nav which might be tricky */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #000000 !important;
    }
    
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00e5ff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
    }
    div[data-testid="stMetric"] label {
        color: #000000 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #000000 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #dee2e6;
    }
    
    /* Inputs in Light Mode */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #999999 !important; /* Made border darker */
        caret-color: #000000 !important; /* Cursor color */
    }
    .stTextInput input::placeholder {
        color: #333333 !important; /* Placeholder text color */
        opacity: 1 !important;
    }
    
    .stSelectbox > div > div > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #999999 !important; /* Made border darker */
        border-radius: 4px;
    }
    .stSelectbox div, .stSelectbox span {
        color: #000000 !important;
    }
    
    /* Custom Buttons - Force ALL buttons to match specific brand styling */
    .stButton > button, 
    div[data-testid="stForm"] button, 
    button[kind="primary"], 
    button[kind="secondary"] {
        background-color: #00e5ff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 1px solid #000000 !important; /* Added border to buttons for contrast */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }

    /* Hover State for ALL buttons */
    .stButton > button:hover, 
    div[data-testid="stForm"] button:hover,
    button[kind="primary"]:hover, 
    button[kind="secondary"]:hover {
        background-color: #00b8cc !important;
        transform: scale(1.02);
        box-shadow: 0 4px 6px rgba(0,0,0,0.15) !important;
        color: #000000 !important;
    }
    
    /* Fix for Table/Dataframe borders/text */
    [data-testid="stDataFrame"] {
        border: 1px solid #999999 !important;
    }
    
    /* FIX: Top Header Bar */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    
    /* FIX: Expanders (like 'Additional Details') */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #999999 !important;
    }
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #999999 !important;
        border-top: none !important;
    }
    
    /* FIX: Dropdown Menus (Popover options) */
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 1px solid #999999 !important;
    }
    div[data-baseweb="menu"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    /* Aggressive Catch-all for Dropdown Internals */
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] span,
    div[data-baseweb="popover"] div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    li[data-baseweb="option"] {
         color: #000000 !important;
    }
    
    /* FIX: Selectbox Arrow/Caret */
    .stSelectbox svg {
        fill: #000000 !important;
        color: #000000 !important;
    }
    div[data-testid="stSelectbox"] svg {
        fill: #000000 !important;
    }

    /* FIX: Sidebar Collapse Control (The arrow to open sidebar) */
    [data-testid="stSidebarCollapsedControl"] {
        color: #000000 !important;
        fill: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #999999 !important;
        border-radius: 5px !important;
        opacity: 1 !important;
        z-index: 100000 !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: #000000 !important;
        color: #000000 !important;
    }
    
    /* FIX: Radio Buttons */
    div[role="radiogroup"] label {
        color: #000000 !important;
    }
    
    /* FIX: DataFrame (Invert Dark Theme to Light) */
    [data-testid="stDataFrame"] {
        filter: invert(1) hue-rotate(180deg);
        border: 1px solid #cccccc !important;
    }
    
    /* FIX: File Uploader */
    [data-testid="stFileUploader"] {
        background-color: #ffffff;
    }
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f1f3f6 !important;
        border-right: 1px solid #e0e0e0;
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #000000 !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: #f8f9fa !important;
        border: 2px dashed #999999 !important;
        color: #000000 !important;
    }
    /* FIX: Uploaded File List Text (Filename, etc) */
    [data-testid="stFileUploader"] div,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] p {
        color: #000000 !important;
    }
    
    [data-testid="stFileUploader"] section > button {
         color: #000000 !important; /* Browse button text */
    }
    [data-testid="stFileUploader"] svg {
        fill: #000000 !important;
    }
    
    /* FIX: Expanders (Broad Targeting) */
    details {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 5px;
    }
    details > summary {
         background-color: #f8f9fa !important;
         color: #000000 !important;
         border-radius: 5px;
    }
    details > div {
         background-color: #ffffff !important;
         color: #000000 !important;
    }
</style>
"""

st.markdown(get_theme_css(st.session_state['theme']), unsafe_allow_html=True)

# --- CONSTANTS ---
USER_DB_FILE = 'users.csv'
MASTER_INVENTORY_FILE = 'master_inventory.csv'
RECALL_LOG_FILE = 'recall_requests_log.csv'
AUDIT_LOG_FILE = 'audit_requests_log.csv'
SETTINGS_FILE = 'settings.json'
LOGO_FILE = 'logo.jpg'

# --- 🛠️ SELF-HEALING DATABASE FUNCTION ---
def repair_user_database():
    """Checks if users.csv validation state. If broken or old schema, resets or attempts migration."""
    reset_needed = False
    migrated = False
    
    if not os.path.exists(USER_DB_FILE):
        reset_needed = True
    else:
        try:
            df = pd.read_csv(USER_DB_FILE)
            # Check for new 'company', 'email', 'name', 'theme' columns
            req_cols = ['username', 'password', 'role', 'company', 'email', 'name', 'theme']
            
            # Migration Logic: Add missing columns if file exists but schema is old
            if not df.empty:
                save_required = False
                if 'company' not in df.columns:
                    df['company'] = 'WestWorld' # Default fallback
                    save_required = True
                if 'email' not in df.columns:
                    df['email'] = '' # Default empty
                    save_required = True
                if 'name' not in df.columns:
                    df['name'] = df['username'] # Default to username
                    save_required = True
                if 'theme' not in df.columns:
                    df['theme'] = 'light' # Default to Light
                    save_required = True
                
                if save_required:
                    df.to_csv(USER_DB_FILE, index=False)
                    migrated = True
                    print(f"⚠️ System migrated: {USER_DB_FILE} updated with new columns.")
            
            # Re-verify
            if not all(col in df.columns for col in req_cols):
                # If still failing (e.g. empty file), reset
                if not migrated: reset_needed = True
                
        except:
            reset_needed = True

    if reset_needed:
        # Create a fresh file with WestWorld Super Admin
        with open(USER_DB_FILE, 'w') as f:
            f.write("username,password,role,company,email,name,theme\n")
            f.write("admin,admin123,admin,WestWorld,admin@westworld.com,Chris Jakobsen,light\n")
        print(f"⚠️ System repaired: {USER_DB_FILE} was recreated with new schema.")

repair_user_database()

# --- HELPER FUNCTIONS ---
def load_data(file_path, default_cols=None):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Cleanup: Remove UI artifact columns if accidentally saved
            if 'Select' in df.columns:
                df = df.drop(columns=['Select'])
            return df
        except:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def check_login(username, password):
    users = load_data(USER_DB_FILE, ['username', 'password', 'role', 'company', 'email', 'name', 'theme'])
    user_match = users[users['username'] == username]
    
    if not user_match.empty:
        stored_password = str(user_match.iloc[0]['password']).strip()
        if str(password).strip() == stored_password:
            # Return name if exists, else username
            name = user_match.iloc[0]['name'] if 'name' in user_match.columns and pd.notna(user_match.iloc[0]['name']) else username
            theme = user_match.iloc[0]['theme'] if 'theme' in user_match.columns and pd.notna(user_match.iloc[0]['theme']) else 'light'
            return user_match.iloc[0]['role'], user_match.iloc[0]['company'], name, theme
    return None, None, None, None

def get_company_logo(company):
    """Fetches the company logo if exists, else returns the default logo."""
    # Ensure logos directory exists
    if not os.path.exists('logos'):
        os.makedirs('logos')
        
    # Check for company specific logo (supported extensions)
    for ext in ['png', 'jpg', 'jpeg', 'webp']:
        path = f"logos/{company}.{ext}"
        if os.path.exists(path):
            return path
    
    # Fallback to default
    if os.path.exists(LOGO_FILE):
        return LOGO_FILE
    return None

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {
        "email_rules": [],
        "smtp_server": "",
        "smtp_port": 587,
        "smtp_user": "",
        "smtp_pass": ""
    }

def is_global_admin():
    """Helper to check if user has global administrative powers."""
    return st.session_state['user_role'] == 'admin' or (st.session_state['user_role'] == 'manager' and st.session_state['company'] == 'WestWorld')

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def process_recall_request(items_df, user, company):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = items_df.copy()
    if 'Select' in log_entry.columns:
        log_entry = log_entry.drop(columns=['Select'])
    log_entry['Requested By'] = user
    log_entry['Company'] = company # Fallback if not present
    # If the dataframe already has a 'Company' column (e.g. All Companies view), use that.
    # Otherwise use the passed context (e.g. Specific view where we know the target)
    if 'Company' in items_df.columns:
        log_entry['Company'] = items_df['Company']
    else:
        log_entry['Company'] = company
    log_entry['Request Time'] = timestamp
    log_entry['Status'] = 'Pending' # Init status
    
    old_log = load_data(RECALL_LOG_FILE)
    if not old_log.empty and 'Status' not in old_log.columns:
        old_log['Status'] = 'Pending'
        
    new_log = pd.concat([old_log, log_entry], ignore_index=True)
    save_data(new_log, RECALL_LOG_FILE)
    
    # Notify logic: Find matching emails
    settings = load_settings()
    rules = settings.get("email_rules", [])
    
    recipients = set()
    for r in rules:
        trigger_co = r.get("company", "ALL")
        email = r.get("email", "").strip()
        
        if email:
                if trigger_co == "ALL" or trigger_co == company:
                    recipients.add(email)
    
    # Send actual email if SMTP is configured
    recipient_list = list(recipients)
    if recipient_list:
        subject = f"🚨 RECALL REQUEST: {company} - {len(items_df)} Item(s)"
        body = f"A new recall request has been submitted by {user}.\n\n"
        body += "Items Recalled:\n"
        for _, row in items_df.iterrows():
            sn = row.get('Serial Number', 'N/A')
            model = row.get('Model', 'N/A')
            body += f"- SN: {sn} | Model: {model}\n"
        
        body += f"\nView full details in the WestWorld Portal."
        
        send_email_actual(recipient_list, subject, body)
                
    return ", ".join(recipients) if recipients else "No Notification Configured"

def process_audit_request(items_df, user, company, comment):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = items_df.copy()
    if 'Select' in log_entry.columns:
        log_entry = log_entry.drop(columns=['Select'])
    
    log_entry['Requested By'] = user
    log_entry['Company'] = company
    if 'Company' in items_df.columns:
        log_entry['Company'] = items_df['Company']
        
    log_entry['Request Time'] = timestamp
    log_entry['Audit Comment'] = comment
    log_entry['Status'] = 'Pending'
    
    old_log = load_data(AUDIT_LOG_FILE)
    new_log = pd.concat([old_log, log_entry], ignore_index=True)
    save_data(new_log, AUDIT_LOG_FILE)
    return True

def send_email_actual(recipients, subject, body):
    import smtplib
    from email.mime.text import MIMEText
    
    settings = load_settings()
    server = settings.get("smtp_server")
    port = settings.get("smtp_port", 587)
    user = settings.get("smtp_user")
    pwd = settings.get("smtp_pass")
    
    if not all([server, user, pwd]):
        return # Not configured
        
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = user
        msg['To'] = ", ".join(recipients)
        
        with smtplib.SMTP(server, port) as s:
            s.starttls()
            s.login(user, pwd)
            s.sendmail(user, recipients, msg.as_string())
    except Exception as e:
        print(f"❌ SMTP Error: {str(e)}")

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False, 
        'user_role': None, 
        'username': None,
        'company': None,
        'name': None,
        'theme': 'light'
    })

# =======================================================
#                      LOGIN SCREEN
# =======================================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # For login screen, we don't know the company yet until they type it or login.
        # But we can try to guess if they typed something, or just use default.
        logo_to_show = get_company_logo("WestWorld")
        if logo_to_show:
            st.image(logo_to_show, width=300)
        else:
            st.title("🌐 WestWorld Telecom (v2.9)")
            
        st.subheader("Partner Portal Login")
        st.markdown("---")
        
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Log In", type="primary", use_container_width=True):
            role, company, name, theme = check_login(username_input, password_input)
            if role:
                st.session_state.update({
                    'logged_in': True, 
                    'user_role': role, 
                    'username': username_input,
                    'company': company,
                    'name': name,
                    'theme': theme
                })
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

# =======================================================
#                  MAIN DASHBOARD
# =======================================================
else:
    # Sidebar
    with st.sidebar:
        logo_to_show = get_company_logo(st.session_state['company'])
        if logo_to_show:
            st.image(logo_to_show, width=200)
        
        st.markdown(f"### Welcome, {st.session_state.get('name', st.session_state['username'])}")
        st.caption(f"🏢 {st.session_state['company']}")
        st.divider()
        
        # Menu Permissions
        menu_options = ["Inventory Search", "Recall Management", "Audit Management", "My Profile"]
        
        # Super Admin & WestWorld Global Managers
        if is_global_admin():
            menu_options = ["Inventory Search", "Recall Management", "Audit Management", "Inventory Management", "User Management", "Settings", "My Profile"]
        
        # Client Admin / Manager (Can manage their own users and branding)
        elif st.session_state['user_role'] == 'manager':
            menu_options = ["Inventory Search", "Recall Management", "Audit Management", "User Management", "Settings", "My Profile"]
            
        page = st.radio("Navigate", menu_options)
            
        st.divider()
        if st.button("Log Out"):
            st.session_state.update({'logged_in': False, 'user_role': None, 'username': None, 'company': None, 'name': None})
            st.rerun()

    # --- PAGE 1: INVENTORY SEARCH ---
    if page == "Inventory Search":
        # Determine which company's inventory to show
        target_company = st.session_state['company']
        
        # If Global Admin, allow selecting any company
        if is_global_admin():
            users_df = load_data(USER_DB_FILE)
            company_list = ["All Companies"] + list(users_df[users_df['company'] != 'WestWorld']['company'].unique())
            target_company = st.selectbox("Select Client View:", company_list)
        
        st.title(f"📦 Inventory: {target_company}")
        df = load_data(MASTER_INVENTORY_FILE)
        
        if 'owner' in df.columns: 
            # Filter by Company
            if target_company == "All Companies":
                user_df = df.copy()
                user_df.rename(columns={'owner': 'Company'}, inplace=True) # Show Company Column
            else:
                user_df = df[df['owner'] == target_company].drop(columns=['owner'])
            
            if not user_df.empty:
                # View Filters
                filter_mode = st.radio("Show Details:", ["All Equipment Received", "Equipment On-Hand", "Equipment Sold"], horizontal=True)
                display_df = user_df.copy()
                
                if filter_mode == "Equipment On-Hand":
                    if 'Status' in display_df.columns:
                        display_df = display_df[display_df['Status'].astype(str).str.upper().str.contains("ON HAND") | display_df['Status'].isnull()]
                elif filter_mode == "Equipment Sold":
                    if 'Status' in display_df.columns:
                        display_df = display_df[display_df['Status'].astype(str).str.upper().str.contains("SOLD")]

                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Items Count", len(display_df))
                m2.metric("Unique POs", display_df['PO'].nunique() if 'PO' in display_df.columns else 0)
                
                val = "N/A"
                if 'Sales Price' in display_df.columns:
                    try:
                        total_sum = display_df['Sales Price'].replace(r'[\$,]', '', regex=True).astype(float).sum()
                        val = f"${total_sum:,.2f}"
                    except:
                        pass
                m3.metric("Total Asset Value", val)
                
                st.markdown("---")
                
                # Search Bar
                search_term = st.text_input("🔍 Quick Search...", placeholder="Serial Number, Model, PO...")
                if search_term:
                    mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                    display_df = display_df[mask]

                # Interactive Data Table
                if filter_mode == "Equipment On-Hand":
                    st.caption("Select items to request a recall:")
                    if "Select" not in display_df.columns:
                        display_df.insert(0, "Select", False)
                    edited = st.data_editor(
                        display_df, 
                        hide_index=True, 
                        width="stretch", 
                        column_config={
                            "Select": st.column_config.CheckboxColumn(required=True),
                            "Sales Price": st.column_config.NumberColumn(format="$%.2f")
                        }
                    )
                    
                    if not edited[edited.Select].empty:
                        st.markdown("### Recall Request")
                        if st.button(f"🚀 Request Recall for {len(edited[edited.Select])} Item(s)"):
                            # Pass target_company to ensure correct attribution (not just who is logged in)
                            # Pass 'name' for Requested By
                            requester_name = st.session_state.get('name', st.session_state['username'])
                            emails = process_recall_request(edited[edited.Select], requester_name, target_company)
                            st.balloons()
                            st.success(f"✅ Recall request submitted! Notifications sent to: {emails}")
                else:
                    st.dataframe(display_df, hide_index=True, width="stretch")
                
                st.download_button("📥 Export to CSV", display_df.to_csv(index=False).encode('utf-8'), "inventory_export.csv", "text/csv")
            else:
                st.warning(f"No inventory records found for **{target_company}**.")
        else:
            st.info("Master Inventory Database is empty.")

    # --- PAGE 2: RECALL MANAGEMENT ---
    elif page == "Recall Management":
        st.title("🛡️ Recall Management")
        
        recall_df = load_data(RECALL_LOG_FILE)
        
        if recall_df.empty:
            st.info("No active recall requests.")
        else:
            # Init Status
            if 'Status' not in recall_df.columns: recall_df['Status'] = 'Pending'
            
            # Filter Logic
            if not is_global_admin():
                # Client View: See OWN requests only
                view_df = recall_df[recall_df['Company'] == st.session_state['company']]
                st.subheader("Your Request History")
                st.dataframe(view_df.sort_values('Request Time', ascending=False), hide_index=True, width="stretch")
            else:
                # Super Admin View
                st.subheader("Active Recall Queue")
                
                # Active vs History
                queue_mode = st.radio("View", ["Pending actions", "Completed History"], horizontal=True)
                
                if queue_mode == "Pending actions":
                    active_df = recall_df[recall_df['Status'] == 'Pending'].copy()
                    if active_df.empty:
                        st.success("🎉 All caught up! No pending recalls.")
                    else:
                        st.info("Select items to mark as RECEIVED. ⚠️ This will REMOVE them from the Master Inventory.")
                        active_df.insert(0, "Mark Received", False)
                        edited_recall = st.data_editor(active_df, hide_index=True, width="stretch", column_config={"Mark Received": st.column_config.CheckboxColumn(required=True)})
                        
                        if st.button("✅ Confirm Receipt & Remove from Inventory"):
                            to_update = edited_recall[edited_recall['Mark Received']]
                            if not to_update.empty:
                                master_inventory = load_data(MASTER_INVENTORY_FILE)
                                removed_count = 0
                                
                                for idx, row in to_update.iterrows():
                                    # 1. Update Status in Recall Log using UNIQUE INDEX
                                    if idx in recall_df.index:
                                        recall_df.loc[idx, 'Status'] = 'Completed'
                                        recall_df.loc[idx, 'Processed By'] = st.session_state.get('name', st.session_state['username'])
                                    
                                    # 2. Remove from Master Inventory (Granular Removal)
                                    if not master_inventory.empty:
                                        inv_mask = None
                                        
                                        # Strict Match Logic
                                        if 'Serial Number' in row and not pd.isna(row['Serial Number']):
                                            if 'Serial Number' in master_inventory.columns:
                                                inv_mask = master_inventory['Serial Number'] == row['Serial Number']
                                        elif 'PO' in row and not pd.isna(row['PO']):
                                            if 'PO' in master_inventory.columns:
                                                inv_mask = master_inventory['PO'] == row['PO']
                                            
                                        if inv_mask is not None and inv_mask.any():
                                            # FIND ALL COMPLETELY MATCHING ITEMS, BUT ONLY REMOVE ONE
                                            # This prevents wiping out 5 identical items if we only recalled 1
                                            matching_indices = master_inventory[inv_mask].index.tolist()
                                            if matching_indices:
                                                drop_idx = matching_indices[0] # Drop only the first match
                                                master_inventory = master_inventory.drop(drop_idx)
                                                removed_count += 1

                                save_data(recall_df, RECALL_LOG_FILE)
                                save_data(master_inventory, MASTER_INVENTORY_FILE)
                                st.success(f"Updated! {removed_count} items removed from Master Inventory.")
                                st.rerun()
                else:
                    # History
                    history_df = recall_df[recall_df['Status'] == 'Completed'].copy()
                    if history_df.empty:
                        st.info("No completed history.")
                    else:
                        st.write("### Completed Recalls")
                        st.warning("⚠️ 'Restock' will add the item BACK to the Master Inventory and set status to 'Restocked'.")
                        
                        history_df.insert(0, "Restock", False)
                        edited_history = st.data_editor(
                            history_df, 
                            hide_index=True, 
                            width="stretch",
                            column_config={"Restock": st.column_config.CheckboxColumn(required=True)}
                        )
                        
                        if st.button("🔄 Restock Selected Items"):
                            to_restock = edited_history[edited_history['Restock']]
                            if not to_restock.empty:
                                master_inventory = load_data(MASTER_INVENTORY_FILE)
                                restored_count = 0
                                
                                for idx, row in to_restock.iterrows():
                                    # 1. Update Recall Log using UNIQUE INDEX
                                    if idx in recall_df.index:
                                        recall_df.loc[idx, 'Status'] = 'Restocked'
                                        recall_df.loc[idx, 'Processed By'] = st.session_state.get('name', st.session_state['username'])
                                    
                                    # 2. Add back to Master Inventory
                                    clean_row = row.drop(labels=['Mark Received', 'Restock', 'Requested By', 'Company', 'Request Time', 'Status', 'Select', 'Processed By'], errors='ignore')
                                    
                                    # Ensure we have the correct columns for master inventory
                                    # We need to map 'Company' back to 'owner' if it's not present (it was dropped above)
                                    # But wait, original master inventory uses 'owner'.
                                    # The 'row' here comes from history_df which has 'Company' (from process_recall_request).
                                    # So we need to put 'owner' back.
                                    clean_row['owner'] = row['Company']
                                    
                                    # Force 'ON HAND' status if not present (logic assumption)
                                    if 'Status' not in clean_row:
                                        clean_row['Status'] = 'ON HAND'
                                    
                                    master_inventory = pd.concat([master_inventory, pd.DataFrame([clean_row])], ignore_index=True)
                                    restored_count += 1
                                    
                                save_data(recall_df, RECALL_LOG_FILE)
                                save_data(master_inventory, MASTER_INVENTORY_FILE)
                                st.success(f"Restocked {restored_count} items back to inventory!")
                                st.rerun()


    # --- PAGE 3: AUDIT MANAGEMENT ---
    elif page == "Audit Management":
        target_company = st.session_state['company']
        
        # If Global Admin, allow selecting any company
        if is_global_admin():
            users_df = load_data(USER_DB_FILE)
            company_list = ["All Companies"] + list(users_df[users_df['company'] != 'WestWorld']['company'].unique())
            target_company = st.selectbox("Select Client View for Audit:", company_list)
        
        st.title(f"🔍 Audit Management: {target_company}")
        st.info("Select items to request an audit. These items will remain in your inventory.")
        
        df = load_data(MASTER_INVENTORY_FILE)
        
        if 'owner' in df.columns:
            # Filter by Company
            if target_company == "All Companies":
                user_df = df.copy()
                user_df.rename(columns={'owner': 'Company'}, inplace=True)
            else:
                user_df = df[df['owner'] == target_company].drop(columns=['owner'])
            
            if not user_df.empty:
                # Search Bar for focusing audit
                search_term = st.text_input("🔍 Search items to audit...", placeholder="Serial Number, Model, PO...")
                if search_term:
                    mask = user_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                    user_df = user_df[mask]

                # Selection Table
                st.caption("Select items for audit:")
                if "Select" not in user_df.columns:
                    user_df.insert(0, "Select", False)
                
                edited_audit = st.data_editor(
                    user_df,
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "Select": st.column_config.CheckboxColumn(required=True),
                        "Sales Price": st.column_config.NumberColumn(format="$%.2f")
                    }
                )
                
                selected_items = edited_audit[edited_audit.Select]
                
                if not selected_items.empty:
                    st.markdown("---")
                    st.subheader("Audit Details")
                    audit_comment = st.text_area("What is the reason for this audit request?", placeholder="Enter details here...")
                    
                    if st.button(f"🚩 Submit Audit Request for {len(selected_items)} Item(s)", type="primary"):
                        if not audit_comment.strip():
                            st.warning("Please provide a comment for the audit request.")
                        else:
                            requester_name = st.session_state.get('name', st.session_state['username'])
                            process_audit_request(selected_items, requester_name, target_company, audit_comment)
                            st.balloons()
                            st.success("✅ Audit request submitted successfully! Items remain in your inventory search.")
                            st.rerun()
            else:
                st.warning(f"No inventory records found for **{target_company}**.")
        else:
            st.info("Master Inventory Database is empty.")
            
        st.divider()
        st.subheader("📋 Audit History")
        audit_history_df = load_data(AUDIT_LOG_FILE)
        
        if audit_history_df.empty:
            st.info("No audit requests logged yet.")
        else:
            if not is_global_admin():
                # Filter for own company
                display_history = audit_history_df[audit_history_df['Company'] == st.session_state['company']]
            else:
                display_history = audit_history_df
                
            if display_history.empty:
                st.info("No audit history for this company.")
            else:
                st.dataframe(display_history.sort_values('Request Time', ascending=False), hide_index=True, width="stretch")


    # --- PAGE 4: INVENTORY MANAGEMENT (SUPER ADMIN ONLY) ---
    elif page == "Inventory Management":
        st.title("📂 Inventory Management")
        st.info("Upload Master Excel to assign stock to a Client Company.")
        
        users_df = load_data(USER_DB_FILE)
        client_companies = users_df[users_df['company'] != 'WestWorld']['company'].unique()
        
        with st.form("upload_form"):
            target_client_co = st.selectbox("Select Target Client (Company)", client_companies)
            uploaded_file = st.file_uploader("Upload Master Excel File", type=['xlsx'])
            submitted = st.form_submit_button("Start Processing")
            
            if submitted and uploaded_file:
                with st.spinner("Processing Excel..."):
                    try:
                        xls = pd.ExcelFile(uploaded_file)
                        inv_s = next((s for s in xls.sheet_names if "inv" in s.lower() or "hand" in s.lower()), None)
                        if not inv_s: inv_s = xls.sheet_names[0]
                        
                        df_inv = pd.read_excel(uploaded_file, sheet_name=inv_s)
                        if 'Status' not in df_inv.columns: df_inv['Status'] = 'ON HAND'
                        frames = [df_inv]
                        
                        sold_s = next((s for s in xls.sheet_names if "sold" in s.lower()), None)
                        if sold_s:
                            df_sold = pd.read_excel(uploaded_file, sheet_name=sold_s)
                            if 'Status' not in df_sold.columns: df_sold['Status'] = 'SOLD'
                            frames.append(df_sold)
                        
                        new_data = pd.concat(frames, ignore_index=True)
                        new_data['owner'] = target_client_co 
                        
                        master_df = load_data(MASTER_INVENTORY_FILE)
                        if not master_df.empty and 'owner' in master_df.columns:
                            master_df = master_df[master_df['owner'] != target_client_co]
                        
                        final_df = pd.concat([master_df, new_data], ignore_index=True)
                        save_data(final_df, MASTER_INVENTORY_FILE)
                        st.success(f"✅ Successfully assigned {len(new_data)} records to {target_client_co}!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing file: {str(e)}")

    # --- PAGE 5: USER MANAGEMENT ---
    elif page == "User Management":
        st.title("👥 User Administration")
        users_df = load_data(USER_DB_FILE)
        
        # Tabbed interface for better organization
        tab1, tab2, tab3 = st.tabs(["➕ Create User", "✏️ Edit/Reset User", "📋 Existing Users"])
        
        with tab1:
            st.subheader("Create New User")
            with st.form("create_user_form"):
                c1, c2, c3 = st.columns(3)
                c4, c5 = st.columns(2)
                
                with c1: new_u = st.text_input("Username")
                with c2: new_p = st.text_input("Password", type="password")
                with c3: new_email = st.text_input("Email (For Recovery)")
                
                with st.expander("Additional Details", expanded=True):
                    new_name = st.text_input("Full Name", placeholder="e.g. John Doe")

                if is_global_admin():
                    # RBAC Logic: Only Super Admin can create other Admins
                    roles = ["viewer", "manager"]
                    if st.session_state['user_role'] == 'admin':
                        roles.append("admin")
                    
                    with c4: new_r = st.selectbox("Role", roles)
                    with c5: 
                        # Get existing companies from inventory or users
                        inv_data = load_data(MASTER_INVENTORY_FILE)
                        # Robustly get owner column regardless of case
                        o_col = next((c for c in inv_data.columns if c.lower() == 'owner'), None)
                        inv_cos = set(inv_data[o_col].unique()) if o_col else set()
                        known_cos = sorted(list(inv_cos | set(users_df['company'].unique())))
                        new_co = st.selectbox("Company Name", known_cos)
                else:
                    # Managers can create other managers or viewers for their own company
                    with c4: new_r = st.selectbox("Role", ["viewer", "manager"])
                    with c5: new_co = st.text_input("Company", value=st.session_state['company'], disabled=True)
                
                if st.form_submit_button("Save New User"):
                    if new_u and new_p and new_co:
                        if new_u in users_df['username'].values:
                            st.error("User already exists.")
                        else:
                            # Ensure columns exist
                            if 'email' not in users_df.columns: users_df['email'] = ''
                            if 'name' not in users_df.columns: users_df['name'] = ''
                            
                            new_row = pd.DataFrame([[new_u, new_p, new_r, new_co, new_email, new_name]], columns=['username', 'password', 'role', 'company', 'email', 'name'])
                            save_data(pd.concat([users_df, new_row], ignore_index=True), USER_DB_FILE)
                            st.success(f"✅ User {new_u} created!")
                            st.rerun()
                    else:
                        st.warning("Please fill required fields (Username, Password).")

        with tab2:
            st.subheader("Edit User Details / Reset Password")
            viewable_users_edit = users_df
            if not is_global_admin():
                viewable_users_edit = users_df[users_df['company'] == st.session_state['company']]
            
            target_user_edit = st.selectbox("Select User to Edit", sorted(viewable_users_edit['username'].unique()), key="edit_selector")
            
            if target_user_edit:
                user_data = users_df[users_df['username'] == target_user_edit].iloc[0]
                
                with st.form("edit_user_form"):
                    e_name = st.text_input("Full Name", value=user_data.get('name', ''))
                    e_email = st.text_input("Email Address", value=user_data.get('email', ''))
                    
                    # Role/Company change only for Super Admin or if editing someone in company
                    if is_global_admin() and target_user_edit != 'admin':
                        inv_data = load_data(MASTER_INVENTORY_FILE)
                        # Robustly get owner column regardless of case
                        o_col = next((c for c in inv_data.columns if c.lower() == 'owner'), None)
                        inv_cos = set(inv_data[o_col].unique()) if o_col else set()
                        known_cos = sorted(list(inv_cos | set(users_df['company'].unique())))
                        e_comp = st.selectbox("Company", known_cos, index=known_cos.index(user_data['company']) if user_data['company'] in known_cos else 0)
                        
                        roles_list = ['viewer', 'manager', 'admin']
                        e_role = st.selectbox("Role", roles_list, index=roles_list.index(user_data['role']) if user_data['role'] in roles_list else 0)
                    else:
                        e_comp = user_data['company']
                        e_role = user_data['role']
                        st.info(f"Role: **{e_role}** | Company: **{e_comp}**")

                    st.markdown("---")
                    st.write("🔑 **Password Management**")
                    new_pw = st.text_input("Directly Set New Password (Leave blank to keep current)", type="password")
                    
                    if st.form_submit_button("💾 Save Changes & Update User"):
                        # Update the dataframe
                        idx = users_df[users_df['username'] == target_user_edit].index[0]
                        users_df.at[idx, 'name'] = e_name
                        users_df.at[idx, 'email'] = e_email
                        users_df.at[idx, 'company'] = e_comp
                        users_df.at[idx, 'role'] = e_role
                        
                        pw_changed = False
                        if new_pw:
                            users_df.at[idx, 'password'] = new_pw
                            pw_changed = True
                        
                        save_data(users_df, USER_DB_FILE)
                        st.success(f"✅ User {target_user_edit} updated successfully!")
                        
                        # Send email if password changed and SMTP is set
                        if pw_changed and e_email:
                            msg = f"Hello {e_name or target_user_edit},\n\nYour password for the WestWorld Telecom Consignment Portal has been updated by an administrator.\n\nIf you did not request this, please contact support."
                            send_email_actual(e_email, "Account Update Notification", msg)
                            st.info("📧 Update notification sent to user.")
                            
                        st.rerun()

        with tab3:
            st.subheader("Existing Accounts")
            viewable_users_list = users_df
            if not is_global_admin():
                viewable_users_list = users_df[users_df['company'] == st.session_state['company']]
                
            st.dataframe(viewable_users_list[['username', 'role', 'company', 'email', 'name']], hide_index=True, width="stretch")
            
            st.markdown("---")
            col_del, _ = st.columns(2)
            with col_del:
                d_user = st.selectbox("Select User to Delete", viewable_users_list['username'].unique(), key="del_selector")
                if st.button("🗑️ Permanent Delete"):
                    if d_user == 'admin':
                        st.error("⛔ Cannot delete Super Admin.")
                    elif d_user == st.session_state['username']:
                        st.error("⛔ Cannot delete yourself.")
                    else:
                        save_data(users_df[users_df['username'] != d_user], USER_DB_FILE)
                        st.success(f"User {d_user} deleted.")
                        st.rerun()
                    
    # --- PAGE 6: ADMIN SETTINGS ---
    elif page == "Settings":
        st.title("⚙️ Portal Settings")
        
        # --- 🎨 BRANDING SECTION ---
        st.subheader("🎨 Portal Branding")
        st.caption("Customize the portal logo for your company.")
        
        branding_col1, branding_col2 = st.columns([1, 2])
        company_name = st.session_state['company']
        
        with branding_col1:
            current_logo = get_company_logo(company_name)
            if current_logo:
                st.write("**Current Logo:**")
                st.image(current_logo, width=150)
        
        with branding_col2:
            new_logo_file = st.file_uploader("Upload New Logo (PNG/JPG)", type=['png', 'jpg', 'jpeg', 'webp'], key="logo_uploader")
            if new_logo_file:
                # Save new logo
                if not os.path.exists('logos'):
                    os.makedirs('logos')
                
                # Cleanup old logos for this company to avoid conflict
                for ext in ['png', 'jpg', 'jpeg', 'webp']:
                    old_path = f"logos/{company_name}.{ext}"
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                ext = new_logo_file.name.split('.')[-1]
                save_path = f"logos/{company_name}.{ext}"
                with open(save_path, "wb") as f:
                    f.write(new_logo_file.getbuffer())
                st.success(f"✅ Logo updated for {company_name}!")
                st.rerun()

        st.divider()

        # --- 📧 NOTIFICATIONS SECTION (GLOBAL ADMIN ONLY) ---
        if is_global_admin():
            st.subheader("📧 Notification Configuration")
            st.info("Add email recipients below. You can assign emails to specific companies or 'ALL' companies.")
            
            current_settings = load_settings()
            rules = current_settings.get("email_rules", [])
            
            # Display Current Rules
            if rules:
                st.write("#### Active Notification Rules")
                rule_df = pd.DataFrame(rules)
                
                # Formatted display
                c_rule, c_btn = st.columns([3, 1])
                with c_rule:
                    st.dataframe(rule_df, hide_index=True, width="stretch")
                with c_btn:
                    # Simple Delete Logic
                    idx_to_del = st.number_input("Rule Index to Delete", min_value=0, max_value=len(rules)-1, step=1, label_visibility="collapsed")
                    if st.button("🗑️ Delete Rule by Index"):
                        rules.pop(idx_to_del)
                        save_settings({"email_rules": rules})
                        st.rerun()
            else:
                st.warning("No notification rules set. Recall requests will not trigger alerts.")

            st.markdown("---")
            
            # Add New Rule
            st.write("#### Add New Recipient")
            users_df = load_data(USER_DB_FILE)
            # Companies + ALL
            client_companies = ["ALL"] + list(users_df[users_df['company'] != 'WestWorld']['company'].unique())
            
            with st.form("add_rule_form"):
                c1, c2 = st.columns(2)
                with c1: 
                    r_email = st.text_input("Email Address", placeholder="manager@example.com")
                with c2: 
                    r_company = st.selectbox("Applies To Company", client_companies)
                
                if st.form_submit_button("➕ Add Recipient Rule"):
                    if r_email and "@" in r_email:
                        new_rule = {"company": r_company, "email": r_email}
                        # Avoid duplicates
                        if new_rule not in rules:
                            rules.append(new_rule)
                            current_settings["email_rules"] = rules
                            save_settings(current_settings)
                            st.success(f"Added {r_email} for {r_company}")
                            st.rerun()
                        else:
                            st.warning("Rule already exists.")
                    else:
                        st.error("Invalid email address.")

            st.markdown("---")
            st.subheader("🔐 System SMTP Configuration")
            st.caption("Required for actual email notifications.")
            
            with st.form("smtp_form"):
                c1, c2 = st.columns([2, 1])
                with c1: s_host = st.text_input("SMTP Server", value=current_settings.get("smtp_server", ""))
                with c2: s_port = st.number_input("SMTP Port", value=current_settings.get("smtp_port", 587))
                
                c3, c4 = st.columns(2)
                with c3: s_user = st.text_input("SMTP Username (Email)", value=current_settings.get("smtp_user", ""))
                with c4: s_pass = st.text_input("SMTP Password / App Password", type="password", value=current_settings.get("smtp_pass", ""))
                
                if st.form_submit_button("💾 Save SMTP Settings"):
                    current_settings.update({
                        "smtp_server": s_host,
                        "smtp_port": s_port,
                        "smtp_user": s_user,
                        "smtp_pass": s_pass
                    })
                    save_settings(current_settings)
                    st.success("✅ SMTP settings saved!")
                    st.rerun()

    # --- PAGE 7: MY PROFILE ---
    elif page == "My Profile":
        st.title("👤 My Profile")
        users_df = load_data(USER_DB_FILE)
        current_username = st.session_state['username']
        user_idx = users_df[users_df['username'] == current_username].index[0]
        user_row = users_df.iloc[user_idx]
        
        col_prof1, col_prof2 = st.columns(2)
        
        with col_prof1:
            st.subheader("Update Details")
            with st.form("update_profile_form"):
                p_name = st.text_input("Full Name", value=user_row.get('name', ''))
                p_email = st.text_input("Email Address", value=user_row.get('email', ''))
                
                st.markdown("### Theme Settings")
                current_theme = user_row.get('theme', 'light')
                # Use a specific key for the widget to retrieve its value on submit
                new_theme = st.radio("Choose Theme", ["Light", "Dark"], index=0 if current_theme == 'light' else 1, horizontal=True)
                
                if st.form_submit_button("💾 Save Profile"):
                    users_df.at[user_idx, 'name'] = p_name
                    users_df.at[user_idx, 'email'] = p_email
                    
                    # Handle Theme Update
                    selected_theme_val = new_theme.lower()
                    if selected_theme_val != current_theme:
                        users_df.at[user_idx, 'theme'] = selected_theme_val
                        st.session_state['theme'] = selected_theme_val
                        st.success(f"Profile and Theme updated! Switching to {new_theme}...")
                    else:
                        st.success("Profile updated!")
                        
                    save_data(users_df, USER_DB_FILE)
                    st.session_state['name'] = p_name 
                    st.rerun()
                    
        with col_prof2:
            st.subheader("Change Password")
            with st.form("change_password_form"):
                curr_pw = st.text_input("Current Password", type="password")
                new_pw1 = st.text_input("New Password", type="password")
                new_pw2 = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("🔐 Update Password"):
                    if curr_pw != user_row['password']:
                        st.error("Incorrect current password.")
                    elif new_pw1 != new_pw2:
                        st.error("New passwords do not match.")
                    elif not new_pw1:
                        st.warning("New password cannot be empty.")
                    else:
                        users_df.at[user_idx, 'password'] = new_pw1
                        save_data(users_df, USER_DB_FILE)
                        st.success("Password changed successfully!")
                        
                        # Notify user via email
                        send_email_actual(p_email, "Password Changed", "Your password for the WestWorld Telecom Portal has been successfully changed.")
                        st.rerun()
