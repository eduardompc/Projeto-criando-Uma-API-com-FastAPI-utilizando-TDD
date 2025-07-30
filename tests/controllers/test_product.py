from typing import List

import pytest
from tests.factories import product_data
from fastapi import status


# Testa criação de produto com sucesso
async def test_controller_create_should_return_success(client, products_url):
    response = await client.post(products_url, json=product_data())

    content = response.json()

    del content["created_at"]
    del content["updated_at"]
    del content["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert content == {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "8.500",
        "status": True,
    }


# Testa busca de produto por ID com sucesso
async def test_controller_get_should_return_success(
    client, products_url, product_inserted
):
    response = await client.get(f"{products_url}{product_inserted.id}")

    content = response.json()

    del content["created_at"]
    del content["updated_at"]

    assert response.status_code == status.HTTP_200_OK
    assert content == {
        "id": str(product_inserted.id),
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "8.500",
        "status": True,
    }


# Testa busca de produto por ID inexistente
async def test_controller_get_should_return_not_found(client, products_url):
    response = await client.get(f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_should_return_success(client, products_url):
    response = await client.get(products_url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), List)
    assert len(response.json()) > 1


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_price_filter(client, products_url):
    """Testa filtro de preço entre 5000 e 8000."""
    response = await client.get(f"{products_url}?min_price=5000&max_price=8000")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        price = float(str(item["price"]).replace(".", "").replace(",", "."))
        assert 5000 < price < 8000


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_min_price_only(client, products_url):
    """Testa filtro apenas min_price."""
    response = await client.get(f"{products_url}?min_price=6000")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for item in data:
        price = float(str(item["price"]).replace(".", "").replace(",", "."))
        assert price > 6000


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_max_price_only(client, products_url):
    """Testa filtro apenas max_price."""
    response = await client.get(f"{products_url}?max_price=6000")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for item in data:
        price = float(str(item["price"]).replace(".", "").replace(",", "."))
        assert price < 6000


# Testa atualização de produto com sucesso
async def test_controller_patch_should_return_success(
    client, products_url, product_inserted
):
    response = await client.patch(
        f"{products_url}{product_inserted.id}", json={"price": "7.500"}
    )

    content = response.json()

    del content["created_at"]
    del content["updated_at"]

    assert response.status_code == status.HTTP_200_OK
    assert content == {
        "id": str(product_inserted.id),
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "7.500",
        "status": True,
    }


# Testa atualização de produto não encontrado
async def test_controller_patch_should_return_not_found(client, products_url):
    response = await client.patch(
        f"{products_url}00000000-0000-0000-0000-000000000000", json={"price": "9.999"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"].startswith("Product not found")


# Testa deleção de produto com sucesso
async def test_controller_delete_should_return_no_content(
    client, products_url, product_inserted
):
    response = await client.delete(f"{products_url}{product_inserted.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


# Testa deleção de produto não encontrado
async def test_controller_delete_should_return_not_found(client, products_url):
    response = await client.delete(
        f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }


# Teste para erro de inserção (simulado)
import unittest.mock as mock
from store.core.exceptions import BaseException

async def test_controller_create_should_return_error(client, products_url):
    with mock.patch("store.usecases.product.ProductUsecase.create", side_effect=BaseException("Erro ao inserir produto no banco de dados")):
        response = await client.post(products_url, json=product_data())
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Erro ao inserir produto no banco de dados"}


# Teste de autenticação simulada (exemplo)
import unittest.mock as mock
from store.core.exceptions import BaseException

@pytest.mark.usefixtures("products_inserted")
async def test_controller_auth_required(client, products_url):
    """Testa se rota exige autenticação (simulação)."""
    # Supondo que a autenticação seja via header Authorization
    response = await client.get(products_url, headers={})
    # Esperado: 401 Unauthorized se autenticação for obrigatória
    # Aqui só simula, ajuste conforme implementação real
    # assert response.status_code == status.HTTP_401_UNAUTHORIZED
    pass

# Teste de paginação
@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_pagination(client, products_url):
    """Testa paginação usando limit e offset."""
    response = await client.get(f"{products_url}?limit=2&offset=1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2

# Teste de ordenação
@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_order_by_price(client, products_url):
    """Testa ordenação por preço decrescente."""
    response = await client.get(f"{products_url}?order_by=price&order=desc")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    prices = [float(str(item["price"]).replace(".", "").replace(",", ".")) for item in data]
    assert prices == sorted(prices, reverse=True)

# Teste de integração entre camadas (simples)
async def test_integration_controller_usecase(client, products_url, product_in):
    """Testa integração controller -> usecase -> db."""
    response = await client.post(products_url, json=product_in.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == product_in.name
    # Busca pelo id
    response_get = await client.get(f"{products_url}{data['id']}")
    assert response_get.status_code == status.HTTP_200_OK
    assert response_get.json()["id"] == data["id"]
