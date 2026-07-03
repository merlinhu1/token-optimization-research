from __future__ import annotations

from beets import plugins
from beets.autotag import AlbumInfo, TrackInfo
from beets.test.helper import PluginTestHelper
from beetsplug import ftintitle


class TestFtInTitleReview(PluginTestHelper):
    plugin = "ftintitle"
    preload_plugin = False

    def test_auto_disabled_preserves_metadata(self) -> None:
        info = TrackInfo(artist="Alice feat. Bob", title="Song")
        with self.configure_plugin({"auto": False}):
            plugins.send("trackinfo_received", info=info)
        assert info.artist == "Alice feat. Bob"
        assert info.title == "Song"

    def test_bare_singleton_collaboration_is_not_fabricated(self) -> None:
        info = TrackInfo(artist="Alice & Bob", title="Song")
        with self.configure_plugin({"auto": True}):
            plugins.send("trackinfo_received", info=info)
        assert info.artist == "Alice & Bob"
        assert info.title == "Song"

    def test_drop_and_keep_together_are_a_noop(self) -> None:
        info = TrackInfo(artist="Alice feat. Bob", title="Song")
        with self.configure_plugin({"drop": True, "keep_in_artist": True}):
            plugin = next(iter(plugins.find_plugins()))
            assert isinstance(plugin, ftintitle.FtInTitlePlugin)
            assert plugin.ft_in_title(info, "") is False
        assert info.artist == "Alice feat. Bob"
        assert info.title == "Song"

    def test_artist_credit_is_preserved_when_credit_mode_is_disabled(self) -> None:
        self.config["artist_credit"] = False
        info = TrackInfo(
            artist="Alice feat. Bob",
            artist_credit="Alice feat. Bobby",
            title="Song",
        )
        with self.configure_plugin({"auto": True}):
            plugins.send("trackinfo_received", info=info)
        assert info.artist == "Alice"
        assert info.artist_credit == "Alice feat. Bobby"
        assert info.title == "Song feat. Bob"
        assert info.item_data["artist_credit"] == "Alice feat. Bobby"

    def test_album_hook_uses_album_artist_for_bare_collaboration(self) -> None:
        track = TrackInfo(
            artist="Alice & Bob",
            artist_sort="Alice & Bob",
            title="Song",
        )
        album = AlbumInfo(artist="Alice", album="Album", tracks=[track])
        with self.configure_plugin({"auto": True}):
            plugins.send("albuminfo_received", info=album)
        assert track.artist == "Alice"
        assert track.artist_sort == "Alice"
        assert track.title == "Song feat. Bob"
        assert track.item_data["artist"] == "Alice"
        assert track.item_data["title"] == "Song feat. Bob"
