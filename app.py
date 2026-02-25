import streamlit as st
import pandas as pd
import os
import datetime
import json
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION & STYLES ---
st.set_page_config(page_title="WestWorld Inventory Portal (v2.2)", layout="wide", page_icon="🌐")

# --- THEME CONFIGURATION ---
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

def get_theme_css(theme):
    if theme == 'dark':
        return """
<style>
    /* WestWorld Premium Dark Theme */
    .stApp {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Text Visibility Fixes */
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: #fafafa;
    }
    
    /* Specific overrides for sidebar nav */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #fafafa !important;
    }
    
    .stTextInput > div > div > input {
        background-color: #262730 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #4b5563 !important;
        caret-color: #ffffff !important;
    }
    .stSelectbox > div > div > div {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #4b5563 !important;
    }
    .stSelectbox div, .stSelectbox span {
        color: #ffffff !important;
    }
    div[data-testid="stMetric"] {
        background-color: #1f2937 !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border-left: 5px solid #00e5ff !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #374151 !important;
    }
    
    /* Custom Buttons - Force ALL buttons to match specific brand styling */
    .stButton > button, 
    div[data-testid="stForm"] button, 
    button[kind="primary"], 
    button[kind="secondary"] {
        background-color: #00e5ff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 1px solid #00b8cc !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover, 
    div[data-testid="stForm"] button:hover,
    button[kind="primary"]:hover, 
    button[kind="secondary"]:hover {
        background-color: #00b8cc !important;
        transform: scale(1.02);
        box-shadow: 0 4px 6px rgba(0,0,0,0.15) !important;
        color: #000000 !important;
    }
    
    /* Radio Buttons / Theme Selector */
    div[role="radiogroup"] label {
        color: #fafafa !important;
    }
    
    /* Header Bar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* FIX: Canvas Table/Dataframe Background in Dark Mode */
    /* st.dataframe ignores CSS colors since it's Canvas. We MUST invert the light mode table visually. */
    [data-testid="stDataFrame"] {
        filter: invert(1) hue-rotate(180deg) !important;
        border: 1px solid #4b5563 !important;
    }
    
    /* REMOVE "SELECT ALL" TOGGLE FROM COLUMN SELECTOR */
    div[data-baseweb="popover"] label:first-of-type {
        display: none !important;
    }
</style>
"""
    else:
        # Premium Light Theme
        return """
<style>
    /* Premium Light Theme - Soft Background, Dark Text */
    .stApp {
        background-color: #f4f6f9 !important; /* Soft slate/off-white background instead of blinding white */
        color: #111111 !important;
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
    
    /* Fix for Table/Dataframe borders/text */
    [data-testid="stDataFrame"] {
        border: 1px solid #999999 !important;
    }
    
    /* FIX: Dropdown & Data Grid Active Selection Text Contrast */
    div.gdg-portal *,
    li[role="option"],
    li[role="option"] *,
    div[data-baseweb="menu"] *,
    div[data-baseweb="popover"] * {
        color: #000000 !important;
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
    
    /* FIX: Top Header Bar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* FIX: Expanders (like 'Additional Details') */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px 6px 0 0 !important;
    }
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        border-top: none !important;
        border-radius: 0 0 6px 6px !important;
    }
    
    /* REMOVE "SELECT ALL" TOGGLE FROM COLUMN SELECTOR */
    div[data-baseweb="popover"] label:first-of-type {
        display: none !important;
    }
    
    /* FIX: Selectbox Arrow/Caret */
    .stSelectbox svg {
        fill: #000000 !important;
        color: #000000 !important;
    }
    div[data-testid="stSelectbox"] svg {
        fill: #000000 !important;
    }

    /* FIX: Sidebar Collapse Control */
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
    
    /* FIX: Text Area */
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
        border: 1px solid #999999 !important;
    }
    div[data-testid="stTextArea"] label {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* FIX: File Uploader Text */
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] small, 
    [data-testid="stFileUploader"] div,
    [data-testid="stFileUploader"] p {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    [data-testid="stFileUploader"] {
        background-color: #ffffff;
    }
    [data-testid="stFileUploader"] section {
        background-color: #f8f9fa !important;
        border: 2px dashed #999999 !important;
        color: #000000 !important;
    }
    [data-testid="stFileUploader"] section > button {
         color: #000000 !important; /* Browse button text */
    }
    [data-testid="stFileUploader"] svg {
        fill: #000000 !important;
    }
    
    /* FIX: Radio Buttons */
    div[role="radiogroup"] label {
        color: #000000 !important;
    }
    
    /* FIX: DataFrame Toolbar Overlay Icons */
    [data-testid="stElementToolbar"], .stElementToolbar {
        background-color: transparent !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
    }
    [data-testid="stElementToolbar"] button,
    .stElementToolbar button,
    [data-testid="stElementToolbar"] button:hover,
    .stElementToolbar button:hover {
        color: #000000 !important;
        background-color: transparent !important;
    }
    [data-testid="stElementToolbar"] svg,
    .stElementToolbar svg,
    [data-testid="stElementToolbar"] button:hover svg,
    .stElementToolbar button:hover svg {
        fill: #000000 !important;
        stroke: #000000 !important;
        color: #000000 !important;
    }
    
    /* FIX: Tooltips */
    div[data-baseweb="tooltip"] {
        background-color: #f8f9fa !important;
        border: 1px solid #cccccc !important;
    }
    div[data-baseweb="tooltip"] * {
        color: #000000 !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #e8eaed !important;
        border-right: 1px solid #d0d0d0;
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
# Use environment variables for Docker compatibility (mounted to /data)
USER_DB_FILE = os.getenv('USER_DB_FILE', 'users.csv')
MASTER_INVENTORY_FILE = os.getenv('MASTER_INVENTORY_FILE', 'master_inventory.csv')
RECALL_LOG_FILE = os.getenv('RECALL_LOG_FILE', 'recall_requests_log.csv')
AUDIT_LOG_FILE = os.getenv('AUDIT_LOG_FILE', 'audit_requests_log.csv')
SETTINGS_FILE = os.getenv('SETTINGS_FILE', 'settings.json')
LOGO_FILE = os.getenv('LOGO_FILE', 'logo.jpg')
COMPANIES_FILE = os.getenv('COMPANIES_FILE', 'companies.csv')

# --- 🛠️ SELF-HEALING DATABASE FUNCTION ---
def repair_user_database():
    """Checks if users.csv validation state. If broken or old schema, resets or attempts migration."""
    # 1. Repair Users DB
    reset_needed = False
    
    if not os.path.exists(USER_DB_FILE):
        reset_needed = True
    else:
        try:
            df = pd.read_csv(USER_DB_FILE)
            # Check for old schema
            req_cols = ['username', 'password', 'role', 'company', 'email', 'name', 'theme']
            
            save_required = False
            if 'email' not in df.columns:
                df['email'] = ''
                save_required = True
            if 'name' not in df.columns:
                df['name'] = df['username'] # Default to username
                save_required = True
            if 'theme' not in df.columns:
                df['theme'] = 'light'
                save_required = True
                
            if save_required:
                df.to_csv(USER_DB_FILE, index=False)
                print("✅ Schema updated with missing columns.")
                
        except:
            reset_needed = True

    if reset_needed:
        # Create a fresh file with WestWorld Super Admin
        with open(USER_DB_FILE, 'w') as f:
            f.write("username,password,role,company,email,name,theme\n")
            f.write("admin,admin123,admin,WestWorld,admin@westworld.com,Chris Jakobsen,light\n")
        print(f"⚠️ System repaired: {USER_DB_FILE} was recreated with new schema.")

    # 2. Repair/Migrate Companies DB
    companies_exist = set()
    if os.path.exists(COMPANIES_FILE):
        try:
            c_df = pd.read_csv(COMPANIES_FILE)
            
            # Schema Update for Companies
            missing_cols = []
            for col in ['address', 'contact_name', 'contact_email', 'contact_phone', 'logo_path']:
                if col not in c_df.columns:
                    c_df[col] = "" # Add missing column with empty string
                    missing_cols.append(col)
            
            if missing_cols:
                c_df.to_csv(COMPANIES_FILE, index=False)
                print(f"✅ Companies DB updated with new columns: {missing_cols}")
            
            # --- DATA MIGRATION: Ensure WestWorld has details ---
            # This ensures that even if pulling from a stale CSV on deployment, 
            # the app corrects the data on startup.
            if 'company_name' in c_df.columns:
                ww_mask = c_df['company_name'] == "WestWorld"
                if ww_mask.any():
                    idx = c_df[ww_mask].index[0]
                    # Only update if address is empty/NaN
                    curr_addr = str(c_df.at[idx, 'address'])
                    if not curr_addr or curr_addr == 'nan':
                        c_df.at[idx, 'address'] = "1122 W. 5th Avenue, Suite 100, Lakeland, Florida 33805, United States"
                        c_df.at[idx, 'contact_phone'] = "(863) 667-4464"
                        c_df.at[idx, 'contact_email'] = "info@westworldtelecom.com" # Default
                        c_df.to_csv(COMPANIES_FILE, index=False)
                        print("✅ WestWorld company details migrated.")

            if 'company_name' in c_df.columns:
                companies_exist = set(c_df['company_name'].unique())
        except: pass
    
    # Harvest legacy companies from Users and Inventory
    legacy_companies = set()
    if os.path.exists(USER_DB_FILE):
        try:
            u_df = pd.read_csv(USER_DB_FILE)
            if 'company' in u_df.columns:
                legacy_companies.update(u_df['company'].dropna().unique())
        except: pass
        
    if os.path.exists(MASTER_INVENTORY_FILE):
        try:
            i_df = pd.read_csv(MASTER_INVENTORY_FILE)
            # Try to find owner column case-insensitively
            o_col = next((c for c in i_df.columns if c.lower() == 'owner'), None)
            if o_col:
                legacy_companies.update(i_df[o_col].dropna().unique())
        except: pass
    
    # Merge and Save
    all_companies = sorted(list(companies_exist | legacy_companies))
    if not all_companies: all_companies = ["WestWorld"]
    
    # Re-save if we found new legacy ones not in file
    if len(all_companies) > len(companies_exist):
        new_df = pd.DataFrame({'company_name': all_companies, 'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        new_df.to_csv(COMPANIES_FILE, index=False)
        print("✅ Companies migrated to centralized DB.")
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
def get_all_companies():
    """Returns list of all companies from centralized DB."""
    if os.path.exists(COMPANIES_FILE):
        try:
            df = pd.read_csv(COMPANIES_FILE)
            if 'company_name' in df.columns:
                return sorted(df['company_name'].dropna().unique().tolist())
        except:
            return ["WestWorld"]
    return ["WestWorld"]

def add_company(name, address="", contact_name="", contact_email="", phone="", logo_file=None):
    """Adds a new company to the DB with optional details."""
    if not name: return False
    
    current = get_all_companies()
    # Case insensitive check
    if any(c.lower() == name.lower() for c in current): return False 
    
    # Handle Logo Upload
    logo_path = ""
    if logo_file:
        try:
            if not os.path.exists("logos"):
                os.makedirs("logos")
            # Sanitize filename
            safe_name = "".join([c for c in name if c.isalnum() or c in (' ','-','_')]).strip().replace(" ", "_")
            ext = logo_file.name.split('.')[-1]
            fname = f"logos/{safe_name}_logo.{ext}"
            with open(fname, "wb") as f:
                f.write(logo_file.getbuffer())
            logo_path = fname
        except Exception as e:
            print(f"❌ Error saving logo: {e}")

    # Append
    new_data = {
        'company_name': name, 
        'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'address': address,
        'contact_name': contact_name,
        'contact_email': contact_email,
        'contact_phone': phone,
        'logo_path': logo_path
    }
    df = pd.DataFrame([new_data])
    
    if os.path.exists(COMPANIES_FILE):
        # Check if empty
        if os.stat(COMPANIES_FILE).st_size == 0:
             df.to_csv(COMPANIES_FILE, index=False)
        else:
             # Ensure headers match if appending. If columns missing in existing file, might need read/rewrite logic.
             # For simplicity in V1, we append blindly assuming standard CSV behavior or just re-read full file.
             # Safer: Read, Concat, Save
             try:
                 old_df = pd.read_csv(COMPANIES_FILE)
                 final_df = pd.concat([old_df, df], ignore_index=True)
                 final_df.to_csv(COMPANIES_FILE, index=False)
             except:
                 df.to_csv(COMPANIES_FILE, index=False) 
    else:
        df.to_csv(COMPANIES_FILE, index=False)
    return True

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
    """Fetches the company logo from companies.csv if exists, else legacy check."""
    # 1. Check entries in companies.csv
    if os.path.exists(COMPANIES_FILE):
        try:
            df = pd.read_csv(COMPANIES_FILE)
            if 'company_name' in df.columns and 'logo_path' in df.columns:
                row = df[df['company_name'] == company]
                if not row.empty:
                    logo_path = row.iloc[0]['logo_path']
                    if logo_path and isinstance(logo_path, str) and os.path.exists(logo_path):
                        return logo_path
        except: pass

    # 2. Legacy: Check logos directory by name
    if not os.path.exists('logos'):
        os.makedirs('logos')
        
    for ext in ['png', 'jpg', 'jpeg', 'webp']:
        path = f"logos/{company}.{ext}"
        if os.path.exists(path):
            return path
    
    # 3. Fallback to default
    if os.path.exists(LOGO_FILE):
        return LOGO_FILE
    return None

def update_company(original_name, new_address, new_contact, new_email, new_phone, new_logo_file=None):
    """Updates an existing company's details."""
    if not os.path.exists(COMPANIES_FILE): return False
    
    try:
        df = pd.read_csv(COMPANIES_FILE)
        if 'company_name' not in df.columns: return False
        
        idx = df[df['company_name'] == original_name].index
        if len(idx) == 0: return False
        idx = idx[0]
        
        # Update text fields
        df.at[idx, 'address'] = new_address
        df.at[idx, 'contact_name'] = new_contact
        df.at[idx, 'contact_email'] = new_email
        df.at[idx, 'contact_phone'] = new_phone
        
        # Handle Logo Update
        if new_logo_file:
            if not os.path.exists("logos"):
                os.makedirs("logos")
                
            safe_name = "".join([c for c in original_name if c.isalnum() or c in (' ','-','_')]).strip().replace(" ", "_")
            ext = new_logo_file.name.split('.')[-1]
            fname = f"logos/{safe_name}_logo_{int(datetime.datetime.now().timestamp())}.{ext}" # Timestamp to bust cache
            
            with open(fname, "wb") as f:
                f.write(new_logo_file.getbuffer())
                
            df.at[idx, 'logo_path'] = fname
            
        df.to_csv(COMPANIES_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error updating company: {e}")
        return False

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {
        "email_rules": []
    }

def is_global_admin():
    """Helper to check if user has global administrative powers."""
    return st.session_state['user_role'] == 'admin' or (st.session_state['user_role'] == 'manager' and st.session_state['company'] == 'WestWorld')

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def process_recall_request(items_df, user, company, comment=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = items_df.copy()
    for col in ['Select', 'Select for Recall', 'Select for Audit']:
        if col in log_entry.columns:
            log_entry = log_entry.drop(columns=[col])
    log_entry['Requested By'] = user
    log_entry['Company'] = company # Fallback if not present
    # If the dataframe already has a 'Company' column (e.g. All Companies view), use that.
    # Otherwise use the passed context (e.g. Specific view where we know the target)
    if 'Company' in items_df.columns:
        log_entry['Company'] = items_df['Company']
    else:
        log_entry['Company'] = company
    log_entry['Request Time'] = timestamp
    log_entry['Recall Comment'] = comment
    log_entry['Status'] = 'Pending' # Init status
    
    old_log = load_data(RECALL_LOG_FILE)
    if not old_log.empty and 'Status' not in old_log.columns:
        old_log['Status'] = 'Pending'
        
    new_log = pd.concat([old_log, log_entry], ignore_index=True)
    
    # Prevent double-click duplicates by dropping identical rows (ignoring the timestamp)
    check_cols = [c for c in new_log.columns if c != 'Request Time']
    new_log = new_log.drop_duplicates(subset=check_cols, keep='last')
    
    save_data(new_log, RECALL_LOG_FILE)
    
    # Notify logic: Find matching emails
    settings = load_settings()
    rules = settings.get("email_rules", [])
    
    recipients = set()
    # Always notify the system admin for recalls
    recipients.add("crjoac3@gmail.com") 
    
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
            # Robust column retrieval
            sn = row.get('Serial Number') or row.get('Internal Serial') or row.get('Mnfr Serial') or 'N/A'
            model = row.get('Model') or row.get('Part#') or 'N/A'
            body += f"- SN: {sn} | Model: {model}\n"
        
        body += f"\nView full details in the WestWorld Portal."
        
        send_email_actual(recipient_list, subject, body)
                
    return ", ".join(recipients) if recipients else "No Notification Configured"

def process_audit_request(items_df, user, company, comment):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = items_df.copy()
    for col in ['Select', 'Select for Recall', 'Select for Audit']:
        if col in log_entry.columns:
            log_entry = log_entry.drop(columns=[col])
    
    log_entry['Requested By'] = user
    log_entry['Company'] = company
    if 'Company' in items_df.columns:
        log_entry['Company'] = items_df['Company']
        
    log_entry['Request Time'] = timestamp
    log_entry['Audit Comment'] = comment
    log_entry['Status'] = 'Pending'
    
    old_log = load_data(AUDIT_LOG_FILE)
    new_log = pd.concat([old_log, log_entry], ignore_index=True)
    
    # Prevent double-click duplicates by dropping identical rows (ignoring the timestamp)
    check_cols = [c for c in new_log.columns if c != 'Request Time']
    new_log = new_log.drop_duplicates(subset=check_cols, keep='last')
    
    save_data(new_log, AUDIT_LOG_FILE)
    return True

def send_email_actual(recipients, subject, body):
    """Send email using SendGrid SMTP."""
    import smtplib
    from email.mime.text import MIMEText
    
    # Get SendGrid credentials from environment variables
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL")
    
    if not api_key or not from_email:
        print("⚠️ SendGrid not configured. Set SENDGRID_API_KEY and SENDGRID_FROM_EMAIL in .env file")
        return
        
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ", ".join(recipients) if isinstance(recipients, list) else recipients
        
        # SendGrid SMTP configuration
        with smtplib.SMTP('smtp.sendgrid.net', 587) as s:
            s.starttls()
            s.login('apikey', api_key)  # Username is literally 'apikey'
            s.sendmail(from_email, recipients, msg.as_string())
        print(f"✅ Email sent to {recipients}")
    except Exception as e:
        print(f"❌ SendGrid Error: {str(e)}")

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
        menu_options = ["Inventory", "My Profile"]
        
        # Super Admin & WestWorld Global Managers
        if is_global_admin():
            menu_options = ["Inventory", "Recall Management", "Audit Management", "Inventory Management", "Company Management", "User Management", "Settings", "My Profile"]
        
        # Client Admin / Manager (Can manage their own users and branding, but UI is consolidated)
        elif st.session_state['user_role'] == 'manager':
            menu_options = ["Inventory", "User Management", "My Profile"]
            
        page = st.radio("Navigate", menu_options)
            
        st.divider()
        if st.button("Log Out"):
            st.session_state.update({'logged_in': False, 'user_role': None, 'username': None, 'company': None, 'name': None})
            st.rerun()

    # --- PAGE 1: INVENTORY ---
    if page == "Inventory":
        # Determine which company's inventory to show
        target_company = st.session_state['company']
        
        # If Global Admin, allow selecting any company
        if is_global_admin():
            all_cos = get_all_companies()
            client_cos = [c for c in all_cos if c != "WestWorld"]
            company_list = ["All Companies"] + client_cos
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
            
            recall_log_df = load_data(RECALL_LOG_FILE)
            if target_company != "All Companies" and not recall_log_df.empty:
                if 'Company' in recall_log_df.columns:
                    recall_log_df = recall_log_df[recall_log_df['Company'] == target_company]
            
            if not user_df.empty or not recall_log_df.empty:
                # View Filters
                filter_mode = st.radio("Show Details:", ["Equipment On-Hand", "Equipment Sold", "Recalled Equipment"], horizontal=True)
                
                if filter_mode == "Recalled Equipment":
                    display_df = recall_log_df.copy()
                else:
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
                if filter_mode == "Equipment Sold":
                    if 'Sales Price' in display_df.columns:
                        try:
                            total_sum = display_df['Sales Price'].replace(r'[\$,]', '', regex=True).astype(float).sum()
                            val = f"${total_sum:,.2f}"
                        except:
                            pass
                    m3.metric("Total Sales Value", val)
                else:
                    if 'Cost' in display_df.columns:
                        try:
                            total_sum = display_df['Cost'].replace(r'[\$,]', '', regex=True).astype(float).sum()
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
                    st.caption("Select items to request a recall or an audit:")
                    
                    # Remove empty cost columns for On-Hand view if they exist
                    cols_to_drop = [c for c in ['Cost', 'Sales Price'] if c in display_df.columns]
                    if cols_to_drop:
                        display_df = display_df.drop(columns=cols_to_drop)
                    
                    # Split Date column into Month, Day, Year
                    if 'Date' in display_df.columns:
                        try:
                            temp_dates = pd.to_datetime(display_df['Date'], errors='coerce')
                            date_idx = list(display_df.columns).index('Date')
                            if 'Month' not in display_df.columns: display_df.insert(date_idx, 'Month', temp_dates.dt.month.astype('Int64'))
                            if 'Day' not in display_df.columns: display_df.insert(date_idx+1, 'Day', temp_dates.dt.day.astype('Int64'))
                            if 'Year' not in display_df.columns: display_df.insert(date_idx+2, 'Year', temp_dates.dt.year.astype('Int64'))
                            display_df = display_df.drop(columns=['Date'])
                        except Exception:
                            pass
                            
                    # Add Condition Dropdown column for later use
                    if "Condition" not in display_df.columns:
                        # Insert next to Status if it exists, else at the end
                        insert_idx = list(display_df.columns).index('Status') + 1 if 'Status' in display_df.columns else len(display_df.columns)
                        display_df.insert(insert_idx, "Condition", "Refurb")
                    else:
                        # If Condition already exists in the CSV data but has None/NaN/Empties, overwrite them entirely
                        display_df['Condition'] = display_df['Condition'].fillna("Refurb").replace(["", "None", "NaN", None], "Refurb")
                        
                    if "Select for Recall" not in display_df.columns:
                        display_df.insert(0, "Select for Recall", False)
                    if "Select for Audit" not in display_df.columns:
                        display_df.insert(1, "Select for Audit", False)
                        
                    edited = st.data_editor(
                        display_df, 
                        hide_index=True, 
                        width="stretch", 
                        column_config={
                            "Select for Recall": st.column_config.CheckboxColumn(required=True),
                            "Select for Audit": st.column_config.CheckboxColumn(required=True),
                            "Sales Price": st.column_config.NumberColumn(format="$%.2f"),
                            "Cost": st.column_config.NumberColumn(format="$%.2f"),
                            "Partner Allocation - Cost": st.column_config.NumberColumn(format="$%.2f"),
                            "Request Time": st.column_config.DatetimeColumn("Request Time", format="MM-DD-YYYY"),
                            "Condition": st.column_config.SelectboxColumn(
                                "Condition", 
                                help="Double-click to select condition", 
                                options=["Refurb", "Defective"],
                                required=False
                            )
                        }
                    )
                    
                    recall_items = edited[edited["Select for Recall"]]
                    audit_items = edited[edited["Select for Audit"]]
                    
                    if not recall_items.empty or not audit_items.empty:
                        st.markdown("### Actions")
                        
                        if not recall_items.empty:
                            with st.expander(f"🚀 Request Recall for {len(recall_items)} Item(s)", expanded=True):
                                recall_comment = st.text_area("Reason for Recall", placeholder="Enter recall details or instructions...")
                                if st.button("Submit Recall"):
                                    if not recall_comment.strip():
                                        st.warning("Please provide a comment for the recall request.")
                                    else:
                                        requester_name = st.session_state.get('name', st.session_state['username'])
                                        emails = process_recall_request(recall_items, requester_name, target_company, recall_comment)
                                        st.balloons()
                                        st.success(f"✅ Recall request submitted! Notifications sent to: {emails}")
                                        st.rerun()
                                
                        if not audit_items.empty:
                            with st.expander(f"🚩 Submit Audit Request for {len(audit_items)} Item(s)", expanded=True):
                                audit_comment = st.text_area("Reason for Audit", placeholder="Enter details or discrepancies here...")
                                if st.button("Submit Audit"):
                                    if not audit_comment.strip():
                                        st.warning("Please provide a comment for the audit request.")
                                    else:
                                        requester_name = st.session_state.get('name', st.session_state['username'])
                                        process_audit_request(audit_items, requester_name, target_company, audit_comment)
                                        st.success("✅ Audit request submitted successfully! Items remain in your inventory view.")
                                        st.rerun()
                elif filter_mode == "Recalled Equipment":
                    st.caption("Recalled Equipment History:")
                    if not display_df.empty:
                        # Generate hyperlinked tracking URLs if tracking numbers exist
                        if 'Tracking Number' in display_df.columns:
                            display_df['Tracking Link'] = display_df['Tracking Number'].apply(
                                lambda x: f"https://www.google.com/search?q={str(x).strip()}" if pd.notna(x) and str(x).strip() else None
                            )
                        else:
                            display_df['Tracking Link'] = None
                            
                        # Remove actual Tracking Number column to just render the URL column as 'Track'
                        display_cols = display_df.columns.tolist()
                        if 'Tracking Number' in display_cols: 
                            display_cols.remove('Tracking Number')
                            
                        st.dataframe(
                            display_df[display_cols],
                            hide_index=True,
                            width="stretch",
                            column_config={
                                "Tracking Link": st.column_config.LinkColumn("Tracking Number", display_text="Track", help="Click to search Tracking Number"),
                                "Request Time": st.column_config.DatetimeColumn("Request Time", format="MM-DD-YYYY"),
                                "Sales Price": st.column_config.NumberColumn(format="$%.2f"),
                                "Cost": st.column_config.NumberColumn(format="$%.2f"),
                                "Partner Allocation - Cost": st.column_config.NumberColumn(format="$%.2f")
                            }
                        )
                    else:
                        st.info("No recorded recalls for this company.")
                else:
                    st.dataframe(
                        display_df, 
                        hide_index=True, 
                        width="stretch",
                        column_config={
                            "Request Time": st.column_config.DatetimeColumn("Request Time", format="MM-DD-YYYY"),
                            "Sales Price": st.column_config.NumberColumn(format="$%.2f"),
                            "Cost": st.column_config.NumberColumn(format="$%.2f"),
                            "Partner Allocation - Cost": st.column_config.NumberColumn(format="$%.2f")
                        }
                    )
                
                if not display_df.empty:
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
                st.dataframe(
                    view_df.sort_values('Request Time', ascending=False), 
                    hide_index=True, 
                    width="stretch",
                    column_config={
                        "Request Time": st.column_config.DatetimeColumn("Request Time", format="MM-DD-YYYY"),
                        "Sales Price": st.column_config.NumberColumn(format="$%.2f"),
                        "Cost": st.column_config.NumberColumn(format="$%.2f")
                    }
                )
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
                        st.info("Fill out tracking and location information, then select items to mark as RECEIVED. ⚠️ This will REMOVE them from the Master Inventory.")
                        active_df.insert(0, "Mark Received", False)
                        
                        if "Tracking Number" not in active_df.columns: active_df["Tracking Number"] = ""
                        if "Location - Bin" not in active_df.columns: active_df["Location - Bin"] = ""
                        if "Location - Warehouse" not in active_df.columns: active_df["Location - Warehouse"] = ""
                        
                        # Prevent StreamlitAPIException: "column type text... not compatible... data type float"
                        for col in ["Tracking Number", "Location - Bin", "Location - Warehouse"]:
                            active_df[col] = active_df[col].fillna("").astype(str)
                        
                        edited_recall = st.data_editor(
                            active_df, 
                            hide_index=True, 
                            width="stretch", 
                            column_config={
                                "Mark Received": st.column_config.CheckboxColumn(required=True),
                                "Tracking Number": st.column_config.TextColumn("Tracking Number"),
                                "Location - Bin": st.column_config.TextColumn("Bin"),
                                "Location - Warehouse": st.column_config.TextColumn("Warehouse"),
                                "Request Time": st.column_config.DatetimeColumn("Request Time", format="MM-DD-YYYY"),
                                "Sales Price": st.column_config.NumberColumn(format="$%.2f"),
                                "Cost": st.column_config.NumberColumn(format="$%.2f")
                            }
                        )
                        
                        if st.button("✅ Confirm Receipt & Remove from Inventory"):
                            to_update = edited_recall[edited_recall['Mark Received']]
                            if not to_update.empty:
                                # Validation: Ensure Tracking Number is provided
                                missing_tracking = to_update[to_update['Tracking Number'].str.strip() == ""]
                                if not missing_tracking.empty:
                                    st.error("⚠️ Cannot confirm receipt: A Tracking Number is required for all selected items.")
                                else:
                                    master_inventory = load_data(MASTER_INVENTORY_FILE)
                                    removed_count = 0
                                    
                                    for idx, row in to_update.iterrows():
                                        # 1. Update Status & Tracking in Recall Log using UNIQUE INDEX
                                        if idx in recall_df.index:
                                            recall_df.loc[idx, 'Status'] = 'Completed'
                                            recall_df.loc[idx, 'Processed By'] = st.session_state.get('name', st.session_state['username'])
                                            if 'Tracking Number' in row: recall_df.loc[idx, 'Tracking Number'] = row['Tracking Number']
                                            if 'Location - Bin' in row: recall_df.loc[idx, 'Location - Bin'] = row['Location - Bin']
                                            if 'Location - Warehouse' in row: recall_df.loc[idx, 'Location - Warehouse'] = row['Location - Warehouse']
                                        
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
                        
                        # Generate hyperlinked tracking URLs if tracking numbers exist
                        if 'Tracking Number' in history_df.columns:
                            # Use regex or simple replace to ensure valid URL text but display cleanly as a link
                            history_df['Tracking Link'] = history_df['Tracking Number'].apply(
                                lambda x: f"https://www.google.com/search?q={str(x).strip()}" if pd.notna(x) and str(x).strip() else None
                            )
                        else:
                            history_df['Tracking Link'] = None
                            
                        # Remove actual Tracking Number column to just render the URL column as 'Track'
                        display_cols = history_df.columns.tolist()
                        if 'Tracking Number' in display_cols: 
                            display_cols.remove('Tracking Number')
                            
                        edited_history = st.data_editor(
                            history_df[display_cols], 
                            hide_index=True, 
                            width="stretch",
                            column_config={
                                "Restock": st.column_config.CheckboxColumn(required=True),
                                "Tracking Link": st.column_config.LinkColumn("Tracking Number", display_text="Track", help="Click to search Tracking Number"),
                                "Request Time": st.column_config.DatetimeColumn("Request Time", format="MM-DD-YYYY"),
                                "Sales Price": st.column_config.NumberColumn(format="$%.2f"),
                                "Cost": st.column_config.NumberColumn(format="$%.2f")
                            }
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
        st.info("Pending Audit Requests will appear here. Mark them as completed when verified.")
        
        audit_history_df = load_data(AUDIT_LOG_FILE)
        
        if audit_history_df.empty:
            st.info("No audit requests have been made yet.")
        else:
            # Add Status if missing from legacy files
            if 'Status' not in audit_history_df.columns:
                audit_history_df['Status'] = 'Pending'
                
            # Filter by company if needed
            if target_company != "All Companies":
                display_df = audit_history_df[audit_history_df['Company'] == target_company]
            else:
                display_df = audit_history_df
                
            if display_df.empty:
                st.info(f"No audit requests found for {target_company}.")
            else:
                # Top Table: Pending Items
                st.subheader("Pending Audit Requests")
                pending_df = display_df[display_df['Status'] == 'Pending'].copy()
                
                if pending_df.empty:
                    st.success("All caught up! No pending audits.")
                else:
                    pending_df.insert(0, "Mark Complete", False)
                    edited_pending = st.data_editor(
                        pending_df,
                        hide_index=True,
                        width="stretch",
                        column_config={
                            "Mark Complete": st.column_config.CheckboxColumn(required=True),
                            "Request Time": st.column_config.DatetimeColumn("Request Time", format="MM-DD-YYYY")
                        }
                    )
                    
                    to_complete = edited_pending[edited_pending['Mark Complete']]
                    
                    if not to_complete.empty:
                        st.markdown("---")
                        st.subheader("Completion Details")
                        completion_comment = st.text_area("Audit Completion Notes (Optional)", placeholder="Enter any notes or findings regarding this completed audit...")
                        
                        if st.button("✅ Confirm Completed Audits"):
                            completed_count = 0
                            # Update statuses based on index matching
                            for idx, row in to_complete.iterrows():
                                if idx in audit_history_df.index:
                                    audit_history_df.loc[idx, 'Status'] = 'Completed'
                                    audit_history_df.loc[idx, 'Processed By'] = st.session_state.get('name', st.session_state['username'])
                                    if completion_comment.strip():
                                        audit_history_df.loc[idx, 'Completion Notes'] = completion_comment.strip()
                                    completed_count += 1
                                    
                            save_data(audit_history_df, AUDIT_LOG_FILE)
                            st.balloons()
                            st.success(f"✅ Marked {completed_count} items as completed!")
                            st.rerun()

                st.divider()
                
                # Bottom Table: Completed Items
                st.subheader("Completed Audit History")
                completed_df = display_df[display_df['Status'] == 'Completed'].copy()
                if completed_df.empty:
                    st.info("No completed audits yet.")
                else:
                    st.dataframe(
                        completed_df.sort_values('Request Time', ascending=False), 
                        hide_index=True, 
                        width="stretch",
                        column_config={
                            "Request Time": st.column_config.DatetimeColumn("Request Time", format="MM-DD-YYYY")
                        }
                    )


    # --- PAGE 4: INVENTORY MANAGEMENT (SUPER ADMIN ONLY) ---
    elif page == "Inventory Management":
        st.title("📂 Inventory Management")
        st.info("Upload Master Excel to assign stock to a Client Company.")
        
        all_cos = get_all_companies()
        client_companies = [c for c in all_cos if c != "WestWorld"]
        
        with st.form("upload_form"):
            target_client_co = st.selectbox("Select Target Client (Company)", client_companies)
            
            upload_mode = st.radio("Upload Mode:", 
                                   ["Replace Existing Inventory (Deletes old records for this client)", 
                                    "Append to Existing Inventory (Keeps old records for this client)"],
                                   index=0)
            
            uploaded_file = st.file_uploader("Upload Master Excel File", type=['xlsx'])
            submitted = st.form_submit_button("Start Processing")
            
            if submitted and uploaded_file:
                with st.spinner("Processing Excel..."):
                    try:
                        xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
                        
                        # 1. Base Inventory (Total Units Received)
                        base_sheet = next((s for s in xls.sheet_names if "recv" in s.lower() or "received" in s.lower() or "inv" in s.lower()), None)
                        if not base_sheet: base_sheet = xls.sheet_names[0]
                        df_base = pd.read_excel(xls, sheet_name=base_sheet).dropna(how='all')
                        st.info(f"Loaded {len(df_base)} total baseline records.")
                        if 'Status' not in df_base.columns: df_base['Status'] = 'ON HAND'
                        df_base['owner'] = target_client_co
                        
                        # 2. Sold Inventory (Units Sold)
                        sold_sheet = next((s for s in xls.sheet_names if "sold" in s.lower()), None)
                        if sold_sheet:
                            df_sold = pd.read_excel(xls, sheet_name=sold_sheet).dropna(how='all')
                            st.info(f"Matched {len(df_sold)} sold records.")
                            if 'Sales Price' not in df_base.columns: df_base['Sales Price'] = 0
                            if 'Cost' not in df_base.columns: df_base['Cost'] = 0

                            # Match by Internal Serial
                            if 'Internal Serial' in df_sold.columns and 'Internal Serial' in df_base.columns:
                                sold_int = df_sold.dropna(subset=['Internal Serial'])
                                if not sold_int.empty:
                                    sold_serials = sold_int['Internal Serial'].tolist()
                                    df_base.loc[df_base['Internal Serial'].isin(sold_serials), 'Status'] = 'SOLD'
                                    
                                    unique_int = sold_int.drop_duplicates(subset=['Internal Serial'])
                                    if 'Sales Price' in sold_int.columns:
                                        sales_map = dict(zip(unique_int['Internal Serial'], unique_int['Sales Price']))
                                        df_base['Sales Price'] = df_base['Internal Serial'].map(sales_map).fillna(df_base['Sales Price'])
                                    
                                    if 'Partner Allocation - Cost' in sold_int.columns:
                                        cost_map = dict(zip(unique_int['Internal Serial'], unique_int['Partner Allocation - Cost']))
                                        mapped_costs = df_base['Internal Serial'].map(cost_map)
                                        df_base.loc[df_base['Status'] == 'SOLD', 'Cost'] = mapped_costs.fillna(df_base['Cost'])

                            # Match by Mnfr Serial (for records missing Internal Serial)
                            if 'Mnfr Serial' in df_sold.columns and 'Mnfr Serial' in df_base.columns:
                                sold_mnf = df_sold.dropna(subset=['Mnfr Serial'])
                                if not sold_mnf.empty:
                                    mnf_serials = sold_mnf['Mnfr Serial'].tolist()
                                    df_base.loc[df_base['Mnfr Serial'].isin(mnf_serials), 'Status'] = 'SOLD'
                                    
                                    unique_mnf = sold_mnf.drop_duplicates(subset=['Mnfr Serial'])
                                    if 'Sales Price' in sold_mnf.columns:
                                        sales_map_m = dict(zip(unique_mnf['Mnfr Serial'], unique_mnf['Sales Price']))
                                        df_base['Sales Price'] = df_base['Mnfr Serial'].map(sales_map_m).fillna(df_base['Sales Price'])
                                    
                                    if 'Partner Allocation - Cost' in sold_mnf.columns:
                                        cost_map_m = dict(zip(unique_mnf['Mnfr Serial'], unique_mnf['Partner Allocation - Cost']))
                                        mapped_costs_m = df_base['Mnfr Serial'].map(cost_map_m)
                                        df_base.loc[df_base['Mnfr Serial'].isin(mnf_serials), 'Cost'] = mapped_costs_m.fillna(df_base['Cost'])

                            # Match by Part# (Tertiary fallback for completely missing serials)
                            if 'Part#' in df_sold.columns and 'Part#' in df_base.columns:
                                sold_prt = df_sold.dropna(subset=['Part#'])
                                if not sold_prt.empty:
                                    prt_serials = sold_prt['Part#'].tolist()
                                    df_base.loc[(df_base['Part#'].isin(prt_serials)) & (df_base['Status'] != 'SOLD'), 'Status'] = 'SOLD'
                                    
                                    unique_prt = sold_prt.drop_duplicates(subset=['Part#'])
                                    if 'Sales Price' in sold_prt.columns:
                                        sales_map_p = dict(zip(unique_prt['Part#'], unique_prt['Sales Price']))
                                        df_base['Sales Price'] = df_base['Part#'].map(sales_map_p).fillna(df_base['Sales Price'])
                                    
                                    if 'Partner Allocation - Cost' in sold_prt.columns:
                                        cost_map_p = dict(zip(unique_prt['Part#'], unique_prt['Partner Allocation - Cost']))
                                        mapped_costs_p = df_base['Part#'].map(cost_map_p)
                                        df_base.loc[df_base['Part#'].isin(prt_serials), 'Cost'] = mapped_costs_p.fillna(df_base['Cost'])

                        # 3. Returned Inventory (Ciena Requested Units Returned)
                        return_sheet = next((s for s in xls.sheet_names if "return" in s.lower()), None)
                        if return_sheet:
                            df_returned = pd.read_excel(xls, sheet_name=return_sheet).dropna(how='all')
                            st.info(f"Processing {len(df_returned)} returned records.")
                            to_remove = pd.DataFrame()
                            
                            # Extract Return by Internal Serial
                            if 'Internal Serial' in df_returned.columns and 'Internal Serial' in df_base.columns:
                                ret_int = df_returned.dropna(subset=['Internal Serial'])
                                if not ret_int.empty:
                                    ret_serials = ret_int['Internal Serial'].tolist()
                                    to_rem_int = df_base[df_base['Internal Serial'].isin(ret_serials)].copy()
                                    df_base = df_base[~df_base['Internal Serial'].isin(ret_serials)]
                                    
                                    if not to_rem_int.empty:
                                        unique_ret = ret_int.drop_duplicates(subset=['Internal Serial'])
                                        if 'Tracking Number' in df_returned.columns:
                                            trk_map = dict(zip(unique_ret['Internal Serial'], unique_ret['Tracking Number']))
                                            to_rem_int['Tracking Number'] = to_rem_int['Internal Serial'].map(trk_map)
                                        if 'Location - Bin' in df_returned.columns:
                                            bin_map = dict(zip(unique_ret['Internal Serial'], unique_ret['Location - Bin']))
                                            to_rem_int['Location - Bin'] = to_rem_int['Internal Serial'].map(bin_map)
                                        if 'Location - Warehouse' in df_returned.columns:
                                            wh_map = dict(zip(unique_ret['Internal Serial'], unique_ret['Location - Warehouse']))
                                            to_rem_int['Location - Warehouse'] = to_rem_int['Internal Serial'].map(wh_map)
                                        to_remove = pd.concat([to_remove, to_rem_int])

                            # Extract Return by Mnfr Serial
                            if 'Mnfr Serial' in df_returned.columns and 'Mnfr Serial' in df_base.columns:
                                ret_mnf = df_returned.dropna(subset=['Mnfr Serial'])
                                if not ret_mnf.empty:
                                    mnf_serials = ret_mnf['Mnfr Serial'].tolist()
                                    to_rem_mnf = df_base[df_base['Mnfr Serial'].isin(mnf_serials)].copy()
                                    df_base = df_base[~df_base['Mnfr Serial'].isin(mnf_serials)]
                                    
                                    if not to_rem_mnf.empty:
                                        unique_ret_m = ret_mnf.drop_duplicates(subset=['Mnfr Serial'])
                                        if 'Tracking Number' in df_returned.columns:
                                            trk_map_m = dict(zip(unique_ret_m['Mnfr Serial'], unique_ret_m['Tracking Number']))
                                            to_rem_mnf['Tracking Number'] = to_rem_mnf['Mnfr Serial'].map(trk_map_m)
                                        if 'Location - Bin' in df_returned.columns:
                                            bin_map_m = dict(zip(unique_ret_m['Mnfr Serial'], unique_ret_m['Location - Bin']))
                                            to_rem_mnf['Location - Bin'] = to_rem_mnf['Mnfr Serial'].map(bin_map_m)
                                        if 'Location - Warehouse' in df_returned.columns:
                                            wh_map_m = dict(zip(unique_ret_m['Mnfr Serial'], unique_ret_m['Location - Warehouse']))
                                            to_rem_mnf['Location - Warehouse'] = to_rem_mnf['Mnfr Serial'].map(wh_map_m)
                                        to_remove = pd.concat([to_remove, to_rem_mnf])
                            
                            # Extract Return by Part#
                            if 'Part#' in df_returned.columns and 'Part#' in df_base.columns:
                                ret_prt = df_returned.dropna(subset=['Part#'])
                                if not ret_prt.empty:
                                    prt_serials = ret_prt['Part#'].tolist()
                                    # Careful here: Part# is rarely totally unique to one row. 
                                    to_rem_prt = df_base[df_base['Part#'].isin(prt_serials)].copy()
                                    df_base = df_base[~df_base['Part#'].isin(prt_serials)]
                                    
                                    if not to_rem_prt.empty:
                                        unique_ret_p = ret_prt.drop_duplicates(subset=['Part#'])
                                        if 'Tracking Number' in df_returned.columns:
                                            trk_map_p = dict(zip(unique_ret_p['Part#'], unique_ret_p['Tracking Number']))
                                            to_rem_prt['Tracking Number'] = to_rem_prt['Part#'].map(trk_map_p)
                                        if 'Location - Bin' in df_returned.columns:
                                            bin_map_p = dict(zip(unique_ret_p['Part#'], unique_ret_p['Location - Bin']))
                                            to_rem_prt['Location - Bin'] = to_rem_prt['Part#'].map(bin_map_p)
                                        if 'Location - Warehouse' in df_returned.columns:
                                            wh_map_p = dict(zip(unique_ret_p['Part#'], unique_ret_p['Location - Warehouse']))
                                            to_rem_prt['Location - Warehouse'] = to_rem_prt['Part#'].map(wh_map_p)
                                        to_remove = pd.concat([to_remove, to_rem_prt])

                            # Process final return log appends
                            if not to_remove.empty:
                                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                to_remove['Status'] = 'Completed'
                                to_remove['Processed By'] = 'System Upload'
                                to_remove['Request Time'] = timestamp
                                to_remove['Requested By'] = 'System'
                                to_remove['Company'] = target_client_co
                                
                                old_log = load_data(RECALL_LOG_FILE)
                                new_log = pd.concat([old_log, to_remove], ignore_index=True)
                                save_data(new_log, RECALL_LOG_FILE)
                        
                        master_df = load_data(MASTER_INVENTORY_FILE)
                        if not master_df.empty and 'owner' in master_df.columns:
                            if "Replace" in upload_mode:
                                master_df = master_df[master_df['owner'] != target_client_co]
                        
                        final_df = pd.concat([master_df, df_base], ignore_index=True)
                        save_data(final_df, MASTER_INVENTORY_FILE)
                        
                        mode_str = "replaced" if "Replace" in upload_mode else "appended"
                        st.success(f"✅ Successfully {mode_str} {len(df_base)} active records for {target_client_co}!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing file: {str(e)}")
                        st.exception(e)


    # --- PAGE: COMPANY MANAGEMENT ---
    elif page == "Company Management":
        st.title("🏢 Company Management")
        st.info("Manage client companies independently of users or inventory.")
        
        tab_create, tab_edit, tab_view = st.tabs(["➕ Create New", "✏️ Edit Existing", "📋 View All"])
        
        # --- TAB 1: CREATE NEW ---
        with tab_create:
            st.subheader("Create New Company")
            with st.form("create_company_form", clear_on_submit=True):
                new_co_name = st.text_input("New Company Name", placeholder="e.g. Acme Corp")
                c_addr = st.text_area("Address")
                
                col_a, col_b = st.columns(2)
                with col_a: c_contact = st.text_input("Contact Name")
                with col_b: c_phone = st.text_input("Phone Number")
                
                c_email = st.text_input("Contact Email")
                c_logo = st.file_uploader("Upload Company Logo", type=['png', 'jpg', 'jpeg'])
                
                if st.form_submit_button("Create Company"):
                    if add_company(new_co_name, c_addr, c_contact, c_email, c_phone, c_logo):
                        st.success(f"✅ Company '{new_co_name}' created!")
                        st.rerun()
                    else:
                        st.error("❌ Company already exists or invalid name.")

        # --- TAB 2: EDIT EXISTING ---
        with tab_edit:
            st.subheader("Edit Company Details")
            all_companies = get_all_companies()
            selected_co = st.selectbox("Select Company to Edit", all_companies)
            
            if selected_co:
                # Load current data
                current_data = {}
                if os.path.exists(COMPANIES_FILE):
                    try:
                        cdf = pd.read_csv(COMPANIES_FILE)
                        row = cdf[cdf['company_name'] == selected_co]
                        if not row.empty:
                            # Replace NaN with empty string to avoid "nan" in inputs
                            current_data = row.fillna('').iloc[0].to_dict()
                    except: pass
                
                with st.form("edit_company_form"):
                    e_addr = st.text_area("Address", value=current_data.get('address', ''))
                    
                    ec1, ec2 = st.columns(2)
                    with ec1: e_contact = st.text_input("Contact Name", value=current_data.get('contact_name', ''))
                    with ec2: e_phone = st.text_input("Phone Number", value=current_data.get('contact_phone', ''))
                    
                    e_email = st.text_input("Contact Email", value=current_data.get('contact_email', ''))
                    
                    # Show current logo
                    curr_logo = current_data.get('logo_path', '')
                    if curr_logo and os.path.exists(str(curr_logo)):
                        try:
                            st.image(str(curr_logo), width=100, caption="Current Logo")
                        except Exception:
                            st.warning("⚠️ Current logo file is invalid or corrupt.")
                        
                    e_logo = st.file_uploader("Upload New Logo (Overwrites current)", type=['png', 'jpg', 'jpeg'])
                    
                    if st.form_submit_button("Update Company"):
                        if update_company(selected_co, e_addr, e_contact, e_email, e_phone, e_logo):
                            st.success(f"✅ {selected_co} updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Update failed.")

        # --- TAB 3: VIEW ALL ---
        with tab_view:
            st.subheader("Existing Companies")
            if os.path.exists(COMPANIES_FILE):
                try:
                    c_df = pd.read_csv(COMPANIES_FILE)
                    if 'company_name' in c_df.columns:
                        st.dataframe(
                            c_df, 
                            column_config={
                                "logo_path": st.column_config.ImageColumn("Logo"),
                                "created_at": st.column_config.DatetimeColumn("Created At", format="MM-DD-YYYY"),
                            },
                            use_container_width=True, 
                            hide_index=True
                        )
                    else:
                        st.info("No companies found.")
                except:
                    st.error("Error reading companies file.")

    # --- PAGE 5: User Management ---
    elif page == "User Management":
        st.title("👥 User Administration")
        users_df = load_data(USER_DB_FILE)
        
        # Tabbed interface for better organization
        tabs = ["➕ Create User", "✏️ Edit/Reset User", "📋 Existing Users"]
        if is_global_admin():
            tabs.append("🛡️ Super User Console")
            
        tab_list = st.tabs(tabs)
        
        if is_global_admin() and len(tab_list) == 4:
            tab1, tab2, tab3, tab_super = tab_list
        else:
            tab1, tab2, tab3 = tab_list
        
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
                        # Get existing companies from centralized DB
                        known_cos = get_all_companies()
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
                
            st.dataframe(
                viewable_users_list[['username', 'role', 'company', 'email', 'name']], 
                hide_index=True, 
                width="stretch",
                column_config={
                    "processed_at": st.column_config.DatetimeColumn("Last Processed", format="MM-DD-YYYY")
                }
            )
            
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
            
        if is_global_admin() and len(tab_list) == 4:
            with tab_super:
                st.subheader("🛡️ Super User Console")
                st.info("Directly edit the User Database. Use with caution!")
                
                # Fetch all companies for dropdown mapping if needed
                all_companies_list = get_all_companies()
                
                # Use data editor for bulk editing
                edited_users = st.data_editor(
                    users_df,
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "role": st.column_config.SelectboxColumn("Role", options=["admin", "manager", "viewer"], required=True),
                        "company": st.column_config.SelectboxColumn("Company", options=all_companies_list, required=True),
                        "password": st.column_config.TextColumn("Password", help="Set new password directly"),
                        "theme": st.column_config.SelectboxColumn("Theme", options=["light", "dark"]),
                        "processed_at": st.column_config.DatetimeColumn("Last Processed", format="MM-DD-YYYY"),
                        "created_at": st.column_config.DatetimeColumn("Created At", format="MM-DD-YYYY")
                    }
                )
                
                if st.button("💾 Overwrite User Database", type="primary"):
                    st.session_state['confirm_user_overwrite'] = True
                
                if st.session_state.get('confirm_user_overwrite'):
                    st.warning("⚠️ Are you sure? This will replace the ENTIRE users.csv file with the data above.")
                    cw1, cw2 = st.columns(2)
                    with cw1:
                        if st.button("🔥 YES, OVERWRITE DATABASE", key="btn_actual_overwrite"):
                            try:
                                save_data(edited_users, USER_DB_FILE)
                                st.success("✅ User database updated successfully!")
                                del st.session_state['confirm_user_overwrite']
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Save failed: {e}")
                    with cw2:
                        if st.button("Cancel Overwrite"):
                            del st.session_state['confirm_user_overwrite']
                            st.rerun()
                    
    # --- PAGE 6: ADMIN SETTINGS ---
    elif page == "Settings":
        st.title("⚙️ Portal Settings")
        
        # --- 🎨 BRANDING SECTION ---
        # Customization moved to "Company Management" page for global admins.
        # This keeps settings focused on Notifications.

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
                    st.dataframe(
                        rule_df, 
                        hide_index=True, 
                        width="stretch",
                        column_config={
                            "created_at": st.column_config.DatetimeColumn("Set On", format="MM-DD-YYYY")
                        }
                    )
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
                    st.rerun()

        # --- 👑 SUPER ADMIN: SYSTEM UPDATE & DATA ---
        if st.session_state.get('username') == 'admin' and st.session_state.get('company') == 'WestWorld':
            st.divider()
            st.subheader("👑 Super Admin: System & Data")
            
            # 1. APPLICATION UPDATE
            with st.expander("Update Application"):
                st.warning("This will pull the latest code from GitHub and restart the app.")
                
                col_reset1, col_reset2 = st.columns(2)
                with col_reset1: reset_users = st.checkbox("Dangerous: Reset 'users.csv' from Repo (Wipes live users)")
                with col_reset2: reset_companies = st.checkbox("Dangerous: Reset 'companies.csv' from Repo (Wipes live data)")
                
                if st.button("🔄 Force Update from GitHub"):
                    try:
                        import subprocess
                        import shutil
                        
                        # 1. Force Update (Fetch + Reset Hard)
                        # This avoids "local changes" errors by discarding them.
                        subprocess.run(["git", "fetch", "origin"], check=True)
                        result = subprocess.run(["git", "reset", "--hard", "origin/main"], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            st.success(f"Update Successful (Reset to origin/main):\n{result.stdout}")
                            
                            # 2. Selective Data Reset
                            def copy_from_repo(filename, target_path):
                                if os.path.exists(filename):
                                    shutil.copy(filename, target_path)
                                    return True
                                return False

                            if reset_users:
                                if copy_from_repo('users.csv', USER_DB_FILE):
                                    st.warning(f"users.csv reset to default from repo -> {USER_DB_FILE}")
                                    
                            if reset_companies:
                                if copy_from_repo('companies.csv', COMPANIES_FILE):
                                    st.warning(f"companies.csv reset to default from repo -> {COMPANIES_FILE}")

                            st.success("Restarting app...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Git Pull Failed:\n{result.stderr}")
                    except Exception as e:
                        st.error(f"Update failed: {e}")

            # 2. DATA FILE MANAGEMENT
            with st.expander("Data File Management"):
                st.info("Manage CSV files currently on the server (Live Data).")
                
                # List all CSVs in the data directory
                data_dir = os.path.dirname(os.path.abspath(USER_DB_FILE))
                if not data_dir: data_dir = "." 
                
                import glob
                csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
                
                if csv_files:
                    st.write("### Download & Delete Live Data")
                    st.caption(f"Found {len(csv_files)} .csv files in {data_dir}")
                    for csv_path in csv_files:
                        file_name = os.path.basename(csv_path)
                        c_dl, c_del = st.columns([3, 1])
                        with c_dl:
                            with open(csv_path, "rb") as f:
                                st.download_button(
                                    label=f"Download {file_name}",
                                    data=f,
                                    file_name=file_name,
                                    mime="text/csv",
                                    key=f"dl_{file_name}",
                                    use_container_width=True
                                )
                        with c_del:
                            if st.button(f"🗑️ Delete", key=f"del_btn_{file_name}", use_container_width=True):
                                st.session_state[f'confirm_del_{file_name}'] = True
                        
                        if st.session_state.get(f'confirm_del_{file_name}'):
                            st.warning(f"⚠️ Confirm deletion of `{file_name}`?")
                            col_c1, col_c2 = st.columns(2)
                            with col_c1:
                                if st.button(f"Confirm Delete: {file_name}", key=f"conf_del_{file_name}"):
                                    os.remove(csv_path)
                                    st.success(f"Deleted {file_name}")
                                    del st.session_state[f'confirm_del_{file_name}']
                                    time.sleep(1)
                                    st.rerun()
                            with col_c2:
                                if st.button("Cancel", key=f"canc_del_{file_name}"):
                                    del st.session_state[f'confirm_del_{file_name}']
                                    st.rerun()
                else:
                    st.warning("No CSV files found in data directory.")

                st.divider()
                st.write("### 🧹 Wipe Inventory Data")
                st.info("Erase data for a specific company OR clear entire files for a system reset.")
                
                # Dynamic aggregation of all existing companies/owners across all files
                all_co_found = set(get_all_companies())
                for label, f_path in {
                    "Users": USER_DB_FILE, 
                    "Inventory": MASTER_INVENTORY_FILE, 
                    "Recall": RECALL_LOG_FILE, 
                    "Audit": AUDIT_LOG_FILE
                }.items():
                    if os.path.exists(f_path):
                        try:
                            # Use low_memory=False to avoid DtypeWarning on large loads
                            tmp_df = pd.read_csv(f_path, low_memory=False)
                            c_col = next((c for c in tmp_df.columns if c.lower() in ['company', 'owner']), None)
                            if c_col:
                                all_co_found.update([str(x) for x in tmp_df[c_col].unique() if pd.notna(x) and x != ''])
                        except:
                            pass
                
                wipe_options = ["--- CLEAR ALL RECORDS ---"] + sorted(list(all_co_found))
                wipe_co = st.selectbox("Select Target to Wipe", wipe_options, key="wipe_co_sel")
                
                files_to_wipe_opts = ["Master Inventory", "Recall Log", "Audit Log"]
                files_to_wipe = st.multiselect(
                    "Select Files to Clean",
                    files_to_wipe_opts,
                    default=["Master Inventory"]
                )
                
                if st.button("🔥 Execute Inventory Data Action"):
                    if not files_to_wipe:
                        st.warning("Please select at least one file to wipe.")
                    elif wipe_co == "WestWorld":
                        st.error("⛔ Cannot wipe the master company (WestWorld).")
                    else:
                        st.session_state['confirm_wipe'] = True

                if st.session_state.get('confirm_wipe'):
                    target_display = "ALL DATA" if wipe_co == "--- CLEAR ALL RECORDS ---" else f"records for {wipe_co}"
                    st.warning(f"⚠️ DANGER: This will delete {target_display} in: {', '.join(files_to_wipe)}")
                    col_w1, col_w2 = st.columns(2)
                    with col_w1:
                        if st.button(f"✅ Confirm Action", key="wipe_btn_actual"):
                            try:
                                file_map = {
                                    "Master Inventory": MASTER_INVENTORY_FILE,
                                    "Recall Log": RECALL_LOG_FILE,
                                    "Audit Log": AUDIT_LOG_FILE
                                }
                                
                                for label in files_to_wipe:
                                    f_path = file_map[label]
                                    if os.path.exists(f_path):
                                        if wipe_co == "--- CLEAR ALL RECORDS ---":
                                            # Truncate to just headers
                                            df_existing = pd.read_csv(f_path, nrows=0)
                                            df_existing.to_csv(f_path, index=False)
                                            st.write(f"Done: Cleared all matching records in {label}.")
                                        else:
                                            # Surgical removal
                                            df_to_clean = pd.read_csv(f_path, low_memory=False)
                                            c_col = next((c for c in df_to_clean.columns if c.lower() in ['company', 'owner']), None)
                                            if c_col:
                                                original_count = len(df_to_clean)
                                                # Convert to string for comparison
                                                df_to_clean[c_col] = df_to_clean[c_col].astype(str)
                                                df_to_clean = df_to_clean[df_to_clean[c_col] != str(wipe_co)]
                                                removed = original_count - len(df_to_clean)
                                                df_to_clean.to_csv(f_path, index=False)
                                                st.write(f"Done: Removed {removed} rows from {label}.")
                                            else:
                                                st.error(f"Could not find company column in {label}. Skipping.")
                                
                                st.success("Data action completed successfully.")
                                del st.session_state['confirm_wipe']
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Operation failed: {e}")
                    with col_w2:
                        if st.button("Cancel Action"):
                            del st.session_state['confirm_wipe']
                            st.rerun()
                    
                st.divider()
                st.write("### Upload / Overwrite Data")
                uploaded_file = st.file_uploader("Upload CSV to replace/add", type=['csv'])
                if uploaded_file:
                    target_path = os.path.join(data_dir, uploaded_file.name)
                    st.warning(f"This will save/overwrite: `{target_path}`")
                    if st.button(f"Confirm Save: {uploaded_file.name}"):
                        with open(target_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        st.success(f"Saved {uploaded_file.name} to server.")
                        time.sleep(1)
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
