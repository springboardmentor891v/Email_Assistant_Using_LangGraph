from langsmith import traceable

@traceable
def test_function():
    return "LangSmith is working!"

print(test_function())
