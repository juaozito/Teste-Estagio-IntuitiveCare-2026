import pandas as pd
import os

def executar_join():
    print("--- Etapa 2.2: Join Ultra-Resiliente ---")
    arq_despesas = "dados/processados/consolidado_despesas.csv"
    arq_cadastro = "dados/processados/operadoras_limpas.csv"
    saida = "dados/processados/relatorio_final.csv"

    if not os.path.exists(arq_despesas) or not os.path.exists(arq_cadastro):
        print("❌ Arquivos não encontrados!")
        return

    df_desp = pd.read_csv(arq_despesas)
    df_cad = pd.read_csv(arq_cadastro)

    # 1. Normaliza nomes de colunas
    df_desp.columns = df_desp.columns.str.upper().str.strip()
    df_cad.columns = df_cad.columns.str.upper().str.strip()

    # 2. LIMPEZA CRÍTICA: Transforma em string, remove espaços e ZEROS À ESQUERDA
    # Isso garante que '04123' vire '4123' em ambos os lados
    def limpar_codigo(serie):
        return serie.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lstrip('0')

    df_desp['CHAVE_JOIN'] = limpar_codigo(df_desp['CNPJ'])
    
    # Identifica a coluna de registro no cadastro (pode ser REGISTRO_ANS ou a primeira coluna)
    col_reg_cad = 'REGISTRO_ANS' if 'REGISTRO_ANS' in df_cad.columns else df_cad.columns[0]
    df_cad['CHAVE_JOIN'] = limpar_codigo(df_cad[col_reg_cad])

    print(f"Cruzando dados... Chave de exemplo Despesas: {df_desp['CHAVE_JOIN'].iloc[0]}")

    # 3. Executa o merge pela nova CHAVE_JOIN
    df_final = pd.merge(df_desp, df_cad, on='CHAVE_JOIN', how='left', suffixes=('', '_CAD'))

    # 4. TRATAMENTO DA RAZÃO SOCIAL:
    # Se encontrou no cadastro (RAZAO_SOCIAL_CAD), usa. Se não, tenta manter a original.
    col_nome_cad = 'RAZAO_SOCIAL' if 'RAZAO_SOCIAL' in df_cad.columns else None
    
    if col_nome_cad:
        # Preenche onde estava "OPERADORA DESCONHECIDA" com o nome real do cadastro
        df_final['RAZAOSOCIAL'] = df_final[col_nome_cad].fillna(df_final['RAZAOSOCIAL'])

    # 5. Salva
    df_final.to_csv(saida, index=False, encoding='utf-8')
    
    # Validação rápida para você ver no terminal
    total = len(df_final)
    desconhecidas = len(df_final[df_final['RAZAOSOCIAL'] == 'OPERADORA DESCONHECIDA'])
    print(f"✅ Relatório Final Gerado!")
    print(f"📊 Total de registros: {total}")
    print(f"⚠️ Ainda restam {desconhecidas} linhas sem nome (sem correspondência no cadastro).")

if __name__ == "__main__":
    executar_join()