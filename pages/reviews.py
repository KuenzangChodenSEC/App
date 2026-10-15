"""User-generated place reviews and ratings; no fabricated sample reviews."""
import tkinter as tk
from tkinter import simpledialog

from .common import (COLORS, FONTS, PAGE_PAD, PLACES, clear_frame, header, make_button,
                     rounded_card, scrollable, show_dialog)
from .social_data import save_social_data, ensure_post_id


class ReviewsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def current_place(self):
        return self.app.selected_place or PLACES[0]

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Reviews')
        outer, content = scrollable(self); outer.pack(fill='both', expand=True)
        place = self.current_place()
        reviews = [p for p in self.app.posts if p.get('place') == place['name'] and p.get('text') and int(p.get('rating') or 0) > 0]
        ratings = [int(p['rating']) for p in reviews]
        average = sum(ratings) / len(ratings) if ratings else 0
        tk.Label(content, text='Reviews & Ratings', font=FONTS['title'], bg=COLORS['bg'], fg=COLORS['brown_dark']).pack(anchor='w', padx=PAGE_PAD, pady=(20, 4))
        tk.Label(content, text=place['name'], font=FONTS['subheading'], bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD, pady=(0, 12))
        summary = rounded_card(content); summary.pack(fill='x', padx=PAGE_PAD)
        tk.Label(summary, text=f'{average:.1f}', font=('Segoe UI', 38, 'bold'), bg=COLORS['white'], fg=COLORS['text']).pack(side='left', padx=20)
        tk.Label(summary, text=(('★' * round(average)) + ('☆' * (5-round(average))) + f'\nBased on {len(ratings)} user rating(s)') if ratings else 'No user ratings yet\nBe the first to rate this place', font=FONTS['body'], fg=COLORS['gold'], bg=COLORS['white']).pack(side='left')
        make_button(summary, 'Write a Review', self.write_review, True).pack(side='right', padx=10)
        box = rounded_card(content); box.pack(fill='x', padx=PAGE_PAD, pady=16)
        tk.Label(box, text='Visitor Reviews', font=FONTS['heading'], bg=COLORS['white'], fg=COLORS['brown_dark']).pack(anchor='w')
        if not reviews:
            tk.Label(box, text='Reviews from LamGo users will appear here after someone posts a rating.', font=FONTS['body'], bg=COLORS['white'], fg=COLORS['muted']).pack(anchor='w', pady=15)
        for post in reversed(reviews):
            row = tk.Frame(box, bg=COLORS['cream'], padx=12, pady=10); row.pack(fill='x', pady=4)
            tk.Label(row, text=f"{post.get('owner_name') or 'LamGo traveller'}  ·  {'★' * int(post.get('rating') or 0)}", font=FONTS['subheading'], bg=COLORS['cream'], fg=COLORS['brown_dark']).pack(anchor='w')
            tk.Label(row, text=post.get('text', ''), font=FONTS['body'], bg=COLORS['cream'], fg=COLORS['text'], justify='left', wraplength=900).pack(anchor='w', pady=(5, 0))

    def write_review(self):
        text = simpledialog.askstring('Write a Review', 'Share your experience with this place:', parent=self)
        if not text or not text.strip():
            return
        rating = simpledialog.askinteger('Your Rating', 'Give this place 1 to 5 stars:', parent=self, minvalue=1, maxvalue=5)
        if rating is None:
            return
        post = {'owner': self.app.current_user.get('email', '').lower(), 'owner_name': self.app.current_user.get('name', 'Traveller'),
                'place': self.current_place()['name'], 'text': text.strip(), 'rating': rating, 'photo': '', 'likes': []}
        ensure_post_id(post); self.app.posts.append(post); save_social_data(self.app.posts, self.app.following)
        self.app.refresh_user_ratings()
        self.app.activity.record_review(self.current_place())
        show_dialog(self, 'Review Added', 'Your review and rating have been saved.', 'success')
        self.refresh()
