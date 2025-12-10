import streamlit as st
import pandas as pd
import os
from io import StringIO

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ciena Consignment Portal", layout="wide")

# --- FILE PATHS ---
USER_DB_FILE = 'users.csv'
MASTER_INVENTORY_FILE = 'master_inventory.csv'

# --- 🛠️ AUTOMATIC TEST DATA GENERATOR ---
# This ensures your app always has data, even after a Community Cloud restart.
def initialize_test_data():
    # 1. Create Dummy Users if missing
    if not os.path.exists(USER_DB_FILE):
        users_data = """username,password,role
admin,admin123,admin
test_user,user123,viewer
ciena_rep,ciena123,viewer"""
        with open(USER_DB_FILE, "w") as f:
            f.write(users_data)
        print("✅ Test users generated.")

    # 2. Create Dummy Inventory if missing (Based on your uploaded file)
    if not os.path.exists(MASTER_INVENTORY_FILE):
        # We assign these rows to 'test_user' so you can verify the filtering works
        inventory_data = """Part#,CLEI,Mnfr Serial,Internal Serial,PO,PO Line Number,Date,owner
NT0H02AD,LG3FGD0AAB,NNTM01GZ1BLKI,702012117,POWWT2088,92,2025-12-02,test_user
NTN433BB,SNI46F0CAA,NNTM0181BOKKA,702012118,POWWT2088,93,2025-12-02,test_user
134-0106-950 REV B,WMUIAKVBAA,T5013808,702012119,POWWT2088,94,2025-12-02,test_user
NT0H05ACE5,WMUCAJNAAH,NNTMRRR019RKG,702012120,POWWT2088,95,2025-12-02,test_user
NTN435BA,SN55F7ZAAA,NNTM014Z39EXS,702012121,POWWT2088,96,2025-12-02,ciena_rep
130-6445-905 ISS1,WMOMARNDAA,M5679586,702012122,POWWT2088,97,2025-12-02,ciena_rep"""
        with open(MASTER_INVENTORY_FILE, "w") as f:
            f.write(inventory_data)
        print("✅ Test inventory generated.")

# Run initialization immediately
initialize_test_data()

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
        # Force strict string comparison to avoid type errors
        stored_password = str(user_match.iloc[0]['password']).strip()
        if str(password).strip() == stored_password:
            return user_match.iloc[0]['role']
    return None

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'username': None})

# --- LOGIN SCREEN ---
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📦 Consignment Portal")
        st.info("Test Credentials:\n- Admin: `admin` / `admin123`\n- Client: `test_user` / `user123`")
        
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Log In", type="primary"):
            role = check_login(username_input, password_input)
            if role:
                st.session_state.update({'logged_in': True, 'user_role': role, 'username': username_input})
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

else:
    # --- LOGGED IN DASHBOARD ---
    
    # Sidebar
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

    # --- PAGE 1: INVENTORY SEARCH (Everyone) ---
    if page == "Inventory Search":
        st.title("📦 Inventory Search")
        
        # Determine filtering
        viewer = st.session_state['username']
        
        if st.session_state['user_role'] == 'admin':
            # Admin view: select user to view as
            users_df = load_data(USER_DB_FILE)
            client_list = users_df[users_df['role'] == 'viewer']['username'].unique()
            viewer = st.selectbox("View inventory for client:", client_list)
        
        # Load Data
        df = load_data(MASTER_INVENTORY_FILE)
        
        if 'owner' in df.columns:
            # FILTER: Only show rows belonging to the viewer
            user_df = df[df['owner'] == viewer].drop(columns=['owner'])
            
            if not user_df.empty:
                # Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Items", len(user_df))
                c2.metric("Unique POs", user_df['PO'].nunique() if 'PO' in user_df.columns else 0)
                c3.metric("Serial Numbers", user_df['Mnfr Serial'].nunique() if 'Mnfr Serial' in user_df.columns else 0)
                
                st.divider()
                
                # Search Bar
                search_term = st.text_input("🔍 Search by Part#, Serial, or PO...")
                
                if search_term:
                    mask = user_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                    display_df = user_df[mask]
                else:
                    display_df = user_df
                
                # Display Data
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Download Button
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download CSV",
                    csv,
                    f"{viewer}_inventory.csv",
                    "text/csv",
                    key='download-csv'
                )
            else:
                st.warning(f"No inventory records found for client: **{viewer}**")
        else:
            st.error("Master database error: 'owner' column missing.")

    # --- PAGE 2: ASSIGN INVENTORY (Admin Only) ---
    elif page == "Assign Inventory":
        st.title("📂 Assign Inventory")
        st.info("Upload an Excel/CSV file to assign it to a specific client. This will REPLACE their current inventory.")
        
        users_df = load_data(USER_DB_FILE)
        clients = users_df[users_df['role'] == 'viewer']['username'].tolist()
        
        target_client = st.selectbox("Select Client", clients)
        uploaded_file = st.file_uploader("Upload Inventory File", type=['csv', 'xlsx'])
        
        if st.button("Update Inventory", type="primary"):
            if uploaded_file and target_client:
                try:
                    # Read new file
                    if uploaded_file.name.endswith('.csv'):
                        new_data = pd.read_csv(uploaded_file)
                    else:
                        new_data = pd.read_excel(uploaded_file)
                    
                    # Tag with owner
                    new_data['owner'] = target_client
                    
                    # Load Master
                    master_df = load_data(MASTER_INVENTORY_FILE)
                    
                    # Clear old data for this client
                    if not master_df.empty and 'owner' in master_df.columns:
                        master_df = master_df[master_df['owner'] != target_client]
                    
                    # Append new data
                    updated_master = pd.concat([master_df, new_data], ignore_index=True)
                    save_data(updated_master, MASTER_INVENTORY_FILE)
                    
                    st.success(f"✅ Inventory for **{target_client}** has been updated with {len(new_data)} items.")
                except Exception as e:
                    st.error(f"Error processing file: {e}")
            else:
                st.error("Please select a client and upload a file.")

    # --- PAGE 3: USER MANAGEMENT (Admin Only) ---
    elif page == "User Management":
        st.title("👥 User Management")
        
        users_df = load_data(USER_DB_FILE)
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Create New User")
            with st.form("add_user"):
                new_u = st.text_input("Username")
                new_p = st.text_input("Password")
                new_r = st.selectbox("Role", ["viewer", "admin"])
                if st.form_submit_button("Add User"):
                    if new_u and new_p:
                        # Filter out existing user with same name
                        users_df = users_df[users_df['username'] != new_u]
                        # Add new
                        new_row = pd.DataFrame([[new_u, new_p, new_r]], columns=['username', 'password', 'role'])
                        users_df = pd.concat([users_df, new_row], ignore_index=True)
                        save_data(users_df, USER_DB_FILE)
                        st.success(f"User **{new_u}** created!")
                        st.rerun()
                    else:
                        st.error("Username and Password required.")

        with c2:
            st.subheader("Current Users")
            st.dataframe(users_df[['username', 'role']], hide_index=True, use_container_width=True)
            
            # Delete logic
            to_delete = st.selectbox("Delete User", users_df['username'].unique())
            if st.button("Delete Selected User"):
                if to_delete == 'admin':
                    st.error("Cannot delete admin.")
                else:
                    users_df = users_df[users_df['username'] != to_delete]
                    save_data(users_df, USER_DB_FILE)
                    st.success(f"Deleted {to_delete}")
                    st.rerun()
