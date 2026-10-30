
from content_generation.content_generator import generate_document_content


# Sample information returned by the RAG system
retrieved_information = [
    {
        "question": "What was the quarterly revenue?",
        "answer": "Quarterly revenue was $2.4 million.",
        "sources": [
            {
                "source": "quarterly_report.pdf",
                "page": 12
            }
        ]
    },
    {
        "question": "What were the quarterly expenses?",
        "answer": "Quarterly expenses were $1.6 million.",
        "sources": [
            {
                "source": "quarterly_report.pdf",
                "page": 14
            }
        ]
    },
    {
        "question": "What was the previous quarter's revenue?",
        "answer": "Previous quarter revenue was $2.0 million.",
        "sources": [
            {
                "source": "quarterly_report.pdf",
                "page": 8
            }
        ]
    }
]


if __name__ == "__main__":

    document_type = "ppt"

    user_prompt = (
        "Create a 5-slide presentation explaining "
        "quarterly business performance for executives."
    )

    result = generate_document_content(
        document_type=document_type,
        user_prompt=user_prompt,
        retrieved_information=retrieved_information
    )

    print("\n" + "=" * 70)
    print("GENERATED DOCUMENT CONTENT")
    print("=" * 70)

    print(result)

    # Save generated content
    with open(
        "generated_content.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(result)

    print("\nOutput saved to generated_content.txt")
