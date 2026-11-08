"""
common.py - colours, fonts, image helpers and reusable widgets shared by all pages.

Sections
    1. Settings        colours, fonts, folders
    2. Basic helpers   frames, buttons, dialogs
    3. Images          finding / loading / auto-resizing pictures
    4. Layout helpers  scrollable page area, auto-wrapping text
    5. Widgets         top header bar, place card, responsive card grid
"""
import os
import tkinter as tk
from tkinter import ttk
import webbrowser
from urllib.parse import quote

try:
    from PIL import Image, ImageTk, ImageOps
    PIL_AVAILABLE = True
except ImportError:                      # the app still starts without Pillow,
    PIL_AVAILABLE = False                # but pictures will not be resized

from .places_data import slugify  # noqa: F401
from .database import get_places
PLACES = get_places()  # database-backed destination catalogue
from .dzongkhag_data import DZONGKHAGS, dzongkhag_rating, places_in  # noqa: F401

# ---------------------------------------------------------------------------
# 1. SETTINGS
# ---------------------------------------------------------------------------
COLORS = {
    # Ice blue / powder blue / white LamGo theme
    'green': '#BFE9F5', 'green_dark': '#78C6DD', 'green_light': '#EAF8FC',
    'bg': '#F7FCFE', 'white': '#FFFFFF', 'text': '#000000', 'muted': '#5B6B73',
    'border': '#C9E5EF', 'gold': '#4AA9C5', 'danger': '#B42318', 'blue': '#4AA9C5',
    'cream': '#EAF8FC', 'powder_blue': '#D8EEF7', 'ice_blue': '#BFE9F5',
    'brown': '#78C6DD', 'brown_dark': '#277C99', 'success': '#4AA9C5',
}

FONTS = {
    'title': ('Segoe UI', 25, 'bold'),
    'heading': ('Segoe UI', 18, 'bold'),
    'subheading': ('Segoe UI', 12, 'bold'),
    'body': ('Segoe UI', 10),
    'small': ('Segoe UI', 9),
    'button': ('Segoe UI', 10, 'bold'),
}

PAGE_PAD = 40            # left/right margin of every page (pixels)

# Folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
PLACES_DIR = os.path.join(ASSETS_DIR, 'places')                      # one photo per place
DZONGKHAGS_DIR = os.path.join(ASSETS_DIR, 'dzongkhags')                # optional: one photo per dzongkhag
DEFAULT_IMAGE = os.path.join(ASSETS_DIR, 'bhutan_place.jpg')         # used if a place has no photo
AUTH_IMAGE = os.path.join(ASSETS_DIR, 'auth_background.jpg')
LOGO_IMAGE = os.path.join(ASSETS_DIR, 'lamgo_logo.png')         # login / sign-up picture
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

# ---------------------------------------------------------------------------
# 2. BASIC HELPERS
# ---------------------------------------------------------------------------
def clear_frame(frame):
    """Remove every widget inside `frame` (pages call this before rebuilding)."""
    for widget in frame.winfo_children():
        widget.destroy()


def rounded_card(parent, bg=None, padx=16, pady=16):
    """A white box with a thin border, used as a 'card' throughout the app."""
    return tk.Frame(parent, bg=bg or COLORS['white'],
                    highlightbackground=COLORS['border'], highlightthickness=1,
                    bd=0, padx=padx, pady=pady)


def add_tooltip(widget, text):
    """Small hover message explaining what a control does."""
    tip = {'win': None}
    def show(_=None):
        if tip['win'] or not text: return
        win = tk.Toplevel(widget); win.wm_overrideredirect(True); win.attributes('-topmost', True)
        x = widget.winfo_rootx() + 8; y = widget.winfo_rooty() + widget.winfo_height() + 4
        win.geometry(f'+{x}+{y}')
        tk.Label(win, text=text, bg='#111111', fg='white', font=('Segoe UI', 9), padx=8, pady=5).pack()
        tip['win'] = win
    def hide(_=None):
        if tip['win']:
            tip['win'].destroy(); tip['win'] = None
    widget.bind('<Enter>', show, add='+'); widget.bind('<Leave>', hide, add='+')
    return widget

def place_stats(app, place):
    """Return one shared, live average based on every user's rating for this place."""
    ratings=[float(p.get('rating',0) or 0) for p in getattr(app,'posts',[]) if p.get('place')==place.get('name') and float(p.get('rating',0) or 0)>0]
    if ratings: return sum(ratings)/len(ratings), len(ratings)
    return float(place.get('rating',0) or 0), int(place.get('reviews',0) or 0)

def make_button(parent, text, command, primary=True, width=None, tooltip=None):
    """Themed button with lightweight hover and press feedback."""
    options={'text':text,'command':command,'bg':COLORS['ice_blue'] if primary else COLORS['white'],
             'fg':'black' if primary else COLORS['brown_dark'],'activebackground':COLORS['powder_blue'],
             'activeforeground':'black','font':FONTS['button'],'bd':0,'cursor':'hand2','padx':14,'pady':8,'relief':'flat'}
    if width: options['width']=width
    button=tk.Button(parent,**options); normal_bg=options['bg']; normal_fg=options['fg']
    def enter(e): button.config(bg=COLORS['brown_dark'] if primary else COLORS['powder_blue'],fg='white' if primary else 'black')
    def leave(e): button.config(bg=normal_bg,fg=normal_fg,relief='flat')
    button.bind('<Enter>',enter); button.bind('<Leave>',leave)
    button.bind('<ButtonPress-1>',lambda e: button.config(relief='sunken'))
    button.bind('<ButtonRelease-1>',lambda e: button.config(relief='flat'))
    add_tooltip(button,tooltip or text); return button

def show_dialog(parent, title, message, kind='info'):
    """Small pop-up message. kind: 'info', 'success', 'warning' or 'error'."""
    colors = {'info': COLORS['brown'], 'success': COLORS['brown'],
              'warning': COLORS['gold'], 'error': COLORS['danger']}
    colour = colors.get(kind, COLORS['brown'])

    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry('370x165')
    win.resizable(False, False)
    win.configure(bg='white')
    win.transient(parent)
    win.grab_set()                                   # block the main window until closed

    tk.Frame(win, bg=colour, height=7).pack(fill='x')                    # coloured top strip
    box = tk.Frame(win, bg='white', padx=22, pady=16)
    box.pack(fill='both', expand=True)
    tk.Label(box, text=title, font=FONTS['subheading'], bg='white', fg=COLORS['text']).pack(anchor='w')
    tk.Label(box, text=message, font=FONTS['body'], bg='white', fg=COLORS['muted'],
             wraplength=315, justify='left').pack(anchor='w', pady=(7, 12))
    tk.Button(box, text='OK', command=win.destroy, bg=colour, fg='white', bd=0,
              font=FONTS['button'], padx=18, pady=6, cursor='hand2').pack(anchor='e')

    win.protocol('WM_DELETE_WINDOW', win.destroy)
    parent.wait_window(win)


def open_map(place):
    """Open the place in Google Maps in the user's web browser."""
    query = f"{place['name']}, {place['location']}, Bhutan"
    webbrowser.open('https://www.google.com/maps/search/?api=1&query=' + quote(query))

# ---------------------------------------------------------------------------
# 3. IMAGES
# ---------------------------------------------------------------------------
_image_cache = {}        # keeps loaded pictures; Tk forgets images that are not referenced


def _find_image(base_name):
    """Look for assets/places/<base_name>.(jpg|jpeg|png|webp) and return its path or None."""
    for extension in IMAGE_EXTENSIONS:
        path = os.path.join(PLACES_DIR, base_name + extension)
        if os.path.exists(path):
            return path
    return None


def place_image_path(place, number=1):
    """
    Return the picture file for a place.

    number=1 -> assets/places/<slug>.jpg        (main photo)
    number=2 -> assets/places/<slug>_2.jpg      (extra photo, falls back to the main photo)
    If the place has no photo at all, the default Bhutan picture is used.
    """
    slug = slugify(place.get('name', ''))
    base_name = slug if number == 1 else f'{slug}_{number}'
    path = _find_image(base_name) if slug else None
    if path:
        return path
    if number > 1:                                    # no extra photo -> reuse the main one
        return place_image_path(place, 1)
    return DEFAULT_IMAGE


def dzongkhag_image_path(dzongkhag, number=1):
    """
    Picture of a dzongkhag.

    1st choice: assets/dzongkhags/<slug>.jpg  (or <slug>_2.jpg, <slug>_3.jpg) - add your own photos here.
    Otherwise : the photo of the dzongkhag's best-known place (2nd / 3rd photo = next places).
    """
    slug = slugify(dzongkhag['name'])
    base_name = slug if number == 1 else f'{slug}_{number}'
    for extension in IMAGE_EXTENSIONS:
        path = os.path.join(DZONGKHAGS_DIR, base_name + extension)
        if os.path.exists(path):
            return path
    places = sorted(places_in(dzongkhag), key=lambda p: p['reviews'], reverse=True)
    if places:
        return place_image_path(places[(number - 1) % len(places)])
    return DEFAULT_IMAGE


def load_image(path, size=(400, 220)):
    """Load an image, preserve its proportions and crop it neatly to ``size``.

    The returned PhotoImage is cached, while every widget still keeps its own
    reference.  This prevents uploaded profile and post photos from vanishing.
    """
    if not path:
        return None
    path = os.path.abspath(os.path.expanduser(str(path)))
    if not os.path.isfile(path):
        return None
    key = (path, tuple(size), os.path.getmtime(path))
    if key in _image_cache:
        return _image_cache[key]
    try:
        if not PIL_AVAILABLE:
            return None
        with Image.open(path) as source:
            picture = ImageOps.exif_transpose(source).convert('RGBA')
            # ImageOps.fit fills the frame without stretching the photograph.
            picture = ImageOps.fit(picture, tuple(size), method=Image.Resampling.LANCZOS,
                                   centering=(0.5, 0.5))
            result = ImageTk.PhotoImage(picture)
        _image_cache[key] = result
        return result
    except Exception:
        return None


def place_image(parent, place, size=(400, 220), path=None):
    """A Label showing the place's own photo at a fixed size (used inside place cards)."""
    img = load_image(path or place_image_path(place), size)
    if img:
        label = tk.Label(parent, image=img, bg='#E9DCCB', bd=0)
        label.image = img                             # keep a reference so Tk does not drop it
        return label
    return tk.Label(parent, text='Bhutan', font=('Segoe UI', 28, 'bold'),
                    fg=COLORS['brown_dark'], bg='#E9DCCB')


def image_banner(parent, height=None, path=None, bg='#E9DCCB'):
    """
    A frame whose picture is automatically re-scaled to fill the frame.

    Give it a `height` when you pack it, or place() it with relwidth/relheight.
    The picture is refreshed (with a short delay) whenever the window is resized.
    """
    box = tk.Frame(parent, bg=bg)
    if height:
        box.configure(height=height)
    box.pack_propagate(False)                         # frame size is set by us, not by the picture

    label = tk.Label(box, bg=bg, bd=0, text='Bhutan', font=('Segoe UI', 28, 'bold'), fg=COLORS['brown_dark'])
    label.pack(fill='both', expand=True)

    image_path = path or DEFAULT_IMAGE
    state = {'job': None, 'size': None}

    def apply():
        """Scale the picture to the current frame size."""
        state['job'] = None
        if not box.winfo_exists():
            return
        # Round the size up so we do not create a new image for every pixel of resizing.
        width = -(-max(box.winfo_width(), 20) // 20) * 20
        height_px = -(-max(box.winfo_height(), 20) // 10) * 10
        if (width, height_px) == state['size']:
            return
        state['size'] = (width, height_px)
        img = load_image(image_path, (width, height_px))
        if img:
            label.config(image=img, text='')
            label.image = img

    def on_resize(_event):
        if state['job']:
            box.after_cancel(state['job'])
        state['job'] = box.after(80, apply)           # wait until resizing pauses

    box.bind('<Configure>', on_resize)
    return box

# ---------------------------------------------------------------------------
# 4. LAYOUT HELPERS
# ---------------------------------------------------------------------------
def scrollable(parent):
    """
    Create a vertically scrollable area.

    Returns (outer, inner): pack `outer` into the page, put your widgets in `inner`.
    """
    outer = tk.Frame(parent, bg=COLORS['bg'])
    canvas = tk.Canvas(outer, bg=COLORS['bg'], highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
    inner = tk.Frame(canvas, bg=COLORS['bg'])
    window_id = canvas.create_window((0, 0), window=inner, anchor='nw')

    # Keep the scroll range equal to the content height ...
    inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    # ... and make the content as wide as the window.
    canvas.bind('<Configure>', lambda e: canvas.itemconfigure(window_id, width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    def on_mouse_wheel(event):
        """Scroll with the mouse wheel (Windows/macOS use delta, Linux uses buttons 4/5)."""
        if not canvas.winfo_exists():
            return
        if event.num == 4:
            step = -1
        elif event.num == 5:
            step = 1
        else:
            step = int(-event.delta / 120) or (-1 if event.delta > 0 else 1)
        canvas.yview_scroll(step, 'units')

    canvas.bind_all('<MouseWheel>', on_mouse_wheel)
    canvas.bind_all('<Button-4>', on_mouse_wheel)
    canvas.bind_all('<Button-5>', on_mouse_wheel)
    return outer, inner


def autowrap(widget, margin=0):
    """Make a Label wrap its text to its own width. Pack the label with fill='x'."""
    widget.bind('<Configure>', lambda e: widget.config(wraplength=max(120, e.width - margin)))

# ---------------------------------------------------------------------------
# 5. WIDGETS
# ---------------------------------------------------------------------------
NAV_PAGES = ['Home', 'Explore', 'Community', 'Saved Places', 'Reviews', 'Create Post', 'Profile']


def header(parent, app, active='Home'):
    """Ice-blue navigation with clear hover and active states."""
    bar=tk.Frame(parent,bg=COLORS['ice_blue'],height=70); bar.pack(fill='x'); bar.pack_propagate(False)
    logo=load_image(LOGO_IMAGE,(52,52))
    logo_button=tk.Button(bar,image=logo if logo else '',text='' if logo else 'LamGo',command=lambda: app.show_page('Home'),bg=COLORS['ice_blue'],activebackground=COLORS['ice_blue'],bd=0,cursor='hand2')
    if logo: logo_button.image=logo
    logo_button.pack(side='left',padx=(16,8),pady=7); add_tooltip(logo_button,'Go to the Home page')
    brand=tk.Label(bar,text='LamGo',font=('Georgia',19,'bold'),fg='black',bg=COLORS['ice_blue']); brand.pack(side='left',padx=(0,16))
    nav=['Home','Explore','Reviews','Create Post','Community','Saved Places','Profile']
    for name in nav:
        active_now=name==active
        btn=tk.Button(bar,text=name,command=lambda n=name: app.show_page(n),font=('Segoe UI',11,'bold'),bd=0,cursor='hand2',padx=10,pady=7,bg=COLORS['white'] if active_now else COLORS['ice_blue'],fg='black',activebackground=COLORS['white'],activeforeground='black',relief='flat')
        btn.pack(side='left',padx=2,pady=12)
        if not active_now:
            btn.bind('<Enter>',lambda e,b=btn:b.config(bg=COLORS['brown_dark'],fg='white'))
            btn.bind('<Leave>',lambda e,b=btn:b.config(bg=COLORS['ice_blue'],fg='black'))
        add_tooltip(btn,f'Open the {name} page')
    icons=tk.Frame(bar,bg=COLORS['ice_blue']); icons.pack(side='left',padx=(7,0))
    def icon(text,page,tip):
        b=tk.Button(icons,text=text,command=lambda: app.show_page(page),bg=COLORS['ice_blue'],fg='black',activebackground=COLORS['white'],bd=0,font=('Segoe UI Emoji',14),cursor='hand2',padx=5,pady=4)
        b.pack(side='left',padx=2); b.bind('<Enter>',lambda e:b.config(bg=COLORS['white'])); b.bind('<Leave>',lambda e:b.config(bg=COLORS['ice_blue'])); add_tooltip(b,tip); return b
    icon('📍','Location','View your current location')
    icon('🔔','Notifications','See your notifications')
    icon('👤','Profile','Open your profile')

def place_card(parent, app, place, compact=False, width=None, note=''):
    """
    One clickable card: photo, save-heart, name, location, rating and category.
    `width` is set by card_grid so cards stretch to fill the window.
    """
    width = width or (210 if compact else 250)
    image_height = int(width * (0.5 if compact else 0.56))
    body_height = (128 if compact else 140) + (30 if note else 0)   # extra room for the reason line

    card = rounded_card(parent, padx=0, pady=0)
    card.configure(width=width, height=image_height + body_height)
    card.pack_propagate(False)                        # keep the exact size we set
    add_tooltip(card, f"Open {place['name']} and see its photos, posts and reviews")
    card.bind('<Button-1>', lambda e: (setattr(app, 'selected_place', place), app.show_page('Place Details')))

    # Top: the photo with a heart button in the corner
    visual = tk.Frame(card, bg='#E9DCCB', height=image_height)
    visual.pack(fill='x')
    visual.pack_propagate(False)
    place_image(visual, place, (width, image_height)).pack(fill='both', expand=True)
    heart = '♥' if place['name'] in app.saved_places else '♡'
    tk.Button(visual, text=heart, command=lambda: app.toggle_saved(place), bg='white',
              fg=COLORS['brown'], bd=0, font=('Segoe UI', 13),
              cursor='hand2').place(relx=.94, rely=.08, anchor='ne')

    # Bottom: text details
    body = tk.Frame(card, bg='white', padx=10, pady=7)
    body.pack(fill='both', expand=True)
    tk.Label(body, text=place['name'], font=FONTS['subheading'], bg='white', fg=COLORS['text'],
             anchor='w', justify='left', wraplength=width - 24).pack(fill='x')
    tk.Label(body, text=place['location'], font=FONTS['small'], bg='white',
             fg=COLORS['muted'], anchor='w').pack(fill='x')
    average, count = place_stats(app, place)
    tk.Label(body, text=f"★ {average:.1f}  ({count})", font=FONTS['small'],
             bg='white', fg=COLORS['gold'], anchor='w').pack(fill='x', pady=(3, 0))
    tk.Label(body, text=place['type'], font=FONTS['small'], bg='white',
             fg=COLORS['muted'], anchor='w').pack(fill='x')
    if note:                                          # why this place was recommended
        tk.Label(body, text='✦ ' + note, font=FONTS['small'], bg='white', fg=COLORS['brown'],
                 anchor='w', justify='left', wraplength=width - 24).pack(fill='x', pady=(3, 0))

    def bind_click(widget):
        """Clicking anywhere on the card (except the heart) opens the place."""
        widget.bind('<Button-1>', lambda e: app.open_place(place))
        for child in widget.winfo_children():
            if not isinstance(child, tk.Button):
                bind_click(child)

    bind_click(card)
    return card


def dzongkhag_card(parent, app, dzongkhag, compact=False, width=None, note=''):
    """One clickable dzongkhag card: photo, name, tagline, rating and number of places."""
    width = width or 250
    image_height = int(width * 0.56)
    rating, reviews, count = dzongkhag_rating(dzongkhag)

    card = rounded_card(parent, padx=0, pady=0)
    card.configure(width=width, height=image_height + 118)
    card.pack_propagate(False)

    visual = tk.Frame(card, bg='#E9DCCB', height=image_height)
    visual.pack(fill='x')
    visual.pack_propagate(False)
    place_image(visual, None, (width, image_height), path=dzongkhag_image_path(dzongkhag)).pack(
        fill='both', expand=True)

    body = tk.Frame(card, bg='white', padx=10, pady=7)
    body.pack(fill='both', expand=True)
    tk.Label(body, text=dzongkhag['name'], font=FONTS['subheading'], bg='white', fg=COLORS['text'],
             anchor='w').pack(fill='x')
    tk.Label(body, text=dzongkhag['tagline'], font=FONTS['small'], bg='white', fg=COLORS['muted'],
             anchor='w', justify='left', wraplength=width - 24).pack(fill='x')
    stars = f'★ {rating}' if count else 'No ratings yet'
    tk.Label(body, text=f"{stars}   •   {count} place{'s' if count != 1 else ''} to visit",
             font=FONTS['small'], bg='white', fg=COLORS['gold'], anchor='w').pack(fill='x', pady=(3, 0))

    def bind_click(widget):
        widget.bind('<Button-1>', lambda e: app.open_dzongkhag(dzongkhag))
        widget.configure(cursor='hand2')
        for child in widget.winfo_children():
            bind_click(child)

    bind_click(card)
    return card


def card_grid(parent, app, places, compact=False, min_w=250, gap=14, max_rows=None, bg=None,
              factory=None, notes=None):
    """
    A grid of place cards that adapts to the window width.

    The number of columns and the width of each card are recalculated whenever the
    window is resized. `max_rows` limits how many rows are shown (None = all places).
    `factory` builds one card (default place_card; use dzongkhag_card for dzongkhags).
    `notes` is an optional {place name: reason text} shown on the place cards.
    """
    factory = factory or place_card
    notes = notes or {}
    grid = tk.Frame(parent, bg=bg or COLORS['bg'])
    state = {'signature': None, 'job': None}

    def layout():
        """(Re)build the cards for the current width."""
        state['job'] = None
        if not grid.winfo_exists():
            return
        width = grid.winfo_width()
        if width < 100 or not places:
            return

        columns = max(1, min(len(places), width // (min_w + gap)))
        card_width = max(min_w, (width // columns) - gap) // 10 * 10
        shown = places[:columns * max_rows] if max_rows else places

        # Skip the rebuild when nothing relevant changed.
        signature = (columns, card_width, len(shown), tuple(app.saved_places))
        if signature == state['signature']:
            return
        state['signature'] = signature

        for widget in grid.winfo_children():
            widget.destroy()
        for column in range(40):                      # equal weight for used columns only
            grid.grid_columnconfigure(column, weight=1 if column < columns else 0)
        for index, place in enumerate(shown):
            factory(grid, app, place, compact=compact, width=card_width,
                    note=notes.get(place['name'], '')).grid(
                row=index // columns, column=index % columns,
                padx=gap // 2, pady=gap // 2, sticky='n')

    def on_resize(_event):
        if state['job']:
            grid.after_cancel(state['job'])
        state['job'] = grid.after(60, layout)         # wait until resizing pauses

    grid.bind('<Configure>', on_resize)
    return grid
