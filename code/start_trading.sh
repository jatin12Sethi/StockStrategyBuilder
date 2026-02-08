#!/bin/bash

# Trading Terminal Launcher Script
# This script starts your complete trading system

echo "🚀 Starting Trading Terminal..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Activate virtual environment
source trading_env/bin/activate

# Check if port is already in use
if lsof -ti:8501 > /dev/null 2>&1; then
    echo "⚠️  Port 8501 is already in use"
    echo "🔄 Stopping existing instance..."
    kill -9 $(lsof -ti:8501) 2>/dev/null
    sleep 2
fi

# Start the trading dashboard
echo "📊 Launching Trading Dashboard..."
streamlit run integrated_trading_dashboard.py --server.headless false --server.port 8501 &

# Wait for dashboard to start
sleep 5

# Check if dashboard started successfully
if lsof -ti:8501 > /dev/null 2>&1; then
    echo "✅ Trading Dashboard is LIVE!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌐 Dashboard URL: http://localhost:8501"
    echo "📱 Open this in your browser"
    echo ""
    echo "📊 Features Available:"
    echo "  • Live NIFTY 50 data"
    echo "  • Real-time options strategies"
    echo "  • Groww order instructions"
    echo "  • Risk management tools"
    echo "  • Trade history tracking"
    echo ""
    echo "📖 Strategy Guide: PROFIT_MAXIMIZATION_STRATEGY.md"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎯 Ready to trade!"

    # Open browser (macOS)
    open http://localhost:8501
else
    echo "❌ Failed to start dashboard"
    echo "Check errors above and try again"
fi
