from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ValidationError

app = FastAPI(title="Product Page API")

PRODUCTS_URL = "https://dummyjson.com/products"
PRODUCT_SELECT_FIELDS = "id,title,price,category"


class ExternalProduct(BaseModel):
    id: int
    title: str
    price: float
    category: str


class ExternalProductPage(BaseModel):
    products: list[ExternalProduct]
    total: int
    skip: int
    limit: int


class ProductPublic(BaseModel):
    id: int
    name: str
    price: float
    category: str


class ProductPage(BaseModel):
    page: int
    size: int
    total: int
    has_next: bool
    items: list[ProductPublic]


async def get_product_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        yield client


ProductClient = Annotated[httpx.AsyncClient, Depends(get_product_client)]


async def fetch_external_products(
    client: httpx.AsyncClient, skip: int, limit: int
) -> ExternalProductPage:
    response = await client.get(
        PRODUCTS_URL,
        params={
            "limit": limit,
            "skip": skip,
            "select": PRODUCT_SELECT_FIELDS,
        },
    )
    response.raise_for_status()
    return ExternalProductPage.model_validate(response.json())


async def build_product_page(
    external: ExternalProductPage, page: int, size: int
) -> ProductPage:
    items = [
        ProductPublic(
            id=product.id,
            name=product.title,
            price=product.price,
            category=product.category,
        )
        for product in external.products
    ]
    return ProductPage(
        page=page,
        size=size,
        total=external.total,
        has_next=external.skip + len(items) < external.total,
        items=items,
    )


async def fetch_product_page_or_http_error(
    client: httpx.AsyncClient, page: int, size: int
) -> ProductPage:
    skip = (page - 1) * size
    try:
        external = await fetch_external_products(client, skip, size)
        return await build_product_page(external, page, size)
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=504, detail="Product API request timed out"
        ) from error
    except (httpx.HTTPError, ValidationError, ValueError) as error:
        raise HTTPException(
            status_code=502, detail="Product API response could not be processed"
        ) from error


@app.get("/products", response_model=ProductPage)
async def list_products(
    client: ProductClient,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=20)] = 10,
) -> ProductPage:
    return await fetch_product_page_or_http_error(client, page, size)
