
import json
import re
from typing import Any

from langchain_core.output_parsers import BaseOutputParser


class QuestionListParser(BaseOutputParser[list[str]]):
    """Parse question-generator output into a clean list of questions."""

    def parse(self, text: str) -> list[str]:
        if not text or not text.strip():
            raise ValueError("Question generator returned empty output.")

        text = text.strip()

        # Remove Markdown code fences if the model includes them.
        text = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()

        # Preferred format: a JSON array of questions.
        try:
            data: Any = json.loads(text)

            if isinstance(data, dict):
                data = data.get("questions")

            if not isinstance(data, list):
                raise ValueError(
                    "Expected a JSON array or an object with a 'questions' array."
                )

            if not all(isinstance(item, str) for item in data):
                raise ValueError("Every question must be a string.")

            questions = data

        except json.JSONDecodeError:
            # Fallback: accept plain-text numbered or bulleted questions.
            questions = [
                re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", line).strip()
                for line in text.splitlines()
                if line.strip()
            ]

        # Normalize whitespace and remove empty or duplicate questions.
        cleaned_questions = []
        seen = set()

        for question in questions:
            question = re.sub(r"\s+", " ", question).strip()

            if not question:
                continue

            # Ignore headings if the model returns grouped questions.
            if question.endswith(":") and len(question) < 80:
                continue

            key = question.casefold()

            if key not in seen:
                seen.add(key)
                cleaned_questions.append(question)

        if not cleaned_questions:
            raise ValueError("No valid questions were parsed.")

        return cleaned_questions

    @property
    def _type(self) -> str:
        return "question_list_parser"
