from flask import render_template, request, session, flash, url_for, redirect
from blog import app
from blog.models import Entry, db
from blog.forms import EntryForm, LoginForm
from blog.blend_function import tackle_post
import functools


def login_required(view_func):
    @functools.wraps(view_func)
    def check_permissions(*args, **kwargs):
        if session.get('logged_in'):
            return view_func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))

    return check_permissions


@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = None
    next_url = request.args.get('next')
    if request.method == 'POST':
        if form.validate_on_submit():
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            errors = form.errors
    return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        flash("You are now logged out.", 'success')
    return redirect(url_for('index'))


@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    form = EntryForm(obj=entry)
    errors = None
    title = "Edytuj"
    if request.method == 'POST':
        if form.validate_on_submit():
            tackle_post(form, entry_id=entry_id, entry=entry)
        else:
            errors = form.errors

        return redirect(url_for("index"))

    return render_template("entry_form.html",
                           form=form, title=title, errors=errors)


@app.route("/new-post/", methods=["GET", "POST"])
@login_required
def create_entry():
    form = EntryForm()
    errors = None
    title = "Dodaj nowy"
    if request.method == 'POST':
        if form.validate_on_submit():
            tackle_post(form, entry_id=None, entry=None)
        else:
            errors = form.errors

        return redirect(url_for("index"))
    return render_template("entry_form.html",
                           form=form, title=title, errors=errors)


@app.route('/', methods=["GET", "POST"])
def index():
    all_posts = Entry.query.filter_by(is_published=True). \
        order_by(Entry.pub_date.desc())

    return render_template("homepage.html", all_posts=all_posts)


@app.route("/delete-post/<int:draft_id>", methods=["POST"])
@login_required
def delete_entry(draft_id):
    entry = Entry.query.filter_by(id=draft_id).first_or_404()
    flag = 0
    if entry.is_published is True:
        flag = 1
    db.session.delete(entry)
    db.session.commit()

    if flag == 0:
        return redirect(url_for("list_drafts"))
    else:
        return redirect(url_for("index"))


@app.route('/drafts/')
@login_required
def list_drafts():
    drafts = Entry.query.filter_by(is_published=False). \
        order_by(Entry.pub_date.desc())

    return render_template("drafts.html", drafts=drafts)
