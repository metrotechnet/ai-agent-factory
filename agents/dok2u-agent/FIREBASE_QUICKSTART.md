# Quick Start: Firebase Frontend Deployment

## One-Time Setup

1. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

2. Login to Firebase:
```bash
firebase login
```

3. Update `.firebaserc` with your project ID (or run `firebase use --add`)

4. Add backend URL to `.env`:
```
BACKEND_URL=https://your-backend-url.run.app
```

## Deploy

### Windows:
```cmd
deploy-frontend.bat
```

### PowerShell/Cross-platform:
```powershell
.\deploy-frontend.ps1
```

### Manual:
```bash
firebase deploy --only hosting
```

## Test Locally

```bash
firebase emulators:start --only hosting
```

Visit: http://localhost:5000

## Files Created

- `firebase.json` - Firebase hosting configuration
- `.firebaserc` - Project reference
- `deploy-frontend.bat` - Windows deployment script  
- `deploy-frontend.ps1` - PowerShell deployment script
- `FIREBASE_DEPLOYMENT.md` - Full documentation

## Notes

- The `public/` folder is auto-generated (gitignored)
- Frontend files are copied from `templates/` and `static/`
- Backend URL is injected into `config.js` during deployment
