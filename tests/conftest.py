import pytest

from mimiron.api import app as _app
from mimiron.ext import db

@pytest.fixture
def app(request):
    _app.config['TESTING'] = True

    ctx = _app.app_context()
    ctx.push()

    def tear_down():
        ctx.pop()

    request.addfinalizer(tear_down)
    return _app

@pytest.yield_fixture
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_db(request, app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/mimirontest'
    db.create_all()

    def tear_down():
        db.session.remove()
        db.drop_all()

    request.addfinalizer(tear_down)

