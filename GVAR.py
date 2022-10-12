 # Global Variables

symbol = "BTCBUSD"
BOT_version = "3.5.3b"
BOT_ID = "NoName"

BOT_SOUNDS_DIR = "../SOUNDS"
BOT_LOCKS_DIR = "../LOCKS"

FLAG_main_thread_exit = False
FLAG_CFB_manual_mode = False
FLAG_CFA_manual_mode = False
FLAG_LOAD_sell_order = False

FLAG_bots_amount_divider = 1

FLAG_GRAPH_mode_on = False
FLAG_ERRORS_retry = True
FLAG_SOUND_mode_on = True
FLAG_ALIVE_counter = 0

# Use this flag to set CFA to specific value the first time the buy loop runs
# This is used in PARSEArgs() with the -CFAmP option
FLAG_first_run = False
FLAG_first_run_CFA_value = 1.0
FLAG_first_run_MODE = "ALTS"

# ======================================================================

#MODE = "ASSISTED"
MODE = "AUTO"

#MODE = "BULL"
#MODE = "BEAR"
#MODE = "FREEFALL_LAB"
#MODE = "REPAIR"

MODE_LOOP = False

MODE_VERBOSE_enabled = True
MODE_VERBOSE_loops = False
MODE_VERBOSE_events = False

MODE_VARS = None

class MODE_VARS_assisted :

    MODE_name = "Assisted v1.0"

    BUY_CFA_margin_percent_default = 0.62
    SELL_CFB_margin_percent_default = 0.52
    SELL_CFB_lnMP_limits = [ 0.10 , 0.20,  0.30 , 0.35 , 0.40 , 0.45 , 0.50 , 0.55 , 0.60 , 0.65 , 0.70 , 0.75 , 0.77 , 0.80 , 0.85 , 0.90 , 0.95 , 0.97 , 1.00 , 1.25 , 1.50 , 1.65 , 2.00 , 2.50 , 3.00 , 3.50 ]
    SELL_CFB_lnMP_values = [ 0.52 , 0.52 , 0.30 , 0.15 , 0.20 , 0.25 , 0.30 , 0.35 , 0.40 , 0.45 , 0.36 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.15 , 0.15 , 0.10 , 0.10 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 ]

###############################################################################

class MODE_VARS_debug :
    MODE_name = "DEBUG v0.1"
    
    SELL_CFB_margin_percent_default = 1
    
    BUY_CFA_margin_percent_default = 1.4
    SELL_CFB_lnMP_limits = [ 0.10, 0.20, 0.30, 0.40, 0.50, 0.60 , 0.70 , 0.80 , 0.90 , 1.00 ]
    SELL_CFB_lnMP_values = [ 0.05, 0.05, 0.05, 0.05, 0.05, 0.05 , 0.05 , 0.05 , 0.05 , 0.05 ]

    #BUY_CFA_margin_percent_default = 1.7
    #SELL_CFB_lnMP_limits = [ 0.10 , 0.20 , 0.30 , 0.40 ]
    #SELL_CFB_lnMP_values = [ 0.30 , 0.30 , 0.20 , 0.10 ]

    BUY_AWT_enabled_min_percent = 1.00
    # AWT Above Wave margin percent (% to wait above last peak)
    # 0.40
    BUY_AWT_AWmP = 0.25
    # Inflexion % is minimun amplitude of price movement to consider it as a "real wave" in order to use it as new potential peak
    # 0.20 (is FEES % + 0.5)
    STATISTICS_TICKER_cache_peak_inflexion_percent = 0.50

class MODE_VARS_vlevel_1 :

    MODE_name = "VolatLevel 1 (0.1.2)"
   
    BUY_CFA_margin_percent_default = 2.55
    SELL_CFB_margin_percent_default = 1.20

    SELL_CFB_lnMP_limits = [ 0.10 , 0.25 , 0.35,  0.45 , 0.55 , 0.65 , 0.75 , 0.90 , 1.00 , 1.50 , 2.00 , 5.00 ]
    SELL_CFB_lnMP_values = [ 0.10 , 0.25 , 0.35 , 0.10 , 0.10 , 0.10 , 0.10 , 0.10 , 0.10 , 0.10 , 0.10 , 0.10 ]
    #SELL_CFB_lnMP_values = [ 0.52 , 0.52 , 0.52 , 0.10 , 0.10 , 0.10 , 0.10 , 0.20 , 0.20 , 0.20 , 0.20 , 0.15 ]
    
    # Wave amplitude % to enable AWT (Amplitude Wave Trading)
    # 0.03 is good enought
    BUY_AWT_enabled_min_percent = 1.00
    # AWT Above Wave margin percent (% to wait above last peak)
    # 0.40
    BUY_AWT_AWmP = 0.25
    # Inflexion % is minimun amplitude of price movement to consider it as a "real wave" in order to use it as new potential peak
    # 0.20 (is FEES % + 0.5)
    STATISTICS_TICKER_cache_peak_inflexion_percent = 0.50
    
class MODE_VARS_vlevel_2 :

    MODE_name = "VolatLevel 2 (0.1.0)"
   
    BUY_CFA_margin_percent_default = 2.55
    SELL_CFB_margin_percent_default = 1.20

    SELL_CFB_lnMP_limits = [ 0.10 , 0.20,  0.30 , 0.35 , 0.40 , 0.45 , 0.50 , 0.55 , 0.60 , 0.65 , 0.70 , 0.75 , 0.77 , 0.80 , 0.85 , 0.90 , 0.95 , 0.97 , 1.00 , 1.25 , 1.50 , 1.65 , 2.00 , 2.50 , 3.00 , 3.50 ]
    SELL_CFB_lnMP_values = [ 2.55 , 2.55 , 2.55 , 2.55 , 2.55 , 2.55 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.10 , 0.10 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 ]

    #SELL_CFB_lnMP_limits = [ 0.10 , 0.25 , 0.35,  0.45 , 0.55 , 0.65 , 0.75 , 0.90 , 1.00 , 1.50 , 2.00 , 5.00 ]
    #SELL_CFB_lnMP_values = [ 0.62 , 0.62 , 0.62 , 0.62 , 0.62 , 0.30 , 0.10 , 0.10 , 0.10 , 0.10 , 0.10 , 0.10 ]
    #SELL_CFB_lnMP_values = [ 0.62 , 0.62 , 0.62 , 0.32 , 0.32 , 0.32 , 0.25 , 0.20 , 0.20 , 0.20 , 0.20 , 0.15 ]
   
    # Wave amplitude % to enable AWT (Amplitude Wave Trading)
    # 0.03 is good enought
    BUY_AWT_enabled_min_percent = 1.00
    # AWT Above Wave margin percent (% to wait above last peak)
    # 0.40
    BUY_AWT_AWmP = 0.25
    # Inflexion % is minimun amplitude of price movement to consider it as a "real wave" in order to use it as new potential peak
    # 0.20 (is FEES % + 0.5)
    STATISTICS_TICKER_cache_peak_inflexion_percent = 0.50

class MODE_VARS_blong_1 :

    MODE_name = "Bottom Long 1 (0.82%)"
   
    BUY_CFA_margin_percent_default = 2.55
    SELL_CFB_margin_percent_default = 1.20

    SELL_CFB_lnMP_limits = [ 0.10 , 0.25 , 0.35,  0.45 , 0.55 , 0.65 , 0.75 , 0.90 , 1.00 , 1.50 , 2.00 , 5.00 ]
    SELL_CFB_lnMP_values = [ 0.82 , 0.82 , 0.82 , 0.82 , 0.82 , 0.82 , 0.25 , 0.20 , 0.20 , 0.20 , 0.20 , 0.15 ]

    # Wave amplitude % to enable AWT (Amplitude Wave Trading)
    # 0.03 is good enought
    BUY_AWT_enabled_min_percent = 1.00
    # AWT Above Wave margin percent (% to wait above last peak)
    # 0.40
    BUY_AWT_AWmP = 0.25
    # Inflexion % is minimun amplitude of price movement to consider it as a "real wave" in order to use it as new potential peak
    # 0.20 (is FEES % + 0.5)
    STATISTICS_TICKER_cache_peak_inflexion_percent = 0.50
    
class MODE_VARS_blong_2 :

    MODE_name = "Bottom Long 2 (1.52%)"
   
    BUY_CFA_margin_percent_default = 2.55
    SELL_CFB_margin_percent_default = 1.20

    SELL_CFB_lnMP_limits = [ 0.10 , 0.25 , 0.35,  0.45 , 0.55 , 0.65 , 0.75 , 0.90 , 1.00 , 1.50 , 2.00 , 5.00 ]
    SELL_CFB_lnMP_values = [ 1.52 , 1.52 , 1.52 , 1.52 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 , 0.15 ]

    # Wave amplitude % to enable AWT (Amplitude Wave Trading)
    # 0.03 is good enought
    BUY_AWT_enabled_min_percent = 1.00
    # AWT Above Wave margin percent (% to wait above last peak)
    # 0.40
    BUY_AWT_AWmP = 0.25
    # Inflexion % is minimun amplitude of price movement to consider it as a "real wave" in order to use it as new potential peak
    # 0.20 (is FEES % + 0.5)
    STATISTICS_TICKER_cache_peak_inflexion_percent = 0.50

class MODE_VARS_blong_3 :

    MODE_name = "Bottom Long 3 (2.52%)"
   
    BUY_CFA_margin_percent_default = 2.55
    SELL_CFB_margin_percent_default = 1.20

    SELL_CFB_lnMP_limits = [ 0.10 , 0.25 , 0.35,  0.45 , 0.55 , 0.65 , 0.75 , 0.90 , 1.00 , 1.50 , 2.00 , 5.00 ]
    SELL_CFB_lnMP_values = [ 2.52 , 2.52 , 2.52 , 2.52 , 2.52 , 2.52 , 0.25 , 0.20 , 0.20 , 0.20 , 0.20 , 0.15 ]

    # Wave amplitude % to enable AWT (Amplitude Wave Trading)
    # 0.03 is good enought
    BUY_AWT_enabled_min_percent = 1.00
    # AWT Above Wave margin percent (% to wait above last peak)
    # 0.40
    BUY_AWT_AWmP = 0.25
    # Inflexion % is minimun amplitude of price movement to consider it as a "real wave" in order to use it as new potential peak
    # 0.20 (is FEES % + 0.5)
    STATISTICS_TICKER_cache_peak_inflexion_percent = 0.50

class MODE_VARS_fixed_long :
    
    fixval = 2.52

    MODE_name = "FixedLong(" + str(fixval) + ")"
    BUY_CFA_margin_percent_default = 5.2
    
    SELL_CFB_margin_percent_default = fixval
    SELL_CFB_lnMP_limits = [ 0.50   , 0.75   , 0.90   , 1.00   , 1.50 , 2.00 , 5.00 ]
    SELL_CFB_lnMP_values = [ fixval , fixval , fixval   , fixval   , fixval , fixval , fixval ] 

    # Wave amplitude % to enable AWT (Amplitude Wave Trading)
    # 0.03 is good enought
    BUY_AWT_enabled_min_percent = 1.00
    # AWT Above Wave margin percent (% to wait above last peak)
    # 0.40
    BUY_AWT_AWmP = 0.25
    # Inflexion % is minimun amplitude of price movement to consider it as a "real wave" in order to use it as new potential peak
    # 0.20 (is FEES % + 0.5)
    STATISTICS_TICKER_cache_peak_inflexion_percent = 0.50

class MODE_VARS_bear :

    MODE_name = "Bear v1.0"

    BUY_CFA_margin_percent_default = 2.1
    SELL_CFB_margin_percent_default = 0.6

    SELL_CFB_lnMP_limits = [ 0.3    , 0.65   , 1      , 1.5   , 2     , 5     ]
    SELL_CFB_lnMP_values = [ 0.3    , 0.2  , 0.15   , 0.25  , 0.20  , 0.15  ]  

    BUY_CFA_margin_percent_freefall = 0.8



###############################################################################

class MODE_VARS_freefall_lab :
    MODE_name = "FFL v1.0"
    
    SELL_CFB_margin_percent_default = 1
    
    BUY_CFA_margin_percent_default = 1.3
    SELL_CFB_lnMP_limits = [ 0.20 , 0.30 , 0.40 , 0.50 , 0.60 , 0.70 , 0.80 , 0.90 ]
    SELL_CFB_lnMP_values = [ 0.70 , 0.70 , 0.60 , 0.60 , 0.30 , 0.30 , 0.20 , 0.10 ]

    #BUY_CFA_margin_percent_default = 1.7
    #SELL_CFB_lnMP_limits = [ 0.10 , 0.20 , 0.30 , 0.40 ]
    #SELL_CFB_lnMP_values = [ 0.30 , 0.30 , 0.20 , 0.10 ]

    BUY_CFA_margin_percent_freefall = 0.8

###############################################################################

class MODE_VARS_auto :
    
    MODE_name = "AUTO v0.1"
        
    BUY_CFA_margin_percent_default = 1.52
    SELL_CFB_margin_percent_default = 0.50
    
    SELL_CFB_lnMP_limits = [ 0.10 , 0.20,  0.30 , 0.35 , 0.40 , 0.45 , 0.50 , 0.55 , 0.60 , 0.65 , 0.70 , 0.75 , 0.77 , 0.80 , 0.85 , 0.90 , 0.95 , 0.97 , 1.00 , 1.25 , 1.50 , 1.65 , 2.00 , 2.50 , 3.00 , 3.50 ]
    SELL_CFB_lnMP_values = [ 0.20 , 0.05 , 0.30 , 0.15 , 0.20 , 0.20 , 0.20 , 0.20 , 0.20 , 0.20 , 0.36 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.60 , 0.55 , 0.52 , 0.49 , 0.48 , 0.25 , 0.25 ]
    #SELL_CFB_lnMP_values = [ 1.52 , 1.52 , 0.30 , 0.15 , 0.20 , 0.25 , 0.30 , 0.35 , 0.40 , 0.45 , 0.36 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.22 , 0.60 , 0.55 , 0.52 , 0.49 , 0.48 , 0.25 , 0.25 ]

    #SELL_CFB_lnMP_limits = [ 0.15 , 0.16,  0.17 , 0.18 , 0.19 , 0.20 , 0.21 , 0.22 , 0.23 , 0.24 , 0.25 , 0.30 , 0.40 , 0.50 , 0.60 , 0.75 , 0.77 , 0.80 , 0.85 , 0.90 , 1.00 ]
    #SELL_CFB_lnMP_values = [ 0.40 , 0.01 , 0.02 , 0.03 , 0.04 , 0.05 , 0.06 , 0.07 , 0.08 , 0.09 , 0.10 , 0.15 , 0.20 , 0.30 , 0.40 , 0.25 , 0.20 , 0.20 , 0.20 , 0.10 , 0.10 ]

    # Wave amplitude % to enable AWT (Amplitude Wave Trading)
    # 0.03 is good enought
    BUY_AWT_enabled_min_percent = 0.03
    # AWT Above Wave margin percent (% to wait above last peak)
    # 0.40
    BUY_AWT_AWmP = 0.10
    # Inflexion % is minimun amplitude of price movement to consider it as a "real wave" in order to use it as new potential peak
    # 0.20 (is FEES % + 0.5)
    STATISTICS_TICKER_cache_peak_inflexion_percent = 0.10

###############################################################################

def MODE_load(PARAM_mode_name) :

    #print "[BOT II] MODE_load() : Selecting mode " + PARAM_mode_name

    global MODE_VARS
    MODE_VARS = MODE_VARS_auto

    mode = PARAM_mode_name
    
    if mode == "VL1" :
        MODE_VARS = MODE_VARS_vlevel_1
    elif mode == "VL2" :
        MODE_VARS = MODE_VARS_vlevel_2
    elif mode == "BL1" :
        MODE_VARS = MODE_VARS_blong_1
    elif mode == "BL2" :
        MODE_VARS = MODE_VARS_blong_2
    elif mode == "BL3" :
        MODE_VARS = MODE_VARS_blong_3
    elif mode == "DBG" :
        MODE_VARS = MODE_VARS_debug
    else :
        print("[BOT II] MODE_load() : ERROR mode " + PARAM_mode_name + " NOT FOUND -> Loading MODE: NEUTRAL")
        print("")

    global BUY_CFA_margin_percent_default
    global SELL_CFB_margin_percent_default
    global SELL_CFB_lnMP_limits
    global SELL_CFB_lnMP_values
    global BUY_AWT_enabled_min_percent
    global BUY_AWT_AWmP
    global STATISTICS_TICKER_cache_peak_inflexion_percent

    BUY_CFA_margin_percent_default = MODE_VARS.BUY_CFA_margin_percent_default
    SELL_CFB_margin_percent_default = MODE_VARS.SELL_CFB_margin_percent_default
    SELL_CFB_lnMP_limits = MODE_VARS.SELL_CFB_lnMP_limits
    SELL_CFB_lnMP_values = MODE_VARS.SELL_CFB_lnMP_values
    BUY_AWT_AWmP = MODE_VARS.BUY_AWT_AWmP
    BUY_AWT_enabled_min_percent = MODE_VARS.BUY_AWT_enabled_min_percent
    STATISTICS_TICKER_cache_peak_inflexion_percent = MODE_VARS.STATISTICS_TICKER_cache_peak_inflexion_percent

# ======================================================================

global TICKER_sleep
# Becarefull BINANCE doesn't allow more than 1200 requests per minute via python API
TICKER_sleep = 0.55
TICKER_paused = False

# ======================================================================
IDLE_locked = True

IDLE_log_counter = 0
IDLE_log_block = 60
# Margin Percent to change from IDLE mode to ACTIVE mode 
# When price reaches this margin BUY order is sent to the server and assets are freezed
# When price leaves this margin BUY order is removed and assets are freed
IDLE_price_margin_mp = 0.20
# Above this price IDLE_mode_on = False 
# Below this price IDLE_mode_on = True
IDLE_price_limit = 0.0

BUY_symbol = "BTC"
BUY_price_stop = 0
BUY_price_limit = 0
BUY_amount = 0
BUY_orderId = 0
BUY_price_margin = 5

BUY_funds_locked = 0.0
BUY_funds_free = 0.0
BUY_amount_max = 0.0

BUY_mode_on = False
BUY_fixed_price_enabled = False

BUY_data = { 
    'BUY_symbol' : BUY_symbol ,
    'BUY_price_stop' : BUY_price_stop ,
    'BUY_price_limit' : BUY_price_limit ,
    'BUY_amount' : BUY_amount ,
    'BUY_orderId' : BUY_orderId ,
    'BUY_price_margin' : BUY_price_margin ,
    }

# ======================================================================
# CFA: Chase From Above buy mode
# Buy price moves when price goes down
# Each new price is calculated as the current price + CFA_margin_percent
# Recommended margin above is 1.1% (personal opinion, not checked)

BUY_CFA_enabled = False
BUY_CFA_stats_block_duration = 60

# Recommended value for CFAmP
# CFAmP BULL LONG RUN -> 1.1 or 1.2
# CFAmP BEAR LONG RUN -> 1.5 or 2.0
BUY_CFA_margin_percent_default = 0
BUY_CFA_margin_percent = BUY_CFA_margin_percent_default

# Max % of price drop to reactivate CFA if manual mode is enabled
BUY_CFA_margin_percent_enabler = 5.0

# MAX margin percent allowed for BUY Stop price when a "Right-PEAK" is spotted
# Used in defs.py -> CFA_PriceinMargin() function
BUY_CFA_max_forced_margin_percent = 1.5

BUY_CFA_MV_margin_percent_default = 0.1
BUY_CFA_MV_margin_percent = BUY_CFA_MV_margin_percent_default

BUY_CFA_LOG_PriceInMargin = ""

# ======================================================================
# AWT: Amplitude wave trading
# Fees require a 0.15% so AWT requires at least 0.15 to work
# Using 0.3 % to enable AWT should be fine

BUY_AWT_enabled = False
BUY_AWT_enabled_min_percent = 0.3

# AWmP = Above Wave margin Percent (wait AWmP + rightest wave peak maximun price) 
# AWmP = 0.1 should be fine to wait just over last wave maximun
BUY_AWT_AWmP = 0.08
# ======================================================================

SELL_symbol = "BUSD"
SELL_price_stop = 0
SELL_price_limit = 0
SELL_price_margin = 5
SELL_amount = 0
SELL_orderId = 0

SELL_mode_on = False

SELL_data = { 
    'SELL_symbol' : SELL_symbol ,
    'SELL_price_stop' : SELL_price_stop ,
    'SELL_price_limit' : SELL_price_limit ,
    'SELL_amount' : SELL_amount ,
    'SELL_orderId' : SELL_orderId ,
    'SELL_price_margin' : SELL_price_margin
    }

# ======================================================================
# CFB: Chase From Below sell mode
# Sell price moves when price goes up
# Each new price is calculated as the current price - CFB_margin_percent
# Recommended margin below is 0.75% to avoid high precision scalpers (personal opinion, not checked)

SELL_CFB_enabled = True
SELL_CFB_mode_on = False
SELL_CFB_label = "CFB"

SELL_CFB_margin_percent_default = 0.7
SELL_CFB_margin_percent = SELL_CFB_margin_percent_default

SELL_CFB_MV_margin_percent_default = 0.01
SELL_CFB_MV_margin_percent = SELL_CFB_MV_margin_percent_default

SELL_CFB_lnMP_limits = []
SELL_CFB_lnMP_values = []
SELL_CFB_lnMP_max_limit = 0
SELL_CFB_lnMP_max_value = 0

SELL_CFB_LOG_PriceInMargin = ""

# Alive counters for each thread, then displayed as whatver signalRender wants

THREADS_SIGNAL_traderMain = 0
THREADS_SIGNAL_poolMonitor = 0
THREADS_SIGNAL_poolPricer = 0


# ======================================================================
# TRADER thread vars

TRADER_enabled = False
TRADER_mode = None
TRADER_marketName = None
TRADER_paused = True
TRADER_logsDir = "LOGS"

TRADER_wins = 0
TRADER_looses = 0

# TRADE vars

TRADE_mode_on = False
TRADE_orderId = 0
TRADE_symbol = ""
TRADE_marketName = ""

TRADE_round_prices = 4
TRADE_round_amounts = 2
TRADE_price_fill = 0
TRADE_price_end = 0
TRADE_amount_bought = 0
TRADE_amount_sold = 0

TRADE_EXCEPTIONS_SELL_e1 = "SELL Exception(1): MARKET price went BELOW SELL order STOP price"

# Aprox of BNB amount used in each TRADE (readed from average trades)
TRADE_FEE_symbol = "BNB"
TRADE_FEE_amount = 0.0222
TRADE_FEE_price = 16.50
# From BINACE fee webpage https://www.binance.com/en/fee/trading
# Taker / Maker < 50 BTC = 0.1
# Using BNB 25% off -> 0.1 * 0.75 = 0.0750
# TRADE fees = BUY + SALE fees -> TRADE fee = 0.0750 + 0.0750 = 0.15
# Example 500 BUSD BUY or SELL FEES = $ 500 / 100 * 0.075 * 2 = $ 0.75 BUSD in FEES

# ========== REAL FEES (FROM TRADING) ==================
#  0.042 BTC -> 0.0181 BNB (BUY) + 0.0181 BNB (SELL) = 0.0362 BNB (each full trade)
# Then 1 BTC -> 0.7762 BNB (each trade approx)
TRADE_FEE_percent = 0.7762

# Data structure for file save, recover trade if bot exits
# NOT USED 
TRADE_data = {
    'TRADE_price_fill' : TRADE_price_fill ,
    'TRADE_price_end' : TRADE_price_end
}

TRADE_abort = False

# Amount of sleeps allowed before the bot checks order status
# Usefull when prices soars or crashes too fast
# Sometimes TICKER price crosses BUY or SELL stop limit and rises or falls again almost instantly
# The bot may not know that the current order was filled (BUY or SELL)
# In order to aboid de-synchronization between the bot and the server, a statusCheck occurs every n-sleeps
# When TRADE_statusCheck_interval == n-sleeps -> check status and synchronize
TRADE_statusCheck_interval = 10
TRADE_statusCheck_counter = 0
TRADE_status = None

# ======================================================================

MOVER_enabled = False
MOVER_running = False
MOVER_side = "BUY"

# Delta to increase or decrease CFAmP or CFBmP depending BUY or SELL phase
MOVER_BUY_delta = 0.1
MOVER_SELL_delta = 0.1

# Aproacher % to aproach CFAmP or CFBmP depending BUY or SELL phase
# Recommended at leat 0.20 for approach to avoid ERRORs with MV_PERCENT
MOVER_aproacher_percent = 0.10
MOVER_aproacher_fixed = 0.10
MOVER_aproacher_MV_percent = 0.05

# ======================================================================

SIMULATOR_ORDERS = False
SIMULATOR_TICKER = False
SIMULATOR_TICKER_debug_stops = False
SIMULATOR_DATA_FILE = ""

SIMULATOR_orderId_counter = 0
SIMULATOR_getStatus_unFilled_returns = 2
SIMULATOR_getStatus_unFilled_returns_counter = 0 

SIMULATOR_TICKER_dataFile = ""
SIMULATOR_TICKER_dataDir = "./RECORDER/RECORDINGS/"
SIMULATOR_TICKER_index = 0
SIMULATOR_TICKER_data = []
SIMULATOR_TICKER_time = ""

# ======================================================================

STATISTICS_trades_counter = 0

STATISTICS_TICKER_cache = []
# 3600 Ticker = approx(1 hour) = 1 ticker x sec * 60 secs * 60 min
# 1800 = approx 30 mins (MACD average wave lenght for BTC)
STATISTICS_TICKER_cache_size = 700

# Time from the last ticker when a price can became a new max
# This is used to avoid confusing the max amplitude if a sudden rise occur
# A sufficient lag should be approx 5 minutes = 5 * 60 = 300
#STATISTICS_TICKER_cache_lag = 300

STATISTICS_TICKER_cache_max = None
STATISTICS_TICKER_cache_max_index = None
STATISTICS_TICKER_cache_min = None
STATISTICS_TICKER_cache_min_index = None

STATISTICS_TICKER_cache_amplitude_price = 0.0
STATISTICS_TICKER_cache_amplitude_percent = 0.0

# Last peak that ocurred
STATISTICS_TICKER_cache_rightest_bottom = None
STATISTICS_TICKER_cache_rightest_peak = None
STATISTICS_TICKER_cache_rightest_peak_found = False
STATISTICS_TICKER_cache_rightest_peak_tries = 0
# Inflexion coeficient -> % of wave amplitude considered enough
# up or down to define an inflexion point (last (rightest) peak from current price)
STATISTICS_TICKER_cache_peak_inflexion_percent = 0.07

STATISTICS_TICKER_cache_inflexion_delta_max = 0
STATISTICS_TICKER_cache_inflexion_delta_max_data = None
STATISTICS_TICKER_cache_peak_candidate_data = None
STATISTICS_TICKER_cache_inflexion_delta_min = 0
STATISTICS_TICKER_cache_inflexion_delta_min_data = None
STATISTICS_TICKER_cache_bottom_candidate_data = None


STATISTICS_trades_results_earnings = []
STATISTICS_trades_results_earnings_percents = []
STATISTICS_trades_results_balances = []
STATISTICS_trades_tradeBuyPrices = []
STATISTICS_trades_topPrices = []
STATISTICS_trades_wins_balances = []
STATISTICS_trades_looses_balances = []

STATISTICS_trades_results_total_earnings = 0
STATISTICS_trades_results_total_earnings_percent = 0
STATISTICS_trades_results_total_balances = 0

STATISTICS_trades_results_total_wins = 0
STATISTICS_trades_results_total_wins_sum = 0
STATISTICS_trades_results_total_looses = 0
STATISTICS_trades_results_total_looses_sum = 0
STATISTICS_trades_results_total_fees_sum = 0

# CURSES screen variables
SCREEN_screen = None
SCREEN_height = 50
SCREEN_width  = 200
SCREEN_enabled = False
SCREEN_exit = False

SCREEN_WIN_log = None
SCREEN_WIN_log_enabled = False
SCREEN_WIN_log_dir = "LOGS"
SCREEN_WIN_log_file = "screen.log"

SCREEN_WIN_poolMonitor = None
SCREEN_WIN_poolMonitor_visible = False
SCREEN_WIN_poolMonitor_marketIndex_start = 0
SCREEN_WIN_poolMonitor_marketIndex_end = 0

SCREEN_WIN_status = None
SCREEN_WIN_status_enabled = False

SCREEN_WIN_trader = None
SCREEN_WIN_trader_enabled = False
SCREEN_WIN_trader_cleared = False

# Numbers of lines to record and show at the log window
SCREEN_WIN_log = None
SCREEN_WIN_log_size = 10
SCREEN_WIN_log_height = 12
SCREEN_WIN_log_width = SCREEN_width - 1
SCREEN_WIN_log_lines = []

SCREEN_WIN_cmd = None
SCREEN_WIN_cmd_inputStr = ""
SCREEN_WIN_cmd_erase = False
SCREEN_WIN_cmd_cmdHistory = []
SCREEN_WIN_cmd_cmdIndex = 0
SCREEN_WIN_cmd_keyHistory = []

SCREEN_WIN_logo = None

#====================================================================

POOLS_DIR_pools = "POOLS"
POOLS_DIR_registers = "REGS"
POOLS_ext = ".yaml"

POOL_name = None
POOL_rawData = []
POOL_markets = []

POOL_FUNDS_symbol = "BUSD"
POOL_FUNDS_free = 0.00
POOL_FUNDS_locked = 0.00
POOL_FUNDS_seek = 0.00
POOL_FUNDS_limit = 0.00

# Min FUNDS to enabled many trading operations (set new order, re-calc amounts, etc)
POOL_FUNDS_min = 14.00
POOL_FUNDS_enabled = False

# When POOL_FUNDS (total FREE + LOCKED) get BELOW POOL_FUNDS_stop -> STOP ALL TRADING (SOMETHING IS GOING TOO WRONG)
POOL_FUNDS_stop = 0.00

# Time between each POOL monitor loop cycle (in seconds)
POOL_monitor_nap = 0.255

POOL_pricer_enabled = False
POOL_pricer_nap = 1

POOL_tickers = []
POOL_tickers_paused = True
POOL_counters_enabled = False
POOL_counters = []

#====================================================================

LOG_WARNINGS_name = "warnings"
