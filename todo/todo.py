from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, g
)
from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)


@bp.route('/')
@login_required
def index():
    db, c = get_db()
    c.execute(
        'select t.id, t.title, t.priority, t.label, t.description, u.username, t.completed, t.created_at '
        'from todo t JOIN user u on t.created_by = u.id where t.created_by = %s order by created_at desc',
        (g.user['id'],)
    )
    todos = c.fetchall()

    return render_template('todo/index.html', todos = todos)


@bp.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        label = request.form['label']
        error = None

        if not title:
            error = 'El título es requerido.'

        if not description:
            error = 'La descripción es requerida.'

        if not priority:
            priority = 3

        if not label:
            label = ''

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'insert into todo (title, priority, label, description, completed, created_by)'
                ' values (%s, %s, %s, %s, %s, %s)',
                (title, priority, label, description, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')


def get_todo(id):
    db, c = get_db()
    c.execute(
        'select t.id, t.title, t.priority, t.label, t.description, t.completed, t.created_by, t.created_at, u.username '
        'from todo t join user u on t.created_by = u.id where t.id = %s',
        (id,)
    )

    todo = c.fetchone()

    if todo is None:
        abort(404, 'El todo de id {0} no existe'.format(id))

    return todo


@bp.route('/<int:id>/update', methods = ['GET', 'POST'])
@login_required
def update(id):
    todo = get_todo(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        label = request.form['label']
        completed = True if request.form.get('completed') == 'on' else False
        error = None

        if not title:
            error = 'El título es requerido.'

        if not description:
            error = 'La descripción es requerida.'

        if not priority:
            priority = 3

        if not label:
            label = ''

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'update todo set title = %s, description = %s, priority = %s, label = %s, completed = %s'
                ' where id = %s and created_by = %s',
                (title, description, priority, label, completed, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))
    return render_template('todo/update.html', todo = todo)


@bp.route('/<int:id>/delete', methods = ['POST'])
@login_required
def delete(id):
    db, c = get_db()
    c.execute('delete from todo where id = %s and created_by = %s', (id, g.user['id']))
    db.commit()
    return redirect(url_for('todo.index'))
