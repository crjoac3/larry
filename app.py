import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Consignment Portal", layout="wide")

# --- FILE PATH CONSTANTS ---
USER_DB_FILE = 'users.csv'
MASTER_INVENTORY_FILE = 'master_inventory.csv'

# --- HELPER FUNCTIONS ---
def load_data(file_path, default_cols=None):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=default_cols)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def check_login(username, password):
    users = load_data(USER_DB_FILE, ['username', 'password', 'role'])
    user_match = users[users['username'] == username]
    
    if not user_match.empty:
        # Strict string comparison to prevent type errors
        stored_password = str(user_match.iloc[0]['password']).strip()
        if str(password).strip() == stored_password:
            return user_match.iloc[0]['role']
    return None

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'username': None})

# =======================================================
#                      LOGIN SCREEN
# =======================================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📦 Consignment Portal")
        
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Log In", type="primary"):
            role = check_login(username_input, password_input)
            if role:
                st.session_state.update({'logged_in': True, 'user_role': role, 'username': username_input})
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

# =======================================================
#                  MAIN APPLICATION
# =======================================================
else:
    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.write(f"👤 **{st.session_state['username']}**")
        st.write(f"🔑 **{st.session_state['user_role'].upper()}**")
        
        st.divider()
        
        if st.session_state['user_role'] == 'admin':
            page = st.radio("Menu", ["Inventory Search", "Assign Inventory", "User Management"])
        else:
            page = "Inventory Search"
            
        st.divider()
        if st.button("Log Out"):
            st.session_state.update({'logged_in': False, 'user_role': None, 'username': None})
            st.rerun()

    # --- PAGE 1: INVENTORY SEARCH ---
    if page == "Inventory Search":
        st.title("📦 Inventory Search")
        
        # 1. Determine Viewer
        viewer = st.session_state['username']
        if st.session_state['user_role'] == 'admin':
            users_df = load_data(USER_DB_FILE)
            client_list = users_df[users_df['role'] == 'viewer']['username'].unique()
            viewer = st.selectbox("View inventory for client:", client_list)
        
        # 2. Load Data
        df = load_data(MASTER_INVENTORY_FILE)
        
        if 'owner' in df.columns:
            # Filter by Owner
            user_df = df[df['owner'] == viewer].drop(columns=['owner'])
            
            if not user_df.empty:
                # --- STATUS FILTER ---
                if 'Status' in user_df.columns:
                    status_opts = ['All'] + sorted(user_df['Status'].astype(str).unique().tolist())
                    status_filter = st.selectbox("Filter by Status:", status_opts)
                    if status_filter != 'All':
                        user_df = user_df[user_df['Status'] == status_filter]

                # --- METRICS ---
                c1, c2, c3 = st.columns(3)
                c1.metric("Items Shown", len(user_df))
                c2.metric("Unique POs", user_df['PO'].nunique() if 'PO' in user_df.columns else 0)
                
                # Calculate Total Value if Sales Price exists
                val_metric = "N/A"
                if 'Sales Price' in user_df.columns:
                    try:
                        # Clean currency strings
                        total = user_df['Sales Price'].replace('[\$,]', '', regex=True).astype(float).sum()
                        val_metric = f"${total:,.2f}"
                    except: pass
                c3.metric("Total Value", val_metric)
                
                st.divider()
                
                # --- SEARCH ---
                search_term = st.text_input("🔍 Search by Part#, Serial, PO, or Status...")
                if search_term:
                    mask = user_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                    display_df = user_df[mask]
                else:
                    display_df = user_df
                
                # --- DISPLAY ---
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # --- DOWNLOAD ---
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, f"{viewer}_inventory.csv", "text/csv")
            else:
                st.warning(f"No inventory records found for client: **{viewer}**")
        else:
            st.info("No inventory database found.")

    # --- PAGE 2: ASSIGN INVENTORY (Admin Only) ---
    elif page == "Assign Inventory":
        st.title("📂 Manage Client Inventory")
        users_df = load_data(USER_DB_FILE)
        clients = users_df[users_df['role'] == 'viewer']['username'].tolist()
        
        if not clients:
            st.warning("No clients found. Go to 'User Management' to create a viewer user first.")
            st.stop()
            
        target_client = st.selectbox("Select Client to Manage", clients)
        
        master_df = load_data(MASTER_INVENTORY_FILE)
        current_count = 0
        if not master_df.empty and 'owner' in master_df.columns:
            current_count = len(master_df[master_df['owner'] == target_client])
            
        st.caption(f"Current inventory count for **{target_client}**: {current_count} items")
        st.divider()

        tab1, tab2 = st.tabs(["📤 Upload Excel (Multi-Tab)", "🗑️ Delete All Data"])
        
        # TAB 1: EXCEL PROCESSING
        with tab1:
            st.write(f"### Update Inventory for {target_client}")
            st.info("ℹ️ Upload Master Excel. Select which tabs contain 'On Hand' vs 'Sold' data.")
            
            uploaded_file = st.file_uploader("Upload Master Excel", type=['xlsx'])
            
            if uploaded_file:
                try:
                    # Inspect Excel
                    xls = pd.ExcelFile(uploaded_file)
                    sheet_names = xls.sheet_names
                    
                    st.write("---")
                    st.subheader("⚙️ Map Your Tabs")
                    
                    c1, c2 = st.columns(2)
                    
                    # Auto-detect tabs
                    def_inv = next((i for i, n in enumerate(sheet_names) if "inventory" in n.lower() or "on hand" in n.lower()), 0)
                    def_sold = next((i for i, n in enumerate(sheet_names) if "sold" in n.lower()), 0)
                    
                    with c1: inv_sheet = st.selectbox("Select 'On Hand' Tab:", sheet_names, index=def_inv)
                    with c2: sold_sheet = st.selectbox("Select 'Sold' Tab:", sheet_names, index=def_sold)
                    
                    st.warning(f"⚠️ Clicking below will DELETE existing data for {target_client} and replace it with data from these two tabs.")
                    
                    if st.button("🔄 Process & Replace Inventory", type="primary", use_container_width=True):
                        # Load & Merge
                        df_inv = pd.read_excel(uploaded_file, sheet_name=inv_sheet)
                        df_sold = pd.read_excel(uploaded_file, sheet_name=sold_sheet)
                        
                        # Add Status if missing
                        if 'Status' not in df_inv.columns: df_inv['Status'] = 'ON HAND'
                        if 'Status' not in df_sold.columns: df_sold['Status'] = 'SOLD'
                            
                        new_data = pd.concat([df_inv, df_sold], ignore_index=True)
                        new_data['owner'] = target_client
                        
                        # Save to Database
                        master_df = load_data(MASTER_INVENTORY_FILE)
                        if not master_df.empty and 'owner' in master_df.columns:
                            master_df = master_df[master_df['owner'] != target_client]
                        
                        updated_master = pd.concat([master_df, new_data], ignore_index=True)
                        save_data(updated_master, MASTER_INVENTORY_FILE)
                        
                        st.success(f"✅ Success! Merged **{len(df_inv)}** On Hand items and **{len(df_sold)}** Sold items.")
                        st.balloons()

                except Exception as e:
                    st.error(f"Error processing Excel: {e}")

        # TAB 2: DELETE ONLY
        with tab2:
            st.write(f"### Clear Inventory for {target_client}")
            if st.button("🗑️ Clear Inventory"):
                master_df = load_data(MASTER_INVENTORY_FILE)
                if not master_df.empty and 'owner' in master_df.columns:
                    master_df = master_df[master_df['owner'] != target_client]
                    save_data(master_df, MASTER_INVENTORY_FILE)
                    st.success(f"✅ Inventory cleared for **{target_client}**.")
                    st.rerun()

    # --- PAGE 3: USER MANAGEMENT ---
    elif page == "User Management":
        st.title("👥 User Management")
        users_df = load_data(USER_DB_FILE)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("➕ Create New User")
            with st.form("add_user"):
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                new_r = st.selectbox("Role", ["viewer", "admin"])
                if st.form_submit_button("Create User"):
                    if new_u and new_p:
                        if new_u in users_df['username'].values:
                            st.error(f"User '{new_u}' already exists.")
                        else:
                            new_row = pd.DataFrame([[new_u, new_p, new_r]], columns=['username', 'password', 'role'])
                            users_df = pd.concat([users_df, new_row], ignore_index=True)
                            save_data(users_df, USER_DB_FILE)
                            st.success(f"User **{new_u}** created!")
                            st.rerun()

            st.divider()
            st.subheader("🔑 Change Password")
            with st.form("change_pwd"):
                target_user = st.selectbox("Select User", users_df['username'].unique())
                new_password = st.text_input("New Password", type="password")
                if st.form_submit_button("Update Password"):
                    if new_password:
                        idx = users_df.index[users_df['username'] == target_user].tolist()
                        if idx:
                            users_df.at[idx[0], 'password'] = new_password
                            save_data(users_df, USER_DB_FILE)
                            st.success(f"Password for **{target_user}** updated!")

        with col2:
            st.subheader("📋 Existing Users")
            st.dataframe(users_df[['username', 'role']], hide_index=True, use_container_width=True)
            st.divider()
            st.subheader("🗑️ Delete User")
            to_delete = st.selectbox("Select User to Delete", users_df['username'].unique())
            if st.button("Delete Selected User", type="primary"):
                if to_delete == st.session_state['username']: st.error("You cannot delete yourself.")
                elif to_delete == 'admin': st.error("You cannot delete the main admin.")
                else:
                    users_df = users_df[users_df['username'] != to_delete]
                    save_data(users_df, USER_DB_FILE)
                    st.success(f"User **{to_delete}** deleted.")
                    st.rerun()
