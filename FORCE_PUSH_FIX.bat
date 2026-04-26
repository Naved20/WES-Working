@echo off
echo ========================================
echo    FORCE PUSH FIX - Removing Token
echo ========================================
echo.

REM Step 1: Fetch latest from remote
echo [1/6] Fetching latest from remote...
git fetch origin

REM Step 2: Reset to remote main (clean slate)
echo [2/6] Resetting to remote main...
git reset --hard origin/main

REM Step 3: Delete mcp.json if exists
echo [3/6] Removing mcp.json...
if exist .kiro\settings\mcp.json del .kiro\settings\mcp.json

REM Step 4: Add important files
echo [4/6] Adding important files...
git add templates/certificate.html
git add static/signature/arif.png
git add static/signature/Silvia.png
git add app.py
git add templates/mentor/editmentorprofile.html
git add .gitignore
git add FRONTEND_BACKEND_SYNC_FIXED.md
git add MENTOR_PROFILE_MANDATORY_FIELDS.md

REM Step 5: Commit
echo [5/6] Committing changes...
git commit -m "Add signatures and fix mentor profile mandatory fields"

REM Step 6: Push
echo [6/6] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo    DONE! Check if push was successful
echo ========================================
pause
