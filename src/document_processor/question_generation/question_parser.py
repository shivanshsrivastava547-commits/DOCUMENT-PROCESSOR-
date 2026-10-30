
import json
import re
from typing import Any
from typing import Any, ClassVar

from langchain_core.output_parsers import BaseOutputParser


class QuestionListParser(BaseOutputParser[list[str]]):
    """Parse and normalize question-generator output."""

    MAX_QUESTIONS: ClassVar[int] = 12

    def parse(self, text: str) -> list[str]:
        if not text or not text.strip():
            raise ValueError("Question generator returned empty output.")

        text = text.strip()

        # Remove Markdown code fences.
        text = re.sub(
            r"```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\s*```", "", text).strip()

        questions: list[str] = []

        # First attempt: parse a JSON array.
        try:
            data: Any = json.loads(text)

            if isinstance(data, dict):
                data = data.get("questions", [])

            if isinstance(data, list):
                questions = [
                    item for item in data
                    if isinstance(item, str)
                ]

        except json.JSONDecodeError:
            # Attempt to extract a JSON array if extra text exists.
            try:
                start = text.index("[")
                decoder = json.JSONDecoder()
                data, _ = decoder.raw_decode(text[start:])

                if isinstance(data, list):
                    questions = [
                        item for item in data
                        if isinstance(item, str)
                    ]

            except (ValueError, json.JSONDecodeError):
                questions = []

        # Fallback: parse numbered or bulleted plain text.
        if not questions:
            for line in text.splitlines():
                line = line.strip()

                if not line:
                    continue

                # Remove numbering and bullet markers.
                line = re.sub(
                    r"^\s*(?:\d+[\.\)]\s*|[-*•]\s*)",
                    "",
                    line,
                )

                # Remove surrounding quotation marks.
                line = line.strip().strip('"').strip("'").strip()

                # Remove trailing commas and semicolons.
                line = line.rstrip(",;").strip()

                # Ignore JSON fragments and headings.
                if line in {"[", "]", "{", "}", "```"}:
                    continue

                if line.lower().startswith("rag retrieval questions"):
                    continue

                if line.endswith(":") and len(line) < 100:
                    continue

                if line:
                    questions.append(line)

        # Normalize, validate, and remove duplicates.
        cleaned_questions = []
        seen = set()

        for question in questions:
            question = re.sub(r"\s+", " ", question).strip()

            question = question.strip('"').strip("'").strip()
            question = question.rstrip(",;").strip()

            # Reject fragments and malformed entries.
            if not question:
                continue

            if question in {"[", "]", "{", "}"}:
                continue

            if len(question) < 10:
                continue

            # Keep actual questions only.
            if not question.endswith("?"):
                continue

            key = question.casefold()

            if key not in seen:
                seen.add(key)
                cleaned_questions.append(question)

        if not cleaned_questions:
            raise ValueError(
                "No valid retrieval questions could be parsed."
            )

        # Final safety limit.
        return cleaned_questions[:self.MAX_QUESTIONS]

    @property
    def _type(self) -> str:
        return "question_list_parser"
