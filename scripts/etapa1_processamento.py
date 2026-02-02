import pandas as pd
import glob, os, unicodedata

def limpar_nomes(t):
    n = "".join([c for c in unicodedata.normalize('NFKD', str(t)) if not unicodedata.combining(c)])
    return n.upper().replace('Ç', 'C').strip()

def processar():
    print("\n[PROCESSANDO] Formatando despesas e limpando valores...")
    arquivos = glob.glob("dados/raw/*.csv")
    lista = []
    
    for arq in arquivos:
        if "operadoras" in arq.lower(): continue
        print(f"[LENDO] {os.path.basename(arq)}...")
        df = pd.read_csv(arq, sep=None, engine='python', encoding='latin-1')
        df.columns = [limpar_nomes(c) for c in df.columns]
        
        col_desc = 'DS_CONTA_CONTABIL' if 'DS_CONTA_CONTABIL' in df.columns else 'DESCRICAO'
        df = df[df[col_desc].str.contains('EVENTOS|SINISTROS', na=False, case=False)]
        
        col_valor = 'VL_SALDO_FINAL' if 'VL_SALDO_FINAL' in df.columns else 'VALOR'
        col_ans = 'REG_ANS' if 'REG_ANS' in df.columns else 'ID_REGISTRO_ANS'
        
        # Converte para número para processamento
        v_num = pd.to_numeric(df[col_valor].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        
        temp = pd.DataFrame({
            'REGISTRO_ANS': df[col_ans].astype(str).str.replace(r'\.0$', '', regex=True),
            'VALOR': v_num.apply(lambda x: f"R$ {int(round(x)):,}".replace(',', '.'))
        })
        lista.append(temp)
    
    print("[SALVANDO] Gerando consolidado_despesas.csv (Apenas Moeda)...")
    pd.concat(lista).to_csv("dados/processados/consolidado_despesas.csv", index=False, sep=';', encoding='utf-8-sig')
    print("✅ [OK] Arquivo de despesas limpo!")

if __name__ == "__main__":
    processar()