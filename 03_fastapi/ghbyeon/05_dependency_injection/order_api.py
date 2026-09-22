"""바이브 코딩으로 생성된 파일"""

from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from fastapi import status as http_status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Cafe Order API")


class OrderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    menu_name: str = Field(min_length=2, max_length=30)
    quantity: int = Field(ge=1, le=10)
    takeout: bool = False


class OrderPublic(BaseModel):
    id: int
    menu_name: str
    quantity: int
    takeout: bool
    status: Literal["received"]


class OrderSummary(BaseModel):
    id: int
    menu_name: str
    status: Literal["received"]


class OrderList(BaseModel):
    items: list[OrderSummary]
    total: int


class OrderFilters(BaseModel):
    status: str | None
    takeout: bool | None
    offset: int
    limit: int


orders: dict[int, dict[str, object]] = {}


def get_order_filters(
    status: Annotated[str | None, Query(min_length=1, max_length=20)] = None,
    takeout: bool | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> OrderFilters:
    return OrderFilters(
        status=status.casefold() if status is not None else None,
        takeout=takeout,
        offset=offset,
        limit=limit,
    )


def select_orders(
    filters: OrderFilters, menu_name: str | None = None
) -> dict[str, object]:
    matched = [
        order
        for order in orders.values()
        if (menu_name is None or order["menu_name"] == menu_name)
        and (filters.status is None or order["status"] == filters.status)
        and (filters.takeout is None or order["takeout"] == filters.takeout)
    ]
    return {
        "items": matched[filters.offset : filters.offset + filters.limit],
        "total": len(matched),
    }


@app.post(
    "/orders", response_model=OrderPublic, status_code=http_status.HTTP_201_CREATED
)
def create_order(order_input: OrderCreate) -> dict[str, object]:
    order_id = max(orders, default=0) + 1
    record: dict[str, object] = {
        "id": order_id,
        **order_input.model_dump(),
        "status": "received",
        "staff_note": "",
    }
    orders[order_id] = record
    return record


@app.get("/orders", response_model=OrderList)
def list_orders(
    filters: Annotated[OrderFilters, Depends(get_order_filters)],
) -> dict[str, object]:
    return select_orders(filters)


@app.get("/menus/{menu_name}/orders", response_model=OrderList)
def list_menu_orders(
    menu_name: Annotated[str, Path(min_length=2, max_length=30)],
    filters: Annotated[OrderFilters, Depends(get_order_filters)],
) -> dict[str, object]:
    return select_orders(filters, menu_name)


@app.get("/orders/{order_id}", response_model=OrderPublic)
def read_order(
    order_id: Annotated[int, Path(ge=1)],
) -> dict[str, object]:
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
