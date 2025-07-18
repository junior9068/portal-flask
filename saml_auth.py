"""
Módulo de Autenticação SAML para Flask
Integração com Microsoft Azure AD

Este módulo fornece todas as funcionalidades necessárias para autenticação SAML
sem modificar significativamente o app.py existente.
"""

from flask import request, redirect, session, url_for, make_response, flash
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
import os
import json
from functools import wraps
import logging
# from funcoes.log import configurar_logs

# configurar_logs()

class SAMLAuth:
    """Classe principal para gerenciar autenticação SAML"""
    
    def __init__(self, app=None, saml_path=None):
        self.app = app
        self.saml_path = saml_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saml')
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o módulo SAML com a aplicação Flask"""
        self.app = app
        
        # Configurar sessão se não estiver configurada
        if not hasattr(app, 'session_interface'):
            app.config.setdefault('SECRET_KEY', 'your-secret-key-change-this')
        
        # Registrar rotas SAML
        self._register_routes()
        
        # Configurar logging
        logging.getLogger('saml_auth').setLevel(logging.INFO)
    
    def _register_routes(self):
        """Registra as rotas SAML na aplicação Flask"""
        
        @self.app.route('/saml/login')
        def saml_login():
            """Inicia o processo de login SAML"""
            req = self._prepare_flask_request(request)
            auth = self._init_saml_auth(req)
            return redirect(auth.login())
        
        @self.app.route('/saml/acs', methods=['POST'])
        def saml_acs():
            """Assertion Consumer Service - Processa a resposta SAML do Azure AD"""
            req = self._prepare_flask_request(request)
            auth = self._init_saml_auth(req)
            
            # Processa a resposta SAML
            auth.process_response()
            errors = auth.get_errors()
            
            if len(errors) == 0:
                # Autenticação bem-sucedida
                session['samlUserdata'] = auth.get_attributes()
                session['samlNameId'] = auth.get_nameid()
                session['samlNameIdFormat'] = auth.get_nameid_format()
                session['samlSessionIndex'] = auth.get_session_index()
                
                logging.info(f"Login SAML bem-sucedido: {auth.get_nameid()}")
                
                # Redirecionar para a URL solicitada ou home
                self_url = OneLogin_Saml2_Utils.get_self_url(req)
                if 'RelayState' in request.form and OneLogin_Saml2_Utils.get_self_url(req) != request.form['RelayState']:
                    return redirect(auth.redirect_to(request.form['RelayState']))
                else:
                    return redirect(url_for('home'))
            else:
                # Erro na autenticação
                error_msg = f"Erro na autenticação SAML: {', '.join(errors)}"
                if auth.get_last_error_reason():
                    error_msg += f" Razão: {auth.get_last_error_reason()}"
                
                logging.error(error_msg)
                flash(error_msg, 'error')
                return redirect(url_for('home'))
        
        @self.app.route('/saml/sls', methods=['GET', 'POST'])
        def saml_sls():
            """Single Logout Service - Processa o logout SAML"""
            req = self._prepare_flask_request(request)
            auth = self._init_saml_auth(req)
            
            # Processa a requisição de logout
            url = auth.process_slo(delete_session_cb=lambda: session.clear())
            errors = auth.get_errors()
            
            if len(errors) == 0:
                logging.info("Logout SAML realizado com sucesso")
                if url is not None:
                    return redirect(url)
                else:
                    flash('Logout realizado com sucesso.', 'success')
                    return redirect(url_for('home'))
            else:
                error_msg = f"Erro no logout SAML: {', '.join(errors)}"
                logging.error(error_msg)
                flash(error_msg, 'error')
                return redirect(url_for('home'))
        
        @self.app.route('/saml/logout')
        def saml_logout():
            """Inicia o processo de logout SAML"""
            if 'samlUserdata' in session:
                # Single Logout via SAML
                req = self._prepare_flask_request(request)
                auth = self._init_saml_auth(req)
                
                name_id = session.get('samlNameId')
                session_index = session.get('samlSessionIndex')
                name_id_format = session.get('samlNameIdFormat')
                
                logging.info(f"Iniciando logout SAML para: {name_id}")
                
                return redirect(auth.logout(
                    name_id=name_id,
                    session_index=session_index,
                    name_id_format=name_id_format
                ))
            else:
                # Logout local apenas
                session.clear()
                flash('Logout realizado com sucesso.', 'success')
                return redirect(url_for('home'))
        
        @self.app.route('/saml/metadata')
        def saml_metadata():
            """Retorna os metadados SAML do Service Provider"""
            try:
                saml_settings = OneLogin_Saml2_Settings(custom_base_path=self.saml_path)
                metadata = saml_settings.get_sp_metadata()
                errors = saml_settings.check_sp_settings()
                
                if len(errors) == 0:
                    resp = make_response(metadata, 200)
                    resp.headers['Content-Type'] = 'text/xml'
                    return resp
                else:
                    error_msg = f"Erro nas configurações SAML: {', '.join(errors)}"
                    logging.error(error_msg)
                    return f"<error>{error_msg}</error>", 500
            except Exception as e:
                logging.error(f"Erro ao gerar metadados: {str(e)}")
                return f"<error>Erro ao gerar metadados: {str(e)}</error>", 500
    
    def _prepare_flask_request(self, request):
        """Prepara o request do Flask para o formato esperado pelo python3-saml"""
        url_data = request.url.split('?')
        return {
            'https': 'on' if request.scheme == 'https' else 'off',
            #'https': 'on',
            'http_host': request.headers.get('Host', request.host),
            'server_port': request.environ.get('SERVER_PORT'),
            #'server_port': 443,
            'script_name': request.path,
            'get_data': request.args.copy(),
            'post_data': request.form.copy(),
            'query_string': url_data[1] if len(url_data) > 1 else ''
        }
    
    def _init_saml_auth(self, req):
        """Inicializa o objeto de autenticação SAML"""
        auth = OneLogin_Saml2_Auth(req, custom_base_path=self.saml_path)
        return auth
    
    def is_authenticated(self):
        """Verifica se o usuário está autenticado via SAML"""
        return 'samlUserdata' in session and session['samlUserdata'] is not None
    
    def get_user_data(self):
        """Retorna os dados do usuário autenticado"""
        if not self.is_authenticated():
            return None
        
        userdata = session.get('samlUserdata', {})
        name_id = session.get('samlNameId', '')
        
        # Processar atributos do usuário
        user_info = {
            'name_id': name_id,
            'email': userdata.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress', [''])[0],
            'display_name': userdata.get('http://schemas.microsoft.com/identity/claims/displayname', [''])[0],
            'given_name': userdata.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname', [''])[0],
            'surname': userdata.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname', [''])[0],
            'upn': userdata.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name', [''])[0],
            'groups': userdata.get('http://schemas.microsoft.com/ws/2008/06/identity/claims/groups', []),
            'tenant_id': userdata.get('http://schemas.microsoft.com/identity/claims/tenantid', [''])[0],
            'object_id': userdata.get('http://schemas.microsoft.com/identity/claims/objectidentifier', [''])[0],
            'all_attributes': userdata
        }
        
        return user_info
    
    def login_required(self, f):
        """Decorator para rotas que requerem autenticação SAML"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                # Salvar a URL atual para redirecionamento após login
                session['next_url'] = request.url
                return redirect(url_for('saml_login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def require_group(self, group_name):
        """Decorator para rotas que requerem um grupo específico"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.is_authenticated():
                    session['next_url'] = request.url
                    return redirect(url_for('saml_login'))
                
                user_data = self.get_user_data()
                groups = user_data.get('groups', [])
                
                if group_name not in groups:
                    flash(f'Acesso negado: grupo "{group_name}" necessário', 'error')
                    return redirect(url_for('home'))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def check_saml_settings(self):
        """Verifica as configurações SAML e retorna status"""
        try:
            saml_settings = OneLogin_Saml2_Settings(custom_base_path=self.saml_path)
            
            # Verificar configurações do SP
            sp_errors = saml_settings.check_sp_settings()
            
            # Verificar configurações do IdP
            idp_errors = saml_settings.check_idp_settings()
            
            # Informações das configurações
            settings_info = {
                'sp_entity_id': saml_settings.get_sp_data().get('entityId'),
                'sp_acs_url': saml_settings.get_sp_data().get('assertionConsumerService', {}).get('url'),
                'sp_sls_url': saml_settings.get_sp_data().get('singleLogoutService', {}).get('url'),
                'idp_entity_id': saml_settings.get_idp_data().get('entityId'),
                'idp_sso_url': saml_settings.get_idp_data().get('singleSignOnService', {}).get('url'),
                'idp_sls_url': saml_settings.get_idp_data().get('singleLogoutService', {}).get('url'),
                'sp_errors': sp_errors,
                'idp_errors': idp_errors,
                'is_valid': len(sp_errors) == 0 and len(idp_errors) == 0
            }
            
            return settings_info
            
        except Exception as e:
            logging.error(f"Erro ao verificar configurações SAML: {str(e)}")
            return {
                'error': str(e),
                'is_valid': False
            }


# Função de conveniência para criar uma instância global
def create_saml_auth(app, saml_path=None):
    """Cria e configura uma instância SAMLAuth"""
    return SAMLAuth(app, saml_path)


# Decorator standalone para compatibilidade
def login_required(f):
    """
    Decorator standalone para autenticação SAML
    Requer que uma instância SAMLAuth seja configurada na aplicação
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar se existe uma instância SAMLAuth configurada
        if hasattr(f.__globals__.get('app', {}), 'saml_auth'):
            saml_auth = f.__globals__['app'].saml_auth
            if not saml_auth.is_authenticated():
                session['next_url'] = request.url
                return redirect(url_for('login'))
        else:
            # Fallback: verificação básica de sessão
            if 'samlUserdata' not in session or session['samlUserdata'] is None:
                session['next_url'] = request.url
                return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

