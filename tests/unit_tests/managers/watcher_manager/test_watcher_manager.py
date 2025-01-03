from pathlib import Path

from aims.managers.watcher_manager import WatcherManager


def test_watcher_manager_setup(
    watcher_manager: WatcherManager,
    tmp_path: Path,
):
    watcher_manager.setup(
        path=str(tmp_path),
    )

    assert any([
        watch.path == str(tmp_path)
        for watch in watcher_manager.observer._watches
    ])


def test_watcher_manager_setup_after_update_path(
    watcher_manager: WatcherManager,
    tmp_path: Path,
):
    watcher_manager.setup(
        path=str(tmp_path),
    )
    watcher_manager.setup(
        path=str(tmp_path),
    )

    assert any([
        watch.path == str(tmp_path)
        for watch in watcher_manager.observer._watches
    ])
