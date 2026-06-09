from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client.post("/seed")


# ===================== CREATE CART TESTS =====================

def test_create_cart():
    response = client.post("/carts/", json={"cust_id": 1})
    assert response.status_code == 201
    data = response.json()
    assert data["cust_id"] == 1
    assert data["status"] == "active"
    assert data["items"] == []


def test_create_cart_with_coupon():
    response = client.post("/carts/", json={
        "cust_id": 1,
        "coupon_code": "SAVE20",
        "discount_amount": 20
    })
    assert response.status_code == 201
    data = response.json()
    assert data["coupon_code"] == "SAVE20"
    assert data["discount_amount"] == 20


def test_create_cart_invalid_customer():
    response = client.post("/carts/", json={"cust_id": 999})
    assert response.status_code == 404


def test_create_cart_missing_cust_id():
    response = client.post("/carts/", json={})
    assert response.status_code == 422


def test_create_cart_string_cust_id():
    response = client.post("/carts/", json={"cust_id": "abc"})
    assert response.status_code == 422


def test_create_cart_negative_discount():
    response = client.post("/carts/", json={"cust_id": 1, "discount_amount": -10})
    assert response.status_code == 422


# ===================== GET CART TESTS =====================

def test_get_cart():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.get(f"/carts/{cart_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cart_id
    assert "items" in data


def test_get_cart_not_found():
    response = client.get("/carts/999")
    assert response.status_code == 404


def test_get_cart_string_id():
    response = client.get("/carts/abc")
    assert response.status_code == 422


# ===================== ADD ITEMS TESTS =====================

def test_add_items():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.post(f"/carts/{cart_id}/items", json={
        "items": [
            {"prod_id": 1, "quantity": 2},
            {"prod_id": 3}
        ]
    })
    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 2


def test_add_items_default_quantity():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1}]
    })
    assert response.status_code == 201
    assert response.json()["items"][0]["quantity"] == 1


def test_add_items_invalid_product():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 999, "quantity": 1}]
    })
    assert response.status_code == 404


def test_add_items_duplicate():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 1}]
    })

    response = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 2}]
    })
    assert response.status_code == 409


def test_add_items_zero_quantity():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 0}]
    })
    assert response.status_code == 422


def test_add_items_negative_quantity():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": -5}]
    })
    assert response.status_code == 422


def test_add_items_empty_array():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.post(f"/carts/{cart_id}/items", json={"items": []})
    assert response.status_code == 422


def test_add_items_cart_not_found():
    response = client.post("/carts/999/items", json={
        "items": [{"prod_id": 1, "quantity": 1}]
    })
    assert response.status_code == 404


def test_add_items_checked_out_cart():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 1}]
    })
    client.patch(f"/carts/{cart_id}/checkout")

    response = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 2, "quantity": 1}]
    })
    assert response.status_code == 400


# ===================== REMOVE ITEMS TESTS =====================

def test_remove_items():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    add = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 1}, {"prod_id": 2, "quantity": 1}]
    })
    item_id = add.json()["items"][0]["id"]

    response = client.request("DELETE", f"/carts/{cart_id}/items", json={
        "item_ids": [item_id]
    })
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


def test_remove_items_not_found():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.request("DELETE", f"/carts/{cart_id}/items", json={
        "item_ids": [999]
    })
    assert response.status_code == 404


def test_remove_items_empty_array():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.request("DELETE", f"/carts/{cart_id}/items", json={
        "item_ids": []
    })
    assert response.status_code == 422


def test_remove_items_checked_out_cart():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    add = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 1}]
    })
    client.patch(f"/carts/{cart_id}/checkout")

    response = client.request("DELETE", f"/carts/{cart_id}/items", json={
        "item_ids": [add.json()["items"][0]["id"]]
    })
    assert response.status_code == 400


# ===================== CHECKOUT TESTS =====================

def test_checkout():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 1}]
    })

    response = client.patch(f"/carts/{cart_id}/checkout")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "checked_out"
    assert "successfully" in data["message"]


def test_checkout_empty_cart():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.patch(f"/carts/{cart_id}/checkout")
    assert response.status_code == 400


def test_checkout_already_checked_out():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 1}]
    })
    client.patch(f"/carts/{cart_id}/checkout")

    response = client.patch(f"/carts/{cart_id}/checkout")
    assert response.status_code == 400


def test_checkout_cart_not_found():
    response = client.patch("/carts/999/checkout")
    assert response.status_code == 404


# ===================== DELETE CART TESTS =====================

def test_delete_cart():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    response = client.delete(f"/carts/{cart_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_cart_not_found():
    response = client.delete("/carts/999")
    assert response.status_code == 404


def test_delete_cart_then_get():
    create = client.post("/carts/", json={"cust_id": 1})
    cart_id = create.json()["id"]

    client.delete(f"/carts/{cart_id}")

    response = client.get(f"/carts/{cart_id}")
    assert response.status_code == 404


# ===================== FULL FLOW TEST =====================

def test_full_flow():
    create = client.post("/carts/", json={"cust_id": 1})
    assert create.status_code == 201
    cart_id = create.json()["id"]

    add = client.post(f"/carts/{cart_id}/items", json={
        "items": [{"prod_id": 1, "quantity": 2}, {"prod_id": 3, "quantity": 1}]
    })
    assert add.status_code == 201
    assert len(add.json()["items"]) == 2

    checkout = client.patch(f"/carts/{cart_id}/checkout")
    assert checkout.status_code == 200
    assert checkout.json()["status"] == "checked_out"

    delete = client.delete(f"/carts/{cart_id}")
    assert delete.status_code == 200

    get = client.get(f"/carts/{cart_id}")
    assert get.status_code == 404
