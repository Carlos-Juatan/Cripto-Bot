import pandas as pd
import os 
import time 
import json
from binance.client import Client, BinanceAPIException 
from binance.enums import *

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('KEY_BINANCE')
secret_key = os.getenv('SECRET_BINANCE')

cliente_binance = Client(api_key, secret_key)

codigo_operado = os.getenv('codigo_operado')
ativo_operado = os.getenv('ativo_operado')
quantidade = os.getenv('quantidade')
periodo_candle = Client.KLINE_INTERVAL_1HOUR

valor_ativo_operado = cliente_binance.get_symbol_ticker(symbol=codigo_operado)

def atualizar_variaveis():
    load_dotenv()
    global codigo_operado, ativo_operado, quantidade, config, posicao_atual, time_to_sleep
    codigo_operado = os.getenv('codigo_operado')
    ativo_operado = os.getenv('ativo_operado')
    quantidade = os.getenv('quantidade')

    # Abrindo o arquivo JSON
    with open('config.json', 'r') as f:
        config = json.load(f)

    posicao_atual = config['posicao_atual']
    time_to_sleep = int(config['time_to_sleep']) * 60 # 60 segundos vezes xx minutos

def pegando_dados(codigo, intervalo):

    candles = cliente_binance.get_klines(symbol = codigo, interval = intervalo, limit = 1000)
    precos = pd.DataFrame(candles)
    precos.columns = ["tempo_abertura", "abertura", "maxima", "minima", "fechamento", "volume", "tempo_fechamento", "moedas_negociadas", "numero_trades",
                    "volume_ativo_base_compra", "volume_ativo_cotação", "-"]
    precos = precos[["fechamento", "tempo_fechamento"]]
    precos["tempo_fechamento"] = pd.to_datetime(precos["tempo_fechamento"], unit = "ms").dt.tz_localize("UTC")
    precos["tempo_fechamento"] = precos["tempo_fechamento"].dt.tz_convert("America/Sao_Paulo")

    return precos


def estrategia_trade(dados, codigo_ativo, ativo_operado, quantidade, posicao):

    dados["media_rapida"] = dados["fechamento"].rolling(window = 7).mean()
    dados["media_devagar"] = dados["fechamento"].rolling(window = 40).mean()

    ultima_media_rapida = dados["media_rapida"].iloc[-1]
    ultima_media_devagar = dados["media_devagar"].iloc[-1]

    # Calculando a diferença entre as médias
    diferenca = ultima_media_rapida - ultima_media_devagar

    # Determinando a tendência
    if diferenca > 0:
        tendencia = "subindo"
    elif diferenca < 0:
        tendencia = "caindo"
    else:
        tendencia = "estável"

    print(f"Últimas Médias - Rápida: {int(ultima_media_rapida*1000)/1000} | - Devagar: {int(ultima_media_devagar*1000)/1000} | Diferença: {diferenca:.2f} | Tendência: {tendencia}")

    conta = cliente_binance.get_account()

    for ativo in conta["balances"]:

        if ativo["asset"] == ativo_operado:

            quantidade_atual = float(ativo["free"])

    if ultima_media_rapida > ultima_media_devagar:

        if posicao == False:
            
            #codigo para comprar o ativo ###################################################################
            try:
                ticker = cliente_binance.get_symbol_ticker(symbol=codigo_operado)
                valor_ativo_operado = ticker['price']
                stop_price = float(valor_ativo_operado) * 0.95
                order = cliente_binance.create_order(symbol = codigo_ativo, side = SIDE_BUY, type = ORDER_TYPE_STOP_LOSS, quantity = quantidade, stopPrice = stop_price)
            except BinanceAPIException as e:
                valor_ativo_operado = 0
                print(f"Erro ao obter o preço do ativo: {e}")
                # Logar o erro
            
            print(f'COMPROU O ATIVO A {valor_ativo_operado}')

            posicao = True

    elif ultima_media_rapida < ultima_media_devagar:

        if posicao == True:
            
            #codigo para vender o ativo ###################################################################
            try:
                ticker = cliente_binance.get_symbol_ticker(symbol=codigo_operado)
                valor_ativo_operado = ticker['price']
                stop_price = float(valor_ativo_operado) * 1.05
                order = cliente_binance.create_order(symbol = codigo_ativo, side = SIDE_SELL, type = ORDER_TYPE_MARKET, quantity = int(quantidade_atual * 1000)/1000, stopPrice = stop_price)
            except BinanceAPIException as e:
                valor_ativo_operado = 0
                print(f"Erro ao obter o preço do ativo: {e}")
                # Logar o erro
            
            print(f'VENDER O ATIVO A {valor_ativo_operado}')

            posicao = False

    return posicao

while True:
    atualizar_variaveis()

    dados_atualizados = pegando_dados(codigo=codigo_operado, intervalo=periodo_candle)

    # Modificar o valor da chave 'nome'
    config['posicao_atual'] = estrategia_trade(dados_atualizados, codigo_ativo=codigo_operado, ativo_operado=ativo_operado, quantidade=quantidade, posicao=posicao_atual)

    # Gravar as alterações
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    time.sleep(time_to_sleep)
