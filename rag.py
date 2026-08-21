import os
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

load_dotenv()

CHAT_MODEL = os.getenv(
    "RAG_CHAT_MODEL",
    "gpt-4o-mini"
)

EMBED_MODEL = os.getenv(
    "RAG_EMBED_MODEL",
    "text-embedding-3-small"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
CHROMA_PATH = STORAGE_DIR / "chroma"

DATA_DIR.mkdir(exist_ok=True)
STORAGE_DIR.mkdir(exist_ok=True)
CHROMA_PATH.mkdir(exist_ok=True)


# ============================================================
# 2. OPENAI CLIENT
# ============================================================

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ============================================================
# 3. CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = chroma_client.get_or_create_collection(
    name="employee_records",
    metadata={"hnsw:space": "cosine"}
)


# ============================================================
# 4. LOAD PDF
# ============================================================

def load_pdf(file_path):
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    return text


# ============================================================
# 5. SPLIT EMPLOYEE RECORDS
# ============================================================

def chunk_employee_records(text):
    """
    Convert the employee master data into
    individual employee records.

    Example:

    EMP001 ...
    EMP002 ...
    EMP003 ...

    Each employee becomes one chunk.
    """

    pattern = r"(EMP\d{3}.*?)(?=EMP\d{3}|$)"

    records = re.findall(
        pattern,
        text,
        flags=re.DOTALL
    )

    return [
        record.strip()
        for record in records
        if record.strip()
    ]

# ------------------------------------------------------
# parsing employee records
# ------------------------------------------------------

def parse_employee_record(record):

    parts = record.split()

    employee_id = parts[0]

    # Find email
    email_index = next(
        i for i, value in enumerate(parts)
        if "@" in value
    )

    email = parts[email_index]
    phone = parts[email_index + 1]
    joining_date = parts[email_index + 2]
    salary = parts[email_index + 3]

    # Everything after salary
    remaining = parts[email_index + 4:]

    # Status
    if remaining[-2:] == ["On", "Leave"]:
        status = "On Leave"
        remaining = remaining[:-2]
    else:
        status = remaining[-1]
        remaining = remaining[:-1]

    # Last two words are manager
    manager = " ".join(remaining[-2:])

    # Word before manager is location
    location = remaining[-3]

    # Everything between name and email is
    # department + job title
    name = " ".join(parts[1:3])

    middle = parts[3:email_index]

    # Known departments in this employee dataset
    departments = [
        "Engineering",
        "Human Resources",
        "Marketing",
        "Product",
        "Sales",
        "Operations",
        "Finance",
        "IT"
    ]

    department = None

    for dept in departments:

        dept_parts = dept.split()

        if middle[:len(dept_parts)] == dept_parts:
            department = dept
            break

    if department is None:
        department = middle[0]

    return {
        "employee_id": employee_id,
        "name": name,
        "department": department,
        "email": email,
        "phone": phone,
        "joining_date": joining_date,
        "salary": salary,
        "location": location,
        "manager": manager,
        "status": status
    }

# ============================================================
# 6. CREATE EMBEDDINGS
# ============================================================

def create_embeddings(records):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=records
    )

    return [
        item.embedding
        for item in response.data
    ]


# ============================================================
# 7. STORE EMPLOYEE RECORDS IN CHROMADB
# ============================================================

def store_in_chroma(records, embeddings, filename):

    ids = [
        f"{filename}_{i}"
        for i in range(len(records))
    ]

    metadatas = []

    for i, record in enumerate(records):

        employee = parse_employee_record(record)

        metadatas.append(
            {
                "filename": filename,
                "employee_index": i,
                "employee_id": employee["employee_id"],
                "status": employee["status"],
                "department": employee["department"],
                "location": employee["location"]
            }
        )

    collection.add(
        ids=ids,
        documents=records,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("Employee records stored in ChromaDB.")


# ============================================================
# 8. SEARCH CHROMADB
# ============================================================

def search_chroma(question, top_k=3, where=None):

    question_embedding = create_embeddings(
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        where=where
    )


    return results

def generate_answer(question, retrieved_documents):
    context = "\n\n".join(retrieved_documents)

    prompt = f"""
You are an employee information assistant.

Answer the user's question using only the information
provided in the context below.

If the answer is not present in the context, say:
"I could not find that information in the employee records."

Do not invent or assume information.

Context:
{context}

User question:
{question}
"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Answer questions using only the provided employee records."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content

# -----------------------------------------------
# route route_query
# -----------------------------------------------
# ============================================================
# 9. QUERY ROUTER
# ============================================================

def route_query(question):

    question_lower = question.lower().strip()

    print("\n========== ROUTER DEBUG ==========")
    print("Question:", repr(question_lower))

    # --------------------------------------------------------
    # 1. Status
    # --------------------------------------------------------

    if "on leave" in question_lower:
        print("ROUTE: STATUS")
        return "status", "On Leave"

    if "active employees" in question_lower:
        print("ROUTE: STATUS")
        return "status", "Active"

    # --------------------------------------------------------
    # 2. Department
    # --------------------------------------------------------

    departments = [
        "engineering",
        "human resources",
        "marketing",
        "product",
        "sales",
        "operations",
        "finance",
        "it"
    ]

    for department in departments:

        if department in question_lower:

            print("ROUTE: DEPARTMENT")
            print("Department:", department)

            return "department", department.title()

    # --------------------------------------------------------
    # 3. Location
    # --------------------------------------------------------

    locations = [
        "gurugram",
        "delhi",
        "chennai",
        "bengaluru",
        "ahmedabad",
        "mumbai",
        "noida",
        "hyderabad"
    ]

    for location in locations:

        if location in question_lower:

            print("ROUTE: LOCATION")
            print("Location:", location)

            return "location", location.title()

    # --------------------------------------------------------
    # 4. Employee ID
    # --------------------------------------------------------

    employee_id_match = re.search(
        r"\bEMP\d{3}\b",
        question.upper()
    )

    if employee_id_match:

        employee_id = employee_id_match.group()

        print("ROUTE: EMPLOYEE ID")
        print("Employee ID:", employee_id)

        return "employee_id", employee_id

    # --------------------------------------------------------
    # 5. Semantic search
    # --------------------------------------------------------

    print("ROUTE: SEMANTIC")

    return "semantic", None

def llm_route_query(question):

    prompt = f"""
You are a query router for an employee database.

Classify the user's question into exactly ONE of these categories:

1. employee_id
2. status
3. department
4. location
5. semantic

Rules:

- employee_id → user asks about a specific employee ID such as EMP001
- status → user asks about Active, On Leave, etc.
- department → user asks about Engineering, Finance, Sales, IT, etc.
- location → user asks about a city such as Hyderabad, Delhi, Mumbai, etc.
- semantic → any other employee-related question

Return ONLY this format:

category|value

Examples:

Question: Who is EMP001?
employee_id|EMP001

Question: Which employees are on leave?
status|On Leave

Question: Which employees work in Engineering?
department|Engineering

Question: Which employees are in Hyderabad?
location|Hyderabad

Question: Who is Kevin Davis?
semantic|None

User question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    print("\nLLM Router Output:")
    print(result)

    category, value = result.split("|", 1)

    return category.strip(), value.strip()
# ============================================================
# 9. MAIN PIPELINE
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # 1. PDF path
    # --------------------------------------------------------

    pdf_path = DATA_DIR / "Employee_Details_100 (1).pdf"

    # --------------------------------------------------------
    # 2. Load PDF
    # --------------------------------------------------------

    text = load_pdf(pdf_path)

    print("\nPDF loaded successfully!")
    print("Characters:", len(text))

    # --------------------------------------------------------
    # 3. Split into employee records
    # --------------------------------------------------------

    records = chunk_employee_records(text)

    print("Number of employee records:", len(records))

    print("\nFirst employee record:")
    print(records[0])

    print("\nSecond employee record:")
    print(records[1])

    print("\nTesting employee record parser:")

    for record in records[:10]:

        employee = parse_employee_record(record)

        print("\n", employee)

    # --------------------------------------------------------
    # 4. Create embeddings
    # --------------------------------------------------------

    embeddings = create_embeddings(records)

    print("\nNumber of embeddings:", len(embeddings))
    print("Embedding dimensions:", len(embeddings[0]))

    # --------------------------------------------------------
    # 5. Store records in ChromaDB
    # --------------------------------------------------------

    store_in_chroma(
        records,
        embeddings,
        pdf_path.name
    )

    # --------------------------------------------------------
    # 6. Interactive RAG chatbot
    # --------------------------------------------------------

    print("\nTesting ChromaDB metadata:")
 
    test_results = collection.get(
       limit=10,
       include=["documents", "metadatas"])


    for i in range(len(test_results["documents"])):
        print("\nDocument:")
        print(test_results["documents"][i])

        print("Metadata:")
        print(test_results["metadatas"][i])

    while True:
        question = input("You: ")

        if question.lower() == "exit":
           print("RAG Agent stopped.")
           break

        # ----------------------------------------------------
        # Query Router
        # ----------------------------------------------------

        route, value = route_query(question)

        print("\nQuery route:", route)

        

        # ====================================================
        # RETRIEVAL BASED ON ROUTE
        # ====================================================

        if route == "status":

            print("🔥 STEP 1: REACHED RETRIEVAL")

            results = search_chroma(
                question,
                top_k=100,
                where={
                    "status": value
                }
            )

            

        elif route == "department":

            results = search_chroma(
                question,
                top_k=100,
                where={
                    "department": value
                }
            )



        elif route == "location":

            print("🔥 STEP 2: LOCATION BRANCH")

            results = search_chroma(
                question,
                top_k=100,
                where={
                    "location": value
                }
            )

        elif route == "employee_id":

            results = search_chroma(
                question,
                top_k=1,
                where={
                    "employee_id": value
                }
            )

        else:

            print("🔥 STEP 3: CHROMA SEARCH FINISHED")

            results = search_chroma(
                question,
                top_k=3
            )

        # ====================================================
        # SHOW RETRIEVED RECORDS
        # ====================================================

        print("🔥 STEP 4: AFTER RETRIEVAL")

        print("\nRetrieved records:")


        retrieved_documents = results["documents"][0]

        for i, document in enumerate(
            retrieved_documents,
            start=1
        ):
            print(f"\n--- Result {i} ---")
            print(document)

        # ====================================================
        # GENERATE FINAL ANSWER
        # ====================================================

        answer = generate_answer(
            question,
            retrieved_documents
        )

        print("\nFinal Answer:")
        print(answer)

# from langchain_core.documents import Document

# documents = []

# for employee in employees:
#     documents.append(
#         Document(
#             page_content=(
#                 f"Employee ID: {employee['employee_id']}\n"
#                 f"Name: {employee['name']}\n"
#                 f"Department: {employee['department']}\n"
#                 f"Job Title: {employee['job_title']}\n"
#                 f"Email: {employee['email']}\n"
#                 f"Phone: {employee['phone']}\n"
#                 f"Joining Date: {employee['joining_date']}\n"
#                 f"Salary: {employee['salary']}\n"
#                 f"Location: {employee['location']}\n"
#                 f"Manager: {employee['manager']}\n"
#                 f"Status: {employee['status']}"
#             ),
#             metadata={
#                 "employee_id": employee["employee_id"],
#                 "department": employee["department"],
#                 "source": "employee_data.pdf"
#             }
#         )
#     )

# print("Number of documents:", len(documents))

# print("\nFirst document:")
# print(documents[0].page_content)

# print("\nMetadata:")
# print(documents[0].metadata)

