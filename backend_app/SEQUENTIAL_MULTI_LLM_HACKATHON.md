# Sequential Multi-LLM Orchestration System with Memory & Logging

## 🏆 Hackathon Project: Vyamit AI

### 📋 System Overview

**System Name:** Sequential Multi-LLM Orchestration System with Memory & Logging

**Core Innovation:** Intelligent model fallback system that tries models in order of speed and capability, with full conversation memory and detailed logging.

### 🔄 Execution Pipeline

```
User Input
    ↓
Preprocessing
    ↓
Master Prompt Generation
    ↓
Sequential Model Execution
    ↓
1. Qwen (Fast Primary) → Success? → Return
    ↓ (if failed)
2. Gemini (Smart Fallback) → Success? → Return  
    ↓ (if failed)
3. Gemma (Final Fallback) → Return
    ↓
Response Validation
    ↓
Memory Storage
    ↓
Structured Terminal Logging
    ↓
API Response
```

### 🤖 Model Configuration

#### 1. **Qwen/Qwen2.5-7B-Instruct** (Primary)
- **Role:** Fast primary model
- **Source:** Hugging Face
- **Strengths:** Speed, multilingual support
- **Use Case:** Most queries, billing tasks

#### 2. **Gemini-1.5-Flash** (Smart Fallback)
- **Role:** Intelligent fallback
- **Source:** Google AI Studio
- **Strengths:** Reasoning, complex queries
- **Use Case:** When Qwen fails or complex reasoning needed

#### 3. **Google/Gemma-2B** (Final Fallback)
- **Role:** Reliable final option
- **Source:** Hugging Face
- **Strengths:** Consistency, small size
- **Use Case:** When both Qwen and Gemini fail

### 🧠 Memory System

**Technology:** LangChain ConversationBufferMemory

**Features:**
- Persistent conversation history
- Context-aware responses
- Memory retrieval for follow-up queries
- Conversation threading

**Implementation:**
```python
memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="chat_history",
    input_key="input",
    output_key="output"
)
```

### 📊 Logging System

**Structured Terminal Output:**
- Timestamp with milliseconds
- Raw user input
- Preprocessed input
- Models tried in sequence
- Successful model identification
- Response validation status
- Execution time breakdown
- Memory context
- Error details (if any)

**Example Log Output:**
```
================================================================================
🔍 DETAILED PROCESSING LOG
================================================================================
⏰ TIMESTAMP: 2026-03-29 15:20:10.123
👤 USER INPUT: '2 kilo chawal 50 rupaye kilo'
🔧 PREPROCESSED: '2 kilo chawal 50 rupaye kilo'
⏱️  TOTAL EXECUTION TIME: 2.456s

🤖 MODEL EXECUTION:
   📋 Models Available: QWEN, GEMINI, GEMMA
   🎯 Successful Model: QWEN
   ✅ Validation Status: PASSED

📤 RESPONSE DETAILS:
   📏 Length: 156 characters
   📝 Content: [{"item": "chawal", "quantity": "2 kg", "price_per_unit": 50, "total_price": 100}]

🧠 CONVERSATION CONTEXT:
   👤 User: Hello, how are you?
   🤖 Assistant: I'm doing well! How can I help you with your grocery needs today?
   👤 User: 2 kilo chawal 50 rupaye kilo
   🤖 Assistant: [{"item": "chawal", "quantity": "2 kg", "price_per_unit": 50, "total_price": 100}]
================================================================================
```

### 🎯 Master Prompt

**Unified Prompt for All Models:**

```
You are VYAMIT AI - a multilingual intelligent assistant for grocery and market systems.

LANGUAGE SUPPORT:
- English
- Hindi  
- Hinglish (Hindi-English mix)

CORE CAPABILITIES:
1. BILLING TASKS → Return structured JSON
2. PRICE QUERIES → Return price information
3. GENERAL QUERIES → Provide helpful responses

BILLING TASK RULES:
- Extract: item name, quantity, price per unit
- Convert to standard units (kg, liter, piece)
- Calculate total price accurately
- Output ONLY clean JSON format:
[
  {
    "item": "item_name",
    "quantity": "number_with_unit",
    "price_per_unit": number_or_null,
    "total_price": number_or_null
  }
]

PRICE QUERY RULES:
Return structured format:
{
  "item": "item_name",
  "price": "price_with_currency",
  "unit": "kg/liter/piece",
  "source": "market_info"
}

GENERAL QUERY RULES:
- Provide short, practical answers
- Focus on grocery/market context
- Be helpful and conversational

STRICT REQUIREMENTS:
- No extra text in JSON responses
- No hallucination of prices
- Clean, structured output only
- Maintain conversation context

CONVERSATION HISTORY:
[Previous conversation context here]

USER INPUT: {user_input}

RESPONSE:
```

### 🚀 Installation & Setup

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Environment Configuration
```bash
# Required API Keys in .env
HUGGINGFACE_API_TOKEN=your_hf_token
GEMINI_API_KEY=your_gemini_key
```

#### 3. Start the System
```bash
# Start the FastAPI server
python start_server.py

# Or use uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 🧪 Testing & Demo

#### 1. Run Hackathon Demo
```bash
# Complete automated demo
python test_sequential_llm_hackathon.py

# API endpoint testing
python test_sequential_api.py
```

#### 2. API Endpoints

**Base URL:** `http://localhost:8000/sequential-llm`

**Endpoints:**
- `POST /query` - Process user query
- `GET /conversation-history` - Get chat history
- `GET /performance-stats` - System performance
- `GET /system-info` - System information
- `POST /demo-test` - Hackathon demo
- `POST /clear-memory` - Clear conversation memory

#### 3. Example API Usage

```python
import requests

# Process a query
response = requests.post(
    "http://localhost:8000/sequential-llm/query",
    json={
        "text": "2 kilo chawal 50 rupaye kilo",
        "include_history": True
    }
)

result = response.json()
print(f"Model Used: {result['model_used']}")
print(f"Response: {result['response']}")
print(f"Execution Time: {result['execution_time']}s")
```

### 📈 Performance Metrics

**Tracked Metrics:**
- Total requests processed
- Success rate per model
- Average response time
- Model usage distribution
- Memory conversation count
- Validation pass rate

**Expected Performance:**
- Qwen: ~70% of queries (fast responses)
- Gemini: ~25% of queries (complex reasoning)
- Gemma: ~5% of queries (final fallback)
- Average response time: <3 seconds

### 🎯 Hackathon Demo Scenarios

#### 1. **Billing Task (Hindi/English Mix)**
```
Input: "2 kilo chawal 50 rupaye kilo aur 1 liter doodh 60 rupaye"
Expected: JSON billing response with calculated totals
```

#### 2. **Price Query (English)**
```
Input: "What is the current price of tomatoes per kg?"
Expected: Structured price information
```

#### 3. **General Query (Hinglish)**
```
Input: "Kya aap mujhe vegetables ki list de sakte hain?"
Expected: Helpful response in context
```

#### 4. **Follow-up Conversation**
```
Input: "Add 3 kg onions at 40 rupees per kg to my previous bill"
Expected: Context-aware billing update using memory
```

#### 5. **Complex Billing (Multiple Items)**
```
Input: "I need 2 kg rice, 1 liter oil, 500g sugar, and 1 kg dal. Rice is 60/kg, oil 120/liter, sugar 45/kg, dal 80/kg"
Expected: Complete JSON billing structure
```

### 🔧 Technical Architecture

#### Core Components:
1. **SequentialMultiLLMService** - Main orchestration service
2. **ModelResponse** - Structured response handling
3. **ProcessingLog** - Comprehensive logging
4. **ConversationBufferMemory** - Memory management
5. **FastAPI Router** - API endpoints

#### Key Features:
- **Async Processing** - Non-blocking execution
- **Response Validation** - Quality assurance
- **Error Handling** - Graceful fallbacks
- **Performance Tracking** - Real-time metrics
- **Memory Management** - Conversation context

### 🏆 Hackathon Advantages

1. **Innovation:** First-of-its-kind sequential model orchestration
2. **Reliability:** Triple fallback ensures response availability
3. **Performance:** Optimized for speed with intelligent routing
4. **Memory:** Conversation-aware responses
5. **Transparency:** Complete execution visibility
6. **Scalability:** Easy to add more models
7. **Multilingual:** Supports English, Hindi, Hinglish

### 🚀 Future Enhancements

1. **Dynamic Routing** - ML-based model selection
2. **Custom Models** - Domain-specific fine-tuned models
3. **Caching Layer** - Response caching for common queries
4. **Load Balancing** - Multiple model instances
5. **Analytics Dashboard** - Real-time performance monitoring
6. **A/B Testing** - Model performance comparison

### 📞 Support & Documentation

**Demo Commands:**
```bash
# Quick test
curl -X POST "http://localhost:8000/sequential-llm/query" \
     -H "Content-Type: application/json" \
     -d '{"text": "2 kilo chawal 50 rupaye kilo"}'

# System info
curl "http://localhost:8000/sequential-llm/system-info"

# Performance stats
curl "http://localhost:8000/sequential-llm/performance-stats"
```

**Troubleshooting:**
- Ensure all API keys are set in `.env`
- Check internet connection for model access
- Verify Python dependencies are installed
- Monitor terminal logs for detailed debugging

---

## 🎉 Ready for Hackathon Presentation!

This system demonstrates cutting-edge AI orchestration with practical applications for grocery and market systems. The combination of speed, reliability, memory, and transparency makes it a winning hackathon solution.