#!/bin/bash
# Fix database permissions for production

echo "============================================================"
echo "FIXING DATABASE PERMISSIONS"
echo "============================================================"

DB_PATH="instance/mentors_connect.db"
DIR_PATH="instance"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Not running as root. Some commands may need sudo."
    USE_SUDO="sudo"
else
    USE_SUDO=""
fi

# Get web server user (usually www-data, nginx, or apache)
if id "www-data" &>/dev/null; then
    WEB_USER="www-data"
elif id "nginx" &>/dev/null; then
    WEB_USER="nginx"
elif id "apache" &>/dev/null; then
    WEB_USER="apache"
else
    echo "❌ Could not find web server user (www-data, nginx, or apache)"
    echo "   Please specify manually: sudo chown YOUR_USER:YOUR_USER $DB_PATH"
    exit 1
fi

echo ""
echo "📋 Current permissions:"
ls -la $DB_PATH
ls -lad $DIR_PATH

echo ""
echo "🔧 Fixing permissions..."

# Fix directory permissions
echo "   Setting directory permissions..."
$USE_SUDO chown -R $WEB_USER:$WEB_USER $DIR_PATH
$USE_SUDO chmod 775 $DIR_PATH

# Fix database file permissions
echo "   Setting database file permissions..."
$USE_SUDO chown $WEB_USER:$WEB_USER $DB_PATH
$USE_SUDO chmod 664 $DB_PATH

echo ""
echo "✅ New permissions:"
ls -la $DB_PATH
ls -lad $DIR_PATH

echo ""
echo "============================================================"
echo "✅ Permissions fixed!"
echo "============================================================"
echo ""
echo "Now restart your application:"
echo "  sudo systemctl restart mentorship"
echo ""
