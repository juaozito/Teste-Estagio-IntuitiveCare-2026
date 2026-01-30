import requests
import os
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
URL_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
URL_CADASTRO = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
PASTA_RAW = "dados/raw/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def baixar_com_retry(session, url, caminho):
    for i in range(3):
        try:
            with session.get(url, stream=True, timeout=120, verify=False) as r:
                r.raise_for_status()
                with open(caminho, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024): f.write(chunk)
            return True
        except Exception: time.sleep(2)
    return False

def baixar_arquivos():
    if not os.path.exists(PASTA_RAW): os.makedirs(PASTA_RAW)
    session = requests.Session()
    session.headers.update(HEADERS)

    # 1. Download Cadastro
    r_cad = session.get(URL_CADASTRO, verify=False)
    soup_cad = BeautifulSoup(r_cad.text, 'html.parser')
    link_cad = urljoin(URL_CADASTRO, next(a.get('href') for a in soup_cad.find_all('a') if 'Relatorio_cadop' in a.get('href')))
    baixar_com_retry(session, link_cad, os.path.join(PASTA_RAW, "operadoras_ativas.csv"))

    # 2. Download 3 Últimos Trimestres
    r_base = session.get(URL_BASE, verify=False)
    anos = sorted([a.get('href').replace('/','') for a in BeautifulSoup(r_base.text, 'html.parser').find_all('a') if a.get('href').replace('/','').isdigit()], reverse=True)
    
    baixados = 0
    for ano in anos:
        if baixados >= 3: break
        url_ano = urljoin(URL_BASE, f"{ano}/")
        r_ano = session.get(url_ano, verify=False)
        links = [urljoin(url_ano, a.get('href')) for a in BeautifulSoup(r_ano.text, 'html.parser').find_all('a') if '.zip' in a.get('href').lower()]
        for link in sorted(links, reverse=True):
            if baixados >= 3: break
            caminho = os.path.join(PASTA_RAW, link.split('/')[-1])
            if baixar_com_retry(session, link, caminho):
                with zipfile.ZipFile(caminho, 'r') as z: z.extractall(PASTA_RAW)
                baixados += 1
    print("✅ Etapa 1 Finalizada.")

if __name__ == "__main__":
    baixar_arquivos()