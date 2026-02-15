
from datetime import datetime
from typing import Optional


class TransactionCategory:
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = '',
        type: str = '',
        created_at: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.type = type
        self.created_at = created_at or datetime.utcnow().isoformat()

    @staticmethod
    def from_dict(data: dict) -> 'TransactionCategory':
        return TransactionCategory(
            id=data.get('id'),
            name=data.get('name', ''),
            type=data.get('type', ''),
            created_at=data.get('created_at'),
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'type': self.type,
        }
