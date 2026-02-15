
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID


@dataclass
class Order:
    id: Optional[int] = None
    customer_id: int = 0
    order_date: Optional[datetime] = None
    status: str = 'pending'
    created_by: Optional[UUID] = None
    total_amount: float = 0.0
    delivery_price: float = 0.0
    delivery_type: str = 'pickup'

    @staticmethod
    def from_dict(data: dict) -> 'Order':
        order_date = data.get('')
        if order_date:
            order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))

        return Order(
            id=data.get('id'),
            customer_id=data.get('customer_id'),
            order_date=order_date,
            status=data.get('status', 'pending'),
            created_by=data.get('created_by'),
            total_amount=float(data.get('total_amount', 0)),
            delivery_price=float(data.get('delivery_price', 0)),
            delivery_type=data.get('delivery_type', 'pickup'),
        )

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'status': self.status,
            'created_by': self.created_by,
            'total_amount': self.total_amount,
            'delivery_price': self.delivery_price,
            'delivery_type': self.delivery_type,
        }
