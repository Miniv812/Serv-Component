from datetime import datetime, timezone
from decimal import Decimal


class InMemoryStorage:
    """Сховище сутностей предметної області в оперативній пам'яті."""

    def __init__(self) -> None:
        self.users: dict[int, dict] = {}
        self.categories: dict[int, dict] = {}
        self.records: dict[int, dict] = {}
        self._user_seq: int = 1
        self._category_seq: int = 1
        self._record_seq: int = 1

    def create_user(self, name: str) -> dict:
        user_id = self._user_seq
        self._user_seq += 1
        user = {
            "id": user_id,
            "name": name,
        }
        self.users[user_id] = user
        return user

    def get_user(self, user_id: int) -> dict | None:
        return self.users.get(user_id)

    def get_all_users(self) -> list[dict]:
        return list(self.users.values())

    def delete_user(self, user_id: int) -> bool:
        return self.users.pop(user_id, None) is not None

    def create_category(self, name: str) -> dict:
        category_id = self._category_seq
        self._category_seq += 1
        category = {
            "id": category_id,
            "name": name,
        }
        self.categories[category_id] = category
        return category

    def get_category(self, category_id: int) -> dict | None:
        return self.categories.get(category_id)

    def get_all_categories(self) -> list[dict]:
        return list(self.categories.values())

    def delete_category(self, category_id: int) -> bool:
        return self.categories.pop(category_id, None) is not None

    def create_record(
        self,
        user_id: int,
        category_id: int,
        amount: Decimal,
    ) -> dict:
        record_id = self._record_seq
        self._record_seq += 1
        record = {
            "id": record_id,
            "user_id": user_id,
            "category_id": category_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "amount": float(amount),
        }
        self.records[record_id] = record
        return record

    def get_record(self, record_id: int) -> dict | None:
        return self.records.get(record_id)

    def delete_record(self, record_id: int) -> bool:
        return self.records.pop(record_id, None) is not None

    def filter_records(
        self,
        user_id: int | None = None,
        category_id: int | None = None,
    ) -> list[dict]:
        result = list(self.records.values())
        if user_id is not None:
            result = [r for r in result if r["user_id"] == user_id]
        if category_id is not None:
            result = [r for r in result if r["category_id"] == category_id]
        return result


storage = InMemoryStorage()
