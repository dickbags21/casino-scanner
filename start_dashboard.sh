#!/bin/bash
# Start Casino Scanner Dashboard

echo "🎰 Starting Casino Scanner Dashboard..."
echo ""

# Check if dashboard is already running
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "⚠️  Dashboard is already running on http://localhost:8000"
    echo "   Stop it first with: pkill -f start_dashboard.py"
    exit 1
fi

# Start dashboard
cd "$(dirname "$0")"
python3 start_dashboard.py > /tmp/casino_dashboard.log 2>&1 &

DASHBOARD_PID=$!
echo "✅ Dashboard starting (PID: $DASHBOARD_PID)"
echo ""
echo "📊 Dashboard will be available at: http://localhost:8000"
echo "📝 Logs: /tmp/casino_dashboard.log"
echo ""
echo "Waiting for dashboard to start..."

# Wait for dashboard to be ready
for i in {1..10}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ Dashboard is ready!"
        echo ""
        echo "Open in browser: http://localhost:8000"
        exit 0
    fi
    sleep 1
done

echo "⚠️  Dashboard may still be starting. Check logs: tail -f /tmp/casino_dashboard.log"
exit 0


