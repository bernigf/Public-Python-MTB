# RECORDER

import sys
import thread

import datetime
import json
import traceback
import time
import math

import keys

from time import sleep
from datetime import date

from binance.client import *
from binance.enums import *

BINANCE = Client(keys.APIKey, keys.SecretKey)

def getNowTime() :
    now = datetime.datetime.now()
    nowStr = now.isoformat()
    hourStr = '{:02d}'.format(now.hour)
    minuteStr = '{:02d}'.format(now.minute)
    secondStr = '{:02d}'.format(now.second)
    timeStr = hourStr + ":" + minuteStr + ":" + secondStr
    return timeStr

def getNowDate() :
    dateStr = str(date.today())
    return dateStr

def write_data (PARAM_file, PARAM_data) :

	file_name = str(PARAM_file)

	with open(file_name, 'a') as f :
		
		f.write(str(PARAM_data) + "\n")

def BINANCE_TICKER_GetTickerData (PARAM_symbol) :

	while True :

		try:

			TICKER_data = BINANCE.get_ticker(symbol=PARAM_symbol)
			data_str = str(TICKER_data)
			data_str = data_str.replace("u'","'")
			data_str = data_str.replace("'",'"')
			data_str = data_str.replace("True","true")
			data_str = data_str.replace("False","false")
			TICKER_data_json = json.loads(data_str)
			break

		except Exception as e:

			e = sys.exc_info()
			print ""
			print "[BOT] BINANCE_TICKER_GetTickerData: ERROR: " + str(e)
			print "[BOT] BINANCE_TICKER_GetTickerData: ERROR return Type: " + str(type(e))
			print "[BOT] BINANCE_TICKER_GetTickerData: ERROR return T: " + str(e[0])
			print "[BOT] BINANCE_TICKER_GetTickerData: ERROR return Type: " + str(e[2])
			print "[BOT] BINANCE_TICKER_GetTickerData: ERROR return Output[-50:] : ... " + str(traceback.format_tb(e[2]))[-50:]
			print ""
			sleep(1)

		else:

			print ""
			print "[BOT] BINANCE_TICKER_GetTickerData: ERROR - Unknown"
			print ""
			sleep(1)

	return TICKER_data_json

def BINANCE_TICKER_GetAllTickersData () :

	defName = "BINANCE_TICKER_GetAllTickersData: "
	while True :

		try:

			TICKER_data = BINANCE.get_all_tickers()
			data_str = str(TICKER_data)
			data_str = data_str.replace("u'","'")
			data_str = data_str.replace("'",'"')
			data_str = data_str.replace("True","true")
			data_str = data_str.replace("False","false")
			TICKER_data_json = json.loads(data_str)
			break

		except Exception as e:

			e = sys.exc_info()
			sleep(1)

		else:

			sleep(1)

	# Check before adding to CACHE if requested symbol is current TRADE symbol
	# When asking for FEE price TICKER_GetTickerData is called with BNBUSDT
	# then wrong prices are added at CACHE and then used as new max for next loop
	#if(PARAM_symbol == GVAR.symbol) :
	#	TICKER_CACHE_AddNewTick(TIME_getNowTime(), TICKER_data_json['bidPrice'])

	return TICKER_data_json

####################################################

FILTER = "BUSD"

FILE_EXT = ".dat"
FILE_DIR = "RECORDINGS"
DATE_TMP = getNowDate()
TIME_TMP = getNowTime().replace(":","_")

FILE_TMP = FILTER + "-" + DATE_TMP + "-" + TIME_TMP

FILE_NAME = raw_input("> Record to ./" + FILE_DIR + "/ -> File Name : [" + FILE_TMP + "]")
if (FILE_NAME == "") :
	FILE_NAME = FILE_TMP

FILE = "./" + FILE_DIR + "/" + FILE_NAME + FILE_EXT
print "Creating file: " + FILE
print ""

while True:

	time = getNowTime()
	#data_json = BINANCE_TICKER_GetTickerData(SYMBOL)
	data_json = BINANCE_TICKER_GetAllTickersData()

	dataLineStr = "TIME=" + time + " "

	for item in data_json :
		
		symbolStr = str(item['symbol'])
		if (symbolStr.find(FILTER) > -1) :
			priceStr = str(item['price'])
			dataLineStr = dataLineStr + symbolStr + "=" + priceStr + " "

	print ">> " + str(time) + " -> SAVED OK"
	write_data(FILE, dataLineStr)
	sleep(1)
	
