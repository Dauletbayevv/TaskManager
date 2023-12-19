from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
logging.basicConfig(level=logging.INFO)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    task_status = db.Column(db.Integer, default=0)
    logging.info(f"New Task {task_name} is created")

    def __repr__(self):
        return '<Tasks_db %r>' % self.id

    def check_status(self):
        response = requests.get(read_file("timeAPI.txt"))
        current_time = datetime.fromisoformat(response.json()['datetime'])
        current_time = current_time.replace(tzinfo=None)
        if current_time > self.deadline and self.task_status != 1:
            self.task_status = 2
    logging.info(f"New Task {task_name} is created")


def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


@app.route('/')
@app.route('/tasks')
def index():
    tasks = Task.query.order_by(Task.deadline).all()
    for task in tasks:
        task.check_status()
    return render_template("index.html", tasks=tasks)


@app.route('/tasks/<int:id>')
def task_edit(id):
    task = Task.query.get(id)
    return render_template("task_edit.html", task=task)


@app.route('/tasks/<int:id>/del')
def task_delete(id):
    task = Task.query.get_or_404(id)

    try:
        db.session.delete(task)
        logging.info(f"Task {task.task_name} is deleted")
        db.session.commit()
        return redirect('/')
    except:
        logging.info(f"Task {task.task_name} can not delete")
        return "Error"

@app.route('/tasks/<int:id>/save', methods=['GET', 'POST'])
def task_save(id):
    task = Task.query.get(id)
    if request.method == "POST":
        task.task_status = int(request.form['task_status'])
        try:
            db.session.commit()
            logging.info(f"Task is saved {task.task_name}")
            return redirect("/tasks")
        except:
            logging.info(f"Task can not saved")
            return "Error"
    else:
        return render_template('task_edit.html', task=task)


@app.route('/add-task', methods=['POST', 'GET'])
def add_task():
    if request.method == "POST":
        task_name = request.form['task_name']
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
        task = Task(task_name=task_name, deadline=deadline)

        try:
            db.session.add(task)
            db.session.commit()
            logging.info(f"New Task Added {task.task_name} is created")
            return redirect('/')
        except:
            logging.info(f"New Task Can not Add")
            return "Error"
    else:
        return render_template('add-task.html')


if __name__ == "__main__":
    app.run(debug=True)