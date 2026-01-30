import pandas as pd
import os
import glob
import zipfile

def validar_cnpj(cnpj):
    cnpj = "".join(filter(str.isdigit, str(cnpj)))
    if len(cnpj) != 14 or len(set(cnpj)) == 1: return False
    def calcular_digito(cnpj, pesos):
        soma = sum(int(a) * b for a, b in zip(cnpj, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]; pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    try:
        if int(cnpj[12]) != calcular_digito(cnpj[:12], pesos1): return False
        if int(cnpj[13]) != calcular_digito(cnpj[:13], pesos2): return False
    except: return False
    return True

def carregar_csv_com_limpeza(caminho):
    for pular in range(5):
        try:
            df = pd.read_csv(caminho, sep=None, engine='python', encoding='latin-1', skiprows=pular, on_bad_lines='skip')
            df.columns = df.columns.str.upper().str.strip()
            # Adicionei 'REG_ANS' que é o que apareceu no seu erro
            if any(c in df.columns for c in ['VL_SALDO_FINAL', 'REG_ANS', 'ID_REGISTRO_ANS']):
                return df
        except: continue
    return None

def encontrar_coluna(df, possiveis_nomes):
    for nome in possiveis_nomes:
        if nome in df.columns: return nome
    return None

def processar_dados():
    print("--- Etapa 1.3 & 2.1: Processamento Ajustado (Filtro de Despesas) ---")
    arquivos = glob.glob("dados/raw/*.csv")
    lista_df = []
    
    for arq in arquivos:
        if any(x in arq.lower() for x in ["relatorio_cadop", "operadoras", "limpas"]): continue
        
        print(f"Processando: {os.path.basename(arq)}")
        df = carregar_csv_com_limpeza(arq)
        
        if df is not None:
            # Mapeamento com os nomes que apareceram no seu terminal
            col_valor = encontrar_coluna(df, ['VL_SALDO_FINAL', 'VALOR'])
            col_ans = encontrar_coluna(df, ['REG_ANS', 'ID_REGISTRO_ANS', 'ID_OPERADORA'])
            col_desc = encontrar_coluna(df, ['DESCRICAO', 'DS_CONTA_CONTABIL'])
            
            if col_valor and col_ans:
                # REQUISITO 1.2: Filtrar apenas Despesas com Eventos/Sinistros
                # Geralmente são contas que começam com '4' ou tem 'EVENTOS'/'SINISTROS' no nome
                if col_desc:
                    df = df[df[col_desc].str.contains('EVENTOS|SINISTROS|DESPESA', na=False, case=False)]

                # Limpeza numérica
                df[col_valor] = df[col_valor].astype(str).str.replace(',', '.')
                df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce')
                df = df.dropna(subset=[col_valor])
                df = df[df[col_valor] > 0]

                # Validação de CNPJ (O REG_ANS as vezes contém o CNPJ ou código, validamos se for 14 dígitos)
                df['CNPJ_VALIDO'] = df[col_ans].apply(lambda x: validar_cnpj(x) if len(str(x)) >= 14 else True)

                temp_df = pd.DataFrame({
                    'CNPJ': df[col_ans],
                    'RazaoSocial': df.get('NM_OPERADORA', 'OPERADORA DESCONHECIDA'),
                    'Trimestre': os.path.basename(arq)[:2].upper(),
                    'Ano': 2025,
                    'ValorDespesas': df[col_valor]
                })
                lista_df.append(temp_df)
                print(f"   ✅ {len(temp_df)} linhas de despesas identificadas.")
            else:
                print(f"   ⚠️ Colunas essenciais não encontradas. Colunas: {list(df.columns)}")
        else:
            print(f"   ❌ Erro na leitura do arquivo.")

    if lista_df:
        consolidado = pd.concat(lista_df).drop_duplicates()
        os.makedirs("dados/processados/", exist_ok=True)
        csv_path = "dados/processados/consolidado_despesas.csv"
        consolidado.to_csv(csv_path, index=False, encoding='utf-8')
        
        with zipfile.ZipFile("dados/processados/consolidado_despesas.zip", 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(csv_path, "consolidado_despesas.csv")
        print(f"\n🏆 SUCESSO: {len(consolidado)} registros consolidados em CSV e ZIP.")
    else:
        print("\n⚠️ Nenhum dado processado. Verifique se os CSVs contêm a coluna VL_SALDO_FINAL.")

if __name__ == "__main__":
    processar_dados()