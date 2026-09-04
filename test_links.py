import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from main import app


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


def create_links(client, count):
    for index in range(count):
        client.post(
            '/api/links',
            json={
                'original_url': f'https://example.com/{index}',
                'short_name': f'link-{index}',
            },
        )


def test_pagination_first_page(client):
    create_links(client, 15)

    response = client.get('/api/links', params={'range': '[0,10]'})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert data[0]['short_name'] == 'link-0'
    assert data[-1]['short_name'] == 'link-9'
    assert response.headers['Content-Range'] == 'links 0-10/15'


def test_pagination_second_page(client):
    create_links(client, 11)

    response = client.get('/api/links', params={'range': '[5,10]'})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]['short_name'] == 'link-5'
    assert data[-1]['short_name'] == 'link-9'
    assert response.headers['Content-Range'] == 'links 5-10/11'


def test_pagination_range_beyond_total(client):
    create_links(client, 3)

    response = client.get('/api/links', params={'range': '[0,10]'})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert response.headers['Content-Range'] == 'links 0-3/3'


def test_pagination_without_range_returns_all(client):
    create_links(client, 4)

    response = client.get('/api/links')

    assert response.status_code == 200
    assert len(response.json()) == 4
    assert 'Content-Range' not in response.headers


def test_pagination_invalid_range_format(client):
    response = client.get('/api/links', params={'range': 'not-json'})

    assert response.status_code == 422
    assert 'detail' in response.json()


def test_pagination_invalid_range_order(client):
    response = client.get('/api/links', params={'range': '[10,5]'})

    assert response.status_code == 422
    assert 'detail' in response.json()


def test_pagination_negative_start(client):
    response = client.get('/api/links', params={'range': '[-1,5]'})

    assert response.status_code == 422
    assert 'detail' in response.json()