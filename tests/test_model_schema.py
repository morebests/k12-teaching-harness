"""模型适配边界必须保留结构化检查所需的实际字段。"""

from langchain_google_genai._function_utils import convert_to_genai_function_declarations

from teaching_harness.contracts import Review


def test_Gemini工具格式保留六项检查依据():
    converted = convert_to_genai_function_declarations([Review])
    schema = converted[0].function_declarations[0].parameters
    evidence = schema.properties["evidence"]
    assert set(evidence.properties or {}) == {
        "coverage",
        "mathematics",
        "progression",
        "conditions",
        "evidence",
        "sources",
    }
