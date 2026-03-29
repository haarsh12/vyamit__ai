# 🚀 Vector RAG System - Quick Start Guide

## Overview
This system connects your Supabase inventory with AI-powered vector search, supporting multilingual queries in Hindi, English, and Hinglish.

## 🎯 What This Does
```
Inventory (Supabase) → Vector Embeddings → User Query → Top 10+ Matches → AI Response
```

## 📋 Prerequisites
- ✅ Supabase database with `item` table
- ✅ Python virtual environment
- ✅ Environment variables in `.env` file

## 🚀 Quick Setup (3 Steps)

### Step 1: Setup Environment
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
.\setup_vector_rag.ps1
```

### Step 2: Setup Supabase Database
1. Go to your Supabase Dashboard → SQL Editor
2. Copy and run the entire content of `supabase_vector_setup.sql`
3. This will:
   - ✅ Enable vector extension
   - ✅ Add embedding column to item table
   - ✅ Create vector index for fast search
   - ✅ Create match_items() function

### Step 3: Test the System
```bash
python test_complete_vector_rag.py
```

## 🧪 What the Test Does

### 1. Dependency Check
- ✅ Verifies all packages are installed
- ✅ Tests database connection
- ✅ Loads embedding model

### 2. Automatic Embedding
- 🧠 Generates embeddings for all inventory items
- 💾 Stores them in Supabase vector column
- 📊 Shows progress with full debug output

### 3. Multilingual Testing
Tests these sample queries:
- `tamatar ka rate kya hai` (Hinglish - tomato)
- `प्याज का भाव बताओ` (Hindi - onion)  
- `rice ka price kitna hai` (Hinglish - rice)
- `dal moong` (Hindi - lentils)
- `oil` (English - oil)

### 4. Interactive Mode
- 💬 Type any query in Hindi/English/Hinglish
- 🎯 Get 10+ matches with similarity scores
- 🔍 Full debug information for every step

## 📊 Expected Output

```
🚀 VECTOR RAG SYSTEM TEST
================================

📦 Loading intfloat/multilingual-e5-small model...
✅ Model loaded in 2.34 seconds

🔍 SEARCHING INVENTORY
========================
❓ Query: 'tamatar ka rate kya hai'
🧠 Embedding text: 'query: tamatar ka rate kya hai'
⚡ Query embedded in 0.045s

📊 Found 12 matches above threshold 0.1

🎯 TOP MATCHES FOR: 'tamatar ka rate kya hai'
--------------------------------------------------
 1. 🟢 Tomato                | 0.847 | ₹25/kg
     Also known as: tamatar, टमाटर
 2. 🟡 Cherry Tomato         | 0.723 | ₹45/kg
 3. 🟡 Onion                 | 0.654 | ₹30/kg
     Also known as: pyaz, प्याज
 4. 🟠 Potato                | 0.612 | ₹20/kg
 5. 🟠 Capsicum              | 0.587 | ₹35/kg
...
```

## 🔧 Configuration Options

### Adjust Match Count
```python
# Get more matches (default: 15)
results = rag_system.search_inventory(query, top_k=20)
```

### Adjust Similarity Threshold
```python
# Lower threshold = more matches (default: 0.1)
results = rag_system.search_inventory(query, similarity_threshold=0.05)
```

### Debug Levels
All operations print detailed debug information:
- 🧠 Embedding generation time
- 📊 Similarity scores
- 🔍 Database query details
- 📈 Performance metrics

## 🎯 Production Integration

### Use in Your API
```python
from vector_rag_system import VectorRAGSystem

# Initialize once (expensive operation)
rag_system = VectorRAGSystem()

# Use in your endpoint
@app.post("/search")
async def search_inventory(query: str):
    results = rag_system.search_inventory(query, top_k=10)
    return {"matches": results}
```

### Performance Tips
- ✅ Initialize VectorRAGSystem once at startup
- ✅ Embed new items immediately when added
- ✅ Use appropriate top_k (10-15 is usually enough)
- ✅ Cache frequent queries if needed

## 🐛 Troubleshooting

### Common Issues

**❌ "vector extension not found"**
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

**❌ "match_items function not found"**
- Re-run the complete `supabase_vector_setup.sql`

**❌ "No matches found"**
- Check if items have embeddings: `SELECT COUNT(*) FROM item WHERE embedding IS NOT NULL`
- Lower similarity threshold: `similarity_threshold=0.05`

**❌ Model loading slow**
- First time downloads ~500MB model
- Subsequent runs are fast (cached)

### Debug Mode
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎉 Success Indicators

✅ **All tests pass**
✅ **10+ matches for each query**  
✅ **Multilingual search working**
✅ **Similarity scores > 0.6 for relevant items**
✅ **Sub-second query response time**

## 📞 Support

If you encounter issues:
1. Check the debug output in terminal
2. Verify all environment variables are set
3. Ensure Supabase setup is complete
4. Test with simple English queries first

---

🚀 **Ready to go!** Your Vector RAG system is now production-ready with full multilingual support and detailed debugging.