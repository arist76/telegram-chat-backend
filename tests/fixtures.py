import pytest
from src.api import Keyclock
from src.models import RoomType, SQLModel, Room, User, Message, engine
from sqlmodel import create_engine, Session
from src.main import app
from fastapi.testclient import TestClient
import httpx


@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    return TestClient(app)


@pytest.fixture(name="engine")
def engine_fixture():
    # Create an in-memory SQLite database
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[Session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="users")
def users_fixture(session: Session):
    user = User(username="dave")
    user1 = User(username="tony")
    user2 = User(username="ivan")
    session.add(user)
    session.add(user1)
    session.add(user2)
    session.commit()

    return [user, user1, user2]


@pytest.fixture(name="rooms")
def rooms_fixture(session: Session, users: list[User]):
    assert users[0].id and users[1].id
    room = Room(owner_id=users[0].id)
    room1 = Room(room_type=RoomType.PRIVATE, owner_id=users[1].id)
    session.add(room)
    session.add(room1)
    session.commit()

    return [room, room1]


@pytest.fixture(name="messages")
def message_fixture(session: Session, users: list[User], rooms: list[Room]):
    message = Message(text="test message", owner=users[0])
    message2 = Message(text="Hello world", owner=users[0])
    message3 = Message(text="Whats up", owner=users[0])
    message4 = Message(text="", owner=users[1])
    message5 = Message(text="Bye!!!", owner=users[1])
    message6 = Message(text="another message", owner=users[2])
    message7 = Message(text="yet another message", owner=users[2])
    session.add(message)
    session.add(message2)
    session.add(message3)
    session.add(message4)
    session.add(message5)
    session.add(message6)
    session.add(message7)
    session.commit()

    return {
        "0": [message, message2, message3],
        "1": [message4, message5],
        "2": [message6, message7],
    }


@pytest.fixture(name="token")
def user_token_fixture(users: list[User]):

    url = (
        "https://stagingauth.mindplex.ai/realms/Mindplex/protocol/openid-connect/token"
    )

    payload = {
        "client_id": "mindplex",
        "username": "dave",
        "password": "dave",
        "grant_type": "password",
        "client_secret": "Dzkhw0zTnV6wgQ59Lsnqm5JaG4CreCAf",
        "scope": "openid",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "AWSALBAPP-0=_remove_; AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_",
    }

    # Send the request
    response = httpx.post(url, headers=headers, data=payload)

    return response.json()["access_token"]

