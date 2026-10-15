"""Follow / Friends: discover LamGo travellers, follow them and like their posts."""
import json
import os
import tkinter as tk
from tkinter import simpledialog
from datetime import datetime

from .common import COLORS, FONTS, PAGE_PAD, autowrap, clear_frame, header, load_image, make_button, rounded_card, scrollable
from .social_data import save_social_data, add_notification


class SocialPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.mode = tk.StringVar(value='Following & everyone')
        self.refresh()

    def _accounts(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'users.json')
        try:
            with open(path, encoding='utf-8') as f:
                raw = json.load(f)
            accounts = []
            for key, user in raw.items():
                email = (user.get('email') or key).strip().lower()
                if email:
                    accounts.append({'email': email, 'name': user.get('name') or email.split('@')[0],
                                     'photo': user.get('photo', '')})
            return accounts
        except (OSError, json.JSONDecodeError, AttributeError):
            return []

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Follow / Friends')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)
        tk.Label(content, text='Your LamGo community', font=FONTS['title'], bg=COLORS['bg'],
                 fg=COLORS['brown_dark']).pack(anchor='w', padx=PAGE_PAD, pady=(20, 2))
        tk.Label(content, text='Follow travellers, discover their posts and learn from real visitor experiences.',
                 font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD, pady=(0, 14))

        bar = tk.Frame(content, bg=COLORS['bg'])
        bar.pack(fill='x', padx=PAGE_PAD, pady=(0, 10))
        for label in ('Following & everyone', 'Following only', 'Discover people'):
            tk.Radiobutton(bar, text=label, value=label, variable=self.mode, command=self.refresh,
                           bg=COLORS['bg'], fg=COLORS['brown_dark'], selectcolor=COLORS['cream'],
                           activebackground=COLORS['bg'], font=FONTS['body']).pack(side='left', padx=(0, 14))

        accounts = self._accounts()
        me = self.app.current_user.get('email', '').lower()
        accounts = [u for u in accounts if u['email'] != me]
        following = self.app.following.setdefault(me, [])
        if self.mode.get() == 'Following only':
            accounts = [u for u in accounts if u['email'] in following]
        elif self.mode.get() == 'Discover people':
            accounts = [u for u in accounts if u['email'] not in following]

        people = rounded_card(content)
        people.pack(fill='x', padx=PAGE_PAD, pady=(0, 16))
        tk.Label(people, text=f'People ({len(accounts)})', font=FONTS['heading'], bg=COLORS['white'],
                 fg=COLORS['brown_dark']).pack(anchor='w', pady=(0, 8))
        if not accounts:
            tk.Label(people, text='No accounts to show here yet. Invite friends to create a LamGo account.',
                     font=FONTS['body'], bg=COLORS['white'], fg=COLORS['muted']).pack(anchor='w', pady=10)
        for user in accounts:
            self._person_row(people, user, me, following)

        feed = tk.Frame(content, bg=COLORS['bg'])
        feed.pack(fill='x', padx=PAGE_PAD, pady=(0, 30))
        tk.Label(feed, text='Traveller posts', font=FONTS['heading'], bg=COLORS['bg'],
                 fg=COLORS['brown_dark']).pack(anchor='w', pady=(0, 8))
        posts = list(reversed(self.app.posts))
        if self.mode.get() == 'Following only':
            posts = [p for p in posts if p.get('owner', '').lower() in following or p.get('owner', '').lower() == me]
        if not posts:
            tk.Label(feed, text='No posts yet. Be the first to share a place review!', font=FONTS['body'],
                     bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', pady=18)
        for post in posts:
            self._post_card(feed, post, me)

    def _person_row(self, parent, user, me, following):
        row = tk.Frame(parent, bg=COLORS['white'], pady=8)
        row.pack(fill='x', pady=3)
        avatar = tk.Frame(row, bg=COLORS['cream'], width=48, height=48)
        avatar.pack(side='left', padx=(0, 10)); avatar.pack_propagate(False)
        photo_path = user.get('photo', '')
        img = load_image(photo_path, (46, 46)) if photo_path and os.path.exists(photo_path) else None
        if img:
            label = tk.Label(avatar, image=img, bg=COLORS['cream']); label.image = img; label.pack(fill='both', expand=True)
        else:
            tk.Label(avatar, text='👤', font=('Segoe UI Emoji', 22), bg=COLORS['cream']).pack(expand=True)
        info = tk.Frame(row, bg=COLORS['white']); info.pack(side='left', fill='x', expand=True)
        tk.Label(info, text=user['name'], font=FONTS['subheading'], bg=COLORS['white'],
                 fg=COLORS['text']).pack(anchor='w')
        count = sum(1 for p in self.app.posts if p.get('owner', '').lower() == user['email'])
        tk.Label(info, text=f"{count} post(s) · {user['email']}", font=FONTS['small'],
                 bg=COLORS['white'], fg=COLORS['muted']).pack(anchor='w')
        make_button(row, 'View profile & posts', lambda u=user: self.view_user(u), False).pack(side='right', padx=5)
        if user['email'] in following:
            button_text = 'Following ✓'
        elif me in self.app.following.get(user['email'], []):
            button_text = 'Follow back'
        else:
            button_text = '＋ Follow'
        make_button(row, button_text, lambda e=user['email']: self.toggle_follow(e), button_text != 'Following ✓').pack(side='right', padx=5)

    def _post_card(self, parent, post, me):
        card = rounded_card(parent)
        card.pack(fill='x', pady=7)
        owner = post.get('owner', '').lower()
        title = tk.Frame(card, bg=COLORS['white']); title.pack(fill='x')
        tk.Button(title, text=f"{post.get('owner_name', 'Traveller')}  ·  {post.get('place', 'Bhutan')}",
                  command=lambda: self.view_user({'email': owner, 'name': post.get('owner_name', 'Traveller'), 'photo': ''}),
                  font=FONTS['subheading'], bg=COLORS['white'], fg=COLORS['brown_dark'], bd=0,
                  cursor='hand2').pack(side='left', anchor='w')
        rating = int(post.get('rating') or 0)
        tk.Label(title, text=('★' * rating + '☆' * (5-rating)) if rating else 'No rating',
                 font=FONTS['body'], bg=COLORS['white'], fg=COLORS['gold']).pack(side='right')
        body = tk.Label(card, text=post.get('text', ''), font=FONTS['body'], bg=COLORS['white'],
                        fg=COLORS['text'], justify='left', anchor='w')
        body.pack(fill='x', pady=(8, 6)); autowrap(body)
        photo = post.get('photo', '')
        if photo and os.path.exists(photo):
            img = load_image(photo, (500, 260))
            if img:
                pic = tk.Label(card, image=img, bg=COLORS['white']); pic.image = img; pic.pack(anchor='w', pady=5)
        likes = post.setdefault('likes', [])
        liked = me in likes
        actions = tk.Frame(card, bg=COLORS['white']); actions.pack(fill='x', anchor='w', pady=(6, 0))
        make_button(actions, f"{'♥' if liked else '♡'}  {len(likes)} Like" + ('d' if len(likes) != 1 else ''),
                    lambda p=post: self.toggle_like(p), primary=liked).pack(side='left', padx=(0, 8))
        comments = post.setdefault('comments', [])
        make_button(actions, f'💬 Comment ({len(comments)})', lambda p=post: self.add_comment(p), False).pack(side='left')
        if comments:
            comment_box = tk.Frame(card, bg=COLORS['cream'], padx=10, pady=7); comment_box.pack(fill='x', pady=(8, 0))
            for comment in comments[-3:]:
                tk.Label(comment_box, text=f"{comment.get('name', 'Traveller')}: {comment.get('text', '')}",
                         font=FONTS['small'], bg=COLORS['cream'], fg=COLORS['text'], wraplength=850, justify='left').pack(anchor='w', pady=2)

    def toggle_follow(self, email):
        me = self.app.current_user.get('email', '').lower()
        people = self.app.following.setdefault(me, [])
        if email in people:
            people.remove(email)
        else:
            people.append(email)
            add_notification(email, me, 'follow', detail=f"{self.app.current_user.get('name', 'A traveller')} started following you.")
        save_social_data(self.app.posts, self.app.following)
        self.refresh()

    def toggle_like(self, post):
        me = self.app.current_user.get('email', '').lower()
        likes = post.setdefault('likes', [])
        if me in likes:
            likes.remove(me)
        elif me:
            likes.append(me)
            add_notification(post.get('owner', ''), me, 'like', post.get('id', ''),
                             f"{self.app.current_user.get('name', 'A traveller')} liked your post about {post.get('place', 'a place')}.")
        save_social_data(self.app.posts, self.app.following)
        self.refresh()

    def add_comment(self, post):
        me = self.app.current_user.get('email', '').lower()
        text = simpledialog.askstring('Comment on post', 'Write your comment:', parent=self)
        if not text or not text.strip() or not me:
            return
        comment = {'id': __import__('uuid').uuid4().hex, 'owner': me,
                   'name': self.app.current_user.get('name', 'Traveller'), 'text': text.strip(),
                   'created_at': datetime.now().isoformat(timespec='seconds')}
        post.setdefault('comments', []).append(comment)
        add_notification(post.get('owner', ''), me, 'comment', post.get('id', ''),
                         f"{comment['name']} commented on your post about {post.get('place', 'a place')}.")
        save_social_data(self.app.posts, self.app.following)
        self.refresh()

    def view_user(self, user):
        clear_frame(self)
        header(self, self.app, 'Follow / Friends')
        outer, content = scrollable(self); outer.pack(fill='both', expand=True)
        tk.Label(content, text=user.get('name', 'Traveller'), font=FONTS['title'], bg=COLORS['bg'],
                 fg=COLORS['brown_dark']).pack(anchor='w', padx=PAGE_PAD, pady=(22, 4))
        tk.Label(content, text=user.get('email', ''), font=FONTS['body'], bg=COLORS['bg'],
                 fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD)
        me = self.app.current_user.get('email', '').lower(); email = user.get('email', '').lower()
        if email and email != me:
            followed = email in self.app.following.setdefault(me, [])
            follows_me = me in self.app.following.get(email, [])
            button_text = 'Following ✓' if followed else ('Follow back' if follows_me else '＋ Follow')
            make_button(content, button_text, lambda: self.toggle_follow(email), not followed).pack(anchor='w', padx=PAGE_PAD, pady=10)
        user_posts = [p for p in reversed(self.app.posts) if p.get('owner', '').lower() == email]
        ratings = [int(p.get('rating') or 0) for p in user_posts if int(p.get('rating') or 0) > 0]
        avg = sum(ratings) / len(ratings) if ratings else 0
        tk.Label(content, text=f'{len(user_posts)} posts · {len(ratings)} place rating(s) · Average rating given: {avg:.1f}/5',
                 font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD, pady=8)
        for post in user_posts:
            self._post_card(content, post, me)
        if not user_posts:
            tk.Label(content, text='This traveller has not posted yet.', font=FONTS['body'], bg=COLORS['bg'],
                     fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD, pady=20)
        make_button(content, '← Back to people', self.refresh, False).pack(anchor='w', padx=PAGE_PAD, pady=20)
