import pandas as pd
import os 
import time 
from binance.client import Client
from binance.enums import *

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")

cliente_binance = Client(api_key, secret_key)

# symbol_info = cliente_binance.get_symbol_info('BTCUSDT')
# lot_size_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
# min_qty = float(lot_size_filter['minQty'])
# max_qty = float(lot_size_filter['maxQty'])
# step_size = float(lot_size_filter['stepSize'])

# print(lot_size_filter, min_qty, max_qty, step_size)

codigo_operado = "SOLBRL"
ativo_operado = "SOL"
periodo_candle = Client.KLINE_INTERVAL_1HOUR
quantidade = 0.015

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

    print(f"Última Média Rápida: {ultima_media_rapida} | Última Média Devagar: {ultima_media_devagar}")

    conta = cliente_binance.get_account()

    for ativo in conta["balances"]:

        if ativo["asset"] == ativo_operado:

            quantidade_atual = float(ativo["free"])

    if ultima_media_rapida > ultima_media_devagar:

        if posicao == False:

            order = cliente_binance.create_order(symbol = codigo_ativo,
                side = SIDE_BUY,
                type = ORDER_TYPE_MARKET,
                quantity = quantidade
                )
            
            
            print("COMPROU O ATIVO")

            posicao = True

    elif ultima_media_rapida < ultima_media_devagar:

        if posicao == True:

            order = cliente_binance.create_order(symbol = codigo_ativo,
                side = SIDE_SELL,
                type = ORDER_TYPE_MARKET,
                quantity = int(quantidade_atual * 1000)/1000)
            
            print("VENDER O ATIVO")

            posicao = False

    return posicao

posicao_atual = False

while True:

    dados_atualizados = pegando_dados(codigo=codigo_operado, intervalo=periodo_candle)
    posicao_atual = estrategia_trade(dados_atualizados, codigo_ativo=codigo_operado, 
                                        ativo_operado=ativo_operado, quantidade=quantidade, posicao=posicao_atual)
    time.sleep(60 * 60)



