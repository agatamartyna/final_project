from blog.models import Entry
from blog import db


def tackle_post(form, entry_id=None, entry=None):
    if entry_id is None:
        entry = Entry(
            title=form.title.data,
            body=form.body.data,
            is_published=form.is_published.data
        )
        db.session.add(entry)
        db.session.commit()
    elif entry_id:
        form.populate_obj(entry)
        db.session.commit()
