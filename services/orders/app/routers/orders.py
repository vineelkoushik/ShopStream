
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import OrderCreate, OrderOut
from app.services import order_service
from app.security import get_current_user
from app.rate_limiter import rate_limit_orders


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(rate_limit_orders)
):
    user_id = int(current_user["sub"])
    token = current_user["raw_token"]

    return order_service.create_order(db, user_id, order_in, token)


@router.get("/", response_model=list[OrderOut])
def get_my_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])
    is_admin = current_user.get("role") == "admin"

    result = order_service.list_orders(db, user_id, is_admin, skip, limit)

    return result["items"]


@router.get("/{order_id}", response_model=OrderOut)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])
    is_admin = current_user.get("role") == "admin"

    return order_service.get_order(db, user_id, order_id, is_admin)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])
    is_admin = current_user.get("role") == "admin"

    return order_service.cancel_order(db, user_id, order_id, is_admin)
