import uuid

from auth.services.auth_service import AccountCacheDTO, AccountCacheSessionDTO
from core.storage import Storage


async def test_storage(storage: Storage) -> None:
    session_value = AccountCacheDTO(
        id=uuid.uuid4(),
        email="user@mail.com",
        sessions=[AccountCacheSessionDTO(session_id=uuid.uuid4(), device="testclient")],
    )

    await storage.save("sessions", str(session_value.id), session_value)

    value_from_cache = await storage.get("sessions", str(session_value.id), model_type=AccountCacheDTO)
    assert value_from_cache == session_value
