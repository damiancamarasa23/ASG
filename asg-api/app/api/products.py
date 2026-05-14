import json
import pathlib

from fastapi import APIRouter, HTTPException

PRODUCTS_PATH = pathlib.Path(__file__).parent.parent.parent / "gucci" / "products.json"

router = APIRouter(tags=["products"])


@router.get("/products")
def list_products():
    return json.loads(PRODUCTS_PATH.read_text())


@router.get("/products/{product_id}")
def get_product(product_id: str):
    products = json.loads(PRODUCTS_PATH.read_text())
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[product_id]
