# frontend.py
import streamlit as st
import requests
import pandas as pd
from datetime import date

# Connect to our local backend
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="HRMS Lite", layout="wide")

st.title("🏢 HRMS Lite System")

# Sidebar Navigation
menu = st.sidebar.selectbox("Menu", ["Employee Management", "Attendance Tracking"])

# --- PAGE 1: Employee Management ---
if menu == "Employee Management":
    st.header("👥 Employee Management")

    # Form to Add Employee
    with st.expander("➕ Add New Employee"):
        c1, c2 = st.columns(2)
        e_id = c1.text_input("Employee ID (e.g., E001)")
        name = c2.text_input("Full Name")
        email = c1.text_input("Email")
        dept = c2.text_input("Department")
        
        if st.button("Add Employee"):
            if e_id and name and email:
                res = requests.post(f"{API_URL}/employees/", json={
                    "emp_id_str": e_id, "name": name, "email": email, "department": dept
                })
                if res.status_code == 200:
                    st.success("Employee Added!")
                else:
                    st.error(f"Error: {res.json().get('detail')}")
            else:
                st.warning("Please fill all fields")

    # List Employees
    st.subheader("Employee List")
    if st.button("Refresh List"):
        st.session_state['refresh'] = True

    try:
        res = requests.get(f"{API_URL}/employees/")
        if res.status_code == 200:
            emp_data = res.json()
            if emp_data:
                df = pd.DataFrame(emp_data)
                # Display as Table
                st.dataframe(df[["emp_id_str", "name", "email", "department"]], use_container_width=True)
                
                # Delete Section
                st.divider()
                del_id = st.selectbox("Select Employee to Delete", [e['emp_id_str'] for e in emp_data])
                if st.button("Delete Selected Employee"):
                    requests.delete(f"{API_URL}/employees/{del_id}")
                    st.rerun() # Refresh page
            else:
                st.info("No employees found.")
    except:
        st.error("Backend is not running!")

# --- PAGE 2: Attendance Tracking ---
elif menu == "Attendance Tracking":
    st.header("📅 Attendance Management")

    # Fetch Employees for Dropdown
    try:
        employees = requests.get(f"{API_URL}/employees/").json()
        emp_options = {e['name']: e['emp_id_str'] for e in employees}
    except:
        emp_options = {}

    if emp_options:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Mark Attendance")
            selected_name = st.selectbox("Select Employee", list(emp_options.keys()))
            selected_id = emp_options[selected_name]
            
            att_date = st.date_input("Date", date.today())
            status = st.radio("Status", ["Present", "Absent"])
            
            if st.button("Submit Attendance"):
                payload = {
                    "emp_id_str": selected_id,
                    "date": str(att_date),
                    "status": status
                }
                res = requests.post(f"{API_URL}/attendance/", json=payload)
                if res.status_code == 200:
                    st.success("Marked!")
                else:
                    st.error("Failed")

        with col2:
            st.subheader(f"History for {selected_name}")
            # Fetch History
            hist = requests.get(f"{API_URL}/attendance/{selected_id}").json()
            if hist:
                df_hist = pd.DataFrame(hist)
                # Color code: Green for Present, Red for Absent
                def color_status(val):
                    color = '#d4edda' if val == 'Present' else '#f8d7da'
                    return f'background-color: {color}'
                
                st.dataframe(df_hist[["date", "status"]].style.applymap(color_status, subset=['status']), use_container_width=True)
            else:
                st.info("No attendance records found.")
    else:
        st.warning("Please add employees first.")