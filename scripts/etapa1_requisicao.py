import requests, os, zipfile, urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Desabilita avisos de certificados inseguros
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def baixar_tudo():
    """
    ETAPA 1: Requisicao com Stream.
    Trade-off: Baixar via stream (chunks) em vez de carregar o arquivo inteiro na RAM.
    Isso evita o erro IncompleteRead em conexoes instaveis com o servidor da ANS.
    """
    print("\n[REQUISICAO] Iniciando busca de dados no portal da ANS")
    path_raw = "dados/raw/"
    if not os.path.exists(path_raw): os.makedirs(path_raw)
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    # 1. Busca Cadastro
    print("[REQUISICAO] Localizando e baixando arquivo de cadastro de operadoras")
    url_cad_base = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
    try:
        soup_cad = BeautifulSoup(session.get(url_cad_base, verify=False, timeout=30).text, 'html.parser')
        link_cad = urljoin(url_cad_base, next(a.get('href') for a in soup_cad.find_all('a') if '.csv' in a.get('href').lower()))
        
        with open(os.path.join(path_raw, "operadoras_ativas.csv"), 'wb') as f:
            f.write(session.get(link_cad, verify=False).content)
    except Exception as e:
        print(f"[ERRO] Falha ao buscar cadastro: {e}")

    # 2. Busca 3 ultimos trimestres
    print("[REQUISICAO] Analisando diretorio de demonstracoes contabeis para localizar ultimos trimestres")
    url_base = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
    root_html = session.get(url_base, verify=False).text
    soup_root = BeautifulSoup(root_html, 'html.parser')
    anos = sorted([a.get('href').replace('/', '') for a in soup_root.find_all('a') if a.get('href').replace('/', '').isdigit()], reverse=True)
    
    arquivos_links = []
    for ano in anos:
        if len(arquivos_links) >= 3: break
        url_ano = urljoin(url_base, f"{ano}/")
        soup_ano = BeautifulSoup(session.get(url_ano, verify=False).text, 'html.parser')
        zips = sorted([urljoin(url_ano, a.get('href')) for a in soup_ano.find_all('a') if '.zip' in a.get('href').lower()], reverse=True)
        for z in zips:
            if len(arquivos_links) < 3: arquivos_links.append(z)

    # 3. Download via STREAM (Chunks de 1MB)
    for i, link in enumerate(arquivos_links):
        nome = link.split('/')[-1]
        dest = os.path.join(path_raw, nome)
        print(f"[REQUISICAO] Baixando arquivo {i+1} de 3: {nome}")
        
        try:
            # stream=True permite baixar o arquivo aos poucos
            with session.get(link, verify=False, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024): # 1MB por vez
                        if chunk:
                            f.write(chunk)
            
            # Extração
            print(f"[REQUISICAO] Extraindo conteudo do arquivo: {nome}")
            with zipfile.ZipFile(dest, 'r') as z:
                z.extractall(path_raw)
                
        except Exception as e:
            print(f"[AVISO] Falha no download de {nome}: {e}")

    print("[REQUISICAO] Processo de requisicao e extracao finalizado")

if __name__ == "__main__":
    baixar_tudo()