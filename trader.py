import keys
import GVAR
from GLOBALS import GSTRING
import defs

from time import sleep

from GVAR import *
from defs import *

def TRADER_main () :

	defName = "TRADER_main: "
	
	GVAR.TRADER_enabled = True
	GVAR.TRADER_paused = False

	MODE_load("VL2")

	bprint(defName + "Starting TRADER loop..")

	while (GVAR.TRADER_enabled == True) :

		tradeMarketName = GVAR.TRADER_marketName
		
		#bprint(defName + "<<< STATUS >>> GVAR.TRADER_mode == " + str(GVAR.TRADER_mode) + " | GVAR.TRADE_mode_on == " + str(GVAR.TRADE_mode_on) + " | GVAR.TRADER_marketName == None -> Do nothing")

		if (tradeMarketName == None) :

			# This IF is only for protection against wrong synchro of variables
			# In case TRADER_mode != "" GVAR.TRADER_marketName == None -> Do nothing
			# There has been cases when TRADER loop tries to start BUY loop without any marketName assigned

			if (GVAR.TRADER_mode != None) :
				
				bprint(defName + "<<< WARNING >>> GVAR.TRADER_mode == " + str(GVAR.TRADER_mode) + " | GVAR.TRADE_mode_on == " + str(GVAR.TRADE_mode_on) + " | GVAR.TRADER_marketName == None -> Do nothing")

		else :

			# Use chain of IFs (not elif) to avoid having to wait a whole MICRO_SLEEP() while LOOP in phase changes
			# IFs should be ordered following TRADE phase changes
			
			if (GVAR.TRADER_paused == False) :

				if(GVAR.TRADER_mode == "BUY") :

					bprint(defName + ">>> DEBUG at here pos 1 -> GVAR.BUY_mode_on = " + str(GVAR.BUY_mode_on) + " | GVAR.SELL_mode_on = " + str(GVAR.SELL_mode_on) + " | GVAR.TRADE_abort = " + str(GVAR.TRADE_abort))

					if(GVAR.BUY_mode_on == False) & (GVAR.SELL_mode_on == False) & (GVAR.TRADE_abort == False):

						bprint(defName + "TRADER_mode == BUY detected -> Runing TRADER_buy(" + tradeMarketName + ")")				

						GVAR.POOL_markets[tradeMarketName]['MARKET_status'] = "TRADING"
						tradeMode = GVAR.POOL_markets[tradeMarketName]['TRADE_mode']
						GVAR.MODE_load(tradeMode)

						#GVAR.STATISTICS_TICKER_cache_rightest_peak = None
						#GVAR.STATISTICS_TICKER_cache_rightest_peak_found = False
						GVAR.SELL_CFB_lnMP_max_limit = 0
						GVAR.SELL_CFB_lnMP_max_value = 0

						bprint(defName + "MODE Name = " + GVAR.MODE_VARS.MODE_name )
						#bprint(defName + "MODE BUY_CFA_margin_percent_default = " + str(GVAR.MODE_VARS.BUY_CFA_margin_percent_default) )
						#bprint(defName + "MODE SELL_CFB_margin_percent_default = " + str(GVAR.MODE_VARS.SELL_CFB_margin_percent_default) )
						bprint(defName + "MODE SELL_CFB_lnMP_limits = " + str(GVAR.MODE_VARS.SELL_CFB_lnMP_limits) )
						bprint(defName + "MODE SELL_CFB_lnMP_values = " + str(GVAR.MODE_VARS.SELL_CFB_lnMP_values) )
						bprint("")

						GVAR.TRADE_mode_on = True
						GVAR.BUY_mode_on = True
						# Call TRADER_buy with already set (by POOL_monitor) highest priority market
						TRADER_buy(tradeMarketName)

				if(GVAR.TRADER_mode == "BUY_FILLED") :

					bprint(defName + "TRADER_mode == BUY_FILLED detected -> BUY order was filled at price [ PRICE_BUY_limit : " + str(GVAR.TRADE_price_fill) + " ]")
					bprint(defName + "Setting vars to start SELL mode for market " + str(tradeMarketName) + " ..")

					fData = POOL_marketGetLastFillData(tradeMarketName, "BUY")
					GVAR.TRADE_price_fill = float(fData['fillPrice'])
					GVAR.TRADE_amount_bought = float(fData['totalQty'])					

					GVAR.TRADER_mode = "SELL"
					GVAR.BUY_mode_on = False
					GVAR.SELL_mode_on = False
					GVAR.TRADE_abort = False
					GVAR.TRADE_mode_on = True					

					TRADER_LOG_trade(tradeMarketName, "BUY")

				if(GVAR.TRADER_mode == "SELL") :

					bprint(defName + ">>> DEBUG at here pos 3")

					if(GVAR.BUY_mode_on == False) & (GVAR.SELL_mode_on == False) :
					
						tradeMarketName = GVAR.TRADER_marketName
						TRADER_sell(tradeMarketName)

				if(GVAR.TRADER_mode == "SELL_FILLED") :

					bprint(defName + "Mode 4: TRADER_mode == SELL_FILLED detected -> Trade FINISHED OK -> Reseting variables and Market STOP, LIMIT, IDLE prices..")

					fData = POOL_marketGetLastFillData(tradeMarketName, "SELL")
					GVAR.TRADE_price_end = float(fData['fillPrice'])
					GVAR.TRADE_amount_sold = float(fData['totalQty'])

					GVAR.TRADER_mode = None
					GVAR.BUY_mode_on = False
					GVAR.SELL_mode_on = False
					GVAR.TRADE_abort = False
					GVAR.TRADE_mode_on = False

					TRADER_LOG_trade(tradeMarketName,"SELL")

					# This function determines wheter if new BUY STOP, LIMIT, IDLE prices have to be re-calculated or not
					# depending the way this last trade finished, before re-enabling the market to be monitored again by POOL_monitor
					POOL_marketTradeFinisher(GVAR.TRADER_marketName)
					
				if(GVAR.TRADER_mode == "LOAD_SELL_ORDER") :

					a = 1
					#TRADER_load()

				if(GVAR.TRADER_mode == "ABORT_BUY") :

					bprint("")
					bprint(defName + "Mode ABORT_BUY: detected")
					bprint(defName + "Mode ABORT_BUY: STEP 1.01 -> Cancel current trade open BUY order ID: " + str(GVAR.TRADE_orderId))

					MARKET_data = POOL_marketGetData(tradeMarketName)
					MARKET_symbol = MARKET_data['MARKET_symbol']

					resp = EXCHANGE_ORDER_Cancel(MARKET_symbol, GVAR.TRADE_orderId)
					bprint(defName + "Retrieving cancelation data..")
					respOrderId = resp.get('orderId')

					if (respOrderId == 0) :

						# Order cancelation FAILED (probably FILLED before canceling due to sudden price moves)
						# If order returned FILLED -> Jump to SELL mode

						bprint(defName + "BUY Order was FILLED before ABORT process -> Go into SELL mode with GVAR.TRADER_mode = BUY_FILLED")
						
						GVAR.BUY_mode_on = False
						GVAR.TRADER_mode = "BUY_FILLED"

					else :
						
						# If order canceling was succesfull -> reset the other variables
						GVAR.TRADER_mode = None
						GVAR.TRADER_marketName = None
						GVAR.TRADE_abort = False
						GVAR.BUY_mode_on = False
						GVAR.SELL_mode_on = False

						# Enable POOL monitor to order new BUY
						GVAR.TRADE_mode_on = False

						priceMarket = float(MARKET_data['PRICE_market'])
						priceIdleLimit = float(MARKET_data['PRICE_IDLE_limit'])
						
						if(priceMarket >= priceIdleLimit) :
							
							# If ABORT_BUY signal was sent with priceMarket >= priceIdleLimit -> Disable MARKET
							# If it is not disabled before going back to POOL monitoring it will RE-ENTER trading instantly
							# This will happen because MARKET price is still in IDLE margin -> READY status would by asidned instantly -> TRADING would restart 
							bprint(defName + "Mode ABORT_BUY: Price still in IDLE margin -> Disabling market: " + tradeMarketName + " to avoid instant re-trading.. ")
							POOL_marketSetEnabled(tradeMarketName, False)

						POOL_marketSetStatus(tradeMarketName, "IDLE")
						POOL_marketSetEnabled(tradeMarketName, True)

						bprint(defName + "Mode ABORT_BUY: IDLE mode set for market " + tradeMarketName + " back to POOL monitoring..")
						bprint("")

				if(GVAR.TRADER_mode == "ABORT_SELL") :

					bprint(defName + "Mode 6: TRADER_mode == ABORT_SELL detected")
					
					MARKET_data = POOL_marketGetData(tradeMarketName)
					MARKET_symbol = MARKET_data['MARKET_symbol']
					
					bprint(defName + "STEP 1.02 -> Cancel current trade open BUY order ID: " + str(GVAR.TRADE_orderId))
					resp = EXCHANGE_ORDER_Cancel(MARKET_symbol, GVAR.TRADE_orderId)

					if (resp != "0") :
						
						# If order canceling was succesfull -> reset the other variables
						GVAR.TRADER_mode = None
						GVAR.TRADER_marketName = None
						GVAR.TRADE_abort = False
						GVAR.BUY_mode_on = False
						GVAR.SELL_mode_on = False

						# Enable POOL monitor to order new BUY
						GVAR.TRADE_mode_on = False

						bprint("")
						bprint(defName + "<<< WARNING >>> ASSET SELLING on trade SELL abort NOT IMPLEMETED -> FIX THIS")
						bprint(defName + "<<< WARNING >>> ASSET SELLING on trade SELL abort NOT IMPLEMETED -> FIX THIS")
						bprint(defName + "<<< WARNING >>> ASSET SELLING on trade SELL abort NOT IMPLEMETED -> FIX THIS")
						bprint(defName + "<<< WARNING >>> No funds will be available for next trade!!!")
						bprint("")

						POOL_marketSetEnabled(tradeMarketName, False)

		THREADS_aliveSignal("TRADER_main")

		MICRO_sleep(0.5)

	#==================

def TRADER_buy (PARAM_marketName) :

	defName = "TRADER_buy: "
 
	marketName = PARAM_marketName


	MARKET_data = POOL_marketGetData(marketName)
	marketSymbol = MARKET_data['MARKET_symbol']
	priceMarket = MARKET_data["PRICE_market"]
	priceStop = MARKET_data['PRICE_BUY_stop']
	priceLimit = MARKET_data['PRICE_BUY_limit']
	assetAmount = MARKET_data['TRADE_ASSET_amount']

	bprint(defName + "Initializing BUY with market: " + str(marketName) + " -> MARKET_symbol = " + str(marketSymbol))


	GVAR.TRADE_mode_on = True
	GVAR.BUY_mode_on = True
	GVAR.SELL_mode_on = False
	GVAR.BUY_AWT_enabled = False
	GVAR.TRADE_abort = False

	GVAR.TRADE_orderId = 0
	resp = POOL_marketCreateStopLimitOrder(marketName, "BUY")
	GVAR.TRADE_orderId = resp['orderId']

	#If order creation succedeed -> GVAR.TRADE_orderId > 0 -> do stuff
	if(GVAR.TRADE_orderId > 0) :
		
		# ==============================================================
		# CAMBIAR TODAS LAS TECLAS DEL MOVER A COMANDOS DEL cmdline
		# ==============================================================
		#if(GVAR.MOVER_enabled == False) :
		#	GVAR.MOVER_enabled = True
		#	MOVER_start()

		bprint(defName + "ORDER CREATED - NEW ORDER ID: " + str(GVAR.TRADE_orderId))
		str1 =  "BUY MODE ON > SYMBOL: " + marketSymbol
		str2 =  " - Waiting BUY order to complete at price " + str(priceStop) + " " + GVAR.SELL_symbol
		bprint(defName + str1 + str2)
		bprint("")

		while(GVAR.BUY_mode_on == True) :

			MARKET_data = POOL_marketGetData(marketName)

			marketSymbol = str(MARKET_data['MARKET_symbol'])
			sellSymbol = str(MARKET_data['SELL_symbol'])
			priceMarket = MARKET_data["PRICE_market"]
			priceStop = MARKET_data['PRICE_BUY_stop']
			priceLimit = MARKET_data['PRICE_BUY_limit']
			priceIdleLimit = MARKET_data['PRICE_IDLE_limit']

			#if(GVAR.FLAG_SOUND_mode_on == True) :
			#	os.system("afplay " + GVAR.BOT_SOUNDS_DIR + "/idle.mp3")
			
			# If while waiting for order to get FILLED a highest priority market set as ready -> Abort and enable highest priority market
			nextMarketName = None
			nextMarketName = POOL_prioRanker(0,False)
			currentMarketPrio = int(MARKET_data['IDLE_priority_index'])
			
			if (nextMarketName != None) :
				
				# bprint(defName + "POOL_prioRanker(0,False) returned " + str(nextMarketName) + " -> Compare priority with current market (" + marketName + ", " + str(currentMarketPrio) + ")")
				nextMarketData = POOL_marketGetData(nextMarketName)
				nextMarketPrio = nextMarketData['IDLE_priority_index']

				if(currentMarketPrio > nextMarketPrio) :
					
					bprint(defName + "Next market (" + nextMarketName + ", " + str(nextMarketPrio) + ") priority is higher than current trading market (" + marketName + ", " + str(currentMarketPrio) + ")")
					GVAR.BUY_mode_on = False
					GVAR.TRADER_mode = "ABORT_BUY"
					
					break
									
			# IDLE LIMIT CHECKER (if price goes below IDLE limit cancel order and go back to IDLE mode)
			if (float(priceMarket) < float(priceIdleLimit)) :

				# Check if the order STILL there (unfilled) then cancel it
				# Sometimes order fills in high volatility and prices goes under IDLE limit (tries to go back to IDLE but SERVER already bought)
				bprint("")
				bprint(defName + "[ MARKET price: " + str(priceMarket) + " " + sellSymbol + " ] < (BELOW) IDLE limit [ GVAR.IDLE_price_limit = " + str(GVAR.IDLE_price_limit) + " " + sellSymbol + " ]")
				bprint(defName + "Trying to check status for order id: " + marketSymbol + " " + str(GVAR.TRADE_orderId) )

				order_data = EXCHANGE_ORDER_GetStatus(GVAR.TRADE_orderId, marketSymbol)
				order_status = str(order_data['status'])

				if (order_status == "FILLED") :
		
					bprint(defName + "Order was FILLED before price drop -> Start SELL mode")

					GVAR.BUY_mode_on = False					
					GVAR.TRADER_mode = "BUY_FILLED"
					
					#BUYCHECK_CreateBuyCheck()
					#if(GVAR.FLAG_SOUND_mode_on == True) :
					#	os.system("afplay " + GVAR.BOT_SOUNDS_DIR +  "/fill.mp3")
					
					break

				elif (order_status == "NEW") :

					bprint(defName + "Price too LOW and BUY order never filled -> ABORT trade and go back to IDLE mode..")

					GVAR.BUY_mode_on = False
					GVAR.TRADER_mode = "ABORT_BUY"

					#bprint(defName + "Unlocking TRADE (BUY mode) .. ")
					#IDLE_ORDER_UnLock()
				
					break

				else :

					bprint(defName + "Order status unknown (" + str(order_status) + ")") 
					bprint(defName + pcolors.RED + "ERROR:" + pcolors.ENDC + " Unknown status -> Exiting Main Loop")
					bprint("")

					quit()

				#=====================================================
				# Price Checks
				#=====================================================
				
			if (float(priceMarket) >= float(priceStop)) :

					bprint("")
					nowStr = TIME_getNowTime()

					bprint(defName + "BUY Loop: STOP BUY Price " + str(priceStop) + " reached at [ " + str(nowStr) + " " + str(priceMarket) + " ] -> Cheking if BUY order got FILLED..")
					
					resp_status = ""
					break_main_loop = False

					tries_count = 0
					max_tries = 5

					# Loop to wait while order is getting FULL filled
					while resp_status != "FILLED" :

						bprint(defName + "BUY Loop: Checking status for order id: " + str(GVAR.TRADE_orderId))

						resp_get_status = EXCHANGE_ORDER_GetStatus (GVAR.TRADE_orderId, marketSymbol)
						resp_status = str(resp_get_status['status'])

						if (resp_status == "FILLED") :

							tries_count = 0
							
							bprint(defName + "BUY Loop: Order Filled -> Start SELL mode")
							bprint("")

							#BUYCHECK_CreateBuyCheck()

							break_main_loop = True

							break

						elif (resp_status == "NEW") : 

							bprint(defName + "(PRICE market > STOP) -> Status check returned: " + str(resp_status) + " -> Partially Filled ?? -> Going back to main BUY loop ..")
							break

						else :

							tries_count += 1

							bprint(defName + "BUY Loop: Status check returned: " + str(resp_status) + " -> Order NOT Filled -> Retrying... Tries left " + str(max_tries - tries_count))

							if(tries_count == max_tries) :

								bprint(defName + "BUY Loop: Too many tries -> Aborting TRADE")
								bprint("")
								
								GVAR.BUY_mode_on = False
								GVAR.TRADER_mode = "ABORT_BUY"

								#bprint(defName + "BUY Loop: Unlocking TRADE (BUY mode) .. ")
								#IDLE_ORDER_UnLock()

								break

						bprint("")
						MICRO_sleep(GVAR.TICKER_sleep)

					if (break_main_loop == True) :

						GVAR.BUY_mode_on = False
						bprint(defName + "break_main_loop == True -> Ending BUY main loop..")

						GVAR.TRADER_mode = "BUY_FILLED"
						
						#GVAR.SELL_mode_on = True
						#if(GVAR.FLAG_SOUND_mode_on == True) :
						#	os.system("afplay " + GVAR.BOT_SOUNDS_DIR + "/fill.mp3")

						break

			#=====================================================
			# Print Trade Output to screen
			#=====================================================
			BUY_printTradeLine(marketName, priceStop, priceMarket, "")

			THREADS_aliveSignal("TRADER_main")

			MICRO_sleep(GVAR.TICKER_sleep)
				
			EXCHANGE_ORDER_StatusSync("BUY", False, defName)
	#==============================================================================

def TRADER_sell (PARAM_marketName) :

	defName = "TRADER_sell: "

	marketName = PARAM_marketName

	MARKET_data = POOL_marketGetData(marketName)
	marketSymbol = str(MARKET_data['MARKET_symbol'])
	sellSymbol = str(MARKET_data['SELL_symbol'])
	priceMarket = MARKET_data["PRICE_market"]
	priceRounder = int(MARKET_data['TRADE_round_prices'])
	assetAmount = float(MARKET_data['TRADE_ASSET_amount'])
	priceSellMargin = MARKET_data["PRICE_SELL_margin"]

	GVAR.TRADE_mode_on = True
	GVAR.BUY_mode_on = False
	GVAR.SELL_mode_on = True
	GVAR.BUY_AWT_enabled = False
	GVAR.TRADE_abort = False

	GVAR.SELL_CFB_margin_percent = GVAR.MODE_VARS.SELL_CFB_margin_percent_default

	bprint(defName + "Creating first SELL order.. ")

	new_order_data = POOL_CFB_updateSellOrder(marketName)
	sell_new_orderId = new_order_data['orderId']

	bprint(defName + "SELL order creation confirmed -> New order ID: " + str(sell_new_orderId))
	bprint(defName + "SELL Loop CFB: SELL CFB mode ON -> Starting SELL loop..")
	bprint("")

	fullFill_tries_max = 11
	fullFill_tries_counter = 0

	SELL_CFB_label_set("CFB","")
	stats_str = ""
	
	while (GVAR.SELL_mode_on == True ) :

		MARKET_data = POOL_marketGetData(marketName)
		priceMarket = MARKET_data["PRICE_market"]
		priceSellStop = MARKET_data["PRICE_SELL_stop"]
		priceSellLimit = MARKET_data["PRICE_SELL_limit"]

		# Step 1: Calc earnings %
		earnings_percent = round(calcPriceDistancePercent(float(GVAR.TRADE_price_fill), float(priceMarket)),2)
		# Step 2: Update CFB_margin_percent from logCFB values according to earnings %
		GVAR.SELL_CFB_margin_percent = SELL_CFB_CalcLogarithmicMarginPercent(earnings_percent)
		# Step 3: Check if current STOP price is correct with current CFB_margin_percent and current MARKET price
		#         If not -> Updates STOP price -> Also returns SELL order current status
		orderStatus = SELL_CFB_StopPriceIncreaser (marketName, priceSellStop, GVAR.SELL_CFB_margin_percent)

		if(orderStatus == "FILLED") :

			bprint ("SELL_CFB_Loop(SECTOR 1): Price increase aborted -> Order status sync returned FILLED -> END TRADE (order was FILLED before SELL STOP increase signal)")
			
			GVAR.SELL_mode_on = False
			#GVAR.BUY_mode_on = False
			#GVAR.BUY_fixed_price_enabled = False
			GVAR.TRADER_mode = "SELL_FILLED"
			
			break

		if ( float(priceMarket) <= float(priceSellStop) ) :

			bprint(defName + "SELL_CFB_Loop(SECTOR 2): STOP LOSS price : "  + str(priceSellStop) + " reached at " + TIME_getNowTime() + " -> MARKET price: " + str(priceMarket) + " "  + str(sellSymbol))
			bprint(defName + "SELL_CFB_Loop(SECTOR 2): Checking if orderId: " + str(GVAR.TRADE_orderId) + " status is FILLED to set current trade as FINISHED..")
			
			tmpResp = EXCHANGE_ORDER_GetStatus(GVAR.TRADE_orderId, marketSymbol)
			tmpStatus = tmpResp['status']
			
			if(tmpStatus == "FILLED") :
				
				GVAR.SELL_mode_on = False
				GVAR.TRADER_mode = "SELL_FILLED"

				bprint(defName + "SELL_CFB_Loop(SECTOR 2): Order Status: " + str(tmpStatus) + " -> FINISHING trade")
				break
			
			else :

				fullFill_tries_counter += 1
				bprint(defName + "SELL_CFB_Loop(SECTOR 2): Order Status: " + str(tmpStatus) + " -> Waiting order to full-fill (tries: " + str(fullFill_tries_counter) + "/" + str(fullFill_tries_max) + ")")
				bprint("")

				if(fullFill_tries_counter > fullFill_tries_max) :

					logprint(GVAR.LOG_WARNINGS_name, "")
					logprint(GVAR.LOG_WARNINGS_name, defName + "<<< WARNING >>> FULL Fill tries tries > " + str(fullFill_tries_max) + " -> Price must have go below SELL LIMIT price without a complete SELL")
					logprint(GVAR.LOG_WARNINGS_name, defName + "<<< WARNING >>> Try increasing market " + marketName + " (actual) PRICE_SELL_margin = " + str(priceSellMargin) + ")")
					logprint(GVAR.LOG_WARNINGS_name, defName + "<<< WARNING >>> [ Market: " + str(marketName) + " ] [ MARKET_price: " + str(priceMarket) + " ] [ PRICE_BUY_stop: " + str(priceSellStop) + " ] -> Will attemp SELL order FIX")
					logprint(GVAR.LOG_WARNINGS_name, "")
					
					bprint(defName + "SELL_CFB_Loop(SECTOR 2): Calling POOL_orderFixer using exception: " + GVAR.TRADE_EXCEPTIONS_SELL_e1)
					
					resp = POOL_orderFixer(marketName, "SELL", GVAR.TRADE_EXCEPTIONS_SELL_e1)
					new_order_Id = float(resp['orderId'])
					new_order_PriceStop = float(resp['priceStop'])
					new_order_PriceLimit = float(resp['priceLimit'])
					
					if(new_order_Id > 0) :
						bprint(defName + "SELL_CFB_Loop(SECTOR 2): SELL order FIX was sucessfull -> New SELL order STOP = " + str(new_order_PriceStop) + " " + sellSymbol + " LIMIT = " + str(new_order_PriceLimit) + " " + sellSymbol)	
						fullFill_tries_counter = 0
						bprint(defName + "SELL_CFB_Loop(SECTOR 2): Reset tries counter -> fullFill_tries_counter = 0")
					else :
						bprint(defName + "<<< ERROR >>> SELL order FIX FAILED")

		if (GVAR.TRADE_abort == True) :
			
			bprint(defName + "SELL_CFB_Loop(Abort) -> Abort signal received -> Canceling SELL Order")
			EXCHANGE_ORDER_Cancel(marketSymbol, GVAR.TRADE_orderId)
			bprint(defName + "SELL_CFB_Loop(Abort) -> Exiting SELL Loop")
			
			GVAR.TRADER_mode = "ABORT"
			GVAR.BUY_mode_on = False
			GVAR.SELL_mode_on = False

			bprint("SELL_CFB_Loop(Abort) Unlocking TRADE (ABORT signal in SELL mode) .. ")
			#IDLE_ORDER_UnLock()

			break

		SELL_printTradeLine(marketName, GVAR.TRADE_price_fill, priceMarket, stats_str)
		
		MICRO_sleep(GVAR.TICKER_sleep)
		
		THREADS_aliveSignal("TRADER_main")

		EXCHANGE_ORDER_StatusSync("SELL", False, defName)
		
def TRADER_abort (PARAM_marketName) :

	a = 1

def TRADER_calcResult () :

	if (GVAR.TRADE_abort == False) :

		trade_end_fee_symbol = GVAR.TRADE_FEE_symbol + GVAR.SELL_symbol
		if (GVAR.SIMULATOR_TICKER == True) :
			# If full simulation mode is ON (simulated TICKER price is ON -> fast CPU process speeds) use fake-fixed data for fees
			FEE_data = BNB_SIMULATED_data
		else :
			FEE_data = BINANCE_TICKER_GetTickerData(trade_end_fee_symbol)

		GVAR.TRADE_FEE_price = float(FEE_data['bidPrice'])
		trade_end_fee = round(GVAR.TRADE_FEE_amount * GVAR.TRADE_FEE_price,5)
		trade_end_fee_str = str(trade_end_fee_symbol) + " " + GVAR.SELL_symbol

		bprint("")
		bprint("")
		bprint("Main Loop: Getting FEE Price: 1 BNB = " + str(GVAR.TRADE_FEE_price) + " " + GVAR.SELL_symbol)
		
		
		trade_end_diff = GVAR.TRADE_price_end - GVAR.TRADE_price_fill
		trade_end_diff_percent = round(100 - (float(GVAR.TRADE_price_fill * 100) / float(GVAR.TRADE_price_end)),5)

		
		trade_end_sell_str = "[ SELL price " + str(GVAR.TRADE_price_end) + " " + GVAR.SELL_symbol + " ]"
		trade_end_buy_str = "[ BUY price +  " + str(GVAR.TRADE_price_fill) + " " + GVAR.SELL_symbol + " ]"
		trade_end_diff_str = str(trade_end_diff) + " " + GVAR.SELL_symbol

		trade_end_earnings = round((trade_end_diff) * GVAR.SELL_amount,5)
		trade_end_earnings_str = str(trade_end_earnings) +  " " + GVAR.SELL_symbol

		trade_end_balance = float(trade_end_earnings) - float(trade_end_fee)
		trade_end_color = pcolors.GREEN
		if (trade_end_balance < 0) :
			trade_end_color = pcolors.RED

		trade_end_balance_str = str(trade_end_balance) +  " " + GVAR.SELL_symbol

		GVAR.STATISTICS_trades_counter += 1

		GVAR.STATISTICS_trades_results_earnings.append(round(trade_end_earnings,5))
		GVAR.STATISTICS_trades_results_earnings_percents.append(round(trade_end_diff_percent,5))
		GVAR.STATISTICS_trades_results_balances.append(round(trade_end_balance,5))

		GVAR.STATISTICS_trades_tradeBuyPrices.append(round(GVAR.TRADE_price_fill,5))
		GVAR.STATISTICS_trades_tradeStopPrices.append(round(GVAR.TRADE_price_end,5))

		GVAR.STATISTICS_trades_results_total_earnings += round(trade_end_earnings,5)
		GVAR.STATISTICS_trades_results_total_earnings_percent += round(trade_end_diff_percent,5)
		GVAR.STATISTICS_trades_results_total_balances += round(trade_end_balance,5)

		if (trade_end_balance > 0) :
			GVAR.STATISTICS_trades_results_total_wins += 1
			GVAR.STATISTICS_trades_wins_balances.append(trade_end_balance)
			GVAR.STATISTICS_trades_results_total_wins_sum += trade_end_balance
		else:
			GVAR.STATISTICS_trades_results_total_looses += 1
			GVAR.STATISTICS_trades_looses_balances.append(trade_end_balance)
			GVAR.STATISTICS_trades_results_total_looses_sum += trade_end_balance

		bprint("Main Loop: TRADE ENDED [ " + str(trade_end_diff_percent)  + " % ] " + trade_end_sell_str  + " -  " + trade_end_buy_str + " = " + trade_end_diff_str)
		bprint("Main Loop: TRADE BALANCE [ EARNINGS " + trade_end_earnings_str + " ] - [ FEES " + trade_end_fee_str + " ] = " + trade_end_balance_str)
		bprint("")

		if(GVAR.SIMULATOR_TICKER_debug_stops == True) :
			sleep(10)

	#except Exception as e:
	#	e = sys.exc_info()
		#bprint("")
		#bprint("[BOT] TRADER_Main(): " + pcolors.RED + "ERROR: " + pcolors.ENDC + str(e))
		#bprint("[BOT] TRADER_Main(): " + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Type: " + str(type(e)))
		#bprint("[BOT] TRADER_Main(): " + pcolors.RED + "ERROR: " + pcolors.ENDC + " return T: " + str(e[0]))
		#bprint("[BOT] TRADER_Main(): " + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Type: " + str(e[2]))
		#bprint("[BOT] TRADER_Main(): " + pcolors.RED + "ERROR: " + pcolors.ENDC + " return Type: " + str(traceback.format_tb(e[2]))[-50:])
		#bprint("")

	GVAR.MODE_VERBOSE = True
	printTradesLoopStatistics()

	if (GVAR.SCREEN_enabled == True) :

		# Set cursor = True again before leaving
		curses.curs_set(1)
		curses.endwin()

# ==============================================================

def TRADER_LOG_trade(PARAM_marketName, PARAM_side) :

	defName = "TRADER_LOG_trade: "
	
	logPath = "./" + GVAR.TRADER_logsDir + "/"
	logFileName = "trades.log"
	logFile = logPath + logFileName

	side = PARAM_side
	nowStr = str(TIME_getNowTime())

	mName = PARAM_marketName
	mData = POOL_marketGetData(mName)

	if (mData) :

		mAmount = mData['TRADE_ASSET_amount']
		mSymbol = mData['MARKET_symbol']
		orderId = GVAR.TRADE_orderId

		if (side == "BUY") :
		
			bprint(defName + "Writing BUY trade (time " + nowStr + ") to log (" + logFileName + ") ..")
			tradePrice = GVAR.TRADE_price_fill
			tradeStr = nowStr + "-> BUY order FILLED [ Market: " + str(mName) + " ] [ Symbol : " + str(mSymbol) + " ] [ orderId: " + str(orderId) + " ] [ Fill price: " + str(tradePrice) + " ] [ Amount: " + str(mAmount) + " ]"
			SYS_IO_writeFile(logFile, tradeStr)

		elif (side == "SELL") :

			bprint(defName + "Writing SELL trade (time " + nowStr + ") to log (" + logFileName + ") ..")
			tradePrice = GVAR.TRADE_price_end
			tradeStr = nowStr + "-> SELL order FILLED [ Market: " + str(mName) + " ] [ Symbol : " + str(mSymbol) + " ] [ orderId: " + str(orderId) + " ] [ Fill price: " + str(tradePrice) + " ] [ Amount: " + str(mAmount) + " ]"
			SYS_IO_writeFile(logFile, tradeStr)
