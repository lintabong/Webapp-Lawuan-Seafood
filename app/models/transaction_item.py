
from datetime import datetime
from typing import Optional


class TransactionItem:
    def __init__(
        self,
        id: Optional[int] = None,
        transaction_id: Optional[int] = None,
        item_type: str = 'product',
        product_id: Optional[int] = None,
        description: Optional[str] = None,
        quantity: float = 1.0,
        price: float = 0.0,
        subtotal: float = 0.0,
        created_at: Optional[str] = None,
    ):
        self.id = id
        self.transaction_id = transaction_id
        self.item_type = item_type
        self.product_id = product_id
        self.description = description
        self.quantity = quantity
        self.price = price
        self.subtotal = subtotal
        self.created_at = created_at or datetime.utcnow().isoformat()

    @staticmethod
    def from_dict(data: dict) -> 'TransactionItem':
        return TransactionItem(
            id=data.get('id'),
            transaction_id=data.get('transaction_id'),
            item_type=data.get('item_type', 'product'),
            product_id=data.get('product_id'),
            description=data.get('description'),
            quantity=float(data.get('quantity', 1)),
            price=float(data.get('price', 0)),
            subtotal=float(data.get('subtotal', 0)),
            created_at=data.get('created_at'),
        )

    def to_dict(self) -> dict:
        return {
            'transaction_id': self.transaction_id,
            'item_type': self.item_type,
            'product_id': self.product_id,
            'description': self.description,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.subtotal,
        }
