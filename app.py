import pandas as pd
import streamlit as st

from database import DuplicateEmailError, EmployeeDatabase
from employee import Employee

st.set_page_config(page_title="Employee Management System", page_icon="👥", layout="wide")

db = EmployeeDatabase()
COLUMNS = ["ID", "Name", "Email", "Department", "Position", "Salary"]


def to_dataframe(employees):
    return pd.DataFrame(
        [[e.id, e.name, e.email, e.department, e.position, e.salary] for e in employees],
        columns=COLUMNS,
    )


def flash(message):
    """Save a message to show after the page reloads."""
    st.session_state["flash"] = message
    st.rerun()


st.title("👥 Employee Management System")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

with st.sidebar:
    st.header("Tools")
    if st.button("Load sample data"):
        added = db.load_sample_data()
        flash(f"Added {added} sample employees.")

dashboard_tab, add_tab, manage_tab = st.tabs(["📊 Dashboard", "➕ Add Employee", "🛠 Manage"])

# ---------------- Dashboard ----------------
with dashboard_tab:
    everyone = db.get_all()
    df_all = to_dataframe(everyone)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total employees", len(everyone))
    c2.metric("Departments", df_all["Department"].nunique() if everyone else 0)
    c3.metric("Average salary", f"{df_all['Salary'].mean():,.0f}" if everyone else "0")

    term = st.text_input("🔍 Search by name, email, department or position")
    shown = db.search(term) if term else everyone

    if shown:
        st.dataframe(to_dataframe(shown), use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download CSV",
            data=db.to_csv(shown),
            file_name="employees.csv",
            mime="text/csv",
        )
    else:
        st.info("No employees found. Add one, or click 'Load sample data' in the sidebar.")

    if everyone:
        st.subheader("Employees per department")
        st.bar_chart(df_all["Department"].value_counts())

# ---------------- Add ----------------
with add_tab:
    st.subheader("Add a new employee")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name")
        email = st.text_input("Email")
        department = st.text_input("Department")
        position = st.text_input("Position")
        salary = st.number_input("Salary", min_value=0.0, step=1000.0, value=50000.0)
        submitted = st.form_submit_button("Add employee")

    if submitted:
        try:
            db.add(Employee(name, email, department, position, salary))
            flash(f"{name.strip()} was added.")
        except (ValueError, DuplicateEmailError) as error:
            st.error(str(error))

# ---------------- Manage ----------------
with manage_tab:
    st.subheader("Edit or delete an employee")
    people = db.get_all()

    if not people:
        st.info("There are no employees yet.")
    else:
        chosen = st.selectbox(
            "Choose an employee", people, format_func=lambda e: f"{e.id} - {e.name}"
        )
        key = chosen.id

        with st.form(f"edit_form_{key}"):
            new_name = st.text_input("Name", chosen.name)
            new_email = st.text_input("Email", chosen.email)
            new_department = st.text_input("Department", chosen.department)
            new_position = st.text_input("Position", chosen.position)
            new_salary = st.number_input(
                "Salary", min_value=0.0, step=1000.0, value=float(chosen.salary)
            )
            save = st.form_submit_button("Save changes")

        if save:
            try:
                db.update(
                    Employee(new_name, new_email, new_department, new_position,
                             new_salary, id=chosen.id)
                )
                flash("Employee updated.")
            except (ValueError, DuplicateEmailError) as error:
                st.error(str(error))

        st.divider()
        confirm = st.checkbox("Yes, I want to delete this employee", key=f"confirm_{key}")
        if st.button("🗑 Delete employee"):
            if confirm:
                db.delete(chosen.id)
                flash(f"{chosen.name} was deleted.")
            else:
                st.warning("Tick the confirm box first.")