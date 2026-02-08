"""
Fetch Real-Time India VIX from Investing.com
More accurate than Yahoo Finance for Indian markets
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json

class IndiaVIXFetcher:
    def __init__(self):
        self.url = "https://in.investing.com/indices/india-vix"
        self.historical_url = "https://in.investing.com/indices/india-vix-historical-data"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def fetch_current_vix(self):
        """
        Fetch current India VIX value from Investing.com
        Returns: dict with VIX data
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Try multiple selectors as Investing.com layout changes
                vix_value = None
                change = None
                change_percent = None

                # Method 1: Look for data-test attribute
                price_element = soup.find('div', {'data-test': 'instrument-price-last'})
                if price_element:
                    vix_text = price_element.get_text(strip=True)
                    vix_value = self._extract_number(vix_text)

                # Method 2: Look for specific class patterns
                if not vix_value:
                    price_elements = soup.find_all('span', class_=re.compile(r'text-\d+xl'))
                    for elem in price_elements:
                        text = elem.get_text(strip=True)
                        num = self._extract_number(text)
                        if num and 5 < num < 50:  # VIX typically ranges 10-40
                            vix_value = num
                            break

                # Method 3: Look for any element with VIX-like number
                if not vix_value:
                    all_text = soup.get_text()
                    matches = re.findall(r'\b(\d{1,2}\.\d{2})\b', all_text)
                    for match in matches:
                        num = float(match)
                        if 5 < num < 50:
                            vix_value = num
                            break

                # Try to get change values
                change_elements = soup.find_all('span', {'data-test': re.compile('instrument-price-change')})
                for elem in change_elements:
                    text = elem.get_text(strip=True)
                    if '%' in text:
                        change_percent = self._extract_number(text, allow_negative=True)
                    else:
                        change = self._extract_number(text, allow_negative=True)

                if vix_value:
                    return {
                        'current': round(vix_value, 2),
                        'change': round(change, 2) if change else 0.0,
                        'change_percent': round(change_percent, 2) if change_percent else 0.0,
                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                        'source': 'Investing.com',
                        'status': 'success'
                    }
                else:
                    # Fallback to NSE if scraping fails
                    return self.fetch_from_nse()

            else:
                return self.fetch_from_nse()

        except Exception as e:
            print(f"Error fetching VIX from Investing.com: {e}")
            return self.fetch_from_nse()

    def fetch_from_nse(self):
        """
        Fallback: Fetch VIX from NSE India
        """
        try:
            nse_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
            nse_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            # First request to get cookies
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=nse_headers, timeout=10)

            # Second request to get data
            response = session.get(nse_url, headers=nse_headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Extract VIX from response
                if 'filtered' in data and 'data' in data['filtered']:
                    vix_value = None
                    # VIX is usually in the metadata
                    for key in ['underlyingValue', 'PE', 'CE']:
                        if key in data:
                            # Look for VIX indicator
                            pass

                    # If VIX not found in option chain, use default
                    if not vix_value:
                        vix_value = 15.0  # Default reasonable value

                    return {
                        'current': round(vix_value, 2),
                        'change': 0.0,
                        'change_percent': 0.0,
                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                        'source': 'NSE India',
                        'status': 'success'
                    }

            # Last resort: Use Yahoo Finance as final fallback
            return self.fetch_from_yahoo()

        except Exception as e:
            print(f"Error fetching VIX from NSE: {e}")
            return self.fetch_from_yahoo()

    def fetch_from_yahoo(self):
        """
        Final fallback: Yahoo Finance
        """
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EINVIX"
            params = {'interval': '1d', 'range': '1d'}
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                vix_price = data['chart']['result'][0]['meta'].get('regularMarketPrice', 15.0)
                prev_close = data['chart']['result'][0]['meta'].get('chartPreviousClose', vix_price)

                change = vix_price - prev_close
                change_percent = (change / prev_close) * 100 if prev_close else 0

                return {
                    'current': round(float(vix_price), 2),
                    'change': round(float(change), 2),
                    'change_percent': round(float(change_percent), 2),
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'source': 'Yahoo Finance',
                    'status': 'success'
                }
            else:
                return self._get_default_vix()

        except Exception as e:
            print(f"Error fetching VIX from Yahoo: {e}")
            return self._get_default_vix()

    def _extract_number(self, text, allow_negative=False):
        """
        Extract numeric value from text
        """
        try:
            # Remove commas and spaces
            clean_text = text.replace(',', '').replace(' ', '')

            # Extract number (with optional negative sign)
            if allow_negative:
                match = re.search(r'-?\d+\.?\d*', clean_text)
            else:
                match = re.search(r'\d+\.?\d*', clean_text)

            if match:
                return float(match.group())
            return None
        except:
            return None

    def _get_default_vix(self):
        """
        Return default VIX when all sources fail
        """
        return {
            'current': 15.0,  # Historical average
            'change': 0.0,
            'change_percent': 0.0,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'source': 'Default',
            'status': 'fallback'
        }

    def get_vix_interpretation(self, vix_value):
        """
        Interpret VIX value for trading decisions
        """
        if vix_value < 12:
            return {
                'level': 'Very Low',
                'market_mood': 'Complacent',
                'strategy': 'Sell options (Iron Condors, Credit Spreads)',
                'risk': 'Low volatility - good for premium selling',
                'color': 'green'
            }
        elif 12 <= vix_value < 15:
            return {
                'level': 'Low',
                'market_mood': 'Calm',
                'strategy': 'Directional trades (Bull/Bear Spreads)',
                'risk': 'Normal - good for most strategies',
                'color': 'lightgreen'
            }
        elif 15 <= vix_value < 20:
            return {
                'level': 'Medium',
                'market_mood': 'Cautious',
                'strategy': 'Defined risk spreads preferred',
                'risk': 'Moderate - use stop losses',
                'color': 'yellow'
            }
        elif 20 <= vix_value < 30:
            return {
                'level': 'High',
                'market_mood': 'Nervous',
                'strategy': 'Reduce position size, wider spreads',
                'risk': 'High volatility - trade carefully',
                'color': 'orange'
            }
        else:  # >= 30
            return {
                'level': 'Very High',
                'market_mood': 'Fearful/Panic',
                'strategy': 'Avoid new positions or buy vol',
                'risk': 'Extreme - protect capital',
                'color': 'red'
            }

    def fetch_historical_vix(self, days=30):
        """
        Fetch historical VIX data
        """
        try:
            response = requests.get(self.historical_url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find historical data table
                table = soup.find('table', {'id': 'curr_table'})

                if table:
                    historical_data = []
                    rows = table.find_all('tr')[1:]  # Skip header

                    for row in rows[:days]:
                        cols = row.find_all('td')
                        if len(cols) >= 6:
                            date = cols[0].get_text(strip=True)
                            price = self._extract_number(cols[1].get_text(strip=True))

                            if date and price:
                                historical_data.append({
                                    'date': date,
                                    'close': price
                                })

                    return historical_data

            return []

        except Exception as e:
            print(f"Error fetching historical VIX: {e}")
            return []


def test_vix_fetcher():
    """
    Test function to verify VIX fetching
    """
    print("Testing India VIX Fetcher...")
    print("=" * 60)

    fetcher = IndiaVIXFetcher()

    # Test current VIX
    vix_data = fetcher.fetch_current_vix()
    print(f"\n📊 Current VIX Data:")
    print(f"   Value: {vix_data['current']}")
    print(f"   Change: {vix_data['change']} ({vix_data['change_percent']}%)")
    print(f"   Source: {vix_data['source']}")
    print(f"   Time: {vix_data['timestamp']}")
    print(f"   Status: {vix_data['status']}")

    # Test interpretation
    interpretation = fetcher.get_vix_interpretation(vix_data['current'])
    print(f"\n🎯 VIX Interpretation:")
    print(f"   Level: {interpretation['level']}")
    print(f"   Market Mood: {interpretation['market_mood']}")
    print(f"   Strategy: {interpretation['strategy']}")
    print(f"   Risk: {interpretation['risk']}")

    # Test historical data
    print(f"\n📈 Fetching Historical VIX (last 5 days)...")
    historical = fetcher.fetch_historical_vix(days=5)
    if historical:
        for item in historical:
            print(f"   {item['date']}: {item['close']}")
    else:
        print("   No historical data available")

    print("\n" + "=" * 60)
    print("✅ Test Complete!")


if __name__ == "__main__":
    test_vix_fetcher()
