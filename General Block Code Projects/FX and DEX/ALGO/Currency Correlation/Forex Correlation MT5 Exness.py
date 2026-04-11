import MetaTrader5 as mt
import pandas as pd
import csv
import time
import os
from datetime import datetime


# ==============================
# MT5 CONNECTION
# ==============================

# MT5 Login Credentials (from provided notebook)
LOGIN = 433031713
PASSWORD = "Soham@987"
SERVER = "Exness-MT5Trial7"

def connect_mt5():
    if not mt.initialize():
        print("initialize() failed, error code =", mt.last_error())
        return False
    
    authorized = mt.login(LOGIN, password=PASSWORD, server=SERVER)
    if authorized:
        print(f"Connected to MT5 account #{LOGIN}")
    else:
        print("failed to connect at account #{}, error code: {}".format(LOGIN, mt.last_error()))
        mt.shutdown()
        return False
    return True

connect_mt5()



# ==============================
# Configurations
# ==============================


SYMBOL_1 = "XAUUSDm"
SYMBOL_2 = "USDJPYm"
SYMBOL_1_QUANTITY = 0.01
SYMBOL_2_QUANTITY = 0.05
TIMEFRAME = 30  # in seconds

CSV_FILE = f"{SYMBOL_1}_{SYMBOL_2}_Progress.csv"

index_1 = 1000.0
index_2 = 1000.0

class Price_Tracker:
    def __init__(self):
        None
    def CMP(self, symbol):
        """Fetches the current market price (average of bid and ask) for a given symbol."""
        tick = mt.symbol_info(symbol)
        if tick is None:
            print(f"Error: Failed to get data for {symbol}")
            return None
        return (tick.bid + tick.ask) / 2

get_price = Price_Tracker()


# ==============================
# Order Execution Functions
# ==============================

def send_order(symbol, order_type, quantity, comment):
    tick = mt.symbol_info_tick(symbol)
    if order_type == mt.ORDER_TYPE_BUY:
        price = tick.ask
    else:
        price = tick.bid

    req={
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": quantity,
        "type": order_type,
        "price": price,
        "comment": comment,
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_IOC
    }
    result = mt.order_send(req)
    print(f"{comment} → retcode={result.retcode}")
    return result

def close_position(ticket):
    # 1. Get position details
    positions = mt.positions_get(ticket=ticket)
    if not positions:
        print(f"Position {ticket} not found.")
        return False
    
    pos = positions[0]
    symbol = pos.symbol
    lot = pos.volume
    pos_type = pos.type  # 0 for Buy, 1 for Sell
    
    # 2. Determine closing type and price (CMP)
    tick = mt.symbol_info_tick(symbol)
    if pos_type == mt.ORDER_TYPE_BUY:
        trade_type = mt.ORDER_TYPE_SELL
        price = tick.bid
    else:
        trade_type = mt.ORDER_TYPE_BUY
        price = tick.ask

    # 3. Create the close request
    # NOTE: The 'position' field is what tells MT5 to CLOSE, not hedge.
    request = {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "position": ticket,      # THIS IS THE KEY FIELD
        "price": price,
        "deviation": 20,         # Slippage
        "magic": 0,
        "comment": "close all current positions",
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_IOC, # Depends on your broker (FOK/IOC)
    }

    # 4. Send the request
    result = mt.order_send(request)
    if result.retcode != mt.TRADE_RETCODE_DONE:
        print(f"Failed to close position {ticket}: {result.comment}")
    else:
        print(f"Position {ticket} closed successfully at CMP.")
    
    return result

def close_all_positions():
    positions = mt.positions_get()
    if positions is None or len(positions) == 0:
        print("No open positions to close.")
        return

    for pos in positions:
        print(f"Closing position: {pos.ticket} ({pos.symbol})")
        close_position(pos.ticket)

    
def flip_positions(symbol_1, symbol_2, index_1, index_2):
    print("Checking for flips...")
    if index_1 > index_2:
        close_all_positions()
        print(f"Flipping positions {symbol_1} to BUY and {symbol_2} to SELL")
        send_order(symbol_1, mt.ORDER_TYPE_BUY, SYMBOL_1_QUANTITY, "Flip Buy")
        send_order(symbol_2, mt.ORDER_TYPE_SELL, SYMBOL_2_QUANTITY, "Flip Sell")
    if index_2 > index_1:
        close_all_positions()
        print(f"Flipping positions {symbol_1} to SELL and {symbol_2} to BUY")
        send_order(symbol_1, mt.ORDER_TYPE_SELL, SYMBOL_1_QUANTITY, "Flip Sell")
        send_order(symbol_2, mt.ORDER_TYPE_BUY, SYMBOL_2_QUANTITY, "Flip Buy")
    else:
        print("No positions to flip")  


# ==============================
# CSV INITIALIZATION
# ==============================

def update_csv(timestamp, symbol_1_name, symbol_2_name, price_1, price_2, pct_change_1, pct_change_2, index_1, index_2, index_spread, long_position, flip_occurred):
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        
        # Write Header if file does not exist
        if not file_exists:
            writer.writerow([
                "timestamp",
                f"{symbol_1_name}_price",
                f"{symbol_2_name}_price",
                f"{symbol_1_name}_pct_change",
                f"{symbol_2_name}_pct_change",
                f"{symbol_1_name}_index",
                f"{symbol_2_name}_index",
                "index_spread",
                "current_position",
                "flip_occurred"
            ])
            print(f"Created new CSV file: {CSV_FILE}")

        # Write Data Row
        writer.writerow([
            timestamp,
            price_1,
            price_2,
            pct_change_1,
            pct_change_2,
            index_1,
            index_2,
            index_spread,
            long_position,
            flip_occurred
        ])



# ==============================
# MAIN Execution Loop
# ==============================

current_position = f"LONG {SYMBOL_1} / SHORT {SYMBOL_2}" # Initial State matching Initial Orders
last_flip_time = None

# Place Initial Orders
# Close any existing positions first to avoid double positioning
close_all_positions() 
send_order(SYMBOL_1, mt.ORDER_TYPE_BUY, SYMBOL_1_QUANTITY, "Initial Buy")
send_order(SYMBOL_2, mt.ORDER_TYPE_SELL, SYMBOL_2_QUANTITY, "Initial Sell")

print(f"Algo started | Initial position: {current_position}")

# Initialize previous indices outside the loop for cumulative tracking
previous_index_1 = index_1
previous_index_2 = index_2

# Track the current trend/position direction
current_trend_direction = 1 

while True:
    # Symbol 1 and 2
    # 1. Fetch Previous Price
    previous_price_1 = get_price.CMP(SYMBOL_1)
    # previous_index_1 is maintained across iterations
    previous_price_2 = get_price.CMP(SYMBOL_2)
    # previous_index_2 is maintained across iterations

    print(f"Waiting {TIMEFRAME} Seconds to get new price.....")
    time.sleep(TIMEFRAME)
    
    # 2. Fetch New Price
    current_price_1 = get_price.CMP(SYMBOL_1)
    current_index_1 = round((current_price_1/previous_price_1)*previous_index_1, 4)
    current_price_2 = get_price.CMP(SYMBOL_2)
    current_index_2 = round((current_price_2/previous_price_2)*previous_index_2, 4)
    
    print(f"Previous CMP, Index {SYMBOL_1}: {previous_price_1, previous_index_1}")
    print(f"Current CMP, Index {SYMBOL_1}: {current_price_1, current_index_1}")
    print(f"Previous CMP, Index {SYMBOL_2}: {previous_price_2, previous_index_2}")
    print(f"Current CMP, Index {SYMBOL_2}: {current_price_2, current_index_2}")

    percentage_change_1 = round(((current_price_1 - previous_price_1) / previous_price_1) * 100, 4)
    percentage_change_2 = round(((current_price_2 - previous_price_2) / previous_price_2) * 100, 4)  
    print(f"Percentage {SYMBOL_1}, Net Index Change: {percentage_change_1, round(current_index_1 - previous_index_1, 4)}")
    print(f"Percentage {SYMBOL_2}, Net Index Change: {percentage_change_2, round(current_index_2 - previous_index_2, 4)}")

    # DETERMINE NEW TREND DIRECTION
    new_trend_direction = 0
    if current_index_1 > current_index_2:
        new_trend_direction = 1
    elif current_index_2 > current_index_1:
        new_trend_direction = -1
    
    flip_occurred = False
    
    # CHECK FOR FLIP
    # Only act if direction is clear (not 0) and different from current
    if new_trend_direction != 0 and new_trend_direction != current_trend_direction:
        print(f"Flip Detected! changing from {current_trend_direction} to {new_trend_direction}")
        
        # Execute the flip using existing function
        flip_positions(SYMBOL_1, SYMBOL_2, current_index_1, current_index_2)
        
        # Update State
        current_trend_direction = new_trend_direction
        flip_occurred = True
        
        if current_trend_direction == 1:
            current_position = f"LONG {SYMBOL_1} / SHORT {SYMBOL_2}"
        else:
            current_position = f"SHORT {SYMBOL_1} / LONG {SYMBOL_2}"
    else:
        # No flip needed, keep positions as is
        pass


    # 3. Calculate Spread and Update CSV
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    index_spread = round(current_index_1 - current_index_2, 4)

    update_csv(
        timestamp=timestamp_str,
        symbol_1_name=SYMBOL_1,
        symbol_2_name=SYMBOL_2,
        price_1=current_price_1,
        price_2=current_price_2,
        pct_change_1=percentage_change_1,
        pct_change_2=percentage_change_2,
        index_1=current_index_1,
        index_2=current_index_2,
        index_spread=index_spread,
        long_position=current_position,
        flip_occurred=flip_occurred
    )

    print("-" * 30)
    previous_index_1 = current_index_1
    previous_index_2 = current_index_2
