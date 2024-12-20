import pandas as pd
# ... (resto do seu código)

# Criar um DataFrame para armazenar os logs, com "tempo_fechamento" como índice
log_df = pd.DataFrame(columns=['tipo_operacao', 'preco', 'quantidade', 'saldo_antes', 'saldo_depois', 'media_rapida', 'media_devagar'])

# ... (resto do seu código)

def log_operacao(data, tipo_operacao, preco, quantidade, saldo_antes, saldo_depois):
    """
    Função para registrar uma operação em um DataFrame.

    Args:
        data (str): Data e hora da operação.
        tipo_operacao (str): Tipo de operação (compra ou venda).
        preco (float): Preço de execução.
        quantidade (float): Quantidade negociada.
        saldo_antes (float): Saldo antes da operação.
        saldo_depois (float): Saldo depois da operação.
    """

    new_row = pd.DataFrame([[tipo_operacao, preco, quantidade, saldo_antes, saldo_depois]]).T
    new_row.index = pd.to_datetime(data)  # Define o índice como a data e hora
    global log_df
    log_df = pd.concat([log_df, new_row], ignore_index=False)  # Mantém o índice original

# ... (resto do seu código)

# Salvar o DataFrame em um arquivo CSV, mantendo o índice como data e hora
def salvar_log():
    log_df.to_csv('log_operacoes.csv', index=True)