import requests
import os
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
PASTA_RAW = "dados/raw/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def baixar_arquivos():
    if not os.path.exists(PASTA_RAW): os.makedirs(PASTA_RAW)
    session = requests.Session()
    
    print(f"Conectando à ANS...")
    try:
        r = session.get(URL_BASE, headers=HEADERS, timeout=30)
        # Usando 'lxml' para ignorar erros de HTML malformado do servidor
        soup = BeautifulSoup(r.content, 'lxml')
        
        anos = []
        for a in soup.find_all('a'):
            href = a.get('href', '').strip('/')
            if href.isdigit() and len(href) == 4:
                anos.append(urljoin(URL_BASE, a.get('href')))
        
        anos = sorted(list(set(anos)), reverse=True)
        baixados = 0

        for url_ano in anos:
            if baixados >= 3: break
            
            print(f"Acessando ano: {url_ano.split('/')[-2]}")
            r_ano = session.get(url_ano, headers=HEADERS)
            soup_ano = BeautifulSoup(r_ano.content, 'lxml')
            
            # Pega trimestres
            trimestres = [urljoin(url_ano, t.get('href')) for t in soup_ano.find_all('a') 
                          if t.get('href') and any(x in t.get('href').upper() for x in ['1T', '2T', '3T', '4T'])]
            trimestres = sorted(list(set(trimestres)), reverse=True)

            for url_tri in trimestres:
                if baixados >= 3: break
                
                r_tri = session.get(url_tri, headers=HEADERS)
                soup_tri = BeautifulSoup(r_tri.content, 'lxml')
                
                zips = [urljoin(url_tri, z.get('href')) for z in soup_tri.find_all('a') 
                        if z.get('href') and z.get('href').lower().endswith('.zip')]

                for url_zip in zips:
                    if baixados >= 3: break
                    nome_zip = url_zip.split('/')[-1]
                    caminho_local = os.path.join(PASTA_RAW, nome_zip)
                    
                    print(f"  -> Baixando: {nome_zip}...")
                    with session.get(url_zip, headers=HEADERS, stream=True) as r_file:
                        with open(caminho_local, 'wb') as f:
                            for chunk in r_file.iter_content(chunk_size=1024*1024):
                                f.write(chunk)
                    
                    print(f"  -> Extraindo: {nome_zip}...")
                    with zipfile.ZipFile(caminho_local, 'r') as zip_ref:
                        zip_ref.extractall(PASTA_RAW)
                    baixados += 1

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    baixar_arquivos()
    print("\n--- Fim. Verifique a pasta dados/raw ---")