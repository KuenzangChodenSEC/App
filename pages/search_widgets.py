"""
search_widgets.py - two small widgets used by the Home and Explore pages.

    attach_suggestions(entry, host, app, on_submit)
        Shows a drop-down under a search box while the user types. Suggestions come from
        recommender.suggest(): dzongkhags, places (ranked for this user) and recent searches.

    location_bar(parent, app, bg, fg)
        One line showing where the app thinks the user is, with [Detect] and [Change] buttons.
"""
import tkinter as tk
from tkinter import ttk

from .common import COLORS, FONTS
from .dzongkhag_data import DZONGKHAGS
from .recommender import suggest


# ---------------------------------------------------------------------------
# Suggestions while typing
# ---------------------------------------------------------------------------
def attach_suggestions(entry, host, app, on_submit):
    """
    entry     the tk.Entry to watch
    host      a widget that CONTAINS the entry and is big enough for the list (e.g. the scrolled
              page content); the drop-down is drawn on top of it
    on_submit called when the user picks a recent search (the entry text is replaced first)
    """
    state = {'items': [], 'box': None}

    def hide(_event=None):
        if state['box'] is not None:
            state['box'].destroy()
            state['box'] = None
        state['items'] = []

    def show(items):
        hide()
        if not items or not entry.winfo_exists():
            return
        state['items'] = items
        box = tk.Listbox(host, height=len(items), font=FONTS['body'], activestyle='none',
                         bd=1, relief='solid', highlightthickness=0, bg='white', fg=COLORS['text'],
                         selectbackground=COLORS['green'], selectforeground='white', cursor='hand2')
        for _kind, label, _value in items:
            box.insert('end', '  ' + label)
        x = entry.winfo_rootx() - host.winfo_rootx()
        y = entry.winfo_rooty() - host.winfo_rooty() + entry.winfo_height()
        box.place(x=x, y=y, width=max(entry.winfo_width(), 260))
        box.lift()
        box.bind('<ButtonRelease-1>', lambda e: pick(box.nearest(e.y)))
        box.bind('<Return>', lambda e: pick(box.curselection()[0]) if box.curselection() else None)
        box.bind('<Escape>', lambda e: (hide(), entry.focus_set()))
        state['box'] = box

    def pick(index):
        if index < 0 or index >= len(state['items']):
            return
        kind, label, value = state['items'][index]
        hide()
        if kind == 'place':
            app.open_place(value)
        elif kind == 'dzongkhag':
            app.open_dzongkhag(value)
        else:                                         # a recent search -> run it again
            entry.delete(0, 'end')
            entry.insert(0, value)
            on_submit()

    def refresh_list(_event=None):
        show(suggest(entry.get(), app.activity, app.user_location))

    def on_key(event):
        if event.keysym in ('Return', 'Escape', 'Up', 'Tab', 'Left', 'Right', 'Shift_L', 'Shift_R'):
            return
        if event.keysym == 'Down':
            if state['box'] is not None:
                state['box'].focus_set()
                state['box'].selection_set(0)
                state['box'].activate(0)
            return
        refresh_list()

    def on_focus_out(_event):
        # wait a moment: the click on a suggestion first removes focus from the entry
        entry.after(200, lambda: hide() if entry.winfo_exists()
                    and entry.focus_get() is not state['box'] else None)

    entry.bind('<KeyRelease>', on_key, add='+')
    entry.bind('<FocusIn>', refresh_list, add='+')       # empty box -> show recent searches
    entry.bind('<FocusOut>', on_focus_out, add='+')
    entry.bind('<Escape>', hide, add='+')
    entry.bind('<Return>', hide, add='+')


# ---------------------------------------------------------------------------
# Where is the user?
# ---------------------------------------------------------------------------
def _location_text(app):
    loc, status = app.user_location, app.location_status
    if status == 'detecting':
        return '📍 Finding your location...'
    if loc and not loc['in_bhutan']:
        return f"📍 You seem to be outside Bhutan ({loc['label']}) - distances are not used"
    if loc:
        how = 'chosen by you' if loc['source'] == 'manual' else 'detected automatically'
        return f"📍 Near you: {loc['label']}  ({how})"
    return '📍 Location unknown - tap Change to get places near you'


def location_bar(parent, app, bg='white', fg=None):
    """A one-line location display with Detect / Change buttons. Updates itself when the location changes."""
    fg = fg or COLORS['muted']
    bar = tk.Frame(parent, bg=bg)
    label = tk.Label(bar, text=_location_text(app), font=FONTS['small'], bg=bg, fg=fg, anchor='w')
    label.pack(side='left')

    def link(text, command):
        tk.Button(bar, text=text, command=command, font=FONTS['small'], bg=bg, fg=fg, bd=0,
                  activebackground=bg, activeforeground=fg, cursor='hand2',
                  underline=0).pack(side='left', padx=(10, 0))

    link('Detect', app.detect_location)
    link('Change', lambda: choose_location_dialog(app))

    def update():
        if label.winfo_exists():
            label.config(text=_location_text(app))
            return True
        return False                                   # page was rebuilt -> forget this bar

    app.location_listeners.append(update)
    return bar


def choose_location_dialog(app):
    """Let the user pick their dzongkhag by hand (works offline)."""
    win = tk.Toplevel(app)
    win.title('Where are you?')
    win.geometry('340x170')
    win.resizable(False, False)
    win.configure(bg='white')
    win.transient(app)
    win.grab_set()

    tk.Frame(win, bg=COLORS['green'], height=7).pack(fill='x')
    box = tk.Frame(win, bg='white', padx=22, pady=14)
    box.pack(fill='both', expand=True)
    tk.Label(box, text='Choose your current dzongkhag', font=FONTS['subheading'],
             bg='white', fg=COLORS['text']).pack(anchor='w')
    current = app.user_location['dzongkhag'] if app.user_location and app.user_location.get('dzongkhag') else ''
    combo = ttk.Combobox(box, values=[d['name'] for d in DZONGKHAGS], state='readonly')
    combo.set(current)
    combo.pack(fill='x', pady=12)

    def apply():
        if combo.get():
            app.set_manual_location(combo.get())
        win.destroy()

    row = tk.Frame(box, bg='white')
    row.pack(anchor='e')
    tk.Button(row, text='Cancel', command=win.destroy, bg='white', fg=COLORS['muted'], bd=0,
              font=FONTS['button'], padx=12, cursor='hand2').pack(side='left')
    tk.Button(row, text='OK', command=apply, bg=COLORS['green'], fg='white', bd=0,
              font=FONTS['button'], padx=18, pady=5, cursor='hand2').pack(side='left')
