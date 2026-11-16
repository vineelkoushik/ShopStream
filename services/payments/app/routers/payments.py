from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PaymentCreate, PaymentOut
from app.services import payment_service
from app.security import get_current_user
from app.models import Payment

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/charge", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def charge_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return payment_service.process_payment(db, payment_in)

@router.get("/{order_id}", response_model=PaymentOut)
def get_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not payment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment