
from app.repositories.product_repo import (
    list_product
)

def list_active_product():
    products = list_product()

    return products
