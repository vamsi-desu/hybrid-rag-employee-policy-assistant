# Employee Hybrid RAG Agent --- Implementation Guide

## 1. Project Overview

This project is an Employee RAG (Retrieval-Augmented Generation)
application.

It reads employee information from a PDF, parses employee records,
creates embeddings, stores records and metadata in ChromaDB, routes user
questions to the appropriate retrieval strategy, retrieves relevant
records, and uses an OpenAI model to generate the final answer.

The current implementation is best described as **Hybrid RAG with Query
Routing**.

It combines:

-   Semantic/vector retrieval
-   Structured metadata filtering
-   Query routing
-   LLM answer generation
-   Streamlit UI

It is not fully Agentic RAG yet because the current query router is
rule-based.

------------------------------------------------------------------------

## 2. Architecture

``` text
Employee PDF
     |
     v
PDF Loader
     |
     v
Employee Record Parser
     |
     v
Structured Employee Records
     |
     +-----------------------------+
     |                             |
     v                             v
OpenAI Embeddings              Metadata
     |                     employee_id/status/
     |                     department/location
     v                             |
                +------------------+
                |
                v
             ChromaDB
                |
                v
             User Query
                |
                v
           Query Router
                |
       +--------+--------+--------+
       |        |        |        |
       v        v        v        v
   Employee   Status  Department Location
      ID       Filter    Filter    Filter
       |        |        |        |
       +--------+--------+--------+
                |
                v
         Semantic Search
                |
                v
        Retrieved Records
                |
                v
            OpenAI LLM
                |
                v
          Final Answer
                |
                v
          Streamlit UI
```

------------------------------------------------------------------------

## 3. Project Structure

``` text
employee policy rag/
|
├── rag.py
├── app.py
├── test_rag.py
├── implementation.md
|
├── Employee_Details_100 (1).pdf
|
├── storage/
│   └── chroma/
|
└── .venv/
```

  File                  Purpose
  --------------------- ----------------------------
  `rag.py`              Main RAG backend
  `app.py`              Streamlit web application
  `test_rag.py`         Backend/RAG tests
  `implementation.md`   Project documentation
  Employee PDF          Source knowledge
  `storage/chroma/`     Persistent ChromaDB data
  `.venv/`              Python virtual environment

------------------------------------------------------------------------

## 4. Data Ingestion

The PDF contains employee records. Each record contains fields such as:

-   Employee ID
-   Name
-   Department
-   Job title
-   Email
-   Phone
-   Joining date
-   Salary
-   Location
-   Manager
-   Status

The current dataset contains 100 employee records.

------------------------------------------------------------------------

## 5. Employee Record Parsing

A raw employee record is converted into a structured dictionary.

Example:

``` python
{
    "employee_id": "EMP001",
    "name": "Kevin Davis",
    "department": "Engineering",
    "email": "kevin.davis1@company.com",
    "phone": "9553035110",
    "joining_date": "2018-04-05",
    "salary": "61,868",
    "location": "Gurugram",
    "manager": "Jennifer Mehta",
    "status": "Active"
}
```

The parser is important because structured fields can later be used for
exact metadata filtering.

------------------------------------------------------------------------

## 6. Embeddings

Each employee record is converted into an embedding using an OpenAI
embedding model.

Current implementation:

``` text
Number of embeddings: 100
Embedding dimensions: 1536
```

Conceptually:

``` text
Employee Record
      |
      v
Embedding Model
      |
      v
1536-dimensional Vector
```

These vectors are used for semantic similarity retrieval.

------------------------------------------------------------------------

## 7. ChromaDB

ChromaDB stores:

1.  Documents
2.  Embeddings
3.  Metadata

Example metadata:

``` python
{
    "employee_id": "EMP001",
    "status": "Active",
    "department": "Engineering",
    "location": "Gurugram",
    "employee_index": 0,
    "filename": "Employee_Details_100 (1).pdf"
}
```

Metadata makes exact filtering possible.

------------------------------------------------------------------------

## 8. Query Router

The current query router selects a retrieval strategy.

Routes:

``` text
employee_id
status
department
location
semantic
```

Examples:

``` text
Who is EMP001?
        -> employee_id
```

``` text
Which employees are on leave?
        -> status
```

``` text
Which employees are in Engineering?
        -> department
```

``` text
Which employees are in Hyderabad?
        -> location
```

``` text
Who is Kevin Davis?
        -> semantic
```

------------------------------------------------------------------------

## 9. Retrieval Strategies

### Employee ID

Uses exact metadata lookup:

``` python
where={"employee_id": "EMP001"}
```

### Status

Example:

``` text
Which employees are on leave?
```

Uses:

``` python
where={"status": "On Leave"}
```

### Department

Example:

``` text
Which employees work in Engineering?
```

Uses:

``` python
where={"department": "Engineering"}
```

### Location

Example:

``` text
Which employees are in Hyderabad?
```

Uses:

``` python
where={"location": "Hyderabad"}
```

### Semantic Search

Questions that do not match a structured route use vector similarity
search.

Example:

``` text
Who is Kevin Davis?
```

------------------------------------------------------------------------

## 10. Why This Is Hybrid RAG

The system combines:

``` text
Structured Metadata Retrieval
            +
Semantic Vector Retrieval
            =
Hybrid RAG
```

Structured retrieval is better for exact conditions such as:

``` text
status = On Leave
location = Hyderabad
department = Engineering
employee_id = EMP001
```

Semantic retrieval is useful for natural-language questions where exact
filtering is not appropriate.

------------------------------------------------------------------------

## 11. Answer Generation

After retrieval, the relevant records are passed to the LLM.

``` text
User Question
      +
Retrieved Records
      |
      v
     LLM
      |
      v
Final Answer
```

The LLM should answer using the retrieved employee records and should
not invent employee information.

------------------------------------------------------------------------

## 12. Streamlit Application

`app.py` provides the user interface.

Flow:

``` text
User enters question
        |
        v
Streamlit
        |
        v
route_query()
        |
        v
search_chroma()
        |
        v
generate_answer()
        |
        v
Answer displayed
```

The application can display:

-   Retrieval strategy
-   Final answer
-   Retrieved records

------------------------------------------------------------------------

## 13. Running the Project

Activate the virtual environment:

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

``` powershell
python -m pip install openai chromadb streamlit
```

If LangChain Core is actually used by the current code:

``` powershell
python -m pip install langchain-core
```

------------------------------------------------------------------------

## 14. Run the Backend

``` powershell
python rag.py
```

Example questions:

``` text
Which employees are on leave?
```

``` text
Which employees are in Hyderabad?
```

``` text
Who is EMP001?
```

------------------------------------------------------------------------

## 15. Run the Streamlit App

``` powershell
python -m streamlit run app.py
```

Then ask questions through the browser.

Example:

``` text
How many employees are working in Hyderabad?
```

------------------------------------------------------------------------

## 16. Testing with test_rag.py

`test_rag.py` tests the backend independently from Streamlit.

The tests should verify:

### Employee ID

``` text
Who is EMP001?
```

Expected:

``` text
employee_id
```

### Department

``` text
Which employees are in Engineering?
```

Expected:

``` text
department
```

### Location

``` text
Which employees are in Hyderabad?
```

Expected:

``` text
location
```

### Status

``` text
Which employees are on leave?
```

Expected:

``` text
status
```

Run:

``` powershell
python test_rag.py
```

Expected:

``` text
Employee ID Test: PASSED
Department Test: PASSED
Location Test: PASSED
Status Test: PASSED

ALL TESTS PASSED
```

------------------------------------------------------------------------

## 17. Testing Strategy

The RAG should be tested at multiple levels.

### Routing Test

Verify that the correct route is selected.

``` text
Hyderabad
    |
    v
location
```

### Retrieval Test

Verify that records are returned.

``` text
location = Hyderabad
        |
        v
records > 0
```

### Data Accuracy Test

Verify that every returned record satisfies the requested filter.

For example, a Hyderabad query should return only records whose location
metadata is Hyderabad.

### Answer Test

Verify that the generated answer is grounded in the retrieved records.

------------------------------------------------------------------------

## 18. ChromaDB Important Rule

When calling:

``` python
collection.add()
```

the following lists must have equal lengths:

``` text
ids
documents
embeddings
metadatas
```

For 100 employee records:

``` text
ids        = 100
documents  = 100
embeddings = 100
metadatas  = 100
```

Otherwise ChromaDB raises an unequal-length error.

------------------------------------------------------------------------

## 19. Rebuilding ChromaDB

If the metadata schema changes significantly, delete:

``` text
storage/chroma/
```

and rebuild the collection.

This prevents stale metadata from interfering with new retrieval logic.

------------------------------------------------------------------------

## 20. Avoid Unnecessary Dependencies

The current employee RAG can perform its core retrieval directly with:

``` text
OpenAI
+
ChromaDB
```

LangChain is not automatically required for a RAG application.

Only install LangChain packages when the implementation actually imports
or uses them.

------------------------------------------------------------------------

## 21. Current Limitations

The current query router is rule-based.

Conceptually:

``` text
User Query
    |
    v
Python Rules
    |
    v
Retrieval Strategy
```

This means adding completely new query types can require additional
routing logic.

For example:

``` text
Show employees earning more than 100000
```

would require additional structured filtering/aggregation logic.

Therefore the current system is:

``` text
Hybrid RAG
+
Rule-based Query Router
```

It should not be described as fully autonomous Agentic RAG.

------------------------------------------------------------------------

## 22. Next Upgrade

The next meaningful upgrade is an LLM-based query router.

Current:

``` text
User
 |
 v
Rule-based Router
 |
 v
ChromaDB
```

Future:

``` text
User
 |
 v
LLM Query Router
 |
 +--> employee_id
 +--> status
 +--> department
 +--> location
 +--> semantic
 |
 v
ChromaDB
 |
 v
LLM
 |
 v
Answer
```

Keep the existing rule-based router as a fallback while developing the
LLM router.

------------------------------------------------------------------------

## 23. Interview Description

A precise description of the project is:

> I built an employee-focused Hybrid RAG system using OpenAI embeddings
> and ChromaDB. The system combines semantic vector retrieval with
> structured metadata filtering and uses a query-routing layer to select
> the appropriate retrieval strategy for employee ID, status,
> department, location, or semantic queries. The retrieved context is
> then passed to an LLM for grounded answer generation, with a Streamlit
> interface for users.

------------------------------------------------------------------------

## 24. End-to-End Flow

``` text
                    USER
                     |
                     v
              Streamlit UI
                     |
                     v
                User Query
                     |
                     v
               Query Router
                     |
          +----------+----------+
          |          |          |
          v          v          v
       Metadata   Employee ID  Semantic
        Filter      Lookup      Search
          |          |          |
          +----------+----------+
                     |
                     v
                  ChromaDB
                     |
                     v
             Retrieved Records
                     |
                     v
                  OpenAI LLM
                     |
                     v
               Final Answer
                     |
                     v
                Streamlit UI
```

------------------------------------------------------------------------

## 25. Current Project Status

-   PDF ingestion --- Complete
-   Employee record parsing --- Complete
-   OpenAI embeddings --- Complete
-   ChromaDB storage --- Complete
-   Metadata filtering --- Complete
-   Semantic retrieval --- Complete
-   Query routing --- Complete
-   LLM answer generation --- Complete
-   Streamlit UI --- Complete
-   RAG tests --- Added
-   LLM-based query routing --- Future enhancement
-   Full Agentic RAG --- Future enhancement

------------------------------------------------------------------------

## 26. Useful Commands

Activate environment:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

``` powershell
python -m pip install -r requirements.txt
```

Run backend:

``` powershell
python rag.py
```

Run tests:

``` powershell
python test_rag.py
```

Run Streamlit:

``` powershell
python -m streamlit run app.py
```

Stop Streamlit:

``` text
Ctrl + C
```
