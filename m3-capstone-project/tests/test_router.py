from agent_humancapital.orchestration.router import route

def test_route_retrieval():
    p = route("find candidates data analyst")
    assert "retrieval" in p.workers

def test_route_interview():
    p = route("generate interview questions for candidate")
    assert "interview" in p.workers
