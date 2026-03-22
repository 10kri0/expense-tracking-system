# TODO: Solve CMD Errors - COMPLETE ✅

## Steps Completed:
- [x] Ran `python app.py` → Flask server starts successfully on http://127.0.0.1:5000 (mongomock handles DB).
- Dependencies already installed globally.

## Next (Optional):
1. [ ] Create venv for isolation: `python -m venv venv`, `venv\Scripts\activate`, `pip install flask flask-login pymongo python-dotenv mongomock click werkzeug`.
2. [ ] Create `.env`: `MONGODB_USE_MOCK=true` (or valid Atlas URI).
3. [ ] Fix Atlas: Update whitelist to your IP (run `curl ifconfig.me` for IP) in Atlas dashboard.
4. [ ] Install local MongoDB: Download from mongodb.com, start service.

App ready: Visit http://127.0.0.1:5000 (Ctrl+C to stop server if running).

