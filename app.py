import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Consignment Portal", layout="wide")

# --- FILE PATHS ---
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
        stored_password = str(user_match.iloc[0]['password'])
        if password == stored_password:
            return user_match.iloc[0]['role']
    return None

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'username': None})

# --- LOGIN SCREEN ---
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.header("🔐 Secure Inventory Login")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        if st.button("Log In"):
            role = check_login(username_input, password_input)
            if role:
                st.session_state.update({'logged_in': True, 'user_role': role, 'username': username_input})
                st.rerun()
            else:
                st.error("Invalid credentials")

else:
    # --- LOGGED IN DASHBOARD ---
    
    # Sidebar Info
    with st.sidebar:
        st.info(f"Logged in as: **{st.session_state['username']}**")
        
        # Navigation
        if st.session_state['user_role'] == 'admin':
            st.subheader("Admin Menu")
            page = st.radio("Navigate", ["Manage Inventory", "Manage Users", "View As..."])
        else:
            page = "My Inventory"
            
        st.divider()
        if st.button("Log Out"):
            st.session_state.update({'logged_in': False, 'user_role': None, 'username': None})
            st.rerun()

    # --- ADMIN: MANAGE USERS ---
    if page == "Manage Users":
        st.title("👥 User Management")
        users_df = load_data(USER_DB_FILE, ['username', 'password', 'role'])
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Create New User")
            with st.form("new_user"):
                new_u = st.text_input("Username")
                new_p = st.text_input("Password", type="password")
                new_r = st.selectbox("Role", ["viewer", "admin"])
                if st.form_submit_button("Create User"):
                    if new_u and new_p:
                        # Remove if exists (update)
                        users_df = users_df[users_df['username'] != new_u]
                        new_entry = pd.DataFrame([[new_u, new_p, new_r]], columns=['username', 'password', 'role'])
                        users_df = pd.concat([users_df, new_entry], ignore_index=True)
                        save_data(users_df, USER_DB_FILE)
                        st.success(f"User {new_u} created!")
                        st.rerun()
                    else:
                        st.error("Missing fields")
        
        with col_b:
            st.subheader("Existing Users")
            st.dataframe(users_df[['username', 'role']], hide_index=True)

    # --- ADMIN: MANAGE INVENTORY ---
    elif page == "Manage Inventory":
        st.title("📂 Assign Inventory")
        
        # Load Users to populate dropdown
        users_df = load_data(USER_DB_FILE, ['username'])
        client_list = users_df[users_df['role'] == 'viewer']['username'].tolist()
        
        selected_user = st.selectbox("Select Client to Update", client_list)
        
        st.write(f"Upload the Excel/CSV file destined for **{selected_user}**.")
        uploaded_file = st.file_uploader("Drop file here", type=['csv', 'xlsx'])
        
        if uploaded_file and selected_user:
            if st.button("Update This Client's Inventory"):
                # 1. Read the new file
                if uploaded_file.name.endswith('.csv'):
                    new_data = pd.read_csv(uploaded_file)
                else:
                    new_data = pd.read_excel(uploaded_file)
                
                # 2. Add 'owner' tag
                new_data['owner'] = selected_user
                
                # 3. Load Master DB
                master_df = load_data(MASTER_INVENTORY_FILE, list(new_data.columns))
                
                # 4. Remove OLD data for this specific user (Overwrite logic)
                # Keep everyone else's data, throw away selected_user's old data
                if not master_df.empty and 'owner' in master_df.columns:
                    master_df = master_df[master_df['owner'] != selected_user]
                
                # 5. Combine and Save
                updated_master = pd.concat([master_df, new_data], ignore_index=True)
                save_data(updated_master, MASTER_INVENTORY_FILE)
                
                st.success(f"Successfully updated inventory for {selected_user}!")

    # --- VIEWER: VIEW INVENTORY (Or Admin "View As") ---
    elif page == "My Inventory" or page == "View As...":
        
        # Determine whose data to show
        target_user = st.session_state['username']
        
        if page == "View As...":
            st.title("🕵️ Admin Inspection Mode")
            users_df = load_data(USER_DB_FILE, ['username'])
            target_user = st.selectbox("Select user to inspect:", users_df['username'].unique())
        else:
            st.title(f"📦 Inventory: {target_user}")

        # Load and Filter Data
        if os.path.exists(MASTER_INVENTORY_FILE):
            df = pd.read_csv(MASTER_INVENTORY_FILE)
            
            # CRITICAL: Filter data to only show rows owned by target_user
            if 'owner' in df.columns:
                user_data = df[df['owner'] == target_user].drop(columns=['owner']) # Hide 'owner' column from view
                
                if not user_data.empty:
                    # Metrics
                    c1, c2 = st.columns(2)
                    c1.metric("Total Items", len(user_data))
                    c2.metric("Unique POs", user_data['PO'].nunique() if 'PO' in user_data.columns else 0)
                    
                    # Search
                    search = st.text_input("Search...")
                    if search:
                        mask = user_data.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
                        user_data = user_data[mask]
                    
                    st.dataframe(user_data, use_container_width=True, hide_index=True)
                else:
                    st.info("No inventory found for this user.")
            else:
                st.error("Master database is corrupted (missing 'owner' column). Admin needs to re-upload data.")
        else:
            st.info("System has no inventory data yet.")
