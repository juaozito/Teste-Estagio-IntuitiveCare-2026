import requests, os, zipfile, urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# [EXPLICAÇÃO]: Desabilita avisos de segurança sobre certificados SSL (InsecureRequestWarning).
# Isso é feito para evitar que o console fique poluído com alertas de segurança, 
# já que o servidor da ANS às vezes possui certificados que não são reconhecidos automaticamente.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def baixar_tudo():
    """
    ETAPA 1: Requisição com Stream.
    OBJETIVO: Automatizar o download de dados do portal de Dados Abertos da ANS.
    
    EXPLICAÇÃO DO TRADE-OFF TÉCNICO:
    O código utiliza 'stream=True' (download em chunks). 
    - Por que? Carregar arquivos ZIP grandes (que podem ter centenas de MB) diretamente na memória RAM 
      poderia causar travamentos no computador ou erros de estouro de memória.
    - Como funciona? Ele baixa o arquivo em pequenos 'pedaços' de 1MB por vez, salvando-os no HD 
      imediatamente, o que garante estabilidade mesmo em conexões de internet instáveis.
    """
    
    print("\n[REQUISICAO] Iniciando busca de dados no portal da ANS")
    
    # [EXPLICAÇÃO]: Criação da estrutura de pastas. 
    # O script verifica se a pasta 'dados/raw/' existe; caso contrário, a cria automaticamente.
    # 'raw' (bruto) é o termo usado para dados que ainda não foram processados ou limpos.
    path_raw = "dados/raw/"
    if not os.path.exists(path_raw): os.makedirs(path_raw)
    
    # [EXPLICAÇÃO]: Configuração da Sessão de Conexão.
    # Usar 'requests.Session()' é mais eficiente do que chamadas isoladas, pois mantém a conexão aberta.
    # O 'User-Agent' simula um navegador real (Mozilla 5.0) para evitar que o site da ANS bloqueie o robô.
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    # --- BLOCO 1: BUSCA DO CADASTRO DE OPERADORAS ---
    # Este arquivo contém a lista oficial de todas as operadoras ativas na ANS.
    print("[REQUISICAO] Localizando e baixando arquivo de cadastro de operadoras")
    url_cad_base = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
    try:
        # BeautifulSoup analisa o HTML da página para encontrar dinamicamente o link do arquivo .csv.
        # Isso previne erros caso o nome do arquivo mude no futuro.
        soup_cad = BeautifulSoup(session.get(url_cad_base, verify=False, timeout=30).text, 'html.parser')
        
        # 'next(...)' localiza o primeiro link (tag <a>) que contenha '.csv' no endereço.
        link_cad = urljoin(url_cad_base, next(a.get('href') for a in soup_cad.find_all('a') if '.csv' in a.get('href').lower()))
        
        # Faz o download do arquivo CSV e o salva localmente.
        with open(os.path.join(path_raw, "operadoras_ativas.csv"), 'wb') as f:
            f.write(session.get(link_cad, verify=False).content)
            
    except Exception as e:
        print(f"[ERRO] Falha ao buscar cadastro: {e}")

    # --- BLOCO 2: LOCALIZAÇÃO DOS 3 ÚLTIMOS TRIMESTRES ---
    # As demonstrações contábeis são organizadas por pastas de Anos.
    print("[REQUISICAO] Analisando diretorio de demonstracoes contabeis para localizar ultimos trimestres")
    url_base = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
    
    # Captura o HTML da página principal das demonstrações contábeis.
    root_html = session.get(url_base, verify=False).text
    soup_root = BeautifulSoup(root_html, 'html.parser')
    
    # [EXPLICAÇÃO]: Lógica de Ordenação de Anos.
    # O código pega todos os links que são números (anos), transforma em lista e ordena do maior para o menor (reverse=True).
    # Isso garante que sempre começaremos a procurar pelos dados de 2024, 2023, e assim por diante.
    anos = sorted([a.get('href').replace('/', '') for a in soup_root.find_all('a') if a.get('href').replace('/', '').isdigit()], reverse=True)
    
    arquivos_links = []
    # Percorre as pastas dos anos até encontrar links para os 3 trimestres mais recentes.
    for ano in anos:
        if len(arquivos_links) >= 3: break
        url_ano = urljoin(url_base, f"{ano}/")
        soup_ano = BeautifulSoup(session.get(url_ano, verify=False).text, 'html.parser')
        
        # Pega os links dos arquivos .zip dentro da pasta do ano e os ordena para pegar os trimestres finais primeiro.
        zips = sorted([urljoin(url_ano, a.get('href')) for a in soup_ano.find_all('a') if '.zip' in a.get('href').lower()], reverse=True)
        for z in zips:
            if len(arquivos_links) < 3: arquivos_links.append(z)

    # --- BLOCO 3: DOWNLOAD VIA STREAM E EXTRAÇÃO ---
    # Aqui ocorre o download real dos arquivos pesados localizados no bloco anterior.
    for i, link in enumerate(arquivos_links):
        nome = link.split('/')[-1] # Extrai o nome do arquivo da URL (ex: 4T2023.zip)
        dest = os.path.join(path_raw, nome)
        print(f"[REQUISICAO] Baixando arquivo {i+1} de 3: {nome}")
        
        try:
            # [EXPLICAÇÃO]: Uso do 'stream=True'.
            # O parâmetro 'stream' mantém a conexão aberta enquanto processamos o conteúdo em partes.
            with session.get(link, verify=False, stream=True, timeout=60) as r:
                r.raise_for_status() # Verifica se o download não deu erro (como erro 404 ou 500)
                with open(dest, 'wb') as f:
                    # 'iter_content' lê o arquivo em blocos de 1 Megabyte (1024*1024 bytes).
                    for chunk in r.iter_content(chunk_size=1024*1024): 
                        if chunk:
                            f.write(chunk)
            
            # [EXPLICAÇÃO]: Extração automática.
            # Após o download completo do ZIP, o módulo 'zipfile' extrai os arquivos CSV de dentro dele.
            print(f"[REQUISICAO] Extraindo conteudo do arquivo: {nome}")
            with zipfile.ZipFile(dest, 'r') as z:
                z.extractall(path_raw)
                
        except Exception as e:
            print(f"[AVISO] Falha no download de {nome}: {e}")

    print("[REQUISICAO] Processo de requisicao e extracao finalizado")

# Ponto de entrada do script: garante que a função 'baixar_tudo' só rode se o arquivo for executado diretamente.
if __name__ == "__main__":
    baixar_tudo()