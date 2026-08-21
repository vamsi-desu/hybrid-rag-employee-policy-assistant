import streamlit as st

from rag import (
    route_query,
    search_chroma,
    generate_answer
)

st.set_page_config(
    page_title="Employee RAG Assistant",
    page_icon="🤖"
)

st.title("🤖 Employee RAG Assistant")

question = st.text_input(
    "Ask your question:",
    placeholder="Which employees are in Hyderabad?"
)

if st.button("Ask"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        # -----------------------------
        # Query Router
        # -----------------------------

        route, value = route_query(question)

        st.info(
            f"Retrieval strategy: {route}"
        )

        # -----------------------------
        # Retrieval
        # -----------------------------

        if route == "status":

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

            results = search_chroma(
                question,
                top_k=3
            )

        # -----------------------------
        # Retrieved documents
        # -----------------------------

        retrieved_documents = results["documents"][0]

        # -----------------------------
        # Generate answer
        # -----------------------------

        answer = generate_answer(
            question,
            retrieved_documents
        )

        st.subheader("Answer")

        st.write(answer)

        # -----------------------------
        # Show retrieved records
        # -----------------------------

        with st.expander("View retrieved records"):

            for i, document in enumerate(
                retrieved_documents,
                start=1
            ):

                st.write(f"**Result {i}**")

                st.code(document)