
from autoops.ai_client import analyze_with_groq

def test_analyze_with_groq_fallback():
    res = analyze_with_groq("ModuleNotFoundError: No module named 'mypkg.utils.file_manager'", model="test-model")
    assert isinstance(res, str)
