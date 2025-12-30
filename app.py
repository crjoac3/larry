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
LOGO_FILE = 'logo.png'  # Place your WestWorld logo file in the same folder

# Email recipients for Recall Requests
RECALL_RECIPIENTS = [
    "mburch@westworldtelecom.com",
    "Larry.glenn@westworldtelecom.com",
    "Justin.cooley@westworldtelecom.com"
]

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
        stored_password = str(user_match.iloc[0]['password']).strip()
        if str(password).strip() == stored_password:
            return user_match.iloc[0]['role']
    return None

def process_recall_request(items_df, user):
    """
    Logs the recall request and simulates sending an email.
    In a real deployment, add SMTP code here.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Log to local CSV
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
        # Logo Display
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=300)
        else:
            st.title("🌐 WestWorld Telecom")
            
        st.subheader("Consignment Partner Portal")
        
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
    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=200)
        st.markdown("### User Profile")
        st.write(f"👤 **{st.session_state['username']}**")
        st.write(f"🔑 **{st.session_state['user_role'].replace('_', ' ').title()}**")
        
        st.divider()
        
        # Navigation Logic
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
        
        # 1. Determine Viewer Context
        viewer = st.session_state['username']
        if st.session_state['user_role'] in ['admin', 'manager']:
            users_df = load_data(USER_DB_FILE)
            client_list = users_df[users_df['role'] == 'viewer']['username'].unique()
            viewer = st.selectbox("Select Consignment Partner:", client_list)
        
        st.title(f"📦 Inventory: {viewer}")
        st.markdown("---")

        # 2. Load & Filter Data
        df = load_data(MASTER_INVENTORY_FILE)
        
        if 'owner' in df.columns:
            # Basic Owner Filter
            user_df = df[df['owner'] == viewer].drop(columns=['owner'])
            
            if not user_df.empty:
                # --- NEW FILTER LOGIC ---
                filter_mode = st.radio(
                    "Select View:", 
                    ["All Equipment Received", "Equipment On-Hand", "Equipment Sold"], 
                    horizontal=True
                )
                
                display_df = user_df.copy()
                
                # Apply Status Filters
                if filter_mode == "Equipment On-Hand":
                    # Filter for 'ON HAND' or Empty status
                    if 'Status' in display_df.columns:
                        display_df = display_df[
                            display_df['Status'].astype(str).str.upper().str.contains("ON HAND") | 
                            display_df['Status'].isnull()
                        ]
                elif filter_mode == "Equipment Sold":
                    # Filter for 'SOLD'
                    if 'Status' in display_df.columns:
                        display_df = display_df[
                            display_df['Status'].astype(str).str.upper().str.contains("SOLD")
                        ]
                # 'All Equipment Received' shows everything (no filter applied)

                # --- METRICS ---
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Line Items", len(display_df))
                
                # Dynamic Metric Label
                po_label = "Unique Sales Orders" if filter_mode == "Equipment Sold" else "Unique POs"
                m2.metric(po_label, display_df['PO'].nunique() if 'PO' in display_df.columns else 0)
                
                # Financials
                val_metric = "N/A"
                if 'Sales Price' in display_df.columns:
                    try:
                        total = display_df['Sales Price'].replace('[\$,]', '', regex=True).astype(float).sum()
                        val_metric = f"${total:,.2f}"
                    except: pass
                m3.metric("Total Value", val_metric)

                st.markdown("---")

                # --- SEARCH ---
                search_term = st.text_input("🔍 Search by Part#, Serial, PO, or Status...")
                if search_term:
                    mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                    display_df = display_df[mask]

                # --- DISPLAY & ACTIONS ---
                
                # Feature: RECALL REQUEST (Only for On-Hand)
                if filter_mode == "Equipment On-Hand":
                    st.info("ℹ️ Select items below to request a Recall / Return Shipping.")
                    
                    # Add selection column using Streamlit Data Editor
                    # This creates the checkboxes naturally
                    display_df.insert(0, "Select", False)
                    edited_df = st.data_editor(
                        display_df, 
                        hide_index=True, 
                        use_container_width=True,
                        column_config={"Select": st.column_config.CheckboxColumn(required=True)}
                    )
                    
                    # Find selected rows
                    selected_rows = edited_df[edited_df.Select]
                    
                    if not selected_rows.empty:
                        st.write(f"**{len(selected_rows)} items selected for recall.**")
                        if st.button("🚀 Submit Recall Request", type="primary"):
                            with st.spinner("Processing request..."):
                                success = process_recall_request(selected_rows, viewer)
                                if success:
                                    st.success(f"✅ Request Submitted! A notification has been sent to: {', '.join(RECALL_RECIPIENTS)}")
                                    st.balloons()
                else:
                    # Read-only view for Sold/All
                    st.dataframe(display_df, use_container_width=True, hide_index=True)

                # --- EXPORT ---
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=display_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"{viewer}_{filter_mode.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No records found for this partner.")
        else:
            st.error("Database Error: 'owner' column missing.")

    # --- PAGE 2: ASSIGN INVENTORY ---
    elif page == "Assign Inventory":
        st.title("📂 Assign Inventory")
        users_df = load_data(USER_DB_FILE)
        clients = users_df[users_df['role'] == 'viewer']['username'].tolist()
        
        target_client = st.selectbox("Select Partner to Update", clients)
        
        st.info("Upload Master Excel File (containing 'Inventory' and 'Sold' tabs).")
        uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])
        
        if uploaded_file and st.button("Process & Replace Inventory", type="primary"):
            try:
                xls = pd.ExcelFile(uploaded_file)
                # Smart sheet detection
                inv_sheet = next((s for s in xls.sheet_names if "inv" in s.lower() or "hand" in s.lower()), xls.sheet_names[0])
                sold_sheet = next((s for s in xls.sheet_names if "sold" in s.lower()), None)
                
                df_inv = pd.read_excel(uploaded_file, sheet_name=inv_sheet)
                if 'Status' not in df_inv.columns: df_inv['Status'] = 'ON HAND'
                
                frames = [df_inv]
                
                if sold_sheet:
                    df_sold = pd.read_excel(uploaded_file, sheet_name=sold_sheet)
                    if 'Status' not in df_sold.columns: df_sold['Status'] = 'SOLD'
                    frames.append(df_sold)
                
                new_data = pd.concat(frames, ignore_index=True)
                new_data['owner'] = target_client
                
                # Overwrite Logic
                master_df = load_data(MASTER_INVENTORY_FILE)
                if not master_df.empty and 'owner' in master_df.columns:
                    master_df = master_df[master_df['owner'] != target_client]
                
                updated_master = pd.concat([master_df, new_data], ignore_index=True)
                save_data(updated_master, MASTER_INVENTORY_FILE)
                st.success(f"✅ Successfully updated {target_client} with {len(new_data)} total items.")
                
            except Exception as e:
                st.error(f"Error: {e}")

    # --- PAGE 3: USER MANAGEMENT ---
    elif page == "User Management":
        st.title("👥 User Administration")
        users_df = load
