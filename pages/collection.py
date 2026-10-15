"""collection.py - lists places for one collection (Most Visited, Nature & Hiking, Cultural Sites)."""
import tkinter as tk

from .common import COLORS, FONTS, PAGE_PAD, PLACES, card_grid, clear_frame, header, scrollable


class CollectionPage(tk.Frame):
    def __init__(self, parent, app, collection_name='Most Visited'):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.collection_name = collection_name
        self.refresh()

    def places_in_collection(self):
        """Choose which places belong to this collection."""
        if self.collection_name == 'Most Visited':
            return sorted(PLACES, key=lambda p: p['reviews'], reverse=True)[:8]
        if self.collection_name == 'Nature & Hiking':
            return [p for p in PLACES if p['type'] == 'Nature & Hiking']
        return [p for p in PLACES if p['type'] == 'Cultural Sites']

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Profile')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        tk.Label(content, text=self.collection_name, font=FONTS['title'],
                 bg=COLORS['bg']).pack(anchor='w', padx=PAGE_PAD, pady=(20, 5))
        tk.Label(content, text='Places in this collection.', font=FONTS['body'],
                 bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD)

        card_grid(content, self.app, self.places_in_collection()).pack(
            fill='x', padx=PAGE_PAD - 7, pady=15)
