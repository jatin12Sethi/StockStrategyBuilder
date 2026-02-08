"""
Groww Trading Assistant - NIFTY 50 Signal Generator
WARNING: For educational purposes only. Use at your own risk.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from datetime import datetime
import pandas as pd
import numpy as np


class GrowwTradingAssistant:
    def __init__(self):
        self.driver = None
        self.nifty_data = None

    def setup_chrome(self):
        """Initialize Chrome browser with proper settings"""
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Uncomment to run headless
        # chrome_options.add_argument('--headless')

        try:
            # Use webdriver-manager to automatically download the correct ChromeDriver version
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome browser initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing Chrome: {e}")
            print("Make sure Chrome browser is installed")
            return False

    def open_groww(self):
        """Navigate to Groww platform"""
        try:
            print("🌐 Opening Groww...")
            self.driver.get("https://groww.in")
            time.sleep(3)

            # Navigate to stocks section
            self.driver.get("https://groww.in/stocks")
            time.sleep(2)

            print("✅ Groww opened successfully")
            return True
        except Exception as e:
            print(f"❌ Error opening Groww: {e}")
            return False

    def search_nifty50(self):
        """Search for NIFTY 50 index"""
        try:
            print("🔍 Searching for NIFTY 50...")

            # Navigate directly to NIFTY 50
            self.driver.get("https://groww.in/indices/nifty-50-index")
            time.sleep(3)

            print("✅ NIFTY 50 page loaded")
            return True
        except Exception as e:
            print(f"❌ Error searching NIFTY 50: {e}")
            return False

    def fetch_nifty_data(self):
        """Fetch real-time NIFTY 50 data from public API"""
        try:
            print("📊 Fetching NIFTY 50 market data...")

            # Using NSE India API (public endpoint)
            url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers)
            time.sleep(1)

            response = session.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                nifty_info = data['data'][0]

                self.nifty_data = {
                    'last_price': float(nifty_info['last']),
                    'change': float(nifty_info['change']),
                    'pct_change': float(nifty_info['pChange']),
                    'open': float(nifty_info['open']),
                    'high': float(nifty_info['dayHigh']),
                    'low': float(nifty_info['dayLow']),
                    'previous_close': float(nifty_info['previousClose']),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                print(f"✅ NIFTY 50 Data fetched:")
                print(f"   Last Price: ₹{self.nifty_data['last_price']:.2f}")
                print(f"   Change: ₹{self.nifty_data['change']:.2f} ({self.nifty_data['pct_change']:.2f}%)")
                print(f"   Day High: ₹{self.nifty_data['high']:.2f} | Low: ₹{self.nifty_data['low']:.2f}")
                return True
            else:
                print(f"⚠️  API returned status code: {response.status_code}")
                self._use_simulated_data()
                return True

        except Exception as e:
            print(f"⚠️  Error fetching real data: {e}")
            print("📊 Using simulated data for demonstration...")
            self._use_simulated_data()
            return True

    def _use_simulated_data(self):
        """Use simulated data when API is unavailable"""
        # Simulated realistic NIFTY 50 data
        base_price = 23500
        change = np.random.uniform(-200, 200)

        self.nifty_data = {
            'last_price': base_price + change,
            'change': change,
            'pct_change': (change / base_price) * 100,
            'open': base_price,
            'high': base_price + abs(change) * 1.2,
            'low': base_price - abs(change) * 0.8,
            'previous_close': base_price,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        print(f"📊 Simulated NIFTY 50 Data:")
        print(f"   Last Price: ₹{self.nifty_data['last_price']:.2f}")
        print(f"   Change: ₹{self.nifty_data['change']:.2f} ({self.nifty_data['pct_change']:.2f}%)")

    def analyze_market_sentiment(self):
        """Analyze market sentiment based on various indicators"""
        print("\n🧠 Analyzing Market Sentiment...")

        sentiment_score = 0
        signals = []

        # 1. Price momentum analysis
        if self.nifty_data['pct_change'] > 1:
            sentiment_score += 2
            signals.append("✅ Strong bullish momentum (+1%)")
        elif self.nifty_data['pct_change'] > 0.5:
            sentiment_score += 1
            signals.append("📈 Moderate bullish momentum")
        elif self.nifty_data['pct_change'] < -1:
            sentiment_score -= 2
            signals.append("❌ Strong bearish momentum (-1%)")
        elif self.nifty_data['pct_change'] < -0.5:
            sentiment_score -= 1
            signals.append("📉 Moderate bearish momentum")
        else:
            signals.append("➡️  Neutral momentum")

        # 2. Intraday range analysis
        day_range = self.nifty_data['high'] - self.nifty_data['low']
        current_position = (self.nifty_data['last_price'] - self.nifty_data['low']) / day_range

        if current_position > 0.7:
            sentiment_score += 1
            signals.append("📊 Price near day high (bullish)")
        elif current_position < 0.3:
            sentiment_score -= 1
            signals.append("📊 Price near day low (bearish)")
        else:
            signals.append("📊 Price in mid-range (neutral)")

        # 3. Gap analysis
        gap = ((self.nifty_data['open'] - self.nifty_data['previous_close']) /
               self.nifty_data['previous_close'] * 100)

        if gap > 0.5:
            sentiment_score += 1
            signals.append(f"🔼 Gap up opening ({gap:.2f}% - bullish)")
        elif gap < -0.5:
            sentiment_score -= 1
            signals.append(f"🔽 Gap down opening ({gap:.2f}% - bearish)")

        # 4. Volatility check
        volatility = (day_range / self.nifty_data['previous_close']) * 100

        if volatility > 2:
            signals.append(f"⚡ High volatility ({volatility:.2f}% - caution)")
        else:
            signals.append(f"🔒 Normal volatility ({volatility:.2f}%)")

        return sentiment_score, signals

    def generate_trading_signals(self, sentiment_score, signals):
        """Generate buy/sell recommendations"""
        print("\n" + "="*60)
        print("📈 NIFTY 50 TRADING SIGNALS")
        print("="*60)
        print(f"⏰ Time: {self.nifty_data['timestamp']}")
        print(f"💰 Current Price: ₹{self.nifty_data['last_price']:.2f}")
        print(f"📊 Change: ₹{self.nifty_data['change']:.2f} ({self.nifty_data['pct_change']:.2f}%)")
        print("\n" + "-"*60)
        print("🔍 Market Analysis:")
        print("-"*60)

        for signal in signals:
            print(f"   {signal}")

        print("\n" + "-"*60)
        print("🎯 TRADING RECOMMENDATION:")
        print("-"*60)

        # Calculate support and resistance levels
        pivot = (self.nifty_data['high'] + self.nifty_data['low'] + self.nifty_data['last_price']) / 3
        r1 = 2 * pivot - self.nifty_data['low']
        s1 = 2 * pivot - self.nifty_data['high']
        r2 = pivot + (self.nifty_data['high'] - self.nifty_data['low'])
        s2 = pivot - (self.nifty_data['high'] - self.nifty_data['low'])

        # Generate recommendation based on sentiment
        if sentiment_score >= 3:
            action = "🟢 STRONG BUY"
            recommendation = "Market showing strong bullish signals"
            entry_price = self.nifty_data['last_price']
            target1 = entry_price * 1.01  # 1% target
            target2 = r1
            stop_loss = s1
            position_size = "Moderate to High"

        elif sentiment_score >= 1:
            action = "🟢 BUY"
            recommendation = "Market showing moderate bullish signals"
            entry_price = self.nifty_data['last_price']
            target1 = entry_price * 1.005  # 0.5% target
            target2 = r1
            stop_loss = self.nifty_data['low']
            position_size = "Moderate"

        elif sentiment_score <= -3:
            action = "🔴 STRONG SELL"
            recommendation = "Market showing strong bearish signals"
            entry_price = self.nifty_data['last_price']
            target1 = entry_price * 0.99  # 1% target
            target2 = s1
            stop_loss = r1
            position_size = "Moderate to High"

        elif sentiment_score <= -1:
            action = "🔴 SELL"
            recommendation = "Market showing moderate bearish signals"
            entry_price = self.nifty_data['last_price']
            target1 = entry_price * 0.995  # 0.5% target
            target2 = s1
            stop_loss = self.nifty_data['high']
            position_size = "Moderate"

        else:
            action = "⚪ HOLD / WAIT"
            recommendation = "Market sentiment is neutral. Wait for clearer signals"
            entry_price = self.nifty_data['last_price']
            target1 = r1
            target2 = r2
            stop_loss = s1
            position_size = "None - Wait for confirmation"

        print(f"\n   ACTION: {action}")
        print(f"   Analysis: {recommendation}")
        print(f"\n   📍 Entry Price: ₹{entry_price:.2f}")
        print(f"   🎯 Target 1: ₹{target1:.2f}")
        print(f"   🎯 Target 2: ₹{target2:.2f}")
        print(f"   🛑 Stop Loss: ₹{stop_loss:.2f}")
        print(f"   📏 Position Size: {position_size}")

        print("\n" + "-"*60)
        print("📊 Support & Resistance Levels:")
        print("-"*60)
        print(f"   R2: ₹{r2:.2f}")
        print(f"   R1: ₹{r1:.2f}")
        print(f"   Pivot: ₹{pivot:.2f}")
        print(f"   S1: ₹{s1:.2f}")
        print(f"   S2: ₹{s2:.2f}")

        print("\n" + "="*60)
        print("⚠️  DISCLAIMER:")
        print("="*60)
        print("   - This is an automated signal for educational purposes")
        print("   - NOT financial advice - Do your own research")
        print("   - Always use proper risk management")
        print("   - Never invest more than you can afford to lose")
        print("="*60 + "\n")

        return {
            'action': action,
            'entry': entry_price,
            'target1': target1,
            'target2': target2,
            'stop_loss': stop_loss,
            'sentiment_score': sentiment_score
        }

    def run(self):
        """Main execution flow"""
        try:
            print("🚀 Starting Groww Trading Assistant...")
            print("="*60 + "\n")

            # Step 1: Setup Chrome
            if not self.setup_chrome():
                return

            # Step 2: Open Groww
            if not self.open_groww():
                return

            # Step 3: Search NIFTY 50
            if not self.search_nifty50():
                return

            # Step 4: Fetch market data
            if not self.fetch_nifty_data():
                return

            # Step 5: Analyze sentiment
            sentiment_score, signals = self.analyze_market_sentiment()

            # Step 6: Generate trading signals
            trade_signal = self.generate_trading_signals(sentiment_score, signals)

            # Keep browser open briefly for review
            print("\n✅ Analysis complete! Browser will close in 5 seconds...")
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.driver:
                print("🔒 Closing browser...")
                self.driver.quit()
                print("✅ Browser closed successfully")


def main():
    """Entry point"""
    assistant = GrowwTradingAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
