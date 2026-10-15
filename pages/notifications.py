"""Persistent, per-account activity notifications."""
import tkinter as tk
from datetime import datetime

from .common import COLORS, FONTS, PAGE_PAD, clear_frame, header, make_button, rounded_card, scrollable
from .social_data import load_notifications, mark_notifications_read


class NotificationsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Notifications')
        outer, content = scrollable(self)
        outer.pack(fill='both', expand=True)
        box = rounded_card(content)
        box.pack(fill='x', padx=PAGE_PAD, pady=30)
        tk.Label(box, text='Your activity', font=FONTS['title'], bg=COLORS['white'],
                 fg=COLORS['brown_dark']).pack(anchor='w')
        email = self.app.current_user.get('email', '').lower()
        self.app.notifications = load_notifications(email)
        unread = sum(not item.get('read', False) for item in self.app.notifications)
        tk.Label(box, text=f'{unread} unread notification(s)', font=FONTS['small'],
                 bg=COLORS['white'], fg=COLORS['muted']).pack(anchor='w', pady=(2, 12))
        for item in self.app.notifications:
            row_bg = COLORS['cream'] if not item.get('read') else COLORS['white']
            row = tk.Frame(box, bg=row_bg, pady=10, padx=8)
            row.pack(fill='x', pady=3)
            symbol = {'follow': '＋', 'like': '♥', 'comment': '💬'}.get(item.get('kind'), '🔔')
            tk.Label(row, text=symbol, font=FONTS['heading'], bg=row_bg,
                     fg=COLORS['brown']).pack(side='left', padx=(0, 10))
            message = item.get('detail') or 'You have a new LamGo notification.'
            tk.Label(row, text=message, font=FONTS['body'], bg=row_bg, fg=COLORS['text'],
                     wraplength=850, justify='left').pack(side='left', fill='x', expand=True)
            if not item.get('read'):
                tk.Label(row, text='NEW', font=FONTS['small'], bg=row_bg,
                         fg=COLORS['brown']).pack(side='right', padx=8)
        if not self.app.notifications:
            tk.Label(box, text='No notifications yet. When someone follows you, likes your post, or comments, you will see it here.',
                     font=FONTS['body'], bg=COLORS['white'], fg=COLORS['muted'],
                     wraplength=750, justify='left').pack(anchor='w', pady=25)
        make_button(box, 'Mark All as Read', self.mark_read, False).pack(anchor='e', pady=12)

    def mark_read(self):
        mark_notifications_read(self.app.current_user.get('email', '').lower())
        self.refresh()
