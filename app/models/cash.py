
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Cash:
    id: Optional[int] = None
    name: str = ""
    balance: float = 0.0
    is_active: bool = True
    created_at: Optional[datetime] = None

    @staticmethod
    def from_dict(data: dict) -> 'Cash':
        created_at = data.get('created_at')
        if created_at:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        return Cash(
            id=data.get('id'),
            name=data.get('name', ''),
            balance=float(data.get('balance', 0)),
            is_active=data.get('is_active', True),
            created_at=created_at,
        )

    def to_dict(self):
        return {
            'name': self.name,
            'balance': self.balance,
            'is_active': self.is_active,
        }
