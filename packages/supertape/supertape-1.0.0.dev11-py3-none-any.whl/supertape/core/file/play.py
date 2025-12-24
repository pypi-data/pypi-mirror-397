from __future__ import annotations

from supertape.core.audio.api import BitListener
from supertape.core.audio.signal_out import AudioPlayer, AudioPlayerObserver
from supertape.core.file.api import TapeFile
from supertape.core.file.block import BlockSerializer
from supertape.core.file.bytes import ByteSerializer
from supertape.core.file.tapefile import TapeFileSerializer


class _bit_accumulator(BitListener):
    """Accumulates both bits and silence events for later playback.

    This accumulator stores the complete audio stream including both
    data bits (which generate FSK tones) and silence events (which generate
    zero-level samples). The data is stored as a list of tuples where each
    item is either ('bit', value) or ('silence', None).
    """

    def __init__(self) -> None:
        self.items: list[tuple[str, int | None]] = []

    def process_bit(self, value: int) -> None:
        """Store a data bit."""
        self.items.append(("bit", value))

    def process_silence(self) -> None:
        """Store a silence event marker."""
        self.items.append(("silence", None))


def play_file(file: TapeFile, observer: AudioPlayerObserver, device: int | None = None) -> None:
    bit_accumulator = _bit_accumulator()
    byte_accumulator = ByteSerializer([bit_accumulator])
    block_serializer = BlockSerializer([byte_accumulator])
    tape_serializer = TapeFileSerializer([block_serializer])
    tape_serializer.process_file(file)

    audio_output = AudioPlayer(bit_accumulator.items, observer, device=device)
    audio_output.start()
