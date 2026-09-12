#!/usr/bin/env python3
import os,sys,time,subprocess,urllib.request,py_compile,ctypes
from pathlib import Path
URLS=[
"https://raw.githubusercontent.com/dime-scripts/Aquastrap/refs/heads/main/Main.py",
"https://raw.githubusercontent.com/dime-scripts/Aquastrap/main/Main.py"
]
BASE=Path(__file__).resolve().parent
CACHE=BASE/"Main.py"
def emit(tag,msg):
    print(f"[{tag}]: {msg}",flush=True)
def fetch():
    for u in URLS:
        try:
            req=urllib.request.Request(u,headers={"User-Agent":"Aquastrap-Launcher"})
            with urllib.request.urlopen(req,timeout=20) as r:
                code=r.read().decode("utf-8","replace")
            if "mainloop" in code and "App(" in code:
                return code
            emit("WARNING",f"downloaded file looks invalid: {u}")
        except Exception as e:
            emit("WARNING",f"download failed ({u}): {e}")
    return None
def strip_decorations(proc):
    try:
        from ctypes import cdll,c_void_p,c_char_p,c_ulong,c_int,c_uint,c_long,Structure,POINTER,byref
        class ClassHint(Structure):
            _fields_=[("res_name",c_char_p),("res_class",c_char_p)]
        class Attr(Structure):
            _fields_=[("x",c_int),("y",c_int),("width",c_int),("height",c_int),("border_width",c_int),("depth",c_int),
            ("visual",c_void_p),("root",c_ulong),("c_class",c_int),("bit_gravity",c_int),("win_gravity",c_int),
            ("backing_store",c_int),("backing_planes",c_ulong),("backing_pixel",c_ulong),("save_under",c_int),
            ("colormap",c_ulong),("map_installed",c_int),("map_state",c_int)]
        class WinAttr(Structure):
            _fields_=[("background_pixmap",c_ulong),("background_pixel",c_ulong),("border_pixmap",c_ulong),
            ("border_pixel",c_ulong),("bit_gravity",c_int),("win_gravity",c_int),("backing_store",c_int),
            ("backing_planes",c_ulong),("backing_pixel",c_ulong),("save_under",c_int),("event_mask",c_long),
            ("do_not_propagate_mask",c_long),("override_redirect",c_int),("colormap",c_ulong),("cursor",c_ulong)]
        x=cdll.LoadLibrary("libX11.so.6")
        x.XOpenDisplay.restype=c_void_p;x.XOpenDisplay.argtypes=[c_char_p]
        d=x.XOpenDisplay(None)
        if not d:
            emit("WARNING","no X display available, native title bar cannot be removed")
            return
        x.XDefaultRootWindow.restype=c_ulong;x.XDefaultRootWindow.argtypes=[c_void_p]
        x.XQueryTree.argtypes=[c_void_p,c_ulong,POINTER(c_ulong),POINTER(c_ulong),POINTER(POINTER(c_ulong)),POINTER(c_uint)]
        x.XGetClassHint.argtypes=[c_void_p,c_ulong,POINTER(ClassHint)];x.XGetClassHint.restype=c_int
        x.XInternAtom.restype=c_ulong;x.XInternAtom.argtypes=[c_void_p,c_char_p,c_int]
        x.XChangeProperty.argtypes=[c_void_p,c_ulong,c_ulong,c_ulong,c_int,c_int,c_void_p,c_int]
        x.XFree.argtypes=[c_void_p]
        x.XChangeWindowAttributes.argtypes=[c_void_p,c_ulong,c_ulong,POINTER(WinAttr)]
        for fn in ("XUnmapWindow","XMapWindow","XRaiseWindow"):
            getattr(x,fn).argtypes=[c_void_p,c_ulong]
        x.XGetWindowAttributes.argtypes=[c_void_p,c_ulong,POINTER(Attr)]
        motif=x.XInternAtom(d,b"_MOTIF_WM_HINTS",0)
        wtype=x.XInternAtom(d,b"_NET_WM_WINDOW_TYPE",0)
        splash=x.XInternAtom(d,b"_NET_WM_WINDOW_TYPE_SPLASH",0)
        override=x.XInternAtom(d,b"_KDE_NET_WM_WINDOW_TYPE_OVERRIDE",0)
        frameext=x.XInternAtom(d,b"_NET_FRAME_EXTENTS",0)
        root=x.XDefaultRootWindow(d)
        def walk():
            found=[]
            def rec(w,parent,depth):
                if depth>40:return
                par=c_ulong();rr=c_ulong();n=c_uint();kids=POINTER(c_ulong)()
                if x.XQueryTree(d,w,byref(par),byref(rr),byref(kids),byref(n))==0:return
                try:
                    for i in range(n.value):
                        cw=kids[i]
                        hint=ClassHint()
                        if x.XGetClassHint(d,cw,byref(hint)):
                            cls=hint.res_class or b"";nm=hint.res_name or b""
                            if cls==b"Aquastrap" or nm in (b"aquastrap",b"main"):
                                found.append((cw,parent))
                            if hint.res_name:x.XFree(hint.res_name)
                            if hint.res_class:x.XFree(hint.res_class)
                        rec(cw,cw,depth+1)
                finally:
                    x.XFree(kids)
            rec(root,0,0)
            return found
        def apply_hints(w):
            x.XChangeProperty(d,w,motif,motif,32,4,(c_uint*5)(2,0,0,0,0),5)
            types=(c_ulong*2)(splash,override) if override else (c_ulong*1)(splash)
            x.XChangeProperty(d,w,wtype,x.XInternAtom(d,b"ATOM",0),32,2 if override else 1,types,2 if override else 1)
            x.XChangeProperty(d,w,frameext,x.XInternAtom(d,b"CARDINAL",0),32,4,(c_long*4)(0,0,0,0),4)
            x.XFlush(d)
        def force(w):
            wa=WinAttr();wa.override_redirect=1
            x.XChangeWindowAttributes(d,w,512,byref(wa))
            x.XUnmapWindow(d,w);x.XFlush(d);time.sleep(0.15)
            x.XMapWindow(d,w);x.XRaiseWindow(d,w);x.XFlush(d)
        seen={};forced=set();stripped=set();end=time.time()+8.0
        while time.time()<end:
            for w,parent in walk():
                apply_hints(w)
                if parent==root and w not in stripped:
                    stripped.add(w)
                seen.setdefault(w,time.time())
                if parent!=root and w not in forced and time.time()-seen[w]>1.5:
                    force(w);forced.add(w)
                    emit("AQUA","window manager ignored border hints, forcing borderless window")
            time.sleep(0.2)
        if stripped or forced:
            emit("AQUA","native title bar removed")
        else:
            emit("WARNING","aquastrap window not found for title bar removal")
        while forced and proc.poll() is None:
            for w,_ in walk():
                if w in forced:
                    a=Attr()
                    if x.XGetWindowAttributes(d,w,byref(a)) and a.map_state==0:
                        x.XMapWindow(d,w);x.XRaiseWindow(d,w);x.XFlush(d)
            time.sleep(0.4)
        x.XCloseDisplay(d)
    except Exception as e:
        emit("WARNING",f"title bar removal unavailable: {e}")
def main():
    emit("AQUA","launcher starting")
    code=fetch()
    if code is not None:
        tmp=BASE/".Main.py.new";tmp.write_text(code)
        try:
            py_compile.compile(str(tmp),doraise=True)
            os.replace(tmp,CACHE)
            emit("AQUA","latest Main.py downloaded")
        except Exception as e:
            emit("WARNING",f"downloaded Main.py broken, keeping cached copy: {e}")
            try:tmp.unlink()
            except Exception:pass
    elif CACHE.exists():
        emit("WARNING","offline, running cached Main.py")
    else:
        emit("ERROR","download failed and no cached Main.py exists")
        sys.exit(1)
    proc=subprocess.Popen([sys.executable,str(CACHE)]+sys.argv[1:],cwd=str(BASE))
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        __import__("threading").Thread(target=strip_decorations,args=(proc,),daemon=True).start()
    sys.exit(proc.wait())
if __name__=="__main__":
    main()
