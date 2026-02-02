import pandas as pd
import os

def agregar():
    """
    ETAPA 2.2: Agregação e indicadores.
    Pensamento Crítico: Tratamento de desvio padrão nulo para operadoras com um único registro.
    """
    print("\n[AGREGANDO] Gerando estatísticas finais...")
    path_desp = "dados/processados/consolidado_despesas.csv"
    path_cad = "dados/processados/operadoras_limpas.csv"
    
    if not os.path.exists(path_desp): return

    df_desp = pd.read_csv(path_desp, sep=';', dtype=str)
    cad = pd.read_csv(path_cad, sep=';', dtype=str)

    # Reverte R$ para cálculo
    df_desp['V_NUM'] = df_desp['VALOR'].str.replace('R$ ', '', regex=False).str.replace('.', '', regex=False).astype(float)
    
    # Merge ignorando quem não tem cadastro (Dados Vazios)
    df = pd.merge(df_desp, cad, on='REGISTRO_ANS', how='left').dropna(subset=['RAZAO_SOCIAL'])

    # Agrupamento
    resumo = df.groupby(['RAZAO_SOCIAL', 'UF']).agg(
        TOTAL_GASTO=('V_NUM', 'sum'),
        MEDIA_GASTO=('V_NUM', 'mean'),
        DESVIO_PADRAO=('V_NUM', 'std')
    ).reset_index()

    # Tratamento para registro único: Desvio padrão de 1 valor é indefinido (NaN). 
    # Definimos como 0 para clareza do relatório.
    resumo['DESVIO_PADRAO'] = resumo['DESVIO_PADRAO'].fillna(0)

    # Classificação de Perfil
    def classificar(row):
        if row['MEDIA_GASTO'] == 0: return "SEM DADOS"
        variancia = row['DESVIO_PADRAO'] / row['MEDIA_GASTO']
        return "ALTA VARIACAO" if variancia > 0.5 else "GASTO ESTAVEL"

    resumo['ANALISE_PERFIL'] = resumo.apply(classificar, axis=1)

    # Ordenação e Formatação
    resumo = resumo.sort_values(by='TOTAL_GASTO', ascending=False)
    for col in ['TOTAL_GASTO', 'MEDIA_GASTO', 'DESVIO_PADRAO']:
        resumo[col] = resumo[col].apply(lambda x: f"R$ {int(round(x)):,}".replace(',', '.'))

    resumo.to_csv("dados/processados/consolidado_ans_final.csv", index=False, sep=';', encoding='utf-8-sig')
    print("✅ [SUCESSO] Relatório com análise de variância concluído!")

if __name__ == "__main__":
    agregar()