#Binance

import keys
import GVAR
from GLOBALS import GSTRING
import defs
import trader

import datetime
import json
import sys
import time
import datetime
import pickle

import thread
import threading
import traceback
import logging

import os

from time import sleep
from binance.client import Client
from binance.enums import *

from GVAR import *
from defs import *
from trader import *

# INITIAL SETTINGS v3.0
###################################
#TRADER_MODE = "SIMULATOR_FULL"
#TRADER_MODE = "SIMULATOR_ORDERS_ONLY"
TRADER_MODE = "REAL"

global EXCHANGE_ORDER_Cancel 
global EXCHANGE_ORDER_GetStatus 
global EXCHANGE_ORDER_Create_StopLimit
global SIMULATOR_TICKER_dataFile
global EXCHANGE_TICKER_GetTickerData
global SIMULATOR_DefSet
global TIME_getNowTime

#====================================================================================================
ARGS = sys.argv[1:]
BOT_ParseArgs(ARGS)
#====================================================================================================
# Others configuration variables
GVAR.MODE_VERBOSE = True
#====================================================================================================

bprint('')
bprint(pcolors.TUR + 'TRADE' + pcolors.ENDC + pcolors.TUR + ' BOT' + pcolors.ENDC + pcolors.TUR + ' II' + pcolors.ENDC + ' ' + str(GVAR.BOT_version))
bprint('===================')
bprint('')
bprint('[BOT] Start Local Time: ' + TIME_getNowTime() )

bprint("")
bprint("MAIN: Starting curses screen thread..")
bprint("")

tScreen = threading.Thread(target=SCREEN_init)
tScreen.start()

MICRO_sleep(1)

bprint("MAIN: Starting cmd thread..")

tCmd = threading.Thread(target=SCREEN_cmd)
tCmd.start()

bprint("MAIN: Starting pool monitor thread..")

tPool = threading.Thread(target=POOL_monitor)
tPool.start()

bprint("MAIN: Starting trader thread..")

tTrader = threading.Thread(target=TRADER_main)
tTrader.start()

bprint("MAIN: Starting pricer thread..")

tPricer = threading.Thread(target=POOL_pricer)
tPricer.start()

#t1 = threading.Thread(target=TRADER_main)
#t1.start()

if(GVAR.FLAG_GRAPH_mode_on == True) :

	bprint("MAIN: Starting VISUAL thread..")
	bprint("")

	GRAPH_TRADE_plot(0.25)
	GVAR.FLAG_main_thread_exit = True

bprint("MAIN: Threads execution succesfull -> Main file INIT OK") 

if (TRADER_MODE == "SIMULATOR_FULL") :

	SIMULATOR_DATA_FILE = "ARENA_BEAR.dat"
	#GVAR.TICKER_sleep = 0.00001
	#GVAR.TICKER_sleep = 0.05
	GVAR.TICKER_sleep = 0.1
	#GVAR.TICKER_sleep = 0.5
	GVAR.SIMULATOR_ORDERS = True
	GVAR.SIMULATOR_TICKER = True
	BNB_data = {'bidPrice' : 16.50 }
	GVAR.SIMULATOR_TICKER_debug_stops = True
	GVAR.MODE_VERBOSE = True

if (TRADER_MODE == "SIMULATOR_ORDERS_ONLY") :

	GVAR.TICKER_sleep = 0.00001
	GVAR.SIMULATOR_ORDERS = True
	GVAR.SIMULATOR_TICKER = False
	BNB_data = {'bidPrice' : 16.50 }

if (TRADER_MODE == "REAL") :
	GVAR.SIMULATOR_ORDERS = False
	GVAR.SIMULATOR_TICKER = False
	GVAR.MODE_VERBOSE = True
	GVAR.SIMULATOR_TICKER_debug_stops = False
	BNB_data = {'bidPrice' : 16.50 }


if (GVAR.SIMULATOR_ORDERS == False) :

	BINANCE = Client(keys.APIKey, keys.SecretKey)

	EXCHANGE_ORDER_Cancel = defs.BINANCE_ORDER_Cancel
	EXCHANGE_ORDER_GetStatus = defs.BINANCE_ORDER_GetStatus
	EXCHANGE_ORDER_Create_StopLimit = defs.BINANCE_ORDER_Create_StopLimit
	EXCHANGE_TICKER_GetTickerData = defs.BINANCE_TICKER_GetTickerData
	TIME_getNowTime = defs.TIME_REAL_getNowTime

else :
	EXCHANGE_ORDER_Cancel = defs.SIMULATOR_ORDER_Cancel
	EXCHANGE_ORDER_GetStatus = defs.SIMULATOR_ORDER_GetStatus
	EXCHANGE_ORDER_Create_StopLimit = defs.SIMULATOR_ORDER_Create_StopLimit
	if(GVAR.SIMULATOR_TICKER == True) :
		GVAR.SIMULATOR_TICKER_dataFile = SIMULATOR_DATA_FILE
		EXCHANGE_TICKER_GetTickerData = defs.SIMULATOR_TICKER_GetTickerData
		TIME_getNowTime = defs.TIME_SIMULATOR_getNowTime
	else :
		EXCHANGE_TICKER_GetTickerData = defs.BINANCE_TICKER_GetTickerData
		TIME_getNowTime = defs.TIME_REAL_getNowTime	
	
	SIMULATOR_DefSet(GVAR.SIMULATOR_ORDERS, GVAR.SIMULATOR_TICKER)

if (GVAR.SIMULATOR_ORDERS == True) :
	bprint("")
	bprint("SIMULATOR -> " + pcolors.GREEN + "TICKER_sleep" + pcolors.ENDC + " = " + str(TICKER_sleep))
	bprint("SIMULATOR DATA FILE -> " + pcolors.GREEN + "TICKER_sleep" + pcolors.ENDC + " = " + pcolors.YELLOW + str(GVAR.SIMULATOR_TICKER_dataDir + GVAR.SIMULATOR_TICKER_dataFile) + pcolors.ENDC)
	bprint("")

# ==============================================================

bprint("MAIN: Main file execution succesfull") 
bprint("")
