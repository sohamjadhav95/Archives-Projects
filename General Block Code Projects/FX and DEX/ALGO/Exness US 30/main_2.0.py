import MetaTrader5 as mt
from datetime import datetime
import time

# =============================================================================
# MT5 INIT
# =============================================================================
if not mt.initialize():
    print("MT5 init failed")
    quit()

login  = 125700660
password = "Soham@987"
server   = "Exness-MT5Real7"

if not mt.login(login, password=password, server=server):
    print("Login failed:", mt.last_error())
    quit()

print("Connected to MT5")

# =============================================================================
# CONFIG
# =============================================================================
TICKER = "US30m"

BASE_LOT = 0.03
MULTIPLIER = 1.0

GRID_POINTS_DISTANCE = 25.0          # TOTAL GRID
HALF_GRID_DISTANCE = GRID_POINTS_DISTANCE / 2.0

TP_MULTIPLIER = 4.0
SL_DIFFERENCE = 0.003
MAX_LEVELS = 3
MAGIC_NUMBER = 1234567

# P0 and Grid Levels (Calculated at execution time)
P0 = 0.0
ASK = 0.0
BID = 0.0
ABOVE_GRID = 0.0
BELOW_GRID = 0.0
BUY_SL = 0.0
SELL_SL = 0.0
BUY_TP = 0.0
SELL_TP = 0.0

def calculate_grid_levels():
    global P0, ASK, BID, ABOVE_GRID, BELOW_GRID, BUY_SL, SELL_SL, BUY_TP, SELL_TP
    
    cmp = mt.symbol_info_tick(TICKER)
    if cmp is None:
        print(f"Failed to get symbol info for {TICKER}")
        quit()
        
    P0 = round((cmp.bid + cmp.ask) / 2, 4)
    ASK = cmp.ask
    BID = cmp.bid

    ABOVE_GRID = P0 + (HALF_GRID_DISTANCE)
    BELOW_GRID = P0 - (HALF_GRID_DISTANCE)

    BUY_SL = BELOW_GRID - SL_DIFFERENCE
    SELL_SL = ABOVE_GRID + SL_DIFFERENCE
    BUY_TP = ABOVE_GRID + (GRID_POINTS_DISTANCE * TP_MULTIPLIER)
    SELL_TP = BELOW_GRID - (GRID_POINTS_DISTANCE * TP_MULTIPLIER)
    
    print(f"Grid Levels Calculated based on P0={P0}")

# Base Order

def place_order(type, lot, price, sl, tp, comment):
    req = {
        "action": mt.TRADE_ACTION_PENDING,
        "symbol": TICKER,
        "volume": lot,
        "type": type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": MAGIC_NUMBER,
        "comment": comment,
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_RETURN
    }
    result = mt.order_send(req)
    print(f"{comment} → retcode={result.retcode}")
    return result  

# Helper
def get_lot_size(level_index):
    # Level 1: Base * (M^0)
    # Level 2: Base * (M^1) ...
    return round(BASE_LOT * (MULTIPLIER ** (level_index - 1)), 2)

# Initial Orders

def place_initial_orders():

    buy_price  = ABOVE_GRID
    sell_price = BELOW_GRID

    buy_sl  = BUY_SL
    sell_sl = SELL_SL

    buy_tp  = BUY_TP
    sell_tp = SELL_TP

    place_order(mt.ORDER_TYPE_BUY_STOP, BASE_LOT, buy_price, buy_sl, buy_tp, "L1 BUY")
    place_order(mt.ORDER_TYPE_SELL_STOP, BASE_LOT, sell_price, sell_sl, sell_tp, "L1 SELL")

    print(f"P0={P0}")
    print(f"BUY={buy_price} SELL={sell_price}")
    print(f"Level 1 Stop Orders Placed")


#============================================================================
# Level 1 and 2 Execution
#============================================================================


# =============================================================================
# TIME LOOP EXECUTION
# =============================================================================

print(f"Current Time: {datetime.now().strftime('%H:%M:%S')}")
target_time_str = input("Enter execution start time (HH:MM:SS): ")

print(f"Waiting for {target_time_str}...")

while True:
    current_time_str = datetime.now().strftime("%H:%M:%S")
    if current_time_str >= target_time_str:
        print(f"Time Reached: {current_time_str}. Starting execution...")
        break
    time.sleep(1)

calculate_grid_levels()
place_initial_orders()

while True:
    try:
        time.sleep(0.1)
        
        positions = mt.positions_get(symbol=TICKER)
        if positions is None: positions = []
        
        orders = mt.orders_get(symbol=TICKER)
        if orders is None: orders = []

        buy_pendings = [o for o in orders if o.type == mt.ORDER_TYPE_BUY_STOP]
        sell_pendings = [o for o in orders if o.type == mt.ORDER_TYPE_SELL_STOP]

        # Iterate through levels to handle transitions
        for i in range(1, MAX_LEVELS):
            current_lot = get_lot_size(i)
            next_lot = get_lot_size(i + 1)

            # Identify active positions at this level
            buy_pos = next((p for p in positions if p.type == mt.POSITION_TYPE_BUY and round(p.volume, 2) == current_lot), None)
            sell_pos = next((p for p in positions if p.type == mt.POSITION_TYPE_SELL and round(p.volume, 2) == current_lot), None)

            # -----------------------------------------------------------------
            # IF BUY POSITION ACTIVE AT LEVEL 'i' -> PLACE SELL PENDING LEVEL 'i+1'
            # -----------------------------------------------------------------
            if buy_pos:
                # We expect a SELL Pending of 'next_lot'
                has_next_sell = any(round(o.volume_initial, 2) == next_lot for o in sell_pendings)
                
                if not has_next_sell:
                    print(f"Level {i} Buy Active. Placing Level {i+1} Sell Pending ({next_lot} lots)...")
                    
                    # Cleanup: Remove any smaller/previous Sell Pendings (e.g., Level i pending if it was left over)
                    # We remove ANY sell pending that is SMALLER than the required next lot to ensure we don't have multiple layers
                    for o in sell_pendings:
                        if o.volume_initial < next_lot: 
                            mt.order_send({"action": mt.TRADE_ACTION_REMOVE, "order": o.ticket})
                            print(f"Removed smaller Sell Pending: {o.volume_initial} lots")

                    place_order(mt.ORDER_TYPE_SELL_STOP, next_lot, BELOW_GRID, SELL_SL, SELL_TP, f"L{i+1} SELL")

            # -----------------------------------------------------------------
            # IF SELL POSITION ACTIVE AT LEVEL 'i' -> PLACE BUY PENDING LEVEL 'i+1'
            # -----------------------------------------------------------------
            if sell_pos:
                # We expect a BUY Pending of 'next_lot'
                has_next_buy = any(round(o.volume_initial, 2) == next_lot for o in buy_pendings)
                
                if not has_next_buy:
                    print(f"Level {i} Sell Active. Placing Level {i+1} Buy Pending ({next_lot} lots)...")
                    
                    # Cleanup: Remove any smaller/previous Buy Pendings
                    for o in buy_pendings:
                        if o.volume_initial < next_lot: 
                            mt.order_send({"action": mt.TRADE_ACTION_REMOVE, "order": o.ticket})
                            print(f"Removed smaller Buy Pending: {o.volume_initial} lots")

                    place_order(mt.ORDER_TYPE_BUY_STOP, next_lot, ABOVE_GRID, BUY_SL, BUY_TP, f"L{i+1} BUY")

    except Exception as e:
        print(f"Error in loop: {e}")
        time.sleep(1)
