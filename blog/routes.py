from flask import render_template, request, url_for, redirect
from blog import app
from blog.models import Entry
from blog.forms import EntryForm
from blog.blend_function import tackle_post


@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    form = EntryForm(obj=entry)
    errors = None
    if request.method == 'POST':
        if form.validate_on_submit():
            tackle_post(form, entry_id=entry_id, entry=entry)
        else:
            errors = form.errors

        return redirect(url_for("index"))

    return render_template("entry_form.html", form=form, errors=errors)


@app.route("/new-post/", methods=["GET", "POST"])
def create_entry():
    form = EntryForm()
    errors = None
    if request.method == 'POST':
        if form.validate_on_submit():
            tackle_post(form, entry_id=None, entry=None)
        else:
            errors = form.errors

        return redirect(url_for("index"))
    return render_template("entry_form.html", form=form, errors=errors)


@app.route('/')
def index():
    all_posts = Entry.query.filter_by(is_published=True).\
        order_by(Entry.pub_date.desc())

    return render_template("homepage.html", all_posts=all_posts)
