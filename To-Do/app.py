import streamlit as st
import json
import os
from datetime import datetime, date

st.set_page_config(page_title="To-Do App", layout="centered")
st.title("📝 :blue[Simple To-Do List App]")

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def load_tasks_for_user(user):
    file = f"tasks_{user.lower().strip()}.json"
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks():
    file = f"tasks_{st.session_state.current_user.lower().strip()}.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(st.session_state.tasks, f, indent=2)

users = load_users()
st.sidebar.header("🔐 User Login")
login_option = st.sidebar.radio("Login Option", ["Login", "Register"])

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if login_option == "Login":
    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.success(f"Welcome back, {username}!")
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.session_state.tasks = load_tasks_for_user(username)
        else:
            st.error("Invalid username or password.")
else:
    if st.sidebar.button("Register"):
        if username in users:
            st.warning("Username already exists.")
        elif username and password:
            users[username] = password
            save_users(users)
            st.success("Registration successful. Please log in.")
        else:
            st.warning("Please enter both username and password.")

if not st.session_state.logged_in:
    st.stop()

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks_for_user(st.session_state.current_user)

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

new_task = st.text_input("➕ Add a new task")
due_date = st.date_input("📅 Due date (optional)")
task_type = st.selectbox(
    "📌 Select Task Type",
    ["🏫 Study", "💼 Work", "🏠 Personal", "🧹 Chores", "📚 Reading", "➕ Other"]
)

if st.button("Add Task"):
    if new_task.strip():
        st.session_state.tasks.append({
            "task": new_task.strip(),
            "completed": False,
            "type": task_type,
            "due": due_date.strftime("%Y-%m-%d")
        })
        save_tasks()
        st.rerun()

st.divider()
st.subheader("📌 Your Tasks:")

for i, task_obj in enumerate(st.session_state.tasks):
    col1, col2, col3 = st.columns([6, 2.5, 1.5])

    with col1:
        if st.session_state.edit_index == i:
            st.text_input("✏️ Task Name", value=task_obj["task"], key=f"edit_task_{i}")
        else:
            task_obj["completed"] = st.checkbox(
                f"{task_obj['task']}",
                value=task_obj["completed"],
                key=f"checkbox_{i}"
            )
            save_tasks()

    with col2:
        if st.session_state.edit_index == i:
            updated_task = st.text_input("📝 Edit Task", value=task_obj["task"], key=f"task_input_{i}")
            updated_type = st.selectbox(
             "📌 Edit Task Type",
            ["🏫 Study", "💼 Work", "🏠 Personal", "🧹 Chores", "📚 Reading", "➕ Other"],
            index=["🏫 Study", "💼 Work", "🏠 Personal", "🧹 Chores", "📚 Reading", "➕ Other"].index(task_obj.get("type", "➕ Other")),
             key=f"type_{i}"
    )
            updated_due = st.date_input("📅 Due Date", value=datetime.strptime(task_obj.get("due", date.today().strftime("%Y-%m-%d")), "%Y-%m-%d").date(), key=f"due_{i}")

            if st.button("💾 Save", key=f"save_{i}"):
                st.session_state.tasks[i] = {
                    "task": updated_task.strip(),
                    "completed": task_obj["completed"],
                    "type": task_type,
                    "due": updated_due.strftime("%Y-%m-%d"),
                }
                st.session_state.edit_index = None
                save_tasks()
                st.rerun()
        else:
            if st.button("✏️ Edit", key=f"edit_btn_{i}"):
                st.session_state.edit_index = i

    with col3:
        if st.button("🗑 Delete", key=f"delete_{i}"):
            del st.session_state.tasks[i]
            st.session_state.edit_index = None
            save_tasks()
            st.rerun()

with st.expander("📊 View All Task Information"):
    if st.session_state.tasks:
        summary_data = [
            {
                "Task": t["task"],
                "Type": t.get("type", ""),
                "Due Date": t.get("due", ""),
                "Status": "✅ Done" if t["completed"] else "🕘 Pending"
            }
            for t in st.session_state.tasks
        ]
        st.table(summary_data)
    else:
        st.info("No tasks found.")
