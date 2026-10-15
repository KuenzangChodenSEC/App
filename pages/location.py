"""Location tools for selected destinations and the user's approximate location."""
import tkinter as tk
import webbrowser
from urllib.parse import quote

from .common import (COLORS, FONTS, PAGE_PAD, PLACES, autowrap, clear_frame, header,
                     make_button, open_map, rounded_card, scrollable)
from .dzongkhag_data import DZONGKHAGS


class LocationPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Location')
        outer, content = scrollable(self); outer.pack(fill='both', expand=True)
        place = self.app.selected_place or PLACES[0]

        live = rounded_card(content); live.pack(fill='x', padx=PAGE_PAD, pady=(24, 14))
        tk.Label(live, text='📍 Your Location', font=FONTS['title'], bg=COLORS['white'],
                 fg=COLORS['brown_dark']).pack(anchor='w')
        location = self.app.user_location
        if self.app.location_status == 'detecting':
            status = 'Checking your approximate location…'
        elif location:
            accuracy = ('Precise device location (browser permission)' if location.get('source') == 'browser' else ('Approximate IP-based location' if location.get('source') == 'auto' else 'Location selected manually'))
            status = f"{location.get('label', 'Location found')} · {accuracy}\\nCoordinates: {location.get('lat'):.5f}, {location.get('lon'):.5f}"
        else:
            status = 'Location has not been detected yet. Connect to the internet and try again, or select your district.'
        label = tk.Label(live, text=status, font=FONTS['body'], bg=COLORS['white'], fg=COLORS['text'], justify='left')
        label.pack(anchor='w', pady=(10, 12)); autowrap(label)
        buttons = tk.Frame(live, bg=COLORS['white']); buttons.pack(anchor='w')
        make_button(buttons, 'Use Precise Device Location', self.app.detect_precise_location, True).pack(side='left', padx=(0, 8))
        make_button(buttons, 'Approximate IP Location', self.app.detect_location, False).pack(side='left', padx=(0, 8))
        make_button(buttons, 'Open My Location in Maps', self.open_current_location, False).pack(side='left')

        chooser = rounded_card(content); chooser.pack(fill='x', padx=PAGE_PAD, pady=14)
        tk.Label(chooser, text='Choose a district manually', font=FONTS['heading'], bg=COLORS['white'],
                 fg=COLORS['brown_dark']).pack(anchor='w')
        tk.Label(chooser, text='Useful if your network does not provide location data.', font=FONTS['small'],
                 bg=COLORS['white'], fg=COLORS['muted']).pack(anchor='w', pady=(3, 8))
        from tkinter import ttk
        selected = tk.StringVar(value=(location or {}).get('dzongkhag') or DZONGKHAGS[0]['name'])
        combo = ttk.Combobox(chooser, textvariable=selected, state='readonly', values=[d['name'] for d in DZONGKHAGS], width=28)
        combo.pack(side='left', padx=(0, 8))
        make_button(chooser, 'Use This District', lambda: self.set_district(selected.get()), True).pack(side='left')

        destination = rounded_card(content); destination.pack(fill='x', padx=PAGE_PAD, pady=(14, 30))
        tk.Label(destination, text='Place Location', font=FONTS['heading'], bg=COLORS['white'],
                 fg=COLORS['brown_dark']).pack(anchor='w')
        details = f"{place['name']}\\n{place['location']}, Bhutan\\nWeather: {place.get('weather', 'Check local forecast')}\\nBest time: {place.get('best', 'Seasonal') }"
        tk.Label(destination, text=details, font=FONTS['body'], bg=COLORS['white'], justify='left').pack(anchor='w', pady=12)
        make_button(destination, 'Open This Place in Google Maps', lambda: open_map(place), True).pack(anchor='w')
        note = tk.Label(destination, text='Precise location uses your default browser and asks permission. Accuracy depends on your device, browser, operating-system settings, GPS/Wi-Fi availability, and whether you allow access. If permission is denied or unavailable, use approximate IP location or choose a district manually. LamGo does not invent a fallback coordinate.', font=FONTS['small'], bg=COLORS['white'], fg=COLORS['muted'], justify='left', anchor='w')
        note.pack(fill='x', pady=(12, 0)); autowrap(note)

    def set_district(self, name):
        self.app.set_manual_location(name)
        self.refresh()

    def open_current_location(self):
        location = self.app.user_location
        if location and location.get('lat') is not None and location.get('lon') is not None:
            url = f"https://www.google.com/maps?q={location['lat']},{location['lon']}"
        else:
            url = 'https://www.google.com/maps/'
        webbrowser.open(url)
