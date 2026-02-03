import pandas as pd
import re
import unicodedata

def limpar_texto(texto):
    if not isinstance(texto, str): return str(texto)
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

def extrair_id_limpo(valor):
    if pd.isna(valor) or valor == "": return ""
    # Remove notação científica e pontos decimais
    s = str(valor).upper().split('E')[0].replace('.0', '')
    return re.sub(r'[^0-9]', '', s)

def formatar_valor_br(valor):
    try:
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        num = float(s)
        return f"R$ {num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def gerar_join():
    print("\n[JOIN] Gerando relatorio com CNPJ limpo para visualizacao...")
    
    # Carga dos arquivos
    desp = pd.read_csv("dados/processados/consolidado_despesas.csv", sep=';', dtype=str)
    cad = pd.read_csv("dados/raw/operadoras_ativas.csv", sep=None, engine='python', encoding='latin-1', skiprows=3, dtype=str)

    # Identificando colunas (limpando nomes)
    desp.columns = [limpar_texto(c) for c in desp.columns]
    cad.columns = [limpar_texto(c) for c in cad.columns]
    
    col_id_desp = desp.columns[0]
    col_valor_desp = desp.columns[-1]

    # Normalizando chaves para o Match
    desp['KEY_JOIN'] = desp[col_id_desp].apply(extrair_id_limpo).str.lstrip('0')
    cad['KEY_JOIN_REG'] = cad[cad.columns[0]].apply(extrair_id_limpo).str.lstrip('0')
    cad['KEY_JOIN_CNPJ'] = cad[cad.columns[1]].apply(extrair_id_limpo).str.lstrip('0')

    # Join
    df_final = pd.merge(desp, cad, left_on='KEY_JOIN', right_on='KEY_JOIN_REG', how='inner')
    if df_final.empty:
        df_final = pd.merge(desp, cad, left_on='KEY_JOIN', right_on='KEY_JOIN_CNPJ', how='inner')

    if not df_final.empty:
        df_relatorio = pd.DataFrame()
        
        # FORMATAÇÃO: Usando a fórmula ="VALOR" para o Excel esconder a aspa e manter o zero
        # O resultado visual será: 42465310000121 (exatamente como na imagem)
        cnpj_numeros = df_final[cad.columns[1]].apply(lambda x: extrair_id_limpo(x).zfill(14))
        df_relatorio['CNPJ'] = '="' + cnpj_numeros + '"'
        
        df_relatorio['RazaoSocial'] = df_final[cad.columns[2]].apply(limpar_texto)
        df_relatorio['RegistroANS'] = df_final[cad.columns[0]].apply(extrair_id_limpo)
        df_relatorio['Modalidade'] = df_final[cad.columns[3]].apply(limpar_texto)
        df_relatorio['UF'] = df_final[cad.columns[10]].apply(limpar_texto)
        df_relatorio['ValorDespesas'] = df_final[col_valor_desp].apply(formatar_valor_br)

        # Salvando
        df_relatorio.to_csv("dados/processados/relatorio_enriquecido.csv", index=False, sep=';', encoding='utf-8-sig')
        print(f"[SUCESSO] Relatorio gerado com CNPJ formatado sem a aspa visivel!")
    else:
        print("[ERRO] Falha no cruzamento.")

if __name__ == "__main__":
    gerar_join()