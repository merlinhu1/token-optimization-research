from __future__ import annotations

import pytest

from beets.exceptions import UserError
from beets.test.helper import IOMixin, TestHelper


class ModifyHelper(IOMixin):
    def modify(self, *args: str) -> None:
        self.io.addinput("y")
        self.run_command("modify", *args)


class TestMultiValue(ModifyHelper, TestHelper):
    @pytest.fixture
    def item(self):
        album = self.add_album_fixture()
        [item] = album.items()
        return item

    @pytest.mark.parametrize(
        "initial_genres,modify_arg,expected_genres",
        [
            ([], "genres=Jazz; Blues", ["Jazz", "Blues"]),
            (["Jazz", "Blues"], "genres+=Funk", ["Jazz", "Blues", "Funk"]),
            (["Jazz", "Funk"], "genres+=Funk", ["Jazz", "Funk"]),
            (["Jazz", "Blues", "Funk"], "genres-=Blues", ["Jazz", "Funk"]),
            (["Jazz", "Blues Rock", "Blues"], "genres-=Blues", ["Jazz", "Blues Rock"]),
            (["Jazz", "Blues"], "genres+=Funk; Soul", ["Jazz", "Blues", "Funk", "Soul"]),
        ],
    )
    def test_modify_multi_value(self, item, initial_genres, modify_arg, expected_genres) -> None:
        item.genres = initial_genres
        item.store()
        self.modify("--nowrite", "--nomove", modify_arg)
        item.load()
        assert item.genres == expected_genres

    def test_modify_scalar_operator_error(self, item) -> None:
        original_title = item.title
        with pytest.raises(UserError) as exc_info:
            self.modify("--nowrite", "--nomove", "title+=foo")
        message = str(exc_info.value)
        assert "title" in message
        assert "+=" in message
        item.load()
        assert item.title == original_title
