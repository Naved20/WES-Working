#!/bin/bash
# Restart application without sudo

echo "============================================================"
echo "RESTARTING APPLICATION"
echo "============================================================"

# Find and kill gunicorn processes
echo ""
echo "1. Finding running processes..."
ps aux | grep -i gunicorn | grep -v grep
ps aux | grep -i "python.*app" | grep -v grep

echo ""
echo "2. Stopping old processes..."
pkill -f "gunicorn.*app:app"
pkill -f "python.*app.py"

sleep 2

echo ""
echo "3. Checking if processes stopped..."
RUNNING=$(ps aux | grep -i gunicorn | grep -v grep | wc -l)
if [ $RUNNING -eq 0 ]; then
    echo "   ✅ All processes stopped"
else
    echo "   ⚠️  Some processes still running"
    ps aux | grep -i gunicorn | grep -v grep
fi

echo ""
echo "============================================================"
echo "APPLICATION STOPPED"
echo "============================================================"
echo ""
echo "Now restart from CloudPanel:"
echo "  1. Go to CloudPanel dashboard"
echo "  2. Sites → mentorship.weslux.lu"
echo "  3. Click 'Restart' button"
echo ""
echo "Or start manually:"
echo "  cd /home/luxment/htdocs/mentorship.weslux.lu/WES-Working"
echo "  gunicorn -w 4 -b 0.0.0.0:8000 app:app --daemon"
echo ""
