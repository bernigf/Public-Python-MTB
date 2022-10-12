import sys
import thread
import curses

import datetime
import json
import yaml
import traceback
import time
import math
import os

import keys
import GVAR
from GLOBALS import GSTRING
import visual

from time import sleep
from binance.client import *
from binance.enums import *

from visual import *
from os import path

import ast

import operator

class pcolors:

    GREEN = '\033[92m'
    BLUE = '\033[34m'
    RED = '\033[91m'
    VIOLET = '\33[95m'
    YELLOW = '\33[93m'
    TUR = '\33[96m'

    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

    BLINK    = '\33[5m'
    BLINK2   = '\33[6m'
    SELECTED = '\33[7m'

def calcPriceDistance (PARAM_BuyPrice, PARAM_TickerPrice) :

	diffPrice = float(PARAM_TickerPrice) - float(PARAM_BuyPrice)
	return diffPrice

def calcPriceDistancePercent (PARAM_BuyPrice, PARAM_TickerPrice ) :

	if float(PARAM_TickerPrice) == 0 :

		diffPricePercent = -100

	else :

		diffPricePercent = ((float(PARAM_BuyPrice) * 100 / float(PARAM_TickerPrice)) - 100) * (-1)
	
	return diffPricePercent

def calcIdlePriceLimit(PARAM_BUY_price_stop, PARAM_IDLE_margin_mp, PARAM_rounder) :

	idle_price_limit = float(PARAM_BUY_price_stop) * (1 - (PARAM_IDLE_margin_mp / 100))
	idle_price_limit = round(idle_price_limit, PARAM_rounder)
	return idle_price_limit

def StatsBlockGenerator (PARAM_DurationInSeconds, PARAM_ProgressInSeconds) :

	progress = int(PARAM_ProgressInSeconds * 100  / PARAM_DurationInSeconds)
	
	if (progress % 2 == 0) :
		progressChar = "|"
	else :
		progressChar = "-"

	outputStr = "[ " + str(PARAM_ProgressInSeconds) + "/" + str(PARAM_DurationInSeconds) + " secs " + str(progress) + " % ]"

	if (PARAM_DurationInSeconds == PARAM_ProgressInSeconds) :
		outputStr += "\n"

	return outputStr

def TIME_REAL_getNowTime() :
	now = datetime.datetime.now()
	nowStr = now.isoformat()
	hourStr = '{:02d}'.format(now.hour)
	minuteStr = '{:02d}'.format(now.minute)
	secondStr = '{:02d}'.format(now.second)
	timeStr = hourStr + ":" + minuteStr + ":" + secondStr
	return timeStr

def TIME_SIMULATOR_getNowTime() :
	"""now = datetime.datetime.now()
	nowStr = now.isoformat()
	hourStr = '{:02d}'.format(now.hour)
	minuteStr = '{:02d}'.format(now.minute)
	secondStr = '{:02d}'.format(now.second)
	timeStr = hourStr + ":" + minuteStr + ":" + secondStr"""
	return GVAR.SIMULATOR_TICKER_time

def BUY_CFA_CreateOrder(PARAM_symbol, PARAM_BUY_price, PARAM_BUY_margin_percent) :

	DEBUG_TRADE_printVars("BUY_CFA_CreateOrder")
	resp = EXCHANGE_ORDER_Create_StopLimit (GVAR.symbol, SIDE_BUY, PARAM_BUY_price , GVAR.BUY_price_limit, GVAR.BUY_amount) 

	return resp

def IDLE_printWaitLine(PARAM_TickerBidPrice, PARAM_price_stop_distance) :

	nowStr = TIME_getNowTime()

	GVAR.IDLE_log_counter += 1

	#TICKER_data = EXCHANGE_TICKER_GetTickerData (GVAR.symbol)
	#TICKER_price_bid = TICKER_data["bidPrice"]
	
	TICKER_price_bid = PARAM_TickerBidPrice

	price_stop_len = len(str(int(GVAR.BUY_price_stop)))
	price_bid_str = str(round(float(TICKER_price_bid),GVAR.TRADE_round_prices)).ljust(price_stop_len + 1 + GVAR.TRADE_round_prices)

	#price_distance = abs(round(calcPriceDistancePercent(float(TICKER_price_bid), GVAR.IDLE_price_limit),2))
	price_distance = PARAM_price_stop_distance

	amount_price = round(float(GVAR.BUY_amount) * float(GVAR.BUY_price_limit), GVAR.TRADE_round_prices)

	mode_name = GVAR.MODE
	
	if (GVAR.SCREEN_WIN_log_enabled == False) :

		strP = str(price_distance).ljust(5) + " %"
		strV = "[ " + str(GVAR.BOT_ID) + " v" + str(GVAR.BOT_version) + " ]"
		str1 = strV + " " + nowStr + " <" + mode_name + "> " + pcolors.VIOLET + GVAR.symbol + pcolors.ENDC + " " + price_bid_str
		str2 = " (" + strP + ") to " + pcolors.YELLOW + "IDLE" + pcolors.ENDC + " limit (" + str(GVAR.IDLE_price_margin_mp) + " %) " + pcolors.TUR + str(GVAR.IDLE_price_limit) + pcolors.ENDC + " " + pcolors.GREEN + GVAR.SELL_symbol + pcolors.ENDC
		str3 = " - BUY [ " + pcolors.RED + "STOP" + pcolors.ENDC + " " + pcolors.TUR + str(GVAR.BUY_price_stop) + pcolors.ENDC + " ]"
		str4 = " " + "[ LIMIT" + " " + pcolors.TUR + str(GVAR.BUY_price_limit) + pcolors.ENDC + " ]"
		str5 = " " + "[ AMOUNT" + " " + pcolors.TUR + str(GVAR.BUY_amount) + pcolors.ENDC + " " + pcolors.VIOLET + GVAR.BUY_symbol + pcolors.ENDC + " = " + str(amount_price) + " " + GVAR.SELL_symbol + " ]"
		str6 = " [ " + str(GVAR.IDLE_log_counter).ljust(2) + "/" + str(GVAR.IDLE_log_block) + " ]" 
		
		lineStr = str1 + str2 + str3 + str4 + str5 + str6

		if (GVAR.IDLE_log_counter == 60) :
			sys.stdout.write("\n")
			sys.stdout.flush()
			GVAR.IDLE_log_counter = 0

		if (GVAR.MODE_VERBOSE_enabled == True) :
			sys.stdout.write(lineStr + "\r")
			sys.stdout.flush()

	else :

		timeStr = str(datetime.timedelta(seconds=GVAR.IDLE_log_counter))

		strP = str(price_distance).ljust(5) + " %"
		strV = "[ " + str(GVAR.BOT_ID) + " v" + str(GVAR.BOT_version) + " ]"
		str1 = strV + " " + nowStr + " <" + mode_name + "> " + GVAR.symbol + " " + price_bid_str
		str2 = " (" + strP + ") to " + "IDLE" + " (limit = " + str(GVAR.IDLE_price_margin_mp) + " %) at " + str(GVAR.IDLE_price_limit) + " " + GVAR.SELL_symbol
		str3 = " - BUY [ " + "STOP" + " " + str(GVAR.BUY_price_stop) + " ]"
		str4 = " " + "[ LIMIT" + " " + str(GVAR.BUY_price_limit) + " ]"
		str5 = " " + "[ AMOUNT" + " " + str(GVAR.BUY_amount) + " " + GVAR.BUY_symbol + " = " + str(amount_price) + " " + GVAR.SELL_symbol + " ]"
		str6 = " [ " + timeStr + " ]" 
		
		lineStr = str1 + str2 + str3 + str4 + str5 + str6
		
		bprint(lineStr)

def THREADS_aliveSignal (PARAM_threadName) :

	defName = "THREAD_aliveSignal: "
	tName = PARAM_threadName
	
	maxSignal = 8

	alive_mod = 1000

	if (int(GVAR.FLAG_ALIVE_counter % alive_mod) == 0) :

		nowTime = TIME_getNowTime()
		bprint (defName + "Alive signal " + str(nowTime))
		GVAR.FLAG_ALIVE_counter = 1

	else :

		GVAR.FLAG_ALIVE_counter += 1

	if(tName == "POOL_monitor") :
		
		if(GVAR.THREADS_SIGNAL_poolMonitor == maxSignal) :
			GVAR.THREADS_SIGNAL_poolMonitor = 0
		else :
		 	GVAR.THREADS_SIGNAL_poolMonitor += 1

	elif(tName == "POOL_pricer") :
		
		if(GVAR.THREADS_SIGNAL_poolPricer == maxSignal) :
			GVAR.THREADS_SIGNAL_poolPricer = 0
		else :
		 	GVAR.THREADS_SIGNAL_poolPricer += 1

	elif(tName == "TRADER_main") :
		
		if(GVAR.THREADS_SIGNAL_traderMain == maxSignal) :
			GVAR.THREADS_SIGNAL_traderMain = 0
		else :
		 	GVAR.THREADS_SIGNAL_traderMain += 1

def THREADS_signalRender(PARAM_threadSignalVar) :

	counter = PARAM_threadSignalVar

	if(counter == 0) :
		signalChar = "-"
	elif(counter == 1) :
		signalChar = "\\"
	elif(counter == 2) :
		signalChar = "|"
	elif(counter == 3) :
		signalChar = "/"
	elif(counter == 4) :
		signalChar = "-"
	elif(counter == 5) :
		signalChar = "\\"
	elif(counter == 6) :
		signalChar = "|"
	elif(counter == 7) :
		signalChar = "/"
	elif(counter == 8) :
		signalChar = "-"
	
	return signalChar

def SCREEN_init() :

	defName = "SCREEN_init: "

	print defName + "Starting curses main screen ... "
	
	screen = curses.initscr()
	GVAR.SCREEN_screen = screen
	curses.start_color()

	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
	curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

	GVAR.SCREEN_enabled = True
		
	curses.curs_set(0)
	#screen.border(0)
	
	print defName + "Screen initialized OK"

	#curses.napms(1000)

	SCREEN_monochromer(True)

	SCREEN_WIN_startLogo()
	SCREEN_WIN_log_init()
	GVAR.SCREEN_WIN_trader = SCREEN_WIN_trader_init()
	GVAR.SCREEN_WIN_status = SCREEN_WIN_status_init()
	GVAR.SCREEN_WIN_poolMonitor = SCREEN_WIN_poolMonitor_init()
	GVAR.SCREEN_WIN_cmd = SCREEN_WIN_cmd_init()
	
	#screen.refresh()
	#curses.napms(2000)
	#curses.curs_set(1)
	#curses.endwin()
	#print defName + "Screen ended"

	while (GVAR.SCREEN_exit == False) :

		#try:
	
		if(GVAR.SCREEN_WIN_poolMonitor_visible == True) :

			SCREEN_WIN_poolMonitor_refresh(GVAR.SCREEN_WIN_poolMonitor)
			SCREEN_WIN_status_refresh(GVAR.SCREEN_WIN_status)
			SCREEN_WIN_trader_refresh(GVAR.SCREEN_WIN_trader)
			SCREEN_WIN_cmd_refresh(GVAR.SCREEN_WIN_cmd)
			SCREEN_WIN_log_refresh(GVAR.SCREEN_WIN_log)

		"""except Exception as e:

			e = sys.exc_info()
			bprint("")
			bprint(defName + "ERROR <<< DEBUG >>> Printing error info:")
			ERROR_printer(e,defName)
			bprint("")
			bprint(defName + "ERROR <<< DEBUG >>> Reset curses screen..")
			screen.erase()
			screen.clear()
			screen.refresh()"""

		# Needed if not CPU goes to 100%
		MICRO_sleep(0.25)

def SCREEN_WIN_cmd_init() :

	winXpos = 0

	cmdWin = curses.newwin(3, GVAR.SCREEN_width - 1, GVAR.SCREEN_height - 3 , winXpos)
	cmdWin.border(0)
	winXpos = 0

	return cmdWin

def SCREEN_cmd () :

	defName = "SCREEN_cmd: "
	key = 0

	xPos = 0
	inputStr = ""
	cmdWin = None

	while (cmdWin == None) :

		cmdWin = GVAR.SCREEN_WIN_cmd

		if(cmdWin == None) :
			
			bprint(defName + "No signal from CMD screen..")
			sleep(1)

	while(key != 37) :

		key = cmdWin.getch()
		
		inputStr = GVAR.SCREEN_WIN_cmd_inputStr
		xPos += 1

		doPrintInput = False
		eventKey = False

		if (key == 10) :

			# Enter key -> print as blank space on inputscr
			xPos = 0

			eventKey = True
			doPrintInput = True

			if(inputStr.strip() != "") :

				if(GVAR.MODE_VERBOSE_events == True) :
					bprint(defName + " input: '" + inputStr + "'")
				
				GVAR.SCREEN_WIN_cmd_cmdHistory.append(inputStr)
				GVAR.SCREEN_WIN_cmd_cmdIndex = 0
				SCREEN_cmdLine(inputStr)
				GVAR.SCREEN_WIN_cmd_erase = True
			
			inputStr = ""

		elif (key == 127) :

			# Backspace
			if xPos > 0 :
				
				xPos -= 1
				newLen = len(inputStr) - 1
				inputStr = inputStr[:newLen]
				GVAR.SCREEN_WIN_cmd_erase = True

			eventKey = True
			doPrintInput = True

		elif (key == 43) :

			GVAR.SCREEN_WIN_poolMonitor_marketIndex_start += 1
			GVAR.SCREEN_WIN_poolMonitor_marketIndex_end += 1
			#GVAR.SCREEN_WIN_poolMonitor.erase()
			#GVAR.SCREEN_WIN_poolMonitor.box()

			eventKey = True
			doPrintInput = False

		elif (key == 45) :

			if(GVAR.SCREEN_WIN_poolMonitor_marketIndex_start > 1) :
				GVAR.SCREEN_WIN_poolMonitor_marketIndex_start -= 1
				GVAR.SCREEN_WIN_poolMonitor_marketIndex_end -= 1
				#GVAR.SCREEN_WIN_poolMonitor.erase()
				#GVAR.SCREEN_WIN_poolMonitor.box()

			eventKey = True
			doPrintInput = False

		elif (key == 65) :

			doPrintInput = True

			prevKey = GVAR.SCREEN_WIN_cmd_keyHistory[-1:][0]
			prevPrevKey = GVAR.SCREEN_WIN_cmd_keyHistory[-2:-1][0]

			devprint(GVAR.MODE_VERBOSE_events, defName + "Key 65 = A detected -> checking history -> prevKey = " + str(prevKey) + " | prevPrevKey = " + str(prevPrevKey))

			if((prevKey == 91) & (prevPrevKey == 27)) :

				eventKey = True

				# init cmdIndex to avoid reference before assignament errors later
				cmdIndex = GVAR.SCREEN_WIN_cmd_cmdIndex

				devprint(GVAR.MODE_VERBOSE_events,defName + "Up arrow key pressed (3 keys secuence 27 91 65)")
				devprint(GVAR.MODE_VERBOSE_events,defName + "Decreasing GVAR.SCREEN_WIN_cmd_cmdIndex = " + str(GVAR.SCREEN_WIN_cmd_cmdIndex) + " -> " + str(GVAR.SCREEN_WIN_cmd_cmdIndex - 1))

				if(GVAR.SCREEN_WIN_cmd_cmdIndex < len(GVAR.SCREEN_WIN_cmd_cmdHistory)) :

					GVAR.SCREEN_WIN_cmd_cmdIndex += 1
					cmdIndex = GVAR.SCREEN_WIN_cmd_cmdIndex
					
					devprint(GVAR.MODE_VERBOSE_events,defName + "GVAR.SCREEN_WIN_cmd_cmdHistory (last 5) = " + str(GVAR.SCREEN_WIN_cmd_cmdHistory[-5:]))
					devprint(GVAR.MODE_VERBOSE_events,defName + "len(GVAR.SCREEN_WIN_cmd_cmdHistory) = " + str(len(GVAR.SCREEN_WIN_cmd_cmdHistory)))
					devprint(GVAR.MODE_VERBOSE_events,defName + "GVAR.SCREEN_WIN_cmd_cmdIndex = " + str(GVAR.SCREEN_WIN_cmd_cmdIndex))

					GVAR.SCREEN_WIN_cmd.erase()
					GVAR.SCREEN_WIN_cmd.box()
					
					inputStr = GVAR.SCREEN_WIN_cmd_cmdHistory[-cmdIndex]
				
				else :

					devprint(GVAR.MODE_VERBOSE_events,defName + "GVAR.SCREEN_WIN_cmd_cmdIndex = " + str(GVAR.SCREEN_WIN_cmd_cmdIndex) + " -> No more items in cmd history")
					
					key = 0
					
					if(cmdIndex > 0) :
						inputStr = GVAR.SCREEN_WIN_cmd_cmdHistory[-cmdIndex]
					else :
						inputStr = ""

					doPrintInput = True

		elif (key == 66) :

			doPrintInput = True

			prevKey = GVAR.SCREEN_WIN_cmd_keyHistory[-1:][0]
			prevPrevKey = GVAR.SCREEN_WIN_cmd_keyHistory[-2:-1][0]

			devprint(GVAR.MODE_VERBOSE_events, defName + "Key 66 = B detected -> checking history -> prevKey = " + str(prevKey) + " | prevPrevKey = " + str(prevPrevKey))

			if((prevKey == 91) & (prevPrevKey == 27)) :

				eventKey = True

				# init cmdIndex to avoid reference before assignament errors later
				cmdIndex = GVAR.SCREEN_WIN_cmd_cmdIndex

				devprint(GVAR.MODE_VERBOSE_events,defName + "Down arrow key pressed (3 keys secuence 27 91 66)")
				devprint(GVAR.MODE_VERBOSE_events,defName + "Increasing GVAR.SCREEN_WIN_cmd_cmdIndex = " + str(GVAR.SCREEN_WIN_cmd_cmdIndex) + " -> " + str(GVAR.SCREEN_WIN_cmd_cmdIndex + 1))

				if(GVAR.SCREEN_WIN_cmd_cmdIndex > 0) :

					GVAR.SCREEN_WIN_cmd_cmdIndex -= 1
					cmdIndex = GVAR.SCREEN_WIN_cmd_cmdIndex
					
					devprint(GVAR.MODE_VERBOSE_events,defName + "GVAR.SCREEN_WIN_cmd_cmdHistory (last 5) = " + str(GVAR.SCREEN_WIN_cmd_cmdHistory[-5:]))
					devprint(GVAR.MODE_VERBOSE_events,defName + "len(GVAR.SCREEN_WIN_cmd_cmdHistory) = " + str(len(GVAR.SCREEN_WIN_cmd_cmdHistory)))
					devprint(GVAR.MODE_VERBOSE_events,defName + "GVAR.SCREEN_WIN_cmd_cmdIndex = " + str(GVAR.SCREEN_WIN_cmd_cmdIndex))

					GVAR.SCREEN_WIN_cmd.erase()
					GVAR.SCREEN_WIN_cmd.box()

					inputStr = GVAR.SCREEN_WIN_cmd_cmdHistory[-cmdIndex]
				
				else :

					devprint(GVAR.MODE_VERBOSE_events,defName + "GVAR.SCREEN_WIN_cmd_cmdIndex = " + str(GVAR.SCREEN_WIN_cmd_cmdIndex) + " -> Bottom of cmd history")
					
					key = 0
					
					if(cmdIndex > 0) :
						inputStr = GVAR.SCREEN_WIN_cmd_cmdHistory[-cmdIndex]
					else :
						inputStr = ""

					doPrintInput = True

		if (eventKey == False) :

			inputStr = inputStr + str(chr(key))
			GVAR.SCREEN_WIN_cmd_keyHistory.append(key)
			doPrintInput = True

			if(GVAR.MODE_VERBOSE_events == True) :
				bprint(defName + "inputStr = " + str(inputStr) + " | doPrintInput = " + str(doPrintInput) + " | GVAR.SCREEN_WIN_cmd_keyHistory (last 10) = " + str(GVAR.SCREEN_WIN_cmd_keyHistory[-10:]))

		if (doPrintInput == True) :

			GVAR.SCREEN_WIN_cmd_inputStr = inputStr

			# When key == 0 -> Do nothing
			if (key != 0) :

				if(GVAR.MODE_VERBOSE_events == True) :

					if key == 10 :
						keyChr = "ENTER"
					elif key == 127 :
						keyChr = "BACKSPACE"
					else :
						keyChr = chr(key)

					bprint(defName + "Key pressed: " + str(key) + " = " + str(keyChr))

	if (key == 37) :

		bprint(defName +  "'%' key pressed -> FINISH trade and exit main thread")
		bprint("")

		GVAR.FLAG_main_thread_exit = True
		
		if(GVAR.TRADE_mode_on == True) :
			
			if (GVAR.BUY_mode_on == True) :
				GVAR.TRADER_mode = "ABORT_BUY"
				GVAR.BUY_mode_on = False

			if (GVAR.SELL_mode_on == True) :
				GVAR.TRADER_mode = "ABORT_SELL"
				GVAR.SELL_mode_on = False

		GVAR.MODE_LOOP = False
		GVAR.IDLE_mode_on = False
		GVAR.TRADER_enabled = False
		GVAR.POOL_pricer_enabled = False
		GVAR.SCREEN_exit = True

		curses.curs_set(1)
		#curses.endwin()

		quit()

def SCREEN_WIN_cmd_refresh(PARAM_win) :

	cmdWin = PARAM_win

	preStr = " > "
	inputStr = GVAR.SCREEN_WIN_cmd_inputStr

	if (cmdWin != None) :

		if(GVAR.SCREEN_WIN_cmd_erase == True) :

			GVAR.SCREEN_WIN_cmd_erase = False
			cmdWin.erase()
			cmdWin.border(0)

		cmdWin.addstr(1, 1, preStr + str(inputStr))
		cmdWin.refresh()

def SCREEN_WIN_trades_refresh() :

	winWidth = 100
	winHeight = 12

	winXpos = 50
	winYpos = 50

	xPos = 2
	yPos = 2

	win1 = curses.newwin(winHeight, winWidth, winYpos, winXpos)
	win1.immedok(True)
	win1.box()
	win1.refresh()

	

def SCREEN_WIN_startLogo() :

	winWidth = 37
	winHeight = 12

	#winXpos = int(GVAR.SCREEN_width / 2) - int(winWidth / 2)
	#winYpos = int(GVAR.SCREEN_height / 2) - int(winHeight / 1.5)

	winXpos = 0
	winYpos = 0

	xPos = 2
	yPos = 2

	if(GVAR.SCREEN_WIN_logo == None) :

		win1 = curses.newwin(winHeight, winWidth, winYpos, winXpos)
		GVAR.SCREEN_WIN_logo = win1

	else :

		win1 = GVAR.SCREEN_WIN_logo

	win1.immedok(True)
	win1.box()
	win1.refresh()

	lineCount = 0

	win1.addstr(yPos + lineCount, xPos, GSTRING.LOGO_v_1_line_1); lineCount += 1
	win1.addstr(yPos + lineCount, xPos, GSTRING.LOGO_v_1_line_2); lineCount += 1
	win1.addstr(yPos + lineCount, xPos, GSTRING.LOGO_v_1_line_3); lineCount += 1
	win1.addstr(yPos + lineCount, xPos, GSTRING.LOGO_v_1_line_4); lineCount += 1
	win1.addstr(yPos + lineCount, xPos, GSTRING.LOGO_v_1_line_5); lineCount += 1
	win1.addstr(yPos + lineCount, xPos, GSTRING.LOGO_v_1_line_6); lineCount += 1

	lineCount += 1
	
	win1.addstr(yPos + lineCount, xPos + 10, "Version " + str(GVAR.BOT_version), curses.color_pair(2))

def SCREEN_WIN_status_init() :

	winXmargin = 38

	winWidth = GVAR.SCREEN_width - winXmargin - 1
	winHeight = 7

	winXpos = winXmargin
	winYpos = 0

	win1 = curses.newwin(winHeight, winWidth, winYpos, winXpos)
	win1.immedok(True)
	win1.box()
	win1.refresh()

	# Check funds limit avialability (otherwise re-calc)
	POOL_fundsCheck()

	GVAR.SCREEN_WIN_status_enabled = True

	return win1

def SCREEN_WIN_trader_init() :

	winXmargin = 38

	winWidth = GVAR.SCREEN_width - winXmargin - 1
	winHeight = 5

	winXpos = winXmargin
	winYpos = 7

	win1 = curses.newwin(winHeight, winWidth, winYpos, winXpos)
	win1.immedok(True)
	win1.box()
	win1.refresh()

	GVAR.SCREEN_WIN_status_enabled = True

	return win1

def SCREEN_WIN_status_refresh(PARAM_win):

	win1 = PARAM_win
	#win1.clear()
	#win1.border(0)

	yPos = 1
	xPos = 2

	fundsTotal = GVAR.POOL_FUNDS_free + GVAR.POOL_FUNDS_locked

	win1.addstr(yPos, xPos, "Funds total: ")
	win1.addstr(yPos, xPos + 14, str(fundsTotal).rjust(8))
	win1.addstr(yPos, xPos + 24, GVAR.POOL_FUNDS_symbol)

	yPos = 2
	xPos = 2

	win1.addstr(yPos, xPos, "Funds free: ")
	win1.addstr(yPos, xPos + 14, str(GVAR.POOL_FUNDS_free).rjust(8))
	win1.addstr(yPos, xPos + 24, GVAR.POOL_FUNDS_symbol)

	yPos = 3
	xPos = 2

	win1.addstr(yPos, xPos, "Funds locked: ")
	win1.addstr(yPos, xPos + 14, str(GVAR.POOL_FUNDS_locked).rjust(8))
	win1.addstr(yPos, xPos + 24, GVAR.POOL_FUNDS_symbol)

	yPos = 4
	xPos = 2

	win1.addstr(yPos, xPos, "Funds limit: ")
	win1.addstr(yPos, xPos + 14, str(GVAR.POOL_FUNDS_limit).rjust(8))
	win1.addstr(yPos, xPos + 24, GVAR.POOL_FUNDS_symbol)

	yPos = 5
	xPos = 2

	win1.addstr(yPos, xPos, "Funds stop: ")
	win1.addstr(yPos, xPos + 14, str(GVAR.POOL_FUNDS_stop).rjust(8))
	win1.addstr(yPos, xPos + 24, GVAR.POOL_FUNDS_symbol)

	yPos = 1
	xPos = 33

	win1.addstr(yPos, xPos, "Market Trade: ")
	win1.addstr(yPos, xPos + 14, str(GVAR.TRADER_marketName).ljust(8))

	yPos = 2
	xPos = 33

	mPrio1 = POOL_prioRanker(0, False)
	win1.addstr(yPos, xPos, "Market Prio1: ")
	win1.addstr(yPos, xPos + 14, str(mPrio1).ljust(8))

	yPos = 3
	xPos = 33

	mPrio2 = POOL_prioRanker(1, False)
	win1.addstr(yPos, xPos, "Market Prio2: ")
	win1.addstr(yPos, xPos + 14, str(mPrio2).ljust(8))

	yPos = 1
	xPos = 135

	win1.addstr(yPos, xPos, str("Thread POOL_monitor: ").rjust(23))
	win1.addstr(yPos, xPos + 23, str(THREADS_signalRender(GVAR.THREADS_SIGNAL_poolMonitor)))

	yPos = 2
	xPos = 135

	win1.addstr(yPos, xPos, str("Thread POOL_pricer: ").rjust(23))
	win1.addstr(yPos, xPos + 23, str(THREADS_signalRender(GVAR.THREADS_SIGNAL_poolPricer)))

	yPos = 3
	xPos = 135

	win1.addstr(yPos, xPos, str("Thread TRADER_main: ").rjust(23))
	win1.addstr(yPos, xPos + 23, str(THREADS_signalRender(GVAR.THREADS_SIGNAL_traderMain)))

def SCREEN_WIN_trader_refresh(PARAM_win):

	win1 = PARAM_win

	mName = GVAR.TRADER_marketName
	mData = None
	
	if(mName != None) :
		mData = POOL_marketGetData(mName)

	if(mData) :

		priceBuyStop = mData['PRICE_BUY_stop']
		priceBuyLimit = mData['PRICE_BUY_limit']

		priceSellStop = mData['PRICE_SELL_stop']
		priceSellLimit = mData['PRICE_SELL_limit']

		priceMarket = mData['PRICE_market']
		
		rounderPrices = mData['TRADE_round_prices']
		rounderAmounts = mData['TRADE_round_amounts']

		if (GVAR.SCREEN_WIN_trader_cleared == True) :

			GVAR.SCREEN_WIN_trader_cleared = False
			win1.border(0)

		if (GVAR.TRADE_mode_on == True) :

			yPos = 2
			xPos = 2

			#win1.border(0)

			win1.addstr(yPos, xPos, "TRADE -> ")
			win1.addstr(yPos, xPos + 9, mData['BUY_symbol'], curses.color_pair(6))
			win1.addstr(yPos, xPos + 14, str(priceMarket).rjust(9))
			win1.addstr(yPos, xPos + 24, mData['SELL_symbol'])
			win1.addstr(yPos, xPos + 79, "[ Order Id: ")
			win1.addstr(yPos, xPos + 90, str(GVAR.TRADE_orderId) + "")
			win1.addstr(yPos, xPos + 100 , "| Status: ")
			#win1.addstr(yPos, xPos + 40, str(GVAR.TRADER_run_char))
			win1.addstr(yPos, xPos + 120, "| Side: ")
			win1.addstr(yPos, xPos + 140, str("SIDE").ljust(8))

		if (GVAR.BUY_mode_on == True) :

			yPos = 1
			xPos = 2

			win1.addstr(yPos, xPos, "  BUY -> ", curses.color_pair(2))
			win1.addstr(yPos, xPos + 9, "STOP", curses.color_pair(6))
			win1.addstr(yPos, xPos + 14, str(priceBuyStop).rjust(9))
			win1.addstr(yPos, xPos + 24, mData['SELL_symbol'])
			win1.addstr(yPos, xPos + 35, "LIMIT: ", curses.color_pair(6))
			win1.addstr(yPos, xPos + 45, str(priceBuyLimit).rjust(9))
			win1.addstr(yPos, xPos + 55, mData['SELL_symbol'])

			yPos = 3
			xPos = 2

			win1.addstr(yPos, xPos, "", curses.color_pair(2))
			priceDist = round(float(priceMarket) - float(priceBuyStop), rounderPrices)
			if(priceDist < 0) :
				priceDistStr = str(priceDist)
			else :
				priceDistStr = "+" + str(priceDist)
			win1.addstr(yPos, xPos + 9, "DIST", curses.color_pair(6))
			win1.addstr(yPos, xPos + 14, priceDistStr.rjust(9))
			win1.addstr(yPos, xPos + 24, mData['SELL_symbol'])

		elif (GVAR.SELL_mode_on == True) :

			yPos = 3
			xPos = 2

			win1.addstr(yPos, xPos, " SELL -> ", curses.color_pair(4))
			win1.addstr(yPos, xPos + 14, str(GVAR.POOL_FUNDS_locked).rjust(8))
			win1.addstr(yPos, xPos + 24, GVAR.POOL_FUNDS_symbol)
			win1.addstr(yPos, xPos + 9, "STOP", curses.color_pair(6))
			win1.addstr(yPos, xPos + 14, str(priceSellStop).rjust(9))
			win1.addstr(yPos, xPos + 24, mData['SELL_symbol'])
			win1.addstr(yPos, xPos + 35, "LIMIT: ", curses.color_pair(6))
			win1.addstr(yPos, xPos + 45, str(priceSellLimit).rjust(9))
			win1.addstr(yPos, xPos + 55, mData['SELL_symbol'])

			yPos = 1
			xPos = 2

			win1.addstr(yPos, xPos, "", curses.color_pair(2))
			priceDist = round(float(priceMarket) - float(priceSellStop), rounderPrices)
			if(priceDist < 0) :
				priceDistStr = str(priceDist)
			else :
				priceDistStr = "+" + str(priceDist)
			win1.addstr(yPos, xPos + 9, "DIST", curses.color_pair(6))
			win1.addstr(yPos, xPos + 14, priceDistStr.rjust(9))
			win1.addstr(yPos, xPos + 24, mData['SELL_symbol'])


	else :

		if (GVAR.SCREEN_WIN_trader_cleared == False) :

			GVAR.SCREEN_WIN_trader_cleared = True
			win1.clear()		

def SCREEN_WIN_log_init() :

	winWidth = GVAR.SCREEN_WIN_log_width
	winHeight = GVAR.SCREEN_WIN_log_height

	winXpos = 0
	winYpos = GVAR.SCREEN_height - winHeight - 2

	win1 = curses.newwin(winHeight, winWidth, winYpos, winXpos)
	win1.immedok(True)
	win1.box()
	win1.refresh()

	GVAR.SCREEN_WIN_log = win1
	GVAR.SCREEN_WIN_log_enabled = True

def SCREEN_WIN_poolMonitor_init() :

	winWidth = GVAR.SCREEN_width - 1
	winHeight = 25

	winXpos = 0
	winYpos = 12

	winPM = curses.newwin(winHeight, winWidth, winYpos, winXpos)
	winPM.immedok(True)
	winPM.box()
	winPM.refresh()

	GVAR.SCREEN_WIN_poolMonitor = winPM
	GVAR.SCREEN_WIN_poolMonitor_visible = True

	GVAR.SCREEN_WIN_poolMonitor_marketIndex_start = 1
	GVAR.SCREEN_WIN_poolMonitor_marketIndex_end = 22

	return winPM

def SCREEN_WIN_poolMonitor_refresh(PARAM_win):

	win = PARAM_win

	# Aboid crealing every second because screen does lots of random "blinks"
	#win.clear()
	#win.border(0)

	c1_xPos = 2
	c2_xPos = 15
	c3_xPos = 26
	c4_xPos = 41
	c5_xPos = 52
	c6_xPos = 65
	c7_xPos = 77
	c8_xPos = 89
	c9_xPos = 99
	c10_xPos = 107
	c11_xPos = 115
	c12_xPos = 125
	c13_xPos = 141
	c14_xPos = 146
	c15_xPos = 156
	c16_xPos = 164
	c17_xPos = 174
	c18_xPos = 181

	win.addstr(0, 1, " MARKETS ", curses.color_pair(1))
	win.addstr(1, 1, " NAME         ", curses.color_pair(1))
	win.addstr(1, c2_xPos, "SYMBOL       ", curses.color_pair(1))
	win.addstr(1, c3_xPos, "PRICE            ", curses.color_pair(1))
	win.addstr(1, c4_xPos, "IDLE DP    ", curses.color_pair(1))
	win.addstr(1, c5_xPos, "IDLE LIMIT   ", curses.color_pair(1))
	win.addstr(1, c6_xPos, "IDLE MP      ", curses.color_pair(1))
	win.addstr(1, c7_xPos, "BUY STOP     ", curses.color_pair(1))
	win.addstr(1, c8_xPos, "LIMIT     ", curses.color_pair(1))
	win.addstr(1, c9_xPos, "mBUY    ", curses.color_pair(1))
	win.addstr(1, c10_xPos, "mSELL    ", curses.color_pair(1))
	win.addstr(1, c11_xPos, "AMOUNT         ", curses.color_pair(1))
	win.addstr(1, c12_xPos, "LOT SIZE        ", curses.color_pair(1))
	win.addstr(1, c13_xPos, "PRIO         ", curses.color_pair(1))
	win.addstr(1, c14_xPos, "IDLE TIME      ", curses.color_pair(1))
	win.addstr(1, c15_xPos, "ENABLED      ", curses.color_pair(1))
	win.addstr(1, c16_xPos, "MODE       ", curses.color_pair(1))
	win.addstr(1, c17_xPos, "W/L      ", curses.color_pair(1))
	win.addstr(1, c18_xPos, "STATUS   ", curses.color_pair(1))

	yPos = 2

	startMarketIndex = GVAR.SCREEN_WIN_poolMonitor_marketIndex_start
	endMarketIndex = GVAR.SCREEN_WIN_poolMonitor_marketIndex_end

	marketCounter = 0
	sorted_POOL = []

	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = GVAR.POOL_markets.get(mName)

		mIDP_data = mData['IDLE_distance_percent']
		if (mIDP_data != "") : mIDP = float(mIDP_data)
		else : mIDP = 100

		position = -1
		for item in sorted_POOL :
			
			position += 1
			iName = str(item)
			iData = GVAR.POOL_markets.get(iName)
			iIDP_data = iData['IDLE_distance_percent']
			
			if (iIDP_data != "") : iIDP = float(iIDP_data)
			else : iIDP = 100

			if (iIDP < mIDP) :
				break
			
		sorted_POOL.insert(position, market)

	for market in sorted_POOL :

		marketCounter += 1

		if ((marketCounter >= startMarketIndex) & (marketCounter <= endMarketIndex)) :
		
			mName = str(market)
			mData = GVAR.POOL_markets.get(mName)

			mEnabled = mData['MARKET_enabled']
			mStatus = mData['MARKET_status']

			mSymbol = mData['MARKET_symbol']
			mSellSymbol = mData['SELL_symbol']

			mPriceMarket = mData['PRICE_market']	
			mPriceBuyStop = mData['PRICE_BUY_stop']
			mPriceBuyLimit = mData['PRICE_BUY_limit']
			mPriceIdleLimit = mData['PRICE_IDLE_limit']

			mPriceBuyUpdated = mData['PRICE_BUY_updated']

			mPriceBuyMargin = mData['PRICE_BUY_margin']
			mPriceSellMargin = mData['PRICE_SELL_margin']
			
			mRounderPrices = int(mData['TRADE_round_prices'])

			mBuyAmount = mData['TRADE_ASSET_amount']

			mIdleDistP = mData['IDLE_distance_percent']
			mIdleMarginP = mData['IDLE_margin_percent']
			if(mEnabled == True) :
				mIdleDistPStr = str(mIdleDistP).rjust(7) + " %"
				mIdleMarginPStr = str(mIdleMarginP) + " %"
			else :
				mIdleDistPStr = ""
				mIdleMarginPStr = ""

			mIdleTime = "0:0:0"

			mTradeCounterWins = mData['TRADE_COUNTER_wins']
			mTradeCounterLooses = mData['TRADE_COUNTER_looses']
			
			mWinsLoosesStr = str(mTradeCounterWins) + "/" + str(mTradeCounterLooses)

			mMarketEnabled = mData['MARKET_enabled']
			mTradeMode = mData['TRADE_mode']
			mIdlePrio = mData['IDLE_priority_index']

			mLotSize = round(float(mPriceBuyStop * mBuyAmount), mRounderPrices)
			mLotSizeStr = str(mLotSize) + " " + mSellSymbol

			# =====================================================================

			win.addstr(yPos, c1_xPos, mName.ljust(12))
			win.addstr(yPos, c2_xPos, mSymbol.ljust(12))

			mPriceMarketStr = str(mPriceMarket).ljust(9) + " " + mSellSymbol
			win.addstr(yPos, c3_xPos, mPriceMarketStr.ljust(14), curses.color_pair(3))

			if (mIdleDistP > 0) :
				win.addstr(yPos, c4_xPos, mIdleDistPStr.ljust(8), curses.color_pair(7))
			else :
				win.addstr(yPos, c4_xPos, mIdleDistPStr.ljust(8))
			
			win.addstr(yPos, c5_xPos, str(mPriceIdleLimit).ljust(12))
			win.addstr(yPos, c6_xPos, mIdleMarginPStr.ljust(7))

			if(mPriceBuyUpdated == True) :
				win.addstr(yPos, c7_xPos, str(mPriceBuyStop).ljust(10), curses.color_pair(7))
			else:
				win.addstr(yPos, c7_xPos, str(mPriceBuyStop).ljust(10))
			
			win.addstr(yPos, c8_xPos, str(mPriceBuyLimit).ljust(10))
			win.addstr(yPos, c9_xPos, str(mPriceBuyMargin).ljust(7))
			win.addstr(yPos, c10_xPos, str(mPriceSellMargin).ljust(7))
			win.addstr(yPos, c11_xPos, str(mBuyAmount).ljust(8))
			win.addstr(yPos, c12_xPos, mLotSizeStr)
			win.addstr(yPos, c13_xPos, str(mIdlePrio))
			win.addstr(yPos, c14_xPos, str(mIdleTime))
			win.addstr(yPos, c15_xPos, str(mMarketEnabled).ljust(5))
			win.addstr(yPos, c16_xPos, str(mTradeMode))
			win.addstr(yPos, c17_xPos, str(mWinsLoosesStr))

			if(mStatus == "IDLE") :
				colorPair = 0
			elif(mStatus == "READY") :
				colorPair = 3
			elif(mStatus == "TRADING") :
				colorPair = 2
			elif(mStatus == "OFF") :
				colorPair = 4

			win.addstr(yPos, c18_xPos, str(mStatus).ljust(7), curses.color_pair(colorPair))

			# =====================================================================

			yPos += 1

	#win.refresh()
	
def SCREEN_WIN_log_printLine(PARAM_lineStr) :

	# Text start xPosition inside the log window
	xPos = 2
	endMargin = 2

	logSize = len(GVAR.SCREEN_WIN_log_lines)
	maxSize = GVAR.SCREEN_WIN_log_size
	maxWidth = GVAR.SCREEN_WIN_log_width - xPos - endMargin

	if (logSize == maxSize) :
		GVAR.SCREEN_WIN_log_lines.pop(0)

	newLineStr = PARAM_lineStr
	
	if (len(newLineStr) < maxWidth) :

		lenDiff = maxWidth - len(newLineStr)
		addCount = 0
		#win.addstr(0,0,">>> lenDiff = " + str(lenDiff) + " >>>  ")

		while(addCount < lenDiff) :
			
			newLineStr = newLineStr + " "
			addCount += 1

	else :

		newLineStr = PARAM_lineStr[:maxWidth]

	GVAR.SCREEN_WIN_log_lines.append(newLineStr)

	logFile = GVAR.SCREEN_WIN_log_dir + "/" + GVAR.SCREEN_WIN_log_file
	SYS_IO_writeFile(logFile, newLineStr)


def SCREEN_WIN_log_refresh(PARAM_win) :

	defName = "SCREEN_WIN_log_refresh: "
	win = PARAM_win

	# Text start xPosition inside the log window
	xPos = 2
	endMargin = 2

	logLines = GVAR.SCREEN_WIN_log_lines

	#curses.curs_set(0)
	yPos = 0

	maxSize = GVAR.SCREEN_WIN_log_size
	
	# If something goes wrong and logLines is bigger than it should be -> Reduce logLines
	# Many times logLines exceeded size by an extra line (unkown why with threads)
	if(len(logLines) > maxSize) :

		bprint(defName + "<< WARNING >> Size of log exceeded (GVAR.SCREEN_WIN_log_lines = " + str(len(logLines)) + " > GVAR.SCREEN_WIN_log_size = " + str(maxSize) + " -> Reducing log size..")
		
		safeSize = maxSize - 1
		GVAR.SCREEN_WIN_log_lines = GVAR.SCREEN_WIN_log_lines[-safeSize:]
		logLines = GVAR.SCREEN_WIN_log_lines

	for item in logLines :

		yPos += 1

		try:

			win.addstr(yPos, xPos, str(item))

		except Exception as e:

			e = sys.exc_info()
			ERROR_printer(e,defName)
			bprint("")
			bprint(defName + "<<< ERROR >>> Printing log line -> Skip printing this line on log screen")
			bprint(defName + "<<< ERROR >>> yPos = " + str(yPos) + " | xPos = " + str(xPos))
			bprint(defName + "<<< ERROR >>> item = " + str(item))
			bprint(defName + "<<< ERROR >>> Clearing vars yPos = 0, xPos = 2, item = None")
			bprint("")

			yPos = 0
			xPos = 2
			item = None
			MICRO_sleep(1)
			continue

def SCREEN_monochromer(PARAM_enabled) :

	defName = "SCREEN_monochromer: "

	if PARAM_enabled == False :

		bprint(defName + "Monochrome mode DISABLED")

		pcolors.GREEN = '\033[92m'
		pcolors.BLUE = '\033[34m'
		pcolors.RED = '\033[91m'
		pcolors.VIOLET = '\33[95m'
		pcolors.YELLOW = '\33[93m'
		pcolors.TUR = '\33[96m'

		pcolors.FAIL = '\033[91m'
		pcolors.BOLD = '\033[1m'
		pcolors.UNDERLINE = '\033[4m'
		pcolors.WARNING = '\033[93m'
		pcolors.ENDC = '\033[0m'

		pcolors.BLINK    = '\33[5m'
		pcolors.BLINK2   = '\33[6m'
		pcolors.SELECTED = '\33[7m'

	else :

		bprint(defName + "Monochrome mode ENABLED")

		pcolors.GREEN = ''
		pcolors.BLUE = ''
		pcolors.RED = ''
		pcolors.VIOLET = ''
		pcolors.YELLOW = ''
		pcolors.TUR = ''

		pcolors.FAIL = ''
		pcolors.BOLD = ''
		pcolors.UNDERLINE = ''
		pcolors.WARNING = ''
		pcolors.ENDC = ''

		pcolors.BLINK    = ''
		pcolors.BLINK2   = ''
		pcolors.SELECTED = ''

def SCREEN_cmdLine(PARAM_inputStr) :

	defName = "SCREEN_cmdLine: "

	inputStr = PARAM_inputStr.strip()
	inputList = ARGplusparser(inputStr, " ")

	cmd = ""
	arg1 = ""
	arg2 = ""

	argsCount = 0

	if (inputStr.strip() != "") :

		if (len(inputList) >= 1 ) :
			cmd = inputList[0]
			argsCount = 1
		
		if (len(inputList) >= 2) :
			arg1 = inputList[1]
			argsCount = 2

		if (len(inputList) >= 3) :
			arg2 = inputList[2]
			argsCount = 3

		if (len(inputList) >= 4) :
			arg3 = inputList[3]
			argsCount = 4

	if(GVAR.MODE_VERBOSE_events == True) :
		bprint(defName + "New input cmd='" + cmd + "' arg1='" + arg1 + "' arg2='" + arg2 + "'")

	if (cmd == "clear") :

		GVAR.SCREEN_WIN_log_lines = []
		GVAR.SCREEN_WIN_log.erase()
		GVAR.SCREEN_WIN_log.border(0)
		#GVAR.SCREEN_WIN_log.refresh()

	elif (cmd == "help") :

		bprint("")
		bprint("Available commands: " + arg1)
		bprint("")

		if (arg1 == "") :

			bprint("help trading                                        -> trading commands")
			bprint("help config                                         -> configuration load / save commands")
			bprint("help ui                                             -> user interface commands")

		if (arg1 == "ui") :

			bprint("clear                                               -> Clears log win                            | refresh                                             -> Refresh curses screen")
			bprint("init                                                -> Exec init commands sequence               | init_debug <FUNDS_LIMIT:float>                      -> Init debug trading using FUNDS_LIMIT")
			bprint("get_market_fill <MARKET:string> <SIDE:string>       -> Get last fill price on SIDE for MARKET    | mtop                                                -> Shows top markets order by IDLE DP")
			bprint("print_cfb                                           -> Prints CFB limits and values settings     | mbottom                                             -> Shows bottom markets order by IDLE DP")
			bprint("+ / -                                               -> Moves markets lists from top to bottom     ")

		if (arg1 == "trading") :

			bprint("sms / set_market_stop <MARKET:string> <PRICE:float> -> Sets BUY STOP price for especific MARKET  | set_market_mbuy <MARKET:string> <MARGIN:float>      -> Sets BUY price MARGIN for MARKET")
			bprint("set_market_idle <MARKET:string> <IDLEmP:float>      -> Sets IDLE margin percent for MARKET       | set_market_msell <MARKET:string> <MARGIN:float>     -> Sets SELL price MARGIN for MARKET")
			bprint("set_market_enabled <MARKET:string> <bool>           -> Enables / disables verbose mode for LOOPS | set_market_amount <MARKET:string> <AMOUNT:float>    -> Sets BUY asset AMOUNT for MARKET")
			bprint("set_market_mode <MARKET:string> <MODE:string>       -> Sets trading MODE for especific MARKET    | set_amounts_max                                     -> Sets MAX available amount for all MARKETS")
			bprint("smp / set_market_prio <MARKET:string> <PRIO:int>    -> Sets PRIORITY index (level) for MARKET    | checkfunds                                          -> Request and update server available funds")
			bprint("app / set_market_approach <MARKET:string>           -> Sets MARKET BUY STOP near market price    | set_markets_enabled <bool>                          -> Enable / disable ALL markets")
			bprint("trade_abort                                         -> Aborts current trade                       ")

		if (arg1 == "config") :

			bprint("lpr / load_pool_reg                                 -> Load POOL register file                   | spr / save_pool_reg                                 -> Save POOL register file")
			bprint("set_mode_verbose_events <bool>                      -> Enables / disables verbose EVENTS mode    | set_mode_verbose_loops <bool>                       -> Enables / disables verbose LOOPS mode")
			bprint("set_pool_monitor_nap <float>                        -> Sets POOL monitor nap time in seconds     | stp / set_tickers_paused <bool>                     -> Enables / disables price updates")
			bprint("set_pool_backup                                     -> Sets backups vars for markets")
	
	elif (cmd == "save_pool_reg") or (cmd == "spr") :

		POOL_regSave(True)

	elif (cmd == "load_pool_reg") or (cmd == "lpr") :

		POOL_regLoad(True)

	elif (cmd == "set_pool_backup") :

		POOL_backup()

	elif (cmd == "refresh") :

		GVAR.SCREEN_screen.erase()
		GVAR.SCREEN_screen.redrawwin()
		GVAR.SCREEN_screen.refresh()

		GVAR.SCREEN_WIN_log.border(0)
		GVAR.SCREEN_WIN_status.border(0)
		GVAR.SCREEN_WIN_trader.border(0)
		GVAR.SCREEN_WIN_poolMonitor.erase()
		GVAR.SCREEN_WIN_poolMonitor.border(0)
		GVAR.SCREEN_WIN_logo.border(0)

	elif (cmd == "get_market_fill") :

		if (argsCount == 4) :

			marketName = arg1
			side = arg2
			orderId = arg3

			bprint(defName + "Calling POOL_marketGetFillData with : < " + marketName + " > < " + side + " > < " + orderId +  " >")
			
			resp = POOL_marketGetLastFillData(marketName, side)

			bprint(defName + "POOL_marketGetFillData returned: " + str(resp))

		else :

			bprint(defName + "get_market_fill takes 3 args (marketName, side, orderId)")

	elif (cmd == "print_cfb") :

		CFB_limits = ""
		CFB_values = ""

		CFB_limits = "[ "
		for item in GVAR.MODE_VARS.SELL_CFB_lnMP_limits :
			CFB_limits = CFB_limits + str(item).ljust(5) + ", "
		CFB_limits = CFB_limits + " ]"

		CFB_values = "[ "
		for item in GVAR.MODE_VARS.SELL_CFB_lnMP_values :
			CFB_values = CFB_values + str(item).ljust(5) + ", "
		CFB_values = CFB_values + " ]"

		bprint(defName + "These are current CFB (Chase From Below) limits and values settings:")
		bprint(defName + "CFB LIMITS: " + CFB_limits)
		bprint(defName + "CFB VALUES: " + CFB_values)

	elif (cmd == "checkfunds") :

		POOL_fundsCheck()

	elif (cmd == "init") :

		POOL_fundsCheck()

		sleep(3)
		
		POOL_regLoad(True)
		POOL_setMaxAmounts()
		GVAR.POOL_tickers_paused = False
		
		sleep(3)

		POOL_setAllMarketsEnabled(True)
		GVAR.TRADER_paused = False

	elif (cmd == "mtop") :

			GVAR.SCREEN_WIN_poolMonitor_marketIndex_start = 1
			GVAR.SCREEN_WIN_poolMonitor_marketIndex_end = 22
			GVAR.SCREEN_WIN_poolMonitor.erase()
			GVAR.SCREEN_WIN_poolMonitor.box()

	elif (cmd == "mbottom") :

			marketsCount = len(GVAR.POOL_markets)
			GVAR.SCREEN_WIN_poolMonitor_marketIndex_end = marketsCount
			GVAR.SCREEN_WIN_poolMonitor_marketIndex_start = GVAR.SCREEN_WIN_poolMonitor_marketIndex_end - 20
			GVAR.SCREEN_WIN_poolMonitor.erase()
			GVAR.SCREEN_WIN_poolMonitor.box()
			
	elif (cmd == "init_debug") :

		if (argsCount == 2) :

			funds_limit = float(arg1)

			GVAR.POOL_FUNDS_limit = funds_limit
			GVAR.POOL_tickers_paused = False
			sleep(3)

			POOL_marketSetApproach("BTC")
			POOL_marketSetApproach("ETH")
			POOL_marketSetApproach("LINK")
			POOL_marketSetApproach("ZEC")
			POOL_marketSetApproach("XMR")
			POOL_marketSetApproach("COMP")
			POOL_marketSetApproach("BNB")
			POOL_marketSetApproach("BTT")
			POOL_marketSetApproach("ALGO")
			POOL_marketSetApproach("DOGE")
			POOL_marketSetApproach("BNT")
			POOL_marketSetApproach("JST")
			POOL_marketSetApproach("SNX")
			
			POOL_setAllMarketsEnabled(True)

			GVAR.TRADER_paused = False

		else :

			bprint(defName + "init_debug takes 1 argument (arg1 = float<FUNDS_limit>)")

	elif (cmd == "set_tickers_paused") or (cmd == "stp"):

		if (argsCount == 2) :
			
			GVAR.POOL_tickers_paused = eval(arg1)
			bprint(defName + "Set GVAR.POOLS_tickers_paused = " + str(arg1)) 

	elif (cmd == "set_pool_monitor_nap") :

		if (argsCount == 2) :

			mArg = arg1
			GVAR.POOL_monitor_nap = float(mArg)
			bprint("")
			bprint(defName + "Set POOL monitor nap in seconds -> GVAR.POOL_monitor_nap = " + str(GVAR.POOL_monitor_nap))
			bprint("")

	elif (cmd == "set_mode_verbose_events") :

		if (argsCount == 2) :

			boolArg = arg1
			GVAR.MODE_VERBOSE_events = eval(boolArg)
			bprint("")
			bprint(defName + "EVENTS verbose mode -> GVAR.MODE_VERBOSE_events = " + str(GVAR.MODE_VERBOSE_events))
			bprint("")

	elif (cmd == "set_mode_verbose_loops") :

		if (argsCount == 2) :

			boolArg = arg1
			GVAR.MODE_VERBOSE_loops = eval(boolArg)

			bprint("")
			bprint(defName + "LOOPS verbose mode -> GVAR.MODE_VERBOSE_loops = " + str(GVAR.MODE_VERBOSE_loops))
			bprint("")

	elif (cmd == "set_market_stop") or (cmd == "sms") :

		if (argsCount == 3) :

			POOL_marketSetPriceStop(arg1, arg2)

	elif (cmd == "set_market_prio") or (cmd == "smp") :

		if (argsCount == 3) :

			POOL_marketSetPrio(arg1, arg2)

	elif (cmd == "set_market_amount") :

		if (argsCount == 3) :

			POOL_marketSetAmount(arg1, arg2)

	elif (cmd == "set_amounts_max") :

		POOL_setMaxAmounts()

	elif (cmd == "set_market_idle") :

		if (argsCount == 3) :

			POOL_marketSetIdleMP(arg1, arg2)
	
	elif ((cmd == "set_market_approach") or (cmd == "app")) :

		if (argsCount == 2) :

			POOL_marketSetApproach(arg1)

	elif (cmd == "set_market_mbuy") :

		if (argsCount == 3) :

			POOL_marketSetPriceMargin("BUY",arg1, arg2)

	elif (cmd == "set_market_msell") :

		if (argsCount == 3) :

			POOL_marketSetPriceMargin("SELL",arg1, arg2)

	elif (cmd == "trade_abort") :

		if (argsCount == 1) :

			if(GVAR.BUY_mode_on == True) :
				GVAR.TRADER_mode = "ABORT_BUY"
				GVAR.BUY_mode_on = False

			if(GVAR.SELL_mode_on == True) :
				GVAR.TRADER_mode = "ABORT_SELL"
				GVAR.SELL_mode_on = False
			
			if(TRADER_marketName != None) :
				
				POOL_marketSetEnabled(TRADER_marketName, False)

	elif (cmd == "set_market_enabled") :

		if (argsCount == 3) :

			marketName = arg1
			boolVar = arg2
			POOL_marketSetEnabled(marketName, boolVar)

	elif (cmd == "set_markets_enabled") :

		if (argsCount == 2) :

			boolVar = arg1
			POOL_setAllMarketsEnabled(boolVar)

	elif (cmd == "set_market_mode") :

		if (argsCount == 3) :

			marketName = arg1
			marketFound = False

			for market in GVAR.POOL_markets :

				mName = str(market)

				if (mName == marketName) :

					mData = GVAR.POOL_markets.get(mName)
					marketFound = True
					new_mode = arg2 
					GVAR.POOL_markets[mName]['TRADE_mode'] = new_mode
					
					bprint(defName + "Set market " + marketName + " mode: " + str(new_mode))

			if (marketFound == False) :

				bprint(defName + "ERROR: Unknown market name")

	else :

		bprint(defName + "Command unkown")

def POOL_reload(PARAM_poolFileName) :
	
	defName = "POOL_reload: "

	poolsDir = GVAR.POOLS_DIR_pools
	poolFile = "./" + poolsDir + "/" + PARAM_poolFileName + GVAR.POOLS_ext

	bprint(defName + "Reseting POOL config vars..")

	GVAR.POOL_name = None
	GVAR.POOL_markets = []

	bprint("")
	bprint(defName + "Loading pool file: " + poolFile)

	with open(poolFile, "r") as pfile :
		poolData = yaml.safe_load(pfile)

	poolName = poolData["CONFIG"]["name"]
	GVAR.POOL_name = poolName
	
	GVAR.POOL_FUNDS_symbol = poolData['CONFIG']['FUNDS_symbol']
	GVAR.POOL_FUNDS_seek = poolData['CONFIG']['FUNDS_limit']
	GVAR.POOL_FUNDS_stop = poolData['CONFIG']['FUNDS_stop']
	
	bprint(defName + "Pool name: " + poolName)

	rawMarkets = poolData['MARKETS']
	GVAR.POOL_rawData = rawMarkets
	
	# Transform yaml pool-config file into usable list of dictionaries with fresh data
	POOL_compiler(GVAR.POOL_rawData)
	
	marketsCount = len(GVAR.POOL_rawData)
	
	bprint(defName + "Loaded " + str(marketsCount) + " markets from pool: " + PARAM_poolFileName )

def POOL_regSave (PARAM_verbose) :

	defName = "POOL_regSave: "

	regPath = "./" + GVAR.POOLS_DIR_pools + "/" + GVAR.POOLS_DIR_registers + "/"
	fileName = GVAR.POOL_name + ".reg"

	regFile = regPath + fileName

	outputDict = {}

	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = GVAR.POOL_markets.get(mName)

		mPriceBuyStop = mData['PRICE_BUY_stop']
		mPriceBuyLimit = mData['PRICE_BUY_limit']
		mPriceIdleLimit = mData['PRICE_IDLE_limit']
		mMarketEnabled = mData['MARKET_enabled']
		mTradeMode = mData['TRADE_mode']
		mIdlePrio = mData['IDLE_priority_index']
		mIdleMP = mData['IDLE_margin_percent']
		mPriceBuyMargin = mData['PRICE_BUY_margin']
		mPriceSellMargin = mData['PRICE_SELL_margin']
		mTradeAssetAmount = mData['TRADE_ASSET_amount']
		mTradeCounterWins = mData['TRADE_COUNTER_wins']
		mTradeCounterLooses = mData['TRADE_COUNTER_looses']

		dataList = {}
		dataList["PRICE_BUY_stop"] = mPriceBuyStop
		dataList["PRICE_BUY_limit"] = mPriceBuyLimit
		dataList["PRICE_IDLE_limit"] = mPriceIdleLimit
		dataList['MARKET_enabled'] = mMarketEnabled
		dataList['TRADE_mode'] = mTradeMode
		dataList['IDLE_priority_index'] = mIdlePrio
		dataList['IDLE_margin_percent'] = mIdleMP
		dataList['PRICE_BUY_margin'] = mPriceBuyMargin
		dataList['PRICE_SELL_margin'] = mPriceSellMargin
		dataList['TRADE_ASSET_amount'] = mTradeAssetAmount
		dataList['TRADE_COUNTER_wins'] = mTradeCounterWins
		dataList['TRADE_COUNTER_looses'] = mTradeCounterLooses

		outputDict[mName] = dataList

	with open(regFile , "w") as rfile :

		yaml.dump(outputDict, rfile, default_flow_style=False)

	if(PARAM_verbose == True) :
		bprint(defName + "Pool register file (" + fileName + ") saved OK" )	

	devprint(GVAR.MODE_VERBOSE_events, defName + "Pool register file (" + fileName + ") saved OK" )

def POOL_regLoad (PARAM_verbose) :

	defName = "POOL_regLoad: "

	regPath = "./" + GVAR.POOLS_DIR_pools + "/" + GVAR.POOLS_DIR_registers + "/"
	fileName = GVAR.POOL_name + ".reg"
	regFile = regPath + fileName
	
	with open(regFile, "r") as rfile :
		regData = yaml.safe_load(rfile)

	bprint(defName + "Pool register file (" + fileName + ") loaded OK")
	bprint(defName + str(regData))

	for market in regData :

		mName = str(market)
		mData = regData.get(mName)

		GVAR.POOL_markets[mName]['PRICE_BUY_updated'] = False

		for item in mData :

			itemKey = str(item)
			itemValue = mData.get(itemKey)

			bprint(defName + "Setting GVAR.POOL_markets['" + mName + "']['" + itemKey + "'] = " + str(itemValue))
			
			GVAR.POOL_markets[mName][itemKey] = itemValue

	if(PARAM_verbose == True) :
		bprint(defName + "Register file (" + fileName + ") loaded OK")
		bprint("")

def POOL_monitor ():

	defName = "POOL_monitor: "

	monitor_enabled = True
	
	FUNDS_ERROR_notified = False

	while (monitor_enabled == True) :

		#POOL_counter()

		# When TRADER thread is paused do not re-order markets
		if(GVAR.TRADER_paused == False) :

			# Step 1 -> Analize IDLE condition of each market
			for market in GVAR.POOL_markets :
				mName = str(market)
				POOL_marketIdleCheck(mName)

			# Step 2 -> Find TOP priority of READY markets
			nextMarket = None
			nextMarket = POOL_prioRanker(0,False)
			
			# Step 3 -> Depending the order result start trading or clean variables
			if (nextMarket == None) :
				
				if(GVAR.TRADE_mode_on == False) :
				
					if(GVAR.TRADER_marketName == None) :
					
						if(GVAR.TRADER_mode != None) :
							bprint(defName + "No next market -> Set TRADER_mode = None")
							GVAR.TRADER_mode = None

			else :

				# If no trading going on..
				if (GVAR.TRADE_mode_on == False) :
					
					if (GVAR.TRADER_paused == False) :
					
						if (GVAR.POOL_FUNDS_enabled == True) :

							bprint ("")
							bprint (defName + ">>> DEBUG >>> nextMarket: " + str(nextMarket))

							bprint (defName + "Checking BUY order settings for market " + nextMarket + " before enabling trade mode..")
							
							validOrder = POOL_marketOrderValidator(nextMarket, "BUY")
							
							if (validOrder == True) :

								GVAR.TRADER_marketName = nextMarket
								GVAR.TRADER_mode = "BUY"
								GVAR.TRADE_mode_on = True
								FUNDS_ERROR_notified = False

								bprint(defName + "Next market READY to go (" + str(nextMarket) + ") -> Set TRADE_mode_on = " + str(GVAR.TRADE_mode_on) + " | TRADER_mode = " + str(GVAR.TRADER_mode) + " | TRADER_marketName = " + str(GVAR.TRADER_marketName))

							else :

								bprint(defName + "Not valid BUY order settings to start trade -> Disabling market " + nextMarket)
								POOL_marketSetEnabled(mName, False)
								GVAR.TRADER_marketName = None
								GVAR.TRADER_mode = None
								GVAR.TRADER_mode_on = False
								FUNDS_ERROR_notified = False
						
						else :

							if(FUNDS_ERROR_notified == False) :
								FUNDS_ERROR_notified = True
								bprint(defName + "Pool funds NOT enabled (GVAR.POOL_FUNDS_enabled = " + str(GVAR.POOL_FUNDS_enabled) + ")")
								bprint(defName + "Probably not enough FREE funds for trading (POOL_FUNDS_min = " + str(POOL_FUNDS_min) + " " + str(POOL_FUNDS_symbol) + ")")

		THREADS_aliveSignal("POOL_monitor")

		MICRO_sleep(GVAR.POOL_monitor_nap)

		if (GVAR.FLAG_main_thread_exit == True) :

			curses.endwin()
			quit()

def POOL_prioRanker(PARAM_returnPosition, PARAM_printReadyList) :

	defName = "POOL_prioRanker: "

	# This function creates a list of tuples (marketName, prioIndex)
	# The list is made of ervery market from GVAR.POOL_markets list where MARKET_status == READY 
	# The list is built ordered by IDLE_priority_index (0 is highest priority)
	
	# So the list is a ranking of markets ordered by priority index
	# where each item of the new readyList is a market that is ready to trade

	# readyList[0][0] is the marketName that has 1st priority in all "READY" markets
	# readyList[1][0] is the marketName that has 2nd priority in all "READY" markets
	# readyList[n][0] is the marketName that has Nst priority in all "READY" markets

	readyList = None

	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = GVAR.POOL_markets.get(mName)

		if(mData['MARKET_status'] == "READY") :
			
			mPrioIndex = mData['IDLE_priority_index']
			newItem = (mName, mPrioIndex)

			if(readyList == None) :

				readyList = [newItem]
			
			else :
				
				index = 0
				for item in readyList :

					itemPrio = item[1]
					newItemPrio = mPrioIndex

					if(newItemPrio < itemPrio) :
						
						readyList.insert(index, newItem)
						break
						
					else :
					
						if (index == (len(readyList) - 1)) :

							readyList.append(newItem)
						
						else:

							index += 1

	if (readyList != None) :
		counter = 0
		for item in readyList :

			if(PARAM_printReadyList == True) :
				bprint(defName + "ReadyList pos(" + str(counter) + ") = " + str(item))
				counter += 1
	
		if(PARAM_returnPosition > (len(readyList) - 1)) :
			# if PARAM_returnPosition asked doesn't exist (less items in readyList than returnPosition)
			return None
		else :
			# if returnPosition exists in readyList -> return marketName (readyList is a list of tuples (marketName, prioIndex))
			return readyList[PARAM_returnPosition][0]

	else :

		return None

def POOL_idleLimitReCalc(PARAM_marketName) :

	defName = "POOL_idleLimitReCalc: "

	mName = PARAM_marketName

	marketSymbol = GVAR.POOL_markets[mName]['MARKET_symbol']
	sellSymbol = GVAR.POOL_markets[mName]['SELL_symbol']

	price_rounder = GVAR.POOL_markets[mName]['TRADE_round_prices']
	price_margin_buy = GVAR.POOL_markets[mName]['PRICE_BUY_margin']
	price_margin_idle = GVAR.POOL_markets[mName]['IDLE_margin_percent']
	price_market = GVAR.POOL_markets[mName]['PRICE_market']

	price_stop_current = float(GVAR.POOL_markets[mName]['PRICE_BUY_stop'])
	price_limit_current = float(GVAR.POOL_markets[mName]['PRICE_BUY_limit'])
	idle_limit_current = float(GVAR.POOL_markets[mName]['PRICE_IDLE_limit'])

	price_cache_max = GVAR.POOL_markets[mName]['PRICE_CACHE_market_max']
	
	price_stop_new = round(price_cache_max[1] + price_margin_buy, price_rounder)
	price_limit_new = round(price_stop_new + price_margin_buy, price_rounder)
	idle_limit_new = calcIdlePriceLimit(price_stop_new, price_margin_idle, price_rounder)

	bprint(defName + "Doing IDLE re-calc for market " + mName + " (" + marketSymbol + ") ..")
	bprint(defName + "Current MARKET    price: " + str(price_market) + " " + sellSymbol)
	bprint(defName + "Current Cache MAX price: " + str(price_cache_max) + " " + sellSymbol)
	bprint(defName + "New BUY STOP   price: " + str(price_stop_new) + " " + sellSymbol + " (current BUY STOP: " + str(price_stop_current) + " )")
	bprint(defName + "New BUY LIMIT  price: " + str(price_limit_new) + " " + sellSymbol + " (current BUY LIMIT: " + str(price_limit_current) + " )")
	bprint(defName + "New IDLE LIMIT price: " + str(idle_limit_new) + " " + sellSymbol + " (current IDLE LIMIT: " + str(idle_limit_current) + " )")
	bprint(defName + "Checking if NEW STOP, LIMIT, IDLE prices should be applied (if NEW BUY STOP > Current PRICE STOP) ..")

	if(price_stop_new > price_stop_current) :

		bprint(defName + "Applying NEW STOP, LIMIT, IDLE prices..")

		GVAR.POOL_markets[mName]['PRICE_BUY_stop'] = price_stop_new
		GVAR.POOL_markets[mName]['PRICE_BUY_limit'] = price_limit_new
		GVAR.POOL_markets[mName]['PRICE_IDLE_limit'] = idle_limit_new
	
		bprint(defName + "GVAR.POOL_markets[" + mName + "]['PRICE_CACHE_market_max'] = " + str(price_cache_max))
		bprint(defName + "New BUY_price_stop = " + str(price_stop_new))
		bprint(defName + "New BUY_price_limit = " + str(price_limit_new))
		bprint(defName + "New IDLE_price_limit = " + str(idle_limit_new))
		bprint(defName + "Updating market assets max amounts (price rised) ..")
		POOL_marketSetMaxAmount(mName)
		bprint(defName + "Saving POOL registry with new IDLE limit..")

		POOL_regSave(False)

	else :

		bprint("")
		bprint(defName + "Current BUY " + pcolors.YELLOW + "STOP, LIMIT, IDLE" + pcolors.ENDC + " are " + pcolors.GREEN + "OK" + pcolors.ENDC + " (BUY_price_stop > new_price_stop)")
		bprint(defName + "Using current BUY_price_stop = " + str(price_stop_current))
		bprint(defName + "Using current BUY_price_limit = " + str(price_limit_current))
		bprint(defName + "Using current IDLE_price_limit = " + str(idle_limit_current))
		bprint("")
	
def POOL_tickerCacher(PARAM_marketName, PARAM_time, PARAM_price) :

	mName = PARAM_marketName

	timeStr = str(PARAM_time)
	priceF = float(PARAM_price)
	tickerItem = (timeStr, priceF)

	maxLenght = GVAR.STATISTICS_TICKER_cache_size

	if (len(GVAR.STATISTICS_TICKER_cache) == maxLenght) :
		GVAR.POOL_markets[mName]['PRICE_CACHE_market'].pop(0)

	GVAR.POOL_markets[mName]['PRICE_CACHE_market'].append(tickerItem)

	current_max = GVAR.POOL_markets[mName]['PRICE_CACHE_market_max']
	if(current_max == None) :		
		GVAR.POOL_markets[mName]['PRICE_CACHE_market_max'] = tickerItem
	else :		
		if(priceF > current_max[1]) :
			GVAR.POOL_markets[mName]['PRICE_CACHE_market_max'] = tickerItem

	MARKET_CACHE_analizer(mName)

def POOL_pricer() :

	defName = "POOL_pricer: "

	GVAR.POOL_pricer_enabled = True

	while (GVAR.POOL_pricer_enabled == True) :

		if (GVAR.POOL_tickers_paused == False) :

			try:

				GVAR.POOL_tickers = EXCHANGE_TICKER_GetAllTickersData()

				for item in GVAR.POOL_tickers :

					symbol = item['symbol']
					price = float(item['price'])

					for market in GVAR.POOL_markets :

						marketName = str(market)
						marketData = GVAR.POOL_markets.get(marketName)

						if(marketData['MARKET_symbol'] == symbol) :

							rounder = int(marketData['TRADE_round_prices'])
							rounded_price = round(price, rounder)
							GVAR.POOL_markets[marketName]['PRICE_market'] = rounded_price
							POOL_tickerCacher(marketName, TIME_getNowTime(), rounded_price)

				THREADS_aliveSignal("POOL_pricer")

				MICRO_sleep(GVAR.POOL_pricer_nap)

			except Exception as e:

				e = sys.exc_info()
				nowStr = TIME_getNowTime()

				logprint(GVAR.LOG_WARNINGS_name, defName + "<<< WARNING >>> POOL_pricer throwed Exception at " + nowStr + " -> Printing ERROR data..")
				ERROR_printer(e, defName)

def POOL_marketGetLastFillData(PARAM_marketName, PARAM_side) :

	defName = "POOL_marketGetLastFillData: "

	#fromOrderId = str(PARAM_orderId)
	side = str(PARAM_side)

	fillPrice = None
	
	mName = str(PARAM_marketName)
	mData = POOL_marketGetData(mName)
	
	if(mData) :

		mMarketSymbol = mData['MARKET_symbol']
		mRounderPrices = int(mData['TRADE_round_prices'])
		mRounderAmounts = int(mData['TRADE_round_amounts'])
		mBuySymbol = str(mData['BUY_symbol'])
		mSellSymbol = str(mData['SELL_symbol'])

		#bprint("")
		bprint(defName + "Getting order data for [ MARKET_name = " + mName + " ] [ MARKET_symbol " + mMarketSymbol + " ]")

		resp = EXCHANGE_TRADES_GetMyTrades(mMarketSymbol)

		# Re-order TRADES (server sends older first)
		resp.reverse()

		lastTradeFound = False
		biggestOrderId = None
		biggestOrderPrice = 0.0
		biggestOrderQty = 0.0

		totalQty = 0.0

		if (side == "BUY" ) :
			isBuyerValue = True
		elif (side == "SELL") :
			isBuyerValue = False

		bprint("")

		for tradeItem in resp :

			tradeOrderId = tradeItem['orderId']
			tradeIsBuyer = tradeItem['isBuyer']

			if(tradeIsBuyer == isBuyerValue) :
				
				tradePrice = tradeItem['price']
				
				tradeQty = tradeItem['qty']
				totalQty += float(tradeQty)

				tradeStr = side + " trades: < OrderId = " + str(tradeOrderId) + " > < isBuyer = " + str(tradeIsBuyer) + " > < price = " + str(tradePrice) + " > < qty = " + str(tradeQty) + " >"
				
				lastTradeFound = True
				if (tradeQty > biggestOrderQty) :
					
					biggestOrderId = tradeOrderId
					biggestOrderPrice = tradePrice
					biggestOrderQty = tradeQty

			else :

				if (lastTradeFound == False) :
					
					tradePrice = 0
					tradeQty = 0
					tradeStr = "OTHER trades: < OrderId = + " + str(tradeOrderId) + " > < isBuyer = " + str(tradeIsBuyer) + " >"

				else :

					# All first SELL and BUY orders already analized
					# Anything that comes after this belongs to an older trade on current symbol

					break

			bprint(defName + tradeStr)
		
		fillPrice = round(float(biggestOrderPrice), mRounderPrices)
		totalQtyRounded = round(float(totalQty), mRounderAmounts)
		
		bprint("")
		bprint(defName + "All " + side + " orders from last trade analized")
		bprint(defName + "Biggest order ID    : " + str(biggestOrderId))
		bprint(defName + "Biggest order Qty   : " + str(biggestOrderQty) + " " + mBuySymbol)
		bprint(defName + "Biggest order Price : " + str(biggestOrderPrice) + " " + mSellSymbol)
		bprint(defName + "Total Qty in orders : " + str(totalQty) + " " + mBuySymbol)
		bprint(defName + "Rounding trade-fill  price with: " + str(mRounderPrices) + " decimals")
		bprint(defName + "Rounding trade-qty amounts with: " + str(mRounderAmounts) + " decimals")
		bprint(defName + "Return { side : " + str(side) + " , fillPrice: " + str(fillPrice) + " , totalQty: " + str(totalQtyRounded) + " }")
		bprint("")

		# get_market_fill LINK BUY 59927672
		# get_market_fill ZEC BUY 16626437

		return { "side" : str(side) , "fillPrice" : fillPrice , "totalQty" : totalQtyRounded }

def SIMULATOR_TRADES_GetMyTrades (PARAM_marketName, PARAM_side) :

	defName = "SIMULATOR_TRADES_GetMyTrades: "
	
	orderId = str(PARAM_orderId)
	side = str(PARAM_side)

	fillPrice = None
	
	mName = str(PARAM_marketName)
	mData = POOL_marketGetData(mName)

	#resp = EXCHANGE_ORDER_GetData(orderId, mMarketSymbol)
	fillPrice = 0.0

	if (mData) :

		mMarketSymbol = mData['MARKET_symbol']
		mRounderPrices = int(mData['TRADE_round_prices'])

		bprint(defName + "<< WARNING >> Using FAKE middle-point trade fill for SIMULATED fill pricing..")

		if(side == "BUY") :

			mPriceStop = float(mData['PRICE_BUY_stop'])
			mPriceLimit = float(mData['PRICE_BUY_limit'])

			priceMidPoint = (mPriceStop + mPriceLimit) / 2
			fake_fill = round(priceMidPoint, mRounderPrices)

			bprint(defName + "[ PRICE_BUY_stop = " + str(mPriceStop) + " ] [ PRICE_BUY_limit = " + str(mPriceLimit) + " ] -> Return MID-POINT FAKE fill price: " + str(fake_fill))
		
		elif(side == "SELL") :

			mPriceStop = float(mData['PRICE_SELL_stop'])
			mPriceLimit = float(mData['PRICE_SELL_limit'])

			priceMidPoint = (mPriceStop + mPriceLimit) / 2
			fake_fill = round(priceMidPoint, mRounderPrices)

			bprint(defName + "[ PRICE_SELL_stop = " + str(mPriceStop) + " ] [ PRICE_SELL_limit = " + str(mPriceLimit) + " ] -> Return MID-POINT FAKE fill price: " + str(fake_fill))

		bprint("")

		fillPrice = fake_fill

	return fillPrice

def POOL_fundsCheck() :

	defName = "POOL_fundsCheck: "

	fundsSymbol = GVAR.POOL_FUNDS_symbol

	fundsBalanceData = EXCHANGE_ASSET_GetAssetBalance(fundsSymbol)
	rounder = 3

	fundsLocked = round(float(fundsBalanceData['locked']),rounder)
	fundsFree = round(float(fundsBalanceData['free']),rounder)
	fundsLimit = GVAR.POOL_FUNDS_seek
	fundsSeek = GVAR.POOL_FUNDS_seek
	fundsTotal = fundsLocked + fundsFree
	GVAR.POOL_FUNDS_locked = fundsLocked
	GVAR.POOL_FUNDS_free = fundsFree

	#fundsFree = GVAR.POOL_FUNDS_free
	#fundsLocked = GVAR.POOL_FUNDS_locked
	#fundsLimit = GVAR.POOL_FUNDS_limit
	#fundsSymbol = GVAR.POOL_FUNDS_symbol

	bprint(defName + "Checking FUNDS limit (" + str(fundsLimit) + " " + fundsSymbol + ") avalability..")

	if(fundsFree < fundsSeek) :

		GVAR.POOL_FUNDS_limit = fundsFree
		bprint(defName + "Not enough FREE funds for SEEK funds -> Re-calc NEW max limit -> GVAR.POOL_FUNDS_limit = " + str(GVAR.POOL_FUNDS_limit) + " " + fundsSymbol)
	
	else :

		GVAR.POOL_FUNDS_limit = fundsSeek
		bprint(defName + "Seek funds available -> POOL_FUNDS_limit = " + str(fundsLimit) + fundsSymbol)

	if(GVAR.POOL_FUNDS_limit < GVAR.POOL_FUNDS_min) :

		GVAR.POOL_FUNDS_enabled = False
		bprint(defName + "<<< WARNING >>> Not enough FREE funds to enable transactions -> Minimun FREE funds required GVAR.POOL_FUNDS_min = " + str(GVAR.POOL_FUNDS_min) + " " + fundsSymbol)
	
	else :

		GVAR.POOL_FUNDS_enabled = True
		bprint(defName + "Enough FREE funds available to enable transactions -> POOL_FUNDS_enabled = " + str(GVAR.POOL_FUNDS_enabled))

def POOL_setMaxAmounts() :

	defName = "POOL_setMaxAmounts: "

	bprint(defName + "Updating all markets BUY asset amount to max..")

	for market in GVAR.POOL_markets :

		mName = str(market)
		POOL_marketSetMaxAmount(mName)

	bprint(defName + "Amounts update done for all markets")

def POOL_marketSetMaxAmount(PARAM_marketName) :

	defName = "POOL_marketSetMaxAmount: "

	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	usableFundsP = 99.5

	if (mData) :

		buyPriceLimit = mData['PRICE_BUY_limit']
		currentAmount = mData['TRADE_ASSET_amount']

		if(buyPriceLimit > 0) :
		
			#assetSymbol = GVAR.POOL_markets[mName]['BUY_symbol']
			rounder = mData['TRADE_round_amounts']

			# Python round function uses Bankers method (round direction depends on the float decimals)
			# Use only 99.9% of free funds to avoid float rounding UP problems
			# Sometimes float UP rounding may result in non-available amounts (number bigger than available free limit funds)
			usableFunds = GVAR.POOL_FUNDS_limit * (usableFundsP / 100)

			bprint(defName + "GVAR.POOL_FUNDS_limit = " + str(GVAR.POOL_FUNDS_limit) + " -> Real approximate usable (" + str(usableFundsP) + " %) FUNDS: " + str(usableFunds))
			assetAmount = round(usableFunds / buyPriceLimit, rounder)
			
		else :

			assetAmount = 0
			bprint(defName + "Asset price = 0 for market " + mName + " -> TRADE_ASSET_amount = 0.00")

		mStatus = mData['MARKET_status']

		if((mStatus == "IDLE") or (mStatus == "OFF")) :

			GVAR.POOL_markets[mName]['TRADE_ASSET_amount'] = assetAmount
			bprint(defName + "New ASSET amount " + str(assetAmount) + " set for market " + mName + " (changed from OLD " + str(currentAmount) + " to NEW " + str(assetAmount) + ")")

		else:

			bprint(defName + "Couldn't change BUY AMOUNT (from current " + str(currentAmount) + " to " + str(assetAmount) + ") for market " + mName + " (NOT in IDLE mode, current STATUS = " + str(mStatus) + ")")

	else :

		bprint(defName + "ERROR: Unkown market " + mName)

def POOL_marketSetPrio(PARAM_marketName, PARAM_prio) :

	defName = "POOL_marketSetPrio: "
	
	marketFound = False
	prioFound = False

	marketName = PARAM_marketName
	newPrio = int(PARAM_prio)

	bprint(defName + "Setting new PRIORITY index (level) for market " + marketName)

	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = GVAR.POOL_markets.get(mName)
		mPrio = int(mData['IDLE_priority_index'])
	
		if(mPrio == newPrio) :
	
			prioFound = True
			marketFound = True
			bprint(defName + "ERROR: Priority index " + str(mPrio) + " already used for market " + mName + " -> Nothing changed")

	if (prioFound == False) :

		for market in GVAR.POOL_markets :

			mName = str(market)
			if (mName == marketName) :

				marketFound = True
				GVAR.POOL_markets[mName]['IDLE_priority_index'] = newPrio
				bprint(defName + "New priority index (level) set for " + marketName + " at " + str(newPrio))

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name")

def POOL_marketSetAmount(PARAM_marketName, PARAM_amount) :

	defName = "POOL_marketSetAmount: "
	
	marketFound = False

	marketName = PARAM_marketName

	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = GVAR.POOL_markets.get(mName)
		if (mName == marketName) :

			marketFound = True
			mAmountsRounder = GVAR.POOL_markets[mName]['TRADE_round_amounts']
			mPricesRounder = GVAR.POOL_markets[mName]['TRADE_round_prices']
			mBuyPriceLimit = GVAR.POOL_markets[mName]['PRICE_BUY_limit']
			mBuySymbol = GVAR.POOL_markets[mName]['BUY_symbol']
			mSellSymbol = GVAR.POOL_markets[mName]['SELL_symbol']
			
			fundsFree = GVAR.POOL_FUNDS_free
			fundsSymbol = GVAR.POOL_FUNDS_symbol
			newAmount = round(float(PARAM_amount), mAmountsRounder)
			fundsNecessary = round(newAmount * mBuyPriceLimit, mPricesRounder)

			if(mBuyPriceLimit > 0) :

				if(fundsFree >= fundsNecessary) :

					mStatus = GVAR.POOL_markets[mName]['MARKET_status']

					if(mStatus == "IDLE") :
					
						GVAR.POOL_markets[mName]['TRADE_ASSET_amount'] = newAmount
						bprint(defName + "New BUY AMOUNT = " + str(newAmount) + " " + mBuySymbol + " set for market " + marketName)
					
					else :

						bprint(defName + "Couldn't change BUY AMOUNT for market " + mName + " (NOT in IDLE mode)")
				
				else :
					
					maxAmount = round(fundsFree / mBuyPriceLimit, mAmountsRounder)
					bprint(defName + "ERROR: Not enough FREE funds to buy " + str(newAmount) + " " + mBuySymbol + " (" + str(fundsNecessary) + " " + mSellSymbol + " needed) at BUY price LIMIT " + str(mBuyPriceLimit) + " " + mSellSymbol)
					bprint(defName + "ERROR: FREE funds = " + str(fundsFree) + " " + fundsSymbol + " -> Max BUY AMOUNT = " + str(maxAmount) + " " + mBuySymbol)

			else :

				bprint(defName + "ERROR: BUY price LIMIT = 0 for market " + mName +  " -> Set BUY price LIMIT > 0 before setting ASSET amount")

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name")

def POOL_marketSetIdleMP(PARAM_marketName, PARAM_idleMarginPercent) :

	defName = "POOL_marketSetIdleMP: "
	
	marketFound = False
	newIdleMP = round(float(PARAM_idleMarginPercent),3)
	marketName = PARAM_marketName

	bprint(defName + "Setting new IDLE margin percent for market " + marketName)

	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = GVAR.POOL_markets.get(mName)
		mIdleMP = mData['IDLE_margin_percent']
	
		if (mName == marketName) :

			marketFound = True
			GVAR.POOL_markets[mName]['IDLE_margin_percent'] = newIdleMP
			bprint(defName + "Changed IDLE margin percent for " + marketName + " from " + str(mIdleMP) + " % to " + str(newIdleMP) + " %")

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name")

def POOL_marketSetApproach(PARAM_marketName) :

	defName = "POOL_marketSetApproach: "

	marketName = PARAM_marketName
	marketFound = False

	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = GVAR.POOL_markets.get(mName)

		if (mName == marketName) :

			marketFound = True
			mPriceMarket = float(mData['PRICE_market'])
			mPriceMargin = float(mData['PRICE_BUY_margin'])
			mPriceRounder = mData['TRADE_round_prices']
			
			mMarginReducer = 2
			mPriceApproach = round(mPriceMarket + (mPriceMargin / mMarginReducer), mPriceRounder)
			POOL_marketSetPriceStop(mName, mPriceApproach)

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name " + marketName)

def POOL_marketSetEnabled(PARAM_marketName, PARAM_enabled) :

	defName = "POOL_marketSetEnabled: "

	marketName = PARAM_marketName
	marketFound = False

	for market in GVAR.POOL_markets :

		mName = str(market)

		if (mName == marketName) :

			#mData = GVAR.POOL_markets.get(mName)
			marketFound = True
			new_bool = eval(str(PARAM_enabled))
			GVAR.POOL_markets[mName]['MARKET_enabled'] = new_bool

			bprint(defName + "Set market " + mName + " enabled: " + str(new_bool))

			if(new_bool == True) :
				POOL_marketSetStatus(mName, "IDLE")
			else :
				POOL_marketSetStatus(mName, "OFF")
			
	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name " + marketName)

def POOL_setAllMarketsEnabled(PARAM_enabled) :

	defName = "POOL_setAllMarketsEnabled: "
	boolVar = eval(str(PARAM_enabled))

	bprint(defName + "Setting all markets enabled = " + str(boolVar))

	# To aboid bad priority order pause and resume TRADING

	GVAR.TRADER_paused = True
	
	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = POOL_marketGetData(mName)
		mPriceStop = float(mData['PRICE_BUY_stop'])

		if (mPriceStop > 0) :
			POOL_marketSetEnabled(mName, boolVar)
		else :
			POOL_marketSetEnabled(mName, False)

	GVAR.TRADER_paused = False

def POOL_marketTradeFinisher(PARAM_marketName) :
	
	defName = "POOL_marketTradeFinisher: "

	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	if (mData) :

		bprint(defName + "Pause TRADER activity -> Set GVAR.TRADER_paused = True")
		
		GVAR.TRADER_paused = True
		
		GVAR.TRADE_mode_on = False
		GVAR.TRADER_mode = None

		bprint(defName + "<<< DEBUG >>> GVAR.TRADER_mode == " + str(GVAR.TRADER_mode) + " | GVAR.TRADE_mode_on == " + str(GVAR.TRADE_mode_on) + " | GVAR.TRADER_marketName == None -> Do nothing")

		priceSellFill = GVAR.TRADE_price_end
		priceBuyFill = GVAR.TRADE_price_fill
		sellSymbol = mData['SELL_symbol']

		if (priceSellFill >= priceBuyFill) :

			# TRADE WIN -> Recalc new idle
			bprint(defName + "TRADE FINISHED with SELL FILL price (" + str(priceSellFill) + ") >= BUY FILL price (" + str(priceBuyFill) + ") -> WIN or TIE TRADE -> Do recalc market " + mName + " STOP, IDLE, LIMIT prices")
			GVAR.TRADER_wins += 1
			GVAR.POOL_markets[mName]['TRADE_COUNTER_wins'] += 1
			
		else :

			bprint(defName + "TRADE FINISHED with SELL FILL price (" + str(priceSellFill) + ") < BUY FILL price (" + str(priceBuyFill) + ") -> LOOSE TRADE -> Recalc -> Market: " + mName + " back to IDLE mode")
			# TRADE STOP LOSS -> Do NOT re-calc anything -> Go back to IDLE bode with old STOP, LIMIT, IDLE

			GVAR.TRADER_looses += 1
			GVAR.POOL_markets[mName]['TRADE_COUNTER_looses'] += 1

		mMax = float(mData['PRICE_CACHE_market_max'][1])
		mPriceMargin = float(mData['PRICE_BUY_margin'])

		newPriceStop = mMax + mPriceMargin

		bprint(defName + "Last " + mName + " MAX price = " + str(mMax) + " " + sellSymbol + " -> Set new STOP price = " + str(newPriceStop) + " " + sellSymbol)

		POOL_marketSetEnabled(mName, False)
		POOL_marketSetPriceStop(mName, newPriceStop)

		bprint(defName + "WINS: " + str(GVAR.TRADER_wins) + " - LOOSES: " + str(GVAR.TRADER_looses) + " = BALANCE: " + str(GVAR.TRADER_wins - GVAR.TRADER_looses) )
		
		napTime = 5
		
		bprint(defName + "MARKET reseting done -> " + str(napTime) + " secs nap for FUNDS refresh at server before going back to POOL monitoring mode..")
		
		napCounter = 0
		while (napCounter <= napTime) :
			
			bprint(defName + "Nap " + str(napCounter) + "/" + str(napTime))
			napCounter += 1
			sleep(1)

		bprint(defName + "Checking FUNDS after last trade..")
		POOL_fundsCheck()

		# After funds check -> Force IDLE mode (even if it should be in any other state)
		# So a new amount can be set (SetMaxAmount() only applies new amount if the market is in IDLE state)
		POOL_marketSetStatus(mName, "IDLE")
	

		bprint(defName + "Seting new MAX amount to ALL enabled markets acording to actual funds limit (" + str(GVAR.POOL_FUNDS_limit) + " " + str(GVAR.POOL_FUNDS_symbol) + ")")

		POOL_setAllMarketsEnabled(False)
		POOL_setMaxAmounts()
		
		bprint(defName + "<<< DEBUG >>> GVAR.TRADER_mode == " + str(GVAR.TRADER_mode) + " | GVAR.TRADE_mode_on == " + str(GVAR.TRADE_mode_on) + " | GVAR.TRADER_marketName == None -> Do nothing")
		bprint(defName + "Resume TRADER activity -> Set GVAR.TRADER_paused = False")

		# Finally re-enable market and do IDLE check to resume monitoring / trading cicle
		POOL_setAllMarketsEnabled(True)
		#POOL_marketSetEnabled(mName, True)			
		POOL_marketIdleCheck(mName)
		
		GVAR.TRADER_marketName = None
		GVAR.TRADER_mode = None
		
		GVAR.TRADER_paused = False

		GVAR.TRADE_marketName = None
		GVAR.TRADE_mode_on = False

		bprint("")
		bprint("")
	
	else :

		bprint(defName + "ERROR: Unknown market " + mName)
			
def POOL_marketSetWTFUSARPALGO(PARAM_marketName, PARAM_enabled) :

	defName = "POOL_marketSetEnabled: "

	marketName = PARAM_marketName
	marketFound = False

	for market in GVAR.POOL_markets :

		mName = str(market)

		if (mName == marketName) :

			#mData = GVAR.POOL_markets.get(mName)
			marketFound = True
			new_bool = eval(str(PARAM_enabled))
			GVAR.POOL_markets[mName]['MARKET_enabled'] = new_bool

			bprint(defName + "Set market " + mName + " enabled: " + str(new_bool))

			if(new_bool == True) :
				POOL_marketSetStatus(mName, "IDLE")
			else :
				POOL_marketSetStatus(mName, "OFF")
			
	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name " + marketName)

def POOL_marketSetStatus(PARAM_marketName, PARAM_status) :

	defName = "POOL_marketSetStatus: "

	marketName = PARAM_marketName
	marketFound = False

	for market in GVAR.POOL_markets :

		mName = str(market)

		if (mName == marketName) :

			#mData = GVAR.POOL_markets.get(mName)
			marketFound = True
			new_status = str(PARAM_status) 
			GVAR.POOL_markets[mName]['MARKET_status'] = new_status
			
			bprint(defName + "Set market " + mName + " status: " + str(new_status))

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name " + marketName)

def POOL_marketOrderValidator(PARAM_marketName, PARAM_side) :

	# This function checks if and order can be created using the following criteria
	# Side BUY:
	# 	-> priceStop <= priceLimit (BUY LIMIT price must be ABOVE STOP price)
	#	-> priceStop > priceMarket (STOP price must be ABOVE current MARKET price)
	#	-> amount * priceStop > 10 USD (MINIMUN LOT SIZE in Binance for any market has to be at least 10 USD)
	# Side SELL:
	# 	-> priceStop >= priceLimit (BUY LIMIT price must be BELOW STOP price)
	#	-> priceStop < priceMarket (STOP price must be BELOW current MARKET price)
	#	-> amount * priceStop > 10 USD (MINIMUN LOT SIZE in Binance for any market has to be at least 10 USD)

	defName = "POOL_marketOrderValidator: "
	
	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	priceStop = float(mData['PRICE_BUY_stop'])
	priceLimit = float(mData['PRICE_BUY_limit'])
	priceMarket = float(mData['PRICE_market'])
	sellSymbol = str(mData['SELL_symbol'])

	minValue = 10

	validOrder = False

	bprint(defName + "Invoked -> Validating " + PARAM_side + " order data ..")

	if (PARAM_side == "BUY") :

		check1 = False
		check2 = False
		check3 = False

		amount = float(mData['TRADE_ASSET_amount'])
		lotValue = amount * priceStop

		if (priceStop <= priceLimit) :
			check1 = True
		else :
			bprint(defName + "<< WARNING >> Side: " + str(PARAM_side) + " Market: " + mName + " [ STOP price: " + str(priceStop) + " " + sellSymbol + " ] > [ LIMIT price: " + str(priceLimit) + "] -> Check 1 = False")

		if (priceStop > priceMarket) :
			check2 = True
		else :
			bprint(defName + "<< WARNING >> Side: " + str(PARAM_side) + " Market: " + mName + " [ STOP price: " + str(priceStop) + " " + sellSymbol + " ] < [ MARKET price: " + str(priceMarket) + "] -> Check 2 = False")

		if (lotValue > minValue) :
			check3 = True
		else :
			bprint(defName + "<< WARNING >> Side: " + str(PARAM_side) + " Market: " + mName + " [ LOT value: " + str(lotValue) + " " + sellSymbol + " ] < [ MIN (Binance) value: " + str(minValue) + "] -> Check 3 = False")

		if (check1 and check2 and check3) :

			validOrder = True
	
	elif (PARAM_side == "SELL") :

		check1 = False
		check2 = False
		check3 = False

		bprint(defName + "Getting SELL amount from what was BOUGHT (amount FILLED in BUY order) ..")
		amount = POOL_marketCalcSellAssetAmount(mName)
		lotValue = amount * priceStop

		if (priceStop >= priceLimit) :
			check1 = True
		else :
			bprint(defName + "<< WARNING >> Side: " + str(PARAM_side) + " Market: " + mName + " [ STOP price: " + str(priceStop) + " " + sellSymbol + " ] < [ LIMIT price: " + str(priceLimit) + "] -> Check 1 = False")

		if (priceStop < priceMarket) :
			check2 = True
		else :
			bprint(defName + "<< WARNING >> Side: " + str(PARAM_side) + " Market: " + mName + " [ STOP price: " + str(priceStop) + " " + sellSymbol + " ] > [ LIMIT price: " + str(priceLimit) + "] -> Check 2 = False")

		if (lotValue > minValue) :
			check3 = True
		else :
			bprint(defName + "<< WARNING >> Side: " + str(PARAM_side) + " Market: " + mName + " [ STOP price: " + str(priceStop) + " " + sellSymbol + " ] < [ LIMIT price: " + str(priceLimit) + "] -> Check 3 = False")


		if (check1 and check2 and check3) :

			validOrder = True

	bprint(defName + "[ Side: " + str(PARAM_side) + " ] [ Check1 (LIMIT to STOP): "+ str(check1) + " ] [ Check2 (STOP to MARKET): " + str(check2) + " ] [ Check3 (LOT Value > " + str(minValue) + "): " + str(check3) + " ] -> Valid order: " + str(validOrder))

	return validOrder
		
def POOL_marketSetPriceMargin(PARAM_side, PARAM_marketName, PARAM_priceMargin) :

	defName = "POOL_marketSetPriceMargin: "
	
	marketFound = False
	newPriceMargin = float(PARAM_priceMargin)
	marketName = PARAM_marketName

	if(PARAM_side == "BUY") :

		mDataName = "PRICE_BUY_margin"

	elif(PARAM_side == "SELL") :

		mDataName = "PRICE_SELL_margin"

	else :

		return None

	bprint(defName + "Setting " + mDataName + " = " + str(newPriceMargin) + " for market " + marketName)

	for market in GVAR.POOL_markets :

		mName = str(market)
		mData = GVAR.POOL_markets.get(mName)
		mPriceRounder = mData['TRADE_round_prices']
	
		if (mName == marketName) :

			marketFound = True
			newPriceMarginRounded = round(newPriceMargin, mPriceRounder)
			GVAR.POOL_markets[mName][mDataName] = newPriceMarginRounded
			bprint(defName + "Market TRADE_round_prices = " + str(mPriceRounder))
			bprint(defName + "New PRICE MARGIN set for " + marketName + " -> " + mDataName + " = " + str(newPriceMarginRounded))

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name")

def POOL_marketSetPriceStop(PARAM_marketName, PARAM_priceStop) :

	defName = "POOL_marketSetPriceStop: "
	
	marketFound = False
	marketName = PARAM_marketName
	mPriceStop = PARAM_priceStop

	bprint(defName + "Setting new BUY STOP, BUY LIMIT, IDLE LIMIT prices for market " + marketName)

	for market in GVAR.POOL_markets :

		mName = str(market)

		if (mName == marketName) :

			mData = GVAR.POOL_markets.get(mName)
			marketFound = True
			marketStatus = mData['MARKET_status']
			
			if ((marketStatus == "IDLE") or (marketStatus == "OFF")) :

				marketSellSymbol = mData['SELL_symbol']
				marketPriceRounder = int(mData['TRADE_round_prices'])
				marketBuyPriceMargin = float(mData['PRICE_BUY_margin'])
				marketIdleMarginP = float(mData['IDLE_margin_percent'])
				
				newBuyPriceStop = round(float(mPriceStop),marketPriceRounder)
				
				newBuyPriceLimit = newBuyPriceStop + marketBuyPriceMargin
				newBuyPriceLimit = round(newBuyPriceLimit, marketPriceRounder)
				
				newIdleLimit = calcIdlePriceLimit(newBuyPriceStop, marketIdleMarginP, marketPriceRounder)
				#newIdleLimit = round(newIdleLimit, marketPriceRounder)
				
				GVAR.POOL_markets[mName]['PRICE_BUY_stop'] = newBuyPriceStop
				GVAR.POOL_markets[mName]['PRICE_BUY_updated'] = True
				bprint(defName + "Set market " + marketName + " new BUY STOP price: " + str(newBuyPriceStop) + " " + marketSellSymbol)

				GVAR.POOL_markets[mName]['PRICE_BUY_limit'] = newBuyPriceLimit
				bprint(defName + "Set market " + marketName + " new BUY LIMIT price: " + str(newBuyPriceLimit) + " " + marketSellSymbol)

				GVAR.POOL_markets[mName]['PRICE_IDLE_limit'] = newIdleLimit
				bprint(defName + "Set market " + marketName + " new IDLE LIMIT: " + str(newIdleLimit) + " " + marketSellSymbol)

				POOL_marketSetMaxAmount(marketName)
			
			else :

				bprint(defName + "ERROR: Market " + mName + " NOT in IDLE mode -> No changes applied")

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name")
	
def POOL_CFB_updateSellOrder(PARAM_marketName) :

	defName = "POOL_CFB_updateSellOrder: "
	
	marketFound = False
	marketName = PARAM_marketName

	bprint(defName + "Updating SELL-CFB STOP, LIMIT prices for market " + marketName)

	for market in GVAR.POOL_markets :

		mName = str(market)

		if (mName == marketName) :

			mData = GVAR.POOL_markets.get(mName)
			marketFound = True
			marketStatus = mData['MARKET_status']
			
			if (marketStatus == "TRADING") :

				priceMarket = mData['PRICE_market']
				marketSymbol = mData['MARKET_symbol']
				priceSellMargin = mData['PRICE_SELL_margin']
				sellSymbol = mData['SELL_symbol']
				priceRounder = int(mData['TRADE_round_prices'])
				amountRounder = int(mData['TRADE_round_amounts'])
				
				#assetAmount = mData['TRADE_ASSET_amount']
				assetAmount = POOL_marketCalcSellAssetAmount(mName)
				
				priceMVmargin = mData['PRICE_MV_margin']
				
				new_prices = SELL_CFB_CalcNewStopPrice(GVAR.SELL_CFB_margin_percent, priceSellMargin, priceMVmargin, priceMarket, priceRounder)
				new_SELL_price_stop = round(float(new_prices["price_stop"]), priceRounder)
				new_SELL_price_limit = round(float(new_prices["price_limit"]), priceRounder)

				GVAR.POOL_markets[mName]['PRICE_SELL_stop'] = new_SELL_price_stop
				bprint(defName + "Set market " + marketName + " new SELL STOP price: " + str(new_SELL_price_stop) + " " + sellSymbol)

				GVAR.POOL_markets[mName]['PRICE_SELL_limit'] = new_SELL_price_limit
				bprint(defName + "Set market " + marketName + " new SELL LIMIT price: " + str(new_SELL_price_limit) + " " + sellSymbol)

				# Asset Amount doesn't have to be updated (Amount remains the same throught the whole trade)

				bprint(defName + "Calling POOL_marketCreateStopLimitOrder with [STOP " + str(new_SELL_price_stop) + "] + [LIMIT " + str(new_SELL_price_limit) + "] + [AMOUNT " + str(assetAmount) + "]")
				new_order_resp = POOL_marketCreateStopLimitOrder(marketName, "SELL")

				#new_order_resp = EXCHANGE_ORDER_Create_StopLimit(marketSymbol, SIDE_SELL, new_SELL_price_stop, new_SELL_price_limit, assetAmount)

				GVAR.TRADE_orderId = new_order_resp['orderId']
				bprint(defName + "Set TRADE new OrderId: " + str(GVAR.TRADE_orderId))
				bprint("")

				return new_order_resp
			
			else :

				bprint(defName + "ERROR: Market " + mName + " NOT in IDLE mode -> No changes applied")

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name " + marketName)

def POOL_marketIdleCheck(PARAM_marketName) :

	defName = "POOL_marketIdleCheck: "

	if(GVAR.MODE_VERBOSE_loops == True) :
		bprint(defName + "Doing re-calcs for market " + PARAM_marketName)

	mData = None
	mName = PARAM_marketName

	mData = POOL_marketGetData(mName)

	if (mData) :

		mMarketEnabled = mData['MARKET_enabled']
		mMarketStatus = mData['MARKET_status']

		mPriceRounder = mData['TRADE_round_prices']
		mPriceBuyStop = mData['PRICE_BUY_stop']
		mPriceMarket = mData['PRICE_market']
		mIdleMarginP = mData['IDLE_margin_percent']

		mPriceIdleLimit = mData['PRICE_IDLE_limit']

		#mPriceIdleLimit = calcIdlePriceLimit(mPriceBuyStop, mIdleMarginP)
		#GVAR.POOL_markets[mName]['PRICE_IDLE_limit'] = mPriceIdleLimit

		if(mMarketEnabled == True) :	
			
			mPriceIdleDistP = calcPriceDistancePercent(mPriceBuyStop, mPriceMarket)
			GVAR.POOL_markets[mName]['IDLE_distance_percent'] = round(mPriceIdleDistP,2)

			if(mPriceIdleDistP < 0) :

				# While market price is below IDLE limit
				if ((-mPriceIdleDistP) <= mIdleMarginP) :

					if (mMarketStatus == "IDLE") :
						mMarketStatus = "READY"
						GVAR.POOL_markets[mName]['MARKET_status'] = mMarketStatus

				elif ((-mPriceIdleDistP) > mIdleMarginP) :

					if (mMarketStatus == "READY") :
						mMarketStatus = "IDLE"
						GVAR.POOL_markets[mName]['MARKET_status'] = mMarketStatus

			else : 

				# Market price ABOVE Stop limit -> recalc new IDLE limit
				if (GVAR.TRADE_mode_on == True) :

					if(mPriceMarket > mPriceBuyStop) :

						if (mMarketStatus == "READY") or (mMarketStatus == "IDLE") :

							tradeMarket = GVAR.TRADER_marketName

							bprint("")
							bprint(defName + "TRADE_mode_on == " + str(GVAR.TRADE_mode_on) + " -> Trading is running on other market -> Doing re-calc..")
							bprint(defName + mName + " market price above BUY STOP price but FUNDS are locked by market " + str(tradeMarket) + " -> Re-calc new BUY STOP, LIMIT, IDLE limit")
							bprint(defName + "Set [ MARKET_enabled = False ] for market " + mName + " to be able to set new BUY STOP, LIMIT and AMOUNT")

							POOL_marketSetEnabled(mName, False)
							POOL_idleLimitReCalc(mName)
							POOL_marketSetEnabled(mName, True)

							bprint("")

							#mMarketStatus = "READY"
							#GVAR.POOL_markets[mName]['MARKET_status'] = mMarketStatus

		else:
			
			mPriceIdleLimit = ""
			mPriceIdleDistP = ""
			GVAR.POOL_markets[mName]['IDLE_distance_percent'] = mPriceIdleDistP

		if(GVAR.MODE_VERBOSE_loops == True) :
			bprint(defName + "Market found " + PARAM_marketName)
			bprint(defName + "Updating IDLE limit to " + str(mPriceIdleLimit))

	else :

		bprint(defName + "ERROR: Market unknown " + PARAM_marketName)		

def POOL_marketGetData(PARAM_marketName) :

	defName = "POOL_marketGetData: "

	marketGetName = PARAM_marketName
	marketFound = False
	
	#bprint(defName + "Getting " + marketGetName + " data..")
	mData = GVAR.POOL_markets.get(marketGetName)
	
	if (mData) :
		
		marketFound = True
		#GVAR.POOL_markets[mName]['IDLE_priority_index'] = newPrio
		#bprint(defName + "Market found returning " + marketGetName + " data..")
		return mData

	if (marketFound == False) :

		bprint(defName + "ERROR: Unknown market name")
		return None

def POOL_counter ():

	if (GVAR.POOL_counters_enabled == False) :
		
		# Reset counter the first time
		GVAR.POOL_counters = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
		GVAR.POOL_counters_enabled = True

	#bprint(defName + "Cycle counters = " + str(pCounters))

	pCounters = GVAR.POOL_counters
	index = 0

	for item in pCounters :
		
		if(item > 0) :
			pCounters[index] -= 1
		else :
			pCounters[index] = index
		
		index += 1
	
	GVAR.POOL_counters = pCounters

def POOL_compiler(PARAM_marketsData):

	defName = "POOL_compiler: "

	pMarkets = {}
	pRawData = PARAM_marketsData

	for item in pRawData:

		#marketName = list(item)[0]
		#marketData = item.values()[0]

		marketName = str(item)

		pRawData[marketName]['MARKET_enabled'] = False
		pRawData[marketName]['MARKET_status'] = "OFF"

		pRawData[marketName]['PRICE_market'] = 0.00
		pRawData[marketName]['PRICE_CACHE_market'] = []
		pRawData[marketName]['PRICE_CACHE_market_max'] = None
		pRawData[marketName]['PRICE_CACHE_market_min'] = None
		pRawData[marketName]['PRICE_CACHE_market_max_index'] = None
		pRawData[marketName]['PRICE_CACHE_market_min_index'] = None
		pRawData[marketName]['PRICE_CACHE_market_amplitude_price'] = None
		pRawData[marketName]['PRICE_CACHE_market_amplitude_percent'] = None

		#pRawData[marketName]['PRICE_ask'] = 0.00
		#pRawData[marketName]['PRICE_bid'] = 0.00
		#pRawData[marketName]['BUY_amount'] = 0.00
		#pRawData[marketName]['SELL_amount'] = 0.00

		pRawData[marketName]['PRICE_IDLE_limit'] = 0.00
		
		# IDLE_priority_index must be set at YAML config file
		# if not every time the bot starts there is a manual priority reoder that has to be done
		# Too much work to do it manual every time
		#pRawData[marketName]['IDLE_priority_index'] = 0
		
		pRawData[marketName]['IDLE_distance_percent'] = 0.00

		pRawData[marketName]['PRICE_BUY_stop'] = 0.00
		pRawData[marketName]['PRICE_BUY_limit'] = 0.00
		pRawData[marketName]['PRICE_SELL_stop'] = 0.00
		pRawData[marketName]['PRICE_SELL_limit'] = 0.00
		
		pRawData[marketName]['PRICE_BUY_updated'] = False

		pRawData[marketName]['TRADE_ASSET_amount'] = 0.00
		pRawData[marketName]['TRADE_COUNTER_wins'] = 0
		pRawData[marketName]['TRADE_COUNTER_looses'] = 0

	#bprint(defName + "Markets re-compilation done")
	#bprint(defName + "pMarkets = " + str(pMarkets))

	GVAR.POOL_markets = pRawData

def BUY_printTradeLine(PARAM_marketName, PARAM_BuyPrice, PARAM_TickerBidPrice, PARAM_StatsStr) :

	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	priceMarket = mData['PRICE_market']
	priceLimit = mData['PRICE_BUY_limit']

	rounderPrices = mData['TRADE_round_prices']
	marketSymbol = mData['MARKET_symbol']
	
	timeStr = TIME_getNowTime()
	tmp_price = str(round(float(str(PARAM_TickerBidPrice)),rounderPrices))
	price_bid_str = tmp_price.ljust(7)
	price_buy_str = str(round(float(str(PARAM_BuyPrice)),rounderPrices))

	diff = calcPriceDistance(PARAM_BuyPrice, PARAM_TickerBidPrice)
	diff_percent = calcPriceDistancePercent(PARAM_BuyPrice, PARAM_TickerBidPrice)
	diff_str = str(round(diff,2)).ljust(8)
	diff_percent_str = str(round(diff_percent,2)).ljust(5)

	symbol_str = marketSymbol

	priceDirection = MARKET_CACHE_getPriceDirection(mName)
	priceDirectionStr = TICKER_CACHE_convertPriceDirectionToArrowStr(priceDirection)

	# Color percentages
	if (diff_percent < 0) :
		if (diff_percent >= -0.25) :
			diff_percent_str = "<<" + diff_percent_str + ">>"

		if (diff_percent > -1) :
			diff_percent_str = "<" + diff_percent_str + ">"

		if (diff_percent > -0.05) :
			
			if(GVAR.SIMULATOR_TICKER_debug_stops == True) :
				bprint("\r\n\n >>>>> DEBUG STOP (PRICE DISTANCE TO STOP PRICE < -0.05 %)")
				bprint("BUYING IN SECS.. -> REDUCE SPEED -> GVAR.TICKER_sleep = 1 \n\n\r")
				GVAR.TICKER_sleep = 0.5

	#else :

		#if (diff_percent < 2 ) :
		#	diff_percent_str = pcolors.TUR + diff_percent_str + pcolors.ENDC
		#elif (diff_percent >= 2) :
		#	diff_percent_str = pcolors.GREEN + diff_percent_str + pcolors.ENDC


	if (GVAR.SCREEN_enabled == False) :

		str1 = " [ " + timeStr + " " + priceDirectionStr + " " + symbol_str + " " + price_bid_str + " | " + pcolors.GREEN + "BUY STOP " + pcolors.ENDC + pcolors.TUR + price_buy_str + pcolors.ENDC + ""
		str2 = " = " + diff_str + " = " + diff_percent_str + " % ] "
		str3 = " [ LIMIT " + pcolors.TUR + str(GVAR.BUY_price_limit) + pcolors.ENDC + " " + GVAR.SELL_symbol + " ] "

		lineStr = str1 + str2 + str3 + PARAM_StatsStr

		if (GVAR.MODE_VERBOSE_enabled == True) :
			sys.stdout.write(lineStr + "\r")
			sys.stdout.flush()

	else :

		str1 = " [ " + timeStr + " " + priceDirectionStr + " " + symbol_str + " " + price_bid_str + " | " + "BUY STOP " + price_buy_str + ""
		str2 = " = " + diff_str + " = " + diff_percent_str + " % ] "
		str3 = " [ LIMIT " + str(priceLimit) + " " + GVAR.SELL_symbol + " ] "

		lineStr = str1 + str2 + str3 + PARAM_StatsStr

		bprint(lineStr)

def SELL_printTradeLine(PARAM_marketName, PARAM_TRADE_price, PARAM_TICKER_price_bid, PARAM_StatsStr) :

	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	priceMarket = mData['PRICE_market']
	priceSellStop = mData['PRICE_SELL_stop']
	priceSellLimit = mData['PRICE_SELL_limit']

	rounderPrices = mData['TRADE_round_prices']
	marketSymbol = mData['MARKET_symbol']

	timeStr = TIME_getNowTime()

	tmp_price = str(round(float(str(PARAM_TICKER_price_bid)),GVAR.TRADE_round_prices))
	price_bid_str = tmp_price.ljust(7)
	price_trade_str = str(round(float(str(PARAM_TRADE_price)),GVAR.TRADE_round_prices))

	diff = calcPriceDistance(PARAM_TRADE_price, PARAM_TICKER_price_bid)
	diff_str = str(round(diff,2)).ljust(7)
	if(diff > 0) :
		diff_str = "+" + diff_str

	diff_percent = calcPriceDistancePercent(PARAM_TRADE_price, PARAM_TICKER_price_bid)
	diff_percent_str = str(round(diff_percent,2)).ljust(4)

	priceDirection = MARKET_CACHE_getPriceDirection(mName)
	priceDirectionStr = TICKER_CACHE_convertPriceDirectionToArrowStr(priceDirection)

	# Distance from current price to SELL Stop Price
	stop_diff = float(PARAM_TICKER_price_bid) - float(priceSellStop) 
	stop_diff_percent = calcPriceDistancePercent(priceSellStop, PARAM_TICKER_price_bid)
	stop_diff_percent_str = str(round(stop_diff_percent,2))

	# Color percentages
	if (diff_percent < 0) :
			diff_percent_str = diff_percent_str
	else :
		if (diff_percent < 0.25 ) :
			diff_percent_str = "+" + diff_percent_str
		elif (diff_percent >= 0.25) :
			diff_percent_str = "+" + diff_percent_str

	str1 = " [ " + timeStr + " " + priceDirectionStr + " -> " + price_bid_str + " " + marketSymbol + " - TRADE PRICE: " + price_trade_str + ""
	str2 = " = " + diff_str + " = " + diff_percent_str + " % ]"

	CFBmP_str = str(GVAR.SELL_CFB_margin_percent)
	str3 = " [ " + GVAR.SELL_CFB_label + " = " + CFBmP_str + " % ] -> [ " + stop_diff_percent_str.ljust(5) + " % above " + "STOP" + " " + str(priceSellStop) + " ] "

	CFBmP_stats = GVAR.SELL_CFB_LOG_PriceInMargin

	lineStr = str1 + str2 + str3 + CFBmP_stats + PARAM_StatsStr

	bprint(lineStr)	

def CFA_PriceInMargin (PARAM_CFA_MarginPercent, PARAM_BuyPrice, PARAM_TickerPriceBid) :
	
	price_buy = PARAM_BuyPrice
	price_ticker = PARAM_TickerPriceBid
	margin_P = PARAM_CFA_MarginPercent
	mPStr = str(round(margin_P,2))

	price_dist_P = calcPriceDistancePercent(price_buy, price_ticker)

	# price_dist_P while waiting for buy order is allways negative 
	# so to compare with margin_P has to be converted into positive percent 
	rP = (price_dist_P * -1) - margin_P
	if(rP >= 0) :

		"""if (GVAR.STATISTICS_TICKER_cache_rightest_peak_found == True) :
			if (rP < GVAR.BUY_CFA_max_forced_margin_percent) :
				bprint("")
				bprint("CFA_PriceInMargin: Price too High from TICKER but FORCING base Stop Price")
				bprint("")
				#sleep(10)
				return True
			else :
				# Remove Right-Peak from memory
				bprint("")
				bprint("CFA_PriceInMargin: Price too low to keep forcing Right-Peak as base Stop Price -> Removing Peak data")
				bprint("")
				GVAR.STATISTICS_TICKER_cache_rightest_peak_found = False
				GVAR.STATISTICS_TICKER_cache_rightest_peak = None
				sleep(10)
				return False
		
		else :"""

		return False

	else :
		if((rP * -1) < (margin_P / 2)) :
			rP_str = pcolors.YELLOW + str(round(-rP,2)).ljust(4) + pcolors.ENDC
		else :
			rP_str = str(round(-rP,2)).ljust(4)

		GVAR.BUY_CFA_LOG_PriceInMargin = "[ CFAmP (" + mPStr + " %) " + rP_str + " % ABOVE BID ]"
		return True

def SELL_CFB_StopPriceIncreaser (PARAM_marketName, PARAM_CFB_price_stop, PARAM_CFB_margin_percent) :
	
	defName = "SELL_CFB_StopPriceIncreaser: "

	marketName = PARAM_marketName
	MARKET_data = POOL_marketGetData(marketName)

	marketSymbol = MARKET_data['MARKET_symbol']
	priceMarket = MARKET_data['PRICE_market']
	sellSymbol = MARKET_data['SELL_symbol']

	price_stop = PARAM_CFB_price_stop
	margin_P = PARAM_CFB_margin_percent
	mpStr = str(round(margin_P,2))

	price_dist_P = round(calcPriceDistancePercent(price_stop, priceMarket),2)	
	rP = round(price_dist_P - margin_P,2)

	if(rP > 0) :

		# If SELL STOP has to be updated -> Check if order really still-exists and hasn't been FILLED before canceling
		# Sometimes prices increase too fast since last status-check and order may have been FILLED while this checking process occurs

		bprint(defName + "[ MARKET price - SELL STOP price ] > CFB Margin (SELL STOP price too far from MARKET price)")
		bprint(defName + "Doing order status SYNC to check it was NOT FILLED (NEW) and re-calc new CFB SELL STOP price..")
		orderStatus = EXCHANGE_ORDER_StatusSync("SELL", True, defName)
		bprint(defName + "Status sync RETURNED: " + str(orderStatus))

		if (orderStatus == "NEW") :

			bprint(defName + "Market " + str(marketName) + " (" + str(marketSymbol) + ") current prices [ MARKET price: " + str(priceMarket) + " " + sellSymbol + " ] [ STOP price: " + str(price_stop) + " " + sellSymbol + " ]")
			bprint(defName + "CFB margin: " + str(margin_P) + " %")
			bprint(defName + "Price dist: " + str(price_dist_P) + " %")
			bprint(defName + "Exceeded by: " + str(rP) + " % -> Cancel current SELL order at [ STOP price: " + str(price_stop) + " ] -> Setting new (closer to MARKET price) SELL STOP order ..")

			pre_cancel_orderId = GVAR.TRADE_orderId
			
			resp = EXCHANGE_ORDER_Cancel(marketSymbol, GVAR.TRADE_orderId)
			respOrderId = resp['orderId']

			bprint(defName + "orderId: " + str(GVAR.TRADE_orderId) + " on symbol " + marketSymbol + " cancelation SUCCESFULL")

			# If EXCHANGE_ORDER_Cancel() returns TRADE_OrderID = 0 -> the sell order probably was FILLED between status check and this order cancel
			# Forcing one more status sync will end current trade (use this as a way to finish current trade becase SELL order was FILLED)
			if (respOrderId == 0) :

				bprint(defName + ">>>>>> Cancel order returned GVAR.TRADE_orderId = 0 -> Doing new status sync with last SELL orderId: " + str(pre_cancel_orderId))
				bprint(defName + ">>>>>> Setting old pre-cancelation orderId before FORCED status sync -> GVAR.TRADE_orderId = " + str(pre_cancel_orderId))
				GVAR.TRADE_orderId = pre_cancel_orderId

				extra_check_status = EXCHANGE_ORDER_StatusSync("SELL", True, defName)
				bprint(defName + ">>>>>> TRADE_orderId = 0 Status sync RETURNED: " + str(extra_check_status))
				bprint("")

				return extra_check_status

			else :

				#DEBUG_TRADE_printVars("SELL_CFB_StopPriceIncreaser")
				
				POOL_CFB_updateSellOrder(marketName)
				MICRO_sleep(GVAR.TICKER_sleep)
				
				return orderStatus

		elif (orderStatus == "FILLED") :

			bprint(defName + "Pre-increase order status sync returned FILLED -> Finishing trade..")
			
			return orderStatus

def CFA_BUY_CalcNewPrice (PARAM_CFA_MarginPercent, PARAM_CFA_MV_MarginPercent, PARAM_TickerPriceBid) :

	# If a "RIGHT-Peak" was spotted use it as stop_price
	#if (GVAR.STATISTICS_TICKER_cache_rightest_peak_found == True) :
	#	stopPriceBase = round(float(GVAR.STATISTICS_TICKER_cache_rightest_peak[2]),2)
	#	bprint("CFA_BUY_CalcNewPrice: Right-Peak Spotted -> Using it as base for STOP Price: " + str(stopPriceBase))
	#	sleep(3)
	#else :
		#stopPriceBase = float(PARAM_TickerPriceBid)

	stopPriceBase = float(PARAM_TickerPriceBid)

	newPrice = stopPriceBase * (100 + float(PARAM_CFA_MarginPercent)) / 100
	# Adds extra value using the Micro Volatility margin % (MVmP) to avoid too many new StopPrices updates
	# when price goes down in permited MV margin
	mvDelta = round(newPrice / 100 * float(PARAM_CFA_MV_MarginPercent),2)
	newPriceMV = round(newPrice - mvDelta,2)

	bprint("CFA_BUY_CalcNewPrice: New [ STOP Price: " + str(round(newPrice,GVAR.TRADE_round_prices)) + " ] - [ MV (" + str(PARAM_CFA_MV_MarginPercent) + " %) delta: " + str(round(mvDelta,2)) + " ] = " + str(round(newPriceMV,2)))

	return newPriceMV
	
def SELL_CFB_CalcNewStopPrice (PARAM_CFB_margin_percent, PARAM_CFB_price_limit_margin, PARAM_price_MV_margin, PARAM_priceMarket, PARAM_price_rounder) :

	defName = "SELL_CFB_CalcNewStopPrice: "

	price_rounder = int(PARAM_price_rounder)

	new_price_stop = round(float(PARAM_priceMarket) * (100 - float(PARAM_CFB_margin_percent)) / 100, price_rounder)
	# Adds extra value using the Micro Volatility margin % (MVmP) to avoid too many new StopPrices updates
	# when price goes up or oscilates in permited MV margin
	price_MV_margin = float(PARAM_price_MV_margin)
	new_price_MV_stop = round(float(new_price_stop + price_MV_margin), price_rounder) 

	bprint(defName + "[ MARKET price: " + str(PARAM_priceMarket) + " ] [ CFB margin = " + str(PARAM_CFB_margin_percent) + " % ] -> New [ Clean STOP price (without MV margin): " + str(new_price_stop) + " ]")
	bprint(defName + "[ MV price margin = " + str(price_MV_margin) + " ] + New [ Clean STOP (without MV margin) price = " + str(new_price_stop) + " ] = [ STOP price (with MV margin): " + str(new_price_MV_stop) + " ]")
	
	# Extra check for cases where price is decreasing fast and adding MV margin resulst in new STOP prices ABOVE tickerPrice
	# Abandon MV for a while until prices stops decreasing to avoid run-time errors
	if(new_price_MV_stop >= float(PARAM_priceMarket)) :
		bprint("")
		logprint(GVAR.LOG_WARNINGS_name, defName + "<<< WARNING >>> [ MARKET: " + str(GVAR.TRADER_marketName) + " ] New [ STOP (with MV margin) price = " + str(new_price_MV_stop) + " ] > (ABOVE) [ MARKET price = " + str(PARAM_priceMarket) + " % ) -> Removing MV price margin")
		logprint(GVAR.LOG_WARNINGS_name, defName + "<<< WARNING >>> [ MARKET: " + str(GVAR.TRADER_marketName) + " ] REMOVING [ MV price margin = " + str(price_MV_margin) + " ] from New [ STOP price = " + str(new_price_MV_stop) + " ] -> Using [STOP (without MV margin) = " + str(new_price_stop) + " ]")
		bprint("")
		new_price_MV_stop = new_price_stop

	new_price_limit = new_price_MV_stop - float(PARAM_CFB_price_limit_margin)
	bprint(defName + "Returning NEW [ STOP price: " + str(new_price_MV_stop) + " ] [ LIMIT price: " + str(new_price_limit) + " ] ")

	return { "price_stop" : new_price_MV_stop , "price_limit" : new_price_limit }

def SELL_Calc_PreCFB_Prices ( PARAM_price_trade , PARAM_stop_loss_margin_percent, PARAM_price_sell_margin ) :
	
	# Sets the initial STOP LOSS price and LIMIT right after the BUY trade completed
	# It is the TRADE price -  STOP LOSS margin percent
	price_trade = float(PARAM_price_trade)
	stop_loss_mp = float(PARAM_stop_loss_margin_percent) 
	price_sm = float(PARAM_price_sell_margin)

	sell_price_stop = (100 - stop_loss_mp) * price_trade / 100 
	sell_price_stop = round(sell_price_stop,2)
	sell_price_limit = sell_price_stop - price_sm

	sell_cfb_mode_on_price = round((PARAM_price_trade / 100) * (100 + GVAR.SELL_CFB_margin_percent),2)

	#bprint("[BOT] SELL_Calc_PreCFB_Prices: " + pcolors.YELLOW + "SELL STOP LOSS" + pcolors.ENDC + " margin % : " + pcolors.YELLOW + str(PARAM_stop_loss_margin_percent)  + pcolors.ENDC + " -> New prices calculated for " + pcolors.GREEN + "FIRST" + pcolors.ENDC + pcolors.YELLOW + " STOP LOSS SELL" + pcolors.ENDC + " order StopPrice: " + str(sell_price_stop) + " LimitPrice: " + str(sell_price_limit))

	return { 'price_stop' : sell_price_stop , 'price_limit' : sell_price_limit, 'CFB_mode_on_target_price' : sell_cfb_mode_on_price }

def BINANCE_ORDER_Cancel (PARAM_Symbol, PARAM_OrderId) :

	defName = "BINANCE_ORDER_Cancel: "
	
	symbol_str = PARAM_Symbol
	orderId_str = str(PARAM_OrderId)

	bprint("BINANCE_ORDER_Cancel: symbol: " + symbol_str + " orderId: " + orderId_str + " -> Sending Cancel..")

	error_counter = 0
	max_errors = 15

	if (GVAR.FLAG_ERRORS_retry == False) :

			resp = BINANCE.cancel_order(symbol=symbol_str, orderId=orderId_str, recvWindow=50000)
			bprint("BINANCE_ORDER_Cancel: ORDER Cancelled (No retry mode) -> resp: " + str(resp))
			
	else :
		
		while True :

			try :
				
				resp = BINANCE.cancel_order(symbol=symbol_str, orderId=orderId_str, recvWindow=50000)
				bprint("BINANCE_ORDER_Cancel: ORDER Cancelled (Retry mode) -> resp: " + str(resp))
				
				break
		
			except Exception as e:

				error_counter += 1 

				e = sys.exc_info()
				bprint("")
				bprint(defName + "ERROR arised trying to cancel orderId: " + orderId_str)
				ERROR_printer(e, defName)
				bprint("")
				bprint(defName + "Checking if ERROR was because the order to be canceled no longer exists (who knows why..)")

				orderData = BINANCE_ORDER_GetStatus(PARAM_OrderId, PARAM_Symbol)
				orderStatus = orderData['status']

				if(orderStatus == "FILLED") :

					bprint(defName + "Order already FILLED -> Cannot be canceled anymore -> return Dummy resp (orderId = 0)")

					#resp = "{u'orderId': " + "0" + "}"
					resp = { 'orderId' : 0 }

					#GVAR.TRADE_orderId = 0

					break

				else :

					bprint(defName + "Order still exists with status: " + str(orderStatus))
					bprint(defName + "Will try again -> Tries left: " + str(max_errors - error_counter))
										
					sleep(GVAR.TICKER_sleep)

					if (error_counter == max_errors) :

						# Only in CANCEL order send dummy RESP to let the algoirth keep trading after 5 errors
						# CANCEL response is not very important, and may be trigerred manually after or before the error
						
						#resp = "{u'orderId': " + "0" + "}"
						resp = { 'orderId' : 0 }

						#GVAR.TRADE_orderId = 0

						bprint("")
						bprint(defName + "Persistent Unknown Error -> Sending DUMMY resp with OrderId = 0 " + pcolors.ENDC)
						bprint("")
						break

	return resp

def BINANCE_ORDERS_printOpenOrders() :

	defName = "BINANCE_ORDERS_printOpenOrders: "

	bprint("")
	bprint(defName + "Waiting FULL Open Orders list from BINANCE server ..")
	orders_data = BINANCE.get_open_orders(
		recvWindow=50000
		)

	data_str = JSON_curator(orders_data)
	orders_list_json = json.loads(data_str)

	for order_item_json in orders_list_json :
	
		order_id = order_item_json["orderId"]
		order_symbol = order_item_json['symbol']
		order_amount = round(float(order_item_json['origQty']),5)
		order_price = round(float(order_item_json['price']),5)
		order_side = order_item_json['side']
		order_status = order_item_json['status']

		pcolor = pcolors.VIOLET
		if (order_symbol == symbol) :
			pcolor = pcolors.GREEN
	
		bprint("==============================================================================================================")

		str1 = ">>>>> ORDER FOUND -> symbol: " + pcolor + str(order_symbol) + pcolors.ENDC + " | orderId: " + pcolors.YELLOW + str(order_id) + pcolors.ENDC + " | "
		str2 = "Side: " + str(order_side) + " | Status: " + str(order_status) + " | Amount: " + pcolors.GREEN + str(order_amount) + pcolors.ENDC + " | STOP Price: " + pcolors.TUR + str(order_price) + pcolors.ENDC
		bprint(str1 + str2)

	bprint("==============================================================================================================")
	bprint(defName + "No more open orders found -> Task finished")
	bprint("")

	return orders_list_json

def BINANCE_ORDERS_Cancel_OpenOrders_Symbol(PARAM_symbol, PARAM_side) :

	# PARAM_side not used -> remove if not going to use
	
	symbol = str(PARAM_symbol)

	bprint("")
	bprint("BINANCE_ORDERS_Cancel_OpenOrders_Symbol: Waiting FULL Open Orders list from BINANCE server ..")
	orders_data = BINANCE.get_open_orders(
		recvWindow=50000
		)

	data_str = JSON_curator(orders_data)
	orders_list_json = json.loads(data_str)

	for order_item_json in orders_list_json :
	
		order_id = order_item_json["orderId"]
		order_symbol = order_item_json['symbol']
		order_amount = round(float(order_item_json['origQty']),5)
		order_price = round(float(order_item_json['price']),5)
		order_side = order_item_json['side']

		pcolor = pcolors.VIOLET
		if (order_symbol == symbol) :
			pcolor = pcolors.GREEN
	
		bprint("==============================================================================================================")

		str1 = ">>>>> ORDER FOUND -> symbol: " + pcolor + str(order_symbol) + pcolors.ENDC + " | orderId: " + pcolors.YELLOW + str(order_id) + pcolors.ENDC + " | "
		str2 = "Side: " + str(order_side) + " | Amount: " + pcolors.GREEN + str(order_amount) + pcolors.ENDC + " | STOP Price: " + pcolors.TUR + str(order_price) + pcolors.ENDC
		bprint(str1 + str2)

		if (order_symbol == symbol) :
			bprint(">>>>> SYMBOL MATCH -> Cancelling order .. ")
			BINANCE_ORDER_Cancel(str(symbol), str(order_id))
		else :
			bprint(">>>>> SYMBOL DOES NOT MATCH -> Do nothing ")

	bprint("==============================================================================================================")
	bprint("BINANCE_ORDERS_Cancel_OpenOrders_Symbol: No more open orders found -> Task finished")
	bprint("")

#def BINANCE_ORDER_GetAviableAmount(PARAM_symbol) :

#	symbol = PARAM_symbol


def SIMULATOR_ORDER_Cancel (PARAM_Symbol, PARAM_OrderId) :
	
	symbol_str = PARAM_Symbol
	orderId_str = str(PARAM_OrderId)

	bprint ("SIMULATOR_Order_Cancel : OrderId " + orderId_str + " cancelled -> returning resp data")

	#resp = "{u'orderId': " + orderId_str + "}"
	resp = { 'orderId' : 0 }

	return str(resp)

def SIMULATOR_ORDER_Create_StopLimit (PARAM_Symbol, PARAM_Side, PARAM_Price_Stop, PARAM_Price_Limit, PARAM_Amount) :

	symbol = PARAM_Symbol
	price_stop = str(PARAM_Price_Stop)
	price_limit = str(PARAM_Price_Limit)
	amount = str(PARAM_Amount)
	side = str(PARAM_Side)

	bprint("SIMULATOR_ORDER_Create_StopLimit: New " + side + " order created " + symbol + " StopPrice: " + price_stop + ". StopLimit: " + price_limit + " Amount: " + amount)

	GVAR.SIMULATOR_orderId_counter += 1
	order_id = str(GVAR.SIMULATOR_orderId_counter)

	return { 'orderCreated' :  True, 'orderId' : order_id, 'side' : side, 'priceStop' : price_stop, 'priceLimit' : price_limit, 'amount' : amount, 'symbol' : symbol }

def POOL_marketCreateStopLimitOrder (PARAM_marketName, PARAM_Side) :

	defName = "POOL_marketCreateStopLimitOrder: "

	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	mMarketSymbol = mData['MARKET_symbol']
	mPriceMarket = mData['PRICE_market']
	mSellSymbol = mData['SELL_symbol']
	mRounderPrices = int(mData['TRADE_round_prices'])
	mRounderAmounts = int(mData['TRADE_round_amounts'])
	side = PARAM_Side

	bprint(defName + "Invoked for market: " + str(mName) + " -> [ MARKET_symbol = " + str(mMarketSymbol) + " ] [ PRICE_market = " + str(mPriceMarket) + " " + str(mSellSymbol) + " ]")

	resp = POOL_orderCreator(mName, side)
	new_orderId = resp['orderId']

	if(float(new_orderId) > 0) :

		bprint(defName + "Order created sucesfully (new orderId: " + str(new_orderId) + ") -> Return order creation data..")
		return resp
		
	else:

		errorData = str(resp['error_data'])
		bprint(defName + "<<< ERROR >>> " + side + " order creation error: '" + str(errorData) + "'")
		bprint(defName + "<<< ERROR >>> " + side + " order creation FAILED -> Trying fix..")

		fix_resp = POOL_orderFixer(mName, side, errorData)
		fix_orderId = fix_resp['orderId']

		if(fix_orderId > 0) :

			bprint(defName + "FIX worked! -> Returning new FIXED order data..")
			return fix_resp

		else :

			bprint(defName + "<<< ERROR >>> FIX didn't work -> Returning first (FAILED) order data..")
			return resp

def POOL_orderCreator(PARAM_marketName, PARAM_side) :

	defName = "POOL_orderCreator: "
	
	side = str(PARAM_side)
	mName = str(PARAM_marketName)

	mData = POOL_marketGetData(mName)
	mMarketSymbol = mData['MARKET_symbol']
	
	if (side == "BUY") :
		
		mPriceStop = float(mData['PRICE_BUY_stop'])
		mPriceLimit = float(mData['PRICE_BUY_limit'])
		mAmount = float(mData['TRADE_ASSET_amount'])

	elif (side == "SELL") :

		mPriceStop = float(mData['PRICE_SELL_stop'])
		mPriceLimit = float(mData['PRICE_SELL_limit'])
		mAmount = POOL_marketCalcSellAssetAmount(mName)

	else :

		bprint(defName + "ERROR: Unkown side for order creation")
		return None

	resp = EXCHANGE_ORDER_Create_StopLimit(mMarketSymbol, side, mPriceStop, mPriceLimit, mAmount)
	return resp

def POOL_orderFixer(PARAM_marketName, PARAM_side, PARAM_errorData) :

	defName = "POOL_orderFixer: "
	
	side = str(PARAM_side)
	errorData = str(PARAM_errorData)
	mName = str(PARAM_marketName)
	
	# Order creation failed
	errorStr1 = "APIError(code=-2010): Stop price would trigger immediately."
	errorStr2 = "APIError(code=-2010): Order would trigger immediately."

	if ((errorData == errorStr1) or (errorData == errorStr2)) :

		# refresh market data (market price, etc..)
		mData = POOL_marketGetData(mName)

		mPriceMarket = mData['PRICE_market']
		mPriceStop = mData['PRICE_BUY_stop']
		mBuyPriceMargin = mData['PRICE_BUY_margin']

		mMarketSymbol = mData['MARKET_symbol']
		mSellSymbol = str(mData['SELL_symbol'])
		mRounderPrices = int(mData['TRADE_round_prices'])
		mRounderAmounts = int(mData['TRADE_round_amounts'])
	
		bprint(defName + "<< FIX >> Trying immediate trigger fix -> Update " + side + " STOP, LIMIT prices and asset AMOUNT")
		bprint(defName + "<< FIX >> Fresh data from market " + mName + " [PRICE_market = " + str(mPriceMarket) + " " + str(mSellSymbol) + " ] ")

		fixerTriesMax = 5
		fixerTriesCounter = 1

		while (fixerTriesCounter <= fixerTriesMax) :

			if (side == "BUY") :

				bprint(defName + "Set new BUY STOP, LIMIT price using MARKET price: " + str(mPriceMarket) + " " + mSellSymbol)

				# Set status back to ILDE (won't be able to change STOP price if status is not IDLE)
				bprint(defName + "Pause TRADER and set market " + mName + " status = IDLE before setting new STOP price..")
				GVAR.TRADER_paused = True
				POOL_marketSetStatus(mName, "IDLE")

				# Refresh MARKET price
				mData = POOL_marketGetData(mName)
				mPriceMarket = mData['PRICE_market']
				mPriceStop = mData['PRICE_BUY_stop']
				
				newPriceStop = float(mPriceMarket) + float(mBuyPriceMargin)
				bprint(defName + "Current STOP price: " + str(mPriceStop) + " -> Calc NEW Stop using current MARKET_price + PRICE_BUY_margin")
				bprint(defName + "[ MARKET_price = " + str(mPriceMarket) + " ] + [ PRICE_BUY_margin = " + str(mBuyPriceMargin) + " ] -> NEW STOP price: " + str(newPriceStop) + " " + mSellSymbol)
				POOL_marketSetPriceStop(mName, newPriceStop)
				
				bprint(defName + "Set market " + mName + " status = TRADING and resume TRADER normal trading..")
				POOL_marketSetStatus(mName, "TRADING")
				GVAR.TRADER_paused = False
				
				# reload prices and new amount after POOL_marketSetPriceStop
				mData = POOL_marketGetData(mName)
				mPriceStop = float(mData['PRICE_BUY_stop'])
				mPriceLimit = float(mData['PRICE_BUY_limit'])
				mAmount = float(mData['TRADE_ASSET_amount'])
				
				resp = EXCHANGE_ORDER_Create_StopLimit(mMarketSymbol, side, mPriceStop, mPriceLimit, mAmount)
				new_orderId = str(resp['orderId'])

			if (side == "SELL") :

				bprint(defName + "Set new SELL STOP, LIMIT price using MARKET price: " + str(mPriceMarket) + " " + mSellSymbol)	
				
				priceSellMargin = mData['PRICE_SELL_margin']
				new_prices = SELL_CFB_CalcNewStopPrice(GVAR.SELL_CFB_margin_percent, priceSellMargin, GVAR.SELL_CFB_MV_margin_percent, mPriceMarket, mRounderPrices)
				mPriceStop = round(float(new_prices["price_stop"]), mRounderPrices)
				mPriceLimit = round(float(new_prices["price_limit"]), mRounderPrices)
				GVAR.POOL_markets[mName]['PRICE_SELL_stop'] = mPriceStop
				GVAR.POOL_markets[mName]['PRICE_SELL_limit'] = mPriceLimit
				mBuySymbol = mData['BUY_symbol']
				mRounderAmounts = int(mData['TRADE_round_amounts'])

				bprint(defName + 'In case of PARTIALLY SOLD requesting balance from server for ASSET: ' + str(mBuySymbol))
				
				assetBalanceData = EXCHANGE_ASSET_GetAssetBalance(mBuySymbol)
				unSoldAmount = round(float(assetBalanceData['free']),mRounderAmounts)
				
				originalAmount = POOL_marketCalcSellAssetAmount(mName)

				bprint(defName + 'Server returned ASSET balcance for symbol: ' + str(mBuySymbol) + " = " + str(unSoldAmount) + " ( Original bought amount: " + str(originalAmount) + ")" )

				resp = EXCHANGE_ORDER_Create_StopLimit(mMarketSymbol, side, mPriceStop, mPriceLimit, unSoldAmount)
				new_orderId = str(resp['orderId'])

			if (new_orderId != "0") :

				bprint(defName + "<< FIX >> Order fix worked OK at try " + str(fixerTriesCounter) + "/" + str(fixerTriesMax) + " -> Returning new orderId: " + str(new_orderId))
				bprint("")
				break

			else :

				bprint(defName + "<< FIX >> Order fix FAILED -> Retrying " + str(fixerTriesCounter) + "/" + str(fixerTriesMax) + " ..")
				fixerTriesCounter += 1
	
	elif (errorData == GVAR.TRADE_EXCEPTIONS_SELL_e1) :

		# Exception(1): MARKET price BELOW SELL STOP price while waiting for SELL order to FILL
		mData = POOL_marketGetData(mName)

		mPriceMarket = mData['PRICE_market']
		mMarketSymbol = mData['MARKET_symbol']
		mSellSymbol = mData['SELL_symbol']
		mRounderPrices = int(mData['TRADE_round_prices'])
		mRounderAmounts = int(mData['TRADE_round_amounts'])

		bprint(defName + "Fixing: " + GVAR.TRADE_EXCEPTIONS_SELL_e1)
		bprint(defName + "Set new SELL STOP, LIMIT price using MARKET price: " + str(mPriceMarket) + " " + mSellSymbol)
		priceSellMargin = mData['PRICE_SELL_margin']
		new_prices = SELL_CFB_CalcNewStopPrice(GVAR.SELL_CFB_margin_percent, priceSellMargin, GVAR.SELL_CFB_MV_margin_percent, mPriceMarket, mRounderPrices)
		mPriceStop = round(float(new_prices["price_stop"]), mRounderPrices)
		mPriceLimit = round(float(new_prices["price_limit"]), mRounderPrices)
		GVAR.POOL_markets[mName]['PRICE_SELL_stop'] = mPriceStop
		GVAR.POOL_markets[mName]['PRICE_SELL_limit'] = mPriceLimit
		mAmount = POOL_marketCalcSellAssetAmount(mName)

		resp = EXCHANGE_ORDER_Create_StopLimit(mMarketSymbol, side, mPriceStop, mPriceLimit, mAmount)

	else :

		bprint(defName + "<<< ERROR >>> Unkown error data -> errorData = '" + str(errorData) + "'")
		bprint(defName + "<<< ERROR >>> Unkown error data -> Return DUMMY resp (orderId = 0)")
		resp = { 'orderId' : 0 }

	return resp

def POOL_marketCalcSellAssetAmount(PARAM_marketName) :

	defName = "POOL_marketCalcSellAssetAmount: "

	mName = str(PARAM_marketName)
	#mData = POOL_marketGetData(mName)
	#mRounderAmounts = int(mData['TRADE_round_amounts'])

	# =======================================================
	# OLD (remove eventually)
	# =======================================================
	# Binance has this problem where BUY doesn't really BUY the exact ASSET amount you ask for in the BUY order
	# Ussually the new ASSET balance afer a BUY gets FILLED is slightly smaller than the BUY order ASSET amount
	# So to avoid decimal rounding and insuficient amount on SELL orders, the amount used is 99% of the BUY ASSET amount
	# If this isn't considered, all order updates will end in ERROR exceptions when creating SELL orders
	# mAmount = round(float(mData['TRADE_ASSET_amount']) * 0.995, mRounderAmounts)
	# =======================================================

	mAmount = GVAR.TRADE_amount_bought
	bprint(defName + "Called for market " + mName + " -> (NEW GVAR Version) -> Returning BOUGHT amount from [ GVAR.TRADE_amount_bought = " + str(mAmount) + " ]")

	return mAmount

def BINANCE_ORDER_Create_StopLimit (PARAM_symbol, PARAM_side, PARAM_priceStop, PARAM_priceLimit, PARAM_amount) :

	defName = "BINANCE_ORDER_Create_StopLimit: "

	marketSymbol = str(PARAM_symbol)
	priceStop = float(PARAM_priceStop)
	priceLimit = float(PARAM_priceLimit)
	amount = float(PARAM_amount)
	side = None

	# Allow 1 EXCHANGE_ORDER_StatusSync befere flushing after many errors
	tries_max = GVAR.TRADE_statusCheck_interval + 1

	tries_count = 0
	order_created = False
	error_data = None

	if (PARAM_side == "BUY") :
		side = SIDE_BUY	
	elif (PARAM_side == "SELL") :
		side = SIDE_SELL

	while True :
		
		try :
			
			bprint(defName + "Creating new order " + marketSymbol + " [ Side " + PARAM_side + " ] [ STOP price: " + str(priceStop) + " ] [ LIMIT price: " + str(priceLimit) + " ] [ Amount: " + str(amount) + " ] ")

			order_data = BINANCE.create_order(
					symbol=marketSymbol,
					side=side,
					type=ORDER_TYPE_STOP_LOSS_LIMIT,
					timeInForce=TIME_IN_FORCE_GTC,
					quantity=str(amount),
					stopPrice=str(priceStop),
					price=str(priceLimit),
					newOrderRespType='FULL',
					recvWindow=50000
					)

			order_created = True

			break

		except Exception as e:

			e = sys.exc_info()
			bprint("")
			bprint(defName + "Tries " + str(tries_count) + " / " + str(tries_max))
			ERROR_printer(e, defName)
			bprint("")

			if (tries_count < tries_max) :

				tries_count += 1					
				MICRO_sleep(1)

			else :

				bprint(defName + "Tries exhausted (" + str(tries_count) + "/" + str(tries_max) + ") -> Returning orderId = 0 and ERROR data")
				error_data = str(e[1])
				bprint(defName + "Returning received ERROR data: '" + error_data + "'")
				order_created = False
				break

	if (order_created == True) :

		data_str = str(order_data)
		data_str = data_str.replace("u'","'")
		data_str = data_str.replace("'",'"')
		order_data_json = json.loads(data_str)
		order_id = order_data_json["orderId"]

		GVAR.TRADE_statusCheck_counter = 0
		GVAR.TRADE_orderId = order_id

	else :

		order_id = 0
		# Something went wrong trying to create the new order -> Set counter to do Status Sync as immediately
		GVAR.TRADE_statusCheck_counter = GVAR.TRADE_statusCheck_interval
		GVAR.TRADE_orderId = None

	return { 'orderCreated' :  order_created , 'orderId' : order_id, 'side' : str(PARAM_side), 'priceStop' : priceStop, 'priceLimit' : priceLimit, 'amount' : amount, 'symbol' : marketSymbol, 'error_data' : str(error_data) }

def ERROR_printer(PARAM_e, PARAM_caller) :

	defName = "ERROR_printer -> " + PARAM_caller

	e = PARAM_e

	bprint(defName + "String: " + str(e))
	bprint(defName + "Return Type: " + str(type(e)))
	bprint(defName + "Index 0: " + str(e[0]))
	bprint(defName + "Index 1: " + str(e[1]))
	bprint(defName + "Index 2: " + str(e[2]))
	bprint(defName + "TraceBack: " + str(traceback.format_tb(e[2])))
	#return Desc[:30]: " + str(traceback.format_tb(e[2]))[:30] )
	
def IDLE_Delayer() :

	defName = "IDLE_Delayer: "
	
	index = GVAR.IDLE_delayer_index
	
	delay_limit = index
	delay_counter = 0

	# 0.25 is not enough time separation, block file doesn't get written -> 2 or more bots try to go into ACTIVE mode at the same time
	delay_sleep_ms = 0.55

	bprint("")
	bprint("")

	synchronized = False
	# Synchronization occurs every time / synchro_mod = 0
	# So if synchro_mod = 3 -> sync everytime seconds mod 3 = 0 (approx every 3 seconds)
	# BECAREFULL: use big enough synchro_mod value so as to all delayers finish before next time().tm_sec % synchro_mod == 0
	# IF NOT new synchronization chance occurs before all delayers have finished -> 2 bots may finish it's delay at same second -> ERROR
	#  
	synchro_mod = 10

	while(synchronized == False) :
		
		time_seconds = int(time.localtime().tm_sec)
		time_moded = int(time_seconds % synchro_mod)
		bprint(defName + "Synchro wait loop -> synchro_mod = " + str(synchro_mod) + " | time.tm_sec = " + str(time_seconds))
		
		if(time_moded == 0) :

			synchronized = True
			bprint(defName + "Synchro " + pcolors.GREEN + "COMPLETED" + pcolors.ENDC + "")
		
		else :
		
			MICRO_sleep(0.1)

	while(delay_counter < delay_limit) :
		
		bprint(defName + "Delay step: " + str(delay_counter) + " / " + str(delay_limit) + " -> Sleeping " + str(delay_sleep_ms) + " secs")
		MICRO_sleep(delay_sleep_ms)
		delay_counter += 1

	GVAR.IDLE_delayer_over = True

	bprint("")
	bprint("")
	bprint(defName + "Setting " + pcolors.YELLOW + "GVAR.IDLE_delayer_over" + pcolors.ENDC + " = True")
	bprint("")

"""def IDLE_ORDER_CheckStatus(PARAM_orderId, PARAM_symbol) :

	defName = "IDLE_ORDER_CheckStatus: "
	resp_status = "NULL"

	# BINANCE: According to the above information, there is a time gap from the matching engine to the final persistence. 
	# This time difference may be over 10 seconds at the moment when the market price fluctuates greatly. 
	# Our system is constantly optimised to keep the delay within 1 second.
	error_count = 0
	max_errors = 15
	sleep_time = 1

	#bprint(defName + pcolors.VIOLET + ">>>>> DEBUG ICS 1 >>>>> " + pcolors.ENDC + " Sending query to server with: PARAM_orderId = '" + str(PARAM_orderId) + "' | PARAM_symbol = '" + str(PARAM_symbol) + "'")
	#resp_get_status = EXCHANGE_ORDER_GetStatus (str(PARAM_orderId), PARAM_symbol)
	#resp_status = str(resp_get_status['status'])
	#return resp_status

	# Dummy case -> return FILLED
	if (str(PARAM_orderId) == "0") :
		bprint("")
		bprint(defName + pcolors.YELLOW + "DUMMY" + pcolors.ENDC + " case detected -> return FILLED to fool trade loop")
		return "FILLED"

	if (GVAR.FLAG_ERRORS_retry == False) :

		bprint("")
		bprint(defName + pcolors.VIOLET + ">>>>> DEBUG ICS 3 >>>>> " + pcolors.ENDC + " Sending query to server with: PARAM_orderId = '" + str(PARAM_orderId) + "' | PARAM_symbol = '" + str(PARAM_symbol) + "'")
		bprint(defName + "ERROR retry mode -> GVAR.FLAG_ERRORS_retry = " + str(GVAR.FLAG_ERRORS_retry))
		bprint(defName + "Current trade orderId -> GVAR.TRADE_orderId = " + str(GVAR.TRADE_orderId))
		bprint("")
		resp_get_status = EXCHANGE_ORDER_GetStatus (str(PARAM_orderId), str(PARAM_symbol))
		resp_status = str(resp_get_status['status'])

		return resp_status

	else :

		while(error_count < max_errors) :

				try : 

					bprint("")
					bprint(defName + pcolors.VIOLET + ">>>>> DEBUG ICS 2 >>>>> " + pcolors.ENDC + " Sending query to server with: PARAM_orderId = '" + str(PARAM_orderId) + "' | PARAM_symbol = '" + str(PARAM_symbol) + "'")
					bprint(defName + "ERROR retry mode -> GVAR.FLAG_ERRORS_retry = " + str(GVAR.FLAG_ERRORS_retry))
					bprint(defName + "Current trade orderId -> GVAR.TRADE_orderId = " + str(GVAR.TRADE_orderId))
					bprint("")
					resp_get_status = EXCHANGE_ORDER_GetStatus (str(PARAM_orderId), str(PARAM_symbol))
					resp_status = str(resp_get_status['status'])

					return resp_status

				except Exception as e:

					if(error_count < max_errors) :

						error_count += 1
						bprint("")
						
						bprint(defName + "IDLE Check status try ended in EXCEPTION -> error_count = " + str(error_count) + " | max_errors = " + str(max_errors))
						bprint(defName + pcolors.VIOLET + ">>>>> DEBUG ICS 2 >>>>> " + pcolors.ENDC + " Sending query to server with: PARAM_orderId = '" + str(PARAM_orderId) + "' | PARAM_symbol = '" + str(PARAM_symbol) + "'")
						bprint(defName + "ERROR retry mode -> GVAR.FLAG_ERRORS_retry = " + str(GVAR.FLAG_ERRORS_retry))
						bprint(defName + "Current trade orderId -> GVAR.TRADE_orderId = " + str(GVAR.TRADE_orderId))

						e = sys.exc_info()
						bprint("")
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " " + str(e))
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Type: " + str(type(e)))
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " return T: " + str(e[0]))
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Type: " + str(e[2]))
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Desc: " + str(traceback.format_tb(e[2])) )
						bprint("")
						bprint(defName + "Trying again..")
						bprint("")

						MICRO_sleep(sleep_time)

					else :

						bprint("")
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " " + str(e))
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Type: " + str(type(e)))
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " return T: " + str(e[0]))
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Type: " + str(e[2]))
						bprint(defName + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Desc: " + str(traceback.format_tb(e[2])) )
						bprint("")
						bprint(defName + pcolors.VIOLET + "PARAM_orderId = '" + str(PARAM_orderId) + "' | PARAM_symbol = '" + str(PARAM_symbol) + "'")
						bprint(defName + "ERROR retry mode -> GVAR.FLAG_ERRORS_retry = " + str(GVAR.FLAG_ERRORS_retry))
						bprint(defName + "Current trade orderId -> GVAR.TRADE_orderId = " + str(GVAR.TRADE_orderId))
						bprint(defName + "IDLE Check Status error count reached max_errors = " + str(max_errors) + " -> Exit bot")
						bprint("")
						quit()"""

def IDLE_ORDER_CheckLock() :

	lockFileExt = ".lock"
	lockFileDir = GVAR.BOT_LOCKS_DIR

	locked = False

	if any(File.endswith(lockFileExt) for File in os.listdir(lockFileDir)):
		locked = True
	else:
		locked = False

	#Old code to check if file exists
	#locked = path.exists(lockFile)

	return locked

def IDLE_ORDER_Lock() :

	defName = "IDLE_ORDER_Lock(): "
	botID = GVAR.BOT_ID
	lock_FileName = botID + ".lock"

	lock_FileDir = GVAR.BOT_LOCKS_DIR
	lock_File = lock_FileDir + "/" + lock_FileName

	os.system("touch "  + lock_File)

	GVAR.IDLE_locked = True

	bprint("")
	bprint(defName + "Lock file '" + lock_File + "' created")
	bprint("")

	#lockPID = str(os.getpid())
	#unlock_FileName = "trade.unlock"
	#unlock_File = "./" + unlock_FileName
	#os.system("echo 'rm " + lock_File + "\nrm " + unlock_File + "' > " + unlock_File)
	#os.system("chmod +x " + unlock_File)


def IDLE_ORDER_UnLock() :

	defName = "IDLE_ORDER_UnLock(): "
	botID = GVAR.BOT_ID

	lockFileName = botID + ".lock"
	lockFileDir = GVAR.BOT_LOCKS_DIR
	lockFile = lockFileDir + "/" + lockFileName

	os.system("rm " + lockFile)

	GVAR.IDLE_locked = False
	GVAR.IDLE_delayer_over = False

	bprint("")
	bprint(defName + "Lock file '" + lockFile + "' removed")
	bprint("")

	#lockPID = str(os.getpid())
	#unlock_FileName = "trade.unlock"
	#unlock_File = "./" + unlock_FileName
	#os.system("rm " + unlock_File)


def IDLE_ORDER_ReCalc() :

	defName = "IDLE_ORDER_ReCalc(): "

	new_price_stop = float(GVAR.STATISTICS_TICKER_cache_max[1]) + float(GVAR.BUY_price_margin)

	if(float(new_price_stop) > float(GVAR.BUY_price_stop)) :

		GVAR.BUY_price_stop = round(new_price_stop, GVAR.TRADE_round_prices)
		GVAR.BUY_price_limit = round(float(GVAR.BUY_price_stop) + float(GVAR.BUY_price_margin), GVAR.TRADE_round_prices)
		GVAR.IDLE_price_limit = calcIdlePriceLimit(GVAR.BUY_price_stop, GVAR.IDLE_price_margin_mp)

		bprint("")
		bprint(defName + "GVAR.STATISTICS_TICKER_cache_max = " + str(GVAR.STATISTICS_TICKER_cache_max))
		bprint(defName + "New GVAR.BUY_price_stop = " + str(GVAR.BUY_price_stop))
		bprint(defName + "New GVAR.BUY_price_limit = " + str(GVAR.BUY_price_limit))
		bprint(defName + "New GVAR.IDLE_price_limit = " + str(GVAR.IDLE_price_limit))
		bprint("")

	else :

		bprint("")
		bprint(defName + "Current BUY " + pcolors.YELLOW + "STOP, LIMIT, IDLE" + pcolors.ENDC + " are " + pcolors.GREEN + "OK" + pcolors.ENDC + " (BUY_price_stop > new_price_stop)")
		bprint(defName + "Using current GVAR.BUY_price_stop = " + str(GVAR.BUY_price_stop))
		bprint(defName + "Using current GVAR.BUY_price_limit = " + str(GVAR.BUY_price_limit))
		bprint(defName + "Using current GVAR.IDLE_price_limit = " + str(GVAR.IDLE_price_limit))
		bprint("")
	
	GVAR.IDLE_mode_on = True
	GVAR.BUY_fixed_price_enabled = True


def BUYCHECK_CreateBuyCheck() :

	defName = "BUYCHECK_CreateBuyCheck(): "

	checkDir = "../BUYCHECKS"
	checkFileName = GVAR.BOT_ID + ".in"
	checkFile = checkDir + "/" + checkFileName

	os.system("touch " + checkFile)

	bprint("")
	bprint(defName + pcolors.YELLOW + "BUY checkfile " + pcolors.ENDC + pcolors.GREEN + "CREATED" + pcolors.ENDC + " (" + checkFileName + ")")
	bprint("")

def BUYCHECK_RemoveBuyCheck() :

	defName = "BUYCHECK_RemoveBuyCheck(): "

	checkDir = "../BUYCHECKS"
	checkFileName = GVAR.BOT_ID + ".in"
	checkFile = checkDir + "/" + checkFileName

	os.system("rm " + checkFile)

	bprint("")
	bprint("")
	bprint(defName + pcolors.YELLOW + "BUY checkfile " + pcolors.ENDC + pcolors.GREEN + "REMOVED" + pcolors.ENDC + " (" + checkFileName + ")")
	bprint("")

def BUY_PRICE_improver() :

	a = 1
	
def BINANCE_ORDER_GetStatus (PARAM_Order_Id, PARAM_Symbol) :
	
	symbol = str(PARAM_Symbol)
	orderId = str(PARAM_Order_Id)

	defName = "BINANCE_ORDER_GetStatus: "

	# BINANCE: According to the above information, there is a time gap from the matching engine to the final persistence. 
	# This time difference may be over 10 seconds at the moment when the market price fluctuates greatly. 
	# Our system is constantly optimised to keep the delay within 1 second.

	error_count = 0
	max_errors = 15
	sleep_time = 1

	order_found = False

	# Dummy case -> return FILLED
	if (str(PARAM_Order_Id) == "0") :
		bprint("")
		bprint(defName + "DUMMY case detected -> return FILLED to fool trade loop")
		return { 'orderId' : "0" , 'status' : "FILLED" }

	while (error_count <= max_errors) :

		try :

			order_data = BINANCE.get_order(symbol=symbol, orderId=orderId, recvWindow=50000)
			order_found = True

			break

		except Exception as e:

			if (error_count < max_errors) :

				if (error_count == 0) :
					
					#bprint("")
					bprint(defName + "Check status (order_id = " + str(orderId) + ") try ended in EXCEPTION (GVAR.FLAG_ERRORS_retry = " + str(GVAR.FLAG_ERRORS_retry) + ") -> error_count = " + str(error_count) + " | max_errors = " + str(max_errors))
					bprint(defName + "<<< WARNING >>>" + pcolors.ENDC + " Status updates in Binance order engine takes up to 10 secs to update")

				e = sys.exc_info()
				bprint(defName + "ERROR [orderId = " + str(orderId) + "] [symbol = " + str(symbol) + "] -> Try(" + str(error_count) + ") = " + str(e[1]) )
				
				error_count += 1
				MICRO_sleep(sleep_time)

			else :

				bprint("")
				bprint(defName + "<<< WARNING >>> ERROR count reached max_errors = " + str(max_errors) + " -> Checking with ALL open orders..")
				bprint("")

				order_found = False
				open_orders_data_json = BINANCE_ORDERS_printOpenOrders()
				for item_json in open_orders_data_json :

					item_order_id = item_json['orderId']
					if (str(item_order_id) == str(orderId)) :
						
						order_found = True
						item_order_status = item_json['status']

						bprint(defName + "ORDER FOUND in OPEN ORDERS list -> returning status: " + str(item_order_status))
						return { 'orderId' : item_order_id , 'status' : item_order_status }

				break

	if (order_found == True) :

		data_str = str(order_data)
		data_str = data_str.replace("u'","'")
		data_str = data_str.replace("'",'"')
		data_str = data_str.replace("True",'true')
		data_str = data_str.replace("False",'false')
		order_data_json = json.loads(data_str)

		order_id = order_data_json["orderId"]
		order_status = order_data_json['status']

		return { 'orderId' : order_id , 'status' : order_status }
	
	else :
		
		bprint(defName + "<<< ERROR >>> Order NOT FOUND (" + str(orderId) + ") -> Will try returning DUMMY response with { orderId = 0 , status = 'FILLED' } to fool trade loop..")
		return { 'orderId' : 0 , 'status' : "FILLED" }

def BINANCE_ORDER_GetData (PARAM_Order_Id, PARAM_Symbol) :
	
	symbol = PARAM_Symbol
	orderId = PARAM_Order_Id

	while True :

		try :

			order_data = BINANCE.get_order(symbol=symbol, orderId=orderId, recvWindow=50000)

			break

		except Exception as e:

			e = sys.exc_info()
			print ""
			print "[BOT] BINANCE_ORDER_GetData: ERROR: " + str(e)
			print "[BOT] BINANCE_ORDER_GetData: ERROR return Type: " + str(type(e))
			print "[BOT] BINANCE_ORDER_GetData: ERROR return T: " + str(e[0])
			print "[BOT] BINANCE_ORDER_GetData: ERROR return Type: " + str(e[2])
			print "[BOT] BINANCE_ORDER_GetData: ERROR return Type: " + str(traceback.format_tb(e[2]))
			print ""

			sleep(GVAR.TICKER_sleep)

		else :

			print ""
			print "[BOT] ERROR >>> BINANCE_ORDER_GetStatus: " + "ERROR Unknown"
			print ""

			sleep(GVAR.TICKER_sleep)

	data_str = str(order_data)
	data_str = data_str.replace("u'","'")
	data_str = data_str.replace("'",'"')
	data_str = data_str.replace("True",'true')
	data_str = data_str.replace("False",'false')
	order_data_json = json.loads(data_str)

	#bprint("BINANCE_ORDER_GetStatus: Order Id: " + str(orderId) + " -> Order Status: " + pcolors.GREEN + order_status + pcolors.ENDC)
	return order_data

def BINANCE_GetMyTrades (PARAM_symbol) :
	
	symbol = str(PARAM_symbol)
	#fromOrderId = int(PARAM_fromOrderId)
	
	defName = "BINANCE_GetMyTrades: "

	# Limit the amount of trades received starting from last trade in a given symbol
	limit = 20

	bprint(defName + "Sending request to BINANCE server.. < symbol = " + symbol + " > < limit = " + str(limit) + " >")

	while True :

		try :

			#order_data = BINANCE.get_my_trades(symbol=symbol, limit=limit, fromId=fromOrderId, recvWindow=50000)
			order_data = BINANCE.get_my_trades(symbol=symbol, limit=limit, recvWindow=50000)

			break

		except Exception as e:

			e = sys.exc_info()
			print ""
			print "[BOT] BINANCE_ORDER_GetData: ERROR: " + str(e)
			print "[BOT] BINANCE_ORDER_GetData: ERROR return Type: " + str(type(e))
			print "[BOT] BINANCE_ORDER_GetData: ERROR return T: " + str(e[0])
			print "[BOT] BINANCE_ORDER_GetData: ERROR return Type: " + str(e[2])
			print "[BOT] BINANCE_ORDER_GetData: ERROR return Type: " + str(traceback.format_tb(e[2]))
			print ""

			sleep(GVAR.TICKER_sleep)

		else :

			print ""
			print "[BOT] ERROR >>> BINANCE_ORDER_GetStatus: " + "ERROR Unknown"
			print ""

			sleep(GVAR.TICKER_sleep)

	data_str = str(order_data)
	data_str = data_str.replace("u'","'")
	data_str = data_str.replace("'",'"')
	data_str = data_str.replace("True",'true')
	data_str = data_str.replace("False",'false')
	order_data_json = json.loads(data_str)

	#bprint("BINANCE_ORDER_GetStatus: Order Id: " + str(orderId) + " -> Order Status: " + pcolors.GREEN + order_status + pcolors.ENDC)
	return order_data

def SIMULATOR_ORDER_GetStatus (PARAM_OrderId, PARAM_Symbol) :

	symbol = PARAM_Symbol
	orderId = PARAM_OrderId

	fake_counter = GVAR.SIMULATOR_getStatus_unFilled_returns_counter
	fake_counter_max = GVAR.SIMULATOR_getStatus_unFilled_returns
	if (fake_counter == fake_counter_max) :
		order_status = "FILLED"
	else :
		order_status = "NEW"
		GVAR.SIMULATOR_getStatus_unFilled_returns_counter += 1
		fake_counter = GVAR.SIMULATOR_getStatus_unFilled_returns_counter
		bprint("SIMULATOR_ORDER_GetStatus: Use " + pcolors.YELLOW + "FAKE " + pcolors.ENDC + str(fake_counter) + "/" + str(fake_counter_max) + " return -> Set Order Status: " + pcolors.GREEN + order_status + pcolors.ENDC)

	bprint("SIMULATOR_ORDER_GetStatus: Order Id: " + str(orderId) + " -> Order Status: " + pcolors.GREEN + order_status + pcolors.ENDC)

	return { 'orderId' : orderId , 'status' : order_status }

def EXCHANGE_ORDER_StatusSync(PARAM_Side, PARAM_ForceCheck, PARAM_Caller) :

	defName = "EXCHANGE_ORDER_StatusSync: "
	callerStr = str(PARAM_Caller)
	
	mName = GVAR.TRADER_marketName
	mData = POOL_marketGetData(mName)
	mSymbol = mData['MARKET_symbol']

	GVAR.TRADE_statusCheck_counter += 1
	orderId = GVAR.TRADE_orderId

	if (str(orderId) == "0") :
		bprint("")
		bprint(defName + "<<< WARNING >>> orderId = " + str(orderId) + " -> Do Nothing")
		bprint("")
		return None
		
	if((GVAR.TRADE_statusCheck_counter == GVAR.TRADE_statusCheck_interval) or (PARAM_ForceCheck == True)) :

		bprint("")
		bprint(defName + "Invoked by '" + callerStr + "' Side: " + str(PARAM_Side) + " ForceCheck: " + str(PARAM_ForceCheck) + " GVAR.TRADE_statusCheck_counter: " + str(GVAR.TRADE_statusCheck_counter))
		
		if(GVAR.TRADE_statusCheck_counter == GVAR.TRADE_statusCheck_interval) :
			bprint(defName + "[Market: " + mName + "] [Symbol: " + mSymbol + "] [Side: " + PARAM_Side + "] [Check counter: " + str(GVAR.TRADE_statusCheck_counter) + "] -> Checking Status for orderId: " + str(orderId))

		if(PARAM_ForceCheck == True) :
			bprint(defName + "Forced Check -> Checking Status for orderId: " + str(orderId))

		GVAR.TRADE_statusCheck_counter = 0

		tmpResp = EXCHANGE_ORDER_GetStatus(orderId, mSymbol)
		GVAR.TRADE_status = tmpResp['status']
		
		if (GVAR.TRADE_status == "FILLED") :

			bprint(defName + "Server reply : Order Status " + pcolors.TUR + GVAR.TRADE_status + pcolors.ENDC)

			if(PARAM_Side == "BUY") :
				
				bprint(defName + "BUY Order was FILLED and still used as TRADE order: -> Enable SELL mode NOW")

				GVAR.BUY_mode_on = False
				GVAR.TRADER_mode = "BUY_FILLED"

				#IDLE_ORDER_Lock()
				#BUYCHECK_CreateBuyCheck()

			if(PARAM_Side == "SELL") :
				
				bprint("EXCHANGE_ORDER_StatusSync: SELL Order was FILLED and still used as TRADE order: -> Set TRADE as FINISHED")
				
				GVAR.SELL_mode_on = False
				GVAR.TRADER_mode = "SELL_FILLED"

				#IDLE_ORDER_UnLock()
				#BUYCHECK_RemoveBuyCheck()

			return "FILLED"

		elif (GVAR.TRADE_status == "NEW") :
			
			if(PARAM_Side == "BUY") :
				bprint(defName + "Server replied BUY orderId (" + str(orderId) + ") status: NEW (not filled) -> Do NOTHING")
				bprint("")

			if(PARAM_Side == "SELL") :
				bprint(defName + "Server replied SELL orderId (" + str(orderId) + ") status: NEW (not filled) -> Do NOTHING")
				bprint("")

			return "NEW"
		
		else :

			bprint("")
			bprint(defName + "Status Check ELSE case -> Check returned status: " + str(GVAR.TRADE_status))
			bprint("")
			return GVAR.TRADE_status

def IO_PreCreateOrderInfo (PARAM_Buy_Price_Stop, PARAM_Buy_Price_Limit, PARAM_Buy_Price_Margin, PARAM_Buy_Amount, PARAM_Buy_Symbol, PARAM_Sell_Symbol) :

	price_stop = PARAM_Buy_Price_Stop
	price_limit = PARAM_Buy_Price_Limit
	amount = PARAM_Buy_Amount
	symbol_buy = PARAM_Buy_Symbol
	symbol_sell = PARAM_Sell_Symbol
	price_margin = PARAM_Buy_Price_Margin

	tmp_str0 = "If price goes above " + pcolors.TUR + str(price_stop) + pcolors.ENDC + " "
	tmp_str01 = pcolors.GREEN + symbol_sell + pcolors.ENDC
	tmp_str1 = " -> Buy " + pcolors.TUR + str(amount) + pcolors.ENDC + " " + pcolors.GREEN + symbol_buy + pcolors.ENDC
	tmp_str2 = " at STOP "+ pcolors.TUR + str(price_stop) + pcolors.ENDC
	tmp_str3 = " " + pcolors.GREEN + symbol_sell + pcolors.ENDC
	tmp_str4 = " LIMIT " + pcolors.TUR + str(price_limit) + pcolors.ENDC + " " + pcolors.GREEN + symbol_sell + pcolors.ENDC
	bprint("IO_PreCreateOrderInfo: Stop price margin is: " + str(price_margin))
	bprint("IO_PreCreateOrderInfo: " + tmp_str0 + tmp_str01 + tmp_str1 + tmp_str2 + tmp_str3 + tmp_str4)

def BUY_CFA_Looper (	PARAM_BUY_CFA_margin_percent ,
						PARAM_BUY_CFA_MV_margin_percent ,
						PARAM_BUY_price_margin ,
						PARAM_BUY_price_stop ,
						PARAM_TICKER_price_bid ,
						PARAM_BUY_symbol ,
						PARAM_SELL_symbol ,
						PARAM_symbol ,
						PARAM_TRADE_orderId , 
						PARAM_BUY_amount ,
					) :

	# checks ir buy price is still inside the permited margin when prices are going down
	# if not (price too "up" from TICKER) -> cancel order -> create new buy order at CFA_margin from TICKER price

	if (GVAR.FLAG_CFA_manual_mode == False) :
		result = CFA_PriceInMargin(PARAM_BUY_CFA_margin_percent, PARAM_BUY_price_stop, PARAM_TICKER_price_bid)
	else :
		result = CFA_PriceInMargin(GVAR.BUY_CFA_margin_percent_enabler, PARAM_BUY_price_stop, PARAM_TICKER_price_bid)
		if (result == False) :
			bprint("")
			bprint("")
			bprint("STOP price distance > " + str(GVAR.BUY_CFA_margin_percent_enabler) + " -> CFA manual mode disabled -> CFA enabled again")
			bprint("")

	if (result == False) :

		GVAR.FLAG_CFA_manual_mode = False

		str1 = pcolors.TUR + str(PARAM_BUY_price_stop) + pcolors.ENDC
		str2 = str(round(float(PARAM_TICKER_price_bid),2))
		str2_1 = " (CFAmp = " + str(PARAM_BUY_CFA_margin_percent) + " %)"

		bprint("BUY_CFA_Looper: " + pcolors.YELLOW + "BUY price " + pcolors.ENDC + str1 + " too high from current price " + pcolors.TUR + str2 + pcolors.ENDC + str2_1)

		# Use CFA (Chase (buy price) From Avobe (ticker price)) margin percent to set new StopPrice
		# Also uses the MVM (micro volatility margin) to avoid constant updates of new StopPrice when price swings down in permited MVM
		new_price_stop = round(CFA_BUY_CalcNewPrice(PARAM_BUY_CFA_margin_percent, PARAM_BUY_CFA_MV_margin_percent, PARAM_TICKER_price_bid),GVAR.TRADE_round_prices)
		new_price_limit = new_price_stop + PARAM_BUY_price_margin
		new_price_stop_str = pcolors.TUR + str(new_price_stop) + pcolors.ENDC
		str3 = pcolors.GREEN + PARAM_SELL_symbol + pcolors.ENDC

		bprint("")
		bprint("BUY_CFA_Looper: New BUY Stop price set at: " + new_price_stop_str + " " + str3)
		bprint("BUY_CFA_Looper: Canceling Order ID: " + pcolors.VIOLET + str(PARAM_TRADE_orderId) + pcolors.ENDC)

		resp = EXCHANGE_ORDER_Cancel(PARAM_symbol, PARAM_TRADE_orderId)

		bprint("BUY_CFA_Looper: Order canceled -> resp[:30]: " + str(resp)[:30])
		bprint("")
		bprint("BUY_CFA_Looper: Create new BUY order " + "STOP: " + pcolors.TUR + str(new_price_stop) + pcolors.ENDC + " LIMIT: " + pcolors.TUR + str(new_price_limit) + pcolors.ENDC + " Symbol: " + str(PARAM_symbol) + " Amount: " + str(PARAM_BUY_amount) + str2_1)

		resp = EXCHANGE_ORDER_Create_StopLimit (PARAM_symbol, SIDE_BUY, new_price_stop, new_price_limit, PARAM_BUY_amount)

		# Set the new values for global variables	
		new_orderId = resp['orderId']
		GVAR.TRADE_orderId = new_orderId
		GVAR.BUY_price_stop = new_price_stop
		GVAR.BUY_price_limit = new_price_limit

		bprint("BUY_CFA_Looper: ORDER CREATED - New OrderId: " + str(new_orderId))
		bprint("")

def fix_floats(data):
    if isinstance(data,list):
        iterator = enumerate(data)
    elif isinstance(data,dict):
        iterator = data.items()
    else:
        raise TypeError("can only traverse list or dict")

    for i,value in iterator:
        if isinstance(value,(list,dict)):
            fix_floats(value)
        elif isinstance(value,str):
            try:
                data[i] = float(value)
            except ValueError:
                pass

def SIMULATOR_TICKER_GetTickerData (PARAM_symbol) :

	if (GVAR.SIMULATOR_TICKER_data == []) :
		bprint("")
		bprint("")
		bprint("SIMULATOR_TICKER_GetTickerData: " + pcolors.YELLOW  + "Loading File -> " + pcolors.ENDC + pcolors.GREEN + GVAR.SIMULATOR_TICKER_dataFile + pcolors.ENDC)
		bprint("")
		SIMULATOR_TICKER_LoadData()
	
	index = GVAR.SIMULATOR_TICKER_index
	
	if( index < len(GVAR.SIMULATOR_TICKER_data) ) :
		data_str = GVAR.SIMULATOR_TICKER_data[index]

		if(GVAR.MODE_VERBOSE_enabled == False) :
			data_lines = len(GVAR.SIMULATOR_TICKER_data)
			sim_progress_percent = round(index * 100 / data_lines,2)
			sys.stdout.write(" >> TICKER " + str(index) + "/" + str(data_lines) + " ( " + str(sim_progress_percent) + "% ) \r")
			sys.stdout.flush()

	else :
		bprint("")
		bprint("")
		bprint("SIMULATOR_TICKER_GetTickerData: " + pcolors.YELLOW  + "SIMULATION END -> " + pcolors.ENDC + pcolors.GREEN + GVAR.SIMULATOR_TICKER_dataFile + pcolors.ENDC)
		bprint("")
		printTradesLoopStatistics()
		quit()

	# TRIME price float sub string
	time_str = data_str[:8]
	#price = float(price_str)

	# TRIME price float sub string
	price_str = data_str[9:20]
	#price_str = price_str[:12]
	price = float(price_str)
	
	data_json_fake = { 'bidPrice' : price , 'time' : time_str } 

	TICKER_CACHE_AddNewTick(time_str, price)
	
	GVAR.SIMULATOR_TICKER_index += 1
	GVAR.SIMULATOR_TICKER_time = time_str
	
	#bprint("")
	#bprint("")
	#bprint("SIMULATOR_TICKER_GetTickerData: " + pcolors.YELLOW  + "PRICE -> " + pcolors.ENDC + pcolors.GREEN + str(price_str) + pcolors.ENDC)
	#bprint("")

	return data_json_fake

def SIMULATOR_TICKER_LoadData() :

	file_name = GVAR.SIMULATOR_TICKER_dataDir + GVAR.SIMULATOR_TICKER_dataFile

	with open(file_name) as f:
		content = f.readlines()
		# you may also want to remove whitespace characters like `\n` at the end of each line
		content = [x.strip() for x in content]

	GVAR.SIMULATOR_TICKER_data = content
	GVAR.SIMULATOR_TICKER_index = 0

def BINANCE_ASSET_GetAssetBalance (PARAM_asset) :

	mAsset = PARAM_asset
	ASSET_data = BINANCE.get_asset_balance(asset=mAsset)
	data_str = str(ASSET_data)
	data_str = data_str.replace("u'","'")
	data_str = data_str.replace("'",'"')
	data_str = data_str.replace("True","true")
	data_str = data_str.replace("False","false")
	ASSET_data_json = json.loads(data_str)

	return ASSET_data_json

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
			bprint("")
			bprint("[BOT] BINANCE_TICKER_GetTickerData: ERROR: " + str(e))
			bprint("[BOT] BINANCE_TICKER_GetTickerData: ERROR return Type: " + str(type(e)))
			bprint("[BOT] BINANCE_TICKER_GetTickerData: ERROR return T: " + str(e[0]))
			bprint("[BOT] BINANCE_TICKER_GetTickerData: ERROR return Type: " + str(e[2]))
			bprint("[BOT] BINANCE_TICKER_GetTickerData: ERROR return Output[-50:] : ... " + str(traceback.format_tb(e[2]))[-50:])
			bprint("")
			MICRO_sleep(GVAR.TICKER_sleep)

		else:

			bprint("")
			bprint("[BOT] BINANCE_TICKER_GetTickerData: ERROR - Unknown")
			bprint("")
			MICRO_sleep(GVAR.TICKER_sleep)

	# Check before adding to CACHE if requested symbol is current TRADE symbol
	# When asking for FEE price TICKER_GetTickerData is called with BNBUSDT
	# then wrong prices are added at CACHE and then used as new max for next loop
	#if(PARAM_symbol == GVAR.symbol) :
	#	TICKER_CACHE_AddNewTick(TIME_getNowTime(), TICKER_data_json['bidPrice'])

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
			bprint("")
			bprint(defName + "ERROR: " + str(e))
			bprint(defName + "ERROR return Type: " + str(type(e)))
			bprint(defName + "ERROR return T: " + str(e[0]))
			bprint(defName + "ERROR return Type: " + str(e[2]))
			bprint(defName + "ERROR return Output[-50:] : ... " + str(traceback.format_tb(e[2]))[-50:])
			bprint("")
			MICRO_sleep(GVAR.TICKER_sleep)

		else:

			bprint("")
			bprint(defName + "ERROR - Unknown")
			bprint("")
			MICRO_sleep(GVAR.TICKER_sleep)

	# Check before adding to CACHE if requested symbol is current TRADE symbol
	# When asking for FEE price TICKER_GetTickerData is called with BNBUSDT
	# then wrong prices are added at CACHE and then used as new max for next loop
	#if(PARAM_symbol == GVAR.symbol) :
	#	TICKER_CACHE_AddNewTick(TIME_getNowTime(), TICKER_data_json['bidPrice'])

	return TICKER_data_json

def TICKER_CACHE_AddNewTick(PARAM_time, PARAM_price) :

	timeStr = str(PARAM_time)
	priceF = float(PARAM_price)
	tickerItem = (timeStr, priceF)

	maxLenght = GVAR.STATISTICS_TICKER_cache_size

	if (len(GVAR.STATISTICS_TICKER_cache) == maxLenght) :
		GVAR.STATISTICS_TICKER_cache.pop(0)

	GVAR.STATISTICS_TICKER_cache.append(tickerItem)
	TICKER_CACHE_analize()

def MARKET_CACHE_getPriceDirection(PARAM_marketName) :

	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	max = GVAR.POOL_markets[mName]['PRICE_CACHE_market_max'][1]
	min = GVAR.POOL_markets[mName]['PRICE_CACHE_market_min'][1]

	delta = round(100 - (min * 100) / max,2)

	max_index = GVAR.POOL_markets[mName]['PRICE_CACHE_market_max']
	min_index = GVAR.POOL_markets[mName]['PRICE_CACHE_market_min']
	directionStr = "None"

	if (max_index > min_index ) : directionStr = "UP"
	if (max_index == min_index ) : directionStr = "UNCH"
	if (max_index < min_index ) : directionStr = "DOWN"

	return (directionStr, delta)

def TICKER_CACHE_convertPriceDirectionToArrowStr(PARAM_PriceDirectionTuple) :

	priceDirection = PARAM_PriceDirectionTuple

	if(priceDirection[0] == "UP") : 		
		priceDirectionStr = pcolors.GREEN + "/\\" + pcolors.ENDC
	elif(priceDirection[0] == "DOWN") :
		priceDirectionStr = pcolors.RED + "\\/" + pcolors.ENDC
	elif(priceDirection[0] == "UNCH") :
		priceDirectionStr = "--"

	return priceDirectionStr

def MARKET_CACHE_analizer(PARAM_marketName) :

	defName = "MARKET_CACHE_analizer: "

	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	#bprint(defName + ">>> DEBUG: Analizing market " + mName)

	TICKER_cache = mData['PRICE_CACHE_market']

	GVAR.POOL_markets[mName]['PRICE_CACHE_market_max'] = TICKER_cache[0]
	GVAR.POOL_markets[mName]['PRICE_CACHE_market_min'] = TICKER_cache[0]
	GVAR.POOL_markets[mName]['PRICE_CACHE_market_max_index'] = 0
	GVAR.POOL_markets[mName]['PRICE_CACHE_market_min_index'] = 0

	max = TICKER_cache[0][1]
	min = TICKER_cache[0][1]
	amplitude_percent = None

	# This will be the maximun-index-position where a new max can be determined
	# The lag is necesary because if it is not used, any sudden rise in price becomes the new max
	# lag_index = (GVAR.STATISTICS_TICKER_cache_size - GVAR.STATISTICS_TICKER_cache_lag)

	for item in TICKER_cache :

		#item_index = float(TICKER_cache.index(item[0]))
		item_val = float(item[1])
		if item_val >= max :
			max = item_val
			GVAR.POOL_markets[mName]['PRICE_CACHE_market_max'] = item
			GVAR.POOL_markets[mName]['PRICE_CACHE_market_max_index'] = TICKER_cache.index(item)
			GVAR.POOL_markets[mName]['PRICE_CACHE_market_amplitude_price'] = max - min
			amplitude_percent = round(100 - (min * 100 / max),2)
			GVAR.POOL_markets[mName]['PRICE_CACHE_market_amplitude_percent'] = amplitude_percent

		if item_val <= min :
			min = item_val
			GVAR.POOL_markets[mName]['PRICE_CACHE_market_min'] = item
			GVAR.POOL_markets[mName]['PRICE_CACHE_market_min_index'] = TICKER_cache.index(item)

	#if(GVAR.IDLE_mode_on == False) :

		# Disable peak search for now

		#TICKER_CACHE_identifyRightestPeak(GVAR.STATISTICS_TICKER_cache_peak_inflexion_percent)

def BUY_AWT_CalcBuyPrices(PARAM_last_peak_price) :

	wave_max_amplitude = round(GVAR.STATISTICS_TICKER_cache_amplitude_percent,2)
	last_peak_price = round(float(PARAM_last_peak_price),GVAR.TRADE_round_prices)
	stop_price = round(last_peak_price + (last_peak_price / 100 * GVAR.BUY_AWT_AWmP),2)
	limit_price = stop_price + GVAR.BUY_price_margin

	return { 'price_stop' : stop_price, 'price_limit' : limit_price }

def BUY_AWT_changeBuyOrderPrice(PARAM_orderId, PARAM_price_stop, PARAM_price_limit) :

	orderId = PARAM_orderId
	stop_price = float(PARAM_price_stop)
	limit_price = float(PARAM_price_limit)

	bprint ("BUY_AWT_changeBuyOrderPrice: Cancelling orderId: " + str(orderId))
	resp = EXCHANGE_ORDER_Cancel(GVAR.symbol, orderId)
	bprint ("BUY_AWT_changeBuyOrderPrice: Creating new BUY order at STOP price: " + pcolors.VIOLET + str(stop_price) + pcolors.ENDC + " LIMIT price: " + pcolors.VIOLET + str(limit_price) + pcolors.ENDC + " " + pcolors.GREEN + GVAR.SELL_symbol + pcolors.ENDC)
	resp = EXCHANGE_ORDER_Create_StopLimit(GVAR.symbol, SIDE_BUY, stop_price, limit_price, GVAR.BUY_amount)
	if (resp['orderCreated'] == True) :
		GVAR.BUY_price_stop = stop_price
		GVAR.BUY_price_limit = limit_price
		GVAR.TRADE_orderId = resp['orderId']

		if(GVAR.SIMULATOR_TICKER_debug_stops == True) :
			GVAR.TICKER_sleep = 1

	bprint ("BUY_AWT_changeBuyOrderPrice: Order created -> New orderId: " + pcolors.VIOLET + str(GVAR.TRADE_orderId) + pcolors.ENDC )
	bprint ("")

def TICKER_CACHE_identifyRightestPeak(PARAM_fallPercent) :

	TICKER_cache = GVAR.STATISTICS_TICKER_cache
	TICKER_cache_indexed = []
	
	DELTA_max = 0
	DELTA_max_item = None
	DELTA_min = 0
	DELTA_min_item = None
	STATISTICS_TICKER_cache_rightest_bottom = None
	STATISTICS_TICKER_cache_rightest_peak = None
	#STATISTICS_TICKER_cache_rightest_peak_found = False

	STATISTICS_TICKER_cache_inflexion_delta_max = 0
	STATISTICS_TICKER_cache_inflexion_delta_max_data = None
	STATISTICS_TICKER_cache_peak_candidate_data = None
	STATISTICS_TICKER_cache_inflexion_delta_min = 0
	STATISTICS_TICKER_cache_inflexion_delta_min_data = None
	STATISTICS_TICKER_cache_bottom_candidate_data = None

	# Clone list with index
	index = 0
	for item in GVAR.STATISTICS_TICKER_cache :
		TICKER_cache_indexed.append((index, item[0], item[1]))
		index += 1

	# Reverse TICKER cache to search from right
	TICKER_cache_indexed.reverse()
	TICKER_cache_reversed = TICKER_cache_indexed

	price_prev = 0
	counter = 0
	fallPercent = float(PARAM_fallPercent) * -1
	risePercent = float(PARAM_fallPercent)

	rightest_peak_item = None
	rightest_bottom_item = None
	# First candidate is first item in list
	rightest_bottom_candidate_item = TICKER_cache_reversed[0]
	# Search bottom to start search
	found_bottom = False
	found_peak = False
	# Start search 1) bottom 2) peek "after" (is "before" but reversed is "after") peek
	for item in TICKER_cache_reversed :

		price = float(item[2])

		if (found_bottom == False) :

			rightest_bottom_candidate_price = float(rightest_bottom_candidate_item[2])

			if (price <= rightest_bottom_candidate_price) :

				# Using <= here is very important (do not use <) so that final selected bottom item is the closest distance possible from the peak
				rightest_bottom_candidate_item = item

			else :

				price_diff_percent = 100 - ((rightest_bottom_candidate_price * 100) / price)
				price_diff_percent = round(price_diff_percent, 2)

				# Saving this data (biggest price increase) for debug
				if(price_diff_percent > DELTA_max) :
					DELTA_max = price_diff_percent
					DELTA_max_item = item
			
				if(price_diff_percent >= risePercent) :
					found_bottom = True
					rightest_bottom_item = rightest_bottom_candidate_item
					# Continue search from right-to-left from current item since price "peaked" if we got to this point
					rightest_peak_candidate_item = item
					#bprint(">>>>>>>> DEBUG identifyPeak >>>>>>>> SWITCHING TO search PEAK price ")
					
					#GVAR.STATISTICS_TICKER_cache_bottom_candidate_data = item
					#print "\n\n FOUND Bottom -> " + str(rightest_bottom_item)

		else :

			rightest_peak_candidate_price = float(rightest_peak_candidate_item[2])

			if(price >= rightest_peak_candidate_price) :
				
				#print "NEW MAX " + str(item)
				rightest_peak_candidate_item = item

			else :

				price_diff_percent = 100 - ((rightest_peak_candidate_price * 100) / price)
				price_diff_percent = round(price_diff_percent, 2)
				
				# Saving this data (biggest price decrease) for debug
				if(price_diff_percent < DELTA_min) : 
					DELTA_min = price_diff_percent
					DELTA_min_item = item

				if(price_diff_percent <= fallPercent) :

					# Price distance % from peak candidate falled enought to consider last candidate as a peak
					#bprint("\n\n\n FALL OCURRED AT " + str(item[1]) + " price : " + str(item[2]) + " --> LAST MAX: " + str(rightest_peak_candidate_item) + " \n\n")

					found_peak = True
					rightest_peak_item = rightest_peak_candidate_item

					#GVAR.STATISTICS_TICKER_cache_peak_candidate_data = item
					#print "\n\n FOUND Peak -> " + str(rightest_peak_item)

					break
	
	GVAR.STATISTICS_TICKER_cache_inflexion_delta_max = DELTA_max
	GVAR.STATISTICS_TICKER_cache_inflexion_delta_min = DELTA_min
	GVAR.STATISTICS_TICKER_cache_inflexion_delta_max_data = DELTA_max_item
	GVAR.STATISTICS_TICKER_cache_inflexion_delta_min_data = DELTA_min_item
	
	if( found_bottom and found_peak ) :
		
		peak_index = TICKER_cache_reversed.index(rightest_peak_item)
		bottom_index = TICKER_cache_reversed.index(rightest_bottom_item)

		#Check that Bottom is "newer" or "at right" of Peak
		if(bottom_index < peak_index) :			

			potential_peak_price = rightest_peak_item[2]

			if (GVAR.STATISTICS_TICKER_cache_rightest_peak == None) : 

				bprint("")
				bprint("")
				bprint("TICKER_CACHE_identifyRightestPeak: Setting FIRST peak price to NEW peak price: " + str(rightest_peak_item))
				current_GVAR_peak_price = 0

			else :
				
				current_GVAR_peak_price = GVAR.STATISTICS_TICKER_cache_rightest_peak[2]

			if (current_GVAR_peak_price != potential_peak_price) :

				bprint("")
				bprint("")
				bprint("TICKER_CACHE_identifyRightestPeak: NEW peak " + str(rightest_peak_item) + " FOUND")
				bprint("TICKER_CACHE_identifyRightestPeak: Setting LAST peak price = " + str(current_GVAR_peak_price) + " to NEW peak price: " + str(potential_peak_price) + " -> Do evaluation for potential new stop price")

				GVAR.STATISTICS_TICKER_cache_rightest_bottom = rightest_bottom_item
				GVAR.STATISTICS_TICKER_cache_rightest_peak = rightest_peak_item
			
				if (GVAR.STATISTICS_TICKER_cache_rightest_peak_found == False) :
					GVAR.STATISTICS_TICKER_cache_rightest_peak_found = True
					GVAR.STATISTICS_TICKER_cache_rightest_peak_tries = 0

				# When new peak is detected recalc new BUY_STOP price with AWT mode
				if (GVAR.BUY_mode_on == True and GVAR.SELL_CFB_mode_on == False) :

					AWT_min_percent = GVAR.BUY_AWT_enabled_min_percent
					if (GVAR.STATISTICS_TICKER_cache_amplitude_percent >= AWT_min_percent) :

						bprint("TICKER_CACHE_identifyRightestPeak: Minimun Wave Amplitude % for AWT mode detected -> Enabling AWT mode ")
						bprint("TICKER_CACHE_identifyRightestPeak: STATISTICS_TICKER_cache_amplitude_percent: " + str(GVAR.STATISTICS_TICKER_cache_amplitude_percent) + " >= GVAR.BUY_AWT_enabled_min_percent: " + str(GVAR.BUY_AWT_enabled_min_percent))
						GVAR.BUY_AWT_enabled = True
						last_peak_price = GVAR.STATISTICS_TICKER_cache_rightest_peak[2]
						BUY_AWT_evalCurrentStopPriceVsLastPeakPrice(last_peak_price)

					else :

						bprint("TICKER_CACHE_identifyRightestPeak: Potential new STOP price " + pcolors.RED + "REJECTED" + pcolors.ENDC)
						bprint("TICKER_CACHE_identifyRightestPeak: STATISTICS_TICKER_cache_amplitude_percent: " + str(GVAR.STATISTICS_TICKER_cache_amplitude_percent) + " % <= GVAR.BUY_AWT_enabled_min_percent: " + str(GVAR.BUY_AWT_enabled_min_percent) + " %")
						bprint("STATISTICS_TICKER_cache_amplitude_percent <= Minimun Wave Amplitude % for AWT mode -> GVAR.BUY_AWT_enabled = False ")
						bprint("")
						GVAR.BUY_AWT_enabled = False

				else :

						bprint("TICKER_CACHE_identifyRightestPeak: TRADE CFB_mode_on == " + pcolors.GREEN + str(GVAR.SELL_CFB_mode_on) + pcolors.ENDC + " -> Price evaluation " + pcolors.RED + "REJECTED" + pcolors.ENDC)
						bprint("")

	else :
		
		#bprint("TICKER_CACHE_identifyRightestPeak: Couldnt find Peak -> Search ended")
		GVAR.STATISTICS_TICKER_cache_rightest_peak_found = False
		GVAR.STATISTICS_TICKER_cache_rightest_peak_tries += 1

def TICKER_CACHE_getPeakCurrentIndex(PARAM_peak_time, PARAM_peak_price) :

	tmp_item = (str(PARAM_peak_time), float(PARAM_peak_price))
	index = GVAR.STATISTICS_TICKER_cache.index(tmp_item)
	return index

def BUY_AWT_evalCurrentStopPriceVsLastPeakPrice(PARAM_last_peak_price) :

	current_stop_price = GVAR.BUY_price_stop
	current_bid_price = GVAR.STATISTICS_TICKER_cache[-1][1]
	
	potential_new_prices = BUY_AWT_CalcBuyPrices(PARAM_last_peak_price)
	potential_new_stop_price = potential_new_prices['price_stop']
	potential_new_limit_price = potential_new_prices['price_limit']

	bprint("")
	bprint("BUY_AWT_evalCurrentStopPriceVsLastPeakPrice: Received last peak price: " + str(PARAM_last_peak_price) + " for evaluation..")
	bprint("BUY_AWT_evalCurrentStopPriceVsLastPeakPrice: GVAR.BUY_AWT_AWmP (Amplitude Wave Trading Above Wave margin percent) is : " + str(GVAR.BUY_AWT_AWmP) + " %")
	bprint("BUY_AWT_evalCurrentStopPriceVsLastPeakPrice: Calculated NEW potential STOP price: " + str(potential_new_stop_price) + " -> Comparing vs CURRENT STOP price: " + str(current_stop_price))
	bprint("")

	if (potential_new_stop_price < current_stop_price) :
		
		if (potential_new_stop_price > current_bid_price) :

			bprint("BUY_AWT_evalCurrentStopPriceVsLastPeakPrice: Current STOP price: " + str(current_stop_price) + " >= NEW STOP price: " + str(potential_new_stop_price) + " -> CHANGE STOP price")
			bprint("BUY_AWT_evalCurrentStopPriceVsLastPeakPrice: Calling BUY_AWT_changeBuyOrderPrice to set BUY order new STOP price .. ")
			bprint("")	
			BUY_AWT_changeBuyOrderPrice(GVAR.TRADE_orderId, potential_new_stop_price, potential_new_limit_price)
			
			if(GVAR.SIMULATOR_TICKER_debug_stops == True) :
				GVAR.TICKER_sleep = 1


		else :

			bprint("TICKER_CACHE_identifyRightestPeak : Current BID price > New potential price -> NOT USING new STOP price ")

	#elif (potential_new_stop_price == current_stop_price) :

		# Do nothing
		#bprint("BUY_AWT_evalCurrentStopPriceVsLastPeakPrice: STOP price stauts is " + pcolors.GREEN + "OK" + pcolors.ENDC + ", should not change from current price ")	
		
	elif (potential_new_stop_price > current_stop_price) :

		bprint("BUY_AWT_evalCurrentStopPriceVsLastPeakPrice: Potential new STOP price >=  Current STOP price -> " + pcolors.GREEN + "(WAVES are going UP)" + pcolors.ENDC)
		bprint("BUY_AWT_evalCurrentStopPriceVsLastPeakPrice: NEW price DISCARTED -> Leaving CURRENT STOP price: " + str(current_stop_price) )
		bprint("")

		#if(GVAR.SIMULATOR_TICKER_debug_stops == True) :
			#GVAR.TICKER_sleep = 1

def TICKER_CACHE_printStatistics() :

	TICKER_cache = GVAR.STATISTICS_TICKER_cache
	
	tickerMaxLen = GVAR.STATISTICS_TICKER_cache_size
	tickerSizeInMinutes = tickerMaxLen / 60

	maxIndex = GVAR.STATISTICS_TICKER_cache_max_index
	minIndex = GVAR.STATISTICS_TICKER_cache_min_index
	amplitude = GVAR.STATISTICS_TICKER_cache_amplitude_price
	amplitudePercent = GVAR.STATISTICS_TICKER_cache_amplitude_percent

	priceDirection = MARKET_CACHE_getPriceDirection()
	directionStr = priceDirection[0]
	dirPercentStr = str(priceDirection[1])

	if(directionStr == "UP") :
		mcolor = pcolors.GREEN
	elif(directionStr == "UNCH") :
		mcolor = pcolors.YELLOW
	elif(directionStr == "DOWN") :
		mcolor = pcolors.RED

	bprint("")
	bprint("==========================================================================================")
	bprint("TICKER_CACHE_printStatistics: Priting statistics so far ..")
	bprint("")
	bprint("GVAR.STATISTICS_TICKER_cache -> MAX_LENGTH: " + str(GVAR.STATISTICS_TICKER_cache_size) + " -> Time approx : " + str(tickerSizeInMinutes) + " minutes")
	bprint("GVAR.STATISTICS_TICKER_cache -> SIZE: " + str(len(TICKER_cache)))
	bprint("")
	bprint("GVAR.STATISTICS_TICKER_cache -> MAX (index " + str(maxIndex) + "): " + str(GVAR.STATISTICS_TICKER_cache_max))
	bprint("GVAR.STATISTICS_TICKER_cache -> MIN (index " + str(minIndex) + "): " + str(GVAR.STATISTICS_TICKER_cache_min))
	bprint("GVAR.STATISTICS_TICKER_cache -> AMPLITUDE :  " + str(amplitude) + " ( " + str(amplitudePercent) + " %)")
	bprint("PRICE DIRECTION : " + mcolor + directionStr + pcolors.ENDC + " " + dirPercentStr + " %")
	bprint("")
	bprint("RECENT REFERENT PEAK FOUND: " + str(GVAR.STATISTICS_TICKER_cache_rightest_peak_found))
	bprint("SEARCH REFERENT PEAK TRIES: " + str(GVAR.STATISTICS_TICKER_cache_rightest_peak_tries))
	bprint("SEARCH PEAK INFLEXION PERCENT: " + str(GVAR.STATISTICS_TICKER_cache_peak_inflexion_percent) +  " %")
	bprint("")
	bprint("Max INCREASE from BOTTOM so far: " + str(GVAR.STATISTICS_TICKER_cache_inflexion_delta_max) + " % -> " + str(GVAR.STATISTICS_TICKER_cache_inflexion_delta_max_data))
	#bprint("Candidate for BOTTOM : " + str(GVAR.STATISTICS_TICKER_cache_bottom_candidate_data))
	bprint("Max DECREASE from PEAK so far: " + str(GVAR.STATISTICS_TICKER_cache_inflexion_delta_min) + " % -> " + str(GVAR.STATISTICS_TICKER_cache_inflexion_delta_min_data))
	#bprint("Candidate for PEAK : " + str(GVAR.STATISTICS_TICKER_cache_peak_candidate_data))
	bprint("")
	bprint("RIGHTEST " + pcolors.GREEN + "PEAK" + pcolors.ENDC + ": " + str(GVAR.STATISTICS_TICKER_cache_rightest_peak) )
	bprint("RIGHTEST " + pcolors.RED + "BOTTOM" + pcolors.ENDC + ": " + str(GVAR.STATISTICS_TICKER_cache_rightest_bottom) )
	#bprint("")
	#bprint(str(TICKER_cache))
	bprint("")
	bprint("TICKER_CACHE_printStatistics: End of statistics")
	bprint("==========================================================================================")
	bprint("")

def SELL_CFB_CalcLogarithmicMarginPercent (PARAM_earning_percent) : 

	# BASE 10 log(x) in python = math.log(x, 10)
	# log(x) ussually means log_base_10(x)
	# So far best log function I found: 
	# 
	#	margin_allowed = -log_base_10(earning_percent + 5.1) + (1.02)
	#
	# Starts with aprox 1.1% at 0% earnings -> 0.7% at 1% earnings -> 0.3% at 5% earnings
	# Plot graph for best understanding www.fooplot.com

	x = float(PARAM_earning_percent)

	"""bprint("")
	bprint(">>>>> DEBUG LOGARITM -> x : " + str(x))
	bprint(">>>>> DEBUG LOGARITM -> SELL_CFB_lnMP_max_limit : " + str(GVAR.SELL_CFB_lnMP_max_limit))
	bprint("")
	bprint("")"""
	
	# CHECK for negatives earnings on first call
	# Send negative values to cero, if negative in first call can return CFBmP = 0 and produce price ERRORs
	if (x < 0.0) : x = 0.0

	if (x >= float(GVAR.SELL_CFB_lnMP_max_limit)) :
	
		#y = -math.log( x + 5.1 , 10) + (1.02)
		
		#################
		# %    # CFBmP  #
		#################
		# 0    # 0.65   #
		# 0.65 # 0.45   #
		# 1	   # 0.30   #
		# 1.5  # 0.15   #
		# 2    # 0.1    #
		# 5    # 0.1    #
		#################

		limits = GVAR.SELL_CFB_lnMP_limits
		values = GVAR.SELL_CFB_lnMP_values
		
		"""
		if 		(x < 0.5) 	: y = 0.65
		elif 	(x < 0.65) 	: y = 0.45
		elif 	(x < 1) 	: y = 0.3
		elif 	(x < 1.5) 	: y = 0.25
		elif 	(x < 2) 	: y = 0.20
		elif 	(x < 5) 	: y = 0.15
		else 				: y = 0.15
		"""

		i = 0
		new_max_limit = 0
		for lim in limits :

			if (x < lim) :
				y = values[i]
				new_max_limit = lim
				break

			# if % is bigger than limits -> use last value
			i += 1
			if (i == len(limits)) :
				y = values[i-1]
				new_max_limit = limits[-1]
				break

		limStr = str(new_max_limit)
		SELL_CFB_label_set("LN",limStr)

		margin_percent = round(y,2)
		GVAR.SELL_CFB_lnMP_max_value = margin_percent
		GVAR.SELL_CFB_lnMP_max_limit = new_max_limit

		#bprint(" SELL_CFB_CalcLogarithmicMarginPercent: PARAM_earning_percent = " + str(x) + " CFBmP = " + str(y))
		#bprint("")

		if (margin_percent == 0) :
			bprint (pcolors.VIOLET + " >>>>>>>>> WARNING!!!!! DEBUG LOGARITMIC RETURN 1 CFBmP = 0 !!!!!!!!!!!!!!!!!!!!!!!!!!! " + pcolors.ENDC )

		return float(margin_percent)
	
	else :

		if (GVAR.SELL_CFB_lnMP_max_value == 0) :
			bprint (pcolors.VIOLET + " >>>>>>>>> WARNING!!!!! DEBUG LOGARITMIC RETURN 2 CFBmP = 0 !!!!!!!!!!!!!!!!!!!!!!!!!!! " + pcolors.ENDC )

		return float(GVAR.SELL_CFB_lnMP_max_value)

def getch():
    import termios
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    return _getch()

# ========================================================
# Listen to keystrokes on a new Thread to choose options

def MOVER_start () :
	
	if(GVAR.MOVER_running == False) :
		if(GVAR.MODE_VERBOSE_enabled == True) :
			inputKey = []
			thread.start_new_thread(MOVER_input_thread, (inputKey,))
			GVAR.MOVER_running = True

def MOVER_input_thread(inputKey) :

	targetStr = "CFAmP / CFBmP"

	bprint("")
	bprint("########## INPUT KEYS ##########")
	bprint("MOVER_input_thread: Keys enabled: ")
	bprint("[ + : INCREASE " + targetStr + " ] [ - : DECREASE " + targetStr + " ]")
	bprint("[ ^ : INCREASE BUY FILL PRICE ] [ _ : DECREASE BUY FILL PRICE ] (ONLY IN SELL MODE AFTER ORDER IF FILLED)")
	bprint("[ G : GET CLOSER TO PRICE  " + targetStr + " ] [ D : DEPART   " + targetStr + " ]")
	bprint("[ M : MANUAL " + targetStr + " mode ON / OFF ] ")
	bprint("[ O : PRINT OPEN ORDERS ] [ P : PRINT CACHE STATISTICS ] [ I : PRINT DEBUG VARS ]  ")
	bprint("[ S : SLOWER SIMULATION ] [ F : FASTER SIMULATION ]  ")
	bprint("[ = : PAUSE / PLAY ] [ V : VISUAL TRADE RENDER ]  ")
	bprint("[ % : EXIT BOT ] ")
	bprint("################################")
	bprint("")

	loop = True
	while loop :

		if(GVAR.FLAG_main_thread_exit == True ) :
			bprint("MOVER_input_thread: EXIT MOVER thread")
			bprint("")
			thread.exit()
			quit()

		inputKey.append(getch())
		
		key = inputKey[-1]

		orderId = GVAR.TRADE_orderId
		sideStr = GVAR.MOVER_side
		symbol = GVAR.symbol
		delta = 0

		if(sideStr == "BUY") :
			targetStr = "CFAmP"
		elif(sideStr == "SELL") :
			targetStr = "CFBmP"

		if GVAR.MOVER_enabled == False :

			bprint("")
			bprint("MOVER_input_thread: MOVER NOT enabled (GVAR.MOVER_enabled = False)")
			bprint("")

		else :

			#bprint("MOVER_input_thread: Keys history (last 10): " + str(inputKey[-10:]))

			if key == '+' :

				if(sideStr == "BUY") :

					delta = GVAR.MOVER_BUY_delta

					old_price_stop = GVAR.BUY_price_stop
					new_price_stop = GVAR.BUY_price_stop + delta
					new_price_limit = CFA_BUY_CalcNewPrice(GVAR.BUY_CFA_margin_percent, GVAR.BUY_CFA_MV_margin_percent, new_price_stop)

					bprint("")
					bprint("MOVER_input_thread: MOVING (" + pcolors.YELLOW + "+ " + str(delta) + pcolors.ENDC + ") STOP PRICE from " + pcolors.TUR + str(old_price_stop) + pcolors.ENDC + " -> " + pcolors.TUR + str(new_price_stop) + pcolors.ENDC + "")
					bprint("")

					MOVER_BUY_stop_limit(orderId, symbol, new_price_stop, new_price_limit)
				
				elif(sideStr == "SELL") :

					GVAR.FLAG_CFB_manual_mode = True
					SELL_CFB_label_set("MANUAL","")
					delta = GVAR.MOVER_SELL_delta
					GVAR.SELL_CFB_margin_percent += delta

					if(GVAR.SELL_CFB_mode_on == True) :

						price_ticker = BINANCE_TICKER_GetTickerData(symbol)
						price_bid = str(price_ticker['bidPrice'])
						new_prices = SELL_CFB_CalcNewStopPrice(GVAR.SELL_CFB_margin_percent, GVAR.SELL_price_margin, GVAR.SELL_CFB_MV_margin_percent, price_bid)
						price_stop = new_prices['price_stop']
						price_limit = new_prices['price_limit']

						MOVER_SELL_stop_limit(orderId, symbol, price_stop, price_limit)

				bprint("MOVER_input_thread: " + pcolors.YELLOW + "INCREASED " + pcolors.ENDC + pcolors.GREEN + targetStr + pcolors.ENDC + " " + pcolors.TUR + str(delta) + pcolors.ENDC + " %")

			elif key == '-' :

				if(sideStr == "BUY") :

					delta = GVAR.MOVER_BUY_delta

					old_price_stop = GVAR.BUY_price_stop
					new_price_stop = GVAR.BUY_price_stop - delta
					new_price_limit = CFA_BUY_CalcNewPrice(GVAR.BUY_CFA_margin_percent, GVAR.BUY_CFA_MV_margin_percent, new_price_stop)

					bprint("")
					bprint("MOVER_input_thread: MOVING (" + pcolors.YELLOW + "- " + str(delta) + pcolors.ENDC + ") STOP PRICE from " + pcolors.TUR + str(old_price_stop) + pcolors.ENDC + " -> " + pcolors.TUR + str(new_price_stop) + pcolors.ENDC + "")
					bprint("")

					if(GVAR.IDLE_mode_on == False) :
						MOVER_BUY_stop_limit(orderId, symbol, new_price_stop, new_price_limit)
					else :
						GVAR.BUY_price_stop = new_price_stop
						GVAR.BUY_price_limit = new_price_limit

				elif(sideStr == "SELL") :
					GVAR.FLAG_CFB_manual_mode = True
					SELL_CFB_label_set("MANUAL","")
					delta = GVAR.MOVER_SELL_delta
					GVAR.SELL_CFB_margin_percent -= delta
					#if(GVAR.SELL_CFB_mode_on == True) :
					#	MOVER_SELL_stop_limit(orderId, symbol)

				bprint("MOVER_input_thread: " + pcolors.YELLOW + "DECREASED " + pcolors.ENDC + pcolors.GREEN + targetStr + pcolors.ENDC + " " + pcolors.TUR + str(delta) + pcolors.ENDC + " %")

			elif key == '_' :

				if(sideStr == "SELL") :

					oldPrice = GVAR.TRADE_price_fill
					delta = (GVAR.BUY_price_margin / 5)
					GVAR.TRADE_price_fill = GVAR.TRADE_price_fill - delta
					bprint("")
					bprint("MOVER_input_thread: CORRECTING (" + pcolors.YELLOW + "- " + str(delta) + pcolors.ENDC + ") TRADE FILL PRICE from " + pcolors.TUR + str(oldPrice) + pcolors.ENDC + " -> " + pcolors.TUR + str(GVAR.TRADE_price_fill) + pcolors.ENDC + "")
					bprint("")

			elif key == '^' :

				if(sideStr == "SELL") :

					oldPrice = GVAR.TRADE_price_fill
					delta = (GVAR.BUY_price_margin / 5)
					GVAR.TRADE_price_fill = GVAR.TRADE_price_fill + delta
					bprint("")
					bprint("MOVER_input_thread: CORRECTING (" + pcolors.YELLOW + "+ " + str(delta) + pcolors.ENDC + ") TRADE FILL PRICE from " + pcolors.TUR + str(oldPrice) + pcolors.ENDC + " -> " + pcolors.TUR + str(GVAR.TRADE_price_fill) + pcolors.ENDC + "")
					bprint("")

			elif key == '%' :

				bprint("MOVER_input_thread: '%' key pressed -> FINISH TRADE")
				bprint("")

				GVAR.TRADE_abort = True
				GVAR.MODE_LOOP = False
				GVAR.IDLE_mode_on = False
				GVAR.TRADER_enabled = False
				
				#Exit main thread
				#thread.interrupt_main()

				#Exit input thread
				quit()

			elif key == 'X' :

				bprint("MOVER_input_thread: 'X' key pressed -> EXIT BOT WITHOUT REMOVING OPEN ORDER")
				bprint("")				
				#Exit main thread
				thread.interrupt_main()
				#Exit input thread
				quit()

			elif key == 'M' :

				if (GVAR.BUY_mode_on == True) :

					GVAR.FLAG_CFA_manual_mode = not(GVAR.FLAG_CFA_manual_mode)
					#if(GVAR.FLAG_CFA_manual_mode == True) :
					#	SELL_CFB_label_set("MANUAL","")
					#else :
					#	SELL_CFB_label_set("???","")

					bprint("MOVER_input_thread: 'M' key pressed -> GVAR.FLAG_CFB_manual_mode: " + pcolors.YELLOW + str(GVAR.FLAG_CFB_manual_mode) + pcolors.ENDC)
					bprint("")

				if (GVAR.SELL_mode_on == True) :

					GVAR.FLAG_CFB_manual_mode = not(GVAR.FLAG_CFB_manual_mode)
					if(GVAR.FLAG_CFB_manual_mode == True) :
						SELL_CFB_label_set("MANUAL","")
					else :
						SELL_CFB_label_set("???","")

					bprint("MOVER_input_thread: 'M' key pressed -> GVAR.FLAG_CFB_manual_mode: " + pcolors.YELLOW + str(GVAR.FLAG_CFB_manual_mode) + pcolors.ENDC)
					bprint("")

			elif key == 'G' :

				bprint("MOVER_input_thread: " + pcolors.YELLOW + "APROACH using GVAR.MOVER_aproacher_fixed : " + pcolors.TUR + str(GVAR.MOVER_aproacher_fixed) + pcolors.ENDC + " margin from ticker BID price")
				#bprint("MOVER_input_thread: " + pcolors.YELLOW + "APROACH " + pcolors.ENDC + pcolors.GREEN + targetStr + pcolors.ENDC + " " + pcolors.TUR + str(GVAR.MOVER_aproacher_percent) + pcolors.ENDC + " %")

				if(sideStr == "BUY") :
					GVAR.FLAG_CFB_manual_mode = True

					price_ticker = BINANCE_TICKER_GetTickerData(symbol)
					price_bid = float(price_ticker['bidPrice'])
					price_stop = price_bid + GVAR.MOVER_aproacher_fixed
					price_limit = price_stop + GVAR.BUY_price_margin

					MOVER_BUY_stop_limit(orderId, symbol, price_stop, price_limit)

				elif(sideStr == "SELL") :
					GVAR.FLAG_CFB_manual_mode = True
					SELL_CFB_label_set("MANUAL","")

					price_ticker = BINANCE_TICKER_GetTickerData(symbol)
					price_bid = float(price_ticker['bidPrice'])
					price_stop = price_bid - GVAR.MOVER_aproacher_fixed
					price_limit = price_stop - GVAR.BUY_price_margin

					# NO NEED TO CANCEL CURRENT ORDER -> LOOPER WILL DETECT CURRENT PRICE TOO FAR AND RE CREATE new orders
					# EXCEPT WHEN CFB mode is still waiting to start
					#if(GVAR.SELL_CFB_mode_on == True) :

					MOVER_SELL_stop_limit(orderId, symbol, price_stop, price_limit)

			elif key == 'D' :

				# INSTANT DEPART -> SET CFAmP = CFAmP_default or CFBmp = CFBmP_default
				
				bprint("MOVER_input_thread: " + pcolors.YELLOW + "DEPART " + pcolors.ENDC + pcolors.GREEN + sideStr + pcolors.ENDC + " " + targetStr + " " + pcolors.TUR + str(GVAR.BUY_CFA_margin_percent_default) + pcolors.ENDC + " %")
				if(sideStr == "BUY") :
				
					GVAR.FLAG_CFA_manual_mode = True
					GVAR.BUY_CFA_MV_margin_percent = GVAR.BUY_CFA_MV_margin_percent_default
					GVAR.BUY_CFA_margin_percent = GVAR.BUY_CFA_margin_percent_default

					price_ticker = BINANCE_TICKER_GetTickerData(symbol)
					price_bid = float(price_ticker['bidPrice'])
					price_stop = CFA_BUY_CalcNewPrice(GVAR.BUY_CFA_margin_percent, GVAR.BUY_CFA_MV_margin_percent, price_bid)
					price_limit = price_stop + GVAR.BUY_price_margin
					MOVER_BUY_stop_limit(orderId, symbol, price_stop, price_limit)
				
				elif(sideStr == "SELL") :
				
					GVAR.FLAG_CFB_manual_mode = True
					SELL_CFB_label_set("MANUAL","")
					GVAR.SELL_CFB_MV_margin_percent = GVAR.SELL_CFB_MV_margin_percent_default
					GVAR.SELL_CFB_margin_percent = GVAR.MODE_VARS.SELL_CFB_margin_percent_default

					TICKER_data = EXCHANGE_TICKER_GetTickerData (GVAR.symbol)
					GVAR.TRADE_TICKER_price_bid = TICKER_data["bidPrice"]
					new_prices = SELL_CFB_CalcNewStopPrice(GVAR.SELL_CFB_margin_percent, GVAR.SELL_price_margin, GVAR.SELL_CFB_MV_margin_percent, GVAR.TRADE_TICKER_price_bid)
					price_stop = round(float(new_prices["price_stop"]),GVAR.TRADE_round_prices)
					price_limit = round(float(new_prices["price_limit"]),GVAR.TRADE_round_prices)
					if(GVAR.SELL_CFB_mode_on == True) :
						MOVER_SELL_stop_limit(orderId, symbol, price_stop, price_limit)
						
			elif key == 'O' :

				EXCHANGE_ORDER_Print_OpenOrders_Symbol(symbol,sideStr, False)

			elif key == 'P' :

				TICKER_CACHE_printStatistics()

			elif key == 'I' :

				DEBUG_TRADE_printVars("MOVER_input_thread")

			elif key == 'S' :

				if(GVAR.TICKER_sleep < 2) :
					GVAR.TICKER_sleep = 2
				else :
					if(GVAR.TICKER_sleep < 5) :
						ticker_sleep = GVAR.TICKER_sleep
						ticker_sleep_new = float(ticker_sleep) * 2
						#if (ticker_sleep_new < 1) :
						bprint("")
						bprint("")
						bprint("GVAR.TICKER_sleep: " + str(ticker_sleep) + " -> " + str(ticker_sleep_new) )
						GVAR.TICKER_sleep = ticker_sleep_new

			elif key == 'F' :

				ticker_sleep = GVAR.TICKER_sleep
				ticker_sleep_new = float(ticker_sleep) / 4
				bprint("")
				bprint("")
				bprint("GVAR.TICKER_sleep: " + str(ticker_sleep) + " -> " + str(ticker_sleep_new) )
				GVAR.TICKER_sleep = ticker_sleep_new

			elif key == 'V' :

				bprint("")
				bprint("")
				bprint("GVAR.MOVER_input_thread: Rendering visual data of trade ..")
				bprint("")
				GRAPH_TRADE_plot(GVAR.TICKER_sleep)
				
			elif key == '=' :

				TRADE_pause()

			else : 

				bprint("MOVER_input_thread: '" + str(key) + "' key pressed -> NOT MAPPED -> DO NOTHING")

			bprint("")

def TRADE_pause() :

	if GVAR.TICKER_paused == True :
		GVAR.TICKER_paused = False
		sleep(1)
		bprint("")
		bprint("")
		bprint("TRADE_pause : Exiting pause ..")
	else :
		bprint("")
		bprint("")
		bprint("TRADE_pause : Going to a pause ..")
		GVAR.TICKER_paused = True

def SELL_CFB_label_set(PARAM_label, PARAM_extraStr) :

	PARAM_extraStr = str(PARAM_extraStr)

	if(PARAM_label == "MANUAL") :
		
		GVAR.SELL_CFB_label = "CFBmp " + pcolors.BLINK + pcolors.RED + PARAM_label + pcolors.ENDC
	
	elif (PARAM_label == "LN") :

		lnStr = pcolors.GREEN + " ln<" + GVAR.MODE_VARS.MODE_name + "> lim( " + pcolors.TUR + PARAM_extraStr + pcolors.ENDC + pcolors.GREEN + " % )" + pcolors.ENDC
		GVAR.SELL_CFB_label = "CFBmp " + pcolors.GREEN + lnStr + pcolors.ENDC

	elif (PARAM_label == "PreCFB") :

		GVAR.SELL_CFB_label = "CFBmp " + pcolors.YELLOW + PARAM_label + pcolors.ENDC

	else :

		GVAR.SELL_CFB_label = "CFBmp " + pcolors.BLINK + pcolors.RED + PARAM_label + pcolors.ENDC

def MOVER_SELL_stop_limit(PARAM_orderId, PARAM_symbol, PARAM_price_stop, PARAM_price_limit) :

	orderId = str(PARAM_orderId)
	symbol = PARAM_symbol
	
	buy_symbol = GVAR.BUY_symbol
	sell_symbol = GVAR.SELL_symbol
	price_ticker = BINANCE_TICKER_GetTickerData(symbol)
	price_bid = str(price_ticker['bidPrice'])
	
	price_stop = PARAM_price_stop
	price_limit = PARAM_price_limit
	
	side = BINANCE.SIDE_SELL
	amount = GVAR.SELL_amount

	new_price_stop = round(float(price_stop),5)
	new_price_limit = round(float(price_limit),5)

	resp = ""
	bprint("MOVER_SELL_stop_limit: Canceling orderId : " + orderId)
	resp = EXCHANGE_ORDER_Cancel(symbol, orderId)
	bprint("MOVER_SELL_stop_limit: Order canceled -> resp[:30]: " + str(resp)[:30] + "..")
	bprint("MOVER_SELL_stop_limit: Creating new " + pcolors.GREEN + "SELL" + pcolors.ENDC + " order STOP: " + pcolors.TUR + str(new_price_stop) + pcolors.ENDC + " LIMIT: " + pcolors.TUR + str(new_price_limit) + " " + pcolors.GREEN + sell_symbol + pcolors.ENDC)
	bprint("")
	resp = EXCHANGE_ORDER_Create_StopLimit(symbol, side, new_price_stop, new_price_limit, amount)
	bprint("MOVER_SELL_stop_limit: Order canceled -> resp[:30]: " + str(resp)[:30])
	
	new_orderId = resp['orderId']

	if(int(new_orderId) > 0) :

		GVAR.TRADE_orderId = new_orderId
		bprint("MOVER_SELL_stop_limit: Order created OK new orderId: " + pcolors.VIOLET + str(new_orderId) + pcolors.ENDC)

		GVAR.SELL_price_stop = new_price_stop
		GVAR.SELL_price_limit = new_price_limit

	else : 

		bprint("MOVER_SELL_stop_limit: " + pcolors.RED + "ERROR" + pcolors.ENDC + " creating new order -> resp: " + str(resp))
		GVAR.TRADE_orderId = 0

def MOVER_BUY_stop_limit(PARAM_orderId, PARAM_symbol, PARAM_price_stop, PARAM_price_limit) :

	orderId = str(PARAM_orderId)
	symbol = PARAM_symbol
	
	buy_symbol = GVAR.BUY_symbol
	sell_symbol = GVAR.SELL_symbol

	price_stop = PARAM_price_stop
	price_limit = PARAM_price_limit
	
	side = BINANCE.SIDE_BUY
	amount = GVAR.BUY_amount

	new_price_stop = round(float(price_stop),5)
	new_price_limit = round(float(price_limit),5)

	resp = ""
	bprint("[BOT II] MOVER_BUY_stop_limit: Canceling orderId : " + orderId)
	resp = EXCHANGE_ORDER_Cancel(symbol, orderId)
	bprint("[BOT II] MOVER_BUY_stop_limit: Order canceled -> resp[:30]: " + str(resp)[:30] + "..")
	bprint("[BOT II] MOVER_BUY_stop_limit: Creating new " + pcolors.GREEN + "BUY" + pcolors.ENDC + " order STOP: " + pcolors.TUR + str(new_price_stop) + pcolors.ENDC + " LIMIT: " + pcolors.TUR + str(new_price_limit) + " " + pcolors.GREEN + sell_symbol + pcolors.ENDC)
	bprint("")
	resp = EXCHANGE_ORDER_Create_StopLimit(symbol, side, new_price_stop, new_price_limit, amount)
	bprint("[BOT II] MOVER_BUY_stop_limit: Order canceled -> resp[:30]: " + str(resp)[:30])
	
	new_orderId = resp['orderId']

	if(int(new_orderId) > 0) :

		GVAR.TRADE_orderId = new_orderId
		bprint("MOVER_BUY_stop_limit: Order created OK new orderId: " + pcolors.VIOLET + str(new_orderId) + pcolors.ENDC)

		GVAR.BUY_price_stop = new_price_stop
		GVAR.BUY_price_limit = new_price_limit
		
	else : 

		bprint("[BOT II] MOVER_BUY_stop_limit: " + pcolors.RED + "ERROR" + pcolors.ENDC + " creating new order -> resp: " + str(resp))
		GVAR.TRADE_orderId = 0

def MICRO_sleep(time):

	# 1 seconds = 10 microseconds (1 ms = 0.1)
	"""if (time >= 1) :

		time_steps = time * 10
		for i in range(1,time_steps,1) :
			sleep(0.1)
	
	else :"""

	if (GVAR.TICKER_paused == False) :
		sleep(time)
	else :
		while(True) :
			sleep(1)
			if (GVAR.TICKER_paused == False) :
				break

def bprint(PARAM_string) :

	if(GVAR.MODE_VERBOSE_enabled == True) :

		if (GVAR.SCREEN_WIN_log_enabled == False) :

			sys.stdout.write("\r")

			preStr = ""
			if(PARAM_string == "") :
				preStr = ""
			else:
				preStr = "[BOTP] "

			sys.stdout.write(preStr + PARAM_string + "\n")
			sys.stdout.flush()

		else :

			SCREEN_WIN_log_printLine(PARAM_string)

def devprint(PARAM_boolVar, PARAM_printStr) :

	if (PARAM_boolVar == True) :

		SCREEN_WIN_log_printLine(PARAM_printStr)

def logprint(PARAM_fileName, PARAM_printStr) :

	defName = "logprint: "
	
	logPath = "./" + GVAR.TRADER_logsDir + "/"
	logFileName = PARAM_fileName + ".log"
	logFile = logPath + logFileName

	logStr = str(PARAM_printStr)
	bprint(defName + logStr)

	SYS_IO_writeFile(logFile, logStr)

def printTradesLoopStatistics() :

	GVAR.MODE_VERBOSE_enabled = True

	bprint("")
	bprint("")
	bprint("#################### " + pcolors.YELLOW + "TRADES STATISTICS" + pcolors.ENDC + " ####################")
	bprint("")
	bprint(" >>>>> TRADE MODE: " + GVAR.MODE_VARS.MODE_name)
	bprint("")
	bprint(" >>>>> DATA FILE: " + GVAR.SIMULATOR_TICKER_dataDir + GVAR.SIMULATOR_TICKER_dataFile )
	bprint("")
	bprint(" >>>>> TRADE CFAmP: " + str(GVAR.MODE_VARS.BUY_CFA_margin_percent_default))
	bprint(" >>>>> TRADE CFBmP: " + str(GVAR.MODE_VARS.SELL_CFB_margin_percent_default))
	bprint(" >>>>> TRADE lnCFBmP limits: " + str(GVAR.MODE_VARS.SELL_CFB_lnMP_limits))
	bprint(" >>>>> TRADE lnCFBmP values: " + str(GVAR.MODE_VARS.SELL_CFB_lnMP_values))
	bprint("")
	bprint(" >>>>> TOTAL EARNING : " + str(GVAR.STATISTICS_trades_results_total_earnings) )
	bprint(" >>>>> TOTAL EARNING % : " + str(GVAR.STATISTICS_trades_results_total_earnings_percent) )
	bprint("")
	#bprint(" >>>>> TRADES EARNINGS       : " + GVAR.SELL_symbol + " " + str(GVAR.STATISTICS_trades_results_earnings) )
	#bprint(" >>>>> TRADES EARNINGS %     : " + str(GVAR.STATISTICS_trades_results_earnings_percents) )
	#bprint(" >>>>> BALANCES (EARN - FEE) : " + GVAR.SELL_symbol + " " + str(GVAR.STATISTICS_trades_results_balances) )
	#bprint("")
	#bprint(" >>>>> PRICES BUYS  : " + str(GVAR.STATISTICS_trades_tradeBuyPrices) )
	#bprint(" >>>>> PRICES SELLS : " + str(GVAR.STATISTICS_trades_tradeStopPrices) )
	#bprint("")
	bprint(" >>>>> TOTAL TRADES : " + str(GVAR.STATISTICS_trades_counter) )
	bprint(" >>>>> TOTAL " + pcolors.YELLOW + "BALANCES" + pcolors.ENDC + " : " + str(GVAR.STATISTICS_trades_results_total_balances) + " " + GVAR.SELL_symbol )
	bprint(" >>>>> TOTAL " + pcolors.GREEN + "WINS" + pcolors.ENDC + " : " + str(GVAR.STATISTICS_trades_results_total_wins) )
	bprint(" >>>>> TOTAL " + pcolors.RED + "LOOSES" + pcolors.ENDC + " : " + str(GVAR.STATISTICS_trades_results_total_looses) )	
	bprint("")
	
	wins_vs_looses = GVAR.STATISTICS_trades_results_total_wins - GVAR.STATISTICS_trades_results_total_looses

	fstr1 = "" + GVAR.MODE_VARS.MODE_name.ljust(5) + " " + GVAR.SIMULATOR_TICKER_dataFile.ljust(14) + " | CFA " + str(GVAR.MODE_VARS.BUY_CFA_margin_percent_default) + " | CFB " + str(GVAR.MODE_VARS.SELL_CFB_margin_percent_default) + " | "
	
	CFBlStr = "CFBl {" + str(GVAR.MODE_VARS.SELL_CFB_lnMP_limits)[-20:] +  ""
	CFBvStr = "CFBv {" + str(GVAR.MODE_VARS.SELL_CFB_lnMP_values)[-20:] +  ""
	CFBStr = CFBlStr + " " + CFBvStr + " "

	fstr2 = "BAL " + str(GVAR.STATISTICS_trades_results_total_balances).ljust(6) + " " + GVAR.SELL_symbol + " | TRADES " + str(GVAR.STATISTICS_trades_counter).ljust(3) + " | "
	fstr3 = "W-L " + str(wins_vs_looses).ljust(2) + " | W " + str(GVAR.STATISTICS_trades_results_total_wins).ljust(2) + " = " + GVAR.SELL_symbol + " " + str(GVAR.STATISTICS_trades_results_total_wins_sum).ljust(5) + " | "
	fstr4 = "L " + str(GVAR.STATISTICS_trades_results_total_looses ).ljust(2) + " = " + GVAR.SELL_symbol + " " + str(GVAR.STATISTICS_trades_results_total_looses_sum).ljust(7) + ""
	fstr5 = "F " + str(GVAR.STATISTICS_trades_results_total_fees_sum).ljust(5) + " " + GVAR.SELL_symbol
	file_output_str = fstr1 + CFBStr + fstr2 + fstr3 + fstr4 + fstr5
	write_file("STATS.dat", file_output_str)

def SYS_IO_writeFile (PARAM_file, PARAM_data) :

	file_name = str(PARAM_file)
	data = str(PARAM_data)

	with open(file_name, 'a') as f :
		
		f.write(data + "\n")

def write_session_data (PARAM_session_name) :

	session_name = PARAM_session_name
	session_ext = "json"
	session_file_name = session_name + "." + session_ext

	TRADE_data = GVAR.TRADE_data
	BUY_data = GVAR.BUY_data
	SELL_data = GVAR.SELL_data
	data = [ TRADE_data, BUY_data, SELL_data]

	with open("./SESSIONS/" + session_file_name, 'w') as f :
		json.dump(data, f, indent=4, sort_keys=True)


def DEBUG_TRADE_printVars(PARAM_calledFrom) :
	bprint(pcolors.VIOLET + ">>>>>>>> DEBUG_TRADE_printVars() >>>>>>>>>>> CALLED FROM: " + pcolors.ENDC + pcolors.YELLOW + str(PARAM_calledFrom) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.BOT_ID : " + str(GVAR.BOT_ID) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.BOT_version : " + str(GVAR.BOT_version) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.TICKER_sleep : " + str(GVAR.TICKER_sleep) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.symbol : " + str(GVAR.symbol) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.MODE : " + str(GVAR.MODE) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.MODE_VARS.MODE_name : " + str(GVAR.MODE_VARS.MODE_name) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.BUY_mode_on : " + str(GVAR.BUY_mode_on) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.SELL_CFB_mode_on : " + str(GVAR.SELL_CFB_mode_on) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.TRADE_TICKER_price_bid : " + str(GVAR.TRADE_TICKER_price_bid) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.BUY_price_stop : " + str(GVAR.BUY_price_stop) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.SELL_price_stop : " + str(GVAR.SELL_price_stop) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.FLAG_CFA_manual_mode : " + str(GVAR.FLAG_CFA_manual_mode) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.FLAG_CFB_manual_mode : " + str(GVAR.FLAG_CFB_manual_mode) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.FLAG_ERRORS_retry : " + str(GVAR.FLAG_ERRORS_retry) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.FLAG_SOUND_mode_on : " + str(GVAR.FLAG_SOUND_mode_on) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.FLAG_GRAPH_mode_on : " + str(GVAR.FLAG_GRAPH_mode_on) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " CFAmP (GVAR.MODE_VARS.BUY_CFA_margin_percent) : " + str(GVAR.BUY_CFA_margin_percent)  + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.MODE_VARS.BUY_CFA_margin_percent_default : " + str(GVAR.BUY_CFA_margin_percent_default)  + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.TRADE_price_end : " + str(GVAR.TRADE_price_end) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.TRADE_price_fill: " + str(GVAR.TRADE_price_fill) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.TRADE_round_prices: " + str(GVAR.TRADE_round_prices) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.TRADE_round_amounts: " + str(GVAR.TRADE_round_amounts) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " lnCFBmp (GVAR.SELL_CFB_lnMP_max_limit) : " + str(GVAR.SELL_CFB_lnMP_max_limit) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " lnCFBmp (GVAR.SELL_CFB_lnMP_max_value) : " + str(GVAR.SELL_CFB_lnMP_max_value) + pcolors.ENDC)	
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " CFBmp (GVAR.SELL_CFB_margin_percent) : " + str(GVAR.SELL_CFB_margin_percent) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " MV_CFBmP (GVAR.SELL_CFB_MV_margin_percent) : " + str(GVAR.SELL_CFB_MV_margin_percent) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.SELL_price_margin: " + str(GVAR.SELL_price_margin) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.BUY_price_margin: " + str(GVAR.BUY_price_margin) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.VIOLET + " GVAR.BUY_amount : " + str(GVAR.BUY_amount) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.SELL_amount: " + str(GVAR.SELL_amount) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.IDLE_locked: " + str(GVAR.IDLE_locked) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.IDLE_delayer_index: " + str(GVAR.IDLE_delayer_index) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.IDLE_delayer_over: " + str(GVAR.IDLE_delayer_over) + pcolors.ENDC)
	bprint(pcolors.VIOLET + ">>>>>>>> " + pcolors.ENDC + pcolors.YELLOW + " GVAR.IDLE_price_margin_mp: " + str(GVAR.IDLE_price_margin_mp) + pcolors.ENDC)

def JSON_curator(PARAM_JSON_string) :

	Jstr = str(PARAM_JSON_string)

	Jstr = Jstr.replace("u'","'")
	Jstr = Jstr.replace("'",'"')
	Jstr = Jstr.replace("False","false")
	Jstr = Jstr.replace("True","true")

	return Jstr

# =========================================================

#====================================================================================================

EXCHANGE_ORDER_Cancel = BINANCE_ORDER_Cancel
EXCHANGE_ORDER_GetStatus = BINANCE_ORDER_GetStatus
EXCHANGE_ORDER_GetData = BINANCE_ORDER_GetData
EXCHANGE_ORDER_Create_StopLimit = BINANCE_ORDER_Create_StopLimit

EXCHANGE_TICKER_GetTickerData = BINANCE_TICKER_GetTickerData
EXCHANGE_TICKER_GetAllTickersData = BINANCE_TICKER_GetAllTickersData

EXCHANGE_ASSET_GetAssetBalance = BINANCE_ASSET_GetAssetBalance

EXCHANGE_TRADES_GetMyTrades = BINANCE_GetMyTrades

EXCHANGE_ORDER_Print_OpenOrders = BINANCE_ORDERS_printOpenOrders
#EXCHANGE_ORDER_OpenOrders_Symbol = BINANCE_ORDERS_OpenOrders_Symbol

TIME_getNowTime = TIME_REAL_getNowTime
#BINANCE = Client
BINANCE = Client(keys.APIKey, keys.SecretKey) 

def SIMULATOR_DefSet (PARAM_SIMULATOR_orders, PARAM_SIMULATOR_ticker) :

	global EXCHANGE_ORDER_Cancel 
	global EXCHANGE_ORDER_GetStatus 
	global EXCHANGE_ORDER_Create_StopLimit
	global SIMULATOR_TICKER_dataFile
	global EXCHANGE_TICKER_GetTickerData
	global TIME_getNowTime
	global BINANCE

	if (PARAM_SIMULATOR_orders == False) :

		BINANCE = Client(keys.APIKey, keys.SecretKey) 

		EXCHANGE_ORDER_Cancel = BINANCE_ORDER_Cancel
		EXCHANGE_ORDER_GetStatus = BINANCE_ORDER_GetStatus
		EXCHANGE_ORDER_Create_StopLimit = BINANCE_ORDER_Create_StopLimit
		EXCHANGE_TICKER_GetTickerData = BINANCE_TICKER_GetTickerData
		EXCHANGE_TRADES_GetMyTrades = BINANCE_GetMyTrades
		TIME_getNowTime = TIME_REAL_getNowTime

	else :

		EXCHANGE_ORDER_Cancel = SIMULATOR_ORDER_Cancel
		EXCHANGE_ORDER_GetStatus = SIMULATOR_ORDER_GetStatus
		EXCHANGE_ORDER_Create_StopLimit = SIMULATOR_ORDER_Create_StopLimit
		if(PARAM_SIMULATOR_ticker == True) :
			EXCHANGE_TICKER_GetTickerData = SIMULATOR_TICKER_GetTickerData
			EXCHANGE_TRADES_GetMyTrades = SIMULATOR_TRADES_GetMyTrades
			TIME_getNowTime = TIME_SIMULATOR_getNowTime
		else :
			BINANCE = Client(keys.APIKey, keys.SecretKey) 
			EXCHANGE_TICKER_GetTickerData = BINANCE_TICKER_GetTickerData
			EXCHANGE_TRADES_GetMyTrades = BINANCE_GetMyTrades		

#====================================================================================================

def ORDER_LoadOpenOrder(PARAM_orderId, PARAM_symbol, PARAM_mode) :

	order_id = PARAM_orderId
	order_symbol = PARAM_symbol

	defName = "ORDER_LoadOpenOrder: "
	bprint(defName + "Asking server for order data -> OrderId: " + str(order_id) + " | Symbol: " + str(order_symbol))

	order_data = EXCHANGE_ORDER_GetData(order_id, order_symbol)

	bprint("")
	bprint(str(order_data))
	bprint("")

	order_amount = order_data['origQty']
	order_price_limit = order_data['price']
	order_price_stop = order_data['stopPrice']
	order_side = order_data['side']

	if(order_side == "SELL") :

		GVAR.FLAG_LOAD_sell_order = True

		bprint(defName + "Setting BUY_mode_on = False")	
		bprint(defName + "Setting SELL_mode_on = True")
		bprint(defName + "Setting IDLE_mode_on = False")
		
		bprint(defName + "Setting GVAR.MODE = " + str(PARAM_mode))
		GVAR.MODE = PARAM_mode
		bprint(defName + "Loading GVAR.MODE.load(" + str(PARAM_mode) + ")")
		GVAR.MODE_load(PARAM_mode)

		GVAR.BUY_mode_on = False
		GVAR.SELL_mode_on = True

		GVAR.SELL_orderId = order_id
		GVAR.TRADE_orderId = order_id
		
		GVAR.SELL_price_stop = order_price_stop
		GVAR.SELL_price_limit = order_price_limit

	bprint("")	
	#bprint("Ok so far")
	#quit()

def CFB_AddValueTolnCFBmp (limit, value) :

	GVAR.MODE_VARS.SELL_CFB_lnMP_limits.append(limit)
	GVAR.MODE_VARS.SELL_CFB_lnMP_values.append(value)

	GVAR.SELL_CFB_lnMP_limits = GVAR.MODE_VARS.SELL_CFB_lnMP_limits
	GVAR.SELL_CFB_lnMP_values = GVAR.MODE_VARS.SELL_CFB_lnMP_values

	print ""
	print " >> lnCFBmP_limits : " + str(GVAR.MODE_VARS.SELL_CFB_lnMP_limits)
	print " >> lnCFBmP_values : " + str(GVAR.MODE_VARS.SELL_CFB_lnMP_values)
	print ""

def CF_SetCFs (value) :

	GVAR.MODE_VARS.BUY_CFA_margin_percent_default = value
	GVAR.MODE_VARS.SELL_CFB_margin_percent_default = value
	GVAR.MODE_VARS.SELL_CFB_lnMP_limits = [ 0.10 ]
	GVAR.MODE_VARS.SELL_CFB_lnMP_values = [ 0.10 ]

	GVAR.BUY_CFA_margin_percent_default = GVAR.MODE_VARS.BUY_CFA_margin_percent_default
	GVAR.SELL_CFB_margin_percent_default = GVAR.MODE_VARS.SELL_CFB_margin_percent_default
	GVAR.SELL_CFB_lnMP_limits = GVAR.MODE_VARS.SELL_CFB_lnMP_limits
	GVAR.SELL_CFB_lnMP_values = GVAR.MODE_VARS.SELL_CFB_lnMP_values
	
	print ""
	print " >> CFAmP, CFBmP : " + str(value)
	print " >> lnCFBmP_limits : " + str(GVAR.MODE_VARS.SELL_CFB_lnMP_limits)
	print " >> lnCFBmP_values : " + str(GVAR.MODE_VARS.SELL_CFB_lnMP_values)
	print ""

def BOT_ParseArgs(PARAM_args) :

	#args_input_list = eval(PARAM_args[1])
	#print "[BOT II] Debug: " + str(PARAM_args) + " -> len(ARGS) = " + str(len(PARAM_args))
	#quit()

	defName = "BOT_ParseArgs: "

	if (len(PARAM_args) == 1) :
			
		if (PARAM_args[0] == "-help") :

				print ""
				print "AVAILABLE ARGUMENTS (1 at a time, can't use combined)" 
				print ""
				print "-pool <string>                                             Load pool filename"
				print ""
				print "-open_orders                                               Print all open orders at exchange and quit bot"
				print "-load_sell_order <string>+<long>+<string>+<float>+<float>  Symbol + Order ID + Trade Mode + Amount + Buy order fill price   Ex: BTCUSDT+123456789+FLONG+0.05+12500"
				print ""
				print "-ID+S+BAD+FM+FP <string>+<string>+<float>+<string>+<float> Bot ID + Symbol + Bots Amount Divider + First Mode + Fixed Price Ex: BOT_1+BTCUSDT+3+ASSISTED+9500.0"
				print ""
				print "-fixed <float>                                             Set BUY stop price at fixed price with CFA disabled              Ex: 9500.00 , 0.080 , 0.000051"
				print "-fixedP <float>                                            Set BUY stop price at % above current ticker price               Ex: 1.00 , 0.5 , 0.1"
				print ""
				print "-CFAmP <float>                                             Set FIRST (and only first) CFA margin percent at specific %      Ex: 1.52 , 1.00 , 0.5"
				print ""
				print "-mode <string>                                             Set BOT mode at specific defined mode in GVAR.py                 Ex: AUTO, ASSISTED, etc"
				print ""
				print ""
				print "SIMULATIONS ARGUMENTS:" 
				print ""
				print "+CFsmP <float>                 Set BUY_CFAmP and SELL_CFBmP to specific %                    (for batch calibration of variables)"
				print "+lnCFBmP <float_1> <float_2>   Add to current lnCFB (limit, value) = (float_1, float_2)      (for batch testing of lnCFB values)"
				print ""

				quit()
		
		if (PARAM_args[0] == "-open_orders") :

			print "[BOT II] Printing open orders : "
			print ""
			EXCHANGE_ORDER_Print_OpenOrders_Symbol("","")
			quit()
					
	if (len(PARAM_args) == 2) :

		print ""		
		print "[BOT II] Reading arguments: ARGS[0] = '" + PARAM_args[0] + "' ARGS[1] = '" + PARAM_args[1] + "'"

		if (PARAM_args[0] == "-pool") :

			print ""
			print defName + "Loading pool file '" + PARAM_args[1] + "'" 
			print ""
			POOL_reload(str(PARAM_args[1]))

		if (PARAM_args[0] == "+TICKER_data_file") :

			print "[BOT II] Loading data file : (" + PARAM_args[1] + ")" 
			print ""
			GVAR.SIMULATOR_TICKER_dataFile = str(PARAM_args[1])

		if (PARAM_args[0] == "-load_sell_order") :

			defName = "BOT_ParseArgs: "
			bprint("")
			bprint(defName + "Loading SELL order format: Symbol+OrderID+TradeMode+Amount+BuyFillPrice")
			#bprint(defName + "Loading SELL order ex    : BTCUSDT+1234567890+ASSISTED+9500.00")
			bprint("")
			bprint(defName + "Loading order : " + pcolors.YELLOW + PARAM_args[1] + pcolors.ENDC + "")
			bprint("")

			subARGS = ARGplusparser(PARAM_args[1],"+")

			min_subArgs = 4
			if(len(subARGS) < min_subArgs) :
				bprint("BOT_ParseArgs() : " + pcolors.RED + "ERROR" + pcolors.ENDC + " Wrong number of sub-arguments (minimum " + str(min_subArgs) + ")" )
				quit()

			order_symbol = str(subARGS[0])
			order_id = str(subARGS[1])
			order_mode = str(subARGS[2])
			order_amount = float(subARGS[3])
			order_buy_fill_price = float(subARGS[4])

			GVAR.FLAG_LOAD_sell_order = True
			
			GVAR.symbol = order_symbol
			GVAR.TRADE_price_fill = order_buy_fill_price
			GVAR.BUY_price_limit = order_buy_fill_price
			GVAR.BUY_price_stop = order_buy_fill_price - GVAR.BUY_price_margin
			GVAR.BUY_amount = order_amount

			bprint(defName + "Setting GVAR.TRADE_price_fill = " + pcolors.TUR + str(GVAR.TRADE_price_fill) + pcolors.ENDC)
			bprint(defName + "Setting GVAR.BUY_price_limit = " + pcolors.TUR + str(GVAR.BUY_price_limit) + pcolors.ENDC)
			bprint(defName + "Setting GVAR.BUY_price_stop = " + pcolors.TUR + str(GVAR.BUY_price_stop) + pcolors.ENDC)
			bprint("")

			ORDER_LoadOpenOrder(order_id, order_symbol, order_mode)
		
		if (PARAM_args[0] == "-mode") :

			print "[BOT II] Setting Mode : " + pcolors.YELLOW + PARAM_args[1] + pcolors.ENDC + ""
			print ""
			GVAR.MODE = str(PARAM_args[1])
			GVAR.MODE_load(GVAR.MODE)

		if (PARAM_args[0] == "-load_order") :

			print "[BOT II] Loading order : " + pcolors.YELLOW + PARAM_args[1] + pcolors.ENDC + ""
			print ""

			subARGS = ARGplusparser(PARAM_args[1],"+")

			min_subArgs = 3
			if(len(subARGS) < min_subArgs) :
				bprint("BOT_ParseArgs() : " + pcolors.RED + "ERROR" + pcolors.ENDC + " Wrong number of sub-arguments (minimum " + str(min_subArgs) + ")" )
				quit()

			order_symbol = str(subARGS[0])
			order_id = str(subARGS[1])
			order_mode = str(subARGS[2])
			
			ORDER_LoadOpenOrder(order_id, order_symbol, order_mode)

		if (PARAM_args[0] == "-fixed") :

			print "[BOT II] Setting Fixed BUY price at : " + pcolors.YELLOW + PARAM_args[1] + pcolors.ENDC + ""
			print ""
			GVAR.BUY_CFA_enabled = False
			GVAR.BUY_fixed_price_enabled = True
			GVAR.BUY_price_stop = float(PARAM_args[1])
			GVAR.BUY_price_limit = GVAR.BUY_price_stop + GVAR.BUY_price_margin

		if (PARAM_args[0] == "-fixedP") :

			fixed_percent = float(PARAM_args[1])
			print "[BOT II] Setting Fixed Percent BUY price at : " + pcolors.YELLOW + str(fixed_percent) + pcolors.ENDC + " %"
			print ""
			GVAR.BUY_CFA_enabled = False
			GVAR.BUY_fixed_price_enabled = True
			ticker_data = EXCHANGE_TICKER_GetTickerData(GVAR.symbol)
			ticker_price_bid = float(ticker_data['bidPrice'])
			
			GVAR.BUY_price_stop = round(float(ticker_price_bid * (1 + fixed_percent / 100)),GVAR.TRADE_round_prices)
			GVAR.BUY_price_limit = GVAR.BUY_price_stop + GVAR.BUY_price_margin

		if (PARAM_args[0] == "-CFAmP") :

				print "[BOT II] Setting to CFAmP to = " + pcolors.YELLOW + PARAM_args[1] + pcolors.ENDC + " %" 
				print ""
				GVAR.FLAG_CFA_first_run = True
				GVAR.FLAG_CFA_first_run_value = float(PARAM_args[1])

		if (PARAM_args[0] == "+CFAmP") :

				print "[BOT II] Setting to CFAmP, CFBmP and lnCFAmP values, limit to = (" + PARAM_args[1] + ")" 
				print ""
				CF_SetCFs(float(PARAM_args[1]))

		if (PARAM_args[0] == "-ID+S+BAD+FM+FP") :

			subARGS = ARGplusparser(PARAM_args[1],"+")
			bprint("")
			bprint("BOT_ParseArgs() : Using option -ID+S+BAD+FM+FP (Bot ID + Symbol + Amount Divider + First Mode + Fixed Price)")
			bprint("BOT_ParseArgs() : Received sub-arguments string " + pcolors.YELLOW + str(PARAM_args[1]) + pcolors.ENDC + " -> subARGS parsing returned: " + str(subARGS))
			
			if(len(subARGS) < 3) :
				bprint("BOT_ParseArgs() : " + pcolors.RED + "ERROR" + pcolors.ENDC + " Wrong number of sub-arguments (minimum 3)" )
				quit()

			botID = subARGS[0]
			symbol = subARGS[1]
			bots_amount_divider = subARGS[2]
			first_mode = subARGS[3]
			fixed_price = subARGS[4]

			GVAR.FLAG_first_run = True
			GVAR.IDLE_mode_on = True
			
			bprint("")
			bprint("BOT_ParseArgs() : Setting Bot ID " + pcolors.GREEN + botID + pcolors.ENDC + "")
			GVAR.BOT_ID = botID
			bprint("BOT_ParseArgs() : Setting SYMBOL " + pcolors.GREEN + symbol + pcolors.ENDC + "")
			GVAR.symbol = symbol
			
			bprint("BOT_ParseArgs() : Dividing amount in " + pcolors.TUR + str(bots_amount_divider) + pcolors.ENDC + " BOTS " + pcolors.VIOLET + GVAR.symbol + pcolors.ENDC + " at " + pcolors.GREEN + "BUY STOP" + pcolors.ENDC + " price : " + pcolors.TUR + str(fixed_price) + pcolors.ENDC + " " + pcolors.VIOLET + GVAR.SELL_symbol + pcolors.ENDC)
			
			GVAR.BUY_CFA_enabled = False
			GVAR.BUY_fixed_price_enabled = True

			GVAR.FLAG_bots_amount_divider = float(bots_amount_divider)
			GVAR.BUY_price_stop = float(fixed_price)
			
			# Set GVAR.IDLE_price_limit here only for visual.py initalization purpouses (to avoid errors when calcs % of graph scaling)
			# (Will be recalculated later with correct rounding variables)
			GVAR.IDLE_price_limit = calcIdlePriceLimit(GVAR.BUY_price_stop, GVAR.IDLE_price_margin_mp)
			
			bprint("BOT_ParseArgs() : Setting Mode " + pcolors.YELLOW + first_mode + pcolors.ENDC + "")
			bprint("")
			GVAR.FLAG_first_run_MODE = str(first_mode)
			GVAR.MODE = first_mode
			GVAR.MODE_load(GVAR.FLAG_first_run_MODE)

	if (len(PARAM_args) == 3) :
		
		print ""
		print "[BOT II] Reading arguments: ARGS[0] = '" + PARAM_args[0] + "' ARGS[1] = '" + PARAM_args[1] + "'" + "' ARGS[2] = '" + PARAM_args[2] + "'"
		
		if (PARAM_args[0] == "+lnCFBmP") :

			print "[BOT II] Adding to lnCFBmP -> (limit, value) = (" + PARAM_args[1] + " , " + PARAM_args[2] + ")" 
			print ""
			CFB_AddValueTolnCFBmp(float(PARAM_args[1]), float(PARAM_args[2]))

def ARGplusparser(PARAM_string, PARAM_separator) :

	separator = PARAM_separator
	# Add extra string to enabled full parsing of the whole line
	# Otherwise for loop goes only to the n-1 char
	str = PARAM_string + separator

	start_pos = 0
	plus_pos = 0
	end_pos = 0
	str_len = len(str)

	items_list = []

	index = 0

	for char in str :

		if char == separator :

			end_pos = index
			item = str[start_pos:end_pos]
			items_list.append(item)
			start_pos = index + 1
	
		index += 1
	
	return items_list

#====================================================================================================
#====================================================================================================
#====================================================================================================
#====================================================================================================
#====================================================================================================


def BlockGenerator_OLD(PARAM_BlockSize) :

	horizontal_blocks = 1
	seconds_counter = 0
	block_counter = 0
	block_points_size = PARAM_BlockSize
	block_points_counter = 0
	block_tickers_per_point = 1
	ticker_counter = 0
	point_str = ":"
	block_started = True
	printStr = ""
	flushPrintStr = False

	while(seconds_counter < PARAM_BlockSize) :

		"""#CLOSE_VALS = client.get_historical_klines(gvar_symbol, Client.KLINE_INTERVAL_1MINUTE, '1 hour ago UTC')
		TICKER_DATA = Client.get_ticker(symbol=GVAR.symbol)
		data_str = str(TICKER_DATA)
		data_str = data_str.replace("u'","'")
		data_str = data_str.replace("'",'"')
		TICKER_JSON = json.loads(data_str)
		TICKER_PRICE_BID = TICKER_JSON["bidPrice"]
		timeStr = TIME_getNowTime()"""

		seconds_counter = seconds_counter + 1

		# ====== BLOCK CREATOR ======
		# 1 point = n tickers (block_tickers_per_point = n)
		# 1 block = m points (block_size = m)
		# 1 hour = 6 blocks x 10 tickers (1 ticker per second approx)

		if (block_points_counter == 0) :
			if (ticker_counter == 0) :
				printStr += "["

		dotStr = ""
		for i in range(seconds_counter) :
			dotStr = dotStr + ":"

		spaceStr = ""
		for i in range(PARAM_BlockSize - seconds_counter) :
			spaceStr = spaceStr + " "

		printStr = "     [" + dotStr + spaceStr + "]     "

		sys.stdout.write(printStr + "\r")
		sys.stdout.flush()

		if (flushPrintStr == True) :
			printStr = ""
			flushPrintStr = False

		sleep(1)

	return ""

def POOL_backup() :

	GVAR.POOL_markets['NEO']['PRICE_IDLE_limit'] = 17.38                                                                                                                         
	GVAR.POOL_markets['NEO']['IDLE_priority_index'] = 22                                                                                                                         
	GVAR.POOL_markets['NEO']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['NEO']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['NEO']['PRICE_BUY_margin'] = 0.1                                                                                                                           
	GVAR.POOL_markets['NEO']['TRADE_ASSET_amount'] = 6.885                                                                                                                       
	GVAR.POOL_markets['NEO']['PRICE_SELL_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['NEO']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['NEO']['PRICE_BUY_stop'] = 17.415                                                                                                                          
	GVAR.POOL_markets['NEO']['PRICE_BUY_limit'] = 17.515                                                                                                                         
	GVAR.POOL_markets['BAT']['PRICE_IDLE_limit'] = 0.2211                                                                                                                        
	GVAR.POOL_markets['BAT']['IDLE_priority_index'] = 34                                                                                                                         
	GVAR.POOL_markets['BAT']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['BAT']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['BAT']['PRICE_BUY_margin'] = 0.005                                                                                                                         
	GVAR.POOL_markets['BAT']['TRADE_ASSET_amount'] = 532.38                                                                                                                      
	GVAR.POOL_markets['BAT']['PRICE_SELL_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['BAT']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['BAT']['PRICE_BUY_stop'] = 0.2215                                                                                                                          
	GVAR.POOL_markets['BAT']['PRICE_BUY_limit'] = 0.2265                                                                                                                         
	GVAR.POOL_markets['DOGE']['PRICE_IDLE_limit'] = 0.0026611                                                                                                                    
	GVAR.POOL_markets['DOGE']['IDLE_priority_index'] = 10                                                                                                                        
	GVAR.POOL_markets['DOGE']['IDLE_margin_percent'] = 0.52                                                                                                                      
	GVAR.POOL_markets['DOGE']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['DOGE']['PRICE_BUY_margin'] = 5e-05                                                                                                                        
	GVAR.POOL_markets['DOGE']['TRADE_ASSET_amount'] = 44251.0                                                                                                                    
	GVAR.POOL_markets['DOGE']['PRICE_SELL_margin'] = 5e-05                                                                                                                       
	GVAR.POOL_markets['DOGE']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['DOGE']['PRICE_BUY_stop'] = 0.002675                                                                                                                       
	GVAR.POOL_markets['DOGE']['PRICE_BUY_limit'] = 0.002725                                                                                                                      
	GVAR.POOL_markets['BCH']['PRICE_IDLE_limit'] = 266.25                                                                                                                        
	GVAR.POOL_markets['BCH']['IDLE_priority_index'] = 35                                                                                                                         
	GVAR.POOL_markets['BCH']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['BCH']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['BCH']['PRICE_BUY_margin'] = 0.5                                                                                                                           
	GVAR.POOL_markets['BCH']['TRADE_ASSET_amount'] = 0.45116                                                                                                                     
	GVAR.POOL_markets['BCH']['PRICE_SELL_margin'] = 0.5                                                                                                                          
	GVAR.POOL_markets['BCH']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['BCH']['PRICE_BUY_stop'] = 266.78                                                                                                                          
	GVAR.POOL_markets['BCH']['PRICE_BUY_limit'] = 267.28                                                                                                                         
	GVAR.POOL_markets['RSR']['PRICE_IDLE_limit'] = 0.01113                                                                                                                       
	GVAR.POOL_markets['RSR']['IDLE_priority_index'] = 17                                                                                                                         
	GVAR.POOL_markets['RSR']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['RSR']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['RSR']['PRICE_BUY_margin'] = 0.001                                                                                                                         
	GVAR.POOL_markets['RSR']['TRADE_ASSET_amount'] = 9924.7                                                                                                                      
	GVAR.POOL_markets['RSR']['PRICE_SELL_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['RSR']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['RSR']['PRICE_BUY_stop'] = 0.01115                                                                                                                         
	GVAR.POOL_markets['RSR']['PRICE_BUY_limit'] = 0.01215                                                                                                                        
	GVAR.POOL_markets['ATOM']['PRICE_IDLE_limit'] = 6.043                                                                                                                        
	GVAR.POOL_markets['ATOM']['IDLE_priority_index'] = 42                                                                                                                        
	GVAR.POOL_markets['ATOM']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['ATOM']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['ATOM']['PRICE_BUY_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['ATOM']['TRADE_ASSET_amount'] = 19.591                                                                                                                     
	GVAR.POOL_markets['ATOM']['PRICE_SELL_margin'] = 0.1                                                                                                                         
	GVAR.POOL_markets['ATOM']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['ATOM']['PRICE_BUY_stop'] = 6.055                                                                                                                          
	GVAR.POOL_markets['ATOM']['PRICE_BUY_limit'] = 6.155                                                                                                                         
	GVAR.POOL_markets['EOS']['PRICE_IDLE_limit'] = 2.726                                                                                                                         
	GVAR.POOL_markets['EOS']['IDLE_priority_index'] = 21                                                                                                                         
	GVAR.POOL_markets['EOS']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['EOS']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['EOS']['PRICE_BUY_margin'] = 0.01                                                                                                                          
	GVAR.POOL_markets['EOS']['TRADE_ASSET_amount'] = 43.99                                                                                                                       
	GVAR.POOL_markets['EOS']['PRICE_SELL_margin'] = 0.01                                                                                                                         
	GVAR.POOL_markets['EOS']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['EOS']['PRICE_BUY_stop'] = 2.7315                                                                                                                          
	GVAR.POOL_markets['EOS']['PRICE_BUY_limit'] = 2.7415                                                                                                                         
	GVAR.POOL_markets['ETC']['PRICE_IDLE_limit'] = 5.5204                                                                                                                        
	GVAR.POOL_markets['ETC']['IDLE_priority_index'] = 52                                                                                                                         
	GVAR.POOL_markets['ETC']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['ETC']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['ETC']['PRICE_BUY_margin'] = 0.1                                                                                                                           
	GVAR.POOL_markets['ETC']['TRADE_ASSET_amount'] = 21.41                                                                                                                       
	GVAR.POOL_markets['ETC']['PRICE_SELL_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['ETC']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['ETC']['PRICE_BUY_stop'] = 5.5315                                                                                                                          
	GVAR.POOL_markets['ETC']['PRICE_BUY_limit'] = 5.6315                                                                                                                         
	GVAR.POOL_markets['IDEX']['PRICE_IDLE_limit'] = 0.07485                                                                                                                      
	GVAR.POOL_markets['IDEX']['IDLE_priority_index'] = 54                                                                                                                        
	GVAR.POOL_markets['IDEX']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['IDEX']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['IDEX']['PRICE_BUY_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['IDEX']['TRADE_ASSET_amount'] = 1586.6                                                                                                                     
	GVAR.POOL_markets['IDEX']['PRICE_SELL_margin'] = 0.001                                                                                                                       
	GVAR.POOL_markets['IDEX']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['IDEX']['PRICE_BUY_stop'] = 0.075                                                                                                                          
	GVAR.POOL_markets['IDEX']['PRICE_BUY_limit'] = 0.076                                                                                                                         
	GVAR.POOL_markets['MKR']['PRICE_IDLE_limit'] = 599.948                                                                                                                       
	GVAR.POOL_markets['MKR']['IDLE_priority_index'] = 19                                                                                                                         
	GVAR.POOL_markets['MKR']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['MKR']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['MKR']['PRICE_BUY_margin'] = 0.5                                                                                                                           
	GVAR.POOL_markets['MKR']['TRADE_ASSET_amount'] = 0.20042                                                                                                                     
	GVAR.POOL_markets['MKR']['PRICE_SELL_margin'] = 0.5                                                                                                                          
	GVAR.POOL_markets['MKR']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['MKR']['PRICE_BUY_stop'] = 601.15                                                                                                                          
	GVAR.POOL_markets['MKR']['PRICE_BUY_limit'] = 601.65                                                                                                                         
	GVAR.POOL_markets['BNB']['PRICE_IDLE_limit'] = 31.9946                                                                                                                       
	GVAR.POOL_markets['BNB']['IDLE_priority_index'] = 4                                                                                                                          
	GVAR.POOL_markets['BNB']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['BNB']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['BNB']['PRICE_BUY_margin'] = 0.1                                                                                                                           
	GVAR.POOL_markets['BNB']['TRADE_ASSET_amount'] = 3.75                                                                                                                        
	GVAR.POOL_markets['BNB']['PRICE_SELL_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['BNB']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['BNB']['PRICE_BUY_stop'] = 32.0587                                                                                                                         
	GVAR.POOL_markets['BNB']['PRICE_BUY_limit'] = 32.1587                                                                                                                        
	GVAR.POOL_markets['KSM']['PRICE_IDLE_limit'] = 28.658                                                                                                                        
	GVAR.POOL_markets['KSM']['IDLE_priority_index'] = 45                                                                                                                         
	GVAR.POOL_markets['KSM']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['KSM']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['KSM']['PRICE_BUY_margin'] = 0.1                                                                                                                           
	GVAR.POOL_markets['KSM']['TRADE_ASSET_amount'] = 4.185                                                                                                                       
	GVAR.POOL_markets['KSM']['PRICE_SELL_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['KSM']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['KSM']['PRICE_BUY_stop'] = 28.715                                                                                                                          
	GVAR.POOL_markets['KSM']['PRICE_BUY_limit'] = 28.815                                                                                                                         
	GVAR.POOL_markets['ETH']['PRICE_IDLE_limit'] = 386.56                                                                                                                        
	GVAR.POOL_markets['ETH']['IDLE_priority_index'] = 2                                                                                                                          
	GVAR.POOL_markets['ETH']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['ETH']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['ETH']['PRICE_BUY_margin'] = 0.5                                                                                                                           
	GVAR.POOL_markets['ETH']['TRADE_ASSET_amount'] = 0.31092                                                                                                                     
	GVAR.POOL_markets['ETH']['PRICE_SELL_margin'] = 0.5                                                                                                                          
	GVAR.POOL_markets['ETH']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['ETH']['PRICE_BUY_stop'] = 387.33                                                                                                                          
	GVAR.POOL_markets['ETH']['PRICE_BUY_limit'] = 387.83                                                                                                                         
	GVAR.POOL_markets['DATA']['PRICE_IDLE_limit'] = 0.04707                                                                                                                      
	GVAR.POOL_markets['DATA']['IDLE_priority_index'] = 37                                                                                                                        
	GVAR.POOL_markets['DATA']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['DATA']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['DATA']['PRICE_BUY_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['DATA']['TRADE_ASSET_amount'] = 2503.8                                                                                                                     
	GVAR.POOL_markets['DATA']['PRICE_SELL_margin'] = 0.001                                                                                                                       
	GVAR.POOL_markets['DATA']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['DATA']['PRICE_BUY_stop'] = 0.04716                                                                                                                        
	GVAR.POOL_markets['DATA']['PRICE_BUY_limit'] = 0.04816                                                                                                                       
	GVAR.POOL_markets['DOT']['PRICE_IDLE_limit'] = 4.4825                                                                                                                        
	GVAR.POOL_markets['DOT']['IDLE_priority_index'] = 40                                                                                                                         
	GVAR.POOL_markets['DOT']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['DOT']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['DOT']['PRICE_BUY_margin'] = 0.1                                                                                                                           
	GVAR.POOL_markets['DOT']['TRADE_ASSET_amount'] = 26.26                                                                                                                       
	GVAR.POOL_markets['DOT']['PRICE_SELL_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['DOT']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['DOT']['PRICE_BUY_stop'] = 4.4915                                                                                                                          
	GVAR.POOL_markets['DOT']['PRICE_BUY_limit'] = 4.5915                                                                                                                         
	GVAR.POOL_markets['DGB']['PRICE_IDLE_limit'] = 0.0241                                                                                                                        
	GVAR.POOL_markets['DGB']['IDLE_priority_index'] = 55                                                                                                                         
	GVAR.POOL_markets['DGB']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['DGB']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['DGB']['PRICE_BUY_margin'] = 0.001                                                                                                                         
	GVAR.POOL_markets['DGB']['TRADE_ASSET_amount'] = 4794.6                                                                                                                      
	GVAR.POOL_markets['DGB']['PRICE_SELL_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['DGB']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['DGB']['PRICE_BUY_stop'] = 0.02415                                                                                                                         
	GVAR.POOL_markets['DGB']['PRICE_BUY_limit'] = 0.02515                                                                                                                        
	GVAR.POOL_markets['JST']['PRICE_IDLE_limit'] = 0.02647                                                                                                                       
	GVAR.POOL_markets['JST']['IDLE_priority_index'] = 8                                                                                                                          
	GVAR.POOL_markets['JST']['IDLE_margin_percent'] = 0.32                                                                                                                       
	GVAR.POOL_markets['JST']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['JST']['PRICE_BUY_margin'] = 0.001                                                                                                                         
	GVAR.POOL_markets['JST']['TRADE_ASSET_amount'] = 4377.0                                                                                                                      
	GVAR.POOL_markets['JST']['PRICE_SELL_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['JST']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['JST']['PRICE_BUY_stop'] = 0.02655                                                                                                                         
	GVAR.POOL_markets['JST']['PRICE_BUY_limit'] = 0.02755                                                                                                                        
	GVAR.POOL_markets['PAXG']['PRICE_IDLE_limit'] = 1921.7                                                                                                                       
	GVAR.POOL_markets['PAXG']['IDLE_priority_index'] = 47                                                                                                                        
	GVAR.POOL_markets['PAXG']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['PAXG']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['PAXG']['PRICE_BUY_margin'] = 5                                                                                                                            
	GVAR.POOL_markets['PAXG']['TRADE_ASSET_amount'] = 0.062461                                                                                                                   
	GVAR.POOL_markets['PAXG']['PRICE_SELL_margin'] = 5                                                                                                                           
	GVAR.POOL_markets['PAXG']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['PAXG']['PRICE_BUY_stop'] = 1925.55                                                                                                                        
	GVAR.POOL_markets['PAXG']['PRICE_BUY_limit'] = 1930.55                                                                                                                       
	GVAR.POOL_markets['NANO']['PRICE_IDLE_limit'] = 0.8498                                                                                                                       
	GVAR.POOL_markets['NANO']['IDLE_priority_index'] = 39                                                                                                                        
	GVAR.POOL_markets['NANO']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['NANO']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['NANO']['PRICE_BUY_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['NANO']['TRADE_ASSET_amount'] = 140.79                                                                                                                     
	GVAR.POOL_markets['NANO']['PRICE_SELL_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['NANO']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['NANO']['PRICE_BUY_stop'] = 0.8515                                                                                                                         
	GVAR.POOL_markets['NANO']['PRICE_BUY_limit'] = 0.8565                                                                                                                        
	GVAR.POOL_markets['YFI']['PRICE_IDLE_limit'] = 14488.96                                                                                                                      
	GVAR.POOL_markets['YFI']['IDLE_priority_index'] = 32                                                                                                                         
	GVAR.POOL_markets['YFI']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['YFI']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['YFI']['PRICE_BUY_margin'] = 10                                                                                                                            
	GVAR.POOL_markets['YFI']['TRADE_ASSET_amount'] = 0.0083                                                                                                                      
	GVAR.POOL_markets['YFI']['PRICE_SELL_margin'] = 10                                                                                                                           
	GVAR.POOL_markets['YFI']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['YFI']['PRICE_BUY_stop'] = 14518.0                                                                                                                         
	GVAR.POOL_markets['YFI']['PRICE_BUY_limit'] = 14528.0                                                                                                                        
	GVAR.POOL_markets['FIO']['PRICE_IDLE_limit'] = 0.1113                                                                                                                        
	GVAR.POOL_markets['FIO']['IDLE_priority_index'] = 36                                                                                                                         
	GVAR.POOL_markets['FIO']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['FIO']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['FIO']['PRICE_BUY_margin'] = 0.005                                                                                                                         
	GVAR.POOL_markets['FIO']['TRADE_ASSET_amount'] = 1035.06                                                                                                                     
	GVAR.POOL_markets['FIO']['PRICE_SELL_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['FIO']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['FIO']['PRICE_BUY_stop'] = 0.1115                                                                                                                          
	GVAR.POOL_markets['FIO']['PRICE_BUY_limit'] = 0.1165                                                                                                                         
	GVAR.POOL_markets['SXP']['PRICE_IDLE_limit'] = 1.3588                                                                                                                        
	GVAR.POOL_markets['SXP']['IDLE_priority_index'] = 13                                                                                                                         
	GVAR.POOL_markets['SXP']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['SXP']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['SXP']['PRICE_BUY_margin'] = 0.01                                                                                                                          
	GVAR.POOL_markets['SXP']['TRADE_ASSET_amount'] = 87.92                                                                                                                       
	GVAR.POOL_markets['SXP']['PRICE_SELL_margin'] = 0.01                                                                                                                         
	GVAR.POOL_markets['SXP']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['SXP']['PRICE_BUY_stop'] = 1.3615                                                                                                                          
	GVAR.POOL_markets['SXP']['PRICE_BUY_limit'] = 1.3715                                                                                                                         
	GVAR.POOL_markets['ALPHA']['PRICE_IDLE_limit'] = 0.03648                                                                                                                     
	GVAR.POOL_markets['ALPHA']['IDLE_priority_index'] = 38                                                                                                                       
	GVAR.POOL_markets['ALPHA']['IDLE_margin_percent'] = 0.2                                                                                                                      
	GVAR.POOL_markets['ALPHA']['TRADE_mode'] = "VL2"                                                                                                                               
	GVAR.POOL_markets['ALPHA']['PRICE_BUY_margin'] = 0.001                                                                                                                       
	GVAR.POOL_markets['ALPHA']['TRADE_ASSET_amount'] = 3211.3                                                                                                                    
	GVAR.POOL_markets['ALPHA']['PRICE_SELL_margin'] = 0.001                                                                                                                      
	GVAR.POOL_markets['ALPHA']['MARKET_enabled'] = True                                                                                                                          
	GVAR.POOL_markets['ALPHA']['PRICE_BUY_stop'] = 0.03655                                                                                                                       
	GVAR.POOL_markets['ALPHA']['PRICE_BUY_limit'] = 0.03755                                                                                                                      
	GVAR.POOL_markets['WRX']['PRICE_IDLE_limit'] = 0.0                                                                                                                           
	GVAR.POOL_markets['WRX']['IDLE_priority_index'] = 46                                                                                                                         
	GVAR.POOL_markets['WRX']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['WRX']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['WRX']['PRICE_BUY_margin'] = 0.001                                                                                                                         
	GVAR.POOL_markets['WRX']['TRADE_ASSET_amount'] = 0                                                                                                                           
	GVAR.POOL_markets['WRX']['PRICE_SELL_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['WRX']['MARKET_enabled'] = False                                                                                                                           
	GVAR.POOL_markets['WRX']['PRICE_BUY_stop'] = 0.0                                                                                                                             
	GVAR.POOL_markets['WRX']['PRICE_BUY_limit'] = 0.0                                                                                                                            
	GVAR.POOL_markets['CAKE']['PRICE_IDLE_limit'] = 1.0035                                                                                                                       
	GVAR.POOL_markets['CAKE']['IDLE_priority_index'] = 43                                                                                                                        
	GVAR.POOL_markets['CAKE']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['CAKE']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['CAKE']['PRICE_BUY_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['CAKE']['TRADE_ASSET_amount'] = 119.33                                                                                                                     
	GVAR.POOL_markets['CAKE']['PRICE_SELL_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['CAKE']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['CAKE']['PRICE_BUY_stop'] = 1.0055                                                                                                                         
	GVAR.POOL_markets['CAKE']['PRICE_BUY_limit'] = 1.0105                                                                                                                        
	GVAR.POOL_markets['AION']['PRICE_IDLE_limit'] = 0.0813                                                                                                                       
	GVAR.POOL_markets['AION']['IDLE_priority_index'] = 31                                                                                                                        
	GVAR.POOL_markets['AION']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['AION']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['AION']['PRICE_BUY_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['AION']['TRADE_ASSET_amount'] = 1461.64                                                                                                                    
	GVAR.POOL_markets['AION']['PRICE_SELL_margin'] = 0.001                                                                                                                       
	GVAR.POOL_markets['AION']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['AION']['PRICE_BUY_stop'] = 0.0815                                                                                                                         
	GVAR.POOL_markets['AION']['PRICE_BUY_limit'] = 0.0825                                                                                                                        
	GVAR.POOL_markets['IOTA']['PRICE_IDLE_limit'] = 0.2851                                                                                                                       
	GVAR.POOL_markets['IOTA']['IDLE_priority_index'] = 25                                                                                                                        
	GVAR.POOL_markets['IOTA']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['IOTA']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['IOTA']['PRICE_BUY_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['IOTA']['TRADE_ASSET_amount'] = 414.81                                                                                                                     
	GVAR.POOL_markets['IOTA']['PRICE_SELL_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['IOTA']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['IOTA']['PRICE_BUY_stop'] = 0.2857                                                                                                                         
	GVAR.POOL_markets['IOTA']['PRICE_BUY_limit'] = 0.2907                                                                                                                        
	GVAR.POOL_markets['VIDT']['PRICE_IDLE_limit'] = 0.4606                                                                                                                       
	GVAR.POOL_markets['VIDT']['IDLE_priority_index'] = 30                                                                                                                        
	GVAR.POOL_markets['VIDT']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['VIDT']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['VIDT']['PRICE_BUY_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['VIDT']['TRADE_ASSET_amount'] = 258.49                                                                                                                     
	GVAR.POOL_markets['VIDT']['PRICE_SELL_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['VIDT']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['VIDT']['PRICE_BUY_stop'] = 0.4615                                                                                                                         
	GVAR.POOL_markets['VIDT']['PRICE_BUY_limit'] = 0.4665                                                                                                                        
	GVAR.POOL_markets['OCEAN']['PRICE_IDLE_limit'] = 0.3608                                                                                                                      
	GVAR.POOL_markets['OCEAN']['IDLE_priority_index'] = 48                                                                                                                       
	GVAR.POOL_markets['OCEAN']['IDLE_margin_percent'] = 0.2                                                                                                                      
	GVAR.POOL_markets['OCEAN']['TRADE_mode'] = "VL2"                                                                                                                               
	GVAR.POOL_markets['OCEAN']['PRICE_BUY_margin'] = 0.001                                                                                                                       
	GVAR.POOL_markets['OCEAN']['TRADE_ASSET_amount'] = 332.65                                                                                                                    
	GVAR.POOL_markets['OCEAN']['PRICE_SELL_margin'] = 0.001                                                                                                                      
	GVAR.POOL_markets['OCEAN']['MARKET_enabled'] = True                                                                                                                          
	GVAR.POOL_markets['OCEAN']['PRICE_BUY_stop'] = 0.3615                                                                                                                        
	GVAR.POOL_markets['OCEAN']['PRICE_BUY_limit'] = 0.3625                                                                                                                       
	GVAR.POOL_markets['BTT']['PRICE_IDLE_limit'] = 0.0003653                                                                                                                     
	GVAR.POOL_markets['BTT']['IDLE_priority_index'] = 14                                                                                                                         
	GVAR.POOL_markets['BTT']['IDLE_margin_percent'] = 0.52                                                                                                                       
	GVAR.POOL_markets['BTT']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['BTT']['PRICE_BUY_margin'] = 5e-06                                                                                                                         
	GVAR.POOL_markets['BTT']['TRADE_ASSET_amount'] = 323979.0                                                                                                                    
	GVAR.POOL_markets['BTT']['PRICE_SELL_margin'] = 5e-06                                                                                                                        
	GVAR.POOL_markets['BTT']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['BTT']['PRICE_BUY_stop'] = 0.0003672                                                                                                                       
	GVAR.POOL_markets['BTT']['PRICE_BUY_limit'] = 0.0003722                                                                                                                      
	GVAR.POOL_markets['IQ']['PRICE_IDLE_limit'] = 0.002449                                                                                                                       
	GVAR.POOL_markets['IQ']['IDLE_priority_index'] = 28                                                                                                                          
	GVAR.POOL_markets['IQ']['IDLE_margin_percent'] = 0.2                                                                                                                         
	GVAR.POOL_markets['IQ']['TRADE_mode'] = "VL2"                                                                                                                                  
	GVAR.POOL_markets['IQ']['PRICE_BUY_margin'] = 5e-06                                                                                                                          
	GVAR.POOL_markets['IQ']['TRADE_ASSET_amount'] = 49038.0                                                                                                                      
	GVAR.POOL_markets['IQ']['PRICE_SELL_margin'] = 5e-06                                                                                                                         
	GVAR.POOL_markets['IQ']['MARKET_enabled'] = True                                                                                                                             
	GVAR.POOL_markets['IQ']['PRICE_BUY_stop'] = 0.002454                                                                                                                         
	GVAR.POOL_markets['IQ']['PRICE_BUY_limit'] = 0.002459                                                                                                                        
	GVAR.POOL_markets['COMP']['PRICE_IDLE_limit'] = 105.21                                                                                                                       
	GVAR.POOL_markets['COMP']['IDLE_priority_index'] = 12                                                                                                                        
	GVAR.POOL_markets['COMP']['IDLE_margin_percent'] = 0.32                                                                                                                      
	GVAR.POOL_markets['COMP']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['COMP']['PRICE_BUY_margin'] = 2                                                                                                                            
	GVAR.POOL_markets['COMP']['TRADE_ASSET_amount'] = 1.1212                                                                                                                     
	GVAR.POOL_markets['COMP']['PRICE_SELL_margin'] = 2                                                                                                                           
	GVAR.POOL_markets['COMP']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['COMP']['PRICE_BUY_stop'] = 105.55                                                                                                                         
	GVAR.POOL_markets['COMP']['PRICE_BUY_limit'] = 107.55                                                                                                                        
	GVAR.POOL_markets['XVS']['PRICE_IDLE_limit'] = 3.308                                                                                                                         
	GVAR.POOL_markets['XVS']['IDLE_priority_index'] = 18                                                                                                                         
	GVAR.POOL_markets['XVS']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['XVS']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['XVS']['PRICE_BUY_margin'] = 0.01                                                                                                                          
	GVAR.POOL_markets['XVS']['TRADE_ASSET_amount'] = 36.266                                                                                                                      
	GVAR.POOL_markets['XVS']['PRICE_SELL_margin'] = 0.01                                                                                                                         
	GVAR.POOL_markets['XVS']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['XVS']['PRICE_BUY_stop'] = 3.315                                                                                                                           
	GVAR.POOL_markets['XVS']['PRICE_BUY_limit'] = 3.325                                                                                                                          
	GVAR.POOL_markets['TOMO']['PRICE_IDLE_limit'] = 0.764                                                                                                                        
	GVAR.POOL_markets['TOMO']['IDLE_priority_index'] = 51                                                                                                                        
	GVAR.POOL_markets['TOMO']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['TOMO']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['TOMO']['PRICE_BUY_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['TOMO']['TRADE_ASSET_amount'] = 156.5                                                                                                                      
	GVAR.POOL_markets['TOMO']['PRICE_SELL_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['TOMO']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['TOMO']['PRICE_BUY_stop'] = 0.7655                                                                                                                         
	GVAR.POOL_markets['TOMO']['PRICE_BUY_limit'] = 0.7705                                                                                                                        
	GVAR.POOL_markets['FIL']['PRICE_IDLE_limit'] = 50.0013                                                                                                                       
	GVAR.POOL_markets['FIL']['IDLE_priority_index'] = 53                                                                                                                         
	GVAR.POOL_markets['FIL']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['FIL']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['FIL']['PRICE_BUY_margin'] = 0.25                                                                                                                          
	GVAR.POOL_markets['FIL']['TRADE_ASSET_amount'] = 2.39                                                                                                                        
	GVAR.POOL_markets['FIL']['PRICE_SELL_margin'] = 0.25                                                                                                                         
	GVAR.POOL_markets['FIL']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['FIL']['PRICE_BUY_stop'] = 50.1015                                                                                                                         
	GVAR.POOL_markets['FIL']['PRICE_BUY_limit'] = 50.3515                                                                                                                        
	GVAR.POOL_markets['XTZ']['PRICE_IDLE_limit'] = 2.2784                                                                                                                        
	GVAR.POOL_markets['XTZ']['IDLE_priority_index'] = 23                                                                                                                         
	GVAR.POOL_markets['XTZ']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['XTZ']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['XTZ']['PRICE_BUY_margin'] = 0.01                                                                                                                          
	GVAR.POOL_markets['XTZ']['TRADE_ASSET_amount'] = 52.59                                                                                                                       
	GVAR.POOL_markets['XTZ']['PRICE_SELL_margin'] = 0.01                                                                                                                         
	GVAR.POOL_markets['XTZ']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['XTZ']['PRICE_BUY_stop'] = 2.283                                                                                                                           
	GVAR.POOL_markets['XTZ']['PRICE_BUY_limit'] = 2.293                                                                                                                          
	GVAR.POOL_markets['ZRX']['PRICE_IDLE_limit'] = 0.4346                                                                                                                        
	GVAR.POOL_markets['ZRX']['IDLE_priority_index'] = 58                                                                                                                         
	GVAR.POOL_markets['ZRX']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['ZRX']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['ZRX']['PRICE_BUY_margin'] = 0.005                                                                                                                         
	GVAR.POOL_markets['ZRX']['TRADE_ASSET_amount'] = 273.75                                                                                                                      
	GVAR.POOL_markets['ZRX']['PRICE_SELL_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['ZRX']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['ZRX']['PRICE_BUY_stop'] = 0.4355                                                                                                                          
	GVAR.POOL_markets['ZRX']['PRICE_BUY_limit'] = 0.4405                                                                                                                         
	GVAR.POOL_markets['DASH']['PRICE_IDLE_limit'] = 70.01                                                                                                                        
	GVAR.POOL_markets['DASH']['IDLE_priority_index'] = 33                                                                                                                        
	GVAR.POOL_markets['DASH']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['DASH']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['DASH']['PRICE_BUY_margin'] = 0.25                                                                                                                         
	GVAR.POOL_markets['DASH']['TRADE_ASSET_amount'] = 1.71286                                                                                                                    
	GVAR.POOL_markets['DASH']['PRICE_SELL_margin'] = 0.25                                                                                                                        
	GVAR.POOL_markets['DASH']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['DASH']['PRICE_BUY_stop'] = 70.15                                                                                                                          
	GVAR.POOL_markets['DASH']['PRICE_BUY_limit'] = 70.4                                                                                                                          
	GVAR.POOL_markets['STORJ']['PRICE_IDLE_limit'] = 0.4506                                                                                                                      
	GVAR.POOL_markets['STORJ']['IDLE_priority_index'] = 50                                                                                                                       
	GVAR.POOL_markets['STORJ']['IDLE_margin_percent'] = 0.2                                                                                                                      
	GVAR.POOL_markets['STORJ']['TRADE_mode'] = "VL2"                                                                                                                               
	GVAR.POOL_markets['STORJ']['PRICE_BUY_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['STORJ']['TRADE_ASSET_amount'] = 264.15                                                                                                                    
	GVAR.POOL_markets['STORJ']['PRICE_SELL_margin'] = 0.005                                                                                                                      
	GVAR.POOL_markets['STORJ']['MARKET_enabled'] = True                                                                                                                          
	GVAR.POOL_markets['STORJ']['PRICE_BUY_stop'] = 0.4515                                                                                                                        
	GVAR.POOL_markets['STORJ']['PRICE_BUY_limit'] = 0.4565                                                                                                                       
	GVAR.POOL_markets['LUNA']['PRICE_IDLE_limit'] = 0.3408                                                                                                                       
	GVAR.POOL_markets['LUNA']['IDLE_priority_index'] = 60                                                                                                                        
	GVAR.POOL_markets['LUNA']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['LUNA']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['LUNA']['PRICE_BUY_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['LUNA']['TRADE_ASSET_amount'] = 348.01                                                                                                                     
	GVAR.POOL_markets['LUNA']['PRICE_SELL_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['LUNA']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['LUNA']['PRICE_BUY_stop'] = 0.3415                                                                                                                         
	GVAR.POOL_markets['LUNA']['PRICE_BUY_limit'] = 0.3465                                                                                                                        
	GVAR.POOL_markets['ADA']['PRICE_IDLE_limit'] = 0.11395                                                                                                                       
	GVAR.POOL_markets['ADA']['IDLE_priority_index'] = 7                                                                                                                          
	GVAR.POOL_markets['ADA']['IDLE_margin_percent'] = 0.52                                                                                                                       
	GVAR.POOL_markets['ADA']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['ADA']['PRICE_BUY_margin'] = 0.0005                                                                                                                        
	GVAR.POOL_markets['ADA']['TRADE_ASSET_amount'] = 1048.1                                                                                                                      
	GVAR.POOL_markets['ADA']['PRICE_SELL_margin'] = 0.0005                                                                                                                       
	GVAR.POOL_markets['ADA']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['ADA']['PRICE_BUY_stop'] = 0.11455                                                                                                                         
	GVAR.POOL_markets['ADA']['PRICE_BUY_limit'] = 0.11505                                                                                                                        
	GVAR.POOL_markets['UNI']['PRICE_IDLE_limit'] = 3.3915                                                                                                                        
	GVAR.POOL_markets['UNI']['IDLE_priority_index'] = 27                                                                                                                         
	GVAR.POOL_markets['UNI']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['UNI']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['UNI']['PRICE_BUY_margin'] = 0.1                                                                                                                           
	GVAR.POOL_markets['UNI']['TRADE_ASSET_amount'] = 34.47                                                                                                                       
	GVAR.POOL_markets['UNI']['PRICE_SELL_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['UNI']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['UNI']['PRICE_BUY_stop'] = 3.3983                                                                                                                          
	GVAR.POOL_markets['UNI']['PRICE_BUY_limit'] = 3.4983                                                                                                                         
	GVAR.POOL_markets['ZIL']['PRICE_IDLE_limit'] = 0.01951                                                                                                                       
	GVAR.POOL_markets['ZIL']['IDLE_priority_index'] = 49                                                                                                                         
	GVAR.POOL_markets['ZIL']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['ZIL']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['ZIL']['PRICE_BUY_margin'] = 0.001                                                                                                                         
	GVAR.POOL_markets['ZIL']['TRADE_ASSET_amount'] = 5867.9                                                                                                                      
	GVAR.POOL_markets['ZIL']['PRICE_SELL_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['ZIL']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['ZIL']['PRICE_BUY_stop'] = 0.01955                                                                                                                         
	GVAR.POOL_markets['ZIL']['PRICE_BUY_limit'] = 0.02055                                                                                                                        
	GVAR.POOL_markets['BNT']['PRICE_IDLE_limit'] = 1.1817                                                                                                                        
	GVAR.POOL_markets['BNT']['IDLE_priority_index'] = 11                                                                                                                         
	GVAR.POOL_markets['BNT']['IDLE_margin_percent'] = 0.32                                                                                                                       
	GVAR.POOL_markets['BNT']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['BNT']['PRICE_BUY_margin'] = 0.01                                                                                                                          
	GVAR.POOL_markets['BNT']['TRADE_ASSET_amount'] = 100.87                                                                                                                      
	GVAR.POOL_markets['BNT']['PRICE_SELL_margin'] = 0.01                                                                                                                         
	GVAR.POOL_markets['BNT']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['BNT']['PRICE_BUY_stop'] = 1.1855                                                                                                                          
	GVAR.POOL_markets['BNT']['PRICE_BUY_limit'] = 1.1955                                                                                                                         
	GVAR.POOL_markets['XRP']['PRICE_IDLE_limit'] = 0.25005                                                                                                                       
	GVAR.POOL_markets['XRP']['IDLE_priority_index'] = 20                                                                                                                         
	GVAR.POOL_markets['XRP']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['XRP']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['XRP']['PRICE_BUY_margin'] = 0.0005                                                                                                                        
	GVAR.POOL_markets['XRP']['TRADE_ASSET_amount'] = 480.3                                                                                                                       
	GVAR.POOL_markets['XRP']['PRICE_SELL_margin'] = 0.0005                                                                                                                       
	GVAR.POOL_markets['XRP']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['XRP']['PRICE_BUY_stop'] = 0.25055                                                                                                                         
	GVAR.POOL_markets['XRP']['PRICE_BUY_limit'] = 0.25105                                                                                                                        
	GVAR.POOL_markets['XMR']['PRICE_IDLE_limit'] = 123.9                                                                                                                         
	GVAR.POOL_markets['XMR']['IDLE_priority_index'] = 6                                                                                                                          
	GVAR.POOL_markets['XMR']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['XMR']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['XMR']['PRICE_BUY_margin'] = 0.5                                                                                                                           
	GVAR.POOL_markets['XMR']['TRADE_ASSET_amount'] = 0.96739                                                                                                                     
	GVAR.POOL_markets['XMR']['PRICE_SELL_margin'] = 0.5                                                                                                                          
	GVAR.POOL_markets['XMR']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['XMR']['PRICE_BUY_stop'] = 124.15                                                                                                                          
	GVAR.POOL_markets['XMR']['PRICE_BUY_limit'] = 124.65                                                                                                                         
	GVAR.POOL_markets['ZEC']['PRICE_IDLE_limit'] = 65.02                                                                                                                         
	GVAR.POOL_markets['ZEC']['IDLE_priority_index'] = 5                                                                                                                          
	GVAR.POOL_markets['ZEC']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['ZEC']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['ZEC']['PRICE_BUY_margin'] = 0.25                                                                                                                          
	GVAR.POOL_markets['ZEC']['TRADE_ASSET_amount'] = 1.84381                                                                                                                     
	GVAR.POOL_markets['ZEC']['PRICE_SELL_margin'] = 0.25                                                                                                                         
	GVAR.POOL_markets['ZEC']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['ZEC']['PRICE_BUY_stop'] = 65.15                                                                                                                           
	GVAR.POOL_markets['ZEC']['PRICE_BUY_limit'] = 65.4                                                                                                                           
	GVAR.POOL_markets['BTS']['PRICE_IDLE_limit'] = 0.02051                                                                                                                       
	GVAR.POOL_markets['BTS']['IDLE_priority_index'] = 57                                                                                                                         
	GVAR.POOL_markets['BTS']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['BTS']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['BTS']['PRICE_BUY_margin'] = 0.001                                                                                                                         
	GVAR.POOL_markets['BTS']['TRADE_ASSET_amount'] = 5595.6                                                                                                                      
	GVAR.POOL_markets['BTS']['PRICE_SELL_margin'] = 0.001                                                                                                                        
	GVAR.POOL_markets['BTS']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['BTS']['PRICE_BUY_stop'] = 0.02055                                                                                                                         
	GVAR.POOL_markets['BTS']['PRICE_BUY_limit'] = 0.02155                                                                                                                        
	GVAR.POOL_markets['TRX']['PRICE_IDLE_limit'] = 0.0271                                                                                                                        
	GVAR.POOL_markets['TRX']['IDLE_priority_index'] = 24                                                                                                                         
	GVAR.POOL_markets['TRX']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['TRX']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['TRX']['PRICE_BUY_margin'] = 0.0005                                                                                                                        
	GVAR.POOL_markets['TRX']['TRADE_ASSET_amount'] = 4361.1                                                                                                                      
	GVAR.POOL_markets['TRX']['PRICE_SELL_margin'] = 0.0005                                                                                                                       
	GVAR.POOL_markets['TRX']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['TRX']['PRICE_BUY_stop'] = 0.02715                                                                                                                         
	GVAR.POOL_markets['TRX']['PRICE_BUY_limit'] = 0.02765                                                                                                                        
	GVAR.POOL_markets['SUSHI']['PRICE_IDLE_limit'] = 0.726                                                                                                                       
	GVAR.POOL_markets['SUSHI']['IDLE_priority_index'] = 44                                                                                                                       
	GVAR.POOL_markets['SUSHI']['IDLE_margin_percent'] = 0.2                                                                                                                      
	GVAR.POOL_markets['SUSHI']['TRADE_mode'] = "VL2"                                                                                                                               
	GVAR.POOL_markets['SUSHI']['PRICE_BUY_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['SUSHI']['TRADE_ASSET_amount'] = 164.734                                                                                                                   
	GVAR.POOL_markets['SUSHI']['PRICE_SELL_margin'] = 0.005                                                                                                                      
	GVAR.POOL_markets['SUSHI']['MARKET_enabled'] = True                                                                                                                          
	GVAR.POOL_markets['SUSHI']['PRICE_BUY_stop'] = 0.727                                                                                                                         
	GVAR.POOL_markets['SUSHI']['PRICE_BUY_limit'] = 0.732                                                                                                                        
	GVAR.POOL_markets['LTC']['PRICE_IDLE_limit'] = 51.45                                                                                                                         
	GVAR.POOL_markets['LTC']['IDLE_priority_index'] = 26                                                                                                                         
	GVAR.POOL_markets['LTC']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['LTC']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['LTC']['PRICE_BUY_margin'] = 0.25                                                                                                                          
	GVAR.POOL_markets['LTC']['TRADE_ASSET_amount'] = 2.3279                                                                                                                      
	GVAR.POOL_markets['LTC']['PRICE_SELL_margin'] = 0.25                                                                                                                         
	GVAR.POOL_markets['LTC']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['LTC']['PRICE_BUY_stop'] = 51.55                                                                                                                           
	GVAR.POOL_markets['LTC']['PRICE_BUY_limit'] = 51.8                                                                                                                           
	GVAR.POOL_markets['SRM']['PRICE_IDLE_limit'] = 1.3488                                                                                                                        
	GVAR.POOL_markets['SRM']['IDLE_priority_index'] = 29                                                                                                                         
	GVAR.POOL_markets['SRM']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['SRM']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['SRM']['PRICE_BUY_margin'] = 0.01                                                                                                                          
	GVAR.POOL_markets['SRM']['TRADE_ASSET_amount'] = 88.57                                                                                                                       
	GVAR.POOL_markets['SRM']['PRICE_SELL_margin'] = 0.01                                                                                                                         
	GVAR.POOL_markets['SRM']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['SRM']['PRICE_BUY_stop'] = 1.3515                                                                                                                          
	GVAR.POOL_markets['SRM']['PRICE_BUY_limit'] = 1.3615                                                                                                                         
	GVAR.POOL_markets['ALGO']['PRICE_IDLE_limit'] = 0.3069                                                                                                                       
	GVAR.POOL_markets['ALGO']['IDLE_priority_index'] = 9                                                                                                                         
	GVAR.POOL_markets['ALGO']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['ALGO']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['ALGO']['PRICE_BUY_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['ALGO']['TRADE_ASSET_amount'] = 385.87                                                                                                                     
	GVAR.POOL_markets['ALGO']['PRICE_SELL_margin'] = 0.005                                                                                                                       
	GVAR.POOL_markets['ALGO']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['ALGO']['PRICE_BUY_stop'] = 0.3075                                                                                                                         
	GVAR.POOL_markets['ALGO']['PRICE_BUY_limit'] = 0.3125                                                                                                                        
	GVAR.POOL_markets['BTC']['PRICE_IDLE_limit'] = 11702.55                                                                                                                      
	GVAR.POOL_markets['BTC']['IDLE_priority_index'] = 1                                                                                                                          
	GVAR.POOL_markets['BTC']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['BTC']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['BTC']['PRICE_BUY_margin'] = 5                                                                                                                             
	GVAR.POOL_markets['BTC']['TRADE_ASSET_amount'] = 0.010279                                                                                                                    
	GVAR.POOL_markets['BTC']['PRICE_SELL_margin'] = 5                                                                                                                            
	GVAR.POOL_markets['BTC']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['BTC']['PRICE_BUY_stop'] = 11726.0                                                                                                                         
	GVAR.POOL_markets['BTC']['PRICE_BUY_limit'] = 11731.0                                                                                                                        
	GVAR.POOL_markets['WAVES']['PRICE_IDLE_limit'] = 3.1751                                                                                                                      
	GVAR.POOL_markets['WAVES']['IDLE_priority_index'] = 15                                                                                                                       
	GVAR.POOL_markets['WAVES']['IDLE_margin_percent'] = 0.2                                                                                                                      
	GVAR.POOL_markets['WAVES']['TRADE_mode'] = "VL2"                                                                                                                               
	GVAR.POOL_markets['WAVES']['PRICE_BUY_margin'] = 1                                                                                                                           
	GVAR.POOL_markets['WAVES']['TRADE_ASSET_amount'] = 28.84                                                                                                                     
	GVAR.POOL_markets['WAVES']['PRICE_SELL_margin'] = 1                                                                                                                          
	GVAR.POOL_markets['WAVES']['MARKET_enabled'] = True                                                                                                                          
	GVAR.POOL_markets['WAVES']['PRICE_BUY_stop'] = 3.1815                                                                                                                        
	GVAR.POOL_markets['WAVES']['PRICE_BUY_limit'] = 4.1815                                                                                                                       
	GVAR.POOL_markets['LINK']['PRICE_IDLE_limit'] = 10.9763                                                                                                                      
	GVAR.POOL_markets['LINK']['IDLE_priority_index'] = 3                                                                                                                         
	GVAR.POOL_markets['LINK']['IDLE_margin_percent'] = 0.32                                                                                                                      
	GVAR.POOL_markets['LINK']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['LINK']['PRICE_BUY_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['LINK']['TRADE_ASSET_amount'] = 10.85                                                                                                                      
	GVAR.POOL_markets['LINK']['PRICE_SELL_margin'] = 0.1                                                                                                                         
	GVAR.POOL_markets['LINK']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['LINK']['PRICE_BUY_stop'] = 11.0115                                                                                                                        
	GVAR.POOL_markets['LINK']['PRICE_BUY_limit'] = 11.1115                                                                                                                       
	GVAR.POOL_markets['CREAM']['PRICE_IDLE_limit'] = 35.683                                                                                                                      
	GVAR.POOL_markets['CREAM']['IDLE_priority_index'] = 56                                                                                                                       
	GVAR.POOL_markets['CREAM']['IDLE_margin_percent'] = 0.2                                                                                                                      
	GVAR.POOL_markets['CREAM']['TRADE_mode'] = "VL2"                                                                                                                               
	GVAR.POOL_markets['CREAM']['PRICE_BUY_margin'] = 0.25                                                                                                                        
	GVAR.POOL_markets['CREAM']['TRADE_ASSET_amount'] = 3.349                                                                                                                     
	GVAR.POOL_markets['CREAM']['PRICE_SELL_margin'] = 0.25                                                                                                                       
	GVAR.POOL_markets['CREAM']['MARKET_enabled'] = True                                                                                                                          
	GVAR.POOL_markets['CREAM']['PRICE_BUY_stop'] = 35.755                                                                                                                        
	GVAR.POOL_markets['CREAM']['PRICE_BUY_limit'] = 36.005                                                                                                                       
	GVAR.POOL_markets['AVA']['PRICE_IDLE_limit'] = 0.6043                                                                                                                        
	GVAR.POOL_markets['AVA']['IDLE_priority_index'] = 41                                                                                                                         
	GVAR.POOL_markets['AVA']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['AVA']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['AVA']['PRICE_BUY_margin'] = 0.005                                                                                                                         
	GVAR.POOL_markets['AVA']['TRADE_ASSET_amount'] = 197.52                                                                                                                      
	GVAR.POOL_markets['AVA']['PRICE_SELL_margin'] = 0.005                                                                                                                        
	GVAR.POOL_markets['AVA']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['AVA']['PRICE_BUY_stop'] = 0.6055                                                                                                                          
	GVAR.POOL_markets['AVA']['PRICE_BUY_limit'] = 0.6105                                                                                                                         
	GVAR.POOL_markets['SNX']['PRICE_IDLE_limit'] = 4.223                                                                                                                         
	GVAR.POOL_markets['SNX']['IDLE_priority_index'] = 16                                                                                                                         
	GVAR.POOL_markets['SNX']['IDLE_margin_percent'] = 0.2                                                                                                                        
	GVAR.POOL_markets['SNX']['TRADE_mode'] = "VL2"                                                                                                                                 
	GVAR.POOL_markets['SNX']['PRICE_BUY_margin'] = 0.1                                                                                                                           
	GVAR.POOL_markets['SNX']['TRADE_ASSET_amount'] = 27.842                                                                                                                      
	GVAR.POOL_markets['SNX']['PRICE_SELL_margin'] = 0.1                                                                                                                          
	GVAR.POOL_markets['SNX']['MARKET_enabled'] = True                                                                                                                            
	GVAR.POOL_markets['SNX']['PRICE_BUY_stop'] = 4.231                                                                                                                           
	GVAR.POOL_markets['SNX']['PRICE_BUY_limit'] = 4.331                                                                                                                          
	GVAR.POOL_markets['VTHO']['PRICE_IDLE_limit'] = 0.000724                                                                                                                     
	GVAR.POOL_markets['VTHO']['IDLE_priority_index'] = 59                                                                                                                        
	GVAR.POOL_markets['VTHO']['IDLE_margin_percent'] = 0.2                                                                                                                       
	GVAR.POOL_markets['VTHO']['TRADE_mode'] = "VL2"                                                                                                                                
	GVAR.POOL_markets['VTHO']['PRICE_BUY_margin'] = 1e-05                                                                                                                        
	GVAR.POOL_markets['VTHO']['TRADE_ASSET_amount'] = 164061.286                                                                                                                 
	GVAR.POOL_markets['VTHO']['PRICE_SELL_margin'] = 1e-05                                                                                                                       
	GVAR.POOL_markets['VTHO']['MARKET_enabled'] = True                                                                                                                           
	GVAR.POOL_markets['VTHO']['PRICE_BUY_stop'] = 0.000725                                                                                                                       
	GVAR.POOL_markets['VTHO']['PRICE_BUY_limit'] = 0.000735
	
	bprint("Backup done")
	bprint("")

	"""create_test_order_resp = client.create_test_order(
			timeInForce=TIME_IN_FORCE_GTC,
	symbol=gvar_symbol,
			type=ORDER_TYPE_LIMIT,
	side=SIDE_BUY,
	quantity=gvar_start_buy_amount,
	price=str(gvar_start_buy_price)
			)

	order_created_ok = False

	create_buy_order_resp = client.order_oco_buy(
	stopLimitTimeInForce='GTC', symbol=gvar_symbol, stopPrice=gvar_start_buy_price,
	stopLimitPrice=tmp_stop_limit_price, quantity=gvar_start_buy_amount, newOrderRespType='JSON')"""

	#print "[BOT] SERVER CREATE ORDER RESPONSE: " + json.dumps(parsed_order_data, indent=4, sort_keys=True)
