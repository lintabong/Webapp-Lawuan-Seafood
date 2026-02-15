
from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderItem:
    id: Optional[int] = None
    order_id: int = 0
    product_id: int = 0
    quantity: float = 0.0
    buy_price: float = 0.0
    sell_price: float = 0.0
    is_prepared: bool = False

    @staticmethod
    def from_dict(data: dict) -> 'OrderItem':
        return OrderItem(
            id=data.get('id'),
            order_id=data.get('order_id'),
            product_id=data.get('product_id'),
            quantity=float(data.get('quantity', 0)),
            buy_price=float(data.get('buy_price', 0)),
            sell_price=float(data.get('sell_price', 0)),
            is_prepared=data.get('is_prepared', False),
        )

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'is_prepared': self.is_prepared,
        }
