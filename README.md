# Multi-Agent AI Platform 🤖

A scalable multi-agent architecture where specialized AI assistants can be deployed and managed independently while sharing common infrastructure. Currently featuring Ben Boulanger's nutrition expertise, fitness coaching, and wellness therapy.

## 🏗️ Architecture Overview

```
ai-agent/
├── agents/                    # Individual AI agents
│   ├── ben-nutritionist/     # Ben Boulanger nutrition expert
│   ├── fitness-coach/        # Fitness and workout specialist  
│   └── wellness-therapist/   # Mental health and wellness
├── gateway/                  # API Gateway and routing
├── shared/                   # Shared components
└── infrastructure/           # Terraform and deployment
```

## 🤖 Available Agents

### 🥗 Ben Boulanger - Nutrition Expert
- **Expertise**: 842+ indexed nutrition documents
- **Features**: ChromaDB vector search, multilingual support
- **Specialties**: Meal planning, supplement advice, dietary restrictions

### 💪 Fitness Coach  
- **Expertise**: Workout planning and exercise guidance
- **Features**: Progressive workout plans, form coaching
- **Specialties**: Strength training, cardio, injury prevention

### 🧘 Wellness Therapist
- **Expertise**: Mental health and mindfulness
- **Features**: Stress management, meditation guidance  
- **Specialties**: Anxiety support, work-life balance, emotional wellness

## 🚀 **Quick Start**

### **1. Environment Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export GOOGLE_CLOUD_PROJECT="your-project"
```

### **2. Run API Gateway**
```bash
cd gateway
python main.py
```

### **3. Run Individual Agent**
```bash
cd agents/ben-nutritionist
python app.py
```

## 📁 **Project Structure**
├── scripts/               # Utility scripts
│   ├── extract_docx.py    # Document extraction
│   ├── index_chromadb.py  # Database indexing
│   └── init_chromadb.py   # Database initialization
├── config/                # Secure configuration files
│   ├── style_guides.json  # AI personality and style rules
│   └── system_prompts.json # Multilingual system prompts
├── static/                # Frontend assets
├── templates/             # HTML templates
├── documents/             # Source documents
├── chroma_db/            # Vector database storage
└── app.py                # FastAPI application entry point
```

## ⚙️ Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file with your OpenAI API key:
```env
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. Document Setup
Add your documents (.docx, .txt) to the `documents/` folder structure

## 🛠️ Usage

### Initialize and Index Documents
```bash
# Extract text from Word documents
python scripts/extract_docx.py

# Initialize ChromaDB database
python scripts/init_chromadb.py

# Index documents for search
python scripts/index_chromadb.py
```

### Run the Application
```bash
# Start the web server
python app.py

# Or use PowerShell script
.\start_server.ps1
```

Access the application at **http://localhost:8001**

### Command Line Interface
```bash
# Direct querying (for testing)
python core/query_chromadb.py
```

## 🎯 Key Features

- **🧠 Expert AI Persona**: Configured with Ben Boulanger's nutritional expertise
- **🌍 Multilingual**: Seamless French/English support
- **📊 Smart Indexing**: 842+ document chunks intelligently indexed
- **⚡ Fast Responses**: Optimized retrieval and generation pipeline
- **🔐 Production Ready**: Secure configuration management
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🔧 Technical Stack

- **Backend**: FastAPI, Python 3.12+
- **AI/ML**: OpenAI GPT-4, ChromaDB vector database
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Storage**: Local ChromaDB with SQLite backend
- **Configuration**: JSON-based external configs
- **Security**: Protected configuration files outside web root

## 📊 Performance

- **Document Coverage**: 15+ expert documents indexed
- **Response Time**: < 2 seconds average
- **Accuracy**: High relevance through semantic search
- **Scalability**: Optimized for production deployment

## 🚀 Deployment

The application is containerized and ready for deployment:

```bash
# Build Docker image
docker build -t benboulanger-ai .

# Run container
docker run -p 8001:8001 benboulanger-ai
```

## 🔐 Security

- Configuration files secured in `/config` directory
- No sensitive data exposed through static file serving
- Environment-based API key management
- CORS and security headers configured

## 📝 Requirements

- **Python**: 3.12 or higher
- **Memory**: 2GB+ recommended
- **Storage**: 1GB for documents and database
- **API**: OpenAI API key required
