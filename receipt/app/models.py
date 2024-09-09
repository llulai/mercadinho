from typing import List
from typing import Literal
from pydantic import BaseModel


class Product(BaseModel):
    idx: int
    sku: str
    description: str
    quantity: float
    quantity_measure: Literal['UN', 'KG']
    unit_price: float
    total_price: float


class Store(BaseModel):
    name: str
    cnpj: str
    address: str


class Receipt(BaseModel):
    store: Store
    products: List[Product]
    receipt_datetime: str
