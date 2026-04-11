import requests
import json
import time
import hmac
import hashlib
import csv
import os
from datetime import datetime

# ==============================
# DELTA EXCHANGE CONNECTION
# ==============================

API_KEY = "yc6zUCfaA0plHZy0EkgkOUITcfThm4"
API_SECRET = "IUj2RbmlQZDs1ZKCnm7GZaN1Ksk7JnuhqXsiuRdOHTsiTRxAWoBrSvrvlpI2"
BASE_URL = "https://api.india.delta.exchange"

def generate_signature(method, path, timestamp, payload=""):
    # prehash string: method + timestamp + path + query_params + body
    message = method + timestamp + path + payload
    return hmac.new(
        API_SECRET.encode('utf-8'), 
        message.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()

def get_common_headers(method, path, payload=""):
    timestamp = str(int(time.time()))
    signature = generate_signature(method, path, timestamp, payload)
    return {
        "api-key": API_KEY,
        "signature": signature,
        "timestamp": timestamp,
        "User-Agent": "python-rest-client", 
        "Content-Type": "application/json"
    }

# ==============================
# Configurations & Helpers
# ==============================

SYMBOL_1 = "BTCUSD" 
SYMBOL_2 = "DOGEUSD" 
SYMBOL_1_QUANTITY = 1
SYMBOL_2_QUANTITY = 7

TIMEFRAME = 30  # in seconds
CSV_FILE = f"{SYMBOL_1}_{SYMBOL_2}_Progress.csv"
index_1 = 1000.0
index_2 = 1000.0

# Product ID Cache
PRODUCT_IDS = {}

def initialize_product_ids():
    """Fetches all products once and populates the cache."""
    path = "/v2/products"
    try:
        response = requests.get(BASE_URL + path)
        if response.status_code == 200:
            products = response.json().get('result', [])
            count = 0
            for p in products:
                PRODUCT_IDS[p['symbol']] = p['id']
                count += 1
            print(f"Loaded {count} products from Delta Exchange.")
        else:
            print(f"Error fetching products: {response.text}")
    except Exception as e:
        print(f"Exception fetching products: {e}")

def get_product_id(symbol):
    if not PRODUCT_IDS:
        initialize_product_ids()
    
    pid = PRODUCT_IDS.get(symbol)
    if pid:
        return pid
    
    # Retry/Refresh if not found (maybe new listing or partial load?)
    print(f"Symbol {symbol} not found in cache. Refreshing...")
    initialize_product_ids()
    return PRODUCT_IDS.get(symbol)

# Initialize IDs
print("Fetching Product IDs...")
initialize_product_ids()

PID_1 = get_product_id(SYMBOL_1)
PID_2 = get_product_id(SYMBOL_2)
print(f"{SYMBOL_1} ID: {PID_1}")
print(f"{SYMBOL_2} ID: {PID_2}")

if not PID_1 or not PID_2:
    print("CRITICAL ERROR: Could not find Product IDs. Exiting.")
    exit()


class Price_Tracker:
    def __init__(self):
        None
    
    def CMP(self, symbol):
        """Fetches the current market price (mark price or mid price) for a given symbol."""
        
        path = f"/v2/tickers/{symbol}"
        try:
            response = requests.get(BASE_URL + path)
            if response.status_code == 200:
                result = response.json().get('result')
                # Result might be a single dict or list depending on endpoint.
                # Usually /tickers/{symbol} returns the object directly or list of 1.
                if isinstance(result, list):
                    t = result[0] if result else None
                else:
                    t = result
                
                if t:
                    bid = float(t.get('best_bid', 0) or 0)
                    ask = float(t.get('best_ask', 0) or 0)
                    if bid and ask:
                        return (bid + ask) / 2
                    return float(t.get('mark_price', 0))
            
            # Fallback to general list if specific endpoint fails (e.g. 404)
            # useful if symbol format differs slightly
        except Exception as e:
            pass # Fallthrough to general search or return None

        # Fallback: Search all tickers (expensive but safe)
        try:
           path_all = "/v2/tickers"
           response = requests.get(BASE_URL + path_all)
           if response.status_code == 200:
                tickers = response.json().get('result', [])
                for t in tickers:
                    if t['symbol'] == symbol:
                         bid = float(t.get('best_bid', 0) or 0)
                         ask = float(t.get('best_ask', 0) or 0)
                         if bid and ask:
                             return (bid + ask) / 2
                         return float(t.get('mark_price', 0))
        except Exception as e:
             print(f"Error getting price for {symbol}: {e}")
        
        return None

get_price = Price_Tracker()


# ==============================
# Order Execution Functions
# ==============================

def send_order(symbol, order_type_str, quantity, comment):
    # order_type_str expected: 'buy' or 'sell'
    product_id = PRODUCT_IDS.get(symbol)
    if not product_id:
        print(f"Product ID not found for {symbol}")
        return None

    path = "/v2/orders"
    payload = {
        "product_id": product_id,
        "size": int(quantity), # Must be integer for most Delta derivatives
        "side": order_type_str, 
        "order_type": "market_order"
    }
    
    payload_str = json.dumps(payload)
    headers = get_common_headers("POST", path, payload_str)
    
    try:
        response = requests.post(BASE_URL + path, data=payload_str, headers=headers)
        result = response.json()
        
        success = result.get('success', False)
        print(f"{comment} [{symbol} {order_type_str} {quantity}] → success={success}")
        if not success:
             print(f"Error: {result}")
        return result
    except Exception as e:
        print(f"Exception sending order: {e}")
        return None

def get_position(product_id):
    path = f"/v2/positions?product_id={product_id}"
    headers = get_common_headers("GET", path)
    try:
        response = requests.get(BASE_URL + path, headers=headers)
        if response.status_code != 200:
             print(f"Error fetching position (Status {response.status_code}): {response.text}")
        data = response.json()
        if not data.get('success', True): # Some endpoints might default true, but check if present
             print(f"API Error in get_position: {data}")
        return data
    except Exception as e:
        print(f"Exception in get_position: {e}")
        return {}

def close_position(product_id, size, side):
    # If you are Long (buy), side should be "sell" to close
    path = "/v2/orders"
    payload = {
        "product_id": product_id,
        "size": size,
        "side": side,
        "order_type": "market_order",
        "reduce_only": True 
    }
    payload_str = json.dumps(payload)
    headers = get_common_headers("POST", path, payload_str)
    response = requests.post(BASE_URL + path, data=payload_str, headers=headers)
    return response.json()

def close_all_positions():
    print("Closing all positions...")
    # Iterate over our known products
    for pid, symbol in [(PID_1, SYMBOL_1), (PID_2, SYMBOL_2)]:
        if not pid: continue
        
        try:
            res = get_position(pid)
            # Result is usually a list of positions (even with product_id filter, it returns list)
            result = res.get('result', [])
            if isinstance(result, list):
                if not result: continue
                pos = result[0]
            else:
                pos = result
            
            size = int(pos.get('size', 0))
            if size > 0:
                # Determine side to close
                # Delta sizes are absolute usually. We need to check 'side' field or if size is signed in some endpoints.
                # Assuming 'side' field exists and is 'buy' or 'sell'.
                # API usually returns 'entry_price', 'size', 'side' (buy/sell) OR 'size' with sign.
                # Let's try to get 'side'.
                open_side = pos.get('side')
                if not open_side:
                    # Fallback: try to guess or close both?
                    # Previous code guessed based on size sign, but used abs(size).
                    # Let's assume 'size' is abs and try to read 'side'.
                    # If side is missing, we have a problem.
                    pass
                
                close_side = "sell" if open_side == "buy" else "buy"
                print(f"Closing {symbol}: Found {open_side} {size}. Sending {close_side}...")
                
                resp = close_position(pid, size, close_side)
                if not resp.get('success'):
                     print(f"Failed to close {symbol}: {resp}")
                else:
                     print(f"Closed {symbol} successfully.")

        except Exception as e:
            print(f"Error checking/closing {symbol}: {e}")



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
send_order(SYMBOL_1, "buy", SYMBOL_1_QUANTITY, "Initial Buy")
send_order(SYMBOL_2, "sell", SYMBOL_2_QUANTITY, "Initial Sell")

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
    previous_price_2 = get_price.CMP(SYMBOL_2)

    if previous_price_1 is None or previous_price_2 is None:
        print("Error fetching initial prices, retrying in 5s...")
        time.sleep(5)
        continue

    print(f"Waiting {TIMEFRAME} Seconds to get new price.....")
    time.sleep(TIMEFRAME)
    
    # 2. Fetch New Price
    current_price_1 = get_price.CMP(SYMBOL_1)
    current_price_2 = get_price.CMP(SYMBOL_2)
    
    if current_price_1 is None or current_price_2 is None:
         print("Error fetching new prices, skipping...")
         continue

    current_index_1 = round((current_price_1/previous_price_1)*previous_index_1, 4)
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
    if new_trend_direction != 0 and new_trend_direction != current_trend_direction:
        print(f"Flip Detected! changing from {current_trend_direction} to {new_trend_direction}")
        
        # Execute the flip
        # Strategy: Execute orders twice. 
        # Iteration 1: Closes existing opposite positions (Net 0).
        # Iteration 2: Opens new positions (Net 1).
        
        flip_success = True
        
        for i in range(2):
            print(f"Flip Iteration {i+1}/2...", flush=True)
            res1 = None
            res2 = None
            
            if new_trend_direction == 1: # Index 1 > Index 2 -> Buy 1, Sell 2
                 print(f"Flipping positions {SYMBOL_1} to BUY and {SYMBOL_2} to SELL", flush=True)
                 res1 = send_order(SYMBOL_1, "buy", SYMBOL_1_QUANTITY, "Flip Buy")
                 res2 = send_order(SYMBOL_2, "sell", SYMBOL_2_QUANTITY, "Flip Sell")
                 
            elif new_trend_direction == -1: # Index 2 > Index 1 -> Sell 1, Buy 2
                 print(f"Flipping positions {SYMBOL_1} to SELL and {SYMBOL_2} to BUY", flush=True)
                 res1 = send_order(SYMBOL_1, "sell", SYMBOL_1_QUANTITY, "Flip Sell")
                 res2 = send_order(SYMBOL_2, "buy", SYMBOL_2_QUANTITY, "Flip Buy")
            
            # Check success of this iteration
            if not (res1 and res1.get('success') and res2 and res2.get('success')):
                flip_success = False
                print(f"WARNING: Flip iteration {i+1} failed! Aborting flip sequence.", flush=True)
                if res1: print(f"Order 1 Result: {res1}")
                if res2: print(f"Order 2 Result: {res2}")
                break
            
            # Wait between iterations (but not after the last one)
            if i == 0:
                print("Waiting 2s before opening new positions...", flush=True)
                time.sleep(2)

        # Update State only if both iterations succeeded
        if flip_success:
            if new_trend_direction == 1:
                current_position = f"LONG {SYMBOL_1} / SHORT {SYMBOL_2}"
            else:
                current_position = f"SHORT {SYMBOL_1} / LONG {SYMBOL_2}"
                
            current_trend_direction = new_trend_direction
            flip_occurred = True
            print(f"Flip Complete. New Position: {current_position}")
        else:
            print("Flip failed during execution. Will retry/re-evaluate next cycle.", flush=True)

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