import pandas as pd
import re
import unicodedata

# --- BLOCO DE FUNÇÕES AUXILIARES PARA PADRONIZAÇÃO ---

def limpar_texto(texto):
    """
    OBJETIVO: Normalizar cabeçalhos e textos.
    Remove acentos, converte para maiúsculas e remove espaços extras.
    Isso evita que colunas não sejam encontradas por causa de uma letra minúscula ou um acento.
    """
    if not isinstance(texto, str): return str(texto)
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

def extrair_id_limpo(valor):
    """
    OBJETIVO: Limpar IDs (CNPJ ou Registro ANS).
    - Trata o erro comum do Excel/Pandas de transformar números longos em notação científica (ex: 4E10).
    - Remove o '.0' que aparece quando números são lidos como decimais (floats).
    - Deixa apenas os dígitos numéricos.
    """
    if pd.isna(valor) or valor == "": return ""
    # Remove notação científica e pontos decimais residuais
    s = str(valor).upper().split('E')[0].replace('.0', '')
    return re.sub(r'[^0-9]', '', s)

def formatar_valor_br(valor):
    """
    OBJETIVO: Transformar números em formato de moeda Brasileira (R$).
    - Converte o valor para float.
    - Aplica o formato R$ 1.234,56 utilizando uma técnica de substituição temporária 
      para trocar pontos por vírgulas conforme o padrão ABNT.
    """
    try:
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        num = float(s)
        return f"R$ {num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def gerar_join():
    """
    OBJETIVO PRINCIPAL: Realizar o 'Merge' (Join) entre as despesas e o cadastro.
    Esta etapa é fundamental para responder à pergunta: 'A qual operadora pertence esta despesa?'.
    """
    print("\n[JOIN] Gerando relatorio...")
    
    # --- BLOCO: CARGA DOS DADOS ---
    # Lê o consolidado gerado na Etapa 1 e o cadastro bruto baixado originalmente.
    desp = pd.read_csv("dados/processados/consolidado_despesas.csv", sep=';', dtype=str)
    cad = pd.read_csv("dados/raw/operadoras_ativas.csv", sep=None, engine='python', encoding='latin-1', skiprows=3, dtype=str)

    # Aplica a limpeza nos nomes das colunas de ambos os arquivos para garantir compatibilidade.
    desp.columns = [limpar_texto(c) for c in desp.columns]
    cad.columns = [limpar_texto(c) for c in cad.columns]
    
    # Identifica dinamicamente as colunas de ID e Valor (primeira e última colunas).
    col_id_desp = desp.columns[0]
    col_valor_desp = desp.columns[-1]

    # --- BLOCO: NORMALIZAÇÃO DAS CHAVES DE MATCH ---
    # [TÉCNICA]: Removemos zeros à esquerda (.lstrip('0')) de ambos os lados do Join.
    # Isso garante que o registro '00123' encontre o registro '123'.
    desp['KEY_JOIN'] = desp[col_id_desp].apply(extrair_id_limpo).str.lstrip('0')
    cad['KEY_JOIN_REG'] = cad[cad.columns[0]].apply(extrair_id_limpo).str.lstrip('0')
    cad['KEY_JOIN_CNPJ'] = cad[cad.columns[1]].apply(extrair_id_limpo).str.lstrip('0')

    # --- BLOCO: EXECUÇÃO DO JOIN (PROCV / MERGE) ---
    # Tenta o cruzamento primeiro pelo Registro ANS. 
    # Se não encontrar nada (df_final vazio), tenta cruzar pelo CNPJ.
    df_final = pd.merge(desp, cad, left_on='KEY_JOIN', right_on='KEY_JOIN_REG', how='inner')
    if df_final.empty:
        df_final = pd.merge(desp, cad, left_on='KEY_JOIN', right_on='KEY_JOIN_CNPJ', how='inner')

    # --- BLOCO: CONSTRUÇÃO DO RELATÓRIO FINAL ---
    if not df_final.empty:
        df_relatorio = pd.DataFrame()
        
        # [TRUQUE DE EXCEL]: A construção '="' + valor + '"' é uma fórmula de texto.
        # Quando o Excel abre esse CSV, ele interpreta o valor como texto literal.
        # Resultado: O CNPJ mantém todos os 14 dígitos (incluindo zeros à esquerda) sem mostrar a aspa.
        cnpj_numeros = df_final[cad.columns[1]].apply(lambda x: extrair_id_limpo(x).zfill(14))
        df_relatorio['CNPJ'] = '="' + cnpj_numeros + '"'
        
        # Mapeia as colunas do cadastro original para o nosso novo relatório.
        df_relatorio['RazaoSocial'] = df_final[cad.columns[2]].apply(limpar_texto)
        df_relatorio['RegistroANS'] = df_final[cad.columns[0]].apply(extrair_id_limpo)
        df_relatorio['Modalidade'] = df_final[cad.columns[3]].apply(limpar_texto)
        df_relatorio['UF'] = df_final[cad.columns[10]].apply(limpar_texto)
        
        # Aplica a formatação de moeda brasileira na coluna de valores.
        df_relatorio['ValorDespesas'] = df_final[col_valor_desp].apply(formatar_valor_br)

        # --- BLOCO: SALVAMENTO ---
        # Salva o arquivo final enriquecido na pasta de processados.
        df_relatorio.to_csv("dados/processados/relatorio_enriquecido.csv", index=False, sep=';', encoding='utf-8-sig')
        print(f"[SUCESSO] Relatorio gerado com sucesso.")
    else:
        print("[ERRO] Falha no cruzamento: Nenhuma correspondência encontrada entre despesas e cadastro.")

if __name__ == "__main__":
    gerar_join()