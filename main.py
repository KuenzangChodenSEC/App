"""
main.py - starting point of the LamGo desktop app.

Run with:   python main.py

The app is one window (LamGoApp) that holds every page stacked on top of each other.
`show_page(name)` raises the requested page to the front.
"""
import json
import os
import queue
import threading
import tkinter as tk

from pages.common import COLORS, show_dialog
from pages.auth import AuthPage
from pages.collection import CollectionPage
from pages.create_post import CreatePostPage
from pages.dzongkhag_page import DzongkhagPage
from pages.geo import detect_location_blocking, location_from_dzongkhag, request_browser_geolocation, make_location
from pages.recommender import Activity
from pages.explore import ExplorePage
from pages.filters import FiltersPage
from pages.home import HomePage
from pages.location import LocationPage
from pages.my_posts import MyPostsPage
from pages.notifications import NotificationsPage
from pages.place_details import PlaceDetailsPage
from pages.profile import ProfilePage
from pages.reviews import ReviewsPage
from pages.saved_places import SavedPlacesPage
from pages.social import SocialPage
from pages.social_data import load_social_data, save_social_data, ensure_post_id, load_notifications
from pages.database import initialize_database
from pages.paths import user_data_path

LOGIN_PAGE = 'Login / Sign Up'


class LamGoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('LamGo - Discover Bhutan')
        self.minsize(1100, 700)
        self.configure(bg=COLORS['bg'])
        self.start_maximized()

        # Ensure the SQLite place catalogue exists before pages load their data.
        initialize_database()

        # ----- Data shared by all pages -----
        self.current_user = {}          # name, email, photo of the logged-in user
        self.selected_place = None      # place currently open in Place Details / Reviews
        self.selected_dzongkhag = None  # dzongkhag currently open in the Dzongkhag page
        self.activity = Activity('')    # searches / interests of the logged-in user (feeds the recommender)
        self.user_location = None       # {'lat', 'lon', 'label', 'source', 'dzongkhag', 'in_bhutan'}
        self.location_status = 'idle'   # 'idle', 'detecting', 'ok' or 'failed'
        self.location_listeners = []    # location bars that want to know when the location changes
        self._geo_queue = None
        self.saved_places = []          # names of saved places
        self.posts, self.following = load_social_data()  # persistent user posts, likes and follows
        self.refresh_user_ratings()
        self.notifications = []

        # ----- Page container -----
        # All pages live in the same grid cell; the cell grows with the window.
        self.container = tk.Frame(self, bg=COLORS['bg'])
        self.container.pack(fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # ----- Navigation state -----
        self.frames = {}                # page name -> page widget
        self.history = []               # pages visited before the current one (for the back arrow)
        self.current_page = None
        self._navigating = False        # True while going "back" so history is not recorded

        self.register_pages()
        self.show_page(LOGIN_PAGE, record=False)    # the login page is always shown first

    def refresh_user_ratings(self):
        """Make destination averages/counts reflect LamGo users' submitted ratings."""
        from pages.common import PLACES
        for place in PLACES:
            ratings = [int(post.get('rating') or 0) for post in self.posts
                       if post.get('place') == place.get('name') and int(post.get('rating') or 0) > 0]
            place['rating'] = round(sum(ratings) / len(ratings), 1) if ratings else 0
            place['reviews'] = len(ratings)

    # ------------------------------------------------------------------
    # Window / page setup
    # ------------------------------------------------------------------
    def start_maximized(self):
        """Open the window filling the whole desktop (Windows, Linux and macOS)."""
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{width}x{height}+0+0')      # fallback: full screen size
        try:
            self.state('zoomed')                    # Windows / macOS
        except tk.TclError:
            try:
                self.attributes('-zoomed', True)    # Linux
            except tk.TclError:
                pass

    def register_pages(self):
        """Create every page once and stack them in the container."""
        pages = {
            'Home': HomePage,
            'Explore': ExplorePage,
            'Place Details': PlaceDetailsPage,
            'Dzongkhag': DzongkhagPage,
            'Reviews': ReviewsPage,
            'Create Post': CreatePostPage,
            'Profile': ProfilePage,
            'Follow / Friends': SocialPage,
            LOGIN_PAGE: AuthPage,
            'Notifications': NotificationsPage,
            'Filters': FiltersPage,
            'Location': LocationPage,
            'Saved Places': SavedPlacesPage,
            'My Posts': MyPostsPage,
            # These three use the same class; the name decides which places are listed.
            'Most Visited': CollectionPage,
            'Nature & Hiking': CollectionPage,
            'Cultural Sites': CollectionPage,
        }
        for name, page_class in pages.items():
            if page_class is CollectionPage:
                frame = page_class(self.container, self, collection_name=name)
            else:
                frame = page_class(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky='nsew')

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def show_page(self, page_name, place=None, record=True, search=None):
        """
        Bring a page to the front.

        place   - optionally select a place first (for Place Details / Reviews)
        record  - remember the page we are leaving so the back arrow works
        search  - pre-fill the Explore search box
        """
        if page_name not in self.frames:
            return
        if place:
            self.selected_place = place
        if search is not None and page_name == 'Explore':
            self.frames['Explore'].search_var.set(search)
            self.activity.record_search(search)         # remembered for future recommendations

        leaving = self.current_page
        should_record = (record and leaving and leaving != page_name
                         and not self._navigating and leaving != LOGIN_PAGE)
        if should_record:
            self.history.append(leaving)
        self.current_page = page_name

        frame = self.frames[page_name]
        if hasattr(frame, 'refresh'):
            frame.refresh()                         # rebuild the page with the latest data
        frame.tkraise()

    def go_back(self):
        """Go to the previous page (or Home when there is no history)."""
        if self.history:
            previous = self.history.pop()
            self._navigating = True
            self.show_page(previous, record=False)
            self._navigating = False
        else:
            self.show_page('Home', record=False)

    def open_place(self, place):
        """Open the details page of a place (and learn that the user is interested in it)."""
        self.selected_place = place
        self.activity.record_view(place)
        self.show_page('Place Details')

    def open_dzongkhag(self, dzongkhag):
        """Open the page of one dzongkhag (e.g. Thimphu) with all its places to visit."""
        self.selected_dzongkhag = dzongkhag
        self.show_page('Dzongkhag')

    # ------------------------------------------------------------------
    # Account actions
    # ------------------------------------------------------------------
    def log_in(self, user):
        """Start a session for `user` and go straight to the Home page."""
        self.current_user = user
        self.notifications = load_notifications(user.get('email', '').lower())
        # Assign stable IDs/like lists to older posts loaded from the social store.
        for post in self.posts:
            ensure_post_id(post)
        self.activity = Activity(user.get('email', ''))   # load this user's saved interests / searches
        self.history = []
        self.show_page('Home', record=False)
        self.detect_location()                            # runs in the background; Home updates when done

    def logout(self):
        save_social_data(self.posts, self.following)
        self.current_user = {}
        self.activity = Activity('')
        self.user_location = None
        self.location_status = 'idle'
        self.history = []
        self.show_page(LOGIN_PAGE, record=False)

    def save_current_user(self):
        """Write the current user's name / email / photo back to users.json."""
        path = user_data_path('users.json', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json'))
        try:
            users = {}
            if os.path.exists(path):
                with open(path, encoding='utf-8') as file:
                    users = json.load(file)

            email = self.current_user.get('email', '').lower()
            # Find the existing record (the email may have been edited, so match on the old key).
            old_key = next((key for key, value in users.items()
                            if value.get('email', key).lower() == email), None)
            record = {'name': self.current_user.get('name', ''),
                      'email': email,
                      'photo': self.current_user.get('photo', '')}
            if old_key:
                record['password'] = users[old_key].get('password', '')
                users.pop(old_key)
            users[email] = record

            with open(path, 'w', encoding='utf-8') as file:
                json.dump(users, file, indent=4)
        except Exception:
            pass        # saving the profile is optional; never crash the app because of it

    # ------------------------------------------------------------------
    # Live location
    # ------------------------------------------------------------------
    def detect_location(self):
        """Look up the user's approximate position in a background thread (the window never freezes)."""
        if self.location_status == 'detecting':
            return
        self.location_status = 'detecting'
        self.notify_location_listeners()
        self._geo_queue = queue.Queue()
        result_queue = self._geo_queue
        threading.Thread(target=lambda: result_queue.put(detect_location_blocking()),
                         daemon=True).start()
        self.after(300, self._poll_location)

    def _poll_location(self):
        try:
            location = self._geo_queue.get_nowait()
        except queue.Empty:
            self.after(300, self._poll_location)
            return
        if location:
            self.user_location, self.location_status = location, 'ok'
        else:
            self.location_status = 'failed'      # offline: keep any location the user chose by hand
        self.notify_location_listeners()
        if self.current_page in ('Home', 'Location', 'Explore', 'Dzongkhag'):
            self.frames[self.current_page].refresh()  # update nearby recommendations and the location status

    def detect_precise_location(self):
        """Request actual device/browser location with explicit user permission."""
        def receive(location):
            self.after(0, lambda: self._accept_precise_location(location))
        def failed(message):
            self.after(0, lambda: show_dialog(self, 'Location', f'Could not open location permission: {message}', 'error'))
        if not request_browser_geolocation(receive, failed):
            show_dialog(self, 'Location', 'Could not open your browser for location permission.', 'error')

    def _accept_precise_location(self, location):
        self.user_location = location
        self.location_status = 'ok'
        self.notify_location_listeners()
        if self.current_page in ('Home', 'Location', 'Explore', 'Dzongkhag'):
            self.frames[self.current_page].refresh()
        show_dialog(self, 'Location updated', 'Your device coordinates were received with browser permission.', 'success')

    def set_manual_location(self, dzongkhag_name):
        """The user chose their dzongkhag by hand."""
        self.user_location = location_from_dzongkhag(dzongkhag_name)
        self.location_status = 'ok'
        self.notify_location_listeners()
        if self.current_page in ('Home', 'Explore', 'Dzongkhag'):
            self.frames[self.current_page].refresh()

    def notify_location_listeners(self):
        """Tell every location bar on screen to redraw; forget bars that no longer exist."""
        self.location_listeners = [update for update in self.location_listeners if update()]

    # ------------------------------------------------------------------
    # Saved places
    # ------------------------------------------------------------------
    def toggle_saved(self, place):
        """Save or un-save a place, then refresh the pages that show saved places."""
        name = place['name']
        if name in self.saved_places:
            self.saved_places.remove(name)
            show_dialog(self, 'Saved Places', f'{name} removed.', 'info')
        else:
            self.saved_places.append(name)
            self.activity.record_save(place)
            show_dialog(self, 'Saved Places', f'{name} saved.', 'success')

        for page_name in ['Home', 'Explore', 'Place Details', 'Dzongkhag', 'Profile', 'Saved Places', 'Follow / Friends', 'Reviews', 'My Posts']:
            page = self.frames.get(page_name)
            if page is not None and hasattr(page, 'refresh'):
                page.refresh()


if __name__ == '__main__':
    app = LamGoApp()
    app.mainloop()
