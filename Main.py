#!/usr/bin/env python3
import os,sys,json,subprocess,venv,math,time,threading,shutil,re,traceback,struct,zlib,urllib.request,py_compile,tempfile
from pathlib import Path
BASE=Path(__file__).resolve().parent
VENV=BASE/".venv"
FLAGDIR=BASE/"savedfastflags"
CONFIG=Path.home()/".var/app/org.vinegarhq.Sober/config/sober/config.json"
DATA=Path.home()/".var/app/org.vinegarhq.Sober/data/sober"
APPID="org.vinegarhq.Sober"
VERSION="v0.9"
VERURL="https://raw.githubusercontent.com/dime-scripts/Aquastrap/refs/heads/main/VERSION"
MAINURL="https://raw.githubusercontent.com/dime-scripts/Aquastrap/refs/heads/main/Main.py"
SETTINGS=BASE/".settings.json"
MAINPY=BASE/"main.py"
STAMP="AQUA_READY"
LOGFILE=BASE/"aquastrap.log"
def _emit(tag,msg):
    line=f"[{tag}]: {msg}"
    print(line,flush=True)
    try:
        with open(LOGFILE,"a",encoding="utf-8") as f:f.write(line+"\n")
    except Exception:pass
def log(msg):_emit("AQUA",msg)
def warn(msg):_emit("WARNING",msg)
def error(msg):_emit("ERROR",msg)
def _excepthook(et,ev,tb):
    error("unhandled exception: "+" ".join(traceback.format_exception(et,ev,tb)).replace("\n"," | "))
sys.excepthook=_excepthook
def _tkok():
    try:
        import tkinter
        return True
    except Exception:
        return False
def _bootstrap():
    if os.environ.get(STAMP):
        return
    log("aquastrap starting")
    script=str(Path(__file__).resolve())
    def sysexec():
        warn("virtual environment unavailable, falling back to system python")
        env=dict(os.environ);env[STAMP]="1"
        os.execve(sys.executable,[sys.executable,script]+sys.argv[1:],env)
    need=[]
    if not _tkok():
        warn("python3-tk not detected, attempting apt installation")
        need.append("python3-tk")
    if need:
        try:
            subprocess.run(["pkexec","apt-get","update"])
            subprocess.run(["pkexec","apt-get","install","-y"]+need,check=True)
            log("installed system packages: "+" ".join(need))
        except Exception as e:
            error(f"system package installation failed: {e}")
            sysexec()
    if not VENV.joinpath("bin","python"):
        log("creating virtual environment at .venv")
        try:
            venv.EnvBuilder(system_site_packages=True,with_pip=False).create(str(VENV))
            log("virtual environment created")
        except Exception as e:
            warn(f"venv creation failed ({e}), attempting apt installation of python3-venv")
            try:
                subprocess.run(["pkexec","apt-get","update"])
                subprocess.run(["pkexec","apt-get","install","-y","python3-venv"],check=True)
                venv.EnvBuilder(system_site_packages=True,with_pip=False).create(str(VENV))
                log("virtual environment created after installing python3-venv")
            except Exception as e2:
                error(f"virtual environment setup failed: {e2}")
                sysexec()
    py=VENV/"bin"/"python"
    if not py.exists():
        sysexec()
    log("entering virtual environment")
    env=dict(os.environ);env[STAMP]="1"
    os.execve(str(py),[str(py),script]+sys.argv[1:],env)
_bootstrap()
import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog
BG="#07151e";PANEL="#0b2030";PANEL2="#0d2433";SIDEBAR="#05121b";INK="#d6f6ff";DIM="#7fa6bb";ACC="#22d3ee";ACC2="#0891b2";OK="#34d399";BAD="#fb7185";LINE="#16384a"
FAM="Sans"
def lerp(a,b,t):
    a=a.lstrip("#");b=b.lstrip("#")
    return "#%02x%02x%02x"%tuple(round(int(a[i:i+2],16)+(int(b[i:i+2],16)-int(a[i:i+2],16))*t) for i in (0,2,4))
def rrect(c,x1,y1,x2,y2,r,**k):
    p=[x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1]
    return c.create_polygon(p,smooth=True,**k)
def _undecorate(win):
    try:
        import struct
        from ctypes import cdll,c_ulong,c_int,c_char_p,c_void_p,create_string_buffer
        x11=cdll.LoadLibrary("libX11.so.6")
        x11.XOpenDisplay.restype=c_void_p;x11.XOpenDisplay.argtypes=[c_char_p]
        disp=x11.XOpenDisplay(None)
        if not disp:return False
        wid=int(win.winfo_id(),16)
        x11.XInternAtom.restype=c_ulong;x11.XInternAtom.argtypes=[c_void_p,c_char_p,c_int]
        x11.XChangeProperty.argtypes=[c_void_p,c_ulong,c_ulong,c_ulong,c_int,c_int,c_void_p,c_int]
        m=x11.XInternAtom(disp,b"_MOTIF_WM_HINTS",0)
        buf=create_string_buffer(struct.pack("5I",2,0,0,0,0))
        x11.XChangeProperty(disp,wid,m,m,32,4,buf,5)
        x11.XFlush(disp);x11.XCloseDisplay(disp)
        return True
    except Exception:
        return False
def logo_pixels(n=64):
    def rr_d(x,y):
        r=n*0.234;qx=abs(x-(n-1)/2)-(n/2-r);qy=abs(y-(n-1)/2)-(n/2-r)
        return math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)
    def drop(x,y):
        cx=n*0.5;apex=n*0.172;join=n*0.531;ccy=n*0.641;R=n*0.266
        if y<apex:return False
        if y<=join:
            half=(y-apex)*(math.sqrt(R*R-(join-ccy)**2)/max(1e-9,join-apex))
            return abs(x-cx)<=half
        dx=x-cx;dy=y-ccy
        return dx*dx+dy*dy<=R*R
    def mix(a,b,t):return tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))
    rows=[]
    for yy in range(n):
        cells=[]
        for xx in range(n):
            t=(xx+yy)/(2*n)
            col=mix((5,17,27),(15,52,72),t)
            d=rr_d(xx+0.5,yy+0.5)
            if d>0.5:col=(4,13,20)
            elif -n*0.05<d<=-0.2:col=(34,211,238)
            elif d<=-0.2:
                cov=0
                for sy in (0.25,0.75):
                    for sx in (0.25,0.75):
                        if drop(xx+sx,yy+sy):cov+=1
                if cov:
                    dc=mix((103,232,249),(8,145,178),min(1,max(0,(yy-n*0.156)/(n*0.75))))
                    gx=(xx-n*0.39)/(n*0.094);gy=(yy-n*0.406)/(n*0.133)
                    if gx*gx+gy*gy<1:dc=(224,251,255)
                    col=mix(col,dc,cov/4)
            cells.append(col)
        rows.append(cells)
    return rows
def logo_photo(px):
    n=len(px)
    rows=["{"+" ".join("#%02x%02x%02x"%c for c in row)+"}" for row in px]
    img=tk.PhotoImage(width=n,height=n)
    img.put(" ".join(rows))
    return img
def make_logo(n=64):
    return logo_photo(logo_pixels(n))
def write_png(path,px):
    h=len(px);w=len(px[0])
    raw=b"".join(b"\x00"+bytes(c for pair in row for c in pair) for row in px)
    def chunk(t,d):
        return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))
    data+=chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")
    Path(path).write_bytes(data)
def install_launcher(px):
    try:
        icdir=Path.home()/".local/share/icons/hicolor/128x128/apps"
        apdir=Path.home()/".local/share/applications"
        icdir.mkdir(parents=True,exist_ok=True);apdir.mkdir(parents=True,exist_ok=True)
        write_png(icdir/"aquastrap.png",px)
        script=str(Path(__file__).resolve())
        desktop=f"[Desktop Entry]\nType=Application\nName=Aquastrap\nComment=Aquastrap\nExec={sys.executable} {script}\nIcon=aquastrap\nTerminal=false\nCategories=Game;Utility;\nStartupWMClass=Aquastrap\n"
        (apdir/"aquastrap.desktop").write_text(desktop)
        os.chmod(apdir/"aquastrap.desktop",0o755)
        for cmd in (("update-desktop-database",str(apdir)),("gtk-update-icon-cache",str(icdir.parent.parent))):
            try:subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            except Exception:pass
        log("desktop launcher installed")
    except Exception as e:
        warn(f"could not install desktop launcher: {e}")
def write_echo(path,text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ);env["AQ_OUT"]=str(path);env["AQ_TXT"]=text
    r=subprocess.run(["bash","-c",'echo -E "$AQ_TXT" > "$AQ_OUT"'],env=env)
    if r.returncode!=0:
        error(f"echo write failed for {path} (exit {r.returncode})")
    elif not path.name.startswith("."):
        log(f"wrote {path}")
    return r.returncode
def fval(s):
    if s.lower()=="true":return True
    if s.lower()=="false":return False
    try:return int(s)
    except Exception:pass
    try:return float(s)
    except Exception:return s
def load_settings():
    d={"auto_update":True,"import_replaces":False}
    try:d.update(json.loads(SETTINGS.read_text()))
    except Exception:pass
    return d
def flag_targets():
    users=DATA/"prefix/drive_c/users"
    out=[DATA/"appData/ClientSettings"]
    out += [v/"ClientSettings" for v in users.glob("*/AppData/Local/Roblox/Versions/*")] if users.exists() else []
    seen=set();res=[]
    for v in out:
        v=v.resolve()
        if v not in seen:
            seen.add(v);res.append(v)
    res=[v for v in res if v.parent.is_dir()]
    if not res and DATA.exists():
        res=list(dict.fromkeys(DATA.rglob("ClientSettings")))
    return res
class AquaButton(tk.Canvas):
    def __init__(self,master,text,command=None,w=150,h=38,fs=11,top="#2ee6f5",bot="#0891b2",htop="#a5f3fc",hbot="#22d3ee",fg="#031820",rad=11,pulse=False):
        super().__init__(master,width=w,height=h,highlightthickness=0,bd=0,bg=master.cget("bg"))
        self.w=w;self.h=h;self.text=text;self.command=command;self.t0=top;self.b0=bot;self.ht0=htop;self.hb0=hbot;self.fg=fg;self.rad=rad;self.fs=fs
        self.ht=0.0;self.tgt=0.0;self.down=False;self.pulse=pulse;self.on=True;self.running=False
        self.bind("<Enter>",lambda e:setattr(self,"tgt",1.0))
        self.bind("<Leave>",lambda e:(setattr(self,"tgt",0.0),setattr(self,"down",False)))
        self.bind("<Button-1>",lambda e:setattr(self,"down",True))
        self.bind("<ButtonRelease-1>",self._click)
        self.after(16,self._tick)
    def _click(self,e):
        if not self.on:return
        self.down=False
        if self.command:
            try:self.command()
            except Exception as ex:
                error(f"button action failed: {ex}")
                self.tgt=0.0
    def set_text(self,t):
        self.text=t
    def set_enabled(self,v):
        self.on=v
    def set_running(self,v):
        self.running=v
        self.text="RUNNING" if v else "LAUNCH"
    def _tick(self):
        try:
            self.ht+=(self.tgt-self.ht)*0.28
            p=(0.5+0.5*math.sin(time.time()*3.2)) if self.pulse and self.on else 0.0
            self._draw(self.ht,p)
            self.after(16,self._tick)
        except tk.TclError:
            pass
    def _draw(self,h,p):
        self.delete("all")
        if not self.on:
            t,b,f="#3a4a56","#22303b","#8295a1"
        else:
            t=lerp(self.t0,self.ht0,min(1,h+p*0.25));b=lerp(self.b0,self.hb0,min(1,h+p*0.25));f=self.fg
            if self.running:
                t=lerp(t,"#7df9ff",p*0.5);b=lerp(b,"#06b6d4",p*0.5)
            if self.down:
                t=lerp(t,"#ffffff",0.25);b=lerp(b,"#ffffff",0.25)
        if self.pulse and self.on:
            g=3+p*7
            rrect(self,-g,-g,self.w+g,self.h+g,self.rad+g,fill=ACC,stipple="gray12",outline="")
            rrect(self,-g*0.45,-g*0.45,self.w+g*0.45,self.h+g*0.45,self.rad+g*0.45,fill=ACC,stipple="gray25",outline="")
        r=min(self.rad,self.h/2-1)
        y=0
        while y<self.h:
            d=min(y+1,self.h-(y+1))
            ins=0.0 if d>=r else r-math.sqrt(max(0.0,r*r-(r-d)*(r-d)))
            col=lerp(t,b,(y+1)/self.h)
            self.create_rectangle(ins,y,self.w-ins,y+2.2,fill=col,outline=col)
            y+=2
        self.create_text(self.w/2,self.h/2,text=self.text,fill=f,font=(FAM,self.fs,"bold"))
class ScrollFrame(tk.Frame):
    def __init__(self,master,bg=PANEL):
        super().__init__(master,bg=bg)
        self.canvas=tk.Canvas(self,bg=bg,highlightthickness=0,bd=0)
        self.vsb=tk.Scrollbar(self,orient="vertical",command=self.canvas.yview,bg="#103044",troughcolor=bg,relief="flat",activebackground=ACC,width=10,highlightthickness=0,bd=0)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.inner=tk.Frame(self.canvas,bg=bg)
        self.iid=self.canvas.create_window((0,0),window=self.inner,anchor="nw")
        self.vsb.pack(side="right",fill="y")
        self.canvas.pack(side="left",fill="both",expand=True)
        self.inner.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",lambda e:self.canvas.itemconfigure(self.iid,width=e.width))
    def wheel(self,w):
        for c in (w,)+tuple(w.winfo_children()):
            c.bind("<Button-4>",lambda e:self.canvas.yview_scroll(-3,"units"))
            c.bind("<Button-5>",lambda e:self.canvas.yview_scroll(3,"units"))
class Sidebar(tk.Canvas):
    def __init__(self,root,app,tabs,logo=None):
        self.W=214;self.H=640
        super().__init__(root,width=self.W,height=self.H,bg=SIDEBAR,highlightthickness=0,bd=0)
        self.app=app;self.tabs=tabs;self.active=0;self.pill_y=104;self.hover=-1
        self.phase=0.0
        self.waves=[]
        spec=[(self.H-180,26,0.9,"#0a2636","gray12"),(self.H-132,20,1.4,"#0d3145","gray25"),(self.H-78,15,2.0,"#11435a","gray50")]
        for base,amp,spd,col,st in spec:
            pts=self._pts(base,amp,spd*0)
            it=self.create_polygon(pts,fill=col,stipple=st,outline="")
            self.waves.append((it,base,amp,spd))
        self.bub=[]
        for _ in range(18):
            x=14+os.urandom(1)[0]%(self.W-28);y=os.urandom(1)[0]%self.H;r=1+(os.urandom(1)[0]%3)*0.7;sp=0.25+(os.urandom(1)[0]%30)/60
            it=self.create_oval(x-r,y-r,x+r,y+r,fill=ACC,stipple="gray25",outline="")
            self.bub.append([it,x,y,r,sp])
        if logo is not None:self.create_image(self.W/2,33,image=logo)
        self.create_text(self.W/2,70,text="A Q U A S T R A P",fill="#a5f3fc",font=(FAM,15,"bold"))
        self.create_line(30,90,self.W-30,90,fill=LINE,width=1)
        self.pill=rrect(self,14,104,self.W-14,150,13,fill=ACC,outline="")
        self.labels=[]
        for i,(name,lab) in enumerate(tabs):
            y=127+i*58
            it=self.create_text(self.W/2,y,text=lab,fill="#04141d",font=(FAM,12,"bold"))
            self.labels.append(it)
        self.create_text(self.W/2,self.H-24,text=VERSION,fill="#3f6578",font=(FAM,9))
        self.bind("<Button-1>",self._click)
        self.bind("<Motion>",self._motion)
        self.bind("<Leave>",lambda e:setattr(self,"hover",-1))
        self.after(33,self._tick)
    def _pts(self,base,amp,ph):
        pts=[]
        for x in range(0,self.W+1,8):
            y=base+math.sin(x*0.018+ph)*amp+math.sin(x*0.045+ph*1.7)*amp*0.35
            pts += [x,y]
        pts += [self.W,self.H,0,self.H]
        return pts
    def _motion(self,e):
        self.hover=self._hit(e.y)
        self.config(cursor="hand2" if self.hover>=0 else "")
    def _click(self,e):
        i=self._hit(e.y)
        if i>=0:self.app.show(self.tabs[i][0])
    def _hit(self,y):
        for i in range(len(self.tabs)):
            cy=127+i*58
            if abs(y-cy)<23:return i
        return -1
    def set_active(self,name):
        for i,(n,l) in enumerate(self.tabs):
            if n==name:self.active=i
    def _tick(self):
        try:
            self.phase+=0.018
            for it,base,amp,spd in self.waves:
                self.coords(it,*self._pts(base,amp,self.phase*spd))
            for b in self.bub:
                it,x,y,r,sp=b
                y-=sp;x+=math.sin(self.phase*2+y)*0.18
                if y< -4:y=self.H+4;x=14+os.urandom(1)[0]%(self.W-28)
                b[1]=x;b[2]=y
                self.coords(it,x-r,y-r,x+r,y+r)
            ty=127+self.active*58-23
            self.pill_y+=(ty-self.pill_y)*0.22
            self.coords(self.pill,14,self.pill_y,self.W-14,self.pill_y+46)
            self.tag_raise(self.pill)
            for i,it in enumerate(self.labels):
                if i==self.active:c="#04141d"
                elif i==self.hover:c=INK
                else:c=DIM
                self.itemconfig(it,fill=c)
                self.tag_raise(it)
            self.after(33,self._tick)
        except tk.TclError:
            pass
class AquaDialog(tk.Toplevel):
    def __init__(self,master,title,multiline=False,ok="OK"):
        super().__init__(master)
        self.result=None;self.configure(bg=PANEL)
        self.title(title);self.resizable(False,False)
        try:self.wm_iconphoto(True,master.logo64)
        except Exception:pass
        self.transient(master)
        tk.Label(self,text=title,bg=PANEL,fg=ACC,font=(FAM,14,"bold")).pack(anchor="w",padx=20,pady=(16,8))
        if multiline:
            box=tk.Frame(self,bg=PANEL);box.pack(fill="both",padx=20)
            self.txt=tk.Text(box,width=60,height=11,bg=PANEL2,fg=INK,insertbackground=ACC,selectbackground="#155e75",relief="flat",bd=8,font=("Monospace",10),wrap="word",highlightthickness=1,highlightbackground=LINE,highlightcolor=ACC)
            sb=tk.Scrollbar(box,orient="vertical",command=self.txt.yview,bg="#103044",troughcolor=PANEL2,relief="flat",width=10,highlightthickness=0,bd=0)
            self.txt.configure(yscrollcommand=sb.set);sb.pack(side="right",fill="y");self.txt.pack(side="left",fill="both",expand=True)
        else:
            self.var=tk.StringVar()
            self.ent=tk.Entry(self,width=64,textvariable=self.var,bg=PANEL2,fg=INK,insertbackground=ACC,relief="flat",highlightthickness=1,highlightbackground=LINE,highlightcolor=ACC,font=(FAM,10),bd=8)
            self.ent.pack(fill="x",padx=20)
        row=tk.Frame(self,bg=PANEL);row.pack(pady=16)
        def accept():
            self.result=self.txt.get("1.0","end-1c") if multiline else self.var.get().strip()
            self.destroy()
        AquaButton(row,ok,accept,w=120,h=36,fs=11).pack(side="left",padx=8)
        AquaButton(row,"CANCEL",self.destroy,w=120,h=36,fs=11,top="#1d4a63",bot="#103044",htop="#2a6a8c",hbot="#164861").pack(side="left",padx=8)
        self.bind("<Return>",lambda e:accept() if not multiline else None)
        self.bind("<Escape>",lambda e:self.destroy())
        self.update_idletasks()
        sw,sh=self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry(f"+{(sw-self.winfo_width())//2}+{(sh-self.winfo_height())//2}")
        self.grab_set()
        (self.txt if multiline else self.ent).focus_set()
        self.wait_window(self)
class App(tk.Tk):
    def __init__(self):
        global FAM
        super().__init__(className="Aquastrap")
        self.wm_title("Aquastrap")
        try:self.wm_iconname("Aquastrap")
        except tk.TclError:pass
        self.configure(bg=BG)
        self.resizable(False,False)
        W,H=1000,640
        sw=self.winfo_screenwidth();sh=self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        px128=logo_pixels(128)
        self.logo64=logo_photo(logo_pixels(64));self.logo32=self.logo64.subsample(2);self.logo16=self.logo64.subsample(4)
        self.wm_iconphoto(True,logo_photo(px128),self.logo64)
        self._borderless=_undecorate(self)
        if not self._borderless:
            warn("window manager rejected borderless hints, using native title bar")
        self.after(300,self._reassert_borderless)
        threading.Thread(target=install_launcher,args=(px128,),daemon=True).start()
        av=set(tkfont.families(self))
        FAM=next((f for f in ("Ubuntu","Cantarell","Segoe UI","Sans") if f in av),"Sans")
        self.proc=None
        self.settings=load_settings()
        self.tabs=[("home","HOME"),("flags","FAST FLAGS"),("configuration","CONFIGURATION"),("settings","SETTINGS")]
        self.sb=Sidebar(self,self,self.tabs,self.logo32);self.sb.place(x=0,y=0)
        self.top=tk.Frame(self,bg=BG,height=46);self.top.place(x=214,y=0,width=786,height=46)
        tk.Label(self.top,image=self.logo16,bg=BG).pack(side="left",padx=(16,0))
        self.tlabel=tk.Label(self.top,text="AQUASTRAP",bg=BG,fg=DIM,font=(FAM,12,"bold"));self.tlabel.pack(side="left",padx=10)
        for w in (self.top,self.tlabel):
            w.bind("<ButtonPress-1>",self._drag_start)
            w.bind("<B1-Motion>",self._drag_move)
        self.content=tk.Frame(self,bg="#081823");self.content.place(x=214,y=46,width=786,height=594)
        self.pages={}
        self._build_home()
        self._build_flags()
        self._build_config()
        self._build_settings()
        for n,p in self.pages.items():
            p.place(in_=self.content,x=0,y=0,relwidth=1,relheight=1)
        self.pages["home"].lift()
        self.current="home"
        self._toast=None
        self._ov=None
        self.bind("<Map>",self._on_map)
        self.bind_all("<Button-1>",self._click_focus,add="+")
        self.attributes("-alpha",0.0)
        self._fade(0)
        self.after(120,self.focus_force)
        threading.Thread(target=self._check,daemon=True).start()
        threading.Thread(target=self._version_worker,daemon=True).start()
        log(f"interface ready ({VERSION})")
    def report_callback_exception(self,exc,val,tb):
        error("tk callback: "+" ".join(traceback.format_exception(exc,val,tb)).replace("\n"," | "))
    def _version_worker(self):
        if self.settings.get("auto_update",True):
            self._check_version(False)
        else:
            log("automatic update check disabled")
    def _reassert_borderless(self):
        if self._borderless:
            self._borderless=_undecorate(self)
    def _on_map(self,e):
        self.after(80,self._reassert_borderless)
    def _click_focus(self,e):
        w=e.widget
        try:
            if w.winfo_class() in ("Entry","Text"):
                w.focus_set()
            else:
                self.focus_set()
        except tk.TclError:
            pass
    def destroy(self):
        log("aquastrap closing")
        super().destroy()
    def _fetch(self,url,timeout=8):
        req=urllib.request.Request(url,headers={"User-Agent":"Aquastrap/"+VERSION})
        with urllib.request.urlopen(req,timeout=timeout) as r:
            return r.read().decode("utf-8","replace")
    def _check_version(self,manual=False):
        remote=None
        for u in (VERURL,"https://raw.githubusercontent.com/dime-scripts/Aquastrap/main/VERSION"):
            try:
                remote=self._fetch(u).strip();break
            except Exception as e:
                last=e
        if remote is None:
            warn(f"version check failed: {last}")
            if manual:self.after(0,lambda:self.toast("UPDATE CHECK FAILED",False))
            return
        if not remote:
            warn("version check returned empty response");return
        if remote==VERSION:
            log(f"up to date ({VERSION})")
            if manual:self.after(0,lambda:self.toast(f"UP TO DATE ({VERSION})"))
        else:
            warn(f"new version available: {remote} (current {VERSION})")
            if self.settings.get("auto_update",True) and not manual:
                self.after(0,lambda:self._do_update(remote))
            else:
                self.after(0,lambda:self._update_dialog(remote))
    def _update_dialog(self,newver):
        if self._ov is not None:return
        ov=tk.Frame(self.content,bg=PANEL,highlightthickness=2,highlightbackground=ACC)
        ov.place(relx=0.5,rely=0.5,anchor="center",width=430,height=212)
        self._ov=ov
        tk.Label(ov,text="UPDATE AVAILABLE",bg=PANEL,fg=ACC,font=(FAM,18,"bold")).pack(pady=(28,6))
        tk.Label(ov,text=f"{VERSION}    >    {newver}",bg=PANEL,fg=INK,font=(FAM,12,"bold")).pack()
        tk.Label(ov,text="Downloads the new script and restarts.",bg=PANEL,fg=DIM,font=(FAM,10)).pack(pady=(4,20))
        row=tk.Frame(ov,bg=PANEL);row.pack()
        AquaButton(row,"UPDATE NOW",lambda:self._do_update(newver),w=150,h=38,fs=11).pack(side="left",padx=8)
        AquaButton(row,"LATER",self._close_update,w=130,h=38,fs=11,top="#1d4a63",bot="#103044",htop="#2a6a8c",hbot="#164861").pack(side="left",padx=8)
    def _close_update(self):
        if self._ov is not None:
            self._ov.destroy();self._ov=None
    def _do_update(self,newver):
        self.toast(f"DOWNLOADING {newver}")
        threading.Thread(target=lambda:self._download_update(newver),daemon=True).start()
    def _download_update(self,newver):
        code=None
        for u in (MAINURL,"https://raw.githubusercontent.com/dime-scripts/Aquastrap/main/Main.py"):
            try:
                code=self._fetch(u,20);break
            except Exception as e:
                last=e
        if code is None:
            error(f"update download failed: {last}")
            self.after(0,lambda:self.toast("UPDATE DOWNLOAD FAILED",False));return
        tmp=BASE/".main.new.py"
        try:
            tmp.write_text(code)
            py_compile.compile(str(tmp),doraise=True,cfile=os.path.join(tempfile.gettempdir(),"aquastrap_update.pyc"))
            MAINPY.parent.mkdir(parents=True,exist_ok=True)
            bak=MAINPY.with_name("main.py.bak")
            if MAINPY.exists():shutil.copy2(MAINPY,bak)
            os.replace(tmp,MAINPY)
            os.chmod(MAINPY,0o755)
            log(f"updated to {newver} at {MAINPY}, restarting")
            env=dict(os.environ);env.pop(STAMP,None)
            def restart():
                self.toast(f"UPDATED TO {newver} - RESTARTING")
                self.after(1000,lambda:os.execve(sys.executable,[sys.executable,str(MAINPY)]+sys.argv[1:],env))
            self.after(0,restart)
        except Exception as e:
            error(f"update install failed: {e}")
            try:tmp.unlink()
            except Exception:pass
            self.after(0,lambda:self.toast("UPDATE INSTALL FAILED",False))
    def _fade(self,i):
        self.attributes("-alpha",min(1.0,i/14.0))
        if i<14:self.after(12,lambda:self._fade(i+1))
    def _drag_start(self,e):
        self._dx=e.x_root;self._dy=e.y_root;self._px=self.winfo_x();self._py=self.winfo_y()
    def _drag_move(self,e):
        self.geometry(f"+{self._px+e.x_root-self._dx}+{self._py+e.y_root-self._dy}")
    def show(self,name):
        if name==self.current:return
        p=self.pages[name]
        p.place(in_=self.content,x=34,y=0,relwidth=1,relheight=1)
        p.lift()
        self.sb.set_active(name)
        self.current=name
        self.focus_set()
        def step(i):
            if i>0:
                p.place_configure(x=round(34*i/8))
                self.after(10,lambda:step(i-1))
            else:
                p.place_configure(x=0)
        step(8)
    def toast(self,msg,ok=True):
        if self._toast:
            try:self._toast.destroy()
            except tk.TclError:pass
        t=tk.Label(self.content,text=msg,bg=PANEL,fg=OK if ok else BAD,font=(FAM,10,"bold"),padx=18,pady=8)
        t.place(relx=0.5,rely=-0.02,anchor="n")
        self._toast=t
        def alive():
            return self._toast is t and bool(t.winfo_exists())
        def down(i):
            if not alive():return
            try:t.place_configure(rely=-0.02+0.07*(i+1)/10)
            except tk.TclError:return
            if i<9:self.after(12,lambda:down(i+1))
            else:self.after(1700,lambda:up(0))
        def up(i):
            if not alive():return
            try:t.place_configure(rely=0.05-0.07*i/10)
            except tk.TclError:return
            if i<10:self.after(10,lambda:up(i+1))
            else:
                if alive():
                    t.destroy()
                    if self._toast is t:self._toast=None
        down(0)
    def _card(self,parent,title):
        c=tk.Frame(parent,bg=PANEL,width=218,height=92,highlightthickness=1,highlightbackground=LINE)
        c.pack_propagate(False)
        dot=tk.Canvas(c,width=18,height=18,bg=PANEL,highlightthickness=0,bd=0)
        it=dot.create_oval(4,4,14,14,fill="#475569",outline="")
        dot.pack(anchor="w",padx=14,pady=(12,2))
        tk.Label(c,text=title,bg=PANEL,fg=DIM,font=(FAM,9,"bold")).pack(anchor="w",padx=14)
        v=tk.Label(c,text="CHECKING",bg=PANEL,fg=INK,font=(FAM,12,"bold"));v.pack(anchor="w",padx=14)
        return {"frame":c,"dot":dot,"it":it,"val":v,"state":None}
    def _build_home(self):
        p=tk.Frame(self.content,bg="#081823");self.pages["home"]=p
        tk.Label(p,text="AQUASTRAP",bg="#081823",fg=ACC,font=(FAM,42,"bold")).pack(pady=(64,0))
        self.home_title=p.winfo_children()[-1]
        tk.Label(p,text="DEPLOYMENT CONTROL",bg="#081823",fg=DIM,font=(FAM,10,"bold")).pack(pady=(2,26))
        cards=tk.Frame(p,bg="#081823");cards.pack(pady=6)
        self.c_flat=self._card(cards,"FLATPAK");self.c_flat["frame"].pack(side="left",padx=8)
        self.c_sober=self._card(cards,"SOBER");self.c_sober["frame"].pack(side="left",padx=8)
        self.c_cfg=self._card(cards,"CONFIGURATION");self.c_cfg["frame"].pack(side="left",padx=8)
        self.launch=AquaButton(p,"LAUNCH",self.launch,w=300,h=62,fs=21,rad=16,pulse=True)
        self.launch.pack(pady=34)
        tk.Label(p,text=str(CONFIG),bg="#081823",fg="#45687a",font=(FAM,9)).pack(side="bottom",pady=14)
        self._home_tick(0)
    def _home_tick(self,i):
        try:
            s=0.5+0.5*math.sin(time.time()*2)
            self.home_title.config(fg=lerp("#67e8f9","#0ea5e9",s))
            for card in (self.c_flat,self.c_sober,self.c_cfg):
                st=card["state"]
                if st is None:col="#475569";r=5
                elif st:col=OK;r=4.5+s*1.6
                else:col=BAD;r=5
                card["dot"].coords(card["it"],9-r,9-r,9+r,9+r)
                card["dot"].itemconfig(card["it"],fill=col)
            self.after(40,lambda:self._home_tick(i+1))
        except tk.TclError:
            pass
    def _set_card(self,c,ok,yes,no):
        c["state"]=ok;c["val"].config(text=yes if ok else no,fg=OK if ok else BAD)
    def _check(self):
        flat=shutil.which("flatpak") is not None
        sober=False
        if flat:
            try:
                sober=subprocess.run(["flatpak","info",APPID],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
            except Exception:
                sober=False
        cfg=CONFIG.exists()
        if flat:log("flatpak ready")
        else:warn("flatpak binary not found on PATH")
        if flat:
            if sober:log(f"{APPID} installed")
            else:warn(f"flatpak present but {APPID} is not installed")
        if cfg:log(f"configuration present: {CONFIG}")
        else:warn(f"configuration missing: {CONFIG}")
        self.after(0,lambda:(self._set_card(self.c_flat,flat,"READY","MISSING"),self._set_card(self.c_sober,sober,"INSTALLED","MISSING"),self._set_card(self.c_cfg,cfg,"FOUND","MISSING")))
    def launch(self):
        if self.proc is not None and self.proc.poll() is None:
            warn("launch ignored, sober is already running")
            return
        if not shutil.which("flatpak"):
            error("cannot launch sober, flatpak binary not found")
            self.toast("FLATPAK NOT FOUND",False);return
        log(f"launching: flatpak run {APPID}")
        try:
            self.proc=subprocess.Popen(["flatpak","run",APPID],cwd=str(Path.home()),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL,start_new_session=True)
        except Exception as e:
            error(f"failed to launch sober: {e}")
            self.toast("LAUNCH FAILED",False);return
        log(f"sober started (pid {self.proc.pid})")
        self.launch.set_running(True)
        self.toast("SOBER LAUNCHED")
        self._poll()
    def _poll(self):
        if self.proc is not None and self.proc.poll() is None:
            self.after(500,self._poll)
        else:
            code=self.proc.returncode if self.proc else -1
            self._launch_done(code)
    def _launch_done(self,code):
        self.launch.set_running(False)
        if code==0:
            log("sober closed cleanly")
        else:
            warn(f"sober exited with non-zero code {code}")
        self.toast("SOBER CLOSED" if code==0 else "SOBER EXITED WITH ERROR",code==0)
    def _entry(self,master,w,text=""):
        v=tk.StringVar(value=text)
        e=tk.Entry(master,width=w,textvariable=v,bg=PANEL2,fg=INK,insertbackground=ACC,relief="flat",highlightthickness=1,highlightbackground=LINE,highlightcolor=ACC,font=(FAM,10),bd=4)
        return e,v
    def _build_flags(self):
        p=tk.Frame(self.content,bg="#081823");self.pages["flags"]=p
        top=tk.Frame(p,bg="#081823");top.pack(fill="x",padx=16,pady=(14,8))
        tk.Label(top,text="FAST FLAGS",bg="#081823",fg=INK,font=(FAM,13,"bold")).pack(side="left")
        r=tk.Frame(top,bg="#081823");r.pack(side="right")
        AquaButton(r,"ADD",self._add_from_input,w=78,h=32,fs=10).pack(side="left",padx=(0,12))
        tk.Label(r,text="FLAG",bg="#081823",fg=DIM,font=(FAM,9,"bold")).pack(side="left",padx=(0,4))
        self.f_key,fkv=self._entry(r,26);self.f_key.pack(side="left",padx=(0,14))
        tk.Label(r,text="VALUE",bg="#081823",fg=DIM,font=(FAM,9,"bold")).pack(side="left",padx=(0,4))
        self.f_val,fvv=self._entry(r,30);self.f_val.pack(side="left")
        io=tk.Frame(p,bg="#081823");io.pack(fill="x",padx=16,pady=(0,6))
        sec="#1d4a63";secb="#103044";sech="#2a6a8c";sechb="#164861"
        AquaButton(io,"IMPORT LINK",self._import_link,w=136,h=30,fs=9,top=sec,bot=secb,htop=sech,hbot=sechb,fg=INK,rad=8).pack(side="left",padx=3)
        AquaButton(io,"IMPORT FILE",self._import_file,w=136,h=30,fs=9,top=sec,bot=secb,htop=sech,hbot=sechb,fg=INK,rad=8).pack(side="left",padx=3)
        AquaButton(io,"IMPORT PASTE",self._import_paste,w=136,h=30,fs=9,top=sec,bot=secb,htop=sech,hbot=sechb,fg=INK,rad=8).pack(side="left",padx=3)
        AquaButton(io,"EXPORT FILE",self._export_file,w=136,h=30,fs=9,rad=8).pack(side="right",padx=3)
        AquaButton(io,"COPY JSON",self._copy_flags,w=136,h=30,fs=9,rad=8).pack(side="right",padx=3)
        body=tk.Frame(p,bg="#081823");body.pack(fill="both",expand=True,padx=16)
        left=tk.Frame(body,bg="#081823");left.pack(side="left",fill="both",expand=True)
        head=tk.Frame(left,bg=PANEL);head.pack(fill="x")
        tk.Label(head,text="  FLAG",bg=PANEL,fg=DIM,font=(FAM,9,"bold"),width=30,anchor="w").pack(side="left",padx=(6,4),pady=6)
        tk.Label(head,text="VALUE",bg=PANEL,fg=DIM,font=(FAM,9,"bold"),anchor="w").pack(side="left",fill="x",expand=True)
        tk.Label(head,text=" ",bg=PANEL,width=3).pack(side="right")
        self.sf=ScrollFrame(left);self.sf.pack(fill="both",expand=True)
        right=tk.Frame(body,bg="#081823",width=248);right.pack(side="right",fill="y",padx=(12,0));right.pack_propagate(False)
        tk.Label(right,text="PROFILES",bg="#081823",fg=INK,font=(FAM,11,"bold")).pack(anchor="w",pady=(0,6))
        lf=tk.Frame(right,bg=PANEL,highlightthickness=1,highlightbackground=LINE);lf.pack(fill="both",expand=True)
        self.plist=tk.Listbox(lf,bg=PANEL,fg=INK,selectbackground="#155e75",selectforeground="#ffffff",relief="flat",bd=0,highlightthickness=0,font=(FAM,10),activestyle="none")
        psb=tk.Scrollbar(lf,orient="vertical",command=self.plist.yview,bg="#103044",troughcolor=PANEL,relief="flat",width=10,highlightthickness=0,bd=0)
        self.plist.configure(yscrollcommand=psb.set);psb.pack(side="right",fill="y");self.plist.pack(side="left",fill="both",expand=True,padx=(8,0),pady=8)
        self.plist.bind("<Double-Button-1>",lambda e:self._load_profile())
        self.p_name,pnv=self._entry(right,22);self.p_name.pack(fill="x",pady=(10,6))
        AquaButton(right,"SAVE PROFILE",self._save_profile,w=248,h=34,fs=10).pack(pady=3)
        AquaButton(right,"LOAD PROFILE",self._load_profile,w=248,h=34,fs=10,top="#1d4a63",bot="#103044",htop="#2a6a8c",hbot="#164861").pack(pady=3)
        AquaButton(right,"DELETE PROFILE",self._delete_profile,w=248,h=34,fs=10,top="#f43f5e",bot="#9f1239",htop="#fb7185",hbot="#e11d48",fg="#ffffff").pack(pady=3)
        bar=tk.Frame(p,bg="#081823");bar.pack(fill="x",padx=16,pady=10)
        self.fcount=tk.Label(bar,text="0 FLAGS",bg="#081823",fg=DIM,font=(FAM,10,"bold"));self.fcount.pack(side="left")
        AquaButton(bar,"APPLY FLAGS",self._apply_flags,w=200,h=40,fs=12).pack(side="right")
        self.rows=[]
        self.f_val.bind("<Return>",lambda e:self._add_from_input())
        self.f_key.bind("<Return>",lambda e:self.f_val.focus_set())
        FLAGDIR.mkdir(parents=True,exist_ok=True)
        self._refresh_profiles()
        sess=FLAGDIR/".session.json"
        if sess.exists():
            try:
                for k,v in json.loads(sess.read_text()).items():self._add_row(k,self._v2s(v))
            except Exception:
                pass
    def _v2s(self,v):
        if isinstance(v,bool):return "true" if v else "false"
        return str(v)
    def _add_from_input(self):
        k=self.f_key.get().strip();v=self.f_val.get().strip()
        if not k:return
        self._add_row(k,v)
        self.f_key.delete(0,"end");self.f_val.delete(0,"end");self.f_key.focus_set()
    def _add_row(self,k="",v="",save=True):
        f=tk.Frame(self.sf.inner,bg=PANEL2 if len(self.rows)%2 else PANEL)
        f.pack(fill="x",pady=1)
        ek,kv=self._entry(f,28,k);ek.pack(side="left",padx=(6,4),pady=3)
        ev,vv=self._entry(f,36,v);ev.pack(side="left",fill="x",expand=True,pady=3)
        x=tk.Label(f,text="\u2715",fg=BAD,bg=f.cget("bg"),font=(FAM,11,"bold"),cursor="hand2",width=3)
        x.pack(side="right",padx=4)
        x.bind("<Button-1>",lambda e,fr=f:self._del_row(fr))
        x.bind("<Enter>",lambda e:x.config(bg="#3a1620"))
        x.bind("<Leave>",lambda e:x.config(bg=f.cget("bg")))
        tup=(kv,vv,f)
        self.rows.append(tup)
        self.sf.wheel(f);self._update_count()
        if save:self._autosave()
    def _del_row(self,f):
        self.rows=[r for r in self.rows if r[2] is not f]
        f.destroy();self._update_count();self._autosave()
    def _gather(self):
        d={}
        for kv,vv,f in self.rows:
            k=kv.get().strip()
            if k:d[k]=fval(vv.get().strip())
        return d
    def _update_count(self):
        self.fcount.config(text=f"{len(self.rows)} FLAGS")
    def _autosave(self):
        try:write_echo(FLAGDIR/".session.json",json.dumps(self._gather(),indent=2))
        except Exception as e:warn(f"flag session autosave failed: {e}")
    def _refresh_profiles(self):
        self.plist.delete(0,"end")
        for f in sorted(FLAGDIR.glob("*.json")):
            if not f.name.startswith("."):self.plist.insert("end",f.stem)
    def _selected(self):
        s=self.plist.curselection()
        return self.plist.get(s[0]) if s else None
    def _save_profile(self):
        name=self.p_name.get().strip() or self._selected()
        if not name:
            self.toast("ENTER A PROFILE NAME",False);return
        name=re.sub(r"[^A-Za-z0-9._-]","_",name)
        rc=write_echo(FLAGDIR/f"{name}.json",json.dumps(self._gather(),indent=2))
        if rc==0:
            log(f"fast flag profile saved: {name}")
            self._refresh_profiles();self.toast(f"PROFILE {name} SAVED")
        else:
            error(f"failed to save profile: {name}")
            self.toast("SAVE FAILED",False)
    def _load_profile(self):
        name=self._selected()
        if not name:
            self.toast("SELECT A PROFILE",False);return
        try:
            data=json.loads((FLAGDIR/f"{name}.json").read_text())
        except Exception as e:
            error(f"cannot read profile {name}: {e}")
            self.toast("PROFILE UNREADABLE",False);return
        log(f"fast flag profile loaded: {name} ({len(data)} flags)")
        for _,_,f in self.rows:f.destroy()
        self.rows=[]
        for k,v in data.items():self._add_row(k,self._v2s(v))
        self._autosave();self.toast(f"PROFILE {name} LOADED")
    def _delete_profile(self):
        name=self._selected()
        if not name:
            self.toast("SELECT A PROFILE",False);return
        try:
            (FLAGDIR/f"{name}.json").unlink()
            log(f"fast flag profile deleted: {name}")
        except Exception as e:
            error(f"failed to delete profile {name}: {e}")
            self.toast("DELETE FAILED",False);return
        self._refresh_profiles();self.toast(f"PROFILE {name} DELETED",False)
    def _apply_flags(self):
        data=self._gather();self._autosave()
        log(f"applying {len(data)} fast flags")
        targets=flag_targets()
        if not targets:
            warn("roblox client not found via sober, flags not applied")
            self.toast("ROBLOX NOT FOUND VIA SOBER",False);return
        n=0;failed=0
        for d in targets:
            if write_echo(d/"ClientAppSettings.json",json.dumps(data,indent=2))==0:
                log(f"fast flags deployed to {d/'ClientAppSettings.json'}")
                n+=1
            else:failed+=1
        if failed:warn(f"{failed} target write(s) failed")
        if n:self.toast(f"APPLIED {len(data)} FLAGS TO {n} TARGET" if n==1 else f"APPLIED {len(data)} FLAGS TO {n} TARGETS")
        else:self.toast("FLAG WRITE FAILED",False)
    def _parse_flag_text(self,text):
        data=json.loads(text)
        if not isinstance(data,dict):
            raise ValueError("expected a JSON object of flag names")
        return data
    def _absorb(self,text,src):
        try:
            data=self._parse_flag_text(text)
        except Exception as e:
            error(f"flag import from {src} failed: {e}")
            self.toast("IMPORT FAILED: INVALID JSON",False);return
        if self.settings.get("import_replaces"):
            for _,_,f in self.rows:f.destroy()
            self.rows=[]
        existing={kv.get().strip():vv for kv,vv,f in self.rows}
        added=updated=0
        for k,v in data.items():
            s=self._v2s(v)
            if k in existing:
                existing[k].set(s);updated+=1
            else:
                self._add_row(str(k),s,save=False);added+=1
        self._autosave();self._update_count()
        log(f"imported {added} new and updated {updated} flags from {src}")
        self.toast(f"IMPORTED {added} NEW / {updated} UPDATED")
    def _import_link(self):
        d=AquaDialog(self,"IMPORT FROM LINK")
        url=(d.result or "").strip()
        if not url:return
        if not url.startswith(("http://","https://","raw")):url="https://"+url
        self.toast("DOWNLOADING FLAGS")
        def work():
            try:text=self._fetch(url,15)
            except Exception as e:
                error(f"flag link download failed: {e}")
                self.after(0,lambda:self.toast("LINK DOWNLOAD FAILED",False));return
            self.after(0,lambda:self._absorb(text,"link"))
        threading.Thread(target=work,daemon=True).start()
    def _import_file(self):
        fn=filedialog.askopenfilename(parent=self,title="Import fast flags",filetypes=[("JSON files","*.json"),("All files","*.*")])
        if not fn:return
        try:self._absorb(Path(fn).read_text(encoding="utf-8",errors="replace"),"file")
        except Exception as e:
            error(f"flag file import failed: {e}");self.toast("IMPORT FAILED",False)
    def _import_paste(self):
        d=AquaDialog(self,"PASTE FAST FLAG JSON",multiline=True)
        if d.result and d.result.strip():
            self._absorb(d.result,"clipboard")
    def _export_file(self):
        fn=filedialog.asksaveasfilename(parent=self,title="Export fast flags",defaultextension=".json",initialfile="ClientAppSettings.json",filetypes=[("JSON files","*.json"),("All files","*.*")])
        if not fn:return
        if write_echo(Path(fn),json.dumps(self._gather(),indent=2))==0:
            self.toast("FLAGS EXPORTED")
        else:self.toast("EXPORT FAILED",False)
    def _copy_flags(self):
        self.clipboard_clear()
        self.clipboard_append(json.dumps(self._gather(),indent=2))
        self.update()
        log("fast flags copied to clipboard")
        self.toast("FLAGS COPIED TO CLIPBOARD")
    def _clear_flags(self):
        for _,_,f in self.rows:f.destroy()
        self.rows=[];self._autosave();self._update_count()
        self.toast("ALL FLAGS CLEARED",False)
    def _open_path(self,p):
        try:
            subprocess.Popen(["xdg-open",str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL,start_new_session=True)
        except Exception as e:
            error(f"could not open {p}: {e}");self.toast("OPEN FAILED",False)
    def _build_settings(self):
        p=tk.Frame(self.content,bg="#081823");self.pages["settings"]=p
        wrap=tk.Frame(p,bg="#081823");wrap.pack(fill="both",expand=True,padx=26,pady=22)
        tk.Label(wrap,text="SETTINGS",bg="#081823",fg=INK,font=(FAM,16,"bold")).pack(anchor="w")
        grid=tk.Frame(wrap,bg="#081823");grid.pack(fill="both",expand=True,pady=12)
        left=tk.Frame(grid,bg="#081823");left.pack(side="left",fill="both",expand=True,padx=(0,8))
        right=tk.Frame(grid,bg="#081823");right.pack(side="left",fill="both",expand=True,padx=(8,0))
        def card(parent,title):
            c=tk.Frame(parent,bg=PANEL,highlightthickness=1,highlightbackground=LINE)
            c.pack(fill="x",pady=6)
            tk.Label(c,text=title,bg=PANEL,fg=ACC,font=(FAM,11,"bold"),anchor="w").pack(fill="x",padx=16,pady=(12,6))
            b=tk.Frame(c,bg=PANEL);b.pack(fill="x",padx=16,pady=(0,14))
            return b
        def toggle(parent,text,key):
            var=tk.IntVar(value=1 if self.settings.get(key) else 0)
            cb=tk.Checkbutton(parent,text=text,variable=var,bg=PANEL,fg=INK,activebackground=PANEL,activeforeground=ACC,selectcolor=PANEL2,font=(FAM,10),anchor="w",relief="flat",bd=0,highlightthickness=0,command=lambda:self._set_setting(key,var.get()))
            cb.pack(fill="x",pady=4)
        c1=card(left,"UPDATES")
        toggle(c1,"Check for and install updates on startup","auto_update")
        AquaButton(c1,"CHECK FOR UPDATES NOW",lambda:threading.Thread(target=lambda:self._check_version(True),daemon=True).start(),w=240,h=34,fs=10).pack(anchor="w",pady=(10,2))
        tk.Label(c1,text=f"Installed version: {VERSION}",bg=PANEL,fg=DIM,font=(FAM,9),anchor="w").pack(fill="x",pady=(8,0))
        c2=card(left,"FAST FLAGS")
        toggle(c2,"Import replaces all current flags instead of merging","import_replaces")
        AquaButton(c2,"CLEAR ALL FLAGS",self._clear_flags,w=200,h=34,fs=10,top="#f43f5e",bot="#9f1239",htop="#fb7185",hbot="#e11d48",fg="#ffffff").pack(anchor="w",pady=(10,0))
        c3=card(right,"STORAGE")
        def pathrow(label,path,btn,cmd):
            r=tk.Frame(c3,bg=PANEL);r.pack(fill="x",pady=3)
            tk.Label(r,text=label,bg=PANEL,fg=DIM,font=(FAM,9),anchor="w",width=13).pack(side="left")
            tk.Label(r,text=str(path),bg=PANEL,fg=INK,font=("Monospace",8),anchor="w").pack(side="left",fill="x",expand=True)
            AquaButton(r,btn,cmd,w=70,h=26,fs=8,top="#1d4a63",bot="#103044",htop="#2a6a8c",hbot="#164861",fg=INK,rad=7).pack(side="right")
        pathrow("Flags",FLAGDIR,"OPEN",lambda:self._open_path(FLAGDIR))
        pathrow("Config",CONFIG.parent,"OPEN",lambda:self._open_path(CONFIG.parent))
        pathrow("Log",LOGFILE.parent,"OPEN",lambda:self._open_path(LOGFILE.parent))
        c4=card(right,"RUNTIME")
        AquaButton(c4,"LAUNCH SOBER NOW",self.launch,w=220,h=36,fs=11).pack(anchor="w",pady=2)
        tk.Label(c4,text="flatpak run "+APPID,bg=PANEL,fg=DIM,font=("Monospace",9),anchor="w").pack(fill="x",pady=(8,0))
        tk.Label(wrap,text="Aquastrap "+VERSION,bg="#081823",fg="#3f6578",font=(FAM,9)).pack(side="bottom",anchor="w")
    def _set_setting(self,key,val):
        self.settings[key]=bool(val)
        write_echo(SETTINGS,json.dumps(self.settings,indent=2))
        log(f"setting {key} = {bool(val)}")
    def _build_config(self):
        p=tk.Frame(self.content,bg="#081823");self.pages["configuration"]=p
        bar=tk.Frame(p,bg="#081823");bar.pack(fill="x",padx=16,pady=(14,8))
        tk.Label(bar,text=str(CONFIG),bg="#081823",fg=DIM,font=(FAM,9)).pack(side="left")
        AquaButton(bar,"APPLY",self._apply_config,w=110,h=34,fs=11).pack(side="right",padx=(8,0))
        AquaButton(bar,"VALIDATE",self._validate_config,w=110,h=34,fs=11,top="#1d4a63",bot="#103044",htop="#2a6a8c",hbot="#164861").pack(side="right",padx=(8,0))
        AquaButton(bar,"LOAD",self._load_config,w=110,h=34,fs=11,top="#1d4a63",bot="#103044",htop="#2a6a8c",hbot="#164861").pack(side="right")
        ef=tk.Frame(p,bg=PANEL,highlightthickness=1,highlightbackground=LINE);ef.pack(fill="both",expand=True,padx=16)
        self.txt=tk.Text(ef,bg="#0a1a25",fg="#cfeaf5",insertbackground=ACC,selectbackground="#155e75",relief="flat",bd=8,font=("Monospace",11),wrap="none",highlightthickness=0)
        ysb=tk.Scrollbar(ef,orient="vertical",command=self.txt.yview,bg="#103044",troughcolor="#0a1a25",relief="flat",width=12,highlightthickness=0,bd=0)
        xsb=tk.Scrollbar(p,orient="horizontal",command=self.txt.xview,bg="#103044",troughcolor="#0a1a25",relief="flat",width=10,highlightthickness=0,bd=0)
        self.txt.configure(yscrollcommand=ysb.set,xscrollcommand=xsb.set)
        ysb.pack(side="right",fill="y");self.txt.pack(side="top",fill="both",expand=True)
        xsb.pack(fill="x",padx=16)
        self.txt.bind("<Button-4>",lambda e:self.txt.yview_scroll(-3,"units"))
        self.txt.bind("<Button-5>",lambda e:self.txt.yview_scroll(3,"units"))
        self.cstatus=tk.Label(p,text="",bg="#081823",fg=DIM,font=(FAM,10,"bold"),anchor="w");self.cstatus.pack(fill="x",padx=18,pady=6)
        self._load_config(silent=True)
    def _load_config(self,silent=False):
        if CONFIG.exists():
            text=CONFIG.read_text()
            self.cstatus.config(text="LOADED config.json",fg=DIM)
            log(f"configuration loaded from {CONFIG}")
        else:
            text="{\n}\n"
            self.cstatus.config(text="config.json NOT FOUND - TEMPLATE LOADED",fg=DIM)
            warn(f"configuration not found at {CONFIG}, template loaded")
        self.txt.delete("1.0","end");self.txt.insert("1.0",text)
        if not silent:self.toast("CONFIGURATION LOADED")
    def _validate_config(self):
        try:
            json.loads(self.txt.get("1.0","end-1c"));self.cstatus.config(text="VALID JSON",fg=OK)
            log("configuration json validated")
            return True
        except Exception as e:
            self.cstatus.config(text=f"INVALID JSON: {e}",fg=BAD)
            warn(f"invalid configuration json: {e}")
            return False
    def _apply_config(self):
        if not self._validate_config():
            self.toast("INVALID JSON",False);return
        if write_echo(CONFIG,self.txt.get("1.0","end-1c")+"\n")!=0:
            error("configuration write failed")
            self.toast("WRITE FAILED",False);return
        log(f"configuration written to {CONFIG}")
        self.toast("CONFIGURATION WRITTEN")
if __name__=="__main__":
    App().mainloop()
