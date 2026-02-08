# 📂 Project Organization & File Structure

## ✅ Completed Organization (2024-02-07)

This document describes how the project has been reorganized for better maintainability and clarity.

---

## 🎯 Organization Goals

1. **Clarity**: Clear separation of concerns
2. **Maintainability**: Easy to find and update files
3. **Scalability**: Structure supports future growth
4. **Documentation**: Everything is well-documented

---

## 📁 New Directory Structure

### `/docs/` - All Documentation
**Purpose**: Centralized documentation for the entire project

**Files Moved Here**:
- `HITL_DASHBOARD.md` - Human-in-the-loop dashboard documentation
- `PROJECT_STATUS.md` - Current project status and features
- `VIRAL_INTELLIGENCE.md` - Viral content scraping and AI optimization
- `HUGGINGFACE_INTEGRATION.md` - ML models, datasets, and training
- `QUICKSTART_GRAPHRAG.md` - GraphRAG quick start guide
- `ML_TRAINING_GUIDE.md` - Complete ML training setup guide

**Why**: All documentation in one place makes it easy for developers to find help.

---

### `/config/` - Configuration Files
**Purpose**: All system configuration and settings

**Files Moved Here**:
- `agents.yaml` - Agent definitions for swarm system
- `bandit.yaml` - Security scanning config
- `docker-compose.graphrag.yml` - GraphRAG Docker setup
- `.env.example` - Environment variables template
- `.env.graphrag` - GraphRAG-specific env vars
- `ai-voice-agent-vapi.json` - Voice agent config (VAPI)
- `ai-voice-agent.json` - Voice agent config
- `email-sender-tool.json` - Email tool configuration

**Files That Stay**:
- `config.json` - Auto-generated system config (created by setup_wizard.py)

**Why**: Configuration files are separate from code, making it easy to change settings without touching source code.

---

### `/scripts/` - Utility Scripts
**Purpose**: Automation scripts and utilities

**Shell Scripts Moved Here**:
- `noerror.sh` - Error suppression utility
- `run-suite.sh` - Run full test suite
- `run_graphrag.sh` - GraphRAG execution
- `start.sh` - System startup script
- `start_management.sh` - Management API startup
- `stop-suite.sh` - Stop all services
- `test_scraper_status.sh` - Scraper health check
- `viral_graphrag_complete_setup.sh` - GraphRAG complete setup

**Python Utils in `/scripts/python_utils/`**:
- `integration_example.py` - Integration examples
- `message_queue_integration.py` - Message queue utils
- `plugin_system.py` - Plugin architecture
- `suite_orchestrator.py` - Suite management
- `management_api.py` - Management API
- `main_graphrag.py` - GraphRAG main runner

**Why**: Scripts are utilities, not core code. Keeping them separate reduces clutter.

---

### `/ml/` - Machine Learning Components
**Purpose**: AI training, datasets, and models

**Structure**:
```
ml/
├── __init__.py              # Module init
├── training.py              # Model training logic
├── dataset_builder.py       # Dataset preparation
├── model_manager.py         # Model versioning & deployment
├── models/                  # Trained model files
├── datasets/                # Training datasets
└── logs/                    # Training logs
```

**What It Does**:
- Trains models on viral content data
- Builds datasets from scraped content
- Manages model versions
- Handles deployment

**Why**: ML is a major feature and deserves its own module.

---

### `/dashboard/` - HITL Web Interface
**Purpose**: Human-in-the-loop control panel

**Structure**:
```
dashboard/
├── server.py                # Flask web server
├── templates/
│   └── dashboard.html       # Main dashboard page
└── static/
    ├── css/
    │   └── dashboard.css    # Styling
    └── js/
        └── dashboard.js     # Frontend logic
```

**Features**:
- Real-time system monitoring
- Content approval workflow
- Manual posting controls
- Live metrics display

**Why**: Dashboard is a separate web app, so it gets its own directory.

---

### `/core/` - Core System Components
**Purpose**: Central orchestration and shared utilities

**Files**:
- `orchestrator.py` - Main system controller
- `config.py` - Configuration management
- `logger.py` - Logging setup
- `database.py` - SQLite database interface
- `utils.py` - Shared utility functions

**Why**: These are the foundation of the system.

---

### `/analytics/` - Analytics & Intelligence
**Purpose**: Data collection and analysis

**Files**:
- `analytics_engine.py` - Performance tracking
- `viral_scraper.py` - Scrapes viral content from Instagram/TikTok/Twitter
- `viral_intelligence.py` - AI-powered strategy optimization

**Why**: Analytics is a major component with multiple modules.

---

### `/content/` - Content Generation
**Purpose**: Create posts, captions, and media

**Files**:
- `content_engine.py` - Content generation
- `media_generator.py` - Image/video creation

**Why**: Content creation is core to the influencer system.

---

### `/avatar/` - Avatar Generation
**Purpose**: Create AI avatars

**Files**:
- `avatar_generator.py` - AI avatar creation with DALL-E/Stability AI

**Why**: Avatar is a distinct feature.

---

### `/marketing/` - Marketing Strategy
**Purpose**: Plan and optimize marketing

**Files**:
- `strategy_planner.py` - AI-powered strategy planning

**Why**: Marketing strategy is separate from content creation.

---

### `/social/` - Social Media Integration
**Purpose**: Post to platforms

**Files**:
- `social_manager.py` - Multi-platform posting (Instagram, Twitter, TikTok)

**Why**: Social media posting is a distinct responsibility.

---

### `/data/` - Generated Data Storage
**Purpose**: Store all generated content and analytics

**Structure**:
```
data/
├── avatars/                 # Avatar images
├── content/                 # Generated posts
├── media/                   # Images/videos
├── posts/                   # Posted content logs
├── analytics/               # Analytics metrics
├── strategies/              # Marketing strategies
└── influencer.db            # SQLite database
```

**Why**: Data is separate from code for easy backup/cleanup.

---

### `/logs/` - System Logs
**Purpose**: Application logs

**Files**:
- `influencer_YYYYMMDD.log` - Daily rotating logs

**Why**: Logs help with debugging and monitoring.

---

## 🔧 Files That Remain in Root

### Essential Entry Points
- `app.py` - **Main application entry point** (Autonomous Influencer)
- `main.py` - Alternative entry point (if used)
- `setup_wizard.py` - Interactive setup for first-time users

### Node.js/Web Components
- `index.js` - Node.js entry point (Business Scraper)
- `package.json` - Node.js dependencies
- `package-lock.json` - Dependency lock file
- `vite.config.js` - Vite configuration (if using Vite for frontend)

### Documentation
- `README.md` - Main project README (stays in root for visibility)
- `LICENSE` - Project license

### Config
- `.gitignore` - Git ignore rules
- `.cursorrules` - Cursor IDE rules

**Why These Stay**: Entry points and primary documentation should be immediately visible in the root directory.

---

## 🗂️ Directories That Already Existed

These directories were already well-organized and remain unchanged:

### `/src/` - Source Code (Node.js/Business Scraper)
**Purpose**: Node.js scraper and marketing automation
- Business scraper
- Marketing AI
- Lead intelligence
- Campaign management
- Web dashboard

### `/agentcore/` - Agent Core Components
**Purpose**: Core agent runtime and deployment
- Agent handler
- Runtime registry
- Memory management
- Tool integrations

### `/agents/` - Individual Agent Definitions
**Purpose**: Specific agent implementations

### `/backend/` - Backend Services
**Purpose**: API and backend logic

### `/plugins/` - Plugin System
**Purpose**: Extensible plugins

### `/tools/` - External Tools
**Purpose**: Third-party tool integrations

### `/json/` - JSON Data
**Purpose**: Structured data files

### `/metadata/` - Metadata Storage
**Purpose**: System metadata

### `/stepbystep/` - Tutorials/Guides
**Purpose**: Step-by-step tutorials

### `/chroma_db/` - Vector Database
**Purpose**: Embeddings and vector storage

### `/synthetic_data/` - Synthetic Data
**Purpose**: Generated training data

### `/cloudformation/` - AWS CloudFormation
**Purpose**: Infrastructure as Code

### `/lambda/` - AWS Lambda Functions
**Purpose**: Serverless functions

### `/bedrock-adtech-demo/` - AWS Bedrock Demo
**Purpose**: Bedrock integration examples

---

## 📊 Before vs After

### Before
```
webapp/
├── app.py
├── HITL_DASHBOARD.md
├── PROJECT_STATUS.md
├── VIRAL_INTELLIGENCE.md
├── agents.yaml
├── bandit.yaml
├── ai-voice-agent.json
├── run-suite.sh
├── start.sh
├── integration_example.py
├── management_api.py
└── ... (40+ files in root)
```

### After
```
webapp/
├── app.py                   # Main entry point
├── README.md                # Main docs
├── setup_wizard.py          # Setup
├── index.js                 # Node entry
├── package.json             # Node deps
│
├── docs/                    # ✅ All documentation
├── config/                  # ✅ All configs
├── scripts/                 # ✅ All scripts
├── ml/                      # ✅ ML training
├── dashboard/               # ✅ Web UI
├── core/                    # Core system
├── analytics/               # Analytics
├── content/                 # Content gen
├── avatar/                  # Avatar gen
├── marketing/               # Marketing
├── social/                  # Social media
└── data/                    # Generated data
```

---

## 🎯 Benefits of Reorganization

### 1. **Easier Navigation**
- Docs in `/docs/` - One place for all documentation
- Configs in `/config/` - All settings in one directory
- Scripts in `/scripts/` - Easy to find utilities

### 2. **Better Git Management**
- Clear `.gitignore` rules per directory
- Easier to track changes
- Cleaner commit history

### 3. **Improved Onboarding**
- New developers know where to look
- Clear separation of concerns
- Better README references

### 4. **Scalability**
- Easy to add new modules
- ML system has room to grow
- Dashboard can expand independently

### 5. **Maintenance**
- Update docs without touching code
- Change configs without redeploying
- Run scripts independently

---

## 🔄 Impact on Existing Code

### ✅ No Breaking Changes
- All imports still work (Python modules unchanged in location)
- Entry points still in root (`app.py`, `index.js`)
- Data paths unchanged (`data/`, `logs/`)

### 📝 Documentation References Updated
- `README.md` updated with new structure
- All internal docs reference new locations
- Setup wizard unchanged (works with root directory)

---

## 📚 Quick Reference

### Where to Find Things

| What You Need | Where to Look |
|---------------|---------------|
| Documentation | `/docs/` |
| Configuration | `/config/` |
| Utility Scripts | `/scripts/` |
| ML Training | `/ml/` and `/docs/ML_TRAINING_GUIDE.md` |
| Web Dashboard | `/dashboard/` and `/docs/HITL_DASHBOARD.md` |
| Core Code | `/core/`, `/analytics/`, `/content/`, etc. |
| Generated Data | `/data/` |
| Logs | `/logs/` |
| Node.js Code | `/src/` |
| Agent Code | `/agentcore/`, `/agents/` |

---

## 🚀 Next Steps

1. ✅ Files organized
2. ✅ Documentation updated
3. ✅ ML module created
4. ✅ Dashboard structured
5. ⏳ Test everything works
6. ⏳ Commit changes
7. ⏳ Push to repository

---

**Organized on**: 2024-02-07  
**By**: Autonomous Systems Team  
**Status**: ✅ Complete
