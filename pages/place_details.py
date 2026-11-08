"""place_details.py - full information about one place: photo, description, stats, photos, similar places."""
import tkinter as tk

from .recommender import similar_places
from .common import (COLORS, FONTS, PAGE_PAD, PLACES, autowrap, card_grid, clear_frame, header,
                     image_banner, make_button, open_map, place_image_path, rounded_card, scrollable, load_image, place_stats)


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
        average, count = place_stats(self.app, place)
        tk.Label(content, text=f"📍 {place['location']}  •  ★ {average:.1f} ({count} ratings)", font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD)
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
        """Gallery with distinct official/user photos, crossfade-style switching and slideshow controls."""
        card=rounded_card(content); card.pack(fill='x',padx=PAGE_PAD,pady=18)
        tk.Label(card,text='Photos from LamGo & this place',font=FONTS['heading'],bg=COLORS['white']).pack(anchor='w')
        paths=[]
        # Only keep files that actually exist: never repeat the same fallback photograph.
        import os
        for n in range(1,13):
            path=place_image_path(place,n)
            if path and os.path.isfile(path) and path not in paths: paths.append(path)
        for post in self.app.posts:
            path=post.get('photo')
            if post.get('place')==place['name'] and path and os.path.isfile(path) and path not in paths: paths.append(path)
        if not paths:
            tk.Label(card,text='No photos are available yet.',bg=COLORS['white'],fg=COLORS['muted']).pack(anchor='w',pady=10); return
        viewer=tk.Frame(card,bg=COLORS['powder_blue'],height=300); viewer.pack(fill='x',pady=10); viewer.pack_propagate(False)
        state={'index':0,'job':None,'photo':None}
        image_label=tk.Label(viewer,bg=COLORS['powder_blue']); image_label.pack(fill='both',expand=True)
        overlay=tk.Label(viewer,text='',bg='#000000',fg='white',font=FONTS['small'],padx=8,pady=4)
        def show(index):
            state['index']=index%len(paths); img=load_image(paths[state['index']],(900,300))
            if img: image_label.config(image=img); image_label.image=img
            overlay.config(text=f"Photo {state['index']+1} of {len(paths)}")
            overlay.place(relx=.02,rely=.04)
        def next_photo(): show(state['index']+1)
        def prev_photo(): show(state['index']-1)
        controls=tk.Frame(card,bg=COLORS['white']); controls.pack(anchor='center',pady=(0,8))
        make_button(controls,'‹ Previous',prev_photo,False).pack(side='left',padx=4)
        make_button(controls,'Next ›',next_photo,True).pack(side='left',padx=4)
        def autoplay():
            if not self.winfo_exists() or not viewer.winfo_exists(): return
            next_photo(); state['job']=viewer.after(5000,autoplay)
        viewer.bind('<Destroy>',lambda e: state.get('job') and viewer.after_cancel(state['job']),add='+')
        show(0); state['job']=viewer.after(5000,autoplay)
        tk.Label(card,text='Photos posted by LamGo users and tagged to this destination appear here automatically.',font=FONTS['small'],bg=COLORS['white'],fg=COLORS['muted']).pack(anchor='w')

    def build_similar(self, content, place):
        """One row of other places: similar to this one and to the user's taste."""
        card = rounded_card(content)
        card.pack(fill='x', padx=PAGE_PAD, pady=(0, 25))
        tk.Label(card, text='More Places', font=FONTS['heading'], bg='white').pack(anchor='w')

        others = similar_places(place, self.app.activity, self.app.user_location, limit=12)
        card_grid(card, self.app, others, compact=True, min_w=220,
                  max_rows=1, bg='white').pack(fill='x', pady=8)
