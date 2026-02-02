import pandas as pd
import os

def agregar():
    print("\n[ANALISE CRITICA] Verificando dados e gerando estatisticas (Requisito 2.2)...")
    path_desp = "dados/processados/consolidado_despesas.csv"
    path_cad = "dados/processados/operadoras_limpas.csv"
    
    if not os.path.exists(path_desp):
        print("❌ [ERRO] Arquivo de despesas nao encontrado!")
        return

    # 1. Leitura dos dados
    df_desp = pd.read_csv(path_desp, sep=';', dtype=str)
    cad = pd.read_csv(path_cad, sep=';', dtype=str)

    # 2. Conversao para numero (Limpando o R$)
    df_desp['V_NUM'] = df_desp['VALOR'].str.replace('R$ ', '', regex=False).str.replace('.', '', regex=False).astype(float)

    # 3. TRATAMENTO DE NEGATIVOS (Requisito de Pensamento Critico do PDF)
    # Valores negativos em despesas operacionais sao inconsistencias que distorcem a media
    df_desp = df_desp[df_desp['V_NUM'] > 0]

    # 4. JOIN: Unindo com cadastro (Ignora quem nao tem Razao Social)
    df = pd.merge(df_desp, cad, on='REGISTRO_ANS', how='left').dropna(subset=['RAZAO_SOCIAL'])

    # 5. CALCULOS ESTATISTICOS
    resumo = df.groupby(['RAZAO_SOCIAL', 'UF']).agg(
        TOTAL_GASTO=('V_NUM', 'sum'),
        MEDIA_GASTO=('V_NUM', 'mean'),
        DESVIO_PADRAO=('V_NUM', 'std')
    ).reset_index()

    # Tratando o Desvio Padrao de quem tem apenas 1 registro (NaN -> 0)
    resumo['DESVIO_PADRAO'] = resumo['DESVIO_PADRAO'].fillna(0)

    # 6. ANALISE DE PERFIL (Diferencial de Interpretacao de Dados)
    def classificar_perfil(row):
        if row['MEDIA_GASTO'] == 0: return "SEM DADOS"
        # Se o desvio padrao for maior que 50% da media, o gasto e muito instavel
        variancia = row['DESVIO_PADRAO'] / row['MEDIA_GASTO']
        if variancia > 0.5: return "ALTA VARIACAO"
        return "GASTO ESTAVEL"

    print("[PERFIL] Aplicando analise de variancia nos gastos...")
    resumo['ANALISE_PERFIL'] = resumo.apply(classificar_perfil, axis=1)

    # Ordenacao por maior gasto
    resumo = resumo.sort_values(by='TOTAL_GASTO', ascending=False)

    # 7. FORMATACAO FINAL
    print("[FORMATANDO] Convertendo para padrao monetario R$...")
    for col in ['TOTAL_GASTO', 'MEDIA_GASTO', 'DESVIO_PADRAO']:
        resumo[col] = resumo[col].apply(lambda x: f"R$ {int(round(x)):,}".replace(',', '.'))

    resumo.to_csv("dados/processados/consolidado_ans_final.csv", index=False, sep=';', encoding='utf-8-sig')
    print("✅ [SUCESSO] Relatorio com Desvio Padrao e Analise de Perfil concluido!")

if __name__ == "__main__":
    agregar()