"""
NIFTY 50 Trading Dashboard
User-friendly interface for trading signals and market analysis
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
import numpy as np
import requests
import time
from plotly.subplots import make_subplots


# Page configuration
st.set_page_config(
    page_title="NIFTY 50 Trading Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .buy-signal {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
    }
    .sell-signal {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(239, 68, 68, 0.3);
    }
    .hold-signal {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(245, 158, 11, 0.3);
    }
    .info-box {
        background-color: #eff6ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #3b82f6;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #f59e0b;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)


class TradingDashboard:
    def __init__(self):
        self.nifty_data = None
        self.historical_data = None
        self.vix_data = None
        self.technical_indicators = {}
        self.risk_metrics = {}
        self.recommendation = {}

    def fetch_nifty_data(self):
        """Fetch real-time NIFTY 50 data"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
            params = {'interval': '1d', 'range': '1d'}
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                meta = result['meta']
                quotes = result['indicators']['quote'][0]

                latest_idx = -1
                current_price = meta.get('regularMarketPrice', quotes['close'][latest_idx])
                prev_close = meta.get('chartPreviousClose', quotes['close'][-2] if len(quotes['close']) > 1 else current_price)

                self.nifty_data = {
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
                return True
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return False

    def fetch_historical_data(self):
        """Fetch historical data"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
            params = {'interval': '1d', 'range': '60d'}
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                quotes = result['indicators']['quote'][0]

                self.historical_data = pd.DataFrame({
                    'timestamp': pd.to_datetime(result['timestamp'], unit='s'),
                    'open': quotes['open'],
                    'high': quotes['high'],
                    'low': quotes['low'],
                    'close': quotes['close'],
                    'volume': quotes['volume']
                }).dropna()
                return True
        except:
            return False

    def fetch_vix(self):
        """Fetch India VIX"""
        try:
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
                self.vix_data = {'current': float(vix_current)}
                return True
        except:
            self.vix_data = {'current': 15.0}
            return False

    def calculate_indicators(self):
        """Calculate technical indicators"""
        if self.historical_data is None or len(self.historical_data) < 50:
            # Set default indicators if we can't calculate them
            if self.nifty_data:
                current_price = self.nifty_data['last_price']
                self.technical_indicators = {
                    'SMA_20': current_price,
                    'SMA_50': current_price,
                    'RSI': 50,
                    'MACD': 0,
                    'MACD_Signal': 0,
                    'BB_Upper': current_price * 1.02,
                    'BB_Middle': current_price,
                    'BB_Lower': current_price * 0.98,
                    'price_vs_sma20': 0,
                    'price_vs_sma50': 0,
                }
            return False

        df = self.historical_data.copy()

        # Moving Averages
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        # Bollinger Bands
        df['BB_Middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

        # Store indicators
        current_price = self.nifty_data['last_price']
        self.technical_indicators = {
            'SMA_20': df['SMA_20'].iloc[-1],
            'SMA_50': df['SMA_50'].iloc[-1],
            'RSI': df['RSI'].iloc[-1],
            'MACD': df['MACD'].iloc[-1],
            'MACD_Signal': df['MACD_Signal'].iloc[-1],
            'BB_Upper': df['BB_Upper'].iloc[-1],
            'BB_Middle': df['BB_Middle'].iloc[-1],
            'BB_Lower': df['BB_Lower'].iloc[-1],
            'price_vs_sma20': ((current_price - df['SMA_20'].iloc[-1]) / df['SMA_20'].iloc[-1]) * 100,
            'price_vs_sma50': ((current_price - df['SMA_50'].iloc[-1]) / df['SMA_50'].iloc[-1]) * 100,
        }

        self.historical_data = df
        return True

    def analyze_and_generate_signal(self):
        """Generate trading signal"""
        signal_score = 0

        # Ensure vix_data exists
        if self.vix_data is None:
            self.vix_data = {'current': 15.0}

        # Trend analysis
        price_vs_sma20 = self.technical_indicators.get('price_vs_sma20', 0)
        price_vs_sma50 = self.technical_indicators.get('price_vs_sma50', 0)

        if price_vs_sma20 > 2 and price_vs_sma50 > 2:
            signal_score += 3
        elif price_vs_sma20 > 0 and price_vs_sma50 > 0:
            signal_score += 2
        elif price_vs_sma20 < -2 and price_vs_sma50 < -2:
            signal_score -= 3
        elif price_vs_sma20 < 0 and price_vs_sma50 < 0:
            signal_score -= 2

        # RSI
        rsi = self.technical_indicators.get('RSI', 50)
        if 40 < rsi < 60:
            signal_score += 1
        elif 30 < rsi < 40:
            signal_score += 2
        elif rsi > 70:
            signal_score -= 3
        elif rsi < 30:
            signal_score += 3

        # MACD
        if self.technical_indicators.get('MACD', 0) > self.technical_indicators.get('MACD_Signal', 0):
            signal_score += 2
        else:
            signal_score -= 2

        # VIX
        vix = self.vix_data.get('current', 15.0)
        if vix < 15:
            signal_score += 1
        elif vix > 20:
            signal_score -= 2

        # Calculate risk score
        risk_score = 50
        if vix > 25:
            risk_score = 80
        elif vix > 20:
            risk_score = 65
        elif vix > 15:
            risk_score = 45
        else:
            risk_score = 30

        # Generate recommendation
        current_price = self.nifty_data['last_price']

        if signal_score >= 5 and risk_score < 60:
            action = "STRONG BUY"
            action_type = "buy"
            confidence = "High"
            position_size = "75-100%"
        elif signal_score >= 3 and risk_score < 70:
            action = "BUY"
            action_type = "buy"
            confidence = "Moderate"
            position_size = "50-75%"
        elif signal_score <= -5 and risk_score < 60:
            action = "STRONG SELL"
            action_type = "sell"
            confidence = "High"
            position_size = "75-100%"
        elif signal_score <= -3 and risk_score < 70:
            action = "SELL"
            action_type = "sell"
            confidence = "Moderate"
            position_size = "50-75%"
        else:
            action = "HOLD / WAIT"
            action_type = "hold"
            confidence = "Neutral"
            position_size = "0-25%"

        # Calculate levels
        pivot = (self.nifty_data['high'] + self.nifty_data['low'] + current_price) / 3
        r1 = 2 * pivot - self.nifty_data['low']
        s1 = 2 * pivot - self.nifty_data['high']

        self.recommendation = {
            'action': action,
            'action_type': action_type,
            'confidence': confidence,
            'signal_score': signal_score,
            'risk_score': risk_score,
            'entry': current_price,
            'target1': current_price + (current_price * 0.015) if action_type == 'buy' else current_price - (current_price * 0.015),
            'target2': r1 if action_type == 'buy' else s1,
            'stop_loss': current_price - (current_price * 0.01) if action_type == 'buy' else current_price + (current_price * 0.01),
            'position_size': position_size,
            'r1': r1,
            's1': s1,
            'pivot': pivot
        }

        return True


def create_gauge_chart(value, title, max_value=100, color_range=None):
    """Create a gauge chart"""
    if color_range is None:
        color_range = ["#10b981", "#f59e0b", "#ef4444"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, max_value/3], 'color': color_range[0]},
                {'range': [max_value/3, 2*max_value/3], 'color': color_range[1]},
                {'range': [2*max_value/3, max_value], 'color': color_range[2]}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def create_candlestick_chart(df):
    """Create candlestick chart with indicators"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=('Price with Moving Averages', 'RSI', 'MACD')
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='NIFTY 50'
        ),
        row=1, col=1
    )

    # SMAs
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['SMA_20'], name='SMA 20', line=dict(color='orange', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['SMA_50'], name='SMA 50', line=dict(color='blue', width=1)),
        row=1, col=1
    )

    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['BB_Upper'], name='BB Upper', line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['BB_Lower'], name='BB Lower', line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )

    # RSI
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['RSI'], name='RSI', line=dict(color='purple', width=2)),
        row=2, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # MACD
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['MACD'], name='MACD', line=dict(color='blue', width=2)),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['MACD_Signal'], name='Signal', line=dict(color='orange', width=2)),
        row=3, col=1
    )

    fig.update_layout(
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )

    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)

    return fig


def main():
    # Header
    st.markdown('<h1 class="main-header">📈 NIFTY 50 Trading Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Your Smart Trading Companion - Easy to Understand, Powerful Insights")

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/stocks.png", width=80)
        st.markdown("## 🎯 Control Panel")

        # Refresh button
        if st.button("🔄 Refresh Data", key="refresh"):
            st.rerun()

        st.markdown("---")

        st.markdown("## ℹ️ How to Read")
        st.info("""
        **🟢 BUY Signal**: Good time to buy
        **🔴 SELL Signal**: Consider selling
        **🟡 HOLD**: Wait for better opportunity

        **Risk Score**: Lower is better
        **Signal Score**: Higher is better for BUY
        """)

        st.markdown("---")

        st.markdown("## ⚠️ Disclaimer")
        st.warning("""
        This is for **educational purposes only**.
        Not financial advice.
        Always do your research!
        """)

    # Initialize dashboard
    dashboard = TradingDashboard()

    # Loading state
    with st.spinner('🔍 Analyzing market data...'):
        # Fetch data
        success = dashboard.fetch_nifty_data()
        if not success:
            st.error("❌ Could not fetch market data. Please try again.")
            st.info("💡 Try refreshing the page or check your internet connection.")
            return

        # Fetch additional data (non-critical)
        dashboard.fetch_historical_data()
        dashboard.fetch_vix()

        # Ensure vix_data is initialized
        if dashboard.vix_data is None:
            dashboard.vix_data = {'current': 15.0}
            st.info("ℹ️ Using default VIX value (15.0) - could not fetch real-time VIX data")

        dashboard.calculate_indicators()
        dashboard.analyze_and_generate_signal()

    # Main content
    if dashboard.nifty_data:
        # Current Price Section
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="💰 Current Price",
                value=f"₹{dashboard.nifty_data['last_price']:,.2f}",
                delta=f"{dashboard.nifty_data['pct_change']:+.2f}%"
            )

        with col2:
            st.metric(
                label="📈 Day High",
                value=f"₹{dashboard.nifty_data['high']:,.2f}"
            )

        with col3:
            st.metric(
                label="📉 Day Low",
                value=f"₹{dashboard.nifty_data['low']:,.2f}"
            )

        with col4:
            st.metric(
                label="⚡ India VIX",
                value=f"{dashboard.vix_data['current']:.2f}",
                delta="Fear Index"
            )

        with col5:
            st.metric(
                label="🕐 Updated",
                value=datetime.now().strftime("%H:%M:%S")
            )

        st.markdown("---")

        # Trading Signal
        rec = dashboard.recommendation
        if rec['action_type'] == 'buy':
            st.markdown(f'<div class="buy-signal">🟢 {rec["action"]}</div>', unsafe_allow_html=True)
        elif rec['action_type'] == 'sell':
            st.markdown(f'<div class="sell-signal">🔴 {rec["action"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="hold-signal">🟡 {rec["action"]}</div>', unsafe_allow_html=True)

        # Recommendation Details
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📊 Signal Strength")
            fig_signal = create_gauge_chart(
                abs(rec['signal_score']) * 6.67,  # Scale to 100
                "Signal Score",
                max_value=100,
                color_range=["#ef4444", "#f59e0b", "#10b981"] if rec['signal_score'] > 0 else ["#10b981", "#f59e0b", "#ef4444"]
            )
            st.plotly_chart(fig_signal, width='stretch')

        with col2:
            st.markdown("### ⚠️ Risk Level")
            fig_risk = create_gauge_chart(
                rec['risk_score'],
                "Risk Score",
                max_value=100,
                color_range=["#10b981", "#f59e0b", "#ef4444"]
            )
            st.plotly_chart(fig_risk, width='stretch')

        with col3:
            st.markdown("### 🎯 Confidence")
            confidence_map = {"High": 85, "Moderate": 60, "Neutral": 40, "Low": 20}
            fig_conf = create_gauge_chart(
                confidence_map.get(rec['confidence'], 50),
                "Confidence Level",
                max_value=100
            )
            st.plotly_chart(fig_conf, width='stretch')

        st.markdown("---")

        # Trade Setup
        st.markdown("## 🎯 Trade Setup (If You Decide to Trade)")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("### 📍 Entry & Targets")
            st.markdown(f"""
            - **Entry Price**: ₹{rec['entry']:,.2f}
            - **🎯 Target 1**: ₹{rec['target1']:,.2f} ({((rec['target1']-rec['entry'])/rec['entry']*100):+.2f}%)
            - **🎯 Target 2**: ₹{rec['target2']:,.2f} ({((rec['target2']-rec['entry'])/rec['entry']*100):+.2f}%)
            - **🛑 Stop Loss**: ₹{rec['stop_loss']:,.2f} ({((rec['stop_loss']-rec['entry'])/rec['entry']*100):+.2f}%)
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Key Levels")
            st.markdown(f"""
            - **R1 (Resistance)**: ₹{rec['r1']:,.2f}
            - **Pivot Point**: ₹{rec['pivot']:,.2f}
            - **S1 (Support)**: ₹{rec['s1']:,.2f}
            - **Position Size**: {rec['position_size']}
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        # Simple Explanation
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### 🤔 What Does This Mean?")

        if rec['action_type'] == 'buy':
            st.markdown("""
            **Good news!** Our analysis suggests this might be a good time to buy:
            - 📈 Market trends are looking positive
            - ✅ Risk levels are acceptable
            - 💡 **If you buy**, consider selling at Target 1 or Target 2 to take profits
            - 🛑 **Important**: Set a stop loss at the suggested level to protect yourself
            """)
        elif rec['action_type'] == 'sell':
            st.markdown("""
            **Caution!** Our analysis suggests the market might go down:
            - 📉 Market trends are showing weakness
            - ⚠️ Consider reducing your positions
            - 💡 If you're holding stocks, you might want to sell
            - 🛑 If you still want to hold, watch the stop loss level
            """)
        else:
            st.markdown("""
            **Be patient!** Right now is not the best time to trade:
            - 📊 Market signals are mixed
            - ⏳ Wait for clearer direction
            - 💡 Stay in cash or hold current positions
            - 👀 Keep monitoring for better opportunities
            """)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Technical Indicators
        st.markdown("## 📊 Technical Analysis (For Advanced Users)")

        if dashboard.historical_data is not None:
            # Charts
            fig = create_candlestick_chart(dashboard.historical_data.tail(60))
            st.plotly_chart(fig, width='stretch')

            # Indicator values
            st.markdown("### 📈 Key Indicators Explained")

            col1, col2, col3 = st.columns(3)

            with col1:
                rsi = dashboard.technical_indicators['RSI']
                rsi_color = "🟢" if 40 < rsi < 60 else "🔴" if rsi > 70 or rsi < 30 else "🟡"
                st.markdown(f"""
                **RSI (Momentum)**
                {rsi_color} Value: {rsi:.2f}

                *Shows if market is overbought (>70) or oversold (<30)*
                """)

            with col2:
                macd_signal = "🟢 Bullish" if dashboard.technical_indicators['MACD'] > dashboard.technical_indicators['MACD_Signal'] else "🔴 Bearish"
                st.markdown(f"""
                **MACD (Trend)**
                {macd_signal}

                *Shows market direction and momentum*
                """)

            with col3:
                sma_signal = "🟢 Above" if dashboard.technical_indicators['price_vs_sma20'] > 0 else "🔴 Below"
                st.markdown(f"""
                **Moving Average**
                {sma_signal} 20-day average

                *Price position relative to average*
                """)

        # Risk Management
        st.markdown("---")
        st.markdown("## ⚠️ Risk Management Tips")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown("""
            ### 🛡️ Before You Trade:
            1. **Never invest more than you can afford to lose**
            2. **Always use stop loss** (automatic sell at loss limit)
            3. **Start small** if you're new to trading
            4. **Don't trade based on emotions**
            5. **Diversify** - don't put all money in one trade
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 📋 For This Trade:
            - **Maximum Risk**: 2% of your capital
            - **Current Risk Score**: {rec['risk_score']}/100
            - **Suggested Position**: {rec['position_size']}
            - **Risk Level**: {"🟢 Low" if rec['risk_score'] < 40 else "🟡 Moderate" if rec['risk_score'] < 60 else "🔴 High"}
            - **Action**: {"Favorable to trade" if rec['risk_score'] < 60 else "Be extra cautious!"}
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background-color: #f8fafc; border-radius: 10px;'>
            <h3>📚 Educational Tool Only</h3>
            <p>This analysis is generated automatically and is for learning purposes only.<br>
            <strong>Not financial advice.</strong> Always consult with a financial advisor before trading.</p>
            <p style='font-size: 0.9rem; color: #64748b;'>
                Data sources: Yahoo Finance API | Last updated: {dashboard.nifty_data['timestamp']}
            </p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
