
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ''
    phone: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None

    @staticmethod
    def from_dict(data: dict) -> 'Customer':
        return Customer(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone'),
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            created_at=data.get('created_at'),
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }
