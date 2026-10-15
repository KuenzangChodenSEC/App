"""place_details.py - full information about one place: photo, description, stats, photos, similar places."""
import tkinter as tk

from .recommender import similar_places
from .common import (COLORS, FONTS, PAGE_PAD, PLACES, autowrap, card_grid, clear_frame, header,
                     image_banner, make_button, open_map, place_image_path, rounded_card, scrollable)


class PlaceDetailsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Explore')
        place = self.app.selected_place or PLACES[0]
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        # Title, subtitle and the large main photo of THIS place
        tk.Label(content, text=place['name'], font=FONTS['title'], bg=COLORS['bg']).pack(
            anchor='w', padx=PAGE_PAD, pady=(20, 5))
        tk.Label(content, text=f"📍 {place['location']}  •  ★ {place['rating']} ({place['reviews']} reviews)",
                 font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD)
        image_banner(content, height=400, path=place_image_path(place)).pack(
            fill='x', padx=PAGE_PAD, pady=15)

        self.build_info_card(content, place)
        self.build_photos(content, place)
        self.build_similar(content, place)

    # ------------------------------------------------------------------
    def build_info_card(self, content, place):
        """Description, quick facts and the action buttons."""
        info = rounded_card(content)
        info.pack(fill='x', padx=PAGE_PAD)

        tk.Label(info, text='About this place', font=FONTS['heading'], bg='white').pack(anchor='w')
        description = tk.Label(info, text=place['description'], font=('Segoe UI', 11), bg='white',
                               fg=COLORS['muted'], justify='left', anchor='w')
        description.pack(fill='x', pady=8)
        autowrap(description)

        # Row of small fact boxes
        stats = tk.Frame(info, bg='white')
        stats.pack(fill='x', pady=8)
        facts = [('Weather', place['weather']), ('Best Time', place['best']),
                 ('Travel Time', place['time']), ('Difficulty', place['difficulty']),
                 ('Elevation', place['elevation'])]
        for title, value in facts:
            box = tk.Frame(stats, bg='#F6F8F6', padx=10, pady=10)
            box.pack(side='left', fill='both', expand=True, padx=3)
            tk.Label(box, text=title, font=FONTS['small'], bg='#F6F8F6', fg=COLORS['muted']).pack()
            tk.Label(box, text=value, font=FONTS['small'], bg='#F6F8F6', wraplength=200).pack()

        # Buttons: map, reviews, save
        actions = tk.Frame(info, bg='white')
        actions.pack(fill='x', pady=12)
        saved_text = '♥ Save' if place['name'] in self.app.saved_places else '♡ Save'
        buttons = [
            ('📍 Live Location / Map', lambda: open_map(place), True),
            ('★ Reviews & Ratings', lambda: self.app.show_page('Reviews', place=place), False),
            (saved_text, lambda: self.app.toggle_saved(place), False),
        ]
        for text, command, primary in buttons:
            make_button(actions, text, command, primary).pack(side='left', fill='x', expand=True, padx=4)

    def build_photos(self, content, place):
        """Three equal photos. Add <slug>_2.jpg and <slug>_3.jpg in assets/places for different ones."""
        card = rounded_card(content)
        card.pack(fill='x', padx=PAGE_PAD, pady=18)
        tk.Label(card, text='Photos', font=FONTS['heading'], bg='white').pack(anchor='w')

        row = tk.Frame(card, bg='white')
        row.pack(fill='x', pady=8)
        for column in range(3):
            row.grid_columnconfigure(column, weight=1, uniform='photos')   # equal widths
            image_banner(row, height=220, path=place_image_path(place, column + 1)).grid(
                row=0, column=column, padx=5, sticky='ew')

    def build_similar(self, content, place):
        """One row of other places: similar to this one and to the user's taste."""
        card = rounded_card(content)
        card.pack(fill='x', padx=PAGE_PAD, pady=(0, 25))
        tk.Label(card, text='More Places', font=FONTS['heading'], bg='white').pack(anchor='w')

        others = similar_places(place, self.app.activity, self.app.user_location, limit=12)
        card_grid(card, self.app, others, compact=True, min_w=220,
                  max_rows=1, bg='white').pack(fill='x', pady=8)
