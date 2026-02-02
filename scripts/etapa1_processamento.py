import pandas as pd
import glob, os, unicodedata

def limpar_nomes(t):
    n = "".join([c for c in unicodedata.normalize('NFKD', str(t)) if not unicodedata.combining(c)])
    return n.upper().replace('Ç', 'C').strip()

def processar():
    """
    ETAPA 1.1: Processamento com limpeza de inconsistências.
    Trade-off: Valores negativos/zerados são tratados como 'sujeira' contábil 
    e removidos para não afetar o cálculo da média real de gastos.
    """
    print("\n[PROCESSANDO] Filtrando e limpando despesas...")
    arquivos = glob.glob("dados/raw/*.csv")
    lista = []
    
    for arq in arquivos:
        if "operadoras" in arq.lower(): continue
        df = pd.read_csv(arq, sep=None, engine='python', encoding='latin-1')
        df.columns = [limpar_nomes(c) for c in df.columns]
        
        col_desc = 'DS_CONTA_CONTABIL' if 'DS_CONTA_CONTABIL' in df.columns else 'DESCRICAO'
        df = df[df[col_desc].str.contains('EVENTOS|SINISTROS', na=False, case=False)]
        
        col_valor = 'VL_SALDO_FINAL' if 'VL_SALDO_FINAL' in df.columns else 'VALOR'
        col_ans = 'REG_ANS' if 'REG_ANS' in df.columns else 'ID_REGISTRO_ANS'
        
        # Converte para número
        v_num = pd.to_numeric(df[col_valor].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        
        # --- ANÁLISE CRÍTICA (Pág 10 do PDF) ---
        # Filtramos apenas valores positivos (>0). Negativos costumam ser estornos 
        # e zeros indicam ausência de movimentação real na conta filtrada.
        df_limpo = df[v_num > 0].copy()
        v_num_limpo = v_num[v_num > 0]
        
        temp = pd.DataFrame({
            'REGISTRO_ANS': df_limpo[col_ans].astype(str).str.replace(r'\.0$', '', regex=True),
            'VALOR': v_num_limpo.apply(lambda x: f"R$ {int(round(x)):,}".replace(',', '.'))
        })
        lista.append(temp)
    
    pd.concat(lista).to_csv("dados/processados/consolidado_despesas.csv", index=False, sep=';', encoding='utf-8-sig')
    print("✅ [OK] Consolidado gerado (apenas valores positivos)!")

if __name__ == "__main__":
    processar()