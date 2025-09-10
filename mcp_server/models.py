"""Pydantic models for MCP server tools"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


# Customer Models
class CustomerCreate(BaseModel):
    name: str = Field(description="Customer name")
    email: Optional[str] = Field(None, description="Customer email")
    phone: Optional[str] = Field(None, description="Customer phone number")
    address: Optional[str] = Field(None, description="Customer address")


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Customer name")
    email: Optional[str] = Field(None, description="Customer email")
    phone: Optional[str] = Field(None, description="Customer phone number")
    address: Optional[str] = Field(None, description="Customer address")


# Item Models
class ItemCreate(BaseModel):
    name: str = Field(description="Item name")
    model: Optional[str] = Field(None, description="Item model")
    brand: Optional[str] = Field(None, description="Item brand")
    item_group: int = Field(description="Item group ID")
    price: float = Field(0.0, description="Item price")


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Item name")
    model: Optional[str] = Field(None, description="Item model")
    brand: Optional[str] = Field(None, description="Item brand")
    item_group: Optional[int] = Field(None, description="Item group ID")
    price: Optional[float] = Field(None, description="Item price")


# Invoice Models
class InvoiceDetailCreate(BaseModel):
    item: int = Field(description="Item ID")
    quantity: int = Field(1, description="Quantity")
    unit_price: float = Field(description="Unit price")


class InvoiceCreate(BaseModel):
    customer: int = Field(description="Customer ID")
    invoice_date: date = Field(description="Invoice date (YYYY-MM-DD)")
    status: str = Field("pending", description="Invoice status")
    details: List[InvoiceDetailCreate] = Field(description="Invoice line items")


class InvoiceUpdate(BaseModel):
    customer: Optional[int] = Field(None, description="Customer ID")
    invoice_date: Optional[date] = Field(None, description="Invoice date (YYYY-MM-DD)")
    status: Optional[str] = Field(None, description="Invoice status")
    total_amount: Optional[float] = Field(None, description="Total amount")


# Contract Models
class ContactDetailCreate(BaseModel):
    contact_person: str = Field(description="Contact person name")
    role: Optional[str] = Field(None, description="Contact person role")
    phone: Optional[str] = Field(None, description="Contact phone")
    email: Optional[str] = Field(None, description="Contact email")


class ContractCreate(BaseModel):
    customer: int = Field(description="Customer ID")
    start_date: date = Field(description="Contract start date (YYYY-MM-DD)")
    end_date: date = Field(description="Contract end date (YYYY-MM-DD)")
    contract_type: str = Field(description="Contract type")
    status: str = Field("active", description="Contract status")
    terms: Optional[str] = Field(None, description="Contract terms")
    contact_details: Optional[List[ContactDetailCreate]] = Field(
        None, description="Contact details"
    )


class ContractUpdate(BaseModel):
    customer: Optional[int] = Field(None, description="Customer ID")
    start_date: Optional[date] = Field(
        None, description="Contract start date (YYYY-MM-DD)"
    )
    end_date: Optional[date] = Field(None, description="Contract end date (YYYY-MM-DD)")
    contract_type: Optional[str] = Field(None, description="Contract type")
    status: Optional[str] = Field(None, description="Contract status")
    terms: Optional[str] = Field(None, description="Contract terms")


# Serial Models
class SerialCreate(BaseModel):
    serial_number: str = Field(description="Serial number")
    item: int = Field(description="Item ID")
    status: str = Field("active", description="Serial status")
    manufactured_date: Optional[date] = Field(
        None, description="Manufactured date (YYYY-MM-DD)"
    )
    warranty_end_date: Optional[date] = Field(
        None, description="Warranty end date (YYYY-MM-DD)"
    )


class SerialUpdate(BaseModel):
    serial_number: Optional[str] = Field(None, description="Serial number")
    item: Optional[int] = Field(None, description="Item ID")
    status: Optional[str] = Field(None, description="Serial status")
    manufactured_date: Optional[date] = Field(
        None, description="Manufactured date (YYYY-MM-DD)"
    )
    warranty_end_date: Optional[date] = Field(
        None, description="Warranty end date (YYYY-MM-DD)"
    )


# Service Models
class ServiceDetailCreate(BaseModel):
    serial: Optional[int] = Field(None, description="Serial ID")
    description: str = Field(description="Service description")
    parts_used: Optional[str] = Field(None, description="Parts used")
    labor_hours: float = Field(0.0, description="Labor hours")
    cost: float = Field(0.0, description="Service cost")


class ServiceCreate(BaseModel):
    service_name: str = Field(description="Service name")
    customer: int = Field(description="Customer ID")
    service_date: date = Field(description="Service date (YYYY-MM-DD)")
    technician: Optional[str] = Field(None, description="Technician name")
    status: str = Field("scheduled", description="Service status")
    notes: Optional[str] = Field(None, description="Service notes")
    details: Optional[List[ServiceDetailCreate]] = Field(
        None, description="Service details"
    )


class ServiceUpdate(BaseModel):
    service_name: Optional[str] = Field(None, description="Service name")
    customer: Optional[int] = Field(None, description="Customer ID")
    service_date: Optional[date] = Field(None, description="Service date (YYYY-MM-DD)")
    technician: Optional[str] = Field(None, description="Technician name")
    status: Optional[str] = Field(None, description="Service status")
    notes: Optional[str] = Field(None, description="Service notes")
