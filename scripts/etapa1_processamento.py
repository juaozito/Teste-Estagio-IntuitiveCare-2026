import pandas as pd
import glob, os, unicodedata, re

def limpar_nomes(t):
    """
    FUNÇÃO DE AUXÍLIO: Normalização de Strings.
    - Remove acentos e caracteres especiais de cabeçalhos.
    - Transforma tudo em maiúsculas e remove espaços extras.
    - Isso garante que 'vl_saldo_final' e 'VL_SALDO_FINAL' sejam lidos como a mesma coluna.
    """
    n = "".join([c for c in unicodedata.normalize('NFKD', str(t)) if not unicodedata.combining(c)])
    return n.upper().replace('Ç', 'C').strip()

def extrair_periodo(nome_arq):
    """
    LOGICA DE EXTRAÇÃO POR REGEX:
    Os arquivos da ANS vêm com nomes variados como '1T2023.csv' ou '2023_4T.csv'.
    - Esta função usa Expressões Regulares (re) para capturar o Trimestre (T) e o Ano.
    - Retorna o par (trimestre, ano) para ser usado como coluna no relatório final.
    """
    padrao = re.findall(r'(\d)T(\d{4})|(\d{4})_(\d)T', nome_arq.upper())
    if padrao:
        matches = [m for m in padrao[0] if m]
        if len(matches) == 2:
            trim = matches[0] if len(matches[0]) == 1 else matches[1]
            ano = matches[1] if len(matches[1]) == 4 else matches[0]
            return trim, ano
    return "N/A", "N/A"

def processar():
    """
    ETAPA 1 (CORE): Consolidação e Enriquecimento.
    OBJETIVO: Ler múltiplos arquivos de despesas contábeis e unificá-los, substituindo
    o código Registro ANS pelo CNPJ real de 14 dígitos.
    """
    print("\n[PROCESSAMENTO] Corrigindo 'Bugs'...")
    
    # --- BLOCO 1: CARREGAR DICIONÁRIO DE REFERÊNCIA ---
    # Para evitar carregar o arquivo de cadastro milhares de vezes, criamos um "mapa" em memória.
    path_cad = "dados/raw/operadoras_ativas.csv"
    if not os.path.exists(path_cad):
        print("[ERRO] Cadastro nao encontrado para buscar o CNPJ real.")
        return
    
    # Lê o cadastro usando delimitador automático (sep=None) e trata tudo como String (dtype=str)
    # para não perder os zeros à esquerda do CNPJ ou Registro ANS.
    df_ref = pd.read_csv(path_cad, sep=None, engine='python', encoding='latin-1', skiprows=3, dtype=str)
    
    # [MAPEAMENTO]: Cria dicionários de busca rápida (Key: Registro ANS -> Value: CNPJ/Nome).
    mapa_cnpj = pd.Series(df_ref.iloc[:, 1].values, index=df_ref.iloc[:, 0].values).to_dict()
    mapa_nome = pd.Series(df_ref.iloc[:, 2].values, index=df_ref.iloc[:, 0].values).to_dict()

    # --- BLOCO 2: ITERAÇÃO SOBRE OS ARQUIVOS DE DESPESAS ---
    # Localiza todos os arquivos CSV baixados na etapa de requisição.
    arquivos = glob.glob("dados/raw/*.csv")
    lista = []
    
    for arq in arquivos:
        # Pula o arquivo de operadoras, pois ele serve apenas como referência de nomes/CNPJ.
        if "operadoras" in arq.lower(): continue
        nome_base = os.path.basename(arq)
        print(f"-> Lendo: {nome_base}")
        
        # Identifica a qual trimestre/ano o arquivo pertence através do nome dele.
        trimestre, ano = extrair_periodo(nome_base)
        
        # Lê o CSV contábil. Nota: a ANS usa encoding latin-1.
        df = pd.read_csv(arq, sep=None, engine='python', encoding='latin-1')
        # Aplica a normalização nos nomes das colunas.
        df.columns = [limpar_nomes(c) for c in df.columns]
        
        # --- BLOCO 3: FILTRAGEM E LIMPEZA DOS DADOS ---
        # Conforme o teste, devemos focar em 'EVENTOS' ou 'SINISTROS' (despesas assistenciais).
        col_desc = 'DS_CONTA_CONTABIL' if 'DS_CONTA_CONTABIL' in df.columns else 'DESCRICAO'
        df = df[df[col_desc].str.contains('EVENTOS|SINISTROS', na=False, case=False)]
        
        # Identifica as colunas de valor e identificação da operadora (que variam entre os anos).
        col_valor = 'VL_SALDO_FINAL' if 'VL_SALDO_FINAL' in df.columns else 'VALOR'
        col_ans = 'REG_ANS' if 'REG_ANS' in df.columns else 'ID_REGISTRO_ANS'
        
        # Converte os valores para float, tratando a vírgula decimal brasileira por ponto.
        df[col_valor] = pd.to_numeric(df[col_valor].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        # Filtra apenas registros com despesa real (maior que zero).
        df = df[df[col_valor] > 0].copy()

        # --- BLOCO 4: SUBSTITUIÇÃO E FORMATAÇÃO ---
        # Converte o Registro ANS para string limpa (removendo .0 de floats).
        registro_ans = df[col_ans].astype(str).str.replace(r'\.0$', '', regex=True)
        
        # Busca o CNPJ real no mapa criado no Bloco 1. 
        # zfill(14) garante que o CNPJ tenha sempre 14 caracteres (zeros à esquerda).
        cnpj_real = registro_ans.map(mapa_cnpj).apply(lambda x: str(x).zfill(14) if pd.notna(x) else "00000000000000")
        razao_real = registro_ans.map(mapa_nome).fillna("OPERADORA DESCONHECIDA")

        # Cria o DataFrame temporário com os dados padronizados.
        temp = pd.DataFrame({
            # '="' + valor + '"' é um truque para o Excel não ocultar os zeros à esquerda.
            'CNPJ': '="' + cnpj_real + '"', 
            'RazaoSocial': razao_real,
            'Trimestre': trimestre,
            'Ano': ano,
            # Formatação de moeda: R$ 1.234,56
            'ValorDespesas': df[col_valor].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        })
        lista.append(temp)
    
    # --- BLOCO 5: SALVAMENTO ---
    if lista:
        # Junta todos os trimestres em um único tabelão.
        df_final = pd.concat(lista).drop_duplicates(subset=['CNPJ', 'Trimestre', 'Ano'], keep='first')
        
        # Garante a existência da pasta de saída.
        if not os.path.exists("dados/processados/"): os.makedirs("dados/processados/")
        
        output_csv = "dados/processados/consolidado_despesas.csv"
        # utf-8-sig garante que o Excel abra o arquivo com os caracteres brasileiros corretos.
        df_final.to_csv(output_csv, index=False, sep=';', encoding='utf-8-sig')
        print(f"[SUCESSO] Consolidado.")

if __name__ == "__main__":
    processar()