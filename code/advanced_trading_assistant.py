"""
Advanced Groww Trading Assistant - Comprehensive Market & Risk Analysis
Author: Trading Bot v2.0
WARNING: For educational purposes only. Use at your own risk.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class AdvancedTradingAssistant:
    def __init__(self):
        self.driver = None
        self.nifty_data = {}
        self.historical_data = None
        self.vix_data = None
        self.technical_indicators = {}
        self.risk_metrics = {}

    def setup_chrome(self):
        """Initialize Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome initialized (headless mode)")
            return True
        except Exception as e:
            print(f"⚠️  Chrome initialization failed: {e}")
            print("Continuing with API-only analysis...")
            return False

    def fetch_comprehensive_market_data(self):
        """Fetch comprehensive market data from multiple sources"""
        print("\n" + "="*70)
        print("📊 FETCHING COMPREHENSIVE MARKET DATA")
        print("="*70)

        # Fetch NIFTY 50 data
        self.fetch_nifty_data_yahoo()

        # Fetch historical data for technical analysis
        self.fetch_historical_data()

        # Fetch VIX (Volatility Index)
        self.fetch_india_vix()

        # Fetch Bank NIFTY for correlation
        self.fetch_bank_nifty()

        return True

    def fetch_nifty_data_yahoo(self):
        """Fetch real-time NIFTY 50 data from Yahoo Finance"""
        try:
            print("\n📈 Fetching NIFTY 50 real-time data...")

            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
            params = {'interval': '1d', 'range': '1d'}
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                meta = result['meta']

                # Extract current data
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]

                # Get latest values
                latest_idx = -1
                current_price = meta.get('regularMarketPrice', quotes['close'][latest_idx])
                prev_close = meta.get('chartPreviousClose', quotes['close'][-2] if len(quotes['close']) > 1 else current_price)

                self.nifty_data = {
                    'symbol': '^NSEI',
                    'name': 'NIFTY 50',
                    'last_price': float(current_price),
                    'open': float(quotes['open'][latest_idx]) if quotes['open'][latest_idx] else current_price,
                    'high': float(quotes['high'][latest_idx]) if quotes['high'][latest_idx] else current_price,
                    'low': float(quotes['low'][latest_idx]) if quotes['low'][latest_idx] else current_price,
                    'volume': int(quotes['volume'][latest_idx]) if quotes['volume'][latest_idx] else 0,
                    'previous_close': float(prev_close),
                    'change': float(current_price - prev_close),
                    'pct_change': float((current_price - prev_close) / prev_close * 100),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                print(f"✅ NIFTY 50: ₹{self.nifty_data['last_price']:.2f} "
                      f"({self.nifty_data['pct_change']:+.2f}%)")
                return True

        except Exception as e:
            print(f"⚠️  Yahoo Finance error: {e}")
            self._use_fallback_data()
            return False

    def fetch_historical_data(self):
        """Fetch historical data for technical indicators"""
        try:
            print("📊 Fetching 50-day historical data...")

            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
            params = {'interval': '1d', 'range': '60d'}
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                quotes = result['indicators']['quote'][0]

                # Create DataFrame
                self.historical_data = pd.DataFrame({
                    'timestamp': pd.to_datetime(result['timestamp'], unit='s'),
                    'open': quotes['open'],
                    'high': quotes['high'],
                    'low': quotes['low'],
                    'close': quotes['close'],
                    'volume': quotes['volume']
                }).dropna()

                print(f"✅ Historical data: {len(self.historical_data)} trading days")
                return True

        except Exception as e:
            print(f"⚠️  Historical data error: {e}")
            return False

    def fetch_india_vix(self):
        """Fetch India VIX (Volatility Index)"""
        try:
            print("⚡ Fetching India VIX...")

            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EINVIX"
            params = {'interval': '1d', 'range': '5d'}
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                meta = result['meta']
                quotes = result['indicators']['quote'][0]

                vix_current = meta.get('regularMarketPrice', quotes['close'][-1])

                self.vix_data = {
                    'current': float(vix_current),
                    'status': self._interpret_vix(vix_current)
                }

                print(f"✅ India VIX: {self.vix_data['current']:.2f} ({self.vix_data['status']})")
                return True

        except Exception as e:
            print(f"⚠️  VIX data error: {e}")
            self.vix_data = {'current': 15.0, 'status': 'Moderate'}
            return False

    def fetch_bank_nifty(self):
        """Fetch Bank NIFTY for market breadth analysis"""
        try:
            print("🏦 Fetching Bank NIFTY...")

            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEBANK"
            params = {'interval': '1d', 'range': '1d'}
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                meta = result['meta']
                quotes = result['indicators']['quote'][0]

                bank_price = meta.get('regularMarketPrice', quotes['close'][-1])
                bank_prev = meta.get('chartPreviousClose', quotes['close'][-2] if len(quotes['close']) > 1 else bank_price)
                bank_change = ((bank_price - bank_prev) / bank_prev) * 100

                self.nifty_data['bank_nifty_change'] = float(bank_change)

                print(f"✅ Bank NIFTY: {bank_change:+.2f}%")
                return True

        except Exception as e:
            print(f"⚠️  Bank NIFTY error: {e}")
            self.nifty_data['bank_nifty_change'] = self.nifty_data['pct_change']
            return False

    def calculate_technical_indicators(self):
        """Calculate comprehensive technical indicators"""
        print("\n" + "="*70)
        print("🔬 CALCULATING TECHNICAL INDICATORS")
        print("="*70)

        if self.historical_data is None or len(self.historical_data) < 50:
            print("⚠️  Insufficient historical data for full technical analysis")
            return self._calculate_basic_indicators()

        df = self.historical_data.copy()

        # 1. Moving Averages
        print("\n📈 Moving Averages...")
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()

        current_price = self.nifty_data['last_price']
        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]

        self.technical_indicators['SMA_20'] = sma_20
        self.technical_indicators['SMA_50'] = sma_50
        self.technical_indicators['price_vs_sma20'] = ((current_price - sma_20) / sma_20) * 100
        self.technical_indicators['price_vs_sma50'] = ((current_price - sma_50) / sma_50) * 100

        print(f"   SMA 20: ₹{sma_20:.2f} | Price vs SMA20: {self.technical_indicators['price_vs_sma20']:+.2f}%")
        print(f"   SMA 50: ₹{sma_50:.2f} | Price vs SMA50: {self.technical_indicators['price_vs_sma50']:+.2f}%")

        # 2. RSI (Relative Strength Index)
        print("\n📊 RSI (Relative Strength Index)...")
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        rsi = df['RSI'].iloc[-1]
        self.technical_indicators['RSI'] = rsi
        self.technical_indicators['RSI_signal'] = self._interpret_rsi(rsi)

        print(f"   RSI: {rsi:.2f} - {self.technical_indicators['RSI_signal']}")

        # 3. MACD
        print("\n📉 MACD (Moving Average Convergence Divergence)...")
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        macd = df['MACD'].iloc[-1]
        macd_signal = df['MACD_Signal'].iloc[-1]
        macd_hist = df['MACD_Histogram'].iloc[-1]

        self.technical_indicators['MACD'] = macd
        self.technical_indicators['MACD_Signal'] = macd_signal
        self.technical_indicators['MACD_Histogram'] = macd_hist
        self.technical_indicators['MACD_crossover'] = 'Bullish' if macd > macd_signal else 'Bearish'

        print(f"   MACD: {macd:.2f} | Signal: {macd_signal:.2f}")
        print(f"   Histogram: {macd_hist:.2f} - {self.technical_indicators['MACD_crossover']}")

        # 4. Bollinger Bands
        print("\n📊 Bollinger Bands...")
        df['BB_Middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

        bb_upper = df['BB_Upper'].iloc[-1]
        bb_middle = df['BB_Middle'].iloc[-1]
        bb_lower = df['BB_Lower'].iloc[-1]

        self.technical_indicators['BB_Upper'] = bb_upper
        self.technical_indicators['BB_Middle'] = bb_middle
        self.technical_indicators['BB_Lower'] = bb_lower
        self.technical_indicators['BB_Position'] = ((current_price - bb_lower) / (bb_upper - bb_lower)) * 100

        print(f"   Upper: ₹{bb_upper:.2f} | Middle: ₹{bb_middle:.2f} | Lower: ₹{bb_lower:.2f}")
        print(f"   Position: {self.technical_indicators['BB_Position']:.1f}% of band width")

        # 5. ATR (Average True Range) for volatility
        print("\n⚡ ATR (Average True Range)...")
        df['H-L'] = df['high'] - df['low']
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(window=14).mean()

        atr = df['ATR'].iloc[-1]
        atr_pct = (atr / current_price) * 100

        self.technical_indicators['ATR'] = atr
        self.technical_indicators['ATR_pct'] = atr_pct

        print(f"   ATR: ₹{atr:.2f} ({atr_pct:.2f}% of price)")

        # 6. Volume Analysis
        print("\n📊 Volume Analysis...")
        avg_volume_20 = df['volume'].rolling(window=20).mean().iloc[-1]
        current_volume = self.nifty_data['volume']
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0

        self.technical_indicators['volume_ratio'] = volume_ratio
        self.technical_indicators['volume_signal'] = 'High' if volume_ratio > 1.5 else 'Normal' if volume_ratio > 0.7 else 'Low'

        print(f"   Current Volume: {current_volume:,}")
        print(f"   20-day Avg: {avg_volume_20:,.0f}")
        print(f"   Ratio: {volume_ratio:.2f}x - {self.technical_indicators['volume_signal']}")

        return True

    def _calculate_basic_indicators(self):
        """Fallback for basic indicators when historical data is limited"""
        current_price = self.nifty_data['last_price']

        # Simple pivot points
        pivot = (self.nifty_data['high'] + self.nifty_data['low'] + current_price) / 3

        self.technical_indicators = {
            'SMA_20': current_price,
            'SMA_50': current_price,
            'RSI': 50,
            'RSI_signal': 'Neutral',
            'MACD_crossover': 'Neutral',
            'ATR_pct': 1.0,
            'volume_signal': 'Normal',
            'BB_Position': 50
        }

        return True

    def calculate_risk_metrics(self):
        """Calculate comprehensive risk metrics"""
        print("\n" + "="*70)
        print("⚠️  RISK ANALYSIS")
        print("="*70)

        # 1. Volatility Risk
        print("\n📊 Volatility Risk...")
        if self.vix_data is None:
            self.vix_data = {'current': 15.0, 'status': 'Moderate'}
        vix = self.vix_data['current']
        vix_risk = 'High' if vix > 20 else 'Moderate' if vix > 15 else 'Low'

        self.risk_metrics['volatility_risk'] = vix_risk
        self.risk_metrics['vix'] = vix

        print(f"   India VIX: {vix:.2f} - {vix_risk} Risk")

        # 2. Trend Risk
        print("\n📈 Trend Risk...")
        price_vs_sma20 = self.technical_indicators.get('price_vs_sma20', 0)
        price_vs_sma50 = self.technical_indicators.get('price_vs_sma50', 0)

        if price_vs_sma20 > 2 and price_vs_sma50 > 5:
            trend_risk = 'Overbought Risk'
        elif price_vs_sma20 < -2 and price_vs_sma50 < -5:
            trend_risk = 'Oversold - Bounce Potential'
        else:
            trend_risk = 'Normal'

        self.risk_metrics['trend_risk'] = trend_risk
        print(f"   Trend Risk: {trend_risk}")

        # 3. RSI Extremes
        print("\n📊 RSI Risk...")
        rsi = self.technical_indicators.get('RSI', 50)

        if rsi > 70:
            rsi_risk = 'Overbought - Reversal Risk High'
        elif rsi < 30:
            rsi_risk = 'Oversold - Bounce Likely'
        else:
            rsi_risk = 'Normal Range'

        self.risk_metrics['rsi_risk'] = rsi_risk
        print(f"   RSI Risk: {rsi_risk}")

        # 4. Market Breadth
        print("\n🏦 Market Breadth...")
        nifty_change = self.nifty_data['pct_change']
        bank_change = self.nifty_data.get('bank_nifty_change', nifty_change)

        divergence = abs(nifty_change - bank_change)

        if divergence > 1.0:
            breadth_risk = 'High Divergence - Caution'
        elif divergence > 0.5:
            breadth_risk = 'Moderate Divergence'
        else:
            breadth_risk = 'Good Correlation'

        self.risk_metrics['market_breadth'] = breadth_risk
        print(f"   NIFTY vs Bank NIFTY: {breadth_risk}")
        print(f"   Divergence: {divergence:.2f}%")

        # 5. Support/Resistance Risk
        print("\n📊 Support/Resistance Risk...")
        current_price = self.nifty_data['last_price']
        day_high = self.nifty_data['high']
        day_low = self.nifty_data['low']

        day_range = day_high - day_low
        position_in_range = ((current_price - day_low) / day_range * 100) if day_range > 0 else 50

        if position_in_range > 80:
            sr_risk = 'Near resistance - Breakout or reversal'
        elif position_in_range < 20:
            sr_risk = 'Near support - Breakdown or bounce'
        else:
            sr_risk = 'Mid-range - Room to move'

        self.risk_metrics['support_resistance_risk'] = sr_risk
        print(f"   Position in day range: {position_in_range:.1f}%")
        print(f"   Assessment: {sr_risk}")

        # 6. Overall Risk Score
        print("\n⚠️  Overall Risk Score...")
        risk_score = self._calculate_overall_risk_score()

        self.risk_metrics['overall_score'] = risk_score
        self.risk_metrics['overall_rating'] = self._interpret_risk_score(risk_score)

        print(f"   Risk Score: {risk_score}/100")
        print(f"   Rating: {self.risk_metrics['overall_rating']}")

        return True

    def _calculate_overall_risk_score(self):
        """Calculate overall risk score (0-100, higher = more risky)"""
        score = 0

        # VIX contribution (30 points)
        vix = self.vix_data['current']
        if vix > 25:
            score += 30
        elif vix > 20:
            score += 20
        elif vix > 15:
            score += 10
        else:
            score += 5

        # RSI contribution (20 points)
        rsi = self.technical_indicators.get('RSI', 50)
        if rsi > 70 or rsi < 30:
            score += 20
        elif rsi > 60 or rsi < 40:
            score += 10
        else:
            score += 5

        # Volatility contribution (20 points)
        atr_pct = self.technical_indicators.get('ATR_pct', 1.0)
        if atr_pct > 2.5:
            score += 20
        elif atr_pct > 1.5:
            score += 10
        else:
            score += 5

        # Trend contribution (15 points)
        price_vs_sma20 = abs(self.technical_indicators.get('price_vs_sma20', 0))
        if price_vs_sma20 > 5:
            score += 15
        elif price_vs_sma20 > 3:
            score += 10
        else:
            score += 5

        # Market breadth (15 points)
        nifty_change = self.nifty_data['pct_change']
        bank_change = self.nifty_data.get('bank_nifty_change', nifty_change)
        divergence = abs(nifty_change - bank_change)
        if divergence > 1.5:
            score += 15
        elif divergence > 0.75:
            score += 10
        else:
            score += 5

        return min(score, 100)

    def _interpret_risk_score(self, score):
        """Interpret overall risk score"""
        if score >= 75:
            return "🔴 VERY HIGH RISK - Trade with extreme caution"
        elif score >= 60:
            return "🟠 HIGH RISK - Reduce position size"
        elif score >= 40:
            return "🟡 MODERATE RISK - Normal caution"
        elif score >= 25:
            return "🟢 LOW RISK - Favorable conditions"
        else:
            return "🟢 VERY LOW RISK - Ideal trading conditions"

    def generate_comprehensive_signals(self):
        """Generate comprehensive trading signals"""
        print("\n" + "="*70)
        print("🎯 SIGNAL GENERATION")
        print("="*70)

        signal_score = 0
        signals = []

        # 1. Trend Signals (weight: 3)
        print("\n📈 Trend Analysis...")
        price_vs_sma20 = self.technical_indicators.get('price_vs_sma20', 0)
        price_vs_sma50 = self.technical_indicators.get('price_vs_sma50', 0)

        if price_vs_sma20 > 2 and price_vs_sma50 > 2:
            signal_score += 3
            signals.append("✅ Strong uptrend (above both SMAs)")
        elif price_vs_sma20 > 0 and price_vs_sma50 > 0:
            signal_score += 2
            signals.append("📈 Uptrend (above SMAs)")
        elif price_vs_sma20 < -2 and price_vs_sma50 < -2:
            signal_score -= 3
            signals.append("❌ Strong downtrend (below both SMAs)")
        elif price_vs_sma20 < 0 and price_vs_sma50 < 0:
            signal_score -= 2
            signals.append("📉 Downtrend (below SMAs)")
        else:
            signals.append("➡️  Mixed trend signals")

        # 2. Momentum Signals (weight: 3)
        print("⚡ Momentum Analysis...")
        rsi = self.technical_indicators.get('RSI', 50)

        if 40 < rsi < 60:
            signal_score += 1
            signals.append("📊 RSI neutral (balanced momentum)")
        elif 30 < rsi < 40:
            signal_score += 2
            signals.append("📈 RSI oversold (bullish reversal setup)")
        elif 60 < rsi < 70:
            signal_score -= 1
            signals.append("⚠️  RSI approaching overbought")
        elif rsi > 70:
            signal_score -= 3
            signals.append("❌ RSI overbought (bearish reversal risk)")
        elif rsi < 30:
            signal_score += 3
            signals.append("✅ RSI oversold (strong bounce potential)")

        # 3. MACD Signals (weight: 2)
        print("📊 MACD Analysis...")
        macd_crossover = self.technical_indicators.get('MACD_crossover', 'Neutral')
        macd_hist = self.technical_indicators.get('MACD_Histogram', 0)

        if macd_crossover == 'Bullish' and macd_hist > 0:
            signal_score += 2
            signals.append("✅ MACD bullish crossover")
        elif macd_crossover == 'Bearish' and macd_hist < 0:
            signal_score -= 2
            signals.append("❌ MACD bearish crossover")
        else:
            signals.append("➡️  MACD neutral")

        # 4. Volatility Signals (weight: 2)
        print("⚡ Volatility Analysis...")
        vix = self.vix_data['current']

        if vix < 12:
            signal_score += 2
            signals.append("✅ Very low volatility (stable market)")
        elif vix < 15:
            signal_score += 1
            signals.append("📊 Low volatility (calm market)")
        elif vix > 25:
            signal_score -= 2
            signals.append("❌ High volatility (risky market)")
        elif vix > 20:
            signal_score -= 1
            signals.append("⚠️  Elevated volatility (caution)")
        else:
            signals.append("📊 Moderate volatility")

        # 5. Volume Signals (weight: 1)
        print("📊 Volume Analysis...")
        volume_signal = self.technical_indicators.get('volume_signal', 'Normal')

        if volume_signal == 'High':
            if self.nifty_data['pct_change'] > 0:
                signal_score += 1
                signals.append("✅ High volume with uptrend (conviction)")
            else:
                signal_score -= 1
                signals.append("⚠️  High volume with downtrend (selling pressure)")
        elif volume_signal == 'Low':
            signals.append("⚠️  Low volume (weak conviction)")
        else:
            signals.append("📊 Normal volume")

        # 6. Market Breadth (weight: 2)
        print("🏦 Market Breadth Analysis...")
        nifty_change = self.nifty_data['pct_change']
        bank_change = self.nifty_data.get('bank_nifty_change', nifty_change)

        if abs(nifty_change - bank_change) < 0.3:
            if nifty_change > 0.5:
                signal_score += 2
                signals.append("✅ Broad market rally (strong conviction)")
            elif nifty_change < -0.5:
                signal_score -= 2
                signals.append("❌ Broad market decline (weak)")
        else:
            signals.append("⚠️  Market divergence (mixed signals)")

        # 7. Intraday Position (weight: 1)
        print("📍 Intraday Position...")
        day_range = self.nifty_data['high'] - self.nifty_data['low']
        if day_range > 0:
            position = (self.nifty_data['last_price'] - self.nifty_data['low']) / day_range

            if position > 0.75:
                signal_score += 1
                signals.append("📈 Near day high (bullish)")
            elif position < 0.25:
                signal_score -= 1
                signals.append("📉 Near day low (bearish)")
            else:
                signals.append("📊 Mid-range position")

        return signal_score, signals

    def generate_trading_recommendation(self, signal_score, signals):
        """Generate final trading recommendation with risk management"""
        print("\n" + "="*70)
        print("🎯 COMPREHENSIVE TRADING RECOMMENDATION")
        print("="*70)

        # Display current market status
        print(f"\n⏰ Time: {self.nifty_data['timestamp']}")
        print(f"💰 NIFTY 50: ₹{self.nifty_data['last_price']:.2f}")
        print(f"📊 Change: ₹{self.nifty_data['change']:.2f} ({self.nifty_data['pct_change']:+.2f}%)")
        print(f"📈 Day Range: ₹{self.nifty_data['low']:.2f} - ₹{self.nifty_data['high']:.2f}")
        print(f"⚡ India VIX: {self.vix_data['current']:.2f}")

        # Display all signals
        print("\n" + "-"*70)
        print("📋 MARKET SIGNALS:")
        print("-"*70)
        for signal in signals:
            print(f"   {signal}")

        print("\n" + "-"*70)
        print("⚠️  RISK ASSESSMENT:")
        print("-"*70)
        print(f"   Overall Risk: {self.risk_metrics['overall_rating']}")
        print(f"   Volatility: {self.risk_metrics['volatility_risk']}")
        print(f"   Trend: {self.risk_metrics['trend_risk']}")
        print(f"   Market Breadth: {self.risk_metrics['market_breadth']}")

        # Calculate support and resistance
        current_price = self.nifty_data['last_price']
        atr = self.technical_indicators.get('ATR', current_price * 0.01)

        pivot = (self.nifty_data['high'] + self.nifty_data['low'] + current_price) / 3
        r1 = 2 * pivot - self.nifty_data['low']
        s1 = 2 * pivot - self.nifty_data['high']
        r2 = pivot + (self.nifty_data['high'] - self.nifty_data['low'])
        s2 = pivot - (self.nifty_data['high'] - self.nifty_data['low'])

        # Get risk score
        risk_score = self.risk_metrics['overall_score']

        # Generate recommendation based on signal score and risk
        print("\n" + "="*70)
        print("🎯 FINAL RECOMMENDATION:")
        print("="*70)

        if signal_score >= 6 and risk_score < 60:
            action = "🟢 STRONG BUY"
            confidence = "High"
            rationale = "Strong bullish signals with acceptable risk"
            position_size = "75-100% of planned allocation"
            entry = current_price
            target1 = current_price + (atr * 1.5)
            target2 = r1
            stop_loss = current_price - (atr * 1.0)

        elif signal_score >= 3 and risk_score < 70:
            action = "🟢 BUY"
            confidence = "Moderate"
            rationale = "Positive signals with manageable risk"
            position_size = "50-75% of planned allocation"
            entry = current_price
            target1 = current_price + atr
            target2 = r1
            stop_loss = current_price - (atr * 1.0)

        elif signal_score <= -6 and risk_score < 60:
            action = "🔴 STRONG SELL / SHORT"
            confidence = "High"
            rationale = "Strong bearish signals with acceptable risk"
            position_size = "75-100% of planned allocation"
            entry = current_price
            target1 = current_price - (atr * 1.5)
            target2 = s1
            stop_loss = current_price + (atr * 1.0)

        elif signal_score <= -3 and risk_score < 70:
            action = "🔴 SELL / SHORT"
            confidence = "Moderate"
            rationale = "Negative signals with manageable risk"
            position_size = "50-75% of planned allocation"
            entry = current_price
            target1 = current_price - atr
            target2 = s1
            stop_loss = current_price + (atr * 1.0)

        elif risk_score >= 75:
            action = "⚪ STAY OUT"
            confidence = "High"
            rationale = "Risk too high - market conditions unfavorable"
            position_size = "0% - Do not trade"
            entry = current_price
            target1 = r1
            target2 = r2
            stop_loss = s1

        else:
            action = "⚪ HOLD / WAIT"
            confidence = "Neutral"
            rationale = "Mixed signals - wait for clearer direction"
            position_size = "25-50% or wait"
            entry = current_price
            target1 = r1
            target2 = r2
            stop_loss = s1

        print(f"\n   ACTION: {action}")
        print(f"   Confidence: {confidence}")
        print(f"   Signal Score: {signal_score}/15")
        print(f"   Risk Score: {risk_score}/100")
        print(f"\n   📝 Rationale: {rationale}")

        print(f"\n   📍 Entry Price: ₹{entry:.2f}")
        print(f"   🎯 Target 1: ₹{target1:.2f} ({((target1-entry)/entry*100):+.2f}%)")
        print(f"   🎯 Target 2: ₹{target2:.2f} ({((target2-entry)/entry*100):+.2f}%)")
        print(f"   🛑 Stop Loss: ₹{stop_loss:.2f} ({((stop_loss-entry)/entry*100):+.2f}%)")
        print(f"   📏 Position Size: {position_size}")

        # Risk-Reward Ratio
        potential_gain = abs(target1 - entry)
        potential_loss = abs(entry - stop_loss)
        rr_ratio = potential_gain / potential_loss if potential_loss > 0 else 0

        print(f"\n   💰 Risk-Reward Ratio: 1:{rr_ratio:.2f}")

        print("\n" + "-"*70)
        print("📊 KEY LEVELS:")
        print("-"*70)
        print(f"   R2 (Strong Resistance): ₹{r2:.2f}")
        print(f"   R1 (Resistance): ₹{r1:.2f}")
        print(f"   Pivot: ₹{pivot:.2f}")
        print(f"   S1 (Support): ₹{s1:.2f}")
        print(f"   S2 (Strong Support): ₹{s2:.2f}")

        print("\n" + "-"*70)
        print("📋 RISK MANAGEMENT RULES:")
        print("-"*70)
        print("   1. Never risk more than 2% of capital on single trade")
        print("   2. Use stop loss ALWAYS - no exceptions")
        print("   3. Take partial profits at Target 1 (50%)")
        print("   4. Trail stop loss to entry after Target 1")
        print("   5. Exit immediately if risk conditions deteriorate")
        print(f"   6. Current risk level: {self.risk_metrics['overall_rating']}")

        print("\n" + "="*70)
        print("⚠️  CRITICAL DISCLAIMERS:")
        print("="*70)
        print("   • This is an AUTOMATED analysis for EDUCATIONAL purposes")
        print("   • NOT financial advice - Do your own research")
        print("   • Markets can be unpredictable - trade at your own risk")
        print("   • Always use proper position sizing and risk management")
        print("   • Past performance does not guarantee future results")
        print("   • Consider consulting a financial advisor before trading")
        print("="*70 + "\n")

        return {
            'action': action,
            'confidence': confidence,
            'signal_score': signal_score,
            'risk_score': risk_score,
            'entry': entry,
            'target1': target1,
            'target2': target2,
            'stop_loss': stop_loss,
            'rr_ratio': rr_ratio
        }

    def _use_fallback_data(self):
        """Use fallback data when APIs fail"""
        base_price = 25693.70  # Last known price
        change = np.random.uniform(-150, 150)

        self.nifty_data = {
            'symbol': '^NSEI',
            'name': 'NIFTY 50',
            'last_price': base_price + change,
            'open': base_price,
            'high': base_price + abs(change) * 1.3,
            'low': base_price - abs(change) * 0.7,
            'volume': 250000000,
            'previous_close': base_price,
            'change': change,
            'pct_change': (change / base_price) * 100,
            'bank_nifty_change': (change / base_price) * 100,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        print(f"⚠️  Using fallback data: ₹{self.nifty_data['last_price']:.2f}")

    def _interpret_vix(self, vix):
        """Interpret VIX level"""
        if vix > 25:
            return "High Fear"
        elif vix > 20:
            return "Elevated Fear"
        elif vix > 15:
            return "Moderate"
        elif vix > 12:
            return "Low Fear"
        else:
            return "Very Low Fear"

    def _interpret_rsi(self, rsi):
        """Interpret RSI value"""
        if rsi >= 70:
            return "Overbought"
        elif rsi >= 60:
            return "Bullish"
        elif rsi >= 40:
            return "Neutral"
        elif rsi >= 30:
            return "Bearish"
        else:
            return "Oversold"

    def run(self):
        """Main execution flow"""
        try:
            print("\n" + "="*70)
            print("🚀 ADVANCED TRADING ASSISTANT v2.0")
            print("="*70)
            print("Comprehensive Market & Risk Analysis for NIFTY 50")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)

            # Step 1: Setup Chrome (optional for visual confirmation)
            self.setup_chrome()

            if self.driver:
                try:
                    print("\n🌐 Opening Groww for visual confirmation...")
                    self.driver.get("https://groww.in/indices/nifty-50-index")
                    time.sleep(3)
                    print("✅ Groww loaded (background)")
                except:
                    print("⚠️  Groww page load failed, continuing with API data...")

            # Step 2: Fetch comprehensive market data
            self.fetch_comprehensive_market_data()

            # Step 3: Calculate technical indicators
            self.calculate_technical_indicators()

            # Step 4: Calculate risk metrics
            self.calculate_risk_metrics()

            # Step 5: Generate signals
            signal_score, signals = self.generate_comprehensive_signals()

            # Step 6: Generate final recommendation
            recommendation = self.generate_trading_recommendation(signal_score, signals)

            print("✅ Analysis Complete!")

            time.sleep(2)

        except KeyboardInterrupt:
            print("\n\n⚠️  Analysis interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                print("\n🔒 Closing browser...")
                self.driver.quit()
                print("✅ Browser closed")


def main():
    """Entry point"""
    assistant = AdvancedTradingAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
