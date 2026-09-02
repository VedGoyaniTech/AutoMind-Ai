def test_search_cars_empty(client):
    response = client.get("/api/v1/cars")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_car_detail_not_found(client):
    response = client.get("/api/v1/cars/999999")
    assert response.status_code == 404
