# Vyamit AI Backend

FastAPI backend for the Vyamit AI voice-powered billing application with LangChain + Hugging Face integration.

## 🚀 NEW: LangChain + Hugging Face Integration

**MAJOR UPDATE**: Migrated from Google Gemini API to LangChain + Hugging Face for open-source AI capabilities!

### ✅ What's New
- **AI Model**: Now using `google/gemma-2-27b-it` via Hugging Face
- **Framework**: LangChain for better AI workflow management  
- **Features**: Chat history, conversation memory, embeddings
- **Cost**: Free tier with Hugging Face (2000 requests/day)

### 🔧 Quick Migration
```bash
# Automatic setup (recommended)
python quick_start_langchain.py

# Manual setup
python install_langchain_deps.py
python test_langchain_setup.py
```

📖 **Full Guide**: See [LANGCHAIN_MIGRATION_GUIDE.md](LANGCHAIN_MIGRATION_GUIDE.md)

---

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Server
```bash
# Option 1: Using startup script
python start_server.py

# Option 2: Direct run
cd app
python main_simple.py
```

### 4. Test Server
```bash
python test_endpoints.py
```

## 📡 API Endpoints

### Base URLs
- **Local Development**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/api/test` | API test |
| GET | `/api/database/test` | Database connectivity test |
| GET | `/api/v1/users` | Get users |
| GET | `/api/v1/items` | Get items |
| GET | `/api/v1/bills` | Get bills |

## 🗄️ Database Configuration

### Supabase PostgreSQL (NEW PROJECT)
- **Host**: `db.lhafpdiovrxxvxyqemtg.supabase.co`
- **Database**: `postgres`
- **Port**: `5432`
- **Password**: `VyamitAI12fgco`
- **Supabase URL**: `https://lhafpdiovrxxvxyqemtg.supabase.co`
- **Connection**: Currently using REST API (direct PostgreSQL connection has network issues)

### Environment Variables
Create `.env` file with:
```env
DATABASE_URL=postgresql://postgres:VyamitAI12fgco@db.lhafpdiovrxxvxyqemtg.supabase.co:5432/postgres
SUPABASE_URL=https://lhafpdiovrxxvxyqemtg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxoYWZwZGlvdnJ4eHZ4eXFlbXRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MDgzNDEsImV4cCI6MjA5MDI4NDM0MX0.Td5ELvaDoOW3ek1yAUARTkuUrZSKOGAUSk477DzveyA
SECRET_KEY=your_secret_key_here
```

## 🧪 Testing

### Connection Tests
```bash
# Test Supabase API
python test_supabase_api.py

# Test PostgreSQL connection
python test_connection.py

# Test all endpoints
python test_endpoints.py
```

## 📁 Project Structure

```
backend_app/
├── app/
│   ├── __init__.py
│   ├── main.py              # Full FastAPI app with database
│   ├── main_simple.py       # Simple FastAPI app (currently used)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration settings
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py      # Database connection
│   │   └── models.py        # SQLAlchemy models
│   ├── api/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── main/
│       └── __init__.py
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies
├── .env_config             # Environment variables
├── start_server.py         # Server startup script
├── test_connection.py      # Database connection test
├── test_supabase_api.py    # Supabase API test
├── test_endpoints.py       # API endpoints test
└── README.md              # This file
```

## 🔧 Development

### Adding New Endpoints
1. Edit `app/main_simple.py`
2. Add your endpoint function
3. Test with `python test_endpoints.py`

### Database Integration
1. Configure Supabase connection in `app/core/config.py`
2. Define models in `app/db/models.py`
3. Use `app/main.py` for full database integration

## 🚨 Current Status

✅ **Working:**
- FastAPI server running on port 8000
- All API endpoints responding
- CORS configured for frontend
- Virtual environment set up
- Dependencies installed

⚠️ **Issues:**
- Direct PostgreSQL connection has network/DNS issues
- Using REST API approach as alternative
- Need to implement actual Supabase integration

## 🎯 Next Steps

1. ✅ Set up virtual environment
2. ✅ Install dependencies  
3. ✅ Create basic FastAPI server
4. ✅ Test all endpoints
5. 🔄 Implement Supabase REST API integration
6. 🔄 Add authentication endpoints
7. 🔄 Add inventory management endpoints
8. 🔄 Add billing endpoints

## 📞 Support

If you encounter issues:
1. Check if virtual environment is activated
2. Verify all dependencies are installed
3. Test endpoints with `python test_endpoints.py`
4. Check server logs for errors