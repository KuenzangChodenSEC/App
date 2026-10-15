"""my_posts.py - all posts created by the logged-in user."""
import os
import tkinter as tk

from .common import (COLORS, FONTS, PAGE_PAD, autowrap, clear_frame, header, load_image,
                     make_button, rounded_card, scrollable)


class MyPostsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Create Post')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        # Title row with a "Create Post" button
        top = tk.Frame(content, bg=COLORS['bg'])
        top.pack(fill='x', padx=PAGE_PAD, pady=18)
        tk.Label(top, text='My Posts', font=FONTS['title'], bg=COLORS['bg']).pack(side='left')
        make_button(top, 'Create Post', lambda: self.app.show_page('Create Post'), True).pack(side='right')

        email = self.app.current_user.get('email')
        posts = [p for p in self.app.posts if p.get('owner') == email]
        if not posts:
            tk.Label(content, text='You have not created a post yet.', font=FONTS['body'],
                     bg=COLORS['bg'], fg=COLORS['muted']).pack(pady=60)
            return

        for post in posts:
            self.add_post_card(content, post)

    def add_post_card(self, content, post):
        """One post: picture on the left, place / stars / text on the right."""
        card = rounded_card(content)
        card.pack(fill='x', padx=PAGE_PAD, pady=8)

        # Picture (or a "No photo" placeholder)
        left = tk.Frame(card, bg='white', width=220, height=150)
        left.pack(side='left')
        left.pack_propagate(False)
        photo = post.get('photo')
        if photo and os.path.exists(photo):
            image = load_image(photo, (210, 140))
            picture = tk.Label(left, image=image, bg='white')
            picture.image = image                         # keep a reference
            picture.pack(fill='both', expand=True)
        else:
            tk.Label(left, text='📷\nNo photo', font=('Segoe UI Emoji', 18), bg='#F0F5F1',
                     fg=COLORS['muted']).pack(fill='both', expand=True)

        # Text
        right = tk.Frame(card, bg='white', padx=18)
        right.pack(side='left', fill='both', expand=True)
        tk.Label(right, text=post.get('place', ''), font=FONTS['heading'], bg='white').pack(anchor='w')
        tk.Label(right, text='★ ' * post.get('rating', 0), font=FONTS['body'], fg=COLORS['gold'],
                 bg='white').pack(anchor='w')
        text = tk.Label(right, text=post.get('text', ''), font=FONTS['body'], bg='white',
                        fg=COLORS['muted'], justify='left', anchor='w')
        text.pack(fill='x', pady=8)
        autowrap(text)
