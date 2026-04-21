> # 🎯 Goa Heritage Assistant - Complete Setup Guide

## ⚡ Quick Start (3 Simple Steps)

### Step 1: Start the Backend Server

1. **Double-click:** `START_BACKEND.bat`
2. Wait for the message: `Uvicorn running on http://127.0.0.1:9000`
3. **Keep this window open!**

### Step 2: Start the Frontend App

1. **Open a NEW terminal/command prompt**
2. **Double-click:** `START_FRONTEND.bat`
3. Wait for Chrome to open with the app

### Step 3: Use the App

1. The app will open in Chrome
2. Click the **A.I.** tab in the bottom navigation
3. Click **"The Architecture Expert"** card
4. Type your question: _"Tell me about Goa architecture"_
5. Click the **blue send button** ➤
6. See the AI response! 🎉

---

## 📂 Project Structure

```
final-year-main/
├── START_BACKEND.bat          ← Run this first!
├── START_FRONTEND.bat         ← Run this second!
├── backend/
│   ├── index.html            (Chat preview)
│   ├── parse.py
│   ├── pyproject.toml
│   └── app/
│       ├── main.py           (Backend server)
│       ├── infer.py
│       ├── llm_client.py
│       └── test.py
└── flutterapp/
    ├── lib/
    │   └── src/
    │       ├── screens/
    │       │   └── ai_screen.dart    (Chat interface)
    │       ├── services/
    │       └── ...
    └── pubspec.yaml
```

---

## 🔧 Manual Commands (If Scripts Don't Work)

### Start Backend (Copy & Paste in Terminal):

```bash
cd C:\Users\user\Downloads\final-year-main\final-year-main\backend\app
pip install -r requirements.txt
python main.py
```

### Start Frontend (Copy & Paste in ANOTHER Terminal):

```bash
cd C:\Users\user\Downloads\final-year-main\final-year-main\flutterapp
flutter run -d chrome
```

---

## 🎯 What Each Screen Does

### Feature Cards Screen

- Shows "The Time Machine" (Not active yet)
- Shows "The Architecture Expert" (Click to activate chat)

### Chat Interface

- Type questions about Goa architecture
- Send button triggers AI response
- See messages with markdown formatting
- Auto-scroll to latest messages
- Back button to return to feature cards

---

## ⚠️ Troubleshooting

### Problem: "Connection Failed" Error

**Solution:** Backend is not running

1. Check if `START_BACKEND.bat` is still open
2. If closed, run it again
3. Wait for `Uvicorn running on http://127.0.0.1:9000`

### Problem: App won't open in Chrome

**Solution:** Flutter not installed

1. Download Flutter: https://flutter.dev
2. Run: `flutter doctor` in terminal
3. Fix any issues it reports
4. Try `START_FRONTEND.bat` again

### Problem: "Port 9000 already in use"

**Solution:** Kill existing process

```bash
netstat -ano | findstr :9000
taskkill /PID <PID> /F
```

Then run `START_BACKEND.bat` again

### Problem: Python not found

**Solution:** Install Python

1. Download: https://www.python.org
2. Check "Add Python to PATH" during installation
3. Run `START_BACKEND.bat` again

---

## 📊 Features

✅ **AI Chat Interface**

- Real-time responses from backend
- Markdown formatting in responses
- Auto-scroll messages
- Typing indicator

✅ **Feature Cards**

- "The Architecture Expert" button
- Clean card design
- Easy navigation

✅ **Full Mobile UI**

- Bottom navigation (Maps, History, A.I., Profile)
- Responsive design
- Works on mobile & web

---

## 🚀 Testing the Chat

**Question:** "Tell me about Aguada Fort"
**Expected Response:** Information about the fort's architecture and history

**Question:** "What are Portuguese influences in Goa?"
**Expected Response:** Details about Portuguese architectural styles

---

## 📞 If Something Still Doesn't Work

1. Check console for error messages
2. Make sure BOTH terminals are running (Backend + Frontend)
3. Wait 30 seconds after starting backend before opening frontend
4. Refresh the browser (Ctrl+R or F5)
5. Restart both services from scratch

---

**Everything should now work! Follow the 3 steps at the top. 🎉**
