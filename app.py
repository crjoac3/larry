import streamlit as st
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(page_title="Consignment Inventory", layout="wide")

# 2. Simple Authentication Function
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct
        return True

# 3. Main Application Logic
if check_password():
    st.title("📦 Ciena Consignment Receipts")
    
    # Sidebar for File Upload
    st.sidebar.header("Data Management")
    uploaded_file = st.sidebar.file_uploader("Upload updated Excel/CSV", type=['xlsx', 'csv'])

    # Logic to load data
    df = pd.DataFrame() # Empty dataframe placeholder
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        # Fallback: You can keep a 'default.csv' in the folder if you want data to load automatically
        # For now, we ask the user to upload.
        st.info("Please upload the latest spreadsheet using the sidebar to view data.")

    # 4. Data Display
    if not df.empty:
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items", len(df))
        col2.metric("Unique POs", df['PO'].nunique() if 'PO' in df.columns else 0)
        col3.metric("Unique Parts", df['Part#'].nunique() if 'Part#' in df.columns else 0)

        st.markdown("---")
        
        # Search Filter
        st.subheader("Search Inventory")
        search_term = st.text_input("Search by Serial Number, PO, or Part#")

        # Filtering Logic
        if search_term:
            # Convert whole dataframe to string to search everywhere
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df

        # Interactive Table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        # Download Button
        st.download_button(
            label="Download Data as CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='filtered_consignment_data.csv',
            mime='text/csv',
        )