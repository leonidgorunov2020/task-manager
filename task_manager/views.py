from task_manager import app, request, db
from task_manager.models import User, Task, Comment
from task_manager import redirect, url_for, flash, render_template
from flask_login import login_required, current_user, login_user, logout_user
from task_manager import login_manager
from sqlalchemy.orm import joinedload
from datetime import date, timedelta
from task_manager.functions import *


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logout')
def logout():
    logout_user()  # Clear the user session
    flash('You have been logged out.', 'info')
    return redirect(url_for('list_tasks'))  # Redirect to the home page

@app.route('/')
def idx():
    return redirect(url_for('login'))  # Redirect to the home page

@app.route('/tasks/status_chart')
@login_required
def task_status_chart():
    # Query the number of open and closed tasks
    open_tasks_count = Task.query.filter_by(status=1).count()
    closed_tasks_count = Task.query.filter_by(status=0).count()
    is_admin = True if current_user.is_admin else False
    return render_template('task_status_chart.html', open_tasks_count=open_tasks_count, closed_tasks_count=closed_tasks_count, is_admin=is_admin)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        is_admin = bool(request.form.get('is_admin'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists!"

        new_user = User(username=username, is_admin=is_admin, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('list_tasks'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/search/tasks', methods=['GET'])
def search_tasks():
    from sqlalchemy import or_
    query = request.args.get('query')
    user = User.query.filter_by(id=current_user.id).first()
    if query:
        # Perform search in task titles and bodies
        search_results = Task.query.filter(or_(Task.title.like(f'%{query}%'), Task.body.like(f'%{query}%'))).all()
    else:
        search_results = []

    return render_template('search_results.html', search_results=search_results, username=user.username)


@app.route('/tasks', methods=['GET'])
@login_required
def list_tasks():
    if current_user.is_admin:
        tasks = Task.query.filter_by( status=1).order_by(Task.expiration_date.asc()).options(
            joinedload(Task.comments)).all()
        user = current_user
    else:
        tasks = Task.query.filter_by(user_id=current_user.id, status=1).order_by(Task.expiration_date.asc()).options(
            joinedload(Task.comments)).all()
        user = User.query.filter_by(id=current_user.id).first()
    is_admin = True if current_user.is_admin else False
    return render_template('tasks.html', tasks=tasks, username=user.username, is_admin=is_admin)

@app.route('/weekly_tasks', methods=['GET'])
@login_required
def weekly_tasks():
    one_week_from_today = date.today() + timedelta(days=7)
    if current_user.is_admin:
        tasks = Task.query.filter_by(status=1).filter(Task.expiration_date <= one_week_from_today).order_by(Task.expiration_date.asc()).options(joinedload(Task.comments)).all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id, status=1).filter(Task.expiration_date <= one_week_from_today).order_by(Task.expiration_date.asc()).options(joinedload(Task.comments)).all()
    user = User.query.filter_by(id=current_user.id).first()
    page_title = "Weekly tasks"
    is_admin = True if current_user.is_admin else False
    return render_template('tasks.html', tasks=tasks, username=user.username, page_title=page_title, is_admin=is_admin)

@app.route('/closed', methods=['GET'])
@login_required
def closed_tasks():
    if current_user.is_admin:
        tasks = Task.query.filter_by(status=0)
    else:
        tasks = Task.query.filter_by(user_id=current_user.id, status=0)
    user = User.query.filter_by(id=current_user.id).first()
    page_title = "Closed tasks"
    is_admin = True if current_user.is_admin else False
    return render_template('tasks.html', tasks=tasks, username=user.username, page_title=page_title, is_admin=is_admin)

@app.route('/monthly_tasks', methods=['GET'])
@login_required
def monthly_tasks():
    one_week_from_today = date.today() + timedelta(days=30)
    if current_user.is_admin:
        tasks = Task.query.filter_by(status=1).filter(Task.expiration_date <= one_week_from_today).order_by(Task.expiration_date.asc()).options(joinedload(Task.comments)).all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id, status=1).filter(Task.expiration_date <= one_week_from_today).order_by(Task.expiration_date.asc()).options(joinedload(Task.comments)).all()
    user = User.query.filter_by(id=current_user.id).first()
    page_title = "Montly tasks"
    is_admin = True if current_user.is_admin else False
    return render_template('tasks.html', tasks=tasks, username=user.username, page_title=page_title, is_admin=is_admin)

@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        user_id = request.form.get('user_id')
        status = request.form.get('status')
        if not user_id:
            user_id = current_user.id
        expiration_date = request.form['expiration_date']
        if len(expiration_date) == 0:
            #If not expirate date is set, we will set it to 14 days ahead
            import time
            from datetime import datetime
            expiration_date = datetime.utcfromtimestamp(int(time.time()) + (14 * 86400)).strftime("%Y-%m-%d")

        # Create the task with the selected user
        # Example:
        new_task = Task(title=title, body=body, user_id=user_id, expiration_date=expiration_date, status=status)
        db.session.add(new_task)
        db.session.commit()
        send_email(User.query.filter_by(id=user_id).first().email, 'New task has been added', f"Task title: {title}")
        flash('Task created successfully!', 'success')
        return redirect(url_for('list_tasks'))

    users = User.query.all()
    is_admin = True if current_user.is_admin else False
    return render_template('create_task.html', users=users, current_user=current_user, is_admin=is_admin)


@app.route('/tasks/<int:task_id>/update', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    if not current_user.is_admin and task.user_id != current_user.id:
        flash('You are not authorized to update this task.', 'danger')
        return redirect(url_for('list_tasks'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.body = request.form['body']
        task.status = request.form.get('status')
        if len(request.form['expiration_date']) > 0:
            task.expiration_date = request.form['expiration_date']

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('list_tasks'))
    users = User.query.all()
    is_admin = True if current_user.is_admin else False
    return render_template('update_task.html', users=users, task=task, is_admin=is_admin)


@app.route('/tasks/<int:task_id>/view', methods=['GET', 'POST'])
@login_required
def view_task(task_id):

    task = Task.query.get_or_404(task_id)
    user = User.query.filter_by(id=current_user.id).first()
    if not current_user.is_admin and task.user_id != current_user.id:
        flash('You are not authorized to update this task.', 'danger')
        return redirect(url_for('list_tasks'))

    is_admin = True if current_user.is_admin else False
    return render_template('view_task.html', task=task, username=user.username, is_admin=is_admin)

@app.route('/tasks/<int:task_id>/delete', methods=['GET'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if not current_user.is_admin and task.user_id != current_user.id:
        flash('You are not authorized to delete this task.', 'danger')
        return redirect(url_for('list_tasks'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('list_tasks'))



@app.route('/tasks/<int:task_id>/add_comment', methods=['POST'])
@login_required
def add_comment(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        body = request.form['body']
        if len(body) == 1:
            flash('No empty comments allowed.', 'danger')
            return redirect(url_for('list_tasks'))
        user_id = current_user.id  # Set the user_id based on the current user

        get_user = User.query.filter_by(id=current_user.id).first()
        username = get_user.username
        new_comment = Comment(body=body, task_id=task_id, user_id=current_user.id, comment_owner=username)
        db.session.add(new_comment)
        db.session.commit()
        is_admin = True if current_user.is_admin else False
        return redirect(url_for('view_task', task_id=task_id, is_admin=is_admin))

@app.route('/comments/<int:comment_id>/update', methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if request.method == 'POST':
        if not comment.user_id == current_user.id:
            flash('No permissions to update this comment', 'danger')
            return redirect(url_for('list_tasks'))
        # Update the comment based on the form submission
        new_body = request.form['body']
        comment.body = new_body
        db.session.commit()
        flash('Comment updated successfully!', 'success')
        return redirect(url_for('list_tasks'))
    is_admin = True if current_user.is_admin else False
    return render_template('update_comment.html', comment=comment, is_admin=is_admin)


@app.route('/comments/<int:comment_id>/delete', methods=['GET'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        flash('You are not authorized to delete this comment.', 'danger')
        return redirect(url_for('list_tasks'))

    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('view_task', task_id=comment.task_id))