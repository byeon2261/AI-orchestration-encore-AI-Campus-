"""DummyJSON 상품 목록을 페이지 단위의 공개 응답으로 변환한다."""

from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ValidationError

app = FastAPI(title="Product Page API")

DUMMYJSON_PRODUCTS_URL = "https://dummyjson.com/products"


class ExternalProduct(BaseModel):
    """외부 상품에서 공개 응답에 사용할 필드만 검사한다."""

    id: int
    title: str
    price: float
    category: str


class ExternalProductPage(BaseModel):
    """DummyJSON의 상품 목록과 페이지 위치 정보를 검사한다."""

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
    """외부 상품 API를 호출할 비동기 클라이언트를 준비한다."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        yield client


ProductClient = Annotated[httpx.AsyncClient, Depends(get_product_client)]


async def fetch_product_page(
    client: httpx.AsyncClient,
    page: int,
    size: int,
) -> ProductPage:
    """우리 page·size를 외부 API의 skip·limit로 변환한다."""
    skip = (page - 1) * size
    response = await client.get(
        DUMMYJSON_PRODUCTS_URL,
        params={
            "limit": size,
            "skip": skip,
            "select": "id,title,price,category",
        },
    )
    response.raise_for_status()
    external = ExternalProductPage.model_validate(response.json())

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
        has_next=skip + len(items) < external.total,
        items=items,
    )


@app.get("/products", response_model=ProductPage)
async def list_products(
    client: ProductClient,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=20)] = 10,
) -> ProductPage:
    """검증한 페이지 조건으로 외부 상품 목록을 조회한다."""
    try:
        return await fetch_product_page(client, page, size)
    except httpx.TimeoutException as error:
        raise HTTPException(status_code=504, detail="상품 API 응답 시간이 초과됐다") from error
    except (httpx.HTTPError, ValidationError, ValueError) as error:
        raise HTTPException(status_code=502, detail="상품 API 응답을 처리할 수 없다") from error
