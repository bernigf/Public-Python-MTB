import time
import sys
import GVAR

from time import sleep
from GVAR import *

# ======================================================================================
# ======================================================================================
# ======================================================================================

from graphics import *

def GRAPH_scaleValueY(PARAM_value, PARAM_winX, PARAM_winY) :

	global GRAPH_VAR_scale_Y_amplify_percent

	global GRAPH_VAR_scale_Y_substract_percent
	global GRAPH_VAR_scale_Y_substract_fixed_value

	global GRAPH_VAR_scale_Y_step

	global GRAPH_VAR_graphBox_Y1

	marginY = GRAPH_VAR_graphBox_Y1

	maxX = PARAM_winX
	maxY = PARAM_winY

	# substract this value to all values for zooming important END numbers
	# Using GRAPH_VAR_scale_Y_substract_percent = 0.8
	# (Ej: 9150 price -> subtract (9150 * 0.8) = 7320 -> Render 1830 = 9150 - 7320)
	if(GRAPH_VAR_scale_Y_substract_fixed_value == None) :
		GRAPH_VAR_scale_Y_substract_fixed_value = float(PARAM_value) * GRAPH_VAR_scale_Y_substract_percent

	price = (float(PARAM_value) - GRAPH_VAR_scale_Y_substract_fixed_value) * GRAPH_VAR_scale_Y_amplify_percent
	price = price - marginY

	if (price < marginY) :

		# if prices goes below graphBox limits -> re-calc substraction_fixed_value -> re-calc price
		GRAPH_VAR_scale_Y_substract_fixed_value = float(PARAM_value) * GRAPH_VAR_scale_Y_substract_percent

		price = (float(PARAM_value) - GRAPH_VAR_scale_Y_substract_fixed_value) * GRAPH_VAR_scale_Y_amplify_percent
		price = price + marginY
		
	#print ""
	#print "substract_val: " + str(GRAPH_VAR_scale_Y_substract_fixed_value) + " VALUE Y: " + str(PARAM_value) + " -> SCALED Y: " + str(price)
	#print ""
	#sleep(1)

	return price

def GRAPH_scaleValueX(PARAM_value, PARAM_winX, PARAM_winY) :

	global GRAPH_VAR_scale_X_step
	scale_factor = GRAPH_VAR_scale_X_step

	value = float(PARAM_value) * scale_factor

	return value

def GRAPH_plotPoint(PARAM_win, PARAM_pX, PARAM_pY) :

	global GRAPH_VAR_graphBox_X1
	global GRAPH_VAR_graphBox_Y1

	marginX = GRAPH_VAR_graphBox_X1
	marginY = GRAPH_VAR_graphBox_Y1

	pX = PARAM_pX
	pY = PARAM_pY

	win = PARAM_win

	final_pX = pX + marginX
	final_pY = pY + marginY

	#point = Point(final_pX, final_pY)
	#point.setOutline("white")
	#point.draw(win)

	win.plot(final_pX, final_pY, "white")

def GRAPH_plotHLine(PARAM_win, PARAM_value, PARAM_color, PARAM_winX, PARAM_winY) :

	value = PARAM_value
	marginX = GRAPH_VAR_graphBox_X1
	marginY = GRAPH_VAR_graphBox_Y1

	pX1 = marginX
	pY1 = GRAPH_scaleValueY(PARAM_value, PARAM_winX, PARAM_winY) + marginY

	pX2 = PARAM_winX - marginX
	pY2 = pY1

	point1 = Point(pX1, pY1)
	point2 = Point(pX2, pY2)
	
	line = Line(point1, point2)
	line.setOutline(PARAM_color)
	line.draw(PARAM_win)

def GRAPH_plotVLine(PARAM_win, PARAM_value, PARAM_color, PARAM_winX, PARAM_winY) :

	value = PARAM_value
	marginX = GRAPH_VAR_graphBox_X1
	marginY = GRAPH_VAR_graphBox_Y1

	pX1 = GRAPH_scaleValueX(value, PARAM_winX, PARAM_winY) + marginX
	pY1 = marginY

	pX2 = pX1
	pY2 = PARAM_winY - marginY

	point1 = Point(pX1, pY1)
	point2 = Point(pX2, pY2)
	
	line = Line(point1, point2)
	line.setOutline(PARAM_color)
	line.draw(PARAM_win)

def GRAPH_plotCircle(PARAM_pX, PARAM_pY, PARAM_radius, PARAM_color, PARAM_text, PARAM_textPosition, PARAM_win, PARAM_winX, PARAM_winY) :

	radius = PARAM_radius

	pX = GRAPH_scaleValueX(PARAM_pX, PARAM_winX, PARAM_winY) + radius
	pY = GRAPH_scaleValueY(PARAM_pY, PARAM_winX, PARAM_winY) + radius

	circle = Circle(Point(pX,pY),radius)
	circle.setOutline(PARAM_color)
	circle.setFill(PARAM_color)
	circle.draw(PARAM_win)

	text_pY = pY
	if(PARAM_textPosition == "ABOVE") :
		text_pY = pY + 20
	elif(PARAM_textPosition == "BELOW") :
		text_pY = pY - 20

	text = Text(Point(pX, text_pY), str(PARAM_text))
	text.setFace("courier")
	text.setTextColor("white")
	text.draw(PARAM_win)

def GRAPH_printNewPrice(PARAM_win, PARAM_text) :
	
	pX1 = 0.2
	pY1 = 0.2

	pX2 = 9.8
	pY2 = 9.8

	boxPx = Point(pX1 , pY1)
	boxPy = Point(pX2 , pY2)
	
	textPosP = Point(1,2)

	#GRAPH_clearRectangle(PARAM_win, pX1, pY1, pX2, pY2)

	mySquare = Rectangle(boxPx, boxPy) # create a rectangle from (1, 1) to (9, 9)
	mySquare.draw(PARAM_win) # draw it to the window

	newPrice = PARAM_text

	myText = Text(textPosP,str(PARAM_text))
	myText.setTextColor("black")
	myText.draw(PARAM_win)

# ===========================================================================

GRAPH_VAR_winX = 1150
GRAPH_VAR_winY = 500

GRAPH_VAR_max_tickers = GVAR.STATISTICS_TICKER_cache_size

GRAPH_VAR_graphBox_X1 = 10
GRAPH_VAR_graphBox_Y1 = 10

GRAPH_VAR_graphBox_X2 = GRAPH_VAR_winX - 10
GRAPH_VAR_graphBox_Y2 = GRAPH_VAR_winY - 10

GRAPH_VAR_bottomLeft_varsBox_X = 50
GRAPH_VAR_bottomLeft_varsBox_Y = 25

GRAPH_VAR_upperLeft_varsBox_X = 35
GRAPH_VAR_upperLeft_varsBox_Y = 440

# The final * 0.95 is to keep a margin from left box border for new incoming tickers (makes graphic easier to read)
GRAPH_VAR_scale_X_step = round(float(GRAPH_VAR_graphBox_X2 - GRAPH_VAR_graphBox_X1) / float(GRAPH_VAR_max_tickers),2) * 0.95
GRAPH_VAR_scale_Y_step = 1

GRAPH_VAR_scale_Y_substract_percent = 0.995
GRAPH_VAR_scale_Y_substract_fixed_value = None

GRAPH_VAR_scale_Y_amplify_percent = 1.50

GRAPH_VAR_max_price = GVAR.STATISTICS_TICKER_cache_max
GRAPH_VAR_min_price = GVAR.STATISTICS_TICKER_cache_min
GRAPH_VAR_max_index = GVAR.STATISTICS_TICKER_cache_max_index
GRAPH_VAR_min_index = GVAR.STATISTICS_TICKER_cache_min_index

GRAPH_VAR_TRADE_mode = None

def GRAPH_TRADE_plot_fixed_stuff(PARAM_win) :

	global GRAPH_VAR_graphBox_X1
	global GRAPH_VAR_graphBox_Y1
	
	global GRAPH_VAR_graphBox_X2
	global GRAPH_VAR_graphBox_Y2

	global GRAPH_VAR_bottomLeft_varsBox_X
	global GRAPH_VAR_bottomLeft_varsBox_Y

	global GRAPH_VAR_upperLeft_varsBox_X
	global GRAPH_VAR_upperLeft_varsBox_Y

	win = PARAM_win

	myBorder = Rectangle(Point( GRAPH_VAR_graphBox_X1 , GRAPH_VAR_graphBox_Y1 ),Point( GRAPH_VAR_graphBox_X2 , GRAPH_VAR_graphBox_Y2 ))
	myBorder.setOutline("white")
	myBorder = myBorder.draw(win) 

	labelSymbol1 = Text(Point(GRAPH_VAR_bottomLeft_varsBox_X , GRAPH_VAR_bottomLeft_varsBox_Y ), "Symbol: ")
	labelSymbol1.setTextColor("white")
	labelSymbol1.setFace("courier")
	labelSymbol1.draw(win)

	labelSymbol2 = Text(Point(GRAPH_VAR_bottomLeft_varsBox_X + 50, GRAPH_VAR_bottomLeft_varsBox_Y ), "BTCBUSD")
	labelSymbol2.setTextColor("white")
	labelSymbol2.setFace("courier")
	labelSymbol2.draw(win)
	
	#myText = Text(Point(3,4),"Axis X")
	#myText.draw(win)

	labelPrice1 = Text(Point(GRAPH_VAR_bottomLeft_varsBox_X + 140, GRAPH_VAR_bottomLeft_varsBox_Y), "Mode:")
	labelPrice1.setTextColor("white")
	labelPrice1.setFace("courier")
	labelPrice1.draw(win)

	labelPeak1 = Text(Point(GRAPH_VAR_upperLeft_varsBox_X + 17, GRAPH_VAR_upperLeft_varsBox_Y + 30), "Peak:")
	labelPeak1.setTextColor("white")
	labelPeak1.setFace("courier")
	labelPeak1.draw(win)

	labelBottom1 = Text(Point(GRAPH_VAR_upperLeft_varsBox_X + 10, GRAPH_VAR_upperLeft_varsBox_Y + 15), "Bottom:")
	labelBottom1.setTextColor("white")
	labelBottom1.setFace("courier")
	labelBottom1.draw(win)

	labelStop1 = Text(Point(GRAPH_VAR_bottomLeft_varsBox_X + 140, GRAPH_VAR_bottomLeft_varsBox_Y + 15), "Stop:")
	labelStop1.setTextColor("white")
	labelStop1.setFace("courier")
	labelStop1.draw(win)

	labelPrice1 = Text(Point(GRAPH_VAR_bottomLeft_varsBox_X , GRAPH_VAR_bottomLeft_varsBox_Y + 15), "Price:")
	labelPrice1.setTextColor("white")
	labelPrice1.setFace("courier")
	labelPrice1.draw(win)

	labelPrice1 = Text(Point(GRAPH_VAR_bottomLeft_varsBox_X , GRAPH_VAR_bottomLeft_varsBox_Y + 30), "Time:")
	labelPrice1.setTextColor("white")
	labelPrice1.setFace("courier")
	labelPrice1.draw(win)

	priceValue = Text(Point(0.9 , 1), "0")
	priceValue.setFace("courier")


def GRAPH_TRADE_create_tickers(PARAM_tickers_max, PARAM_step) :

	ticker_index = 0
	ticker_posX = 0.0
	ticker_stepX = PARAM_step
	
	global GRAPH_VAR_max_tickers
	
	max_tickers = GRAPH_VAR_max_tickers

	TICKERS = []

	global GRAPH_VAR_graphBox_X1

	marginX = GRAPH_VAR_graphBox_X1

	for item in range(1,max_tickers,1) :

		ticker_posX = (ticker_index * ticker_stepX) + marginX
		# Each TICKER item is a [ Index , Time, Price , Point( pixel_X , pixel_Y ) ]
		ticker_item = [ ticker_index , "" , None , Point( ticker_posX , 0.0 ) ]
		TICKERS.append(ticker_item)
		ticker_index += 1
		
	return TICKERS

def GRAPH_TRADE_plot_tickers(PARAM_TICKER_cache, PARAM_GRAPH_tickers, PARAM_PeakCircle, PARAM_PeakCircleText, PARAM_PeakTimeText, PARAM_PeakPriceText, PARAM_BottomCircle, PARAM_BottomCircleText, PARAM_BottomTimeText, PARAM_BottomPriceText, PARAM_tickers_max, PARAM_win) :

	global GRAPH_VAR_winX
	global GRAPH_VAR_winY

	global GRAPH_VAR_graphBox_X1
	global GRAPH_VAR_graphBox_Y1

	marginX = GRAPH_VAR_graphBox_X1
	marginY = GRAPH_VAR_graphBox_Y1

	winX = GRAPH_VAR_winX
	winY = GRAPH_VAR_winY

	win = PARAM_win

	# WARNING: It's very important to stop in PARAM_tickers_max - 1
	# Since indexes start from 0, and argument are ussually round numbers like 3600 (1 hour) -> 3601 indexes
	max_tickers = PARAM_tickers_max - 1

	index = 0
	
	for item in PARAM_TICKER_cache[-max_tickers:] :

		ticker_time = item[0]
		price = item[1]
		
		PARAM_GRAPH_tickers[index][1] = ticker_time
		PARAM_GRAPH_tickers[index][2] = price

		# No need to scale pointX coords since it correlates index += X_step in list creation
		# Only add_margin
		#point_X = PARAM_GRAPH_tickers[index][3].getX()
		#ticker_PX = point_X
		ticker_PY = round(GRAPH_scaleValueY(price, winX, winY),3)

		# Each GRAPH_TICKER item is a [ Index , Time , Price , Point( pixel_X , pixel_Y ) ]
		PARAM_GRAPH_tickers[index][3].undraw()
		#PARAM_GRAPH_tickers[index][3].x = ticker_PX
		PARAM_GRAPH_tickers[index][3].y = ticker_PY
		PARAM_GRAPH_tickers[index][3].setOutline("white")
		PARAM_GRAPH_tickers[index][3].draw(win)
		
		index += 1

	if (GVAR.STATISTICS_TICKER_cache_rightest_peak_found == True) :

		peak = GVAR.STATISTICS_TICKER_cache_rightest_peak
		peak_time = peak[1]
		peak_price = peak[2]

		bottom = GVAR.STATISTICS_TICKER_cache_rightest_bottom
		bottom_time = bottom[1]
		bottom_price = bottom[2]
		# Search peak new index in current cache
		# (index moves when len(TICKER_cache) >= max_tickers size is reached)
		tmp_item = (str(peak_time), float(peak_price))
		peak_index = GVAR.STATISTICS_TICKER_cache.index(tmp_item)

		# Search bottom new index in current cache
		# (index moves when len(TICKER_cache) >= max_tickers size is reached)
		tmp_bottom_item = (str(bottom_time), float(bottom_price))
		bottom_index = GVAR.STATISTICS_TICKER_cache.index(tmp_bottom_item)

		color_peak = "orange"
		color_bottom = "red"
		#GRAPH_log_file("graph.log", "PEAK index: " + str(peak_index) + " price: " + str(peak_price))
		GRAPH_TRADE_plot_circle(peak_price, peak_index, 10, color_peak, "PEAK", "BELOW", PARAM_PeakCircle, PARAM_PeakCircleText, win, winX, winY)
		GRAPH_TRADE_plot_circle(bottom_price, bottom_index, 10, color_bottom, "PEAK", "BELOW", PARAM_BottomCircle, PARAM_BottomCircleText, win, winX, winY)

		PARAM_PeakTimeText.undraw()
		PARAM_PeakPriceText.undraw()
		PARAM_PeakTimeText.setText(str(peak_time))
		PARAM_PeakPriceText.setText(str(peak_price))
		PARAM_PeakTimeText.draw(win)
		PARAM_PeakPriceText.draw(win)

		PARAM_BottomTimeText.undraw()
		PARAM_BottomPriceText.undraw()
		PARAM_BottomTimeText.setText(str(bottom_time))
		PARAM_BottomPriceText.setText(str(bottom_price))
		PARAM_BottomTimeText.draw(win)
		PARAM_BottomPriceText.draw(win)

	else :

		PARAM_PeakCircle.undraw()
		PARAM_PeakCircleText.undraw()
		PARAM_PeakTimeText.undraw()
		PARAM_PeakPriceText.undraw()
		PARAM_BottomPriceText.undraw()
		PARAM_BottomTimeText.undraw()

	return PARAM_GRAPH_tickers
	
def GRAPH_TRADE_getLastTicker (PARAM_GRAPH_tickers) :

	last_price = 0.0
	last_time = ""

	for item in PARAM_GRAPH_tickers :

		price = item[2]
		ticker_time = item[1]

		if (price != None) :

			last_price = price
			last_time = ticker_time

		else:
			
			break

	return (last_time, last_price)

def GRAPH_log_file (PARAM_file, PARAM_data) :

	file_name = str(PARAM_file)
	data = str(PARAM_data)

	with open(file_name, 'a') as f :
		
		f.write(data + "\n")

# =====================================================================================
# =====================================================================================

def GRAPH_TRADE_plot_line (PARAM_price_stop, PARAM_color, PARAM_stop_Line, PARAM_win) :

	global GRAPH_VAR_winX
	global GRAPH_VAR_winY

	global GRAPH_VAR_graphBox_X1
	global GRAPH_VAR_graphBox_Y1

	value = PARAM_price_stop
	marginX = GRAPH_VAR_graphBox_X1
	marginY = GRAPH_VAR_graphBox_Y1

	pX1 = marginX
	pY1 = GRAPH_scaleValueY(value, GRAPH_VAR_winX, GRAPH_VAR_winY)

	pX2 = GRAPH_VAR_winX - marginX
	pY2 = pY1

	point1 = Point(pX1, pY1)
	point2 = Point(pX2, pY2)

	line = PARAM_stop_Line
	line.undraw()
	line.setOutline(PARAM_color)
	line.p1 = point1
	line.p2 = point2
	line.draw(PARAM_win)

def GRAPH_TRADE_plot_circle (PARAM_price, PARAM_index, PARAM_radius, PARAM_color, PARAM_text, PARAM_textPosition, PARAM_Circle, PARAM_CircleTxt, PARAM_win, PARAM_winX, PARAM_winY) :

	radius = PARAM_radius

	pX = GRAPH_scaleValueX(PARAM_index, PARAM_winX, PARAM_winY) + radius
	pY = GRAPH_scaleValueY(PARAM_price, PARAM_winX, PARAM_winY) + radius

	circle = PARAM_Circle
	circle.undraw()
	circle.p1 = Point(pX, pY)
	circle.p2 = Point(pX + 10, pY - 10)
	circle.setOutline(PARAM_color)
	circle.setFill(PARAM_color)
	circle.draw(PARAM_win)

	text_pY = pY
	if(PARAM_textPosition == "ABOVE") :
		text_pY = pY + 20
	elif(PARAM_textPosition == "BELOW") :
		text_pY = pY - 20

	circleText = PARAM_CircleTxt
	circleText.undraw()
	circleText.setText(PARAM_text)     
	circleText.setFace("courier")
	circleText.setTextColor("white")
	circleText.draw(PARAM_win)

# =====================================================================================
# =====================================================================================

def GRAPH_TRADE_plot(PARAM_TICKER_sleep) :

	global GRAPH_VAR_winX
	global GRAPH_VAR_winY

	global GRAPH_VAR_bottomLeft_varsBox_X
	global GRAPH_VAR_bottomLeft_varsBox_Y

	global GRAPH_VAR_TRADE_mode
	global GRAPH_VAR_scale_X_step

	global GRAPH_VAR_max_tickers
	
	winX = GRAPH_VAR_winX
	winY = GRAPH_VAR_winY

	GRAPH_VAR_TRADE_mode = "???"
	LINE_STOP_price_value = 0
	LINE_STOP_price_color = "white"

	color_line_min = color_rgb(255,102,102)
	color_line_max = color_rgb(128,255,0)

	symbolStr = "BTCBUSD"
	sellSymbolStr = "BUSD"

	win = GraphWin("Trader SYMBOL", width = winX, height = winY, autoflush=False) # create a window	
	win.setCoords(0, 0, winX, winY) # set the coordinates of the window; bottom left is (0, 0) and top right is (10, 10)
	win.setBackground("black")
	win

	GRAPH_TRADE_plot_fixed_stuff(win)

	priceGTxt = Text(Point( GRAPH_VAR_bottomLeft_varsBox_X + 50, GRAPH_VAR_bottomLeft_varsBox_Y + 15), "0")
	priceGTxt.setTextColor("white")
	priceGTxt.setFace("courier")
	priceGTxt.draw(win)

	stopGTxt = Text(Point( GRAPH_VAR_bottomLeft_varsBox_X + 195, GRAPH_VAR_bottomLeft_varsBox_Y + 15), "0")
	stopGTxt.setTextColor("white")
	stopGTxt.setFace("courier")
	stopGTxt.draw(win)

	timeGTxt = Text(Point( GRAPH_VAR_bottomLeft_varsBox_X + 50, GRAPH_VAR_bottomLeft_varsBox_Y + 30), "0:0:0")
	timeGTxt.setTextColor("white")
	timeGTxt.setFace("courier")
	timeGTxt.draw(win)

	modeGTxt = Text(Point( GRAPH_VAR_bottomLeft_varsBox_X + 190, GRAPH_VAR_bottomLeft_varsBox_Y), GRAPH_VAR_TRADE_mode)
	modeGTxt.setFace("courier")
	modeGTxt.draw(win)

	peakTimeGTxt = Text(Point( GRAPH_VAR_upperLeft_varsBox_X + 100, GRAPH_VAR_upperLeft_varsBox_Y + 30), "0:0:0")
	peakTimeGTxt.setTextColor("orange")
	peakTimeGTxt.setFace("courier")
	peakTimeGTxt.draw(win)

	peakPriceGTxt = Text(Point( GRAPH_VAR_upperLeft_varsBox_X + 170, GRAPH_VAR_upperLeft_varsBox_Y + 30), "0.0")
	peakPriceGTxt.setTextColor("orange")
	peakPriceGTxt.setFace("courier")
	peakPriceGTxt.draw(win)

	bottomTimeGTxt = Text(Point( GRAPH_VAR_upperLeft_varsBox_X + 100, GRAPH_VAR_upperLeft_varsBox_Y + 15), "0:0:0")
	bottomTimeGTxt.setTextColor("red")
	bottomTimeGTxt.setFace("courier")
	bottomTimeGTxt.draw(win)

	bottomPriceGTxt = Text(Point( GRAPH_VAR_upperLeft_varsBox_X + 170, GRAPH_VAR_upperLeft_varsBox_Y + 15), "0.0")
	bottomPriceGTxt.setTextColor("red")
	bottomPriceGTxt.setFace("courier")
	bottomPriceGTxt.draw(win)

	LINE_BUY_color = "green"
	LINE_FILL_color = "white"
	LINE_IDLE_color = "yellow"
	
	STOP_Gline = Line(Point(0,100),Point(100,100))
	STOP_Gline.draw(win)

	IDLE_Gline = Line(Point(0,100),Point(100,100))
	IDLE_Gline.draw(win)

	FILL_Gline = Line(Point(0,100),Point(100,100))
	FILL_Gline.draw(win)

	FEE_Gline = Line(Point(0,100),Point(100,100))
	FEE_Gline.draw(win)

	PERCENT_1_Gline = Line(Point(0,100),Point(100,100))
	PERCENT_1_Gline.draw(win)

	RPEAK_GCircle = Circle(Point(0,0),0)
	RPEAK_GCircle.setFill("white")
	RPEAK_GCircleTxt = Text(Point(0,0),"")
	RPEAK_GCircle.draw(win)
	RPEAK_GCircleTxt.draw(win)

	RBOTTOM_GCircle = Circle(Point(0,0),0)
	RBOTTOM_GCircle.setFill("white")
	RBOTTOM_GCircleTxt = Text(Point(0,0),"")
	RBOTTOM_GCircle.draw(win)
	RBOTTOM_GCircleTxt.draw(win)

	# ===== Create TICKERS items list =====
	
	tickers_max = GRAPH_VAR_max_tickers
	tickers_step = GRAPH_VAR_scale_X_step
	# Create EMPTY Graph-TICKERS-list with n-tickers_max empty items	
	GRAPH_tickers = GRAPH_TRADE_create_tickers(tickers_max, tickers_step)

	# ===== =====

	while (True) :	
		
		GRAPH_tickers = GRAPH_TRADE_plot_tickers(GVAR.STATISTICS_TICKER_cache, GRAPH_tickers, RPEAK_GCircle, RPEAK_GCircleTxt, peakTimeGTxt, peakPriceGTxt, RBOTTOM_GCircle, RBOTTOM_GCircleTxt, bottomTimeGTxt, bottomPriceGTxt, tickers_max, win)

		last_ticker = GRAPH_TRADE_getLastTicker(GRAPH_tickers)

		last_ticker_price = last_ticker[1] 
		last_ticker_time = last_ticker[0]
		
		priceGTxt.setText(str(last_ticker_price))
		timeGTxt.setText(str(last_ticker_time))

		if (GVAR.BUY_mode_on == True) :
			
			GRAPH_VAR_TRADE_mode = "BUY"
			LINE_STOP_color = "green"
			
			FILL_Gline.undraw()
			PERCENT_1_Gline.undraw()
			FEE_Gline.undraw()
			GRAPH_TRADE_plot_line(GVAR.BUY_price_limit, LINE_STOP_color, STOP_Gline, win)
			GRAPH_TRADE_plot_line(GVAR.IDLE_price_limit, LINE_IDLE_color, IDLE_Gline, win)
		
		elif (GVAR.BUY_mode_on == False ) :

			GRAPH_VAR_TRADE_mode = "SELL"
			LINE_STOP_color = "red"
			LINE_FEE_color = "yellow"
			LINE_PERCENT_1_color = "green"

			FEE_price = GVAR.TRADE_price_fill + (GVAR.TRADE_FEE_percent * GVAR.TRADE_FEE_price)
			PERCENT_1_price = GVAR.TRADE_price_fill * (1.01)

			GRAPH_TRADE_plot_line(GVAR.SELL_price_limit, LINE_STOP_color, STOP_Gline, win)
			GRAPH_TRADE_plot_line(GVAR.TRADE_price_fill, LINE_FILL_color, FILL_Gline, win)
			GRAPH_TRADE_plot_line(FEE_price, LINE_FEE_color, FEE_Gline, win)
			GRAPH_TRADE_plot_line(PERCENT_1_price, LINE_PERCENT_1_color, PERCENT_1_Gline, win)
		
		modeGTxt.setTextColor(LINE_STOP_color)
		modeGTxt.setText(GRAPH_VAR_TRADE_mode)

		stopGTxt.setTextColor(LINE_STOP_color)
		stopGTxt.setText(str(str(GVAR.BUY_price_stop)))

		update()
		sleep(PARAM_TICKER_sleep)

	#win.getMouse() # pause before closing

#GRAPH_TRADE_plot(1)
