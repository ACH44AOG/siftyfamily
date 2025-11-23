from flet import *
import psutil 
import pygetwindow as gw
import time 
import os 
import webbrowser 
import threading


ASSETS_DIR = 'assets'
BANNED_TXT = os.path.join(ASSETS_DIR, 'banned.txt')
INDEX_HTML = os.path.join(ASSETS_DIR, 'index.html')

def ensure_assets():
    os.makedirs(ASSETS_DIR,exist_ok=True)

    if not os.path.exists(BANNED_TXT):
        with open(BANNED_TXT,'w', encoding="utf-8") as f:
            f.write('adult\nbadsite\n')
    if not os.path.exists(INDEX_HTML):
        with open(INDEX_HTML,'w',encoding="utf-8") as f :
            f.write("""
<!doctype html>
<html lang="ar">
<head>
<meta charset="utf-8">
<title>محظور</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body { 
    background:#0b1220; 
    color:#fff; 
    font-family:Segoe UI, 
    Tahoma, sans-serif; 
    display:flex; 
    align-items:center; 
    justify-content:center; 
    height:100vh; margin:0; }
  .card { 
    text-align:center; 
    padding:40px; 
    border-radius:12px; 
    box-shadow:0 10px 30px rgba(0,0,0,0.6); 
    background: linear-gradient(135deg,#1f2937 0%, #111827 100%); 
    width:80%; max-width:720px; }
  h1 { margin:0 0 10px 0; color:#ff6b6b; font-size:36px; }
  p { color:#bfc7d6; margin:0; font-size:18px; }
</style>
</head>
<body>
  <div class="card">
    <h1> تم حظر هذا المحتوى</h1>
    <p>تم استبدال الصفحة التي تحاول زيارتها بصفحة تحذير حفاظًا على سلامة العائلة.</p>
  </div>
</body>
</html>
""")
ensure_assets()

def load_banned_words():

    try:
        with open(BANNED_TXT,'r',encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except Exception:
        return ['adult','badsite']
    
banned_words = load_banned_words()

try:
    import keyboard
    KEYBOARD_AVAILABLE= True
except Exception:
    KEYBOARD_AVAILABLE = False


def open_index_in_same_tab_via_keyboard() :

    index_path = os.path.abspath(INDEX_HTML).replace('\\','/') 
    target = f'file:///{index_path}'

    try :
        keyboard.send("ctrl+l")
        time.sleep(0.1)
        keyboard.write(target)
        time.sleep(0.05)
        keyboard.send("enter")
    except Exception:
        webbrowser.open(target)


def monitor_browser_loop(page,status_text):

    while True :
        try:
            for proc in psutil.process_iter(['pid','name']):
                name = (proc.info.get('name') or "").lower()

                if any(b in name for b in ['chrome','firefox','edge','brave','opera']):
                    try :
                        wins = gw.getWindowsWithTitle('')
                    except Exception :
                        wins = []
                    for w in wins:
                        title = (w.title or "").lower()
                        if not title :
                            continue
                        if any(bad in title for bad in banned_words):
                            try:
                                w.activate()
                            except Exception :
                                pass
                                
                            time.sleep(0.12)

                            if KEYBOARD_AVAILABLE :
                                try :
                                    open_index_in_same_tab_via_keyboard()

                                    try :
                                        page.update()
                                    except Exception :
                                        pass
                                except Exception :
                                    try: 
                                        w.close()
                                    except Exception :
                                        pass
                                    webbrowser.open(f'file:///{os.path.abspath(INDEX_HTML)}')
                            else :
                                try: 
                                    w.close()
                                except Exception :
                                    pass
                                webbrowser.open(f'file:///{os.path.abspath(INDEX_HTML)}')
                            time.sleep(1.0)
            time.sleep(0.9)  
        except Exception :
            time.sleep(1.0)
                

def main(page:Page):

    page.title = "Family Sifty"
    page.bgcolor = "#071124"
    page.theme_mode = ThemeMode.DARK
    page.window.width = 600
    page.window.height = 400

    title = Text("Family Sifty",size=36,weight=FontWeight.BOLD,color="#00E0FF",text_align="center")
    subtitle = Text(
        "برنامج حماية تلقائي يمنع المواقع الغير مرغوب فيها.",
        color="#B9C8D8",size=16,text_align="center"
    )

    status_text = Text("جاري المراقبة ....",size=18,weight=FontWeight.BOLD,color="#01F663",text_align="center")

    layout = Column(
        [
            Container(title,alignment=alignment.center,padding=20),
            Container(subtitle,alignment=alignment.center,padding=10),
            Container(status_text,alignment=alignment.center,padding=30)
        ],
        alignment="center",
        horizontal_alignment="center",
        expand=True
    )

    page.add(layout)
    page.update()


    t_mon = threading.Thread(target=monitor_browser_loop,args=(page, status_text),daemon=True)
    t_mon.start()
    def hide_after_delay():
        time.sleep(5)
        try:
            page.window.visible = False
            try:
                page.update()
            except Exception :
                pass
        except Exception:
            pass
    
    threading.Thread(target=hide_after_delay,daemon=True).start()

if __name__ == "__main__":
    app(target=main,assets_dir=ASSETS_DIR)
