"""
dzongkhag_page.py - opens when you click a dzongkhag on the Home page (e.g. Thimphu).

Shows: big photo, rating, description, best time to travel, climate, three photos
and every place to visit in that dzongkhag (best match for the user first).
"""
import tkinter as tk

from .common import (COLORS, FONTS, PAGE_PAD, PLACES, autowrap, card_grid, clear_frame,
                     dzongkhag_image_path, header, image_banner, make_button, rounded_card,
                     scrollable)
from .dzongkhag_data import DZONGKHAGS, dzongkhag_rating, places_in
from .recommender import notes_for, recommend


class DzongkhagPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Home')
        dz = self.app.selected_dzongkhag or DZONGKHAGS[0]
        rating, reviews, count = dzongkhag_rating(dz)
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        # Title, subtitle and the large photo
        tk.Label(content, text=dz['name'], font=FONTS['title'], bg=COLORS['bg']).pack(
            anchor='w', padx=PAGE_PAD, pady=(20, 2))
        tk.Label(content, text=dz['tagline'], font=FONTS['subheading'], bg=COLORS['bg'],
                 fg=COLORS['green']).pack(anchor='w', padx=PAGE_PAD)
        stars = f'★ {rating} ({reviews:,} reviews)' if count else 'No ratings yet'
        tk.Label(content, text=f"📍 {dz['region']} Bhutan  •  Main town: {dz['town']}  •  {stars}  •  "
                               f"{count} place{'s' if count != 1 else ''} to visit",
                 font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(
            anchor='w', padx=PAGE_PAD, pady=(4, 0))
        image_banner(content, height=380, path=dzongkhag_image_path(dz)).pack(
            fill='x', padx=PAGE_PAD, pady=15)

        self.build_info(content, dz, rating, reviews, count)
        self.build_photos(content, dz)
        self.build_places(content, dz)

    # ------------------------------------------------------------------
    def build_info(self, content, dz, rating, reviews, count):
        card = rounded_card(content)
        card.pack(fill='x', padx=PAGE_PAD)

        tk.Label(card, text=f"About {dz['name']}", font=FONTS['heading'], bg='white').pack(anchor='w')
        about = tk.Label(card, text=dz['description'], font=('Segoe UI', 11), bg='white',
                         fg=COLORS['muted'], justify='left', anchor='w')
        about.pack(fill='x', pady=8)
        autowrap(about)

        # Row of fact boxes
        stats = tk.Frame(card, bg='white')
        stats.pack(fill='x', pady=8)
        facts = [('Rating', f'★ {rating}' if count else '-'),
                 ('Best time to travel', dz['best']),
                 ('Places to visit', str(count)),
                 ('Region', f"{dz['region']} Bhutan")]
        for title, value in facts:
            box = tk.Frame(stats, bg='#F6F8F6', padx=10, pady=10)
            box.pack(side='left', fill='both', expand=True, padx=3)
            tk.Label(box, text=title, font=FONTS['small'], bg='#F6F8F6', fg=COLORS['muted']).pack()
            tk.Label(box, text=value, font=FONTS['subheading'], bg='#F6F8F6', wraplength=220).pack()

        # Climate gets its own full-width box because it is a longer text
        climate = tk.Frame(card, bg='#EAF6EF', padx=14, pady=10)
        climate.pack(fill='x', pady=(8, 4), padx=3)
        tk.Label(climate, text='🌤  Climate', font=FONTS['subheading'], bg='#EAF6EF',
                 fg=COLORS['green_dark']).pack(anchor='w')
        climate_text = tk.Label(climate, text=dz['climate'], font=('Segoe UI', 11), bg='#EAF6EF',
                                fg=COLORS['text'], justify='left', anchor='w')
        climate_text.pack(fill='x', pady=(4, 0))
        autowrap(climate_text)

        # Typical temperatures reported for the places inside this dzongkhag
        temps = sorted({p['weather'] for p in places_in(dz) if p['weather'] != 'Varies'})
        if temps:
            tk.Label(climate, text='Typical temperature at its places: ' + ', '.join(temps),
                     font=FONTS['small'], bg='#EAF6EF', fg=COLORS['muted']).pack(anchor='w', pady=(4, 0))

        actions = tk.Frame(card, bg='white')
        actions.pack(fill='x', pady=(10, 0))
        make_button(actions, '📍 Open in Google Maps', lambda: self.open_map(dz), True).pack(side='left')
        make_button(actions, '← All dzongkhags', lambda: self.app.show_page('Home'), False).pack(
            side='left', padx=8)

    @staticmethod
    def open_map(dz):
        import webbrowser
        from urllib.parse import quote
        webbrowser.open('https://www.google.com/maps/search/?api=1&query='
                        + quote(f"{dz['name']} Dzongkhag, Bhutan"))

    def build_photos(self, content, dz):
        card = rounded_card(content)
        card.pack(fill='x', padx=PAGE_PAD, pady=18)
        tk.Label(card, text=f"Photos of {dz['name']}", font=FONTS['heading'], bg='white').pack(anchor='w')
        row = tk.Frame(card, bg='white')
        row.pack(fill='x', pady=8)
        for column in range(3):
            row.grid_columnconfigure(column, weight=1, uniform='photos')
            image_banner(row, height=220, path=dzongkhag_image_path(dz, column + 1)).grid(
                row=0, column=column, padx=5, sticky='ew')

    def build_places(self, content, dz):
        """Every place in this dzongkhag, ordered for this user (interests, searches, location)."""
        names = {p['name'] for p in places_in(dz)}
        ranked = [r for r in recommend('', self.app.activity, self.app.user_location)
                  if r['place']['name'] in names]
        tk.Label(content, text=f"Places to visit in {dz['name']}", font=FONTS['heading'],
                 bg=COLORS['bg']).pack(anchor='w', padx=PAGE_PAD, pady=(4, 8))
        if not ranked:
            tk.Label(content, text='No places have been added for this dzongkhag yet.',
                     font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(pady=30)
            return
        card_grid(content, self.app, [r['place'] for r in ranked],
                  notes=notes_for(ranked)).pack(fill='x', padx=PAGE_PAD - 7, pady=(0, 30))
