# Quick Start Guide - User History Features

## 🚀 Setup Instructions

### 1. Backend Setup

The backend is already configured! The new user history endpoints are automatically available.

**What was added:**
- New router: `backend/routers/user_history.py`
- Registered in `backend/main.py`

**MongoDB Collections (Auto-created):**
- `chat_history` - Stores chat conversations
- `resume_analyses` - Stores resume uploads & analyses  
- `job_recommendations` - Stores job search results

**No additional setup required!** Just make sure MongoDB is running.

### 2. Frontend Setup

Everything is already integrated! No additional setup needed.

**What was added:**
- New page: `src/pages/UserHistory.jsx`
- Updated: `src/pages/Chatbot.jsx` (with sidebar & persistence)
- Updated: `src/pages/JobRecommendations.jsx` (Indian locations & INR)
- Updated: `src/services/api.js` (new API methods)
- Updated: `src/routes.jsx` (added `/history` route)
- Updated: `src/components/Navbar.jsx` (added History link)

### 3. Start the Application

#### Backend:
```powershell
cd backend
python main.py
```

Backend runs on: `http://localhost:8000`

#### Frontend:
```powershell
npm run dev
```

Frontend runs on: `http://localhost:5173`

### 4. Test the Features

1. **Open** `http://localhost:5173`
2. **Login/Signup** with your credentials
3. **Upload a Resume** → Automatically saved to your history
4. **View Jobs** → Now shows Indian locations and INR salaries
5. **Chat with AI** → Conversations persist, accessible from sidebar
6. **Visit History Page** → See all your past activity

## 📋 Feature Tour

### Chat Persistence
1. Go to `/chatbot`
2. Send a few messages
3. **Refresh the page** → Your chat is still there!
4. Click hamburger menu (mobile) or sidebar (desktop) to see all chats
5. Click "New Chat" to start a fresh conversation
6. Previous chats are saved automatically

### Indian Job Listings
1. Go to `/jobs`
2. Notice:
   - Locations: "Bangalore", "Mumbai", "India (Remote)"
   - Salaries: "₹8-15 LPA" instead of "$80k-$120k"
   - All automatically converted!

### User History Dashboard
1. Go to `/history`
2. See 3 tabs:
   - **Chats**: All your conversations
   - **Resumes**: All your uploaded resumes
   - **Jobs**: All your job search results
3. Click to view or delete any item

## 🔍 Verification Checklist

- [ ] Backend starts without errors
- [ ] Can login/signup
- [ ] Can upload resume (saved to history)
- [ ] Can chat (messages persist after refresh)
- [ ] Jobs show Indian locations (Bangalore, Mumbai, etc.)
- [ ] Salaries shown in INR (₹ LPA format)
- [ ] History page shows all activity
- [ ] Can delete old chats
- [ ] Can resume previous chats
- [ ] Mobile view works (responsive)

## 🐛 Troubleshooting

### Chat not persisting?
- Check if logged in (need JWT token)
- Check browser console for errors
- Verify MongoDB is running
- Check `localStorage.getItem('user')` has user ID

### Jobs not showing Indian locations?
- Check `localStorage.getItem('jobRecommendations')`
- Verify jobs were fetched from API
- Check browser console for conversion errors

### History page empty?
- Verify you're logged in
- Check MongoDB has data for your user ID
- Try uploading a resume or chatting first
- Check network tab for API errors

### Backend errors?
- Ensure MongoDB is running on `mongodb://localhost:27017`
- Check `MONGODB_URL` environment variable
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check `SECRET_KEY` is set for JWT tokens

## 🎯 Key API Endpoints to Test

### Test with curl or Postman:

**Get Chat History:**
```bash
curl "http://localhost:8000/user-history/chat/list?user_id=YOUR_USER_ID"
```

**Save Chat:**
```bash
curl -X POST "http://localhost:8000/user-history/chat/save" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"YOUR_USER_ID","messages":[{"role":"user","content":"Hello","timestamp":"2026-01-25T10:00:00"}]}'
```

**Get Summary:**
```bash
curl "http://localhost:8000/user-history/summary?user_id=YOUR_USER_ID"
```

Replace `YOUR_USER_ID` with actual user ID from MongoDB or localStorage.

## 📱 Mobile Testing

1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device (iPhone, Android)
4. Test:
   - Chat sidebar toggle
   - History page tabs
   - Job cards layout
   - Responsive navigation

## 🎉 Success Criteria

You've successfully set up user history when:

✅ Chats persist across page refreshes  
✅ Jobs show "Bangalore", "Mumbai" instead of "USA", "Remote"  
✅ Salaries display as "₹8-15 LPA" instead of "$80k-$120k"  
✅ History page shows all user activities  
✅ Resume uploads are saved to database  
✅ Can delete and resume old chats  

## 📞 Support

If you encounter issues:
1. Check browser console for errors
2. Check backend terminal for Python errors
3. Verify MongoDB is running: `mongosh` or `mongo`
4. Check `USER_HISTORY_IMPLEMENTATION.md` for detailed docs

---

**Everything is ready to use! Just start the servers and test the features.** 🚀
