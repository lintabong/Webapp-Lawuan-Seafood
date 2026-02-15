
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
        created_at: Optional[str] = None,
    ):
        self.id = id
        self.type = type
        self.category_id = category_id
        self.reference_type = reference_type
        self.reference_id = reference_id
        self.amount = amount
        self.description = description
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow().isoformat()

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
            created_at=data.get('created_at'),
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
        }
