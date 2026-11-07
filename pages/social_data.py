"""Portable JSON storage for LamGo posts, comments, likes and notifications.

This is local storage: accounts on the same installation share it. For users on
separate laptops to see each other's activity, configure a hosted backend.
"""
import json
import os
import uuid
import shutil
from datetime import datetime, timezone
from .paths import user_data_path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOCIAL_FILE = user_data_path('social_data.json', os.path.join(BASE_DIR, 'social_data.json'))


def _read():
    try:
        with open(SOCIAL_FILE, encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write(data):
    os.makedirs(os.path.dirname(SOCIAL_FILE), exist_ok=True)
    temp = SOCIAL_FILE + '.tmp'
    with open(temp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp, SOCIAL_FILE)


def load_social_data():
    data = _read()
    posts = data.get('posts', [])
    changed = False
    for post in posts:
        if not post.get('id'):
            post['id'] = uuid.uuid4().hex; changed = True
        for key, value in {'likes': [], 'comments': [], 'owner': '', 'owner_name': 'LamGo traveller',
                           'place': '', 'text': '', 'rating': 0, 'photo': '', 'created_at': ''}.items():
            if key not in post:
                post[key] = value; changed = True
    if changed:
        data.update(posts=posts)
        _write(data)
    return posts


def save_social_data(posts):
    data = _read()
    data.pop('follows', None)  # remove obsolete follow data from older installations
    data.update(posts=posts)
    data.setdefault('notifications', {})
    _write(data)


def load_notifications(email):
    notifications = _read().get('notifications', {})
    return notifications.get((email or '').strip().lower(), [])


def add_notification(recipient, actor, kind, target_id='', detail=''):
    """Persist an activity notification for a user's inbox."""
    recipient = (recipient or '').strip().lower()
    actor = (actor or '').strip().lower()
    if not recipient or recipient == actor:
        return
    data = _read()
    inboxes = data.setdefault('notifications', {})
    inbox = inboxes.setdefault(recipient, [])
    inbox.insert(0, {
        'id': uuid.uuid4().hex, 'actor': actor, 'kind': kind,
        'target_id': target_id, 'detail': detail,
        'created_at': datetime.now(timezone.utc).isoformat(), 'read': False,
    })
    inboxes[recipient] = inbox[:300]
    _write(data)


def mark_notifications_read(email):
    data = _read()
    inboxes = data.setdefault('notifications', {})
    for item in inboxes.get((email or '').strip().lower(), []):
        item['read'] = True
    _write(data)



def store_uploaded_image(source_path, prefix='image'):
    """Copy an uploaded image into LamGo's writable data folder and return its stable path."""
    if not source_path or not os.path.isfile(source_path):
        return ''
    folder = user_data_path('uploads', os.path.join(BASE_DIR, 'data', 'uploads'))
    os.makedirs(folder, exist_ok=True)
    ext = os.path.splitext(source_path)[1].lower() or '.jpg'
    target = os.path.join(folder, f"{prefix}_{uuid.uuid4().hex}{ext}")
    try:
        shutil.copy2(source_path, target)
        return target
    except OSError:
        return ''

def add_app_notification(recipient, kind, detail):
    """Create a non-social notification for an account."""
    recipient = (recipient or '').strip().lower()
    if not recipient: return
    data = _read(); inboxes = data.setdefault('notifications', {})
    inbox = inboxes.setdefault(recipient, [])
    inbox.insert(0, {'id': uuid.uuid4().hex, 'actor': 'lamgo', 'kind': kind,
                     'target_id': '', 'detail': detail,
                     'created_at': datetime.now(timezone.utc).isoformat(), 'read': False})
    inboxes[recipient] = inbox[:300]; _write(data)

def ensure_post_id(post):
    post.setdefault('id', uuid.uuid4().hex)
    post.setdefault('likes', [])
    post.setdefault('comments', [])
    return post
