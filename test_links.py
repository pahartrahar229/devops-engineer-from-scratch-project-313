import pytest
from fastapi.testclient import TestClient
from main import app
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session


@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name='client')
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_create_link(client):
    response = client.post(
        '/api/links',
        json={
            'original_url': 'https://example.com/long-url',
            'short_name': 'exmpl',
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data['original_url'] == 'https://example.com/long-url'
    assert data['short_name'] == 'exmpl'
    assert data['short_url'].endswith('/r/exmpl')
    assert 'id' in data


def test_list_links(client):
    client.post(
        '/api/links',
        json={'original_url': 'https://a.com', 'short_name': 'a1'},
    )
    client.post(
        '/api/links',
        json={'original_url': 'https://b.com', 'short_name': 'b1'},
    )

    response = client.get('/api/links')

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_link(client):
    created = client.post(
        '/api/links',
        json={'original_url': 'https://example.com', 'short_name': 'ex1'},
    ).json()

    response = client.get(f"/api/links/{created['id']}")

    assert response.status_code == 200
    assert response.json()['short_name'] == 'ex1'


def test_get_link_not_found(client):
    response = client.get('/api/links/999')

    assert response.status_code == 404
    assert 'detail' in response.json()


def test_update_link(client):
    created = client.post(
        '/api/links',
        json={'original_url': 'https://old.com', 'short_name': 'old1'},
    ).json()

    response = client.put(
        f"/api/links/{created['id']}",
        json={'original_url': 'https://new.com', 'short_name': 'new1'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['original_url'] == 'https://new.com'
    assert data['short_name'] == 'new1'


def test_update_link_not_found(client):
    response = client.put(
        '/api/links/999',
        json={'original_url': 'https://x.com', 'short_name': 'x1'},
    )

    assert response.status_code == 404


def test_delete_link(client):
    created = client.post(
        '/api/links',
        json={'original_url': 'https://del.com', 'short_name': 'del1'},
    ).json()

    response = client.delete(f"/api/links/{created['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/api/links/{created['id']}")
    assert get_response.status_code == 404


def test_delete_link_not_found(client):
    response = client.delete('/api/links/999')

    assert response.status_code == 404


def test_redirect(client):
    client.post(
        '/api/links',
        json={
            'original_url': 'https://target.example.com',
            'short_name': 'redir1',
        },
    )

    response = client.get('/r/redir1', follow_redirects=False)

    assert response.status_code == 302
    assert response.headers['location'] == 'https://target.example.com'


def test_redirect_not_found(client):
    response = client.get('/r/unknown', follow_redirects=False)

    assert response.status_code == 404
    assert 'detail' in response.json()


def test_create_link_invalid_body(client):
    response = client.post('/api/links', json={'original_url': 'no-name'})

    assert response.status_code == 422
    assert 'detail' in response.json()


def test_create_link_duplicate_short_name(client):
    client.post(
        '/api/links',
        json={'original_url': 'https://a.com', 'short_name': 'dup'},
    )
    response = client.post(
        '/api/links',
        json={'original_url': 'https://b.com', 'short_name': 'dup'},
    )

    assert response.status_code == 422
    assert 'detail' in response.json()