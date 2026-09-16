"""模型适配边界必须保留结构化检查所需的实际字段。"""

from langchain_google_genai._function_utils import convert_to_genai_function_declarations

from teaching_harness.contracts import Review, YearBlueprint


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


def test_Gemini全年工具保留单元覆盖与知识依据字段():
    converted = convert_to_genai_function_declarations([YearBlueprint])
    schema = converted[0].function_declarations[0].parameters
    assert "narrative" in schema.properties["units"].items.properties
    assert "allocations" in schema.properties["goals"].items.properties
    assert "record_ids" in schema.properties["knowledge_uses"].items.properties


def test_Gemini全年工具能看见固定身份和内容层级():
    schema = (
        convert_to_genai_function_declarations([YearBlueprint])[0]
        .function_declarations[0]
        .parameters
    )
    assert schema.properties["id"].enum == ["curriculum"]
    assert schema.properties["kind"].enum == ["grade"]
