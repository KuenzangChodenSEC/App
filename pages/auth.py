"""
auth.py - Login / Sign Up / Reset Password page.

Left side : large Bhutan picture (assets/auth_background.jpg) with a caption.
Right side: login or sign-up form. The caption, heading and form change when the
            user switches tab.
Both a successful login and a successful sign-up go directly to the Home page.
'Forgot password?' opens a reset form where the user chooses a new password.
"""
import hashlib
import json
import os
import re
import tkinter as tk

from .common import AUTH_IMAGE, BASE_DIR, COLORS, FONTS, image_banner, show_dialog
from .paths import user_data_path

USERS_FILE = user_data_path('users.json', os.path.join(BASE_DIR, 'users.json'))
CAPTION_BG = '#65432F'
PASSWORD_RULES = 'Use 8+ characters with uppercase, lowercase, a number and a symbol.'

# Text shown over the picture for each tab
CAPTIONS = {
    'login': ('Discover Bhutan, one place at a time.',
              'Find places, weather, photos, ratings and travel ideas.'),
    'signup': ('Start your Bhutan journey.',
               'Create a free account to save places and share your own travel stories.'),
    'reset': ('Forgot your password?',
              'No problem - choose a new one and get back to exploring Bhutan.'),
}


# ----------------------------------------------------------------------
# Small helper functions (account storage and validation)
# ----------------------------------------------------------------------
def load_users():
    """Read all accounts from users.json (returns {} if the file is missing or broken)."""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, encoding='utf-8') as file:
            return json.load(file)
    except Exception:
        return {}


def save_users(users):
    """Write all accounts to users.json."""
    with open(USERS_FILE, 'w', encoding='utf-8') as file:
        json.dump(users, file, indent=4)


def hash_password(password):
    """Passwords are stored as a SHA-256 hash, never as plain text."""
    return hashlib.sha256(password.encode()).hexdigest()


def valid_email(email):
    return re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', email or '') is not None


def strong_password(password):
    """At least 8 characters with an uppercase, lowercase, digit and symbol."""
    return bool(len(password) >= 8
                and re.search('[A-Z]', password)
                and re.search('[a-z]', password)
                and re.search(r'\d', password)
                and re.search(r'[^A-Za-z0-9]', password))


# ----------------------------------------------------------------------
# The page
# ----------------------------------------------------------------------
class AuthPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.users = load_users()
        self.build_layout()
        self.show_login()

    def refresh(self):
        """Called every time the page is shown (e.g. after logout): start with a clean login form."""
        self.users = load_users()
        self.show_login()

    # ------------------------------------------------------------------
    # Fixed layout (built once)
    # ------------------------------------------------------------------
    def build_layout(self):
        """Two equal-ish halves: picture on the left, form on the right."""
        outer = tk.Frame(self, bg=COLORS['bg'])
        outer.pack(fill='both', expand=True, padx=50, pady=40)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=5)
        outer.grid_columnconfigure(1, weight=4)

        # --- Left: picture + caption strip at the bottom ---
        left = tk.Frame(outer, bg=COLORS['green_dark'])
        left.grid(row=0, column=0, sticky='nsew')
        image_banner(left, path=AUTH_IMAGE, bg=COLORS['green_dark']).place(
            relx=0, rely=0, relwidth=1, relheight=1)

        caption = tk.Frame(left, bg=CAPTION_BG)
        caption.place(relx=0, rely=.70, relwidth=1, relheight=.30)
        tk.Label(caption, text='LamGo', font=('Segoe UI', 30, 'bold'),
                 bg=CAPTION_BG, fg='white').pack(anchor='w', padx=35, pady=(25, 3))
        self.caption_title = tk.Label(caption, font=('Segoe UI', 15, 'bold'), bg=CAPTION_BG, fg='white')
        self.caption_title.pack(anchor='w', padx=35)
        self.caption_text = tk.Label(caption, font=FONTS['body'], bg=CAPTION_BG, fg='#DCEBE4')
        self.caption_text.pack(anchor='w', padx=35, pady=7)

        # --- Right: white panel with the form centred in it ---
        right = tk.Frame(outer, bg='white')
        right.grid(row=0, column=1, sticky='nsew')
        self.form = tk.Frame(right, bg='white', padx=10, pady=10)
        self.form.place(relx=.5, rely=.5, anchor='center', width=480)

        self.title = tk.Label(self.form, font=('Segoe UI', 25, 'bold'), bg='white', fg=COLORS['text'])
        self.title.pack(anchor='w')
        self.subtitle = tk.Label(self.form, font=FONTS['small'], bg='white', fg=COLORS['muted'])
        self.subtitle.pack(anchor='w', pady=(5, 18))

        # LOGIN / SIGN UP tabs
        tabs = tk.Frame(self.form, bg='white')
        tabs.pack(fill='x', pady=(0, 16))
        self.login_tab = tk.Button(tabs, text='LOGIN', command=self.show_login, bd=0,
                                   font=FONTS['button'], padx=25, pady=8, cursor='hand2')
        self.login_tab.pack(side='left')
        self.signup_tab = tk.Button(tabs, text='SIGN UP', command=self.show_signup, bd=0,
                                    font=FONTS['button'], padx=25, pady=8, cursor='hand2')
        self.signup_tab.pack(side='left', padx=5)

        # The fields below the tabs are rebuilt each time the tab changes
        self.body = tk.Frame(self.form, bg='white')
        self.body.pack(fill='both', expand=True)

    # ------------------------------------------------------------------
    # Helpers for building the changing part of the form
    # ------------------------------------------------------------------
    def clear_body(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def style_tabs(self, active):
        """Highlight the active tab ('login' or 'signup'); None highlights neither."""
        on = {'bg': COLORS['green'], 'fg': 'white'}
        off = {'bg': COLORS['green_light'], 'fg': COLORS['green']}
        self.login_tab.config(**(on if active == 'login' else off))
        self.signup_tab.config(**(on if active == 'signup' else off))

    def set_texts(self, mode, title, subtitle):
        """Update the heading and the caption over the picture."""
        self.title.config(text=title)
        self.subtitle.config(text=subtitle)
        self.caption_title.config(text=CAPTIONS[mode][0])
        self.caption_text.config(text=CAPTIONS[mode][1])

    def add_field(self, label_text, show=None, on_enter=None):
        """Add a label + text box to the form and return the text box."""
        tk.Label(self.body, text=label_text, font=FONTS['small'], bg='white',
                 fg=COLORS['text']).pack(anchor='w', pady=(8, 2))
        entry = tk.Entry(self.body, font=FONTS['body'], bg='#FAFCFB', relief='solid', bd=1, show=show)
        entry.pack(fill='x', ipady=7)
        if on_enter:
            entry.bind('<Return>', lambda e: on_enter())    # Enter key submits the form
        return entry

    def add_password_fields(self, on_enter, password_label='Password', confirm_label='Confirm Password'):
        """
        Add a password box and a confirm box and return both.

        - Under the FIRST box: the password rules (turns into a green tick once they are met).
        - Under the CONFIRM box: only 'Passwords match' / 'Passwords do not match'.
        """
        password = self.add_field(password_label, show='•', on_enter=on_enter)
        rules = tk.Label(self.body, text=PASSWORD_RULES, font=('Segoe UI', 8), bg='white',
                         fg=COLORS['muted'], justify='left', anchor='w')
        rules.pack(fill='x', pady=(3, 0))

        confirm = self.add_field(confirm_label, show='•', on_enter=on_enter)
        match = tk.Label(self.body, text='', font=('Segoe UI', 8), bg='white', anchor='w')
        match.pack(fill='x', pady=(3, 0))

        def update_rules(_event=None):
            """Rules text under the first box."""
            if password.get() and strong_password(password.get()):
                rules.config(text='✓ Strong password', fg=COLORS['green'])
            else:
                rules.config(text=PASSWORD_RULES, fg=COLORS['muted'])

        def update_match(_event=None):
            """Match message under the confirm box (empty until the user types in it)."""
            if not confirm.get():
                match.config(text='')
            elif confirm.get() == password.get():
                match.config(text='Passwords match.', fg=COLORS['green'])
            else:
                match.config(text='Passwords do not match.', fg=COLORS['danger'])

        password.bind('<KeyRelease>', lambda e: (update_rules(), update_match()))
        confirm.bind('<KeyRelease>', update_match)
        return password, confirm

    def add_link_button(self, text, command, font=None, **pack_options):
        """A text-only green button (used for 'Show password', 'Create an account', ...)."""
        tk.Button(self.body, text=text, command=command, bg='white', fg=COLORS['green'], bd=0,
                  font=font or FONTS['small'], cursor='hand2').pack(**pack_options)

    def add_main_button(self, text, command, **pack_options):
        """The big green submit button."""
        tk.Button(self.body, text=text, command=command, bg=COLORS['green'], fg='white', bd=0,
                  font=FONTS['button'], cursor='hand2', pady=10).pack(fill='x', **pack_options)

    # ------------------------------------------------------------------
    # LOGIN tab
    # ------------------------------------------------------------------
    def show_login(self):
        self.clear_body()
        self.style_tabs('login')
        self.set_texts('login', 'Welcome Back!', 'Login to continue exploring Bhutan.')

        self.login_email = self.add_field('Email Address', on_enter=self.login_user)
        self.login_password = self.add_field('Password', show='•', on_enter=self.login_user)

        self.add_link_button('Show password', self.toggle_login_password, anchor='e', pady=4)
        self.add_link_button('Forgot password?',
                             lambda: self.show_reset(self.login_email.get().strip()),
                             anchor='e', pady=(0, 12))
        self.add_main_button('LOGIN', self.login_user)

        tk.Label(self.body, text="Don't have an account?", font=FONTS['small'], bg='white',
                 fg=COLORS['muted']).pack(pady=(22, 3))
        self.add_link_button('Create an account', self.show_signup, font=FONTS['button'])
        self.login_email.focus_set()

    def toggle_login_password(self):
        """Show or hide the typed password."""
        hidden = bool(self.login_password.cget('show'))
        self.login_password.config(show='' if hidden else '•')

    def login_user(self):
        """Check the email and password; on success go directly to Home."""
        email = self.login_email.get().strip().lower()
        password = self.login_password.get()

        if not email or not password:
            show_dialog(self, 'Login Error', 'Enter your email and password.', 'error')
            return
        if email not in self.users:
            show_dialog(self, 'Login Failed', 'No account found for this email.', 'error')
            return
        account = self.users[email]
        if account.get('password') != hash_password(password):
            show_dialog(self, 'Login Failed', 'Incorrect password.', 'error')
            return

        self.app.log_in({'name': account.get('name', email), 'email': email,
                         'avatar': '👤', 'photo': account.get('photo', '')})

    # ------------------------------------------------------------------
    # SIGN UP tab
    # ------------------------------------------------------------------
    def show_signup(self):
        self.clear_body()
        self.style_tabs('signup')
        self.set_texts('signup', 'Create Account', 'Create an account to save places and share experiences.')

        self.signup_name = self.add_field('Full Name', on_enter=self.signup_user)
        self.signup_email = self.add_field('Email Address', on_enter=self.signup_user)
        self.signup_password, self.signup_confirm = self.add_password_fields(self.signup_user)

        self.add_main_button('CREATE ACCOUNT', self.signup_user, pady=8)

        tk.Label(self.body, text='Already have an account?', font=FONTS['small'], bg='white',
                 fg=COLORS['muted']).pack(pady=(12, 3))
        self.add_link_button('Login here', self.show_login, font=FONTS['button'])
        self.signup_name.focus_set()

    def signup_user(self):
        """Validate the form, create the account and go directly to Home (already logged in)."""
        name = self.signup_name.get().strip()
        email = self.signup_email.get().strip().lower()
        password = self.signup_password.get()
        confirm = self.signup_confirm.get()

        # --- validation: stop at the first problem ---
        if len(name) < 2:
            show_dialog(self, 'Validation', 'Enter your full name.', 'error')
            return
        if not valid_email(email):
            show_dialog(self, 'Validation', 'Enter a valid email.', 'error')
            return
        if email in self.users:
            show_dialog(self, 'Account Exists', 'This email is already registered.', 'error')
            return
        if not strong_password(password):
            show_dialog(self, 'Password', 'Use 8+ characters with upper, lower, number and symbol.', 'warning')
            return
        if password != confirm:
            show_dialog(self, 'Password', 'Passwords do not match.', 'error')
            return

        # --- create and store the account ---
        self.users[email] = {'name': name, 'email': email,
                             'password': hash_password(password), 'photo': ''}
        save_users(self.users)

        # --- log the new user in and open Home straight away ---
        self.app.log_in({'name': name, 'email': email, 'avatar': '👤', 'photo': ''})

    # ------------------------------------------------------------------
    # RESET PASSWORD (opened from "Forgot password?")
    # ------------------------------------------------------------------
    def show_reset(self, email=''):
        """Form to choose a new password for an existing account."""
        self.clear_body()
        self.style_tabs(None)                         # neither LOGIN nor SIGN UP is highlighted
        self.set_texts('reset', 'Reset Password', 'Enter your account email and choose a new password.')

        self.reset_email = self.add_field('Email Address', on_enter=self.reset_password)
        self.reset_email.insert(0, email)             # reuse what was typed on the login form
        self.reset_new, self.reset_confirm = self.add_password_fields(
            self.reset_password, password_label='New Password', confirm_label='Confirm New Password')

        self.add_main_button('RESET PASSWORD', self.reset_password, pady=8)
        self.add_link_button('Back to login', self.show_login, font=FONTS['button'], pady=(10, 0))
        (self.reset_new if email else self.reset_email).focus_set()

    def reset_password(self):
        """Validate the form, store the new password and return to the login form."""
        email = self.reset_email.get().strip().lower()
        password = self.reset_new.get()
        confirm = self.reset_confirm.get()

        if email not in self.users:
            show_dialog(self, 'Reset Password', 'No account found for this email.', 'error')
            return
        if not strong_password(password):
            show_dialog(self, 'Password', 'Use 8+ characters with upper, lower, number and symbol.', 'warning')
            return
        if password != confirm:
            show_dialog(self, 'Password', 'Passwords do not match.', 'error')
            return

        self.users[email]['password'] = hash_password(password)
        save_users(self.users)
        show_dialog(self, 'Password Updated', 'Your password was changed. Please log in with it.', 'success')

        # Back to the login form with the email already filled in.
        self.show_login()
        self.login_email.insert(0, email)
        self.login_password.focus_set()
