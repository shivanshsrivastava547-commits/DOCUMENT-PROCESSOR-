
from pathlib import Path
from RAG.rag_service import ingest_file

file_path = Path(
    r"E:\temperary storage\Downloads\fictional_quarterly_business_performance_report.pdf"
)

if not file_path.is_file():
    raise FileNotFoundError(f"PDF not found: {file_path}")

result = ingest_file(str(file_path))
print(result)
