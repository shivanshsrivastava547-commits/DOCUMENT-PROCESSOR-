
from langchain_core.prompts import PromptTemplate

ppt_content_prompt = PromptTemplate(
    input_variables=["user_prompt", "retrieved_information"],
    template="""
You are an expert business presentation content generator.

Your task is to generate structured content for a PowerPoint presentation.

USER REQUEST:
{user_prompt}

RETRIEVED INFORMATION:
{retrieved_information}

STRICT INSTRUCTIONS:

1. Generate presentation content based on the user's request.
2. Use retrieved information as the factual source.
3. Never invent statistics, financial figures, dates, percentages,
   business events, or metrics.
4. If information is unavailable, explicitly mention
   "Data not available in the provided sources".
5. Recommendations must be clearly distinguished from factual findings.
6. Keep slide content concise and suitable for executive presentations.
7. Generate an appropriate number of slides based on the request.
8. Do not include explanations outside the JSON.

OUTPUT FORMAT:

Return ONLY valid JSON using this exact structure:

{{
    "slides": [
        {{
            "title": "Presentation title",
            "content": [
                "First key point",
                "Second key point",
                "Third key point"
            ]
        }}
    ]
}}

JSON RULES:
- The root must be a JSON object.
- The root must contain a "slides" array.
- Each slide must contain a string "title".
- Each slide must contain a "content" array of strings.
- Use double quotes for all JSON strings.
- Do not use trailing commas.
- Do not wrap the JSON in Markdown code fences.
- Do not write any introductory or concluding text outside JSON.

Return only the JSON object.
"""
)
