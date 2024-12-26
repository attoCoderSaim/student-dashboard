from tkinter import *
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta
import json
import re
import os
import time
import requests

window = Tk()
window.title("Student Dashboard")

icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
window.iconbitmap(icon_path)

with open('view.json', 'r') as file:
    data = json.load(file) 

main_view = data.get('view_option')

if (main_view == 0):
    window.geometry("800x700")
    window.resizable(False, False)
else:
    window.geometry("1200x800")
    window.state('zoomed')
    window.resizable(False, True)

days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
periods = ['Period 1', 'Period 2', 'Period 3', 'Period 4', 'Period 5', 'Period 6', 'Period 7', 'Period 8', 'Period 9']
routine_file = "routine.json"
routine = {}
course_file = "courses.json"
courses = {}
assignment_file = "assignments.json"
assignments = {}

frame = None
entries = {}
course_entries = {}
assignment_entries = []

entry_hour = None
entry_minute = None
entry_second = None
countdown_label = None

todos = []
entry = None
listbox = None
to_do_count = 0

quote = ""

now = datetime.now()
if now.hour >= 17:
    next_day = now + timedelta(days=1)
else:
    next_day = now

next_day_name = next_day.strftime('%A')
today = now.strftime('%A')

if next_day_name in ['Thursday', 'Friday']:
    next_day_name = 'Saturday'

def set_label_style(label):
    label.config(font=("Verdana", 10))

def set_title_style(label):
    label.config(font=("Verdana", 10, "bold"))

def homepage():
    global frame, now
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    title = Label(frame, text="Student Dashboard", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    buttons = [
        ("Daily Routine", show_routine),
        ("Upcoming Sessional", show_nextlab),
        ("Assignments", show_assignments),
        ("To-Do List", show_todo_list),
        ("Set Reminder", show_reminder),
        ("Settings", settings),
    ]

    for (text, command) in buttons:
        button = Button(frame, text=text, command=command, width=25, height=2, font=("Verdana", 12))
        button.pack(pady=10)

    # Daily Quote
    quote = get_random_quote()
    quote_label = Label(frame, text="Daily Quote:", font=("Verdana", 12, "bold"))
    quote_label.pack(pady=20)
    quote_text = Label(frame, text=quote, wraplength=600, font=("Verdana", 10))
    quote_text.pack()

def dashboard():
    global frame, entry, listbox, entry_hour, entry_minute, entry_second, countdown_label, now, next_day_name
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    frame1 = Frame(frame, relief="groove")
    frame1.pack(side='left', fill="both", expand=True)
    frame2 = Frame(frame, relief="groove")
    frame2.pack(side='left', fill="both", expand=True)
    frame3 = Frame(frame, relief="groove")
    frame3.pack(side='right', fill="both", expand=True)

    routine_frame = Frame(frame2, borderwidth=4, relief="groove")
    routine_frame.pack_propagate(False) 
    todo_frame = Frame(frame1, borderwidth=4, relief="groove")
    todo_frame.pack_propagate(False)        
    reminder_frame = Frame(frame3, borderwidth=4, relief="groove")
    reminder_frame.pack_propagate(False)
    quote_frame = Frame(frame2, borderwidth=4, relief="groove")
    quote_frame.pack_propagate(False)
    assignment_frame = Frame(frame1, borderwidth=4, relief="groove")
    assignment_frame.pack_propagate(False)
    nextlab_frame = Frame(frame3, borderwidth=4, relief="groove")
    nextlab_frame.pack_propagate(False)

    routine_frame.pack(side="top", fill="both", expand=True)
    todo_frame.pack(side="bottom", fill="both", expand=True)
    reminder_frame.pack(side="bottom", fill="both", expand=True)
    quote_frame.pack(side="bottom", fill="both", expand=True)
    assignment_frame.pack(side="top", fill="both", expand=True)
    nextlab_frame.pack(side="top", fill="both", expand=True)

    ### Routine
    label = Label(routine_frame, text=f"Today's date: {now.strftime('%Y-%m-%d')}")
    set_title_style(label)
    label.pack()

    routine_day = routine.get(next_day_name, "No routine")

    if now.hour >= 17 or today == 'Friday':
        routine_label = Label(routine_frame, text=f"Tomorrow's routine ({next_day_name}):")
    elif today == 'Thursday':
        routine_label = Label(routine_frame, text=f"Day after tomorrow's routine ({next_day_name}):")
    else:
        routine_label = Label(routine_frame, text=f"Today's routine ({next_day_name}):")
    
    set_label_style(routine_label)
    routine_label.pack()

    if isinstance(routine_day, dict):
        for period, course_num in routine_day.items():
            course_details = courses.get(f"Course {course_num}", {})
            course_code = course_details.get("code", "")
            course_title = course_details.get("title", "")
            period_label = Label(routine_frame, text=f"{period}: {course_code} - {course_title}", wraplength=500)
            set_label_style(period_label)
            period_label.pack()
    else:
        no_routine_label = Label(routine_frame, text=routine_day)
        set_label_style(no_routine_label)
        no_routine_label.pack()

    ### To do
    todo_label = Label(todo_frame, text="To Do List")
    set_title_style(todo_label)
    todo_label.pack()

    entry = Entry(todo_frame, width=40)
    entry.pack(pady=5)

    add_button = Button(todo_frame, text="Add", command=add_todo)
    add_button.pack(pady=5)

    listbox = Listbox(todo_frame, width=40)
    listbox.pack(pady=5)

    delete_button = Button(todo_frame, text="Delete", command=delete_todo)
    delete_button.pack(pady=5)

    save_button = Button(todo_frame, text="Save", command=save_todos)
    save_button.pack(pady=5)

    load_todos()

    ## Reminder
    reminder_label = Label(reminder_frame, text="Set Reminder")
    set_title_style(reminder_label)
    reminder_label.pack()

    hour_label = Label(reminder_frame, text="Hour:")
    set_label_style(hour_label)
    hour_label.pack()
    entry_hour = Entry(reminder_frame, width=30, justify="center")
    entry_hour.pack(pady=5)

    minute_label = Label(reminder_frame, text="Minute:")
    set_label_style(minute_label)
    minute_label.pack()
    entry_minute = Entry(reminder_frame, width=30, justify="center")
    entry_minute.pack(pady=5)

    second_label = Label(reminder_frame, text="Second:")
    set_label_style(second_label)
    second_label.pack()
    entry_second = Entry(reminder_frame, width=30, justify="center")
    entry_second.pack(pady=5)

    clear_button = Button(reminder_frame, text="Clear", command=clear_entries)
    clear_button.pack(pady=5)

    set_reminder_button = Button(reminder_frame, text="Set Reminder", command=set_reminder)
    set_reminder_button.pack(pady=5)

    countdown_label = Label(reminder_frame, text="")
    set_label_style(countdown_label)
    countdown_label.pack()

    ## Assignments
    assignment_label = Label(assignment_frame, text="Assignments")
    set_title_style(assignment_label)
    assignment_label.pack()
    
    assignment_Cnt = 0

    for i, (assignment_key, assignment_value) in enumerate(assignments.items()):
        code = assignment_value.get('code', '')
        name = assignment_value.get('name', '')
        submission_date = assignment_value.get('submission_date', '')

        if code.strip() or name.strip() or submission_date.strip():
            assignment_text = f"{assignment_key}: {code} - {name}, Due: {submission_date}"
            assignment_entry = Label(assignment_frame, text=assignment_text, wraplength=500)
            set_label_style(assignment_entry)
            assignment_entry.pack()
            assignment_Cnt += 1
    if (assignment_Cnt == 0):
        assignment_entry = Label(assignment_frame, text='Chill! No pending Addignments!!!')
        set_label_style(assignment_entry)
        assignment_entry.pack()

    ## Next Lab
    routine_day = routine.get(next_day_name)
    upcoming_sessional = None
    routine_day = routine.get(next_day_name)
    upcoming_sessional = None

    if routine_day:
        for period, course_num in routine_day.items():
            course_details = courses.get(f"Course {course_num}", {})
            course_code = course_details.get("code", "")
            match = re.search(r'\d+', course_code)
            if match:
                course_number = int(match.group())
                if course_number % 2 == 0:
                    upcoming_sessional = f"{period}: {course_code} - {course_details.get('title', '')}"
                    break
    next_lab_label = Label(nextlab_frame, text="Upcoming Sessional:")
    set_title_style(next_lab_label)
    next_lab_label.pack()
    if upcoming_sessional:
        sessional_info_label = Label(nextlab_frame, text=upcoming_sessional, wraplength=500)
        set_label_style(sessional_info_label)
        sessional_info_label.pack()
    else:
        no_sessional_label = Label(nextlab_frame, text="No upcoming sessional for the next day.")
        set_label_style(no_sessional_label)
        no_sessional_label.pack()

    quote = get_random_quote()

    quote_label = Label(quote_frame, text="Daily Quote:")
    set_title_style(quote_label)
    quote_label.pack()
    quote_text = Label(quote_frame, text=quote, wraplength=500)
    set_label_style(quote_text)
    quote_text.pack()
    nl = Label(quote_frame, text=" ")
    nl.pack()
    setting = Button(quote_frame, text="Settings", command=settings)
    setting.pack()

def show_routine():
    global frame, next_day_name
    clear_frame()
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    title = Label(frame, text="Student Dashboard", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    now = datetime.now()
    label = Label(frame, text=f"Today's date: {now.strftime('%Y-%m-%d')}")
    set_title_style(label)
    label.pack()

    routine_day = routine.get(next_day_name, "No routine")

    if now.hour >= 17 or today == 'Friday':
        routine_label = Label(frame, text=f"Tomorrow's routine ({next_day_name}):")
    elif today == 'Thursday':
        routine_label = Label(frame, text=f"Day after tomorrow's routine ({next_day_name}):")
    else:
        routine_label = Label(frame, text=f"Today's routine ({next_day_name}):")
    
    set_label_style(routine_label)
    routine_label.pack()

    if isinstance(routine_day, dict):
        for period, course_num in routine_day.items():
            course_details = courses.get(f"Course {course_num}", {})
            course_code = course_details.get("code", "")
            course_title = course_details.get("title", "")
            period_label = Label(frame, text=f"{period}: {course_code} - {course_title}")
            set_label_style(period_label)
            period_label.pack()
    else:
        no_routine_label = Label(frame, text=routine_day)
        set_label_style(no_routine_label)
        no_routine_label.pack()

    back_button = Button(frame, text="Back", command=back_home)
    back_button.pack(pady=20)

def show_nextlab():
    global frame, next_day_name
    clear_frame()
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    routine_day = routine.get(next_day_name)
    upcoming_sessional = None

    title = Label(frame, text="Student Dashboard", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    if routine_day:
        for period, course_num in routine_day.items():
            course_details = courses.get(f"Course {course_num}", {})
            course_code = course_details.get("code", "")
            match = re.search(r'\d+', course_code)
            if match:
                course_number = int(match.group())
                if course_number % 2 == 0:
                    upcoming_sessional = f"{period}: {course_code} - {course_details.get('title', '')}"
                    break

    next_lab_label = Label(frame, text="Upcoming Sessional:")
    set_title_style(next_lab_label)
    next_lab_label.pack()
    
    if upcoming_sessional:

        sessional_info_label = Label(frame, text=upcoming_sessional)
        set_label_style(sessional_info_label)
        sessional_info_label.pack()
    else:
        no_sessional_label = Label(frame, text="No upcoming sessional for the next day.")
        set_label_style(no_sessional_label)
        no_sessional_label.pack()

    back_button = Button(frame, text="Back", command=back_home)
    back_button.pack(pady=20)

def show_assignments():
    global frame
    clear_frame()
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    title = Label(frame, text="Student Dashboard", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    assignment_label = Label(frame, text="Assignments")
    set_title_style(assignment_label)
    assignment_label.pack()

    assignment_Cnt = 0

    for i, (assignment_key, assignment_value) in enumerate(assignments.items()):
        code = assignment_value.get('code', '')
        name = assignment_value.get('name', '')
        submission_date = assignment_value.get('submission_date', '')

        if code.strip() or name.strip() or submission_date.strip():
            assignment_text = f"{assignment_key}: {code} - {name}, Due: {submission_date}"
            assignment_entry = Label(frame, text=assignment_text)
            set_label_style(assignment_entry)
            assignment_entry.pack()
            assignment_Cnt += 1

    if assignment_Cnt == 0:
        assignment_entry = Label(frame, text='Chill! No pending assignments!!!')
        set_label_style(assignment_entry)
        assignment_entry.pack()

    back_button = Button(frame, text="Back", command=back_home)
    back_button.pack(pady=20)

def show_todo_list():
    global frame, entry, listbox
    clear_frame()
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    title = Label(frame, text="Student Dashboard", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    todo_label = Label(frame, text="To Do List")
    set_title_style(todo_label)
    todo_label.pack()

    entry = Entry(frame, width=40)
    entry.pack(pady=10)

    add_button = Button(frame, text="Add", command=add_todo)
    add_button.pack()

    listbox = Listbox(frame, width=40)
    listbox.pack(pady=10)

    delete_button = Button(frame, text="Delete", command=delete_todo)
    delete_button.pack()

    save_button = Button(frame, text="Save", command=save_todos)
    save_button.pack(pady=10)

    load_todos()

    back_button = Button(frame, text="Back", command=back_home)
    back_button.pack()

def show_reminder():
    global frame, entry_hour, entry_minute, entry_second, countdown_label
    clear_frame()
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    title = Label(frame, text="Student Dashboard", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    reminder_label = Label(frame, text="Set Reminder")
    set_title_style(reminder_label)
    reminder_label.pack()

    hour_label = Label(frame, text="Hour:")
    set_label_style(hour_label)
    hour_label.pack(pady=10)
    entry_hour = Entry(frame, width=30, justify="center")
    entry_hour.pack()

    minute_label = Label(frame, text="Minute:")
    set_label_style(minute_label)
    minute_label.pack(pady=10)
    entry_minute = Entry(frame, width=30, justify="center")
    entry_minute.pack()

    second_label = Label(frame, text="Second:")
    set_label_style(second_label)
    second_label.pack(pady=10)
    entry_second = Entry(frame, width=30, justify="center")
    entry_second.pack()

    clear_button = Button(frame, text="Clear", command=clear_entries)
    clear_button.pack(pady=10)

    set_reminder_button = Button(frame, text="Set Reminder", command=set_reminder)
    set_reminder_button.pack()

    countdown_label = Label(frame, text="")
    set_label_style(countdown_label)
    countdown_label.pack(pady=0)

    back_button = Button(frame, text="Back", command=back_home)
    back_button.pack()

def back_home():
    clear_frame()
    if(main_view == 0):
        homepage()
    else:
        dashboard()

def clear_frame():
    global frame
    for widget in frame.winfo_children():
        widget.destroy()
    frame.pack_forget()

### To Do ###
def add_todo():
    todo = entry.get()
    if todo:
        todos.append(todo)
        listbox.insert(END, todo)
        entry.delete(0, END)

def delete_todo():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        listbox.delete(index)
        todos.pop(index)

def save_todos():
    with open("todos.json", "w") as file:
        json.dump(todos, file)

def load_todos():
    global todos
    if os.path.exists("todos.json"):
        with open("todos.json", "r") as file:
            todos = json.load(file)
            for todo in todos:
                listbox.insert(END, todo)

### Reminder ###
def set_reminder():
    try:
        hour = int(entry_hour.get()) if entry_hour.get() else 0
        minute = int(entry_minute.get()) if entry_minute.get() else 0
        second = int(entry_second.get()) if entry_second.get() else 0
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers for hours, minutes, and seconds.")
        return

    total_seconds = hour * 3600 + minute * 60 + second

    if total_seconds <= 0:
        messagebox.showerror("Invalid input", "The reminder time must be greater than zero.")
        return

    messagebox.showinfo("Reminder set", f"Reminder set for {hour} hours, {minute} minutes, and {second} seconds.")
    countdown(total_seconds)

def countdown(seconds):
    while seconds > 0:
        minutes, seconds_left = divmod(seconds, 60)
        hours, minutes_left = divmod(minutes, 60)
        countdown_label.config(text=f"Time remaining: {hours:02}:{minutes_left:02}:{seconds_left:02}")
        window.update()
        time.sleep(1)
        seconds -= 1

    countdown_label.config(text="Time's up!")
    messagebox.showinfo("Reminder", "Time's up!")

def clear_entries():
    entry_hour.delete(0, END)
    entry_minute.delete(0, END)
    entry_second.delete(0, END)
    countdown_label.config(text="")

def settings():
    global frame
    clear_frame()
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    title = Label(frame, text="Student Dashboard", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    buttons = [
        ("Edit Routine", edit_routine),
        ("Edit Assignments", edit_assignments),
        ("View Options", view_options),
        ("Back", back_home)
    ]

    for (text, command) in buttons:
        button = Button(frame, text=text, command=command, width=25, height=2, font=("Verdana", 12))
        button.pack(pady=10)

def edit_routine():
    global frame
    clear_frame()
    global frame, entries, course_entries
    frame = Frame(window)
    frame.pack()

    entries = {}
    course_entries = {}

    title = Label(frame, text="Edit Routine", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    top_frame = Frame(frame)
    top_frame.pack(side="top", fill="both", expand=True)

    course_frame = Frame(top_frame)
    course_frame.pack(side="left", fill="both", expand=True)
    course_frame.pack_propagate(False) 
    period_frame = Frame(frame)
    period_frame.pack(side="top", fill="both", expand=True)

    ins_frame = Frame(frame)
    ins_frame.pack(side="top", expand=True)

    bttn_frame = Frame(frame)
    bttn_frame.pack(side="top", expand=True, pady=20)

    period_label = Label(period_frame, text='Routine Details:')
    set_title_style(period_label)
    period_label.grid(row=0, column=0)

    for j, period in enumerate(periods):
        label = Label(period_frame, text=f"{period}")
        set_label_style(label)
        label.grid(row=1, column=j + 1)

    for i, day in enumerate(days):
        day_label = Label(period_frame, text=f"{day}")
        set_label_style(day_label)
        day_label.grid(row=i + 2, column=0)

        entries[day] = {}

        for j, period in enumerate(periods):
            entry = Entry(period_frame, width=10)
            entry.grid(row=i + 2, column=j + 1)
            entries[day][period] = entry

            if routine.get(day) and routine[day].get(period):
                entry.insert(0, routine[day].get(period, ""))

        lbl = Label(period_frame, text="       ")
        lbl.grid(row=10, column=10)

    course_label = Label(course_frame, text="Course Details:")
    set_title_style(course_label)
    course_label.grid(row=1, column=0)

    title1 = Label(course_frame, text="Course Code")
    set_label_style(title1)
    title1.grid(row=2, column=1)
    title2 = Label(course_frame, text="Course Title")
    set_label_style(title2)
    title2.grid(row=2, column=2)
    

    if os.path.exists(course_file):
        with open(course_file, 'r') as f:
            courses = json.load(f)
            for i in range(10):
                course_entries[i] = {}
                course_label = Label(course_frame, text=f"{i + 1}")
                set_label_style(course_label)
                course_label.grid(row=3 + i, column=0)
                course_code_entry = Entry(course_frame, width=25)
                course_code_entry.grid(row=3 + i, column=1)
                course_code_entry.insert(0, courses.get(f"Course {i + 1}", {}).get("code", ""))
                course_entries[i]["code"] = course_code_entry
                course_title_entry = Entry(course_frame, width=70)
                course_title_entry.grid(row=3 + i, column=2)
                course_title_entry.insert(0, courses.get(f"Course {i + 1}", {}).get("title", ""))
                course_entries[i]["title"] = course_title_entry
    else:
        for i in range(10):
            course_entries[i] = {}
            course_label = Label(course_frame, text=f"Course {i + 1}")
            set_label_style(course_label)
            course_label.grid(row=3 + i, column=0)
            course_code_entry = Entry(course_frame, width=15)
            course_code_entry.grid(row=3 + i, column=2)
            course_entries[i]["code"] = course_code_entry
            course_title_entry = Entry(course_frame, width=50)
            course_title_entry.grid(row=3 + i, column=4)
            course_entries[i]["title"] = course_title_entry

    ins_label = Label(ins_frame, text='* Write the Serial of the courses only in the routine details *')
    ins_label.grid(row=0, column=0)


    submit_button = Button(bttn_frame, text="Back", command=back_dashboard)
    submit_button.grid(row=len(days) + 20 + i, column=0)

    label = Label(bttn_frame, text="             ")
    label.grid(row=len(days) + 20 + i, column=1)
    
    clear_courses_button = Button(bttn_frame, text="Clear Courses", command=clear_course_entries)
    clear_courses_button.grid(row=len(days) + 20 + i, column=2)

    label = Label(bttn_frame, text="             ")
    label.grid(row=len(days) + 20 + i, column=3)

    clear_routine_button = Button(bttn_frame, text="Clear Routines", command=clear_routine_entries)
    clear_routine_button.grid(row=len(days) + 20 + i, column=4)

    label = Label(bttn_frame, text="             ")
    label.grid(row=len(days) + 20 + i, column=5)

    save_button = Button(bttn_frame, text="Save", command=save_settings)
    save_button.grid(row=len(days) + 20 + i, column=6)

def clear_routine_entries():
    if messagebox.askyesno("Confirmation", "Are you sure you want to clear all routine entries?"):
        for day in entries:
            for period in entries[day]:
                entries[day][period].delete(0, END)

def clear_course_entries():
    if messagebox.askyesno("Confirmation", "Are you sure you want to clear all course entries?"):
        for i in course_entries:
            course_entries[i]["code"].delete(0, END)
            course_entries[i]["title"].delete(0, END)

def edit_assignments():
    global frame, assignment_entries  # Make assignment_entries global
    clear_frame()
    frame = Frame(window)
    frame.pack()

    assignment_entries = []  # Re-initialize global assignment_entries

    title = Label(frame, text="Edit Assignments", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    assign_frame = Frame(frame)
    assign_frame.pack(side="top", fill="both", expand=True)
    assign_frame.pack_propagate(False)

    if os.path.exists(assignment_file):
        with open(assignment_file, 'r') as f:
            assignments = json.load(f)

    title3 = Label(assign_frame, text="Course Code")
    set_label_style(title3)
    title3.grid(row=1, column=1)
    title4 = Label(assign_frame, text="Assignment Name")
    set_label_style(title4)
    title4.grid(row=1, column=2)
    title5 = Label(assign_frame, text="Submission Date")
    set_label_style(title5)
    title5.grid(row=1, column=3)

    bttn_frame = Frame(frame)
    bttn_frame.pack(side="top", expand=True, pady=20)

    for i in range(10):
        assignment_entries.append({})
        assignment_label = Label(assign_frame, text=f"{i + 1}")
        set_label_style(assignment_label)
        assignment_label.grid(row=i + 2, column=0)
        assignment_code_entry = Entry(assign_frame, width=15)
        assignment_code_entry.grid(row=i + 2, column=1)
        assignment_entries[i]["code"] = assignment_code_entry
        assignment_name_entry = Entry(assign_frame, width=41)
        assignment_name_entry.grid(row=i + 2, column=2)
        assignment_entries[i]["name"] = assignment_name_entry
        submission_date_entry = Entry(assign_frame, width=20)
        submission_date_entry.grid(row=i + 2, column=3)
        assignment_entries[i]["submission_date"] = submission_date_entry

        if assignments:
            assignment = assignments.get(f"Assignment {i + 1}")
            if assignment:
                assignment_code_entry.insert(0, assignment.get("code", ""))
                assignment_name_entry.insert(0, assignment.get("name", ""))
                submission_date_entry.insert(0, assignment.get("submission_date", ""))

    submit_button = Button(bttn_frame, text="Back", command=back_dashboard)
    submit_button.grid(row=len(days) + 20 + i, column=0)

    label = Label(bttn_frame, text="             ")
    label.grid(row=len(days) + 20 + i, column=1)

    clear_button = Button(bttn_frame, text="Clear", command=clear_assignment_entries)
    clear_button.grid(row=len(days) + 20 + i, column=2)

    label = Label(bttn_frame, text="             ")
    label.grid(row=len(days) + 20 + i, column=3)

    save_button = Button(bttn_frame, text="Save", command=save_settings)
    save_button.grid(row=len(days) + 20 + i, column=4)

def clear_assignment_entries():
    global assignment_entries  # Reference the global assignment_entries
    if messagebox.askyesno("Confirmation", "Are you sure you want to clear all assignment entries?"):
        for i in range(len(assignment_entries)):
            assignment_entries[i]["code"].delete(0, END)
            assignment_entries[i]["name"].delete(0, END)
            assignment_entries[i]["submission_date"].delete(0, END)

def back_dashboard():
    frame.destroy()
    if(main_view == 0):
        homepage()
    else:
        dashboard()

def save_settings():
    global courses, assignments
    for day, periods in entries.items():
        for period, entry in periods.items():
            code = entry.get()
            if not routine.get(day):
                routine[day] = {}

            routine[day][period] = code

    for i, course_entry in course_entries.items():
        code = course_entry["code"].get()
        title = course_entry["title"].get()
        courses[f"Course {i + 1}"] = {"code": code, "title": title}

    for i, assignment_entry in enumerate(assignment_entries):
        code = assignment_entry["code"].get()
        name = assignment_entry["name"].get()
        submission_date = assignment_entry["submission_date"].get()
        assignments[f"Assignment {i + 1}"] = {"code": code, "name": name, "submission_date": submission_date}

    with open(routine_file, 'w') as f:
        json.dump(routine, f)

    with open(course_file, 'w') as f:
        json.dump(courses, f)

    with open(assignment_file, 'w') as f:
        json.dump(assignments, f)
    back_dashboard()

def view_options():
    global frame
    clear_frame()
    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    title = Label(frame, text="Student Dashboard", font=("Verdana", 20, "bold"))
    title.pack(pady=20)

    options = [
        ("Dashboard View", dashboard_view),
        ("Menu View", menu_view),
        ("Back", back_dashboard)
    ]

    for (text, command) in options:
        button = Button(frame, text=text, command=command, width=25, height=2, font=("Verdana", 12))
        button.pack(pady=10)

def dashboard_view():
    global main_view, window
    with open('view.json', 'r') as file:
        data = json.load(file)
    # Modify the value of 'view_option'
    data['view_option'] = 1

    # Write the modified data back to the JSON file
    with open('view.json', 'w') as file:
        json.dump(data, file, indent=4)

    main_view = 1
    window.state('zoomed')
    window.resizable(False, True)
    back_dashboard()

def menu_view():
    global main_view, window
    main_view = 0
    with open('view.json', 'r') as file:
        data = json.load(file)
    # Modify the value of 'view_option'
    data['view_option'] = 0

    # Write the modified data back to the JSON file
    with open('view.json', 'w') as file:
        json.dump(data, file, indent=4)

    window.state('normal')
    window.geometry("800x700")
    window.resizable(False, False)
    back_dashboard()

# Load initial data from files
if os.path.exists(routine_file):
    with open(routine_file, 'r') as file:
        routine = json.load(file)

if os.path.exists(course_file):
    with open(course_file, 'r') as file:
        courses = json.load(file)

if os.path.exists(assignment_file):
    with open(assignment_file, 'r') as file:
        assignments = json.load(file)

# Fetch a random quote
def get_random_quote():
    global quote
    if(quote == ""):
        try:
            response = requests.get("https://zenquotes.io/api/random")
            if response.status_code == 200:
                quote_data = response.json()
                quote = f"{quote_data[0]['q']} - {quote_data[0]['a']}"
                return quote
        except requests.exceptions.RequestException as e:
            quote = "Trust in Allah but tie your camel. - Al Hadith"
            return quote
    else:
        return quote

# Start with the homepage
if(main_view == 0):
    homepage()
else:
    dashboard()

window.mainloop()