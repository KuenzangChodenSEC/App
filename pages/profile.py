"""profile.py - the user's profile: photo, name, shortcuts, collections and a saved-places preview."""
import os
import tkinter as tk
from tkinter import filedialog

from .common import (COLORS, FONTS, PAGE_PAD, PLACES, card_grid, clear_frame, header,
                     load_image, make_button, rounded_card, scrollable)


class ProfilePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Profile')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        self.build_top_card(content)
        self.build_shortcuts(content)
        self.build_collections(content)
        self.build_saved_preview(content)

    # ------------------------------------------------------------------
    def build_top_card(self, content):
        """Avatar, name, email and the Edit / Change Photo buttons."""
        user = self.app.current_user
        top = rounded_card(content)
        top.pack(fill='x', padx=PAGE_PAD, pady=18)

        avatar = tk.Frame(top, bg='white', width=90, height=90)
        avatar.pack(side='left', padx=10)
        avatar.pack_propagate(False)
        photo = user.get('photo', '')
        if photo and os.path.exists(photo):
            image = load_image(photo, (85, 85))
            picture = tk.Label(avatar, image=image, bg='white')
            picture.image = image                         # keep a reference
            picture.pack(fill='both', expand=True)
        else:
            tk.Label(avatar, text='👤', font=('Segoe UI Emoji', 45), bg='white').pack(expand=True)

        info = tk.Frame(top, bg='white')
        info.pack(side='left', fill='x', expand=True)
        tk.Label(info, text=user.get('name', 'Guest'), font=FONTS['title'], bg='white').pack(anchor='w')
        tk.Label(info, text=user.get('email', ''), font=FONTS['body'], bg='white',
                 fg=COLORS['muted']).pack(anchor='w')

        make_button(top, 'Edit Profile', self.edit_profile, True).pack(side='right', padx=5)
        make_button(top, 'Change Photo', self.change_photo, False).pack(side='right', padx=5)

    def build_shortcuts(self, content):
        """Buttons to the user's own pages, plus Logout."""
        menu = rounded_card(content)
        menu.pack(fill='x', padx=PAGE_PAD, pady=(0, 15))
        shortcuts = [('📌 My Saved Places', 'Saved Places'), ('📝 My Posts', 'My Posts'),
                     ('🔔 Notifications', 'Notifications'), ('📍 Live Location', 'Location'), ('👥 Follow / Friends', 'Follow / Friends')]
        for text, page in shortcuts:
            make_button(menu, text, lambda p=page: self.app.show_page(p), False).pack(
                side='left', expand=True, padx=5)
        make_button(menu, '⇥ Logout', self.app.logout, False).pack(side='left', expand=True, padx=5)

    def build_collections(self, content):
        card = rounded_card(content)
        card.pack(fill='x', padx=PAGE_PAD, pady=(0, 25))
        tk.Label(card, text='My Collections', font=FONTS['heading'], bg='white').pack(anchor='w')
        row = tk.Frame(card, bg='white')
        row.pack(fill='x', pady=10)
        collections = [('🏔️ Most Visited', 'Most Visited'), ('🌿 Nature & Hiking', 'Nature & Hiking'),
                       ('🏯 Cultural Sites', 'Cultural Sites')]
        for text, page in collections:
            make_button(row, text, lambda p=page: self.app.show_page(p), False).pack(
                side='left', fill='x', expand=True, padx=5)

    def build_saved_preview(self, content):
        card = rounded_card(content)
        card.pack(fill='x', padx=PAGE_PAD, pady=(0, 30))
        tk.Label(card, text='Saved Places Preview', font=FONTS['heading'], bg='white').pack(anchor='w')

        saved = [p for p in PLACES if p['name'] in self.app.saved_places]
        if not saved:
            tk.Label(card, text='No saved places yet.', font=FONTS['body'], bg='white',
                     fg=COLORS['muted']).pack(anchor='w', pady=12)
        else:
            card_grid(card, self.app, saved, compact=True, min_w=220, max_rows=1,
                      bg='white').pack(fill='x', pady=8)

    # ------------------------------------------------------------------
    def change_photo(self):
        """Pick a new profile picture from the computer."""
        path = filedialog.askopenfilename(title='Choose profile photo',
                                          filetypes=[('Image files', '*.png *.jpg *.jpeg *.gif')])
        if path:
            self.app.current_user['photo'] = path
            self.app.save_current_user()
            self.refresh()

    def edit_profile(self):
        """Small pop-up window to change the name and email."""
        user = self.app.current_user
        win = tk.Toplevel(self)
        win.title('Edit Profile')
        win.geometry('430x270')
        win.configure(bg='white')
        win.transient(self.app)
        win.grab_set()

        box = tk.Frame(win, bg='white', padx=25, pady=22)
        box.pack(fill='both', expand=True)
        tk.Label(box, text='Edit Profile', font=FONTS['heading'], bg='white').pack(anchor='w')

        tk.Label(box, text='Name', font=FONTS['small'], bg='white').pack(anchor='w', pady=(12, 2))
        name = tk.Entry(box, font=FONTS['body'])
        name.insert(0, user.get('name', ''))
        name.pack(fill='x', ipady=6)

        tk.Label(box, text='Email', font=FONTS['small'], bg='white').pack(anchor='w', pady=(8, 2))
        email = tk.Entry(box, font=FONTS['body'])
        email.insert(0, user.get('email', ''))
        email.pack(fill='x', ipady=6)

        def save():
            # Keep the old value if a box was left empty
            user['name'] = name.get().strip() or user.get('name', '')
            user['email'] = email.get().strip() or user.get('email', '')
            self.app.save_current_user()
            win.destroy()
            self.refresh()

        make_button(box, 'Save Changes', save, True).pack(fill='x', pady=14)
