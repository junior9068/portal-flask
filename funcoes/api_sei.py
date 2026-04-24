import requests, os, logging

URL_TOKEN = os.getenv("URL_TOKEN")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

#OBTER TOKEN

def obter_token():
    try:
    # Body no formato x-www-form-urlencoded
        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(
            URL_TOKEN,
            data=data,
            auth=(CONSUMER_KEY, CONSUMER_SECRET)  # Basic Auth
        )

        if response.status_code != 200:
            logging.error("Erro ao obter token:", response.text)
            return None

        token = response.json().get("access_token")
        print("Token obtido:", token)
        return token
    except Exception as erro:
        print(f"Erro na requisição: {erro}")
        return None


# CONSUMIR A API: Buscar unidades do SEI para o usuário
def buscar_unidades(usuario):
    token = obter_token()
    if not token:
        logging.error("Token de acesso não disponível.")
        return None
    try:
        URL_API = os.getenv("URL_API")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "accept": "*/*"
        }
        payload = {
            "idSistema": "100000100",
            "tipoServidorAutenticacao": "AD",
            "idOrgaoUsuario": "0",
            "siglaUsuario": usuario
        }

        response_api = requests.post(
            URL_API,
            headers=headers,
            json=payload
        )
        #Para debug: Exibe o status e a resposta da API
        # print("Status:", response_api.status_code)
        # print("Resposta RAW:", response_api.text)
        
        # Lista de unidades retornada pela API
        unidades = response_api.json().get("Unidades", [])
        #Varre a lista de unidades e extrai apenas as siglas para retornar
        lista_unidades = []
        dicionario_unidades = {"unidades": []}
        for unidade in unidades:
            lista_unidades.append(unidade.get("SiglaUnidade"))
            dicionario_unidades["unidades"].append({
                "sigla": unidade.get("SiglaUnidade"),
                "descricao": unidade.get("DescricaoUnidade")
            })
        return dicionario_unidades  # Retorna apenas as unidades
        # print("Status:", response_api.status_code)
        # print("Resposta:", response_api.text)
    except Exception as erro:
        logging.error(f"Erro na requisição: {erro}")
        return None

if __name__ == "__main__":
    print(buscar_unidades("thiago.oliveira"))