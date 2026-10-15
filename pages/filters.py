"""filters.py - choose a category; opens Explore filtered by it."""
import tkinter as tk

from .common import (COLORS, FONTS, PAGE_PAD, clear_frame, header, make_button,
                     rounded_card, scrollable)

CATEGORIES = ['Mountains', 'Nature & Hiking', 'Cultural Sites', 'Cities']


class FiltersPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Explore')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        box = rounded_card(content)
        box.pack(fill='x', padx=PAGE_PAD, pady=35)
        tk.Label(box, text='Choose a Category', font=FONTS['title'], bg='white').pack(anchor='w')

        for category in CATEGORIES:
            make_button(box, category, lambda c=category: self.app.show_page('Explore', search=c),
                        False).pack(fill='x', pady=5)
        make_button(box, 'Show All Places', lambda: self.app.show_page('Explore', search=''),
                    True).pack(fill='x', pady=(15, 0))
