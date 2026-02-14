
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    id: Optional[int] = None
    name: str = ''
    category_id: Optional[int] = None
    unit: str = 'kg'
    buy_price: float = 0.0
    sell_price: float = 0.0
    stock: float = 0.0
    is_active: bool = True
    created_at: Optional[datetime] = None

    @staticmethod
    def from_dict(data: dict) -> 'Product':
        from datetime import datetime

        created_at = data.get('created_at')
        if created_at:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        return Product(
            id=data.get('id'),
            name=data.get('name', ""),
            category_id=data.get('category_id'),
            unit=data.get('unit', 'kg'),
            buy_price=float(data.get('buy_price', 0)),
            sell_price=float(data.get('sell_price', 0)),
            stock=float(data.get('stock', 0)),
            is_active=data.get('is_active', True),
            created_at=created_at,
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'category_id': self.category_id,
            'unit': self.unit,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'stock': self.stock,
            'is_active': self.is_active,
        }
