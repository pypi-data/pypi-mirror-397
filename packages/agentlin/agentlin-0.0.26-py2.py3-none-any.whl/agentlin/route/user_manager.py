import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, field_serializer, field_validator
from xlin import *


class UserData(BaseModel):
    """
    UserData is a Pydantic model that represents the data structure for user information.
    It includes fields for user ID, name, email, and other relevant details.
    """

    user_id: str
    name: str
    # use timezone-aware UTC by default to make serialization/deserialization consistent
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    user_profile: str = ""
    preferences: str = ""

    @field_validator("created_at", mode="before")
    def _parse_created_at(cls, v: Any) -> datetime.datetime:
        """Accept ISO strings (with 'Z' or offset) or datetimes; ensure tz-aware UTC datetime."""
        if isinstance(v, str):
            s = v.replace('Z', '+00:00')
            try:
                dt = datetime.datetime.fromisoformat(s)
            except Exception as e:
                raise ValueError(f"Invalid datetime format for created_at: {v}") from e
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt.astimezone(datetime.timezone.utc)
        if isinstance(v, datetime.datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=datetime.timezone.utc)
            return v.astimezone(datetime.timezone.utc)
        # fallback to now UTC
        return datetime.datetime.now(datetime.timezone.utc)

    @field_serializer("created_at")
    def serialize_dt(self, dt: datetime.datetime, _info):
        # always emit UTC with trailing 'Z'
        dt_utc = dt.astimezone(datetime.timezone.utc)
        return dt_utc.isoformat().replace('+00:00', 'Z')



class UserStore:
    """
    UserStore is responsible for managing user data.
    It provides methods to store, retrieve, and delete user information.
    """

    def __init__(self):
        self.users: dict[str, UserData] = {}

    def upsert_user(self, user_id: str, user_data: UserData):
        """Upsert a new user to the store."""
        self.users[user_id] = user_data

    def get_user(self, user_id: str) -> Optional[UserData]:
        """Retrieve user data by user ID."""
        return self.users.get(user_id)

    def delete_user(self, user_id: str):
        """Delete a user from the store."""
        if user_id in self.users:
            del self.users[user_id]

    def update_preferences(self, user_id: str, preferences: str):
        """Update user preferences."""
        if user_id in self.users:
            self.users[user_id].preferences = preferences
        else:
            raise ValueError(f"User with ID {user_id} does not exist.")

    def update_user_profile(self, user_id: str, profile: str):
        """Update user profile information."""
        if user_id in self.users:
            self.users[user_id].user_profile = profile
        else:
            raise ValueError(f"User with ID {user_id} does not exist.")

    def load_from_file(self, file_path: str):
        """Load user data from a file."""
        try:
            jsonlist = read_as_json_list(file_path)
            for user in jsonlist:
                user_data = UserData(**user)
                self.upsert_user(user_data.user_id, user_data)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"Error loading user data: {e}")

    def save_to_file(self, file_path: str):
        """Save user data to a file."""
        try:
            jsonlist = [user.model_dump() for user in self.users.values()]
            save_json_list(jsonlist, file_path)
        except Exception as e:
            print(f"Error saving user data: {e}")


class MemoryManager:
    """
    MemoryManager is responsible for managing the memory of the agent.
    It provides methods to store, retrieve, and delete memory entries.
    """

    def __init__(self):
        self.memory = {}

    def store_memory(self, key: str, value: str):
        """Store a memory entry."""
        self.memory[key] = value

    def retrieve_memory(self, key: str) -> str:
        """Retrieve a memory entry."""
        return self.memory.get(key, "")

    def delete_memory(self, key: str):
        """Delete a memory entry."""
        if key in self.memory:
            del self.memory[key]
