# Complete App Startup Guide

## Prerequisites
- Backend running on `http://localhost:5000`
- Android emulator (Pixel 9) running
- Node.js and npm installed

## Step 1: Start Backend

```bash
cd sinhala_app_backend/api
start_backend.bat/python app.py
```

Wait for:
```
INFO - Loaded 1159 sentences from metadata.csv
INFO - Server will be accessible at http://0.0.0.0:5002
```

## Step 2: Start Frontend

```bash
cd sinhala_app
npx expo start
```

Press `a` to open on Android emulator.

## Step 3: Test the App

### Online Mode (Backend Running)
1. **Sentence Loading**: App should load sentences from backend
2. **Status Indicator**: Green dot showing "Online"
3. **Audio Playback**: Tap "Listen" → Audio plays with word highlighting (purple)
4. **Pronunciation**: Tap "Record" → Speak → See green/red/gray highlighting
5. **Navigation**: Use Previous/Next buttons to switch sentences

### Offline Mode (Backend Stopped)
1. Stop backend (`Ctrl+C`)
2. Restart app or wait for network detection
3. **Status Indicator**: Red dot showing "Offline"
4. **Limited Sentences**: Only 12 easy sentences available
5. **No Audio**: "Listen" button disabled
6. **Simulation Mode**: Recording still works (simulated feedback)

## Features Implemented

### ✅ Backend Integration
- Fetches sentences from `/api/sentences/random`
- Loads audio from `/api/audio/:filename`
- WebSocket for real-time pronunciation feedback

### ✅ Offline Mode
- 12 easy Sinhala sentences for offline use
- Network status detection
- Automatic fallback to offline sentences
- Caching with AsyncStorage

### ✅ Real-Time Word Highlighting
- **During Playback**: Words highlight in purple sequentially
- **After Recording**: Words highlight based on pronunciation:
  - 🟢 Green: Correct (similarity >= 0.7)
  - 🔴 Red: Incorrect (0.4 <= similarity < 0.7)
  - ⚪ Gray: Skipped (similarity < 0.4)

### ✅ User Interface
- Loading states
- Error handling
- Network status indicator
- Sentence navigation (Previous/Next)
- Backend connection status
- Offline mode warning

## Troubleshooting

### "Backend Disconnected" showing
- Check if backend is running: `http://localhost:5000/health`
- Verify emulator can reach `10.0.2.2:5000`
- Check firewall settings

### Audio not playing
- Ensure backend is running
- Check audio files exist in `data/audio/`
- Verify network connection

### Sentences not loading
- Check backend logs for errors
- Verify `metadata.csv` exists
- Check network status

### App crashes on startup
- Clear cache: `npx expo start --clear`
- Reinstall dependencies: `npm install`
- Check for TypeScript errors

## Network Configuration

### Android Emulator
- Uses `10.0.2.2` to access host machine's localhost
- Already configured in `Config.ts`

### Physical Device
- Update `Config.ts`:
  ```typescript
  WEBSOCKET_URL: 'http://YOUR_IP:5000',
  API_BASE_URL: 'http://YOUR_IP:5000',
  ```
- Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

## Testing Checklist

- [ ] Backend starts successfully
- [ ] Frontend loads without errors
- [ ] Sentences load from backend (online mode)
- [ ] Audio plays with word highlighting
- [ ] Recording works
- [ ] Pronunciation feedback shows (green/red/gray)
- [ ] Offline mode activates when backend stops
- [ ] Offline sentences display
- [ ] Navigation buttons work
- [ ] Network status updates correctly

## Next Steps

1. Test on Pixel 9 emulator
2. Verify all features work
3. Test network switching (online ↔ offline)
4. Check pronunciation evaluation accuracy
5. Test with different sentences

**The app is now fully functional and ready for testing!** 🎉
