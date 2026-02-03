import pandas as pd
import os

def formatar_moeda_br(valor):
    """
    FUNÇÃO DE FORMATAÇÃO:
    OBJETIVO: Converter números decimais no padrão R$ 1.234,56.
    
    EXPLICAÇÃO DO PROCESSO:
    O Python, por padrão, usa o ponto como separador decimal. Esta função 
    utiliza uma técnica de substituição em três etapas (X) para inverter 
    o padrão americano para o padrão brasileiro de moeda.
    """
    if pd.isna(valor): return "R$ 0,00"
    # Formata com milhar em vírgula e decimal em ponto, depois inverte para padrão BR
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def agregar():
    """
    ETAPA 2.3: Agregação de Dados.
    OBJETIVO: Calcular o Total, a Média Trimestral e o Desvio Padrão das despesas.
    
    CRITÉRIO DO TESTE: Agrupar os resultados por Operadora e por Estado (UF).
    """
    print("\n[AGREGACAO] Gerando estatisticas...")
    path_input = "dados/processados/relatorio_enriquecido.csv"
    
    # [VERIFICAÇÃO]: Garante que o relatório da etapa anterior existe antes de tentar ler.
    if not os.path.exists(path_input):
        print(f"[ERRO] Arquivo {path_input} nao encontrado.")
        return

    # --- BLOCO 1: CARGA E PREPARAÇÃO ---
    # Carregamos como string para evitar que o Pandas tente adivinhar tipos de dados incorretamente.
    df = pd.read_csv(path_input, sep=';', dtype=str)

    # --- BLOCO 2: CONVERSÃO DE TIPOS (CASTING) ---
    # Para fazer cálculos matemáticos, precisamos remover o "R$", os pontos de milhar 
    # e converter a vírgula decimal em ponto, transformando o texto em um número Float.
    print("[AGREGACAO] Convertendo valores para calculo...")
    df['V_NUM'] = (df['ValorDespesas']
                   .str.replace('R$', '', regex=False)
                   .str.replace('.', '', regex=False)
                   .str.replace(',', '.', regex=False)
                   .str.strip()
                   .astype(float))

    # --- BLOCO 3: PROCESSAMENTO ESTATÍSTICO ---
    # O comando .groupby agrupa todas as linhas da mesma operadora no mesmo estado.
    # O comando .agg executa os cálculos de soma, média e desvio padrão simultaneamente.
    print("[AGREGACAO] Agrupando por Operadora e UF...")
    resumo = df.groupby(['RazaoSocial', 'UF']).agg(
        Total_Despesas=('V_NUM', 'sum'),
        Media_Trimestral=('V_NUM', 'mean'),
        Desvio_Padrao=('V_NUM', 'std')
    ).reset_index()

    # --- BLOCO 4: TRATAMENTO DE VALORES NULOS ---
    # Se uma operadora tiver apenas um registro de despesa, o Desvio Padrão será 'NaN' (nulo).
    # Substituímos por 0 para manter a integridade visual do relatório.
    resumo['Desvio_Padrao'] = resumo['Desvio_Padrao'].fillna(0)

    # --- BLOCO 5: ORDENAÇÃO ---
    # Ordena o DataFrame para que as operadoras com maiores despesas apareçam no topo.
    resumo = resumo.sort_values(by='Total_Despesas', ascending=False)

    # --- BLOCO 6: RE-FORMATAÇÃO PARA APRESENTAÇÃO ---
    # Agora que os cálculos terminaram, voltamos os números para o formato de moeda R$.
    print("[AGREGACAO] Aplicando formato...")
    for col in ['Total_Despesas', 'Media_Trimestral', 'Desvio_Padrao']:
        resumo[col] = resumo[col].apply(formatar_moeda_br)

    # --- BLOCO 7: EXPORTAÇÃO ---
    # Gera o arquivo final que consolida os indicadores de performance do teste.
    output_name = "dados/processados/despesas_agregadas.csv"
    resumo.to_csv(output_name, index=False, sep=';', encoding='utf-8-sig')
    
    print(f"[SUCESSO] Arquivo '{output_name}' gerado com sucesso.")

if __name__ == "__main__":
    agregar()