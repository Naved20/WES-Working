# 🚨 Quick Fix: Remove Figma Token & Push Code

## Problem
GitHub ne push block kar diya kyunki `.kiro/settings/mcp.json` mein Figma token hai.

## ✅ Solution (3 Steps)

### Step 1: Remove file from git tracking
```bash
git rm --cached .kiro/settings/mcp.json
```

### Step 2: Commit this change
```bash
git commit -m "Remove Figma token file from git tracking"
```

### Step 3: Push everything
```bash
git push origin main
```

---

## 🎯 Complete Commands (Copy-Paste)

```bash
git rm --cached .kiro/settings/mcp.json
git commit -m "Remove Figma token file from git tracking"
git push origin main
```

---

## ✅ After Push Success

Production server par:
```bash
git pull origin main
kill -9 $(lsof -t -i:8000)
python3 -m gunicorn -w 4 -b 127.0.0.1:8000 app:app --daemon
```

---

## 📝 Note

- `.kiro/settings/mcp.json` ab `.gitignore` mein hai
- Ye file local machine par rahegi but git mein track nahi hogi
- Production server par manually create karni hogi (agar chahiye to)
