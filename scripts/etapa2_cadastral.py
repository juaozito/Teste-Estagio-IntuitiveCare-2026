import pandas as pd
import unicodedata, re

def limpar_texto_perfeito(texto):
    """
    FUNÇÃO DE TRATAMENTO DE STRING:
    OBJETIVO: Eliminar qualquer caractere que possa causar erro de codificação (encoding) no MySQL.
    
    EXPLICAÇÃO DO TRADE-OFF TÉCNICO:
    - Normalização NFKD: Decompõe caracteres acentuados (ex: 'Ã' vira 'A' + '~'). 
      Isso permite que o script remova apenas o "til" e mantenha a letra 'A'.
    - Por que não usar apenas .replace()? Porque seriam necessários centenas de replaces 
      para cobrir todos os acentos e símbolos possíveis. Esta abordagem é universal.
    """
    if pd.isna(texto): return ""
    
    # Separa o acento da letra base
    nfkd = unicodedata.normalize('NFKD', str(texto))
    
    # Filtra apenas o que não é marca de combinação (acentos)
    texto_limpo = "".join([c for c in nfkd if not unicodedata.combining(c)])
    
    # Tratamento manual para o 'Ç' que às vezes se comporta de forma diferente na normalização
    texto_limpo = texto_limpo.replace('ç', 'c').replace('Ç', 'C')
    
    # [REGULAR EXPRESSION]: Remove tudo o que não for Letra (A-Z), Número (0-9) ou Espaço (\s).
    # O .upper() garante que o banco de dados tenha um padrão visual único.
    texto_limpo = re.sub(r'[^A-Z0-9\s]', '', texto_limpo.upper())
    
    # Remove espaços duplos acidentais no meio do texto e espaços no início/fim
    return " ".join(texto_limpo.split())

def limpar_cad():
    """
    OBJETIVO: Processar o arquivo de Operadoras Ativas baixado da ANS.
    Este arquivo é essencial para validar se as operadoras nas despesas são oficiais.
    """
    print("\n[CADASTRAL] Iniciando limpeza do cadastro de operadoras...")
    
    # Lê o CSV da pasta raw. 
    # skiprow=3: Pula as linhas de cabeçalho administrativo que a ANS coloca no topo do arquivo.
    df = pd.read_csv("dados/raw/operadoras_ativas.csv", sep=None, engine='python', encoding='latin-1', skiprows=3)
    
    # --- BLOCO: PADRONIZAÇÃO DE COLUNAS ---
    # Como os nomes das colunas da ANS podem variar, usamos a posição (índice) delas:
    # df.columns[0] = Registro ANS
    # df.columns[2] = Razão Social
    # df.columns[10] = Unidade Federativa (UF)
    print("[CADASTRAL] Normalizando nomes, UFs e registros ANS...")
    df = df.rename(columns={
        df.columns[0]: 'REGISTRO_ANS', 
        df.columns[2]: 'RAZAO_SOCIAL', 
        df.columns[10]: 'UF'
    })
    
    # Aplica a limpeza de texto nas colunas de nome e estado
    df['RAZAO_SOCIAL'] = df['RAZAO_SOCIAL'].apply(limpar_texto_perfeito)
    df['UF'] = df['UF'].apply(limpar_texto_perfeito)
    
    # [LIMPEZA DE ID]: Garante que o Registro ANS seja puramente numérico.
    # Remove pontos, hífens ou o ".0" que o pandas as vezes adiciona ao ler números.
    df['REGISTRO_ANS'] = df['REGISTRO_ANS'].astype(str).str.replace(r'[^0-9]', '', regex=True)
    
    # --- BLOCO: EXPORTAÇÃO ---
    # Salva apenas as colunas necessárias para o teste na pasta de processados.
    # utf-8-sig: Garante que o arquivo seja lido corretamente em sistemas Windows e Linux.
    df[['REGISTRO_ANS', 'RAZAO_SOCIAL', 'UF']].to_csv(
        "dados/processados/operadoras_limpas.csv", 
        index=False, 
        sep=';', 
        encoding='utf-8-sig'
    )
    print("[CADASTRAL] Cadastro normalizado.")

if __name__ == "__main__":
    limpar_cad()