# Legal AI Backend

A production-ready FastAPI backend service for legal awareness and information retrieval, converted from the open-source [LawGlance](https://github.com/lawglance/lawglance) project (Apache 2.0 licensed).

## Features

✅ **RAG-Powered Legal Q&A**: Retrieval-Augmented Generation using ChromaDB and OpenAI  
✅ **Citation Support**: Every answer includes verifiable citations from legal sources  
✅ **Safety-First**: Built-in checks to refuse illegal guidance requests  
✅ **Production-Ready**: Clean architecture, error handling, and logging  
✅ **FastAPI Backend**: RESTful API with automatic OpenAPI documentation  
✅ **Legal Disclaimer**: Automatically includes disclaimer with every response  

## Architecture

```
app/
├── main.py          # FastAPI application with /chat endpoint
├── rag.py           # Core RAG logic and LLM integration
├── vectorstore.py   # ChromaDB vector store management
└── __init__.py      # Package initialization
```

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Pre-populated ChromaDB database (from LawGlance project)

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd legal_ai_backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   ```

5. **Verify ChromaDB database exists**:
   ```bash
   # Make sure the vector database is at:
   # lawglance/chroma_db_legal_bot_part1/
   ```

## Usage

### Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

#### POST `/chat` - Process Legal Query

**Request:**
```json
{
  "query": "What are the fundamental rights guaranteed by the Indian Constitution?"
}
```

**Response:**
```json
{
  "answer": "The Indian Constitution guarantees several fundamental rights...\n\n**Disclaimer:** This is general legal information, not legal advice.",
  "citations": [
    {
      "source_title": "Constitution of India",
      "source": "constitution.pdf",
      "snippet": "Part III of the Constitution deals with Fundamental Rights...",
      "section": "Article 12-35",
      "page": "8"
    }
  ],
  "has_context": true
}
```

#### GET `/health` - Health Check

**Response:**
```json
{
  "status": "healthy",
  "message": "Legal AI Backend is running",
  "vector_store_loaded": true
}
```

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### Using cURL

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the right to equality under Indian law?"}'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"query": "What is the right to equality under Indian law?"}
)

result = response.json()
print(result["answer"])
print("\nCitations:")
for citation in result["citations"]:
    print(f"- {citation['source_title']}: {citation['snippet'][:100]}...")
```

### Using JavaScript/Fetch

```javascript
fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: 'What is the right to equality under Indian law?'
  })
})
.then(res => res.json())
.then(data => {
  console.log(data.answer);
  console.log('Citations:', data.citations);
});
```

## Key Features

### 1. Context-Based Answering
The system only answers from retrieved context. If insufficient information is found:
```json
{
  "answer": "I don't have enough verified information in my knowledge base to answer that precisely.\n\n**Disclaimer:** This is general legal information, not legal advice.",
  "citations": [],
  "has_context": false
}
```

### 2. Safety Protocol
Illegal query detection automatically refuses requests for illegal guidance:
```json
{
  "answer": "I cannot provide guidance on illegal activities. If you have questions about legal compliance or your rights, I'm happy to help with that instead.\n\n**Disclaimer:** This is general legal information, not legal advice.",
  "citations": [],
  "has_context": false
}
```

### 3. Automatic Citations
Every answer includes verifiable citations with:
- Source title and filename
- Relevant text snippet
- Section numbers (when available)
- Page numbers (when available)

### 4. Legal Disclaimer
Every response automatically includes:
> **Disclaimer:** This is general legal information, not legal advice.

## Legal Knowledge Domains

The system currently covers:
- 🇮🇳 Indian Constitution
- 📜 Bharatiya Nyaya Sanhita, 2023 (BNS)
- ⚖️ Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)
- 📋 Bharatiya Sakshya Adhiniyam, 2023 (BSA)
- 🛡️ Consumer Protection Act, 2019
- 🚗 Motor Vehicles Act, 1988
- 💻 Information Technology Act, 2000
- 👥 Sexual Harassment of Women at Workplace Act, 2013
- 👶 Protection of Children from Sexual Offences Act, 2012

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `CHROMA_DB_PATH` | Path to ChromaDB directory | `lawglance/chroma_db_legal_bot_part1` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `RELOAD` | Enable auto-reload | `False` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

## Development

### Project Structure

```
legal_ai_backend/
├── app/
│   ├── __init__.py       # Package initialization
│   ├── main.py           # FastAPI app and endpoints
│   ├── rag.py            # RAG system logic
│   └── vectorstore.py    # Vector store management
├── lawglance/            # Cloned LawGlance project
│   └── chroma_db_legal_bot_part1/  # Vector database
├── .env                  # Environment variables
├── .env.example          # Example environment file
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Adding New Features

1. **Add new endpoints**: Edit `app/main.py`
2. **Modify RAG logic**: Edit `app/rag.py`
3. **Change vector store config**: Edit `app/vectorstore.py`

## Deployment

### Docker (Future)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY lawglance/chroma_db_legal_bot_part1/ ./lawglance/chroma_db_legal_bot_part1/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

The service can be deployed to:
- **AWS**: EC2, ECS, Lambda (with warmer)
- **Google Cloud**: Cloud Run, GKE, Compute Engine
- **Azure**: App Service, Container Instances, AKS
- **Heroku**: Direct deployment with Procfile

## License

This project is derived from [LawGlance](https://github.com/lawglance/lawglance) which is licensed under Apache 2.0.

## Disclaimer

This is a legal awareness tool providing general information only. It does not constitute legal advice. For specific legal issues, consult a qualified attorney.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Support

For issues or questions:
- Check the [API documentation](http://localhost:8000/docs)
- Review the logs for error messages
- Ensure ChromaDB is properly loaded
- Verify OpenAI API key is valid

---

Built with ❤️ using FastAPI, LangChain, and OpenAI
