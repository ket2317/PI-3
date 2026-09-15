import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def login(email, password):
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.cookies


# ---------------------------------------------------------------------------
# Sin sesión
# ---------------------------------------------------------------------------


def test_anonimo_no_puede_ver_nada():
    assert client.get("/productos/").status_code == 401
    assert client.get("/ventas/").status_code == 401
    assert client.get("/reportes/resumen").status_code == 401


# ---------------------------------------------------------------------------
# Cajero
# ---------------------------------------------------------------------------


def test_cajero_no_ve_otra_sucursal():
    cookies = login("cajero.prueba@test.com", "Test12345")
    assert client.get("/productos/?sucursal_id=1", cookies=cookies).status_code == 403


def test_cajero_no_administra_usuarios():
    cookies = login("cajero.prueba@test.com", "Test12345")
    assert client.get("/usuarios/", cookies=cookies).status_code == 403


def test_cajero_no_ve_reportes():
    cookies = login("cajero.prueba@test.com", "Test12345")
    assert client.get("/reportes/ventas", cookies=cookies).status_code == 403


def test_cajero_ve_productos_de_su_sucursal():
    cookies = login("cajero.prueba@test.com", "Test12345")
    response = client.get("/productos/", cookies=cookies)
    assert response.status_code == 200


def test_cajero_ve_su_sucursal():
    cookies = login("cajero.prueba@test.com", "Test12345")
    response = client.get("/sucursales/", cookies=cookies)
    assert response.status_code == 200


def test_cajero_no_ve_inventario():
    cookies = login("cajero.prueba@test.com", "Test12345")
    response = client.get("/inventario/", cookies=cookies)
    assert response.status_code == 403


def test_cajero_realiza_venta_en_su_sucursal():
    """Protocolo: 'los cajeros podrán realizar ventas...' — venta real, con
    descuento automático de inventario, restaurado al final para no afectar
    otras pruebas ni la demo."""
    admin_cookies = login("pi3@admin.com", "pi12345")
    cajero_cookies = login("cajero.prueba@test.com", "Test12345")

    antes = client.get("/inventario/?sucursal_id=2", cookies=admin_cookies).json()
    existencia_antes = next(i["existencia"] for i in antes if i["producto_id"] == 3)

    payload = {
        "sucursal_id": 2,
        "metodo_pago_id": 1,
        "items": [{"producto_id": 3, "cantidad": 1}],
    }
    response = client.post("/ventas/", json=payload, cookies=cajero_cookies)
    assert response.status_code == 201
    venta = response.json()
    assert venta["sucursal_id"] == 2

    despues = client.get("/inventario/?sucursal_id=2", cookies=admin_cookies).json()
    existencia_despues = next(i["existencia"] for i in despues if i["producto_id"] == 3)
    assert existencia_despues == existencia_antes - 1

    # restaurar la existencia para no afectar otras pruebas ni la demo
    client.put(
        "/inventario/3",
        json={"existencia": existencia_antes, "stock_minimo": 5, "sucursal_id": 2},
        cookies=admin_cookies,
    )


def test_cajero_no_vende_en_otra_sucursal():
    cookies = login("cajero.prueba@test.com", "Test12345")
    payload = {
        "sucursal_id": 1,
        "metodo_pago_id": 1,
        "items": [{"producto_id": 3, "cantidad": 1}],
    }
    assert client.post("/ventas/", json=payload, cookies=cookies).status_code == 403


# ---------------------------------------------------------------------------
# Gerente
# ---------------------------------------------------------------------------


def test_gerente_no_ve_resumen_del_sistema():
    cookies = login("gerente.prueba@test.com", "Test12345")
    assert client.get("/reportes/resumen", cookies=cookies).status_code == 403


def test_gerente_no_crea_sucursales():
    cookies = login("gerente.prueba@test.com", "Test12345")
    payload = {"nombre": "x", "direccion": "x", "telefono": "1", "contacto": None, "gerente_id": None}
    assert client.post("/sucursales/", json=payload, cookies=cookies).status_code == 403


def test_gerente_consulta_informacion_de_su_sucursal():
    """Protocolo: 'Consultar la información de su sucursal.'"""
    cookies = login("gerente.prueba@test.com", "Test12345")
    response = client.get("/sucursales/2", cookies=cookies)
    assert response.status_code == 200
    assert response.json()["id"] == 2


def test_gerente_no_consulta_otra_sucursal():
    cookies = login("gerente.prueba@test.com", "Test12345")
    assert client.get("/sucursales/1", cookies=cookies).status_code == 403


def test_gerente_registra_consulta_y_modifica_producto():
    """Protocolo: 'Registrar productos. Consultar productos. Modificar
    productos.' — se crea, se modifica y se desactiva al final (limpieza)."""
    cookies = login("gerente.prueba@test.com", "Test12345")

    payload = {
        "sucursal_id": 2,
        "codigo": f"PYTEST-{uuid.uuid4().hex[:6]}",
        "nombre": "Producto Pytest",
        "precio": "10.00",
        "iva": "0.16",
        "categoria_id": None,
    }
    response = client.post("/productos/", json=payload, cookies=cookies)
    assert response.status_code == 201
    producto = response.json()

    response = client.get("/productos/", cookies=cookies)
    assert any(p["id"] == producto["id"] for p in response.json())

    payload["nombre"] = "Producto Pytest Editado"
    response = client.put(f"/productos/{producto['id']}", json=payload, cookies=cookies)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Producto Pytest Editado"

    # limpieza
    client.delete(f"/productos/{producto['id']}", cookies=cookies)


def test_gerente_registra_y_elimina_cajero_de_su_sucursal():
    """Protocolo: 'Registrar nuevas cajas. Eliminar cajas.'"""
    cookies = login("gerente.prueba@test.com", "Test12345")

    payload = {
        "nombre": "Cajero Pytest",
        "correo": f"cajero.pytest.{uuid.uuid4().hex[:8]}@test.com",
        "password": "Test12345",
        "rol_id": 3,
        "sucursal_id": 2,
    }
    response = client.post("/usuarios/", json=payload, cookies=cookies)
    assert response.status_code == 200
    cajero = response.json()

    response = client.delete(f"/usuarios/{cajero['id']}", cookies=cookies)
    assert response.status_code == 200


def test_gerente_no_registra_cajero_en_otra_sucursal():
    cookies = login("gerente.prueba@test.com", "Test12345")
    payload = {
        "nombre": "Cajero Otra Sede",
        "correo": f"cajero.otra.{uuid.uuid4().hex[:8]}@test.com",
        "password": "Test12345",
        "rol_id": 3,
        "sucursal_id": 1,
    }
    assert client.post("/usuarios/", json=payload, cookies=cookies).status_code == 403


def test_gerente_no_registra_otro_gerente_ni_admin():
    cookies = login("gerente.prueba@test.com", "Test12345")
    payload = {
        "nombre": "Otro Gerente",
        "correo": f"otro.gerente.{uuid.uuid4().hex[:8]}@test.com",
        "password": "Test12345",
        "rol_id": 2,
        "sucursal_id": 2,
    }
    assert client.post("/usuarios/", json=payload, cookies=cookies).status_code == 403


def test_gerente_ve_inventario_de_su_sucursal():
    cookies = login("gerente.prueba@test.com", "Test12345")
    response = client.get("/inventario/", cookies=cookies)
    assert response.status_code == 200


def test_gerente_actualiza_existencias():
    """Protocolo: 'Controlar el inventario. Actualizar existencias.' — se
    sube en 1 y se restaura al final."""
    cookies = login("gerente.prueba@test.com", "Test12345")

    antes = client.get("/inventario/?sucursal_id=2", cookies=cookies).json()
    item = next(i for i in antes if i["producto_id"] == 3)

    response = client.put(
        "/inventario/3",
        json={"existencia": item["existencia"] + 1, "stock_minimo": item["stock_minimo"], "sucursal_id": 2},
        cookies=cookies,
    )
    assert response.status_code == 200
    assert response.json()["existencia"] == item["existencia"] + 1

    # restaurar
    client.put(
        "/inventario/3",
        json={"existencia": item["existencia"], "stock_minimo": item["stock_minimo"], "sucursal_id": 2},
        cookies=cookies,
    )


def test_gerente_consulta_bajo_inventario():
    """Protocolo: 'Consultar productos con bajo inventario.'"""
    cookies = login("gerente.prueba@test.com", "Test12345")
    response = client.get("/inventario/bajo-stock", cookies=cookies)
    assert response.status_code == 200


def test_gerente_consulta_historial_de_ventas_de_su_sucursal():
    """Protocolo: 'Consultar el historial de ventas. Supervisar las ventas
    realizadas en su sucursal.'"""
    cookies = login("gerente.prueba@test.com", "Test12345")
    response = client.get("/reportes/ventas", cookies=cookies)
    assert response.status_code == 200
    for venta in response.json():
        assert venta["sucursal_id"] == 2


def test_gerente_ve_usuarios_de_su_sucursal():
    cookies = login("gerente.prueba@test.com", "Test12345")
    response = client.get("/usuarios/", cookies=cookies)
    assert response.status_code == 200
    for usuario in response.json():
        assert usuario["sucursal_id"] == 2


# ---------------------------------------------------------------------------
# Administrador General
# ---------------------------------------------------------------------------


def test_admin_ve_todo():
    cookies = login("pi3@admin.com", "pi12345")
    assert client.get("/usuarios/", cookies=cookies).status_code == 200
    assert client.get("/reportes/resumen", cookies=cookies).status_code == 200


def test_admin_consulta_sucursales():
    """Protocolo: 'Consultar sucursales.' — el admin ve TODAS, no solo una."""
    cookies = login("pi3@admin.com", "pi12345")
    response = client.get("/sucursales/", cookies=cookies)
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_admin_crea_modifica_y_elimina_sucursal():
    """Protocolo: 'Crear sucursales. Modificar información de las
    sucursales. Eliminar sucursales.'"""
    cookies = login("pi3@admin.com", "pi12345")

    payload = {
        "nombre": f"Sucursal Pytest {uuid.uuid4().hex[:8]}",
        "direccion": "Direccion de prueba",
        "telefono": "5555555555",
        "contacto": None,
        "gerente_id": None,
    }
    response = client.post("/sucursales/", json=payload, cookies=cookies)
    assert response.status_code == 201
    sucursal = response.json()

    payload["direccion"] = "Direccion editada"
    payload["activo"] = True
    response = client.put(f"/sucursales/{sucursal['id']}", json=payload, cookies=cookies)
    assert response.status_code == 200
    assert response.json()["direccion"] == "Direccion editada"

    response = client.delete(f"/sucursales/{sucursal['id']}", cookies=cookies)
    assert response.status_code == 200


def test_admin_registra_gerente_y_lo_asigna_a_una_sucursal():
    """Protocolo: 'Registrar gerentes. Asignar gerentes a las sucursales.'"""
    cookies = login("pi3@admin.com", "pi12345")

    branch_payload = {
        "nombre": f"Sucursal Temp {uuid.uuid4().hex[:6]}",
        "direccion": "Direccion temporal",
        "telefono": "5550000000",
        "contacto": None,
        "gerente_id": None,
    }
    sucursal = client.post("/sucursales/", json=branch_payload, cookies=cookies).json()

    user_payload = {
        "nombre": "Gerente Pytest",
        "correo": f"gerente.pytest.{uuid.uuid4().hex[:8]}@test.com",
        "password": "Test12345",
        "rol_id": 2,
        "sucursal_id": sucursal["id"],
    }
    response = client.post("/usuarios/", json=user_payload, cookies=cookies)
    assert response.status_code == 200
    gerente = response.json()

    branch_payload["activo"] = True
    branch_payload["gerente_id"] = gerente["id"]
    response = client.put(f"/sucursales/{sucursal['id']}", json=branch_payload, cookies=cookies)
    assert response.status_code == 200
    assert response.json()["gerente_id"] == gerente["id"]

    # limpieza
    client.delete(f"/usuarios/{gerente['id']}", cookies=cookies)
    client.delete(f"/sucursales/{sucursal['id']}", cookies=cookies)


def test_admin_consulta_inventario_de_cualquier_sucursal():
    """Protocolo: 'Consultar los inventarios de las diferentes
    sucursales.'"""
    cookies = login("pi3@admin.com", "pi12345")
    assert client.get("/inventario/?sucursal_id=1", cookies=cookies).status_code == 200
    assert client.get("/inventario/?sucursal_id=2", cookies=cookies).status_code == 200


def test_admin_consulta_ventas_de_las_sucursales():
    """Protocolo: 'Consultar las ventas realizadas en las sucursales.'"""
    cookies = login("pi3@admin.com", "pi12345")
    response = client.get("/reportes/ventas", cookies=cookies)
    assert response.status_code == 200


def test_admin_consulta_informacion_general_del_sistema():
    """Protocolo: 'Consultar información general del sistema.'"""
    cookies = login("pi3@admin.com", "pi12345")
    response = client.get("/reportes/resumen", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert "sucursales_activas" in data
    assert "ventas_totales" in data
