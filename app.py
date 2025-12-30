import streamlit as st
import pandas as pd
import os
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="WestWorld Inventory Portal", layout="wide", page_icon="🌐")

# --- CONSTANTS ---
USER_DB_FILE = 'users.csv'
MASTER_INVENTORY_FILE = 'master_inventory.csv'
RECALL_LOG_FILE = 'recall_requests_log.csv'
LOGO_FILE = 'logo.jpg'

# --- 🛠️ SELF-HEALING DATABASE FUNCTION ---
def repair_user_database():
    """Checks if users.csv is valid. If broken, resets it."""
    reset_needed = False
    
    # Check 1: Does file exist?
    if not os.path.exists(USER_DB_FILE):
        reset_needed = True
    
    # Check 2: Is it empty or missing headers?
    else:
        try:
            df = pd.read_csv(USER_DB_FILE)
            if df.empty or 'username' not in df.columns:
                reset_needed = True
        except:
            reset_needed = True

    if reset_needed:
        # Create a fresh file with default admin
        with open(USER_DB_FILE, 'w') as f:
            f.write("username,password,role\n")
            f.write("admin,admin123,admin\n")
        print(f"⚠️ System repaired: {USER_DB_FILE} was recreated.")

# Run repair immediately on launch
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
    users = load_data(USER_DB_FILE, ['username', 'password', 'role'])
    user_match = users[users['username'] == username]
    
    if not user_match.empty:
        # Robust password check (handles numbers/text/whitespace)
        stored_password = str(user_match.iloc[0]['password']).strip()
        if str(password).strip() == stored_password:
            return user_match.iloc[0]['role']
    return None

def process_recall_request(items_df, user):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = items_df.copy()
    log_entry['Requested By'] = user
    log_entry['Request Time'] = timestamp
    
    old_log = load_data(RECALL_LOG_FILE)
    new_log = pd.concat([old_log, log_entry], ignore_index=True)
    save_data(new_log, RECALL_LOG_FILE)
    return True

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'username': None})

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
            
        st.subheader("Partner Login")
        
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Log In", type="primary"):
            role = check_login(username_input, password_input)
            if role:
                st.session_state.update({'logged_in': True, 'user_role': role, 'username': username_input})
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

# =======================================================
#                  MAIN DASHBOARD
# =======================================================
else:
    with st.sidebar:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=200)
        st.write(f"👤 **{st.session_state['username']}**")
        st.divider()
        
        if st.session_state['user_role'] in ['admin', 'manager']:
            page = st.radio("Menu", ["Inventory Search", "Assign Inventory", "User Management"])
        else:
            page = "Inventory Search"
            
        st.divider()
        if st.button("Log Out"):
            st.session_state.update({'logged_in': False, 'user_role': None, 'username': None})
            st.rerun()

    # --- PAGE 1: INVENTORY SEARCH ---
    if page == "Inventory Search":
        viewer = st.session_state['username']
        if st.session_state['user_role'] in ['admin', 'manager']:
            users_df = load_data(USER_DB_FILE)
            client_list = users_df[users_df['role'] == 'viewer']['username'].unique()
            viewer = st.selectbox("Select Partner:", client_list)
        
        st.title(f"📦 Inventory: {viewer}")
        df = load_data(MASTER_INVENTORY_FILE)
        
        if 'owner' in df.columns:
            user_df = df[df['owner'] == viewer].drop(columns=['owner'])
            
            if not user_df.empty:
                filter_mode = st.radio("View:", ["All Equipment Received", "Equipment On-Hand", "Equipment Sold"], horizontal=True)
                display_df = user_df.copy()
                
                # Filters
                if filter_mode == "Equipment On-Hand":
                    if 'Status' in display_df.columns:
                        display_df = display_df[display_df['Status'].astype(str).str.upper().str.contains("ON HAND") | display_df['Status'].isnull()]
                elif filter_mode == "Equipment Sold":
                    if 'Status' in display_df.columns:
                        display_df = display_df[display_df['Status'].astype(str).str.upper().str.contains("SOLD")]

                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Items", len(display_df))
                po_label = "Unique Sales Orders" if filter_mode == "Equipment Sold" else "Unique POs"
                m2.metric(po_label, display_df['PO'].nunique() if 'PO' in display_df.columns else 0)
                
                val = "N/A"
                if 'Sales Price' in display_df.columns:
                    try: val = f"${display_df['Sales Price'].replace('[\$,]', '', regex=True).astype(float).sum():,.2f}"
                    except: pass
                m3.metric("Total Value", val)
                
                st.markdown("---")
                
                # Search
                search = st.text_input("🔍 Search...")
                if search:
                    mask = display_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
                    display_df = display_df[mask]

                # Actions
                if filter_mode == "Equipment On-Hand":
                    display_df.insert(0, "Select", False)
                    edited = st.data_editor(display_df, hide_index=True, use_container_width=True, column_config={"Select": st.column_config.CheckboxColumn(required=True)})
                    if not edited[edited.Select].empty and st.button("🚀 Submit Recall Request"):
                        process_recall_request(edited[edited.Select], viewer)
                        st.success("Request Sent!")
                else:
                    st.dataframe(display_df, hide_index=True, use_container_width=True)
                
                st.download_button("📥 Download CSV", display_df.to_csv(index=False).encode('utf-8'), "inventory.csv", "text/csv")
            else:
                st.warning("No records found.")
        else:
            st.info("Database empty.")

    # --- PAGE 2: ASSIGN INVENTORY ---
    elif page == "Assign Inventory":
        st.title("📂 Assign Inventory")
        users_df = load_data(USER_DB_FILE)
        target_client = st.selectbox("Select Partner", users_df[users_df['role'] == 'viewer']['username'].unique())
        uploaded_file = st.file_uploader("Upload Master Excel", type=['xlsx'])
        
        if uploaded_file and st.button("Process & Replace"):
            try:
                xls = pd.ExcelFile(uploaded_file)
                inv_s = next((s for s in xls.sheet_names if "inv" in s.lower() or "hand" in s.lower()), xls.sheet_names[0])
                sold_s = next((s for s in xls.sheet_names if "sold" in s.lower()), None)
                
                df_inv = pd.read_excel(uploaded_file, sheet_name=inv_s)
                if 'Status' not in df_inv.columns: df_inv['Status'] = 'ON HAND'
                frames = [df_inv]
                
                if sold_s:
                    df_sold = pd.read_excel(uploaded_file, sheet_name=sold_s)
                    if 'Status' not in df_sold.columns: df_sold['Status'] = 'SOLD'
                    frames.append(df_sold)
                
                new_data = pd.concat(frames, ignore_index=True)
                new_data['owner'] = target_client
                
                master_df = load_data(MASTER_INVENTORY_FILE)
                if not master_df.empty and 'owner' in master_df.columns:
                    master_df = master_df[master_df['owner'] != target_client]
                
                save_data(pd.concat([master_df, new_data], ignore_index=True), MASTER_INVENTORY_FILE)
                st.success("Updated!")
            except Exception as e: st.error(f"Error: {e}")

    # --- PAGE 3: USER MANAGEMENT ---
    elif page == "User Management":
        st.title("👥 User Administration")
        users_df = load_data(USER_DB_FILE)
        c1, c2 = st.columns(2)
        with c1:
            with st.form("user_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                r = st.selectbox("Role", ["viewer", "admin", "manager"])
                if st.form_submit_button("Save User"):
                    users_df = users_df[users_df['username'] != u]
                    new_row = pd.DataFrame([[u, p, r]], columns=['username', 'password', 'role'])
                    save_data(pd.concat([users_df, new_row], ignore_index=True), USER_DB_FILE)
                    st.success("Saved!")
                    st.rerun()
        with c2:
            st.dataframe(users_df[['username', 'role']], hide_index=True)
            d = st.selectbox("Delete User", users_df['username'].unique())
            if st.button("Delete"):
                if d != 'admin' and d != st.session_state['username']:
                    save_data(users_df[users_df['username'] != d], USER_DB_FILE)
                    st.success("Deleted")
                    st.rerun()
