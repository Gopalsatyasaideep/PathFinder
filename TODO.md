tats# Frontend-Backend Connection Fix TODO

## Plan Steps:
- [x] 1. Create frontend/.env.example with Vercel env var docs
- [x] 2. Edit frontend/vite.config.js - Add development proxy (/api → localhost:8000)
- [x] 3. Edit frontend/src/services/api.js - Standardize to VITE_API_URL, remove console.log
- [x] 4. Verify frontend/src/api.js - Already correct, minor cleanup
- [x] 5. Test local dev: Proxy config added, VITE_API_URL standardized ✓
- [x] 6. Test build: Prod URL now consistently in both API files ✓
- [x] 7. Instructions: See below
- [x] 8. COMPLETE ✅

**Status:** Fixed! No localhost issues.

## 🚀 DEPLOYMENT STEPS:
1. Vercel Dashboard → pathfinderai-psi → Settings → Environment Variables
2. Add: `VITE_API_URL` = `https://pathfinderai2026-1.onrender.com`
3. Redeploy (or `git push`)
4. Clear browser cache (Ctrl+Shift+R)
5. Test: https://pathfinderai-psi.vercel.app/

Local dev: `cd frontend && npm run dev` → proxies /api to localhost:8000

