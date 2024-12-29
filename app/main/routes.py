from flask import (Blueprint, render_template, url_for, flash,
                   redirect, request, abort)
from flask_login import current_user, login_required
from app import db
from app.models import User, Title, Entry
from app.main.forms import EntryForm, ReplyForm
from sqlalchemy import func, desc

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    entries = Entry.query.filter_by(parent_id=None)\
        .order_by(Entry.date_posted.desc())\
        .paginate(page=page, per_page=10)
    trending_topics = Title.query.join(Entry)\
        .group_by(Title.id)\
        .order_by(func.count(Entry.id).desc())\
        .limit(10).all()
    return render_template('home.html', entries=entries, trending_topics=trending_topics)

@main.route("/popular")
def popular():
    page = request.args.get('page', 1, type=int)
    entries = Entry.query.join(Entry.likes)\
        .group_by(Entry.id)\
        .order_by(func.count(Entry.likes).desc())\
        .paginate(page=page, per_page=10)
    trending_topics = Title.query.join(Entry)\
        .group_by(Title.id)\
        .order_by(func.count(Entry.id).desc())\
        .limit(10).all()
    return render_template('home.html', entries=entries, trending_topics=trending_topics)

@main.route("/user/<string:username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    entries = Entry.query.filter_by(author=user)\
        .order_by(Entry.date_posted.desc())\
        .paginate(page=page, per_page=10)
    return render_template('profile.html', user=user, entries=entries)

@main.route("/title/<string:title_name>")
def title(title_name):
    title = Title.query.filter_by(title=title_name).first_or_404()
    page = request.args.get('page', 1, type=int)
    entries = Entry.query.filter_by(title_id=title.id)\
        .order_by(Entry.date_posted.desc())\
        .paginate(page=page, per_page=10)
    trending_topics = Title.query.join(Entry)\
        .group_by(Title.id)\
        .order_by(func.count(Entry.id).desc())\
        .limit(10).all()
    form = EntryForm() if current_user.is_authenticated else None
    return render_template('title.html', title=title, entries=entries,
                         trending_topics=trending_topics, form=form)

@main.route("/entry/new", methods=['GET', 'POST'])
@login_required
def new_entry():
    form = EntryForm()
    if form.validate_on_submit():
        title_text = request.args.get('title', form.title.data)
        title = Title.query.filter_by(title=title_text).first()
        if not title:
            title = Title(title=title_text)
            db.session.add(title)
            db.session.commit()
        entry = Entry(content=form.content.data, author=current_user, title_obj=title)
        db.session.add(entry)
        db.session.commit()
        flash('Entry başarıyla oluşturuldu!', 'success')
        return redirect(url_for('main.title', title_name=title.title))
    elif request.args.get('title'):
        form.title.data = request.args.get('title')
    return render_template('create_entry.html', title='Yeni Entry',
                         form=form, legend='Yeni Entry')

@main.route("/entry/<int:entry_id>")
def entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    trending_topics = Title.query.join(Entry)\
        .group_by(Title.id)\
        .order_by(func.count(Entry.id).desc())\
        .limit(10).all()
    form = ReplyForm() if current_user.is_authenticated else None
    return render_template('entry.html', entry=entry,
                         trending_topics=trending_topics, form=form)

@main.route("/entry/<int:entry_id>/update", methods=['GET', 'POST'])
@login_required
def update_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.author != current_user:
        abort(403)
    form = EntryForm()
    if form.validate_on_submit():
        entry.content = form.content.data
        db.session.commit()
        flash('Entry başarıyla güncellendi!', 'success')
        return redirect(url_for('main.entry', entry_id=entry.id))
    elif request.method == 'GET':
        form.content.data = entry.content
        if not entry.parent:
            form.title.data = entry.title_obj.title
    return render_template('create_entry.html', title='Entry Güncelle',
                         form=form, legend='Entry Güncelle')

@main.route("/entry/<int:entry_id>/delete", methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.author != current_user:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry başarıyla silindi!', 'success')
    return redirect(url_for('main.home'))

@main.route("/entry/<int:entry_id>/like", methods=['POST'])
@login_required
def like_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if current_user in entry.likes:
        entry.likes.remove(current_user)
    else:
        entry.likes.append(current_user)
    db.session.commit()
    return redirect(request.referrer)

@main.route("/entry/<int:entry_id>/reply", methods=['POST'])
@login_required
def reply_entry(entry_id):
    parent_entry = Entry.query.get_or_404(entry_id)
    form = ReplyForm()
    if form.validate_on_submit():
        reply = Entry(content=form.content.data,
                     author=current_user,
                     title_obj=parent_entry.title_obj,
                     parent=parent_entry)
        db.session.add(reply)
        db.session.commit()
        flash('Cevabınız başarıyla eklendi!', 'success')
    return redirect(url_for('main.entry', entry_id=entry_id))

@main.route("/search")
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query.startswith('@'):
        username = query[1:]
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('main.profile', username=username))
        else:
            flash('Kullanıcı bulunamadı.', 'warning')
            return redirect(url_for('main.home'))
    
    elif query.startswith('#'):
        try:
            entry_id = int(query[1:])
            entry = Entry.query.get(entry_id)
            if entry:
                return redirect(url_for('main.entry', entry_id=entry_id))
            else:
                flash('Entry bulunamadı.', 'warning')
                return redirect(url_for('main.home'))
        except ValueError:
            flash('Geçersiz entry ID.', 'warning')
            return redirect(url_for('main.home'))
    
    else:
        titles = Title.query.filter(Title.title.ilike(f'%{query}%'))\
            .order_by(Title.title)\
            .paginate(page=page, per_page=10)
        return render_template('search.html', titles=titles, query=query) 