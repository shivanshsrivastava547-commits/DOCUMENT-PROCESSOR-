from LLM import llm
from intelligent_rag_question_generator import question_generator_prompt

document_type = "PPT"

user_prompt = (
    "Create a 10-slide presentation on quarterly business performance."
)

available_context = (
    "The audience is the executive team. "
    "The company sells software subscriptions."
)

# First, test with a short content plan.
content_plan = """
Create a 10-slide executive presentation on quarterly business performance.

Include:
1. Title and reporting period
2. Executive summary
3. Revenue performance
4. Growth trends
5. Customer metrics
6. Expenses and profitability
7. Business segment analysis
8. Risks and challenges
9. Recommendations
10. Conclusion and next steps

Use verified data for all financial figures. Identify missing information
instead of inventing numbers.
"""

formatted_prompt = question_generator_prompt.format(
    document_type=document_type,
    user_prompt=user_prompt,
    available_context=available_context,
    content_plan=content_plan,
)

print("Prompt length:", len(formatted_prompt))

response = llm.invoke(formatted_prompt)

print("\n===== RAW RESPONSE =====")
print(repr(response.content))

print("\n===== RESPONSE METADATA =====")
print(response.response_metadata)

print("\n===== USAGE METADATA =====")
print(response.usage_metadata)

print("\n===== ADDITIONAL KWARGS =====")
print(response.additional_kwargs)