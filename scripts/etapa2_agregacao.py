import pandas as pd
import os

def encontrar_coluna(df, possiveis_nomes):
    for nome in possiveis_nomes:
        if nome.upper() in [c.upper() for c in df.columns]:
            # Retorna o nome exato como está no DF (ex: se o DF tem 'uf', retorna 'uf')
            return [c for c in df.columns if c.upper() == nome.upper()][0]
    return None

def agregar_dados():
    print("--- Etapa 2.3: Agregação e Estatísticas ---")
    caminho_input = "dados/processados/relatorio_final.csv"
    caminho_output = "dados/processados/despesas_agregadas.csv"

    if not os.path.exists(caminho_input):
        print(f"❌ Arquivo {caminho_input} não encontrado!")
        return

    df = pd.read_csv(caminho_input)

    # Identifica os nomes reais das colunas no CSV (Resiliência)
    col_razao = encontrar_coluna(df, ['RAZAOSOCIAL', 'RAZAO_SOCIAL', 'NM_OPERADORA'])
    col_uf = encontrar_coluna(df, ['UF', 'ESTADO'])
    col_valor = encontrar_coluna(df, ['VALORDESPESAS', 'VALOR_DESPESA', 'VL_SALDO_FINAL'])

    if not col_razao or not col_uf or not col_valor:
        print(f"❌ Erro: Colunas necessárias não encontradas. Colunas no arquivo: {list(df.columns)}")
        return

    print(f"Agrupando por {col_razao} e {col_uf}...")

    # Requisito 2.3: Agrupar e calcular Soma, Média e Desvio Padrão
    agregado = df.groupby([col_razao, col_uf]).agg({
        col_valor: ['sum', 'mean', 'std']
    }).reset_index()

    # Renomear colunas para ficar limpo
    agregado.columns = ['RazaoSocial', 'UF', 'TotalDespesas', 'MediaDespesas', 'DesvioPadraoDespesas']

    # Preencher Desvio Padrão nulo com 0 (acontece quando só tem 1 registro para a operadora)
    agregado['DesvioPadraoDespesas'] = agregado['DesvioPadraoDespesas'].fillna(0)

    # Ordenar por valor total (maior para menor) conforme pedido no PDF
    agregado = agregado.sort_values(by='TotalDespesas', ascending=False)

    # Salvar resultado
    agregado.to_csv(caminho_output, index=False, encoding='utf-8')
    print(f"✅ Sucesso! Arquivo gerado: {caminho_output}")
    print(f"📊 Total de grupos: {len(agregado)}")

if __name__ == "__main__":
    agregar_dados()