# AI-Powered Hybrid RAG Employee Policy Assistant

An AI-powered **Hybrid Retrieval-Augmented Generation (RAG)** application that allows users to ask questions about employee and HR policy documents and receive relevant answers based on the provided knowledge base.

The system combines document retrieval with an LLM to reduce hallucinations and provide answers grounded in the available employee-policy information.

## 🚀 Project Overview

Traditional LLMs may not have access to an organization's private or frequently changing information.

This project uses a **Hybrid RAG architecture** to retrieve relevant information from the organization's documents before generating an answer.

The application can be used to answer questions such as:

* What is the work-from-home policy?
* How many days can employees work from home?
* What is an employee's department?
* Who is an employee's manager?
* What is an employee's designation?
* What is an employee's joining date?
* Which employees belong to a particular department?

## 🏗️ Architecture

```text
                    User Query
                        │
                        ▼
                ┌───────────────┐
                │ Query/Input   │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Hybrid        │
                │ Retrieval     │
                └───────┬───────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
      Semantic/Vector        Keyword/Other
         Retrieval             Retrieval
             │                     │
             └──────────┬──────────┘
                        ▼
                 Relevant Context
                        │
                        ▼
                ┌───────────────┐
                │ LLM /         │
                │ Generation    │
                └───────┬───────┘
                        │
                        ▼
                 Grounded Answer
```

## 🔍 Why Hybrid RAG?

A single retrieval method is not always sufficient.

**Vector/semantic retrieval** is useful when the user asks a question using different wording from the source document.

For example:

> "Can employees work remotely?"

can retrieve information related to:

> "Employees are permitted to work from home two days per week."

Keyword-based retrieval can be useful when the query contains exact terms such as employee IDs, names, department names, or policy keywords.

Combining retrieval approaches can improve the chances of finding the correct information.

## 🛠️ Technologies Used

* Python
* Streamlit
* OpenAI API
* ChromaDB
* Vector Embeddings
* Retrieval-Augmented Generation (RAG)
* Hybrid Retrieval
* PDF document processing
* Git & GitHub

## 📁 Project Structure

```text
hybrid-rag-employee-policy-assistant/
│
├── app.py
├── rag.py
├── test_rag.py
├── implementation.md
├── requirements.txt
├── .env.example
├── .gitignore
│
└── data/
    └── Employee Policy / Employee Data Documents
```

## 📌 Main Files

### `app.py`

Contains the Streamlit application and user interface.

### `rag.py`

Contains the main RAG implementation, including document processing, retrieval, and answer generation.

### `test_rag.py`

Used for testing the RAG functionality.

### `implementation.md`

Contains implementation details and development notes.

### `requirements.txt`

Contains the Python dependencies required to run the project.

### `.env.example`

Provides the required environment-variable format without exposing the actual API key.

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/vamsi-desu/hybrid-rag-employee-policy-assistant.git
```

### 2. Navigate to the project

```bash
cd hybrid-rag-employee-policy-assistant
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the API key

Create a `.env` file in the project root.

Use:

```text
OPENAI_API_KEY=your_api_key_here
```

Never commit your actual API key to GitHub.

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

## 🧪 Example Queries

You can test the application with questions such as:

```text
What is the work from home policy?
```

```text
How many days per week can employees work from home?
```

```text
Who is the manager of EMP001?
```

```text
Which department does EMP001 belong to?
```

```text
What is the designation of Kevin Davis?
```

## 🎯 Key Learning Outcomes

Through this project, I implemented and explored:

* Document ingestion
* Text processing
* Chunking
* Embedding generation
* Vector database storage
* Semantic retrieval
* Hybrid retrieval concepts
* Context retrieval
* LLM-based answer generation
* RAG pipeline development
* Streamlit application development
* Environment-variable management
* Git and GitHub project management

## 🔮 Future Improvements

Possible improvements include:

* Add a dedicated keyword/BM25 retriever
* Add a cross-encoder reranker
* Add retrieval evaluation metrics
* Add citation/source display in answers
* Add conversation memory
* Add support for multiple document formats
* Add automated RAG evaluation
* Add authentication and role-based access
* Deploy the application to a cloud platform

## ⚠️ Disclaimer

This project is intended for educational and demonstration purposes.

Do not upload confidential employee information, personal data, API keys, or other sensitive organizational information to a public repository.

## 👨‍💻 Author

**Vamsi Desu**

GitHub:
https://github.com/vamsi-desu
