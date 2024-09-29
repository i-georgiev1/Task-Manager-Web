from flask import Flask, render_template, request, redirect, url_for
from models.manager import TaskManager
from datetime import datetime as dt
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)
app.secret_key = 'supersecretkey'
manager = TaskManager()

filepath = 'data/tasks.csv'

if not os.path.isfile(filepath):
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['description', 'priority', 'status', 'due_date'])
else:
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    for task in data[1:]:
        description = task[0]
        priority = task[1]
        status = task[2]
        due_date = task[3]
        manager.import_task(description, priority, status, due_date)


@app.route('/save_email', methods=['GET', 'POST'])
def save_email():
    user_email = request.form['user_email']
    with open('data/email.txt', 'w') as file:
        file.write(user_email)

    return redirect(url_for('show_tasks', user_email=user_email))


try:
    with open('data/email.txt', 'r') as file:
        user_email = file.read().strip()
except FileNotFoundError:
    user_email = ""
smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
smtp_object.ehlo()
smtp_object.starttls()
email = 'task.manager.notifications@gmail.com'
email_password = 'cihg cftd raed ruji'
smtp_object.login(email, email_password)

for task in manager.tasks:
    curr_date = str(dt.today())
    task_date = task.due_date
    if task_date < curr_date and not task.status:
        task_id = str(manager.tasks.index(task) + 1)
        subject = "Просрочена задача"
        message = f"Имате просрочена задача {task_id}: {task.description}"

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = user_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        smtp_object.sendmail(email, user_email, msg.as_string())

smtp_object.quit()



@app.route('/')
def show_tasks():
    try:
        with open('data/email.txt', 'r') as file:
            user_email = file.read().strip()
    except FileNotFoundError:
        user_email = ""

    return render_template('tasks.html', tasks=manager.tasks, user_email=user_email)


@app.route('/add_task', methods=['POST'])
def add_task():
    description = request.form['description']
    priority = request.form['priority']
    due_date = request.form['due_date']

    due_date = dt.strptime(due_date, "%Y-%m-%dT%H:%M")
    manager.add_task(description, priority, due_date)

    return redirect(url_for('show_tasks'))


@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    manager.mark_completed(task_id)
    return redirect(url_for('show_tasks'))


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task_id += 1
    selected_task = next((task for task in manager.tasks if task.id == task_id), None)


    if not selected_task:
        return "Task not found", 404

    if request.method == 'POST':
        if 'description' in request.form and 'priority' in request.form and 'due_date' in request.form:
            selected_task.description = request.form['description']
            selected_task.priority = request.form['priority']
            selected_task.due_date = request.form['due_date']
            return redirect(url_for('edit_task', task_id=task_id))

    return render_template('edit_task.html', task=selected_task)



@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    manager.delete_task(task_id)
    return redirect(url_for('show_tasks'))


@app.route('/sort_tasks')
def sort_tasks():
    sort_by = request.args.get('sort_by')

    if sort_by == 'priority':
        manager.sort_tasks_priority()
    elif sort_by == 'status':
        # 1 - незавършена, 2 - завършена
        manager.sort_tasks_status(1)
    elif sort_by == 'due_date':
        manager.tasks.sort(key=lambda task: task.due_date)

    return redirect(url_for('show_tasks'))


@app.route('/save_tasks')
def save_tasks():
    with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['description', 'priority', 'status', 'due_date'])

        for task in manager.tasks:
            writer.writerow([task.description, task.priority, task.status, task.due_date])
    return redirect(url_for('show_tasks'))


if __name__ == '__main__':
    app.run(debug=True)