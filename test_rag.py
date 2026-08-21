from rag import route_query, search_chroma, generate_answer


def test_employee_id_query():

    question = "Who is EMP001?"

    route, value = route_query(question)

    assert route == "employee_id"
    assert value == "EMP001"

    results = search_chroma(
        question,
        top_k=1,
        where={
            "employee_id": value
        }
    )

    documents = results["documents"][0]

    assert len(documents) == 1

    print("\nEmployee ID Test: PASSED")
    print(documents[0])


def test_department_query():

    question = "Which employees are in Engineering?"

    route, value = route_query(question)

    assert route == "department"
    assert value == "Engineering"

    results = search_chroma(
        question,
        top_k=100,
        where={
            "department": value
        }
    )

    documents = results["documents"][0]

    assert len(documents) > 0

    print("\nDepartment Test: PASSED")
    print("Number of employees:", len(documents))


def test_location_query():

    question = "Which employees are in Hyderabad?"

    route, value = route_query(question)

    assert route == "location"
    assert value == "Hyderabad"

    results = search_chroma(
        question,
        top_k=100,
        where={
            "location": value
        }
    )

    documents = results["documents"][0]

    assert len(documents) > 0

    print("\nLocation Test: PASSED")
    print("Number of employees:", len(documents))


def test_status_query():

    question = "Which employees are on leave?"

    route, value = route_query(question)

    assert route == "status"
    assert value == "On Leave"

    results = search_chroma(
        question,
        top_k=100,
        where={
            "status": value
        }
    )

    documents = results["documents"][0]

    assert len(documents) > 0

    print("\nStatus Test: PASSED")
    print("Number of employees:", len(documents))


if __name__ == "__main__":

    print("================================")
    print("Employee RAG Testing")
    print("================================")

    test_employee_id_query()
    test_department_query()
    test_location_query()
    test_status_query()

    print("\n================================")
    print("ALL TESTS PASSED")
    print("================================")