"""
capture_screenshots.py - takes every screenshot needed for the LamGo documentation.

HOW TO USE
    1. Put this file inside the App folder (next to main.py).
    2. Run:   python capture_screenshots.py
    3. Do NOT touch the mouse or keyboard until it prints "Done".
    4. Screenshots are saved in the "screenshots" folder, numbered in the same order
       as the figures in the documentation (01_login.png, 02_signup.png, ...).

NOTES
    * A temporary data folder is used (HOME / XDG_DATA_HOME / LOCALAPPDATA are redirected),
      so your real accounts, posts and saved places are NOT changed.
    * A demo account is created automatically: demo@lamgo.bt / Demo@1234
    * Needs Pillow (already in requirements.txt). On Linux, ImageGrab needs an X11 session.
    * Windows: if screenshots are blurry/offset, right-click Python > Properties >
      Compatibility > "Change high DPI settings" > override scaling by Application.
"""
import os
import sys
import tempfile
import time

# ---- 1. Redirect writable data to a temporary folder BEFORE importing the app ----
TMP = tempfile.mkdtemp(prefix='lamgo_demo_')
os.environ['HOME'] = TMP
os.environ['USERPROFILE'] = TMP
os.environ['XDG_DATA_HOME'] = os.path.join(TMP, 'share')
os.environ['LOCALAPPDATA'] = os.path.join(TMP, 'local')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

from PIL import ImageGrab                      # noqa: E402
import tkinter as tk                           # noqa: E402

import main as lamgo                           # noqa: E402
from pages.common import PLACES                # noqa: E402

OUT = os.path.join(HERE, 'screenshots')
os.makedirs(OUT, exist_ok=True)

DEMO_NAME, DEMO_EMAIL, DEMO_PASS = 'Demo Traveller', 'demo@lamgo.bt', 'Demo@1234'
counter = [0]


def pause(app, seconds=0.7):
    """Let Tk finish drawing / animations."""
    end = time.time() + seconds
    while time.time() < end:
        app.update()
        time.sleep(0.02)


def grab_widget(widget, name):
    widget.update_idletasks()
    x, y = widget.winfo_rootx(), widget.winfo_rooty()
    w, h = widget.winfo_width(), widget.winfo_height()
    counter[0] += 1
    path = os.path.join(OUT, f'{counter[0]:02d}_{name}.png')
    ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(path)
    print('saved', os.path.basename(path))


def shot(app, name, wait=0.8):
    pause(app, wait)
    grab_widget(app, name)


def popup_shot(app, name):
    """Capture the next error/success pop-up, then close it.
    Call this BEFORE the action that opens the (blocking) pop-up."""
    def grab_and_close():
        for child in app.winfo_children():
            if isinstance(child, tk.Toplevel):
                grab_widget(child, name)
                child.destroy()
                return
        app.after(200, grab_and_close)          # pop-up not there yet - try again
    app.after(700, grab_and_close)


def fill(entry, text):
    entry.delete(0, 'end')
    entry.insert(0, text)


def main():
    app = lamgo.LamGoApp()
    pause(app, 1.5)
    auth = app.frames[lamgo.LOGIN_PAGE]

    # ---------------- Login / Sign up / Reset ----------------
    auth.show_login()
    shot(app, 'login')
    auth.show_signup()
    shot(app, 'signup')
    auth.show_reset('')
    shot(app, 'reset_password')

    # ---------------- ERROR HANDLING: login ----------------
    auth.show_login()
    popup_shot(app, 'error_login_empty');            auth.login_user()
    fill(auth.login_email, 'nobody@example.com'); fill(auth.login_password, 'Whatever1!')
    popup_shot(app, 'error_login_no_account');       auth.login_user()

    # ---------------- ERROR HANDLING: sign up ----------------
    auth.show_signup()
    fill(auth.signup_name, 'A')
    popup_shot(app, 'error_signup_name');            auth.signup_user()
    fill(auth.signup_name, DEMO_NAME); fill(auth.signup_email, 'not-an-email')
    popup_shot(app, 'error_signup_email');           auth.signup_user()
    fill(auth.signup_email, DEMO_EMAIL); fill(auth.signup_password, 'weak'); fill(auth.signup_confirm, 'weak')
    popup_shot(app, 'error_signup_weak_password');   auth.signup_user()
    fill(auth.signup_password, DEMO_PASS); fill(auth.signup_confirm, 'Different@1')
    popup_shot(app, 'error_signup_mismatch');        auth.signup_user()

    # ---------------- Create the demo account (also shows the Home page) ----------------
    fill(auth.signup_confirm, DEMO_PASS)
    auth.signup_user()                               # logs in and opens Home
    pause(app, 2.5)
    shot(app, 'home', 1.0)

    # Same e-mail again -> "already registered" and wrong password
    app.logout(); pause(app, 0.5)
    auth.show_signup()
    fill(auth.signup_name, DEMO_NAME); fill(auth.signup_email, DEMO_EMAIL)
    fill(auth.signup_password, DEMO_PASS); fill(auth.signup_confirm, DEMO_PASS)
    popup_shot(app, 'error_signup_exists');          auth.signup_user()
    auth.show_login()
    fill(auth.login_email, DEMO_EMAIL); fill(auth.login_password, 'WrongPass1!')
    popup_shot(app, 'error_login_wrong_password');   auth.login_user()
    fill(auth.login_password, DEMO_PASS)
    auth.login_user()                                # real login
    pause(app, 2.0)

    # ---------------- Main pages ----------------
    place = next((p for p in PLACES if 'Taktsang' in p['name']), PLACES[0])

    app.show_page('Filters');                         shot(app, 'filters')
    app.show_page('Explore', search='');              shot(app, 'explore_all')
    app.show_page('Explore', search='hike');          shot(app, 'explore_search_hike')
    app.show_page('Explore', search='zzzzqq');        shot(app, 'error_search_no_results')
    app.open_dzongkhag('Thimphu');                    shot(app, 'dzongkhag_thimphu')
    app.open_place(place);                            shot(app, 'place_details')
    app.show_page('Reviews', place=place);            shot(app, 'reviews')
    app.show_page('Location');                        shot(app, 'location')

    # Save a place (success pop-up) and show Saved Places
    popup_shot(app, 'success_place_saved');           app.toggle_saved(place)
    app.show_page('Saved Places');                    shot(app, 'saved_places')

    # Create post: validation error, then a real post
    app.show_page('Create Post');                     shot(app, 'create_post')
    popup_shot(app, 'error_post_empty');              app.frames['Create Post'].post()
    cp = app.frames['Create Post']
    try:
        cp.place.set(place['name'])
        cp.experience.insert('1.0', 'Beautiful hike with amazing views of the Paro valley. Start early!')
        cp.set_rating(5)
        popup_shot(app, 'success_post_created');      cp.post()
    except Exception as error:                        # layout differs - skip, not critical
        print('Skipped post creation:', error)
    pause(app, 1.0)
    shot(app, 'my_posts')

    app.show_page('Community');                       shot(app, 'community')
    app.show_page('Notifications');                   shot(app, 'notifications')
    app.show_page('Profile');                         shot(app, 'profile')
    app.show_page('Most Visited');                    shot(app, 'collection_most_visited')
    app.show_page('Nature & Hiking');                 shot(app, 'collection_nature_hiking')
    app.show_page('Cultural Sites');                  shot(app, 'collection_cultural_sites')

    print('\nDone. Screenshots are in:', OUT)
    app.destroy()


if __name__ == '__main__':
    main()
