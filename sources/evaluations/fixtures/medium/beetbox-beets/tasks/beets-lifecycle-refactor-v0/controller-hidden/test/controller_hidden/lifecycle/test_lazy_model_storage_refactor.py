from __future__ import annotations

from beets.test import _common
from beets.test.helper import TestHelper


class TestLazyModelStorageBehavior(TestHelper):
    def test_database_round_trip_preserves_fixed_and_flexible_values(self) -> None:
        item = _common.item(self.lib)
        item["custom_field"] = "custom value"
        item.store()

        loaded = self.lib.get_item(item.id)
        assert loaded is not None
        assert loaded.title == "the title"
        assert loaded.year == 1
        assert loaded.genres == ["the genre"]
        assert loaded["custom_field"] == "custom value"

    def test_storage_mappings_support_iteration_copy_and_mutation(self) -> None:
        item = _common.item(self.lib)
        loaded = self.lib.get_item(item.id)
        assert loaded is not None

        fixed = loaded._values_fixed
        before = fixed.copy()
        assert "title" in list(fixed)
        assert before["title"] == "the title"
        fixed["title"] = "changed"
        assert fixed["title"] == "changed"
        assert before["title"] == "the title"

        flex = loaded._values_flex
        flex["temporary"] = "value"
        assert dict(flex.items())["temporary"] == "value"
        del flex["temporary"]
        assert "temporary" not in flex

    def test_model_mapping_delete_and_reinsert_preserves_semantics(self) -> None:
        item = _common.item(self.lib)
        item["temporary"] = "first"
        assert item["temporary"] == "first"
        del item["temporary"]
        assert "temporary" not in item
        item["temporary"] = "second"
        assert item.get("temporary") == "second"
