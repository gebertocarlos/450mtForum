from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, current_app
from flask_login import current_user, login_required
from extensions import db
from models import User, Entry, Like
from forms import EntryForm
from sqlalchemy import func, or_, desc

main = Blueprint('main', __name__)

def get_trending_topics():
    return db.session.query(
        Entry.title,
        func.count(Entry.id).label('entry_count')
    ).group_by(Entry.title).order_by(func.count(Entry.id).desc()).limit(10).all()

@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    total = db.session.query(func.count(Entry.id)).scalar()
    entries = db.session.query(Entry).order_by(desc(Entry.date_posted)).limit(per_page).offset(offset).all()
    
    has_next = offset + per_page < total
    has_prev = page > 1
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'items': entries,
        'has_next': has_next,
        'has_prev': has_prev,
        'pages': (total + per_page - 1) // per_page
    }
    
    trending_topics = get_trending_topics()
    return render_template('home.html', entries=pagination, trending_topics=trending_topics)

@main.route('/entry/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = EntryForm()
    if form.validate_on_submit():
        entry = Entry(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(entry)
        db.session.commit()
        flash('Entry başarıyla oluşturuldu!', 'success')
        return redirect(url_for('main.home'))
    trending_topics = get_trending_topics()
    return render_template('create_entry.html', title='Yeni Entry',
                         form=form, legend='Yeni Entry', trending_topics=trending_topics)

@main.route('/entry/<int:entry_id>')
def entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    form = EntryForm()
    trending_topics = get_trending_topics()
    return render_template('entry.html', title=entry.title, entry=entry, form=form, trending_topics=trending_topics)

@main.route('/entry/<int:entry_id>/update', methods=['GET', 'POST'])
@login_required
def update_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.author != current_user:
        abort(403)
    form = EntryForm()
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.content = form.content.data
        db.session.commit()
        flash('Entry başarıyla güncellendi!', 'success')
        return redirect(url_for('main.entry', entry_id=entry.id))
    elif request.method == 'GET':
        form.title.data = entry.title
        form.content.data = entry.content
    trending_topics = get_trending_topics()
    return render_template('create_entry.html', title='Entry Güncelle',
                         form=form, legend='Entry Güncelle', trending_topics=trending_topics)

@main.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.author != current_user:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry başarıyla silindi!', 'success')
    return redirect(url_for('main.home'))

@main.route('/user/<string:username>')
def profile(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    entries = Entry.query.filter_by(author=user)\
        .order_by(Entry.date_posted.desc())\
        .paginate(page=page, per_page=10)
    trending_topics = get_trending_topics()
    return render_template('profile.html', entries=entries, user=user, trending_topics=trending_topics)

@main.route('/entry/<int:entry_id>/like', methods=['POST'])
@login_required
def like_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    like = Like.query.filter_by(user_id=current_user.id, entry_id=entry.id).first()
    
    if like:
        db.session.delete(like)
    else:
        like = Like(user_id=current_user.id, entry_id=entry.id)
        db.session.add(like)
    
    db.session.commit()
    return redirect(request.referrer)

@main.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        # Yazar araması (@kullanıcı_adı)
        if query.startswith('@'):
            username = query[1:]
            user = User.query.filter(User.username.contains(username)).first()
            if user:
                return redirect(url_for('main.profile', username=user.username))
            else:
                entries = Entry.query.filter(Entry.title.contains(query)).paginate(page=page, per_page=10)
        # Entry araması (#entry_id)
        elif query.startswith('#'):
            try:
                entry_id = int(query[1:])
                entry = Entry.query.get(entry_id)
                if entry:
                    return redirect(url_for('main.entry', entry_id=entry.id))
            except ValueError:
                pass
            entries = Entry.query.filter(Entry.title.contains(query)).paginate(page=page, per_page=10)
        # Normal arama (başlık ve içerik)
        else:
            entries = Entry.query.join(User).filter(
                or_(
                    Entry.title.contains(query),
                    Entry.content.contains(query),
                    User.username.contains(query)
                )
            ).order_by(Entry.date_posted.desc()).paginate(page=page, per_page=10)
    else:
        entries = Entry.query.order_by(Entry.date_posted.desc()).paginate(page=page, per_page=10)
    
    trending_topics = get_trending_topics()
    return render_template('home.html', entries=entries, search_query=query, trending_topics=trending_topics)

@main.route('/popular')
def popular():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    subquery = db.session.query(
        Entry.id,
        func.count(Like.id).label('like_count')
    ).outerjoin(Like).group_by(Entry.id).subquery()
    
    total = db.session.query(func.count(Entry.id)).scalar()
    entries = db.session.query(Entry).join(
        subquery, Entry.id == subquery.c.id
    ).order_by(desc(subquery.c.like_count)).limit(per_page).offset(offset).all()
    
    has_next = offset + per_page < total
    has_prev = page > 1
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'items': entries,
        'has_next': has_next,
        'has_prev': has_prev,
        'pages': (total + per_page - 1) // per_page
    }
    
    trending_topics = get_trending_topics()
    return render_template('home.html', entries=pagination, trending_topics=trending_topics)

@main.route('/entry/<int:entry_id>/reply', methods=['POST'])
@login_required
def reply_entry(entry_id):
    parent_entry = Entry.query.get_or_404(entry_id)
    form = EntryForm()
    if form.validate_on_submit():
        reply = Entry(
            title=parent_entry.title,
            content=form.content.data,
            author=current_user,
            parent_id=entry_id
        )
        db.session.add(reply)
        db.session.commit()
        flash('Yanıtınız başarıyla gönderildi!', 'success')
    return redirect(url_for('main.entry', entry_id=entry_id)) 