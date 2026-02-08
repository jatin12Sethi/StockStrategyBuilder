import requests
import json

def fetch_nifty_data():
    try:
        # Try Yahoo Finance API
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d&range=5d"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            result = data['chart']['result'][0]
            meta = result['meta']

            print("=" * 60)
            print("📊 LIVE NIFTY 50 MARKET DATA")
            print("=" * 60)
            print(f"Current Price: ₹{meta['regularMarketPrice']:.2f}")
            print(f"Previous Close: ₹{meta['previousClose']:.2f}")
            print(f"Day High: ₹{meta['regularMarketDayHigh']:.2f}")
            print(f"Day Low: ₹{meta['regularMarketDayLow']:.2f}")
            change = meta['regularMarketPrice'] - meta['previousClose']
            pct_change = (change / meta['previousClose']) * 100
            print(f"Change: ₹{change:.2f} ({pct_change:+.2f}%)")

            # Get historical data for technical analysis
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            print(f"\n5-Day Data Points: {len(timestamps)}")
            print("=" * 60)
            return True
        else:
            print(f"Failed to fetch data: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    fetch_nifty_data()
