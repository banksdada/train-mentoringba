"""SQLModel data models for the Quick‑Stack API.

- `User` – minimal auth holder (email, hashed password placeholder).
- `Customer` – a business client.
- `Job` – scheduling entry, linked to a `Customer`.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    # In a demo we store a plain‑text password; replace with a hash in prod.
    password: str

    # optional relationship to customers they own (not used now)
    customers: list["Customer"] = Relationship(back_populates="owner")

class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    owner_id: Optional[int] = Field(foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="customers")
    jobs: list["Job"] = Relationship(back_populates="customer")

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    scheduled_at: Optional[str] = None  # iso‑datetime string for demo
    status: str = Field(default="pending")

    customer_id: int = Field(foreign_key="customer.id")
    customer: Customer = Relationship(back_populates="jobs")


class StudentQuestion(SQLModel, table=True):
    """A question typed into the 'Ask the Lab' help box (kept for the trainer's records)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    student_name: str
    question: str
    answer: str
    answered: bool = True  # False when the assistant said it could not help
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
