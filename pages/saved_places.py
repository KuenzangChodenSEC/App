"""saved_places.py - places the user marked with the heart button."""
import tkinter as tk

from .common import COLORS, FONTS, PAGE_PAD, PLACES, card_grid, clear_frame, header, scrollable


class SavedPlacesPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Profile')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        tk.Label(content, text='My Saved Places', font=FONTS['title'], bg=COLORS['bg']).pack(
            anchor='w', padx=PAGE_PAD, pady=(20, 5))
        tk.Label(content, text='Places you saved for a future visit.', font=FONTS['body'],
                 bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD)

        saved = [p for p in PLACES if p['name'] in self.app.saved_places]
        card_grid(content, self.app, saved).pack(fill='x', padx=PAGE_PAD - 7, pady=15)

        if not saved:
            tk.Label(content, text='No saved places yet. Go to Explore and click ♡.',
                     font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(pady=50)
