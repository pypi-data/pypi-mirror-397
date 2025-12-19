from typing import Optional
from .teamtv_object import TeamTVObject


class CustomTag(TeamTVObject):
    @property
    def custom_tag_id(self) -> str:
        return self._custom_tag_id

    @property
    def key(self) -> str:
        return self._key

    @property
    def description(self) -> str:
        return self._description

    @property
    def duration_before(self) -> float:
        return self._duration_before

    @property
    def duration_after(self) -> float:
        return self._duration_after

    @property
    def config(self) -> Optional[dict]:
        return self._config

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def updated_at(self) -> str:
        return self._updated_at

    def __repr__(self):
        return f"<CustomTag custom_tag_id={self.custom_tag_id} key='{self.key}' description='{self.description}'>"

    def _use_attributes(self, attributes: dict):
        self._custom_tag_id = attributes["customTagId"]
        self._key = attributes["key"]
        self._description = attributes["description"]
        self._duration_before = attributes["durationBefore"]
        self._duration_after = attributes["durationAfter"]
        self._config = attributes.get("config")
        self._created_at = attributes["createdAt"]
        self._updated_at = attributes["updatedAt"]

        super()._use_attributes(attributes)
