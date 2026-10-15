"""create_post.py - form to share a photo, rating and experience about a place."""
import os
import tkinter as tk
from tkinter import filedialog, ttk

from .social_data import save_social_data, ensure_post_id
from .common import (COLORS, FONTS, PAGE_PAD, PLACES, autowrap, clear_frame, header,
                     make_button, rounded_card, scrollable, show_dialog)


class CreatePostPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.photo_path = ''                # picture chosen from the computer
        self.rating = tk.IntVar(value=0)    # 0-5 stars
        self.refresh()

    def refresh(self):
        clear_frame(self)
        self.photo_path = ''                # the form is rebuilt empty, so reset its state
        self.rating.set(0)

        header(self, self.app, 'Create Post')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        tk.Label(content, text='Create a Post', font=FONTS['title'], bg=COLORS['bg']).pack(
            anchor='w', padx=PAGE_PAD, pady=(20, 5))
        tk.Label(content, text='Share a place, photo and your experience.', font=FONTS['body'],
                 bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD)

        # Two columns: the form (left) and a preview of recent posts (right)
        body = tk.Frame(content, bg=COLORS['bg'])
        body.pack(fill='x', padx=PAGE_PAD, pady=15)
        self.build_form(body)
        self.build_recent_posts(body)

    # ------------------------------------------------------------------
    def build_form(self, body):
        form = rounded_card(body)
        form.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Picture
        self.upload = tk.Button(form, text='📷 Choose Picture from Desktop', command=self.choose_photo,
                                font=FONTS['body'], bg=COLORS['green_light'], fg=COLORS['brown_dark'], bd=0,
                                height=3, cursor='hand2')
        self.upload.pack(fill='x', pady=8)

        # Place drop-down
        tk.Label(form, text='Place', font=FONTS['subheading'], bg='white').pack(anchor='w', pady=(8, 3))
        self.place = ttk.Combobox(form, values=[p['name'] for p in PLACES], state='readonly')
        self.place.pack(fill='x')
        # Pre-select the place the user was last looking at
        selected = self.app.selected_place or PLACES[0]
        self.place.set(selected['name'])

        # Star rating
        tk.Label(form, text='Rating', font=FONTS['subheading'], bg='white').pack(anchor='w', pady=(10, 3))
        stars = tk.Frame(form, bg='white')
        stars.pack(anchor='w')
        self.star_buttons = []
        for number in range(1, 6):
            button = tk.Button(stars, text='☆', font=('Segoe UI', 20), fg=COLORS['gold'], bg='white',
                               bd=0, cursor='hand2', command=lambda n=number: self.set_rating(n))
            button.pack(side='left')
            self.star_buttons.append(button)

        # Text
        tk.Label(form, text='Your Experience', font=FONTS['subheading'], bg='white').pack(
            anchor='w', pady=(10, 3))
        self.experience = tk.Text(form, height=7, wrap='word', font=FONTS['body'])
        self.experience.pack(fill='x')

        make_button(form, 'Create Post', self.post, True).pack(fill='x', pady=15)
        make_button(form, 'View My Posts', lambda: self.app.show_page('My Posts'), False).pack(fill='x')

    def build_recent_posts(self, body):
        card = rounded_card(body)
        card.pack(side='left', fill='both', expand=True, padx=(10, 0))
        tk.Label(card, text='My Posts', font=FONTS['heading'], bg='white').pack(anchor='w')

        email = self.app.current_user.get('email')
        posts = [p for p in self.app.posts if p.get('owner', email) == email]
        if not posts:
            tk.Label(card, text='Your posts will appear here after you create one.',
                     font=FONTS['body'], bg='white', fg=COLORS['muted']).pack(anchor='w', pady=15)

        for post in posts[-5:]:                           # the five most recent
            tk.Label(card, text=f"{post.get('place', '')}  ★ {post.get('rating', 0)}",
                     font=FONTS['subheading'], bg='white').pack(anchor='w', pady=(10, 2))
            text = tk.Label(card, text=post.get('text', ''), font=FONTS['body'], bg='white',
                            fg=COLORS['muted'], justify='left', anchor='w')
            text.pack(fill='x')
            autowrap(text)

    # ------------------------------------------------------------------
    def choose_photo(self):
        """Let the user pick a picture file from their computer."""
        path = filedialog.askopenfilename(title='Choose a picture',
                                          filetypes=[('Image files', '*.png *.jpg *.jpeg *.gif')])
        if path:
            self.photo_path = path
            self.upload.config(text='✓ ' + os.path.basename(path))

    def set_rating(self, number):
        """Fill the first `number` stars."""
        self.rating.set(number)
        for index, button in enumerate(self.star_buttons, start=1):
            button.config(text='★' if index <= number else '☆')

    def post(self):
        """Save the post and open My Posts."""
        text = self.experience.get('1.0', 'end').strip()
        if not text:
            show_dialog(self, 'Post', 'Write something about your visit.', 'warning')
            return
        post = {
            'owner': self.app.current_user.get('email', '').lower(),
            'owner_name': self.app.current_user.get('name'),
            'place': self.place.get(),
            'text': text,
            'rating': self.rating.get(),
            'photo': self.photo_path,
            'likes': [],
        }
        ensure_post_id(post)
        self.app.posts.append(post)
        save_social_data(self.app.posts, self.app.following)
        self.app.refresh_user_ratings()
        chosen = next((p for p in PLACES if p['name'] == self.place.get()), None)
        if chosen:
            self.app.activity.record_review(chosen)
        show_dialog(self, 'Posted', 'Your post was created.', 'success')
        self.app.show_page('My Posts')
