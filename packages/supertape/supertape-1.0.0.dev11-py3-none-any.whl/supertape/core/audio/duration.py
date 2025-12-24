"""Duration calculation for tape files.

This module provides functionality to calculate the duration of tape files
without actually playing them. It reuses the existing audio modulation pipeline
in "dry-run" mode, counting samples instead of writing to an audio device.
"""

from collections.abc import Sequence

from supertape.core.audio.api import AudioSignalListener
from supertape.core.audio.modulation import AudioModulator
from supertape.core.file.api import TapeFile
from supertape.core.file.block import BlockSerializer
from supertape.core.file.bytes import ByteSerializer


class SampleCounter(AudioSignalListener):
    """Counts audio samples without generating actual audio.

    This listener implements the AudioSignalListener interface but instead of
    writing samples to an audio device, it simply counts them. This allows
    accurate duration calculation by reusing the existing modulation logic.
    """

    def __init__(self) -> None:
        self._total_samples = 0

    def process_samples(self, samples: Sequence[int]) -> None:
        """Count samples without writing to device.

        Args:
            samples: Sequence of audio sample values to count
        """
        self._total_samples += len(samples)

    def get_total_samples(self) -> int:
        """Get the total number of samples counted.

        Returns:
            Total sample count
        """
        return self._total_samples


def calculate_duration(tape_file: TapeFile, sample_rate: int = 44100) -> float:
    """Calculate the duration of a TapeFile without playing audio.

    Reuses the existing audio modulation pipeline but counts samples
    instead of writing to an audio device. Guarantees accuracy by using
    the exact same timing logic as actual playback.

    The calculation pipeline:
    TapeFile → BlockSerializer → ByteSerializer → AudioModulator → SampleCounter

    This ensures:
    - Zero logic duplication (reuses existing format logic)
    - Perfect accuracy (same timing as real playback)
    - Automatic updates (format changes reflected immediately)

    Args:
        tape_file: The TapeFile to calculate duration for
        sample_rate: Audio sample rate in Hz (default: 44100)

    Returns:
        Duration in seconds

    Example:
        >>> from supertape.core.file.load import load_k7_file
        >>> tape_file = load_k7_file("program.k7")
        >>> duration = calculate_duration(tape_file)
        >>> print(f"Duration: {duration:.1f} seconds")
        Duration: 45.3 seconds
    """
    # Create pipeline: BlockSerializer → ByteSerializer → AudioModulator → SampleCounter
    sample_counter = SampleCounter()
    modulator = AudioModulator([sample_counter], sample_rate)
    byte_serializer = ByteSerializer([modulator])
    block_serializer = BlockSerializer([byte_serializer])

    # Process all blocks through the pipeline
    for block in tape_file.blocks:
        block_serializer.process_block(block)

    # Calculate duration from total samples
    total_samples = sample_counter.get_total_samples()
    return total_samples / sample_rate


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2m 34s", "45s", "1h 23m")

    Examples:
        >>> format_duration(45.5)
        '46s'
        >>> format_duration(154.2)
        '2m 34s'
        >>> format_duration(4923.0)
        '1h 22m'
        >>> format_duration(0.5)
        '1s'
    """
    # Use int(seconds + 0.5) for proper "round half up" behavior
    # instead of round() which uses "round half to even" (banker's rounding)
    total_seconds = int(seconds + 0.5)

    if total_seconds < 60:
        return f"{total_seconds}s"

    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60

    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes > 0:
        return f"{hours}h {remaining_minutes}m"
    return f"{hours}h"
