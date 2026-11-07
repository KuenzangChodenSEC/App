"""Community page: browse travellers' posts without follower/following features."""
import os
import tkinter as tk

from .common import COLORS, FONTS, PAGE_PAD, autowrap, clear_frame, header, load_image, make_button, rounded_card, scrollable
from .social_data import save_social_data

class SocialPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app = app
        self.refresh()

    def refresh(self):
        clear_frame(self)
        header(self, self.app, 'Community')
        outer, content = scrollable(self); outer.pack(fill='both', expand=True)
        tk.Label(content, text='LamGo Community', font=FONTS['title'], bg=COLORS['bg'], fg=COLORS['brown_dark']).pack(anchor='w', padx=PAGE_PAD, pady=(20,2))
        tk.Label(content, text='Discover travel experiences, reviews and stories shared by LamGo travellers.', font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['muted']).pack(anchor='w', padx=PAGE_PAD, pady=(0,14))
        me=self.app.current_user.get('email','').lower()
        posts=list(reversed(self.app.posts))
        if not posts:
            tk.Label(content,text='No community posts yet. Be the first to share your Bhutan journey!',font=FONTS['body'],bg=COLORS['bg'],fg=COLORS['muted']).pack(anchor='w',padx=PAGE_PAD,pady=20)
        for post in posts: self._post_card(content,post,me)

    def _post_card(self,parent,post,me):
        card=rounded_card(parent); card.pack(fill='x',padx=PAGE_PAD,pady=7)
        title=tk.Frame(card,bg=COLORS['white']); title.pack(fill='x')
        tk.Button(title, text=f"{post.get('owner_name','Traveller')}  ·  {post.get('place','Bhutan')}", command=lambda p=post: self.view_profile(p), font=FONTS['subheading'], bg=COLORS['white'], fg=COLORS['brown_dark'], bd=0, cursor='hand2').pack(side='left',anchor='w')
        rating=int(post.get('rating') or 0)
        tk.Label(title,text=('★'*rating+'☆'*(5-rating)) if rating else 'No rating',font=FONTS['body'],bg=COLORS['white'],fg=COLORS['gold']).pack(side='right')
        body=tk.Label(card,text=post.get('text',''),font=FONTS['body'],bg=COLORS['white'],fg=COLORS['text'],justify='left',anchor='w'); body.pack(fill='x',pady=(8,6)); autowrap(body)
        photo=post.get('photo','')
        img=load_image(photo,(500,260)) if photo and os.path.isfile(photo) else None
        if img:
            pic=tk.Label(card,image=img,bg=COLORS['white'],bd=0); pic.image=img; pic.pack(anchor='w',pady=8)
        elif photo:
            tk.Label(card, text='Photo unavailable', font=FONTS['small'], bg=COLORS['white'], fg=COLORS['muted']).pack(anchor='w')
        likes=post.setdefault('likes',[]); liked=me in likes
        actions=tk.Frame(card,bg=COLORS['white']); actions.pack(fill='x',pady=(6,0))
        make_button(actions,f"{'♥' if liked else '♡'}  {len(likes)} Like"+('d' if len(likes)!=1 else ''),lambda p=post:self.toggle_like(p),primary=liked).pack(side='left',padx=(0,8))
        tk.Label(actions, text='Community posts are for discovering places — following, chat and comments are disabled.', font=FONTS['small'], bg=COLORS['white'], fg=COLORS['muted']).pack(side='left', padx=8)

    def toggle_like(self,post):
        me=self.app.current_user.get('email','').lower(); likes=post.setdefault('likes',[])
        if me in likes: likes.remove(me)
        elif me:
            likes.append(me)
        save_social_data(self.app.posts); self.refresh()

    def view_profile(self, post):
        win=tk.Toplevel(self); win.title('Traveller Profile'); win.geometry('360x240'); win.configure(bg='white')
        tk.Label(win,text='Traveller Profile',font=FONTS['heading'],bg='white',fg=COLORS['brown_dark']).pack(pady=(28,12))
        tk.Label(win,text=post.get('owner_name','LamGo traveller'),font=FONTS['subheading'],bg='white').pack()
        tk.Label(win,text='Public travel profile\nYou can explore this traveller’s shared destination and review, but following and messaging are not available.',font=FONTS['body'],bg='white',fg=COLORS['muted'],justify='center',wraplength=300).pack(pady=14)
        make_button(win,'Close',win.destroy,False).pack(pady=8)
