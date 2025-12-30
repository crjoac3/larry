import streamlit as st
import pandas as pd
import os
import datetime
import json

# --- CONFIGURATION & STYLES ---
st.set_page_config(page_title="WestWorld Inventory Portal (v2.2)", layout="wide", page_icon="🌐")

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
            # Check for new 'company' and 'email' columns
            req_cols = ['username', 'password', 'role', 'company', 'email']
            
            # Migration Logic: Add missing columns if file exists but schema is old
            if not df.empty:
                save_required = False
                if 'company' not in df.columns:
                    df['company'] = 'WestWorld' # Default fallback
                    save_required = True
                if 'email' not in df.columns:
                    df['email'] = '' # Default empty
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
            f.write("username,password,role,company,email\n")
            f.write("admin,admin123,admin,WestWorld,admin@westworld.com\n")
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
    users = load_data(USER_DB_FILE, ['username', 'password', 'role', 'company', 'email'])
    user_match = users[users['username'] == username]
    
    if not user_match.empty:
        stored_password = str(user_match.iloc[0]['password']).strip()
        if str(password).strip() == stored_password:
            return user_match.iloc[0]['role'], user_match.iloc[0]['company']
    return None, None

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {"email_rules": []}

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
                
    return ", ".join(recipients) if recipients else "No Notification Configured"

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
            st.title("🌐 WestWorld Telecom (v2.2)")
            
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
        menu_options = ["Inventory Search", "Recall Management"]
        
        # WestWorld Admin (Super Admin)
        if st.session_state['user_role'] == 'admin' and st.session_state['company'] == 'WestWorld':
            menu_options = ["Inventory Search", "Recall Management", "Assign Inventory", "User Management", "Settings"]
        
        # Client Admin (Can manage their own users)
        elif st.session_state['user_role'] == 'manager':
            menu_options = ["Inventory Search", "Recall Management", "User Management"]
            
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
                            emails = process_recall_request(edited[edited.Select], st.session_state['username'], target_company)
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
            if st.session_state['company'] != 'WestWorld':
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
                                    
                                    # 2. Add back to Master Inventory
                                    clean_row = row.drop(labels=['Mark Received', 'Restock', 'Requested By', 'Company', 'Request Time', 'Status', 'Select'], errors='ignore')
                                    
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


    # --- PAGE 3: ASSIGN INVENTORY (SUPER ADMIN ONLY) ---
    elif page == "Assign Inventory":
        st.title("📂 Assign Inventory")
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

    # --- PAGE 4: USER MANAGEMENT ---
    elif page == "User Management":
        st.title("👥 User Administration")
        users_df = load_data(USER_DB_FILE)
        
        st.subheader("Create New User")
        with st.form("user_form"):
            c1, c2, c3 = st.columns(3)
            c4, c5 = st.columns(2)
            
            with c1: new_u = st.text_input("Username")
            with c2: new_p = st.text_input("Password", type="password")
            with c3: new_email = st.text_input("Email (For Recovery)")
            
            if st.session_state['user_role'] == 'admin':
                with c4: new_r = st.selectbox("Role", ["viewer", "manager", "admin"])
                with c5: new_co = st.text_input("Company Name")
            else:
                with c4: new_r = st.selectbox("Role", ["viewer"], disabled=True)
                with c5: new_co = st.text_input("Company", value=st.session_state['company'], disabled=True)
            
            if st.form_submit_button("Save User"):
                if new_u and new_p and new_co:
                    users_df = users_df[users_df['username'] != new_u]
                    # Ensure 'email' column exists in dataframe before appending
                    if 'email' not in users_df.columns: users_df['email'] = ''
                    
                    new_row = pd.DataFrame([[new_u, new_p, new_r, new_co, new_email]], columns=['username', 'password', 'role', 'company', 'email'])
                    save_data(pd.concat([users_df, new_row], ignore_index=True), USER_DB_FILE)
                    st.success(f"✅ User {new_u} saved!")
                    st.rerun()
                else:
                    st.warning("Please fill all fields (Username, Password, Company).")

        st.markdown("---")
        st.subheader("Existing Users")
        viewable_users = users_df
        if st.session_state['user_role'] != 'admin':
            viewable_users = users_df[users_df['company'] == st.session_state['company']]
            
        st.dataframe(viewable_users[['username', 'role', 'company', 'email']], hide_index=True, width="stretch")
        
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
                    
    # --- PAGE 5: ADMIN SETTINGS ---
    elif page == "Settings":
        st.title("⚙️ Portal Settings")
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
                        save_settings({"email_rules": rules})
                        st.success(f"Added {r_email} for {r_company}")
                        st.rerun()
                    else:
                        st.warning("Rule already exists.")
                else:
                    st.error("Invalid email address.")
