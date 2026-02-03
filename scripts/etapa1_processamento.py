import pandas as pd
import glob, os, unicodedata, re

def limpar_nomes(t):
    n = "".join([c for c in unicodedata.normalize('NFKD', str(t)) if not unicodedata.combining(c)])
    return n.upper().replace('Ç', 'C').strip()

def extrair_periodo(nome_arq):
    padrao = re.findall(r'(\d)T(\d{4})|(\d{4})_(\d)T', nome_arq.upper())
    if padrao:
        matches = [m for m in padrao[0] if m]
        if len(matches) == 2:
            trim = matches[0] if len(matches[0]) == 1 else matches[1]
            ano = matches[1] if len(matches[1]) == 4 else matches[0]
            return trim, ano
    return "N/A", "N/A"

def processar():
    print("\n[PROCESSAMENTO] Corrigindo CNPJ e RazaoSocial para consolidado...")
    
    # 1. CARREGAR REFERÊNCIA (Para trocar Registro ANS por CNPJ Real)
    path_cad = "dados/raw/operadoras_ativas.csv"
    if not os.path.exists(path_cad):
        print("[ERRO] Cadastro nao encontrado para buscar o CNPJ real.")
        return
    
    df_ref = pd.read_csv(path_cad, sep=None, engine='python', encoding='latin-1', skiprows=3, dtype=str)
    # Criamos mapas: Registro ANS -> CNPJ e Registro ANS -> Razao Social
    mapa_cnpj = pd.Series(df_ref.iloc[:, 1].values, index=df_ref.iloc[:, 0].values).to_dict()
    mapa_nome = pd.Series(df_ref.iloc[:, 2].values, index=df_ref.iloc[:, 0].values).to_dict()

    arquivos = glob.glob("dados/raw/*.csv")
    lista = []
    
    for arq in arquivos:
        if "operadoras" in arq.lower(): continue
        nome_base = os.path.basename(arq)
        print(f"-> Lendo: {nome_base}")
        
        trimestre, ano = extrair_periodo(nome_base)
        df = pd.read_csv(arq, sep=None, engine='python', encoding='latin-1')
        df.columns = [limpar_nomes(c) for c in df.columns]
        
        # Filtro de despesas
        col_desc = 'DS_CONTA_CONTABIL' if 'DS_CONTA_CONTABIL' in df.columns else 'DESCRICAO'
        df = df[df[col_desc].str.contains('EVENTOS|SINISTROS', na=False, case=False)]
        
        col_valor = 'VL_SALDO_FINAL' if 'VL_SALDO_FINAL' in df.columns else 'VALOR'
        col_ans = 'REG_ANS' if 'REG_ANS' in df.columns else 'ID_REGISTRO_ANS'
        
        # Limpeza de valores
        df[col_valor] = pd.to_numeric(df[col_valor].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        df = df[df[col_valor] > 0].copy()

        # 2. SUBSTITUIÇÃO: Registro ANS -> CNPJ de 14 dígitos
        registro_ans = df[col_ans].astype(str).str.replace(r'\.0$', '', regex=True)
        cnpj_real = registro_ans.map(mapa_cnpj).apply(lambda x: str(x).zfill(14) if pd.notna(x) else "00000000000000")
        razao_real = registro_ans.map(mapa_nome).fillna("OPERADORA DESCONHECIDA")

        temp = pd.DataFrame({
            'CNPJ': '="' + cnpj_real + '"', # Formato Excel para preservar os 14 dígitos
            'RazaoSocial': razao_real,
            'Trimestre': trimestre,
            'Ano': ano,
            'ValorDespesas': df[col_valor].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        })
        lista.append(temp)
    
    if lista:
        df_final = pd.concat(lista).drop_duplicates(subset=['CNPJ', 'Trimestre', 'Ano'], keep='first')
        output_csv = "dados/processados/consolidado_despesas.csv"
        df_final.to_csv(output_csv, index=False, sep=';', encoding='utf-8-sig')
        print(f"[SUCESSO] Consolidado agora com CNPJ REAL de 14 digitos!")

if __name__ == "__main__":
    processar()