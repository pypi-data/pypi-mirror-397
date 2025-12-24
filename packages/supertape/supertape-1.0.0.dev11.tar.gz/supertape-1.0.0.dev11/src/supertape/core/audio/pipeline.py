"""Audio processing pipeline factory.

This module provides a factory for creating complete audio processing pipelines,
encapsulating the complexity of connecting audio input/output components with
file processing stages.
"""

from __future__ import annotations

from supertape.core.audio.modulation import AudioDemodulator
from supertape.core.audio.signal_in import AudioInput
from supertape.core.file.api import TapeFileListener
from supertape.core.file.block import BlockParser, BlockPrinter
from supertape.core.file.bytes import ByteDecoder
from supertape.core.file.tapefile import TapeFileLoader, TapeFilePrinter
from supertape.core.output.api import OutputStream


class AudioInputPipeline:
    """Encapsulates an audio input processing pipeline.

    This class provides a unified interface for managing the lifecycle of an
    audio input pipeline, hiding the complexity of the underlying components.
    """

    def __init__(self, audio_input: AudioInput) -> None:
        """Initialize with an AudioInput instance.

        Args:
            audio_input: Configured AudioInput instance
        """
        self.audio_input = audio_input

    def start(self) -> None:
        """Start the audio input pipeline."""
        self.audio_input.start()

    def stop(self) -> None:
        """Stop the audio input pipeline."""
        self.audio_input.stop()

    def is_alive(self) -> bool:
        """Check if the audio input thread is running.

        Returns:
            True if the thread is alive, False otherwise
        """
        return self.audio_input.is_alive()


class AudioPipelineFactory:
    """Factory for creating audio processing pipelines.

    This factory encapsulates the knowledge of how to construct complete
    audio processing pipelines, connecting all necessary components in
    the correct order.
    """

    @staticmethod
    def create_input_pipeline(
        tape_file_listeners: list[TapeFileListener] | None = None,
        output_stream: OutputStream | None = None,
        device: int | None = None,
        sample_rate: int = 44100,
        daemon: bool = True,
    ) -> AudioInputPipeline:
        """Create complete audio input pipeline.

        Constructs a pipeline that processes audio input through the following stages:
        1. AudioInput - Captures audio samples
        2. AudioDemodulator - Demodulates FSK audio to bits
        3. ByteDecoder - Converts bits to bytes
        4. BlockParser - Parses bytes into data blocks
        5. TapeFileLoader - Assembles blocks into complete tape files

        The pipeline automatically includes printers for blocks and tape files,
        and can accept additional tape file listeners for custom processing.

        Args:
            tape_file_listeners: Optional list of listeners for completed tape files.
                                These receive tape files after they're fully loaded.
            output_stream: Optional output stream for printers. If None, uses default print().
            device: Audio device index. If None, uses default input device.
            sample_rate: Sample rate in Hz (default: 44100)
            daemon: Run audio thread as daemon (default: True)

        Returns:
            Configured AudioInputPipeline ready to start

        Example:
            >>> from supertape.core.audio.pipeline import AudioPipelineFactory
            >>> pipeline = AudioPipelineFactory.create_input_pipeline()
            >>> pipeline.start()
            >>> # Audio processing happens in background
            >>> pipeline.stop()
        """
        # Default to empty list if not provided
        if tape_file_listeners is None:
            tape_file_listeners = []

        # Create printer components
        file_printer = TapeFilePrinter(stream=output_stream)
        block_printer = BlockPrinter(stream=output_stream)

        # Combine printers with custom listeners
        all_file_listeners = [file_printer] + tape_file_listeners

        # Build pipeline from right to left (output to input)
        file_loader = TapeFileLoader(all_file_listeners)
        block_parser = BlockParser([block_printer, file_loader])
        byte_decoder = ByteDecoder([block_parser])
        demodulator = AudioDemodulator([byte_decoder], rate=sample_rate)

        # Create audio input with the complete chain
        audio_input = AudioInput([demodulator], daemon=daemon, device=device)

        return AudioInputPipeline(audio_input)
