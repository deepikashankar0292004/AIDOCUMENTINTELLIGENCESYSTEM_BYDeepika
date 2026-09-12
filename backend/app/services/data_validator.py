from typing import Dict, Any


def convert_to_float(value):
    """
    Convert a financial value into a float.
    """

    if value is None:
        return None

    try:
        if isinstance(value, (int, float)):
            return float(value)

        value = str(value)

        value = value.replace(",", "")
        value = value.replace("₹", "")
        value = value.replace("$", "")
        value = value.replace("€", "")
        value = value.replace("£", "")
        value = value.strip()

        return float(value)

    except (ValueError, TypeError):
        return None


def validate_structured_data(
    structured_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate structured information extracted by the local LLM.
    """

    validation_errors = []
    validation_warnings = []

    document_type = structured_result.get(
        "document_type"
    )

    data = structured_result.get(
        "data",
        {}
    )

    # -------------------------------------------------
    # 1. Check document type
    # -------------------------------------------------

    if not document_type:

        validation_errors.append(
            "Document type could not be identified."
        )

    # -------------------------------------------------
    # 2. Check whether data was extracted
    # -------------------------------------------------

    if not data:

        validation_errors.append(
            "No structured data was extracted."
        )

    # -------------------------------------------------
    # 3. Invoice validation
    # -------------------------------------------------

    if document_type == "invoice":

        invoice_number = data.get(
            "invoice_number"
        )

        invoice_date = data.get(
            "invoice_date"
        )

        vendor = data.get(
            "vendor"
        )

        total_amount = data.get(
            "total_amount"
        )

        line_items = data.get(
            "line_items",
            []
        )

        # Check important invoice fields

        if not invoice_number:

            validation_warnings.append(
                "Invoice number was not extracted."
            )

        if not invoice_date:

            validation_warnings.append(
                "Invoice date was not extracted."
            )

        if not vendor:

            validation_warnings.append(
                "Vendor name was not extracted."
            )

        if total_amount is None:

            validation_warnings.append(
                "Invoice total amount was not extracted."
            )

        # Check line items

        if not line_items:

            validation_warnings.append(
                "No invoice line items were extracted."
            )

    # -------------------------------------------------
    # 4. Balance Sheet validation
    # -------------------------------------------------

    if document_type == "balance_sheet":

        financial_items = data.get(
            "financial_items",
            []
        )

        if not financial_items:

            validation_errors.append(
                "No financial items were extracted."
            )

        asset_total = None
        liability_total = None

        # Find asset and liability totals

        for item in financial_items:

            name = str(
                item.get("name", "")
            ).lower().strip()

            if (
                "total assets" in name
                or "assets total" in name
            ):

                asset_total = item

            if (
                "total liabilities" in name
                or "liabilities total" in name
            ):

                liability_total = item

        # ---------------------------------------------
        # Fallback for generic "Total"
        # ---------------------------------------------

        if asset_total is None or liability_total is None:

            total_items = [
                item
                for item in financial_items
                if "total" in str(
                    item.get("name", "")
                ).lower()
            ]

            if len(total_items) >= 2:

                if asset_total is None:

                    asset_total = total_items[0]

                if liability_total is None:

                    liability_total = total_items[1]

        # ---------------------------------------------
        # Validate totals
        # ---------------------------------------------

        if asset_total is None or liability_total is None:

            validation_warnings.append(
                "Could not find both asset and liability totals."
            )

        else:

            # Current year

            current_asset = convert_to_float(
                asset_total.get("current_year")
            )

            current_liability = convert_to_float(
                liability_total.get("current_year")
            )

            if (
                current_asset is not None
                and current_liability is not None
            ):

                if current_asset != current_liability:

                    validation_errors.append(
                        "Current-year balance sheet totals do not match."
                    )

            # Previous year

            previous_asset = convert_to_float(
                asset_total.get("previous_year")
            )

            previous_liability = convert_to_float(
                liability_total.get("previous_year")
            )

            if (
                previous_asset is not None
                and previous_liability is not None
            ):

                if previous_asset != previous_liability:

                    validation_errors.append(
                        "Previous-year balance sheet totals do not match."
                    )

    # -------------------------------------------------
    # 5. Profit & Loss validation
    # -------------------------------------------------

    if document_type == "profit_and_loss":

        financial_items = data.get(
            "financial_items",
            []
        )

        if not financial_items:

            validation_errors.append(
                "No financial items were extracted from the Profit and Loss statement."
            )

        else:

            validation_warnings.append(
                "Profit and Loss financial items were extracted successfully."
            )

    # -------------------------------------------------
    # 6. Cash Flow Statement validation
    # -------------------------------------------------

    if document_type == "cash_flow_statement":

        financial_items = data.get(
            "financial_items",
            []
        )

        if not financial_items:

            validation_errors.append(
                "No financial items were extracted from the Cash Flow Statement."
            )

        else:

            validation_warnings.append(
                "Cash Flow financial items were extracted successfully."
            )

    # -------------------------------------------------
    # 7. Evidence validation
    # -------------------------------------------------

    evidence = structured_result.get(
        "evidence",
        []
    )

    if not evidence:

        validation_warnings.append(
            "No evidence was returned by the LLM."
        )

    # -------------------------------------------------
    # 8. Final validation status
    # -------------------------------------------------

    if validation_errors:

        status = "failed"

    elif validation_warnings:

        status = "warning"

    else:

        status = "passed"

    # -------------------------------------------------
    # 9. Return validation result
    # -------------------------------------------------

    return {
        "status": status,
        "errors": validation_errors,
        "warnings": validation_warnings
    }