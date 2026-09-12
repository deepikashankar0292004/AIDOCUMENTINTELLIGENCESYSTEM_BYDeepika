from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class InvoiceItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None


class InvoiceExtraction(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    vendor: Optional[str] = None
    customer: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    discount: Optional[float] = None
    total_amount: Optional[float] = None
    line_items: List[InvoiceItem] = []


class FinancialItem(BaseModel):
    name: str
    current_year: Optional[str] = None
    previous_year: Optional[str] = None


class FinancialStatementExtraction(BaseModel):
    statement_name: Optional[str] = None
    period: Optional[str] = None
    currency: Optional[str] = None
    financial_items: List[FinancialItem] = []


class ExtractionResult(BaseModel):
    document_type: str
    data: Dict[str, Any]
    evidence: List[Dict[str, Any]] = []