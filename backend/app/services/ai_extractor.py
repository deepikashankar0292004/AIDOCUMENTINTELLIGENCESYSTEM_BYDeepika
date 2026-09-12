import json
import urllib.request
import urllib.error
from typing import Dict, Any


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"


def create_structured_result(
    document_type: str,
    extracted_text: str
) -> Dict[str, Any]:

    if not extracted_text:
        return {
            "document_type": document_type,
            "data": {},
            "evidence": [],
            "raw_text": extracted_text,
            "error": "No text was extracted from the document."
        }

    prompt = f"""
You are a document intelligence system.

Analyze the OCR text below and extract structured information.

Identify the document as one of:

- invoice
- balance_sheet
- profit_and_loss
- cash_flow_statement
- other

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. Do not include markdown.
3. Do not include explanations.
4. For financial statements, identify the current year and previous year.
5. NEVER combine two year values into one value.
6. Keep current-year and previous-year values separate.
7. Preserve the financial item names from the document.
8. If a value cannot be determined, use null.
9. Do not invent values.

For a financial statement, use exactly this structure:

{{
    "document_type": "balance_sheet",
    "data": {{
        "statement_name": "...",
        "period": "...",
        "currency": "...",
        "financial_items": [
            {{
                "name": "Capital",
                "current_year": "1539.34",
                "previous_year": "765.22"
            }}
        ]
    }},
    "evidence": [
        "CONSOLIDATED BALANCE SHEET",
        "As at March 31, 2026"
    ]
}}

For an invoice, use this structure:

{{
    "document_type": "invoice",
    "data": {{
        "invoice_number": "...",
        "invoice_date": "...",
        "vendor": "...",
        "customer": "...",
        "subtotal": null,
        "tax_amount": null,
        "discount": null,
        "total_amount": null,
        "line_items": []
    }},
    "evidence": []
}}

Financial statement:

{document_type}

OCR TEXT:

{extracted_text}
"""

    request_data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:

        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(request_data).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=300
        ) as response:

            response_data = json.loads(
                response.read().decode("utf-8")
            )

        model_output = response_data.get(
            "response",
            ""
        ).strip()

        structured_data = json.loads(
            model_output
        )

        structured_data["raw_text"] = extracted_text

        if "document_type" not in structured_data:
            structured_data["document_type"] = document_type

        if "data" not in structured_data:
            structured_data["data"] = {}

        if "evidence" not in structured_data:
            structured_data["evidence"] = []

        return structured_data

    except json.JSONDecodeError:

        return {
            "document_type": document_type,
            "data": {},
            "evidence": [],
            "raw_text": extracted_text,
            "error": "Local LLM returned invalid JSON."
        }

    except urllib.error.URLError as e:

        return {
            "document_type": document_type,
            "data": {},
            "evidence": [],
            "raw_text": extracted_text,
            "error": (
                "Could not connect to Ollama. "
                "Make sure Ollama is running. "
                f"Details: {str(e)}"
            )
        }

    except Exception as e:

        return {
            "document_type": document_type,
            "data": {},
            "evidence": [],
            "raw_text": extracted_text,
            "error": str(e)
        }