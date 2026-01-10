# Quick Start Guide - Running as One Suite

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (check with `python3 --version`)
- **Node.js 14+** (check with `node --version`)
- **npm** (comes with Node.js)
- **MongoDB** (optional but recommended for backend)

### Option 1: Shell Script (Linux/Mac)

```bash
./run-suite.sh
```

### Option 2: Python Orchestrator (Cross-platform) ⭐ RECOMMENDED

```bash
python suite_orchestrator.py start
```

This will:
1. ✅ Check all prerequisites
2. ✅ Set up Python virtual environment
3. ✅ Install all dependencies
4. ✅ Start all services
5. ✅ Show you the URLs to access each service

### Stop All Services

**Shell script:**
```bash
./stop-suite.sh
```

**Python orchestrator:**
```bash
python suite_orchestrator.py stop
```

Or press `Ctrl+C` in the terminal where the suite is running.

---

## 📋 What Gets Started

When you run `./run-suite.sh`, it starts:

1. **Backend API** (FastAPI)
   - URL: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Port: 8000

2. **Frontend** (React/Vite)
   - URL: http://localhost:5173
   - Port: 5173

3. **Influencer System** (Python)
   - Runs as background process
   - Logs: `logs/influencer.log`

---

## 🎯 Running Specific Services Only

### Using Shell Script

```bash
./run-suite.sh --backend-only
./run-suite.sh --frontend-only
./run-suite.sh --influencer-only
```

### Using Python Orchestrator (More Options)

```bash
# Backend only
python suite_orchestrator.py start --backend-only

# Frontend only
python suite_orchestrator.py start --frontend-only

# Influencer only
python suite_orchestrator.py start --influencer-only

# Multiple specific services
python suite_orchestrator.py start --service backend --service frontend

# Check status
python suite_orchestrator.py status

# Restart services
python suite_orchestrator.py restart
```

---

## ⚙️ First-Time Setup

### 1. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Minimum required:**
- `OPENAI_API_KEY` - Required for AI features

**For full functionality:**
- `MONGODB_URL` - For backend database
- `JWT_SECRET_KEY` - For authentication
- Social media API keys (if using influencer posting features)

### 2. MongoDB Setup (Optional but Recommended)

**Option A: Local MongoDB**
```bash
# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongod

# macOS
brew install mongodb-community
brew services start mongodb-community
```

**Option B: Docker MongoDB**
```bash
cd backend
docker-compose up -d mongodb
```

**Option C: MongoDB Atlas (Cloud)**
- Sign up at https://www.mongodb.com/atlas
- Create a cluster
- Get connection string
- Update `MONGODB_URL` in `.env`

### 3. Run the Suite

```bash
./run-suite.sh
```

---

## 🔍 Troubleshooting

### Port Already in Use

If you see "Port XXXX is already in use":

```bash
# Find what's using the port
lsof -i :8000  # For backend
lsof -i :5173  # For frontend

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

### Python Dependencies Issues

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node.js Dependencies Issues

```bash
# Reinstall node modules
rm -rf node_modules package-lock.json
npm install
```

### MongoDB Connection Issues

1. Check if MongoDB is running:
   ```bash
   sudo systemctl status mongod
   # or
   docker ps | grep mongo
   ```

2. Verify connection string in `.env`:
   ```bash
   # Should be something like:
   MONGODB_URL=mongodb://localhost:27017/agentic_ads
   ```

3. Test connection:
   ```bash
   mongosh "mongodb://localhost:27017/agentic_ads"
   ```

### Services Not Starting

Check the logs:
```bash
# View all logs
ls -la logs/

# View specific service log
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/influencer.log
```

---

## 📊 Service Status

### Check What's Running

```bash
# View PID file
cat .suite-pids

# Check processes
ps aux | grep -E "uvicorn|vite|python.*main.py"
```

### Health Checks

**Backend:**
```bash
curl http://localhost:8000/
# Should return: {"message":"AgenticAds Backend API"}
```

**Frontend:**
```bash
curl http://localhost:5173/
# Should return HTML
```

---

## 🛠️ Development Workflow

### Making Changes

1. **Backend changes**: The backend auto-reloads (uvicorn --reload)
2. **Frontend changes**: Vite has hot module replacement
3. **Influencer system**: Restart required for changes

### Restarting Services

```bash
# Stop all
./stop-suite.sh

# Start all
./run-suite.sh
```

### Individual Service Development

**Backend:**
```bash
cd backend
source ../venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
npm run frontend:dev
```

**Influencer:**
```bash
source venv/bin/activate
python main.py
```

---

## 📝 Environment Variables Reference

See `.env.example` for all available configuration options.

**Critical Variables:**
- `OPENAI_API_KEY` - **REQUIRED** for AI features
- `MONGODB_URL` - Required for backend
- `JWT_SECRET_KEY` - Required for authentication

**Optional Variables:**
- Social media API keys (for actual posting)
- Hugging Face token (for enhanced models)
- Analytics tracking IDs

---

## 🐳 Docker Alternative

If you prefer Docker:

```bash
cd backend
docker-compose up
```

This starts:
- MongoDB
- Redis
- Backend API
- Nginx (optional)

Note: Frontend and Influencer system still need to run separately or be added to docker-compose.

---

## 📚 Additional Resources

- **Full Audit Report**: See `AUDIT_REPORT.md`
- **Architecture**: See `architecture.md`
- **Tech Stack**: See `tech-stack.md`
- **Setup Guide**: See `SETUP.md`

---

## ❓ Common Questions

**Q: Can I run this on Windows?**
A: The shell scripts are for Linux/Mac. On Windows, use WSL or run services individually.

**Q: Do I need all services running?**
A: No! Use the `--backend-only` or `--frontend-only` flags to run just what you need.

**Q: How do I update dependencies?**
A: 
```bash
# Python
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Node.js
npm update
```

**Q: Where are logs stored?**
A: All logs are in the `logs/` directory.

**Q: How do I change ports?**
A: Edit the scripts or use environment variables (if supported by the service).

---

## 🆘 Getting Help

1. Check the logs in `logs/` directory
2. Review `AUDIT_REPORT.md` for detailed information
3. Verify all prerequisites are installed
4. Ensure `.env` file is properly configured
5. Check that ports are not in use by other applications

---

**Happy Coding! 🚀**
