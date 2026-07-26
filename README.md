# 🚀 Auto Coder v1 - Login  key = [ cyber]

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Online-success.svg)]()
[![Author](https://img.shields.io/badge/Author-@cybersecofc-purple.svg)]()

**Auto Coder v1** é uma ferramenta web profissional que gera scripts Python automatizados para verificação de logins em qualquer site. Com uma interface moderna e intuitiva, basta colar a URL e os campos HTML para gerar um script completo de login checker.

---

## 📋 Sumário

- [Funcionalidades](#-funcionalidades)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Gerando Scripts](#-gerando-scripts)
- [Estrutura do Script Gerado](#-estrutura-do-script-gerado)
- [Exemplos](#-exemplos)
- [Configuração](#-configuração)
- [Deploy](#-deploy)
- [Segurança](#-segurança)
- [FAQ](#-faq)
- [Suporte](#-suporte)

---

## ✨ Funcionalidades

### Principais
- 🎯 **Geração automática de scripts** - Cole URL + HTML e tenha um script funcional
- 🔐 **Sistema de keys** - Acesso restrito e seguro
- 🌐 **Qualquer site** - Funciona com qualquer página de login
- 🖥️ **Interface moderna** - Design profissional com tema dark
- 📥 **Download direto** - Baixe o script gerado com um clique
- 🎵 **Música de fundo** - Experiência imersiva
- 🔍 **Parser inteligente** - Detecta automaticamente campos de login

### Técnicas
- ✅ Suporte a inputs, buttons, selects, textareas
- ✅ Detecção automática de campos (usuário/senha)
- ✅ Suporte a CSS Selectors e XPath
- ✅ Headless Chrome com Selenium
- ✅ Sistema de retry automático
- ✅ Logs coloridos e detalhados
- ✅ Salva resultados em lives.txt e dies.txt

---

## 🔧 Instalação

### Pré-requisitos

- **Python** 3.7+
- **pip** (gerenciador de pacotes)
- **Google Chrome** (para Selenium)

### Método 1: Instalação Local


# Clone o repositório
git clone https://github.com/seuusuario/auto-coder.git
cd auto-coder

# Instale as dependências
pip install flask flask-cors requests colorama selenium webdriver-manager

# Execute
python app.py

Método 2: Download Direto
bash
# Baixe o arquivo
wget https://github.com/seuusuario/auto-coder/raw/main/app.py

# Execute
python app.py
Método 3: Instalação Automática
O próprio script instala as dependências automaticamente na primeira execução:

bash
python app.py
# As dependências serão instaladas automaticamente!
🚀 Como Usar
1. Acesse a Interface
Após executar o script, acesse no navegador:

text
http://localhost:5000
2. Faça Login
Use uma key válida para acessar o painel:

text
Keys disponíveis no código fonte
(Seção KEYS = {...})
3. Cole os Dados do Site
Na área de texto, cole a URL seguida dos campos HTML:

text
https://exemplo.com/login
<input type="email" name="email" placeholder="Email">
<input type="password" name="senha" placeholder="Senha">
<button type="submit">Entrar</button>
4. Gere o Script
Clique em ⚡ GERAR e visualize o script gerado.

5. Baixe e Execute
bash
# Baixe o script clicando em 📥 BAIXAR

# Prepare os logins no formato usuario:senha
echo "usuario1@email.com:senha123" > db.txt
echo "usuario2@email.com:senha456" >> db.txt

# Execute o script gerado
python cyber.py
📝 Gerando Scripts
Formato de Entrada
O parser aceita vários formatos de entrada:

Formato 1: URL + HTML
text
https://site.com/login
<input name="user" type="text">
<input name="pass" type="password">
<button>Login</button>
Formato 2: Apenas URL (detecção automática)
text
https://site.com/login
Formato 3: HTML com classes/IDs
text
https://site.com/login
<input id="username" class="form-control" type="email">
<input id="password" class="form-control" type="password">
<button id="btn-login" class="btn-primary">Acessar</button>
Campos Suportados
Tipo	Descrição	Exemplo
input[type="text"]	Campo de texto	<input name="user">
input[type="email"]	Campo de email	<input type="email">
input[type="password"]	Campo de senha	<input type="password">
button	Botão de submit	<button>Login</button>
input[type="submit"]	Botão submit	<input type="submit">
a	Link clicável	<a href="#">Entrar</a>
select	Menu dropdown	<select name="tipo">
textarea	Área de texto	<textarea name="msg">
Detecção Automática
O parser detecta automaticamente:

Campos de usuário: palavras como user, username, email, login, cpf

Campos de senha: palavras como password, senha, pass, pwd

Botões: palavras como entrar, login, submit, acessar, sign in
