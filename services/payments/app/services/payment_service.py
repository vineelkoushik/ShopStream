from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Payment
from app.schemas import PaymentCreate
from app.services.gateway_sim import charge, PaymentDeclinedError, LimitExceededError

def process_payment(db: Session, payment_in: PaymentCreate) -> Payment:
  
    existing_payment = db.query(Payment).filter(
        Payment.order_id == payment_in.order_id,
        Payment.status == "COMPLETED" # <--- Only check for successful ones
    ).first()
    
    if existing_payment:
        return existing_payment
        
    
    try:
        charge(float(payment_in.amount))
        status = "COMPLETED"
    except LimitExceededError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PaymentDeclinedError as e:
        status = "FAILED"
        
    
    failed_payment = db.query(Payment).filter(
        Payment.order_id == payment_in.order_id,
        Payment.status == "FAILED"
    ).first()
    
    if failed_payment:
        
        failed_payment.status = status
        failed_payment.amount = payment_in.amount
        db.commit()
        db.refresh(failed_payment)
        new_payment = failed_payment
    else:
     
        new_payment = Payment(
            order_id=payment_in.order_id,
            amount=payment_in.amount,
            status=status
        )
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
    
    if status == "FAILED":
        raise HTTPException(status_code=402, detail="Payment failed")
        
    return new_payment