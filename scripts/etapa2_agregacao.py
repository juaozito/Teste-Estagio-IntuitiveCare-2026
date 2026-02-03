import pandas as pd
import os

def formatar_moeda_br(valor):
    """Formata o número para o padrão monetário brasileiro com R$: R$ 1.234,56"""
    if pd.isna(valor): return "R$ 0,00"
    # Formata com milhar em vírgula e decimal em ponto, depois inverte para padrão BR
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def agregar():
    print("\n[AGREGACAO] Gerando estatisticas com R$ (Tarefa 2.3)")
    path_input = "dados/processados/relatorio_enriquecido.csv"
    
    if not os.path.exists(path_input):
        print(f"[ERRO] Arquivo {path_input} nao encontrado.")
        return

    # 1. Carrega os dados (Usando dtype str para preservar formatos)
    df = pd.read_csv(path_input, sep=';', dtype=str)

    # 2. Conversao para calculo numerico
    print("[AGREGACAO] Convertendo valores para calculo...")
    # Limpa possíveis R$, pontos e troca vírgula por ponto para virar float
    df['V_NUM'] = (df['ValorDespesas']
                   .str.replace('R$', '', regex=False)
                   .str.replace('.', '', regex=False)
                   .str.replace(',', '.', regex=False)
                   .str.strip()
                   .astype(float))

    # 3. Agrupamento (Item 2.3 do PDF)
    print("[AGREGACAO] Agrupando por Operadora e UF...")
    resumo = df.groupby(['RazaoSocial', 'UF']).agg(
        Total_Despesas=('V_NUM', 'sum'),
        Media_Trimestral=('V_NUM', 'mean'),
        Desvio_Padrao=('V_NUM', 'std')
    ).reset_index()

    # 4. Tratamento de Desvio Padrao
    resumo['Desvio_Padrao'] = resumo['Desvio_Padrao'].fillna(0)

    # 5. Ordenacao por valor total (Maior para Menor)
    resumo = resumo.sort_values(by='Total_Despesas', ascending=False)

    # 6. Aplicacao da formatacao com R$
    print("[AGREGACAO] Aplicando R$ e formatacao brasileira...")
    for col in ['Total_Despesas', 'Media_Trimestral', 'Desvio_Padrao']:
        resumo[col] = resumo[col].apply(formatar_moeda_br)

    # 7. Salvamento Final
    output_name = "dados/processados/despesas_agregadas.csv"
    resumo.to_csv(output_name, index=False, sep=';', encoding='utf-8-sig')
    
    print(f"[SUCESSO] Arquivo '{output_name}' gerado com R$.")

if __name__ == "__main__":
    agregar()