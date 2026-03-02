<!DOCTYPE html>
<html lang="en">
<body>

<h1>🚀 V8 – AI-Powered Deal Intelligence Platform</h1>

<p>
V8 is an AI-driven backend system designed to manage, analyze, summarize, and semantically search business deals.
It combines conversational AI, document processing, vector search, and structured deal tracking into a single intelligent workflow.
</p>

<hr>

<div class="section">
<h2>📌 Project Overview</h2>

<p>
The system enables users to:
</p>

<ul>
    <li>Create and manage deal conversations</li>
    <li>Automatically extract structured intake fields from chat</li>
    <li>Upload and process deal-related documents (PDFs)</li>
    <li>Generate AI-powered deal summaries</li>
    <li>Store semantic embeddings for advanced retrieval</li>
    <li>Search deals using vector similarity</li>
</ul>

<p>
The architecture integrates FastAPI, Redis, LangGraph, LLMs (Ollama/OpenAI), and vector storage for a fully AI-enhanced deal workflow.
</p>
</div>

<hr>

<div class="section">
<h2>🏗️ System Architecture</h2>

<h3>1️⃣ Backend (FastAPI)</h3>
<ul>
    <li>Handles chat interactions</li>
    <li>Manages deal lifecycle</li>
    <li>Triggers AI workflows</li>
    <li>Processes document uploads</li>
</ul>

<h3>2️⃣ Redis (State Management)</h3>
<ul>
    <li>Stores deal metadata</li>
    <li>Tracks conversation messages</li>
    <li>Maintains intake fields</li>
    <li>Tracks document status</li>
</ul>

<h3>3️⃣ LLM Layer</h3>
<ul>
    <li>Supports Ollama (local LLM)</li>
    <li>Supports OpenAI (optional via environment variable)</li>
    <li>Handles chat responses</li>
    <li>Extracts structured data</li>
    <li>Generates deal summaries</li>
</ul>

<h3>4️⃣ LangGraph Workflow</h3>
<ul>
    <li>Controls deal progression logic</li>
    <li>Determines missing intake fields</li>
    <li>Requests required documents</li>
    <li>Marks deal completion</li>
</ul>

<h3>5️⃣ Document Processing</h3>
<ul>
    <li>Loads PDFs using PyMuPDF</li>
    <li>Cleans and normalizes text</li>
    <li>Extracts structured parameters</li>
    <li>Generates AI summaries</li>
</ul>

<h3>6️⃣ Vector Storage</h3>
<ul>
    <li>Stores deal summaries in a vector database</li>
    <li>Supports semantic similarity search</li>
    <li>Enables intelligent deal retrieval</li>
</ul>
</div>

<hr>

<div class="section">
<h2>📂 Project Structure</h2>

<pre>
v8/
│
├── Backend/
│   ├── main.py                 # FastAPI entry point
│   ├── graph.py                # LangGraph workflow
│   ├── redis_client.py         # Redis state management
│   ├── llm_client.py           # LLM integrations
│   ├── document_processor.py   # PDF processing logic
│   ├── vectore_extractor.py    # Semantic search logic
│   ├── summary_generator.py    # AI deal summarization
│   ├── summary_store.py        # Vector storage logic
│   ├── prompts.py              # System prompts
│   └── test files
│
├── Frontend/
│   └── app.py                  # UI layer (client interface)
│
└── test/                       # Test scripts
</pre>
</div>

<hr>

<div class="section">
<h2>🧠 Deal Workflow Logic</h2>

<h3>Step 1: Deal Creation</h3>
<ul>
    <li>User initiates chat</li>
    <li>System creates a unique <code>deal_id</code></li>
    <li>Redis initializes metadata and intake fields</li>
</ul>

<h3>Step 2: Conversational Intake</h3>
<ul>
    <li>LLM extracts required fields:</li>
    <ul>
        <li>Company Name</li>
        <li>Industry</li>
        <li>Deal Type</li>
        <li>Deal Size</li>
        <li>Geography</li>
        <li>Contact Person</li>
    </ul>
</ul>

<h3>Step 3: Document Request</h3>
<ul>
    <li>If intake fields are complete, system requests documents</li>
</ul>

<h3>Step 4: Document Upload & Processing</h3>
<ul>
    <li>PDF is uploaded</li>
    <li>Text is cleaned and extracted</li>
    <li>AI extracts structured insights</li>
</ul>

<h3>Step 5: Summary Generation</h3>
<ul>
    <li>Full conversation + intake fields → AI summary</li>
    <li>Summary stored in vector database</li>
</ul>

<h3>Step 6: Semantic Search</h3>
<ul>
    <li>User query converted to embeddings</li>
    <li>Vector similarity search retrieves relevant deals</li>
</ul>
</div>

<hr>

<div class="section">
<h2>⚙️ Technology Stack</h2>

<ul>
    <li><strong>FastAPI</strong> – API framework</li>
    <li><strong>Redis</strong> – State management</li>
    <li><strong>LangGraph</strong> – Workflow orchestration</li>
    <li><strong>LangChain</strong> – Document handling</li>
    <li><strong>PyMuPDF</strong> – PDF processing</li>
    <li><strong>Ollama / OpenAI</strong> – LLM support</li>
    <li><strong>Chroma (Vector Store)</strong> – Semantic retrieval</li>
</ul>
</div>

<hr>

<div class="section">
<h2>🔌 API Endpoints</h2>

<h3>Chat Endpoint</h3>
<pre>
POST /chat
</pre>

<p><strong>Request:</strong></p>
<pre>
{
  "email": "user@example.com",
  "deal_id": "optional",
  "message": "User message"
}
</pre>

<p><strong>Response:</strong></p>
<pre>
{
  "deal_id": "uuid",
  "reply": "LLM response",
  "completed": false,
  "documents_requested": false,
  "documents_uploaded": false
}
</pre>
</div>

<hr>

<div class="section">
<h2>🚀 Setup Instructions</h2>

<h3>1️⃣ Install Dependencies</h3>
<pre>
pip install -r requirements.txt
</pre>

<h3>2️⃣ Start Redis</h3>
<pre>
redis-server
</pre>

<h3>3️⃣ Start Ollama (Optional)</h3>
<pre>
ollama run llama3.1:8b
</pre>

<h3>4️⃣ Run Backend</h3>
<pre>
uvicorn v8.Backend.main:app --reload
</pre>
</div>

<hr>

<div class="section">
<h2>🎯 Key Features</h2>

<ul>
    <li>AI-guided conversational deal intake</li>
    <li>Automated document intelligence</li>
    <li>Structured metadata extraction</li>
    <li>LLM-generated deal summaries</li>
    <li>Vector-based semantic search</li>
    <li>Redis-backed persistent state</li>
</ul>
</div>

<hr>

<h2>📈 Future Improvements</h2>
<ul>
    <li>User authentication & authorization</li>
    <li>Multi-document support</li>
    <li>Advanced analytics dashboard</li>
    <li>Cloud deployment support</li>
    <li>Role-based access control</li>
</ul>

<hr>

<h3>👨‍💻 Author</h3>
<p>
V8 – Intelligent Deal Processing Engine
</p>

</body>
</html>
