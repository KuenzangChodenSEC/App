"""Reusable non-blocking animation helpers for LamGo."""
import tkinter as tk

class AnimationManager:
    def __init__(self, root):
        self.root=root; self.jobs={}; self.busy=False
    def cancel(self, key):
        job=self.jobs.pop(key,None)
        if job:
            try:self.root.after_cancel(job)
            except tk.TclError:pass
    def schedule(self,key,delay,fn):
        self.cancel(key); self.jobs[key]=self.root.after(delay,fn)
    def fade_window(self, widget, duration=160, steps=8, done=None):
        top=widget.winfo_toplevel()
        try: top.attributes('-alpha', 0.92)
        except tk.TclError:
            if done: done()
            return
        step=0
        def tick():
            nonlocal step
            step+=1
            try: top.attributes('-alpha', min(1.0,0.92+0.08*step/steps))
            except tk.TclError:return
            if step<steps:self.schedule('fade',max(1,duration//steps),tick)
            elif done:done()
        tick()
    def stagger_pack(self, widgets, interval=55):
        for i,w in enumerate(widgets):
            self.schedule('stagger_%s'%id(w), i*interval, lambda x=w: x.winfo_exists() and x.lift())
    def pulse_button(self, button):
        try:
            original=button.cget('relief'); button.config(relief='sunken')
            self.schedule('press_%s'%id(button),90,lambda: button.winfo_exists() and button.config(relief=original))
        except tk.TclError:pass

def slide_widget(widget, start_y, end_y, duration=220, steps=10, key=None):
    """Lightweight place-based slide used only for widgets managed with place()."""
    top=widget.winfo_toplevel(); key=key or ('slide_%s'%id(widget)); step=0
    def tick():
        nonlocal step
        step+=1; t=step/steps; eased=1-(1-t)*(1-t)
        y=start_y+(end_y-start_y)*eased
        try: widget.place_configure(rely=y)
        except tk.TclError:return
        if step<steps: top.after(max(1,duration//steps),tick)
    tick()

def toast(parent, message, kind='success', duration=2600):
    colors={'success':'#4AA9C5','error':'#D9534F','info':'#78C6DD'}
    win=tk.Toplevel(parent); win.overrideredirect(True); win.attributes('-topmost',True)
    win.configure(bg=colors.get(kind,colors['info']))
    label=tk.Label(win,text=message,bg=colors.get(kind,colors['info']),fg='white',font=('Times New Roman',10,'bold'),padx=18,pady=10)
    label.pack(); win.update_idletasks()
    x=parent.winfo_rootx()+max(20,parent.winfo_width()-win.winfo_width()-28); y=parent.winfo_rooty()+70
    win.geometry(f'+{x}+{y}')
    win.after(duration,lambda: win.winfo_exists() and win.destroy())
    return win
