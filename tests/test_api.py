"""Tests pour l'API de triangulation dans zz_app."""
import pytest

from zz_app import app, tri


def verify_error_json_response(response):
    """Vérifie que la réponse JSON contient le code d'erreur et le message attendus."""
    expected_code = "TRIANGULATION_FAILED"
    expected_message = "Triangulation could not be computed for the given point set."

    if response.headers["Content-Type"] != "application/json":
        return False

    json_data = response.get_json()
    return json_data["code"] == expected_code \
        and json_data["message"] == expected_message

@pytest.fixture
def client():
    """Fixture pour le client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_triangulation_success_binary(client, monkeypatch):
    """Teste que la route retourne une triangulation binaire réussie."""
    def fake_triangulate(pointSetId):
        return b"\x00\x00\x00\x00"

    monkeypatch.setattr(tri, "triangulate", fake_triangulate)
    response = client.get("/triangulation/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/octet-stream"
    assert response.data == b"\x00\x00\x00\x00"


def test_invalid_uuid_returns_400(client, monkeypatch):
    """Teste que la route retourne un code 400 pour un UUID invalide."""
    def fake_triangulate(pointSetId):
        raise Exception("incorrect uuid format")

    monkeypatch.setattr(tri, "triangulate", fake_triangulate)
    response = client.get("/triangulation/mauvais-uuid")
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert verify_error_json_response(response)

def test_pointset_not_found_returns_404(client, monkeypatch):
    """Teste que la route retourne un code 404 lorsque le point set n'est pas trouvé."""
    def fake_triangulate(pointSetId):
        raise Exception("Point set not found")

    monkeypatch.setattr(tri, "triangulate", fake_triangulate)
    response = client.get("/triangulation/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert verify_error_json_response(response)


def test_triangulation_internal_error_returns_500(client, monkeypatch):
    """Teste que la route retourne un code 500 en cas d'erreur interne du serveur."""
    def fake_triangulate(pointSetId):
        raise Exception("internal server error")
    monkeypatch.setattr(tri, "triangulate", fake_triangulate)
    response = client.get("/triangulation/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 500
    assert response.headers["Content-Type"] == "application/json"
    assert verify_error_json_response(response)


def test_pointset_manager_unavailable_returns_503(client, monkeypatch):
    """Test 503 si gestionnaire indisponible."""
    def fake_triangulate(pointSetId):
        raise Exception("point set manager unavailable")
    monkeypatch.setattr(tri, "triangulate", fake_triangulate)
    response = client.get("/triangulation/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 503
    assert response.headers["Content-Type"] == "application/json"
    assert verify_error_json_response(response)