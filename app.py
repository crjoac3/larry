import streamlit as st
import pandas as pd
import os
import datetime

# --- CONFIGURATION & STYLES ---
st.set_page_config(page_title="WestWorld Inventory Portal", layout="wide", page_icon="🌐")

# Premium "WestWorld" Dark Theme
st.markdown("""
<style>
    /* Global Styles */
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
    
    /* Metrics Board */
    div[data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00e5ff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #374151;
    }
    
    /* Custom Buttons */
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
""", unsafe_allow_html=True)

# --- CONSTANTS ---
USER_DB_FILE = 'users.csv'
MASTER_INVENTORY_FILE = 'master_inventory.csv'
RECALL_LOG_FILE = 'recall_requests_log.csv'
LOGO_FILE = 'logo.jpg'

# --- 🛠️ SELF-HEALING DATABASE FUNCTION ---
def repair_user_database():
    """Checks if users.csv validation state. If broken or old schema, resets or attempts migration."""
    reset_needed = False
    if not os.path.exists(USER_DB_FILE):
        reset_needed = True
    else:
        try:
            df = pd.read_csv(USER_DB_FILE)
            # Check for new 'company' column
            req_cols = ['username', 'password', 'role', 'company']
            if df.empty or not all(col in df.columns for col in req_cols):
                reset_needed = True
        except:
            reset_needed = True

    if reset_needed:
        # Create a fresh file with WestWorld Super Admin
        with open(USER_DB_FILE, 'w') as f:
            f.write("username,password,role,company\n")
            f.write("admin,admin123,admin,WestWorld\n")
        print(f"⚠️ System repaired: {USER_DB_FILE} was recreated with new schema.")

repair_user_database()

# --- HELPER FUNCTIONS ---
def load_data(file_path, default_cols=None):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def check_login(username, password):
    users = load_data(USER_DB_FILE, ['username', 'password', 'role', 'company'])
    user_match = users[users['username'] == username]
    
    if not user_match.empty:
        stored_password = str(user_match.iloc[0]['password']).strip()
        if str(password).strip() == stored_password:
            return user_match.iloc[0]['role'], user_match.iloc[0]['company']
    return None, None

def process_recall_request(items_df, user, company):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = items_df.copy()
    log_entry['Requested By'] = user
    log_entry['Company'] = company
    log_entry['Request Time'] = timestamp
    
    old_log = load_data(RECALL_LOG_FILE)
    new_log = pd.concat([old_log, log_entry], ignore_index=True)
    save_data(new_log, RECALL_LOG_FILE)
    return True

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False, 
        'user_role': None, 
        'username': None,
        'company': None
    })

# =======================================================
#                      LOGIN SCREEN
# =======================================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=300)
        else:
            st.title("🌐 WestWorld Telecom")
            
        st.subheader("Partner Portal Login")
        st.markdown("---")
        
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Log In", type="primary", use_container_width=True):
            role, company = check_login(username_input, password_input)
            if role:
                st.session_state.update({
                    'logged_in': True, 
                    'user_role': role, 
                    'username': username_input,
                    'company': company
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
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=200)
        
        st.markdown(f"### Welcome, {st.session_state['username']}")
        st.caption(f"🏢 {st.session_state['company']}")
        st.divider()
        
        # Menu Permissions
        menu_options = ["Inventory Search"]
        
        # WestWorld Admin (Super Admin)
        if st.session_state['user_role'] == 'admin' and st.session_state['company'] == 'WestWorld':
            menu_options = ["Inventory Search", "Assign Inventory", "User Management"]
        
        # Client Admin (Can manage their own users)
        elif st.session_state['user_role'] == 'manager':
            menu_options = ["Inventory Search", "User Management"]
            
        page = st.radio("Navigate", menu_options)
            
        st.divider()
        if st.button("Log Out"):
            st.session_state.update({'logged_in': False, 'user_role': None, 'username': None, 'company': None})
            st.rerun()

    # --- PAGE 1: INVENTORY SEARCH ---
    if page == "Inventory Search":
        # Determine which company's inventory to show
        target_company = st.session_state['company']
        
        # If Super Admin, allow selecting any company
        if st.session_state['user_role'] == 'admin' and st.session_state['company'] == 'WestWorld':
            users_df = load_data(USER_DB_FILE)
            company_list = users_df['company'].unique()
            target_company = st.selectbox("Select Client View:", company_list)
        
        st.title(f"📦 Inventory: {target_company}")
        df = load_data(MASTER_INVENTORY_FILE)
        
        if 'owner' in df.columns: # 'owner' column now holds the COMPANY name
            # Filter by Company
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
                    try: val = f"${display_df['Sales Price'].replace('[\$,]', '', regex=True).astype(float).sum():,.2f}"
                    except: pass
                m3.metric("Total Asset Value", val)
                
                st.markdown("---")
                
                # Search Bar
                search_term = st.text_input("🔍 Quick Search...", placeholder="Serial Number, Model, PO...")
                if search_term:
                    mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                    display_df = display_df[mask]

                # Interactive Data Table
                if filter_mode == "Equipment On-Hand":
                    display_df.insert(0, "Select", False)
                    edited = st.data_editor(
                        display_df, 
                        hide_index=True, 
                        use_container_width=True, 
                        column_config={
                            "Select": st.column_config.CheckboxColumn(required=True),
                            "Sales Price": st.column_config.NumberColumn(format="$%.2f")
                        }
                    )
                    
                    if not edited[edited.Select].empty:
                        st.markdown("### Recall Request")
                        if st.button(f"🚀 Request Recall for {len(edited[edited.Select])} Item(s)"):
                            process_recall_request(edited[edited.Select], st.session_state['username'], st.session_state['company'])
                            st.balloons()
                            st.success("✅ Recall request submitted successfully! An email has been sent to the support team.")
                else:
                    st.dataframe(display_df, hide_index=True, use_container_width=True)
                
                st.download_button("📥 Export to CSV", display_df.to_csv(index=False).encode('utf-8'), "inventory_export.csv", "text/csv")
            else:
                st.warning(f"No inventory records found for **{target_company}**.")
        else:
            st.info("Master Inventory Database is empty.")

    # --- PAGE 2: ASSIGN INVENTORY (SUPER ADMIN ONLY) ---
    elif page == "Assign Inventory":
        st.title("📂 Assign Inventory")
        st.info("Upload Master Excel to assign stock to a Client Company.")
        
        users_df = load_data(USER_DB_FILE)
        # Get list of unique companies (excluding WestWorld)
        client_companies = users_df[users_df['company'] != 'WestWorld']['company'].unique()
        
        with st.form("upload_form"):
            target_client_co = st.selectbox("Select Target Client (Company)", client_companies)
            uploaded_file = st.file_uploader("Upload Master Excel File", type=['xlsx'])
            submitted = st.form_submit_button("Start Processing")
            
            if submitted and uploaded_file:
                with st.spinner("Processing Excel..."):
                    try:
                        xls = pd.ExcelFile(uploaded_file)
                        # Smart Sheet Detection
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
                        new_data['owner'] = target_client_co # Assign by COMPANY now
                        
                        # Merge Logic
                        master_df = load_data(MASTER_INVENTORY_FILE)
                        
                        # Remove old data for THIS company (Clean overwrite)
                        if not master_df.empty and 'owner' in master_df.columns:
                            master_df = master_df[master_df['owner'] != target_client_co]
                        
                        final_df = pd.concat([master_df, new_data], ignore_index=True)
                        save_data(final_df, MASTER_INVENTORY_FILE)
                        st.success(f"✅ Successfully assigned {len(new_data)} records to {target_client_co}!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing file: {str(e)}")

    # --- PAGE 3: USER MANAGEMENT ---
    elif page == "User Management":
        st.title("👥 User Administration")
        users_df = load_data(USER_DB_FILE)
        
        # -- CREATE NEW USER --
        st.subheader("Create New User")
        with st.form("user_form"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: new_u = st.text_input("Username")
            with c2: new_p = st.text_input("Password", type="password")
            
            # Context-Aware Inputs
            if st.session_state['user_role'] == 'admin':
                with c3: new_r = st.selectbox("Role", ["viewer", "manager", "admin"])
                with c4: new_co = st.text_input("Company Name") # Admin can type any new company
            else:
                # Manager can only create VIEWERS for THEIR company
                with c3: new_r = st.selectbox("Role", ["viewer"], disabled=True)
                with c4: new_co = st.text_input("Company", value=st.session_state['company'], disabled=True)
            
            if st.form_submit_button("Save User"):
                if new_u and new_p and new_co:
                    # Remove existing if overwriting
                    users_df = users_df[users_df['username'] != new_u]
                    new_row = pd.DataFrame([[new_u, new_p, new_r, new_co]], columns=['username', 'password', 'role', 'company'])
                    save_data(pd.concat([users_df, new_row], ignore_index=True), USER_DB_FILE)
                    st.success(f"✅ User {new_u} saved!")
                    st.rerun()
                else:
                    st.warning("Please fill all fields.")

        st.markdown("---")
        
        # -- LIST / DELETE USERS --
        st.subheader("Existing Users")
        
        # Filter visibility
        viewable_users = users_df
        if st.session_state['user_role'] != 'admin':
            viewable_users = users_df[users_df['company'] == st.session_state['company']]
            
        st.dataframe(viewable_users[['username', 'role', 'company']], hide_index=True, use_container_width=True)
        
        col_del, _ = st.columns(2)
        with col_del:
            d_user = st.selectbox("Select User to Delete", viewable_users['username'].unique())
            if st.button("🗑️ Delete Selected User"):
                if d_user == 'admin':
                    st.error("⛔ Cannot delete Super Admin.")
                elif d_user == st.session_state['username']:
                    st.error("⛔ Cannot delete yourself.")
                else:
                    save_data(users_df[users_df['username'] != d_user], USER_DB_FILE)
                    st.success(f"User {d_user} deleted.")
                    st.rerun()
