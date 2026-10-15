"""explore.py - smart search: results ranked for this user, plus 'You might also like'."""
import tkinter as tk

from .common import COLORS, FONTS, PAGE_PAD, card_grid, clear_frame, header, make_button, scrollable
from .recommender import matching_dzongkhags, notes_for, parse_query, recommend
from .search_widgets import attach_suggestions, location_bar


class ExplorePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        # Text typed in the search box; other pages can set it before showing Explore.
        self.search_var = tk.StringVar()
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Explore')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)

        # Top row: title on the left; Filters button, search box and Search button on the right
        top = tk.Frame(content, bg=COLORS['bg'])
        top.pack(fill='x', padx=PAGE_PAD, pady=(18, 4))
        tk.Label(top, text='Explore Bhutan', font=FONTS['title'], bg=COLORS['bg']).pack(side='left')
        make_button(top, 'Filters', lambda: self.app.show_page('Filters'), False).pack(side='right')
        entry = tk.Entry(top, textvariable=self.search_var, width=35, font=FONTS['body'])
        entry.pack(side='right', ipady=7, padx=8)
        entry.bind('<Return>', lambda e: self.submit())
        make_button(top, 'Search', self.submit, True).pack(side='right')
        attach_suggestions(entry, content, self.app, self.submit)

        location_bar(content, self.app, bg=COLORS['bg']).pack(fill='x', padx=PAGE_PAD, pady=(0, 8))

        query = self.search_var.get().strip()
        activity, location = self.app.activity, self.app.user_location
        ranked = recommend(query, activity, location)
        has_words = bool(parse_query(query)['tokens'])

        # "Open Thimphu" shortcut when the user typed a dzongkhag (typos allowed)
        for dz in (matching_dzongkhags(query) if query else []):
            row = tk.Frame(content, bg=COLORS['green_light'], padx=14, pady=8)
            row.pack(fill='x', padx=PAGE_PAD, pady=(0, 8))
            tk.Label(row, text=f"📍 {dz['name']} is a dzongkhag - see everything to visit there",
                     font=FONTS['body'], bg=COLORS['green_light'], fg=COLORS['green_dark']).pack(side='left')
            make_button(row, f"Open {dz['name']}", lambda d=dz: self.app.open_dzongkhag(d), True).pack(
                side='right')

        fallback = has_words and not ranked
        if fallback:
            # nothing matched the words -> still help, with the user's best recommendations
            tk.Label(content, text=f'No places match "{query}". Here are places picked for you instead:',
                     font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(
                anchor='w', padx=PAGE_PAD, pady=(6, 0))
            ranked = recommend('', activity, location, limit=12)
        elif query:
            tk.Label(content, text=f'{len(ranked)} places found - ranked by your search, interests, '
                                   'recent searches and location', font=FONTS['small'],
                     bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD)
        else:
            tk.Label(content, text=f'All {len(ranked)} places - best matches for you first',
                     font=FONTS['small'], bg=COLORS['bg'], fg=COLORS['muted']).pack(
                anchor='w', padx=PAGE_PAD)

        card_grid(content, self.app, [r['place'] for r in ranked],
                  notes=notes_for(ranked)).pack(fill='x', padx=PAGE_PAD - 7, pady=10)

        # Extra picks below real search results
        if has_words and not fallback and len(ranked) < len(recommend('', activity, location)):
            shown = {r['place']['name'] for r in ranked}
            more = recommend('', activity, location, limit=6, exclude=shown)
            if more:
                tk.Label(content, text='You might also like', font=FONTS['heading'],
                         bg=COLORS['bg']).pack(anchor='w', padx=PAGE_PAD, pady=(12, 4))
                card_grid(content, self.app, [r['place'] for r in more], max_rows=1,
                          notes=notes_for(more)).pack(fill='x', padx=PAGE_PAD - 7, pady=(0, 25))

    def submit(self):
        """Run the search: remember it (it improves future recommendations) and rebuild the page."""
        self.app.activity.record_search(self.search_var.get())
        self.refresh()
