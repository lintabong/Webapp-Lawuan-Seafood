
from datetime import datetime
from typing import Optional


class Transaction:
    def __init__(
        self,
        id: Optional[int] = None,
        type: str = '',
        category_id: Optional[int] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        amount: float = 0.0,
        description: Optional[str] = None,
        created_by: Optional[str] = None,  # UUID
        transaction_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.type = type
        self.category_id = category_id
        self.reference_type = reference_type
        self.reference_id = reference_id
        self.amount = float(amount)
        self.description = description
        self.created_by = created_by
        self.transaction_date = transaction_date or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

    @staticmethod
    def from_dict(data: dict) -> 'Transaction':
        return Transaction(
            id=data.get('id'),
            type=data.get('type', ''),
            category_id=data.get('category_id'),
            reference_type=data.get('reference_type'),
            reference_id=data.get('reference_id'),
            amount=float(data.get('amount', 0)),
            description=data.get('description'),
            created_by=data.get('created_by'),
            transaction_date=_parse_datetime(data.get('transaction_date')),
            created_at=_parse_datetime(data.get('created_at')),
            updated_at=_parse_datetime(data.get('updated_at')),
        )

    def to_dict(self) -> dict:
        return {
            'type': self.type,
            'category_id': self.category_id,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'amount': self.amount,
            'description': self.description,
            'created_by': self.created_by,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
        }

    def validate(self):
        if not self.type:
            raise ValueError("Transaction type is required")

        if self.amount <= 0:
            raise ValueError("Amount must be greater than 0")

def _parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)
