from ppt_planner_prompt import ppt_planner_prompt
from excel_planner_prompt import excel_planner_prompt
from pdf_report_planner_prompt import pdf_report_planner_prompt

from LLM import llm
from intelligent_rag_question_generator import question_generator_prompt

from langchain_core.output_parsers import StrOutputParser
from question_parser import QuestionListParser
from RAG.rag_service import get_rag_response


def select_planner_prompt(document_type: str):
    """Select the appropriate content planner prompt."""

    document_type = document_type.strip().lower()

    if document_type in ["ppt", "powerpoint", "presentation"]:
        return ppt_planner_prompt

    elif document_type in ["excel", "spreadsheet", "workbook"]:
        return excel_planner_prompt

    elif document_type in ["pdf", "report", "pdf report"]:
        return pdf_report_planner_prompt

    else:
        raise ValueError(
            f"Unsupported document type: {document_type}. "
            "Please select PPT, Excel, or PDF."
        )


def run_document_chain(
    document_type: str,
    user_prompt: str,
    available_context: str = "No additional context provided.",
):
    """
    Generate a content plan, generate RAG questions, and retrieve
    evidence-backed answers for each question.

    Args:
        document_type: PPT, Excel, or PDF.
        user_prompt: User's natural-language document request.
        available_context: Additional context supplied by the user.

    Returns:
        A dictionary containing:
        - content_plan: Generated document plan.
        - rag_questions: Parsed retrieval questions.
        - rag_results: Answers and sources for each question.
    """

    # STEP 1: Select the appropriate planner prompt.
    selected_prompt = select_planner_prompt(document_type)

    # STEP 2: Build the Content Planner chain.
    content_planner_chain = (
        selected_prompt
        | llm
        | StrOutputParser()
    )

    # STEP 3: Generate the content plan.
    print("\n[INFO] Generating content plan...")

    content_plan = content_planner_chain.invoke({
        "user_prompt": user_prompt,
        "available_context": available_context,
    })

    if not content_plan or not content_plan.strip():
        raise RuntimeError(
            "The Content Planner returned an empty response."
        )

    print("[INFO] Content plan generated successfully.")
    print(f"[DEBUG] Content plan length: {len(content_plan)} characters")

    # STEP 4: Build the RAG Question Generator chain.
    question_parser = QuestionListParser()

    question_generator_chain = (
        question_generator_prompt
        | llm
        | question_parser
    )

    # STEP 5: Generate and parse retrieval questions.
    print("\n[INFO] Generating RAG questions...")

    question_generator_input = {
        "document_type": document_type,
        "user_prompt": user_prompt,
        "available_context": available_context,
        "content_plan": content_plan,
    }

    try:
        rag_questions = question_generator_chain.invoke(
            question_generator_input
        )

    except Exception as exc:
        raise RuntimeError(
            f"RAG Question Generator or parser failed: {exc}"
        ) from exc

    if not rag_questions:
        raise RuntimeError(
            "The RAG Question Generator returned no valid questions."
        )

    print("[INFO] RAG questions generated successfully.")
    print(f"[INFO] Parsed {len(rag_questions)} retrieval questions.")

    # STEP 6: Display parsed questions.
    print("\n[DEBUG] Parsed RAG questions:")

    for index, question in enumerate(rag_questions, start=1):
        print(f"{index}. {question}")

    # STEP 7: Send every question through the complete RAG pipeline.
    rag_results = []

    print("\n[INFO] Sending questions to RAG...")

    for index, question in enumerate(rag_questions, start=1):
        print(
            f"\n[INFO] Processing question "
            f"{index}/{len(rag_questions)}: {question}"
        )

        try:
            # Retrieves relevant chunks and generates an answer.
            rag_response = get_rag_response(question)

            rag_results.append({
                "question": question,
                "answer": rag_response.get("answer", ""),
                "sources": rag_response.get("sources", []),
            })

            print(f"[INFO] Successfully answered question {index}.")

        except Exception as exc:
            # Keep previous successful answers if one question fails.
            rag_results.append({
                "question": question,
                "answer": None,
                "sources": [],
                "error": str(exc),
            })

            print(
                f"[ERROR] RAG failed for question {index}: {exc}"
            )

    successful_count = sum(
        1 for item in rag_results
        if item.get("answer") is not None and "error" not in item
    )

    failed_count = len(rag_results) - successful_count

    print("\n[INFO] RAG processing completed.")
    print(f"[INFO] Successful answers: {successful_count}")
    print(f"[INFO] Failed questions: {failed_count}")

    # STEP 8: Return results for the document-generation stage.
    return {
        "content_plan": content_plan,
        "rag_questions": rag_questions,
        "rag_results": rag_results,
    }


if __name__ == "__main__":

    result = run_document_chain(
        document_type="PPT",
        user_prompt=(
            "Create a 10-slide presentation on "
            "quarterly business performance."
        ),
        available_context=(
            "The audience is the executive team. "
            "The company sells software subscriptions."
        ),
    )

    print("\n" + "=" * 60)
    print("CONTENT PLAN")
    print("=" * 60)
    print(result["content_plan"])

    print("\n" + "=" * 60)
    print("PARSED RAG QUESTIONS")
    print("=" * 60)

    for index, question in enumerate(
        result["rag_questions"],
        start=1,
    ):
        print(f"{index}. {question}")

    print("\n" + "=" * 60)
    print("RAG ANSWERS AND SOURCES")
    print("=" * 60)

    for index, item in enumerate(result["rag_results"], start=1):
        print(f"\nQuestion {index}: {item['question']}")

        if item.get("error"):
            print(f"Error: {item['error']}")
            continue

        print(f"Answer:\n{item['answer']}")
        print(f"Sources: {item['sources']}")

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Questions generated: {len(result['rag_questions'])}")
    print(f"Results collected: {len(result['rag_results'])}")
