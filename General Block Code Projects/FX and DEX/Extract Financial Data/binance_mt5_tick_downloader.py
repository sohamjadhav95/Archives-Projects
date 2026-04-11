import requests
import pandas as pd
import time
from datetime import datetime, timezone
import os

def download_binance_futures_ticks_mt5_format(symbol, start_time_str, end_time_str, output_file, limit=1000):
    """
    Download raw tick data (aggTrades) from Binance USDT-M Futures
    and stream it directly into a single CSV file in the MT5 Custom Symbol Tick format:
    <DATE>  <TIME>  <BID>   <ASK>   <LAST>  <VOLUME>    <FLAGS>
    """
    url = "https://fapi.binance.com/fapi/v1/aggTrades"
    
    # Force the string parses to strictly evaluate as UTC, since Binance uses UTC.
    start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    
    start_time = int(start_dt.timestamp() * 1000)
    end_time = int(end_dt.timestamp() * 1000)

    current_start = start_time
    total_rows_written = 0
    
    # Initialize the output file with headers
    mt5_cols = ['<DATE>', '<TIME>', '<BID>', '<ASK>', '<LAST>', '<VOLUME>', '<FLAGS>']
    
    # Make sure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write Header First
    pd.DataFrame(columns=mt5_cols).to_csv(output_file, index=False, sep='\t')

    print(f"Downloading {symbol} tick data (aggTrades) from {start_time_str} to {end_time_str} (UTC).")
    print(f"Streaming directly to: {output_file}")
    
    while True:
        params = {
            "symbol": symbol,
            "limit": limit
        }
        if current_start:
            params["startTime"] = current_start
            # Binance only allows max 1 hour between startTime and endTime for aggTrades
            req_end_time = min(end_time, current_start + 3600 * 1000 - 1)
            params["endTime"] = req_end_time
            
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
                
            last_time = data[-1]['T']
            
            # --- Format Chunk ---
            df = pd.DataFrame(data)
            df.rename(columns={'p': 'Price', 'T': 'Timestamp'}, inplace=True)
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms", utc=True)
            df['Price'] = df['Price'].astype(float)
            
            df.sort_values(by="Timestamp", inplace=True)
            
            # MT5 Format parsing
            df['<DATE>'] = df['Timestamp'].dt.strftime('%Y.%m.%d')
            df['<TIME>'] = df['Timestamp'].dt.strftime('%H:%M:%S.%f').str[:-3]
            df['<BID>'] = df['Price']
            df['<ASK>'] = df['Price']
            df['<LAST>'] = ''
            df['<VOLUME>'] = ''
            df['<FLAGS>'] = 6
            
            # Append to massive CSV immediately
            df_mt5 = df[mt5_cols]
            df_mt5.to_csv(output_file, index=False, sep='\t', mode='a', header=False)
            
            total_rows_written += len(df_mt5)
            
            # Print periodic progress every ~100k rows
            if total_rows_written % 100000 < limit:
                current_time_str = pd.to_datetime(current_start, unit='ms', utc=True).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  ... Appended {total_rows_written} rows so far (processing {current_time_str} UTC)")
            
            
            # Time Pagination logic
            if len(data) < limit:
                # If we received less than limit, maybe we caught up to req_end_time
                if req_end_time >= end_time:
                    break
                else:
                    current_start = req_end_time + 1
            else:
                current_start = last_time + 1
                
            time.sleep(0.05)
            
        except Exception as e:
            print(f"Error fetching tick data: {e}")
            break

    return total_rows_written

if __name__ == "__main__":
    symbol = "BTCUSDT"
    
    # UTC timestamps!
    start_date = "2026-02-15 00:00:00"
    end_date = "2026-02-18 00:00:00"
    
    clean_start = start_date.replace('-', '').replace(' ', '').replace(':', '')[:12]
    clean_end = end_date.replace('-', '').replace(' ', '').replace(':', '')[:12]
    output_target = f"E:\\Projects\\General-Projects\\FX Correlation Analysis\\Data\\{symbol}m_{clean_start}_{clean_end}.csv"
    
    total_saved = download_binance_futures_ticks_mt5_format(
        symbol=symbol,
        start_time_str=start_date,
        end_time_str=end_date,
        output_file=output_target,
        limit=1000
    )
    
    print(f"\nFinished stream! Successfully saved massive chunk of {total_saved} total sequential ticks into {output_target}")
