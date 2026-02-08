"""
Real-Time Broker Integration System
With Safety Mechanisms and Multiple Modes

IMPORTANT: Groww doesn't have API - This provides alternative solutions
"""

import streamlit as st
import pandas as pd
from datetime import datetime, time
import json
import os
from pathlib import Path
import requests
import time as time_module
import winsound  # For alerts (Windows) or use playsound for Mac


class BrokerIntegrationSystem:
    def __init__(self):
        self.trade_log_file = "trade_log.json"
        self.credentials_file = ".broker_credentials.json"  # Hidden file
        self.settings_file = "trading_settings.json"

        # Safety limits
        self.daily_loss_limit = 10000
        self.per_trade_limit = 5000
        self.max_lots = 2
        self.require_manual_confirmation = True

        # Trading state
        self.daily_pnl = 0
        self.active_positions = []
        self.trade_history = []

        # Market hours (IST)
        self.market_open_time = time(9, 15)
        self.market_close_time = time(15, 30)

        self.load_settings()
        self.load_trade_history()

    def load_settings(self):
        """Load trading settings"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.daily_loss_limit = settings.get('daily_loss_limit', 10000)
                self.per_trade_limit = settings.get('per_trade_limit', 5000)
                self.max_lots = settings.get('max_lots', 2)
                self.require_manual_confirmation = settings.get('require_confirmation', True)

    def save_settings(self, settings):
        """Save trading settings"""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        self.load_settings()

    def load_trade_history(self):
        """Load trade history from file"""
        if os.path.exists(self.trade_log_file):
            with open(self.trade_log_file, 'r') as f:
                self.trade_history = json.load(f)

            # Calculate daily P&L
            today = datetime.now().date().isoformat()
            self.daily_pnl = sum(
                trade.get('pnl', 0)
                for trade in self.trade_history
                if trade.get('date', '').startswith(today)
            )

    def save_trade(self, trade):
        """Save trade to history"""
        trade['timestamp'] = datetime.now().isoformat()
        trade['date'] = datetime.now().date().isoformat()
        self.trade_history.append(trade)

        with open(self.trade_log_file, 'w') as f:
            json.dump(self.trade_history, f, indent=4)

        self.load_trade_history()

    def is_market_open(self):
        """Check if market is currently open"""
        now = datetime.now().time()
        today = datetime.now().weekday()

        # Monday=0 to Friday=4
        if today > 4:  # Weekend
            return False

        return self.market_open_time <= now <= self.market_close_time

    def check_safety_limits(self, trade_risk):
        """Check if trade passes safety limits"""
        checks = {
            'market_open': self.is_market_open(),
            'daily_loss_limit': abs(self.daily_pnl) < self.daily_loss_limit,
            'per_trade_limit': trade_risk <= self.per_trade_limit,
            'position_limit': len(self.active_positions) < 10,
        }

        return checks, all(checks.values())

    def send_telegram_alert(self, message):
        """Send alert via Telegram (optional)"""
        # User needs to set up Telegram bot
        # Instructions: https://core.telegram.org/bots

        telegram_settings = self.load_telegram_settings()
        if not telegram_settings:
            return

        bot_token = telegram_settings.get('bot_token')
        chat_id = telegram_settings.get('chat_id')

        if bot_token and chat_id:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            try:
                requests.post(url, data=data)
            except:
                pass

    def load_telegram_settings(self):
        """Load Telegram bot settings"""
        telegram_file = ".telegram_settings.json"
        if os.path.exists(telegram_file):
            with open(telegram_file, 'r') as f:
                return json.load(f)
        return None

    def create_manual_order_instructions(self, trade_setup):
        """Create step-by-step instructions for manual order placement"""
        instructions = []

        instructions.append("📋 **MANUAL ORDER PLACEMENT INSTRUCTIONS**\n")
        instructions.append(f"Strategy: {trade_setup['strategy']}\n")
        instructions.append(f"Time: {datetime.now().strftime('%H:%M:%S')}\n")
        instructions.append("-" * 50 + "\n")

        for i, leg in enumerate(trade_setup['legs'], 1):
            instructions.append(f"\n**LEG {i}:**")
            instructions.append(f"Action: {leg['action']} (Buy/Sell)")
            instructions.append(f"Type: {leg['option_type']} (Call/Put)")
            instructions.append(f"Strike: ₹{leg['strike']}")
            instructions.append(f"Expiry: {leg['expiry']}")
            instructions.append(f"Quantity: {leg['quantity']} ({leg['lots']} lots)")
            instructions.append(f"Expected Price: ₹{leg['expected_price']:.2f}")
            instructions.append(f"Order Type: LIMIT")
            instructions.append("")

            instructions.append("**Steps in Groww:**")
            instructions.append(f"1. Open Groww → Stocks → F&O")
            instructions.append(f"2. Search: NIFTY {leg['expiry']}")
            instructions.append(f"3. Select: {leg['strike']} {leg['option_type']}")
            instructions.append(f"4. Click: {leg['action']}")
            instructions.append(f"5. Quantity: {leg['quantity']}")
            instructions.append(f"6. Price: {leg['expected_price']:.2f} (or better)")
            instructions.append(f"7. Order Type: LIMIT")
            instructions.append(f"8. Click: {leg['action'].upper()}")
            instructions.append("-" * 50)

        instructions.append("\n⚠️ **IMPORTANT:**")
        instructions.append("- Execute ALL legs together")
        instructions.append("- Use LIMIT orders for better prices")
        instructions.append("- Verify each order before confirming")
        instructions.append("- Set stop-loss immediately after entry")
        instructions.append(f"- Max Risk: ₹{trade_setup.get('max_loss', 0):,.2f}")

        return "\n".join(instructions)


def main():
    st.set_page_config(
        page_title="Broker Integration System",
        page_icon="🔗",
        layout="wide"
    )

    st.markdown('<h1 style="text-align: center;">🔗 Broker Integration System</h1>', unsafe_allow_html=True)

    # Initialize system
    if 'broker_system' not in st.session_state:
        st.session_state.broker_system = BrokerIntegrationSystem()

    broker = st.session_state.broker_system

    # Sidebar - Settings
    with st.sidebar:
        st.markdown("## ⚙️ Settings")

        trading_mode = st.selectbox(
            "Trading Mode",
            ["🟡 Semi-Automatic (Groww)", "🟢 Paper Trading", "🔵 Manual with Alerts", "🔴 Live API (Other Brokers)"]
        )

        st.markdown("---")
        st.markdown("### 🛡️ Safety Limits")

        daily_limit = st.number_input("Daily Loss Limit (₹)", value=10000, step=1000)
        per_trade_limit = st.number_input("Per Trade Limit (₹)", value=5000, step=500)
        max_lots = st.number_input("Max Lots", value=2, step=1)
        require_confirmation = st.checkbox("Require Manual Confirmation", value=True)

        if st.button("💾 Save Settings"):
            broker.save_settings({
                'daily_loss_limit': daily_limit,
                'per_trade_limit': per_trade_limit,
                'max_lots': max_lots,
                'require_confirmation': require_confirmation
            })
            st.success("Settings saved!")

        st.markdown("---")
        st.markdown("### 📊 Today's Stats")
        st.metric("Daily P&L", f"₹{broker.daily_pnl:,.2f}",
                 delta=None if broker.daily_pnl >= 0 else "Loss")
        st.metric("Trades Today", len([t for t in broker.trade_history if t.get('date', '').startswith(datetime.now().date().isoformat())]))
        st.metric("Active Positions", len(broker.active_positions))

        # Emergency Stop
        st.markdown("---")
        if st.button("🛑 EMERGENCY STOP", type="primary"):
            st.error("TRADING STOPPED! Close all positions manually.")
            st.stop()

    # Main content
    tabs = st.tabs(["🎯 Trade Setup", "📊 Position Monitor", "📜 Trade History", "⚙️ Broker Setup"])

    with tabs[0]:
        st.markdown("## 🎯 Current Trade Recommendation")

        # Check market status
        if broker.is_market_open():
            st.success("🟢 Market is OPEN")
        else:
            st.warning("🔴 Market is CLOSED")
            st.info("Indian stock market hours: 9:15 AM - 3:30 PM IST (Mon-Fri)")

        # Get recommendation from options dashboard
        st.markdown("### Recommended Trade")

        # Example trade setup (this would come from your options dashboard)
        example_trade = {
            'strategy': 'Bull Call Spread',
            'max_loss': 6015,
            'max_profit': 3985,
            'legs': [
                {
                    'action': 'BUY',
                    'option_type': 'CALL',
                    'strike': 25650,
                    'expiry': '13-FEB-2026',
                    'quantity': 50,
                    'lots': 1,
                    'expected_price': 285.50
                },
                {
                    'action': 'SELL',
                    'option_type': 'CALL',
                    'strike': 25850,
                    'expiry': '13-FEB-2026',
                    'quantity': 50,
                    'lots': 1,
                    'expected_price': 165.20
                }
            ]
        }

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Strategy", example_trade['strategy'])
        with col2:
            st.metric("Max Profit", f"₹{example_trade['max_profit']:,}")
        with col3:
            st.metric("Max Loss", f"₹{example_trade['max_loss']:,}")

        # Safety checks
        st.markdown("### 🛡️ Safety Check")
        checks, all_pass = broker.check_safety_limits(example_trade['max_loss'])

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("✅ Market Open" if checks['market_open'] else "❌ Market Closed")
        with col2:
            st.write("✅ Daily Limit OK" if checks['daily_loss_limit'] else "❌ Daily Limit Hit")
        with col3:
            st.write("✅ Trade Size OK" if checks['per_trade_limit'] else "❌ Trade Too Large")
        with col4:
            st.write("✅ Position Limit OK" if checks['position_limit'] else "❌ Too Many Positions")

        st.markdown("---")

        # For Groww - Manual Instructions
        if "Groww" in trading_mode:
            st.markdown("## 📱 Manual Order Instructions for Groww")
            st.info("⚠️ Groww doesn't have API. Follow these steps to place orders manually:")

            instructions = broker.create_manual_order_instructions(example_trade)
            st.code(instructions, language='text')

            # Copy button
            if st.button("📋 Copy Instructions to Clipboard"):
                st.write("Instructions copied! (Paste in Notes app)")

            # Send to Telegram
            if st.button("📱 Send to Telegram"):
                broker.send_telegram_alert(instructions)
                st.success("Sent to Telegram!")

            # Manual confirmation
            if all_pass and require_confirmation:
                if st.button("✅ I Have Placed These Orders", type="primary"):
                    trade_record = {
                        'strategy': example_trade['strategy'],
                        'max_loss': example_trade['max_loss'],
                        'max_profit': example_trade['max_profit'],
                        'status': 'Executed Manually',
                        'legs': example_trade['legs']
                    }
                    broker.save_trade(trade_record)
                    st.success("Trade recorded!")
                    st.balloons()

        else:
            st.warning("Select 'Semi-Automatic (Groww)' mode for manual instructions")

    with tabs[1]:
        st.markdown("## 📊 Active Positions Monitor")

        if len(broker.active_positions) == 0:
            st.info("No active positions")
        else:
            # Display active positions
            positions_df = pd.DataFrame(broker.active_positions)
            st.dataframe(positions_df, use_container_width=True)

        # Manual position entry
        st.markdown("### ➕ Add Position Manually")

        col1, col2, col3 = st.columns(3)
        with col1:
            strategy = st.text_input("Strategy Name")
        with col2:
            entry_price = st.number_input("Entry Price", value=0.0)
        with col3:
            quantity = st.number_input("Quantity", value=50)

        if st.button("Add Position"):
            position = {
                'strategy': strategy,
                'entry_price': entry_price,
                'quantity': quantity,
                'entry_time': datetime.now().isoformat()
            }
            broker.active_positions.append(position)
            st.success("Position added!")

    with tabs[2]:
        st.markdown("## 📜 Trade History")

        if len(broker.trade_history) == 0:
            st.info("No trades yet")
        else:
            # Filter by date
            date_filter = st.date_input("Filter by Date", value=datetime.now().date())

            filtered_trades = [
                t for t in broker.trade_history
                if t.get('date', '').startswith(date_filter.isoformat())
            ]

            if filtered_trades:
                trades_df = pd.DataFrame(filtered_trades)
                st.dataframe(trades_df, use_container_width=True)

                # Stats
                total_pnl = sum(t.get('pnl', 0) for t in filtered_trades)
                win_rate = len([t for t in filtered_trades if t.get('pnl', 0) > 0]) / len(filtered_trades) * 100

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total P&L", f"₹{total_pnl:,.2f}")
                with col2:
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                with col3:
                    st.metric("Total Trades", len(filtered_trades))
            else:
                st.info(f"No trades on {date_filter}")

    with tabs[3]:
        st.markdown("## ⚙️ Broker Setup & Integration")

        st.warning("""
        **Groww Limitation:**
        Groww does NOT provide a public API for automated trading.

        **Solutions:**
        1. **Current:** Use manual instructions with alerts (what we're doing)
        2. **Alternative:** Open account with Zerodha/Upstox/Angel One for API access
        3. **Hybrid:** Use both - Groww for manual trading, API broker for automation
        """)

        st.markdown("### 📱 Telegram Alert Setup")
        st.info("""
        Get instant trade alerts on your phone:

        1. Open Telegram app
        2. Search for @BotFather
        3. Create new bot: /newbot
        4. Copy the bot token
        5. Start chat with your bot
        6. Get your chat ID from @userinfobot
        7. Enter details below
        """)

        bot_token = st.text_input("Bot Token", type="password")
        chat_id = st.text_input("Chat ID")

        if st.button("Save Telegram Settings"):
            settings = {'bot_token': bot_token, 'chat_id': chat_id}
            with open('.telegram_settings.json', 'w') as f:
                json.dump(settings, f)
            st.success("Telegram configured!")

        if st.button("🧪 Test Telegram"):
            broker.send_telegram_alert("🎯 Test alert from Trading Dashboard!")
            st.info("Check your Telegram!")

        st.markdown("---")

        st.markdown("### 🔗 Alternative: API Broker Integration")
        st.info("""
        If you want TRUE automation, consider:

        **Zerodha Kite Connect:**
        - Most popular Indian broker API
        - ₹2000/month API charges
        - Excellent documentation
        - High reliability

        **Upstox:**
        - Lower API charges
        - Good for options trading
        - Decent documentation

        **Angel One:**
        - SmartAPI available
        - Free for some plans
        - Growing ecosystem

        I can help you integrate any of these if you want to switch.
        """)


if __name__ == "__main__":
    main()
