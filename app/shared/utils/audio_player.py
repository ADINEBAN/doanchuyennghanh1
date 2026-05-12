"""Simple cross-platform alert sound helper."""

from __future__ import annotations

from pathlib import Path
from typing import Union


class AudioPlayer:
    def play(self, sound_path: Union[str, Path]) -> None:
        path = Path(sound_path)
        if not path.exists():
            return

        try:
            import winsound

            winsound.PlaySound(str(path), winsound.SND_ASYNC)
        except Exception:
            return
