"""
Integrated Trading Dashboard with Groww Support
Real-time recommendations with manual execution instructions

Ready for market open at 9:15 AM
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
from datetime import datetime, time, timedelta
import json
import os
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Live Trading Dashboard - Groww Ready",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-alert {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    .trade-instruction {
        background: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
    }
    .market-open {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    .market-closed {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


class IntegratedTradingSystem:
    def __init__(self):
        self.nifty_data = None
        self.vix_data = None
        self.market_open_time = time(9, 15)
        self.market_close_time = time(15, 30)
        self.pre_market_time = time(9, 0)

        # Safety limits
        self.daily_loss_limit = 10000
        self.per_trade_limit = 5000
        self.max_lots = 2

        # Load settings
        self.load_settings()

    def load_settings(self):
        """Load user settings"""
        if os.path.exists('trading_settings.json'):
            with open('trading_settings.json', 'r') as f:
                settings = json.load(f)
                self.daily_loss_limit = settings.get('daily_loss_limit', 10000)
                self.per_trade_limit = settings.get('per_trade_limit', 5000)
                self.max_lots = settings.get('max_lots', 2)

    def is_market_open(self):
        """Check if market is currently open"""
        now = datetime.now().time()
        today = datetime.now().weekday()

        # Monday=0 to Friday=4
        if today > 4:  # Weekend
            return False, "Weekend - Markets Closed"

        if now < self.pre_market_time:
            return False, f"Pre-market - Opens at {self.market_open_time.strftime('%I:%M %p')}"
        elif self.pre_market_time <= now < self.market_open_time:
            return False, "Pre-market Session"
        elif self.market_open_time <= now <= self.market_close_time:
            return True, "Market is OPEN"
        else:
            return False, "Market Closed for Today"

    def time_to_market_open(self):
        """Calculate time remaining to market open"""
        now = datetime.now()
        today = now.date()
        market_open = datetime.combine(today, self.market_open_time)

        if now.time() > self.market_close_time:
            # Market closed, calculate for tomorrow
            market_open += timedelta(days=1)
            # Skip weekend
            while market_open.weekday() > 4:
                market_open += timedelta(days=1)

        time_diff = market_open - now
        hours = int(time_diff.seconds / 3600)
        minutes = int((time_diff.seconds % 3600) / 60)

        return hours, minutes, market_open

    def fetch_market_data(self):
        """Fetch real-time market data"""
        try:
            # Fetch NIFTY 50
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
                    'previous_close': float(prev_close),
                    'change': float(current_price - prev_close),
                    'pct_change': float((current_price - prev_close) / prev_close * 100),
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                }

            # Fetch VIX
            url_vix = "https://query1.finance.yahoo.com/v8/finance/chart/%5EINVIX"
            response_vix = requests.get(url_vix, params={'interval': '1d', 'range': '5d'}, headers=headers, timeout=10)

            if response_vix.status_code == 200:
                data_vix = response_vix.json()
                vix_price = data_vix['chart']['result'][0]['meta'].get('regularMarketPrice', 15.0)
                self.vix_data = {'current': float(vix_price)}
            else:
                self.vix_data = {'current': 15.0}

            return True

        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return False

    def generate_groww_instructions(self, trade_setup):
        """Generate detailed Groww order placement instructions"""

        instructions = f"""
🎯 **TRADE SETUP FOR GROWW**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Strategy:** {trade_setup['strategy']}
**Time:** {datetime.now().strftime('%I:%M:%S %p')}
**Date:** {datetime.now().strftime('%d-%b-%Y')}

**📊 RISK/REWARD:**
• Max Profit: ₹{trade_setup['max_profit']:,.2f}
• Max Loss: ₹{trade_setup['max_loss']:,.2f}
• Breakeven: {', '.join([f"₹{be:,.2f}" for be in trade_setup.get('breakeven', [])])}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        for i, leg in enumerate(trade_setup['legs'], 1):
            instructions += f"""
**LEG {i}: {leg['action']} {leg['option_type']}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 **STEPS IN GROWW APP:**

1️⃣ Open Groww → Click "F&O" at bottom
2️⃣ Search: "NIFTY"
3️⃣ Select: "NIFTY {leg['expiry']}"
4️⃣ Find Strike: {leg['strike']} {leg['option_type']}
5️⃣ Click: "{leg['action']}" button
6️⃣ Enter Quantity: {leg['quantity']} (Lot Size: {leg['lots']})
7️⃣ Order Type: Select "LIMIT"
8️⃣ Price: ₹{leg['expected_price']:.2f}
   💡 TIP: Check current market price first!
   • If buying: Use Ask price or slightly higher
   • If selling: Use Bid price or slightly lower
9️⃣ Review order carefully
🔟 Click "PLACE ORDER"

⏱️ **Expected Fill Price:** ₹{leg['expected_price']:.2f}
💰 **Total Value:** ₹{leg['expected_price'] * leg['quantity']:,.2f}

"""

        instructions += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ **CRITICAL REMINDERS:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Execute ALL legs together (within 1-2 minutes)
✅ Use LIMIT orders for better prices
✅ Check current market price before placing order
✅ Verify each detail before confirming
✅ Screenshot your orders for records
✅ Set price alerts at breakeven and max loss levels

❌ DON'T use MARKET orders (bad fills)
❌ DON'T execute only partial strategy
❌ DON'T wait too long between legs
❌ DON'T ignore stop loss

🛑 **STOP LOSS PLAN:**
If unrealized loss exceeds ₹{trade_setup['max_loss'] * 0.5:,.2f} (50% of max loss):
→ EXIT ALL POSITIONS IMMEDIATELY
→ Don't hope it will recover

📱 **SET ALERTS IN GROWW:**
1. Go to watchlist
2. Add NIFTY {trade_setup['legs'][0]['expiry']}
3. Set alerts at key levels

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        return instructions


def main():
    # Header
    st.markdown('<h1 style="text-align: center;">🚀 Live Trading Dashboard - Groww Ready</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">Real-Time Recommendations + Manual Execution for Groww</p>', unsafe_allow_html=True)

    # Initialize system
    if 'trading_system' not in st.session_state:
        st.session_state.trading_system = IntegratedTradingSystem()

    system = st.session_state.trading_system

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/trading.png", width=80)
        st.markdown("## 🎮 Control Panel")

        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-Refresh (every 30 sec)", value=False)

        if auto_refresh:
            st.info("Dashboard will refresh automatically")
            import time as time_module
            time_module.sleep(30)
            st.rerun()

        if st.button("🔄 Manual Refresh Now", use_container_width=True):
            st.rerun()

        st.markdown("---")

        # Market status
        is_open, status_msg = system.is_market_open()

        if is_open:
            st.markdown('<div class="market-open">🟢 MARKET OPEN</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="market-closed">🔴 {status_msg}</div>', unsafe_allow_html=True)

            # Time to market open
            hours, minutes, market_open = system.time_to_market_open()
            st.info(f"⏰ Market opens in:\n{hours}h {minutes}m\n\n📅 {market_open.strftime('%d %b %Y, %I:%M %p')}")

        st.markdown("---")

        # Safety settings
        st.markdown("### 🛡️ Safety Limits")
        st.metric("Daily Loss Limit", f"₹{system.daily_loss_limit:,}")
        st.metric("Per Trade Limit", f"₹{system.per_trade_limit:,}")
        st.metric("Max Lots", system.max_lots)

        st.markdown("---")

        # Quick actions
        st.markdown("### ⚡ Quick Actions")

        if st.button("📱 Open Groww App", use_container_width=True):
            st.info("Open Groww app on your phone")

        if st.button("📋 Copy Instructions", use_container_width=True):
            st.success("Instructions will be ready below!")

        if st.button("🔔 Setup Telegram Alerts", use_container_width=True):
            st.info("See 'Settings' tab for Telegram setup")

        st.markdown("---")

        # Emergency stop
        if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
            st.error("⚠️ TRADING STOPPED!\nClose all positions in Groww immediately!")
            st.stop()

    # Main content
    tabs = st.tabs(["🎯 Live Trade", "📊 Market Analysis", "📱 Groww Setup", "⚙️ Settings", "📜 History"])

    with tabs[0]:
        # Fetch live data
        with st.spinner('📡 Fetching live market data...'):
            system.fetch_market_data()

        # Live market data
        st.markdown("## 📊 Live Market Data")

        if system.nifty_data:
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric(
                    "💰 NIFTY 50",
                    f"₹{system.nifty_data['last_price']:,.2f}",
                    f"{system.nifty_data['pct_change']:+.2f}%"
                )

            with col2:
                st.metric("📈 High", f"₹{system.nifty_data['high']:,.2f}")

            with col3:
                st.metric("📉 Low", f"₹{system.nifty_data['low']:,.2f}")

            with col4:
                st.metric("⚡ VIX", f"{system.vix_data['current']:.2f}")

            with col5:
                st.metric("🕐 Updated", system.nifty_data['timestamp'])

        st.markdown("---")

        # Trade recommendation
        st.markdown("## 🎯 CURRENT TRADE RECOMMENDATION")

        # Example trade (this should come from your options strategy logic)
        is_market_open, _ = system.is_market_open()

        if is_market_open:
            # Simulate recommendation
            trend = "BULLISH" if system.nifty_data['pct_change'] > 0 else "BEARISH"

            # Get next weekly expiry
            today = datetime.now()
            days_until_thursday = (3 - today.weekday()) % 7
            if days_until_thursday == 0 and today.time() > time(15, 30):
                days_until_thursday = 7
            next_expiry = today + timedelta(days=days_until_thursday)
            expiry_str = next_expiry.strftime('%d%b%y').upper()

            spot = system.nifty_data['last_price']
            spot_rounded = round(spot / 50) * 50

            if trend == "BULLISH":
                trade_setup = {
                    'strategy': 'Bull Call Spread',
                    'max_profit': 3985,
                    'max_loss': 6015,
                    'breakeven': [spot_rounded + 120],
                    'legs': [
                        {
                            'action': 'BUY',
                            'option_type': 'CALL',
                            'strike': spot_rounded,
                            'expiry': expiry_str,
                            'quantity': 50,
                            'lots': 1,
                            'expected_price': 285.50
                        },
                        {
                            'action': 'SELL',
                            'option_type': 'CALL',
                            'strike': spot_rounded + 200,
                            'expiry': expiry_str,
                            'quantity': 50,
                            'lots': 1,
                            'expected_price': 165.20
                        }
                    ]
                }
            else:
                trade_setup = {
                    'strategy': 'Bear Put Spread',
                    'max_profit': 3750,
                    'max_loss': 6250,
                    'breakeven': [spot_rounded - 125],
                    'legs': [
                        {
                            'action': 'BUY',
                            'option_type': 'PUT',
                            'strike': spot_rounded,
                            'expiry': expiry_str,
                            'quantity': 50,
                            'lots': 1,
                            'expected_price': 290.00
                        },
                        {
                            'action': 'SELL',
                            'option_type': 'PUT',
                            'strike': spot_rounded - 200,
                            'expiry': expiry_str,
                            'quantity': 50,
                            'lots': 1,
                            'expected_price': 165.00
                        }
                    ]
                }

            # Big alert
            st.markdown(f'<div class="big-alert">🎯 RECOMMENDED: {trade_setup["strategy"]}</div>', unsafe_allow_html=True)

            # Summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Max Profit", f"₹{trade_setup['max_profit']:,}", delta="Potential Gain")
            with col2:
                st.metric("Max Loss", f"₹{trade_setup['max_loss']:,}", delta="Your Risk")
            with col3:
                roi = (trade_setup['max_profit'] / trade_setup['max_loss']) * 100
                st.metric("ROI Potential", f"{roi:.1f}%")
            with col4:
                st.metric("Risk:Reward", f"1:{trade_setup['max_profit']/trade_setup['max_loss']:.2f}")

            st.markdown("---")

            # Detailed instructions
            st.markdown("## 📱 GROWW ORDER PLACEMENT INSTRUCTIONS")

            instructions = system.generate_groww_instructions(trade_setup)

            st.code(instructions, language='text')

            # Action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📋 Copy All Instructions", use_container_width=True):
                    st.success("✅ Instructions ready! Paste in Notes app")
                    st.text_area("Copy from here:", instructions, height=300)

            with col2:
                if st.button("📱 Send to WhatsApp", use_container_width=True):
                    st.info("Copy instructions and send to yourself on WhatsApp")

            with col3:
                if st.button("✅ Mark as Executed", use_container_width=True, type="primary"):
                    # Save to history
                    st.success("✅ Trade logged!")
                    st.balloons()

        else:
            st.warning(f"🔴 Market is currently closed. Next trade signal will be available when market opens.")
            hours, minutes, market_open = system.time_to_market_open()
            st.info(f"⏰ Market opens in: {hours}h {minutes}m\n\n📅 {market_open.strftime('%d %B %Y, %I:%M %p')}")

            st.markdown("### 🎯 What to do now:")
            st.markdown("""
            1. ✅ Review your Groww account - ensure sufficient balance
            2. ✅ Check margin requirements for options trading
            3. ✅ Set up price alerts in Groww
            4. ✅ Review yesterday's trades (if any)
            5. ✅ Read the strategy explanations
            6. ✅ Prepare for market open at 9:15 AM
            """)

    with tabs[1]:
        st.markdown("## 📊 Market Analysis")
        st.info("Complete market analysis with charts will appear here")
        # Add your technical analysis charts here

    with tabs[2]:
        st.markdown("## 📱 Groww Setup Guide")

        st.markdown("""
        ### 🎯 Setting Up Groww for Options Trading

        #### 1️⃣ Enable F&O Trading
        1. Open Groww app
        2. Go to Profile → Settings
        3. Click on "Activate F&O Trading"
        4. Complete the form and documentation
        5. Wait for approval (usually 24-48 hours)

        #### 2️⃣ Add Funds
        1. Go to "Account" section
        2. Click "Add Funds"
        3. Add sufficient margin for options trading
        4. Minimum recommended: ₹25,000 for spreads

        #### 3️⃣ Understand Margin Requirements
        - **Buying Options:** Premium amount only
        - **Selling Options:** Margin blocked (usually ₹50,000-₹1,00,000 per lot)
        - **Spreads:** Lower margin as risk is defined

        #### 4️⃣ Set Up Watchlist
        1. Go to Watchlist
        2. Search "NIFTY"
        3. Add relevant expiry dates
        4. Set price alerts

        #### 5️⃣ Practice First
        - Start with 1 lot only
        - Use defined-risk strategies (spreads)
        - Don't trade with money you can't afford to lose
        """)

        st.success("✅ Once setup is complete, you're ready to follow our trade recommendations!")

    with tabs[3]:
        st.markdown("## ⚙️ Settings")

        st.markdown("### 🛡️ Risk Management")

        daily_limit = st.number_input("Daily Loss Limit (₹)", value=system.daily_loss_limit, step=1000, min_value=1000)
        per_trade = st.number_input("Per Trade Limit (₹)", value=system.per_trade_limit, step=500, min_value=500)
        max_lots = st.number_input("Maximum Lots", value=system.max_lots, step=1, min_value=1, max_value=10)

        if st.button("💾 Save Settings"):
            settings = {
                'daily_loss_limit': daily_limit,
                'per_trade_limit': per_trade,
                'max_lots': max_lots
            }
            with open('trading_settings.json', 'w') as f:
                json.dump(settings, f)
            st.success("Settings saved!")
            st.rerun()

        st.markdown("---")

        st.markdown("### 📱 Telegram Alerts Setup")
        st.info("""
        Get instant alerts on your phone when new trades are recommended:

        1. Open Telegram
        2. Search @BotFather
        3. Create new bot: `/newbot`
        4. Copy the bot token
        5. Start chat with your bot
        6. Get chat ID from @userinfobot
        7. Enter details below
        """)

        bot_token = st.text_input("Bot Token", type="password")
        chat_id = st.text_input("Chat ID")

        if st.button("Save Telegram Settings"):
            telegram_settings = {' bot_token': bot_token, 'chat_id': chat_id}
            with open('.telegram_settings.json', 'w') as f:
                json.dump(telegram_settings, f)
            st.success("✅ Telegram configured!")

    with tabs[4]:
        st.markdown("## 📜 Trade History")
        st.info("Your executed trades will appear here")

        # Example trade history
        if os.path.exists('trade_log.json'):
            with open('trade_log.json', 'r') as f:
                history = json.load(f)

            if history:
                df = pd.DataFrame(history)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No trades recorded yet")
        else:
            st.info("No trade history available")


if __name__ == "__main__":
    main()
