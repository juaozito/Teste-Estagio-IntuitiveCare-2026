import requests, os, zipfile, urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def baixar_tudo():
    print("\n[INICIANDO] Buscando os 3 trimestres mais recentes na ANS...")
    path_raw = "dados/raw/"
    if not os.path.exists(path_raw): os.makedirs(path_raw)
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    # Cadastro
    print("[BUSCANDO] Localizando cadastro de operadoras...")
    url_cad_base = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
    soup_cad = BeautifulSoup(session.get(url_cad_base, verify=False).text, 'html.parser')
    link_cad = urljoin(url_cad_base, next(a.get('href') for a in soup_cad.find_all('a') if '.csv' in a.get('href').lower()))
    with open(os.path.join(path_raw, "operadoras_ativas.csv"), 'wb') as f:
        f.write(session.get(link_cad, verify=False).content)

    # 3 Últimos Trimestres
    print("[ANALISANDO] Verificando pastas de demonstrações contábeis...")
    url_base = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
    soup_root = BeautifulSoup(session.get(url_base, verify=False).text, 'html.parser')
    anos = sorted([a.get('href').replace('/', '') for a in soup_root.find_all('a') if a.get('href').replace('/', '').isdigit()], reverse=True)
    
    arquivos_encontrados = []
    for ano in anos:
        if len(arquivos_encontrados) >= 3: break
        url_ano = urljoin(url_base, f"{ano}/")
        soup_ano = BeautifulSoup(session.get(url_ano, verify=False).text, 'html.parser')
        zips = sorted([urljoin(url_ano, a.get('href')) for a in soup_ano.find_all('a') if '.zip' in a.get('href').lower()], reverse=True)
        for z in zips:
            if len(arquivos_encontrados) < 3: arquivos_encontrados.append(z)

    for i, link in enumerate(arquivos_encontrados):
        nome = link.split('/')[-1]
        print(f"[DOWNLOAD {i+1}/3] {nome}...")
        dest = os.path.join(path_raw, nome)
        with open(dest, 'wb') as f: f.write(session.get(link, verify=False).content)
        with zipfile.ZipFile(dest, 'r') as z: z.extractall(path_raw)
    
    print("✅ [OK] Arquivos prontos!")

if __name__ == "__main__":
    baixar_tudo()