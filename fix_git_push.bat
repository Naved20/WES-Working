@echo off
echo Fixing Git Push Issue - Removing Figma Token from History
echo.

REM Remove the file from git tracking
git rm --cached .kiro/settings/mcp.json

REM Remove from git history
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .kiro/settings/mcp.json" --prune-empty --tag-name-filter cat -- --all

REM Add .gitignore changes
git add .gitignore

REM Commit the changes
git commit -m "Remove Figma token from git history and add to .gitignore"

REM Force push to remote
git push origin main --force

echo.
echo Done! Now you can push your other changes.
pause
