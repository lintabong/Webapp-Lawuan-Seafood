
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class CashLedger:
    id: Optional[int] = None
    cash_account_id: int = 0
    transaction_id: Optional[int] = None
    direction: Optional[str] = None  # "in" or "out"
    amount: float = 0.0
    balance_after: float = 0.0
    created_at: Optional[datetime] = None

    @staticmethod
    def from_dict(data: dict) -> 'CashLedger':
        created_at = data.get('created_at')
        if created_at:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        return CashLedger(
            id=data.get('id'),
            cash_account_id=data.get('cash_account_id'),
            transaction_id=data.get('transaction_id'),
            direction=data.get('direction'),
            amount=float(data.get('amount', 0)),
            balance_after=float(data.get('balance_after', 0)),
            created_at=created_at,
        )

    def to_dict(self):
        return {
            'cash_account_id': self.cash_account_id,
            'transaction_id': self.transaction_id,
            'direction': self.direction,
            'amount': self.amount,
            'balance_after': self.balance_after,
        }
