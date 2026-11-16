from unittest.mock import patch
from app.main import app
from app.security import get_current_user

MOCK_PRODUCT = {
    "id": 1,
    "name": "Mock Headphones",
    "price": "199.99",
    "stock": 10,
    "reserved": 0,
}

def mock_get_current_user():
    return {"sub": "1", "email": "test@example.com", "role": "customer", "raw_token": "fake_token"}

@patch("app.services.order_service.get_product")
def test_create_order_success(mock_get_product, client):
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    mock_get_product.return_value = MOCK_PRODUCT
    
    response = client.post(
        "/orders/",
        json={"items": [{"product_id": 1, "quantity": 2}]}
    )
    
    
    assert response.status_code == 201
    assert response.json()["total"] == "399.98"
    assert response.json()["status"] == "PENDING"
    
    
    app.dependency_overrides.clear()