# Instruções de Integração SAML com seu App.py

## 📋 O que foi criado

Criei um **módulo SAML separado** (`saml_auth.py`) que pode ser facilmente integrado ao seu `app.py` existente sem modificar significativamente sua estrutura atual.

## 🔧 Arquivos criados

1. **`saml_auth.py`** - Módulo principal de autenticação SAML
2. **`app_integrado.py`** - Seu app.py com SAML integrado (exemplo)
3. **`templates/login_saml.html`** - Página de login SAML
4. **`templates/dashboard_saml.html`** - Dashboard para usuários autenticados
5. **`requirements_saml.txt`** - Dependências adicionais
6. **Configurações SAML** (da pasta `saml_app/saml/`)

## 🚀 Como integrar ao seu app.py atual

### Passo 1: Instalar dependências

```bash
pip install -r requirements_saml.txt
```

### Passo 2: Adicionar ao seu app.py

Adicione estas linhas no **início** do seu `app.py`:

```python
# Importar módulo SAML
from saml_auth import create_saml_auth, login_required

# Após criar a instância Flask
app = Flask(__name__)

# Configurar chave secreta (IMPORTANTE!)
app.config['SECRET_KEY'] = 'sua-chave-secreta-mude-em-producao'

# Inicializar autenticação SAML
saml_auth = create_saml_auth(app, saml_path='saml')
app.saml_auth = saml_auth
```

### Passo 3: Proteger rotas existentes

Para proteger qualquer rota existente, basta adicionar o decorator `@login_required`:

```python
@app.route("/cria_usuario")
@login_required  # <- Adicione esta linha
def cria_usuario():
    logging.info(f"Chamou a rota cria_usuario")
    return render_template("formulario_ajax_simples.html")

@app.route("/desativa_usuario")
@login_required  # <- Adicione esta linha
def desativa_usuario():
    logging.info(f"Chamou a rota desativa_usuario")
    return render_template("desativa_usuario.html")
```

### Passo 4: Adicionar rotas de login/dashboard (opcional)

```python
@app.route("/login")
def login():
    return render_template("login_saml.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user_data = saml_auth.get_user_data()
    return render_template("dashboard_saml.html", user=user_data)
```

## 🔐 Como usar o decorator @login_required

### Proteção básica:
```python
@app.route("/minha_rota")
@login_required
def minha_rota():
    # Usuário já está autenticado aqui
    return render_template("minha_pagina.html")
```

### Proteção por grupo específico:
```python
@app.route("/admin")
@saml_auth.require_group("Administradores")
def admin():
    # Apenas usuários do grupo "Administradores"
    return render_template("admin.html")
```

### Obter dados do usuário autenticado:
```python
@app.route("/minha_rota")
@login_required
def minha_rota():
    user_data = saml_auth.get_user_data()
    
    # Dados disponíveis:
    # user_data['email']
    # user_data['display_name']
    # user_data['groups']
    # user_data['upn']
    # etc.
    
    return render_template("minha_pagina.html", user=user_data)
```

## 📁 Estrutura de arquivos necessária

```
seu_projeto/
├── app.py                    # Seu app original (modificado)
├── saml_auth.py             # Módulo SAML (novo)
├── templates/
│   ├── login_saml.html      # Página de login (novo)
│   ├── dashboard_saml.html  # Dashboard (novo)
│   └── ... (seus templates existentes)
├── saml/                    # Configurações SAML
│   ├── settings/
│   │   ├── settings.json
│   │   └── advanced_settings.json
│   └── certs/
└── funcoes/                 # Seus módulos existentes
    ├── log.py
    ├── banco.py
    └── funcoes.py
```

## ⚙️ Configurar Azure AD

1. **Copie a pasta `saml/`** da pasta `saml_app/` para seu projeto
2. **Configure o Azure AD** seguindo as instruções do `README_SAML.md`
3. **Edite `saml/settings/settings.json`** com suas informações:
   - Tenant ID
   - Certificado do Azure AD
   - URLs corretas

## 🔄 Rotas SAML automáticas

O módulo adiciona automaticamente estas rotas:

- `/saml/login` - Inicia login SAML
- `/saml/acs` - Recebe resposta do Azure AD
- `/saml/logout` - Logout SAML
- `/saml/sls` - Single Logout Service
- `/saml/metadata` - Metadados do Service Provider

## 🧪 Testar a integração

1. **Execute seu app:**
   ```bash
   python app.py
   ```

2. **Teste as configurações:**
   ```
   http://localhost:5000/test-saml
   ```

3. **Teste o login:**
   ```
   http://localhost:5000/login
   ```

## 📝 Exemplo completo de integração

```python
from flask import Flask, request, render_template
from funcoes.log import configurar_logs
import logging
from funcoes.banco import inserir_usuario, deletar_usuario, lerResultado
from funcoes.funcoes import capitalizaNome, buscaDepartamento

# Importar módulo SAML
from saml_auth import create_saml_auth, login_required

configurar_logs()

app = Flask(__name__)

# Configurar SAML
app.config['SECRET_KEY'] = 'sua-chave-secreta-mude-em-producao'
saml_auth = create_saml_auth(app, saml_path='saml')
app.saml_auth = saml_auth

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login_saml.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user_data = saml_auth.get_user_data()
    return render_template("dashboard_saml.html", user=user_data)

# Proteger rotas existentes
@app.route("/cria_usuario")
@login_required  # <- Adicione apenas esta linha
def cria_usuario():
    logging.info(f"Chamou a rota cria_usuario")
    return render_template("formulario_ajax_simples.html")

@app.route("/desativa_usuario")
@login_required  # <- Adicione apenas esta linha
def desativa_usuario():
    logging.info(f"Chamou a rota desativa_usuario")
    return render_template("desativa_usuario.html")

# Suas rotas existentes continuam iguais...
@app.route("/executa_cria_usuario", methods=['POST'])
@login_required  # <- Opcional: proteger também as execuções
def executa_cria_usuario():
    # Seu código existente...
    pass

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🔧 Funcionalidades do módulo SAML

### Classe SAMLAuth:
- `is_authenticated()` - Verifica se usuário está autenticado
- `get_user_data()` - Retorna dados do usuário
- `login_required()` - Decorator para proteção de rotas
- `require_group()` - Decorator para proteção por grupo
- `check_saml_settings()` - Verifica configurações

### Decorator standalone:
- `@login_required` - Pode ser usado diretamente nas rotas

## 🚨 Pontos importantes

1. **Chave secreta:** Mude `SECRET_KEY` para uma chave segura em produção
2. **Configuração SAML:** Configure o Azure AD antes de testar
3. **Templates:** Use os templates fornecidos ou adapte os seus
4. **Logs:** O módulo usa o mesmo sistema de logging do seu app
5. **Sessões:** O módulo gerencia sessões automaticamente

## 📞 Suporte

- **Teste configurações:** `/test-saml`
- **Metadados SP:** `/saml/metadata`
- **Logs:** Verifique os logs do Flask para erros SAML
- **Documentação completa:** `README_SAML.md`

---

**A integração é modular e não quebra seu código existente!**

