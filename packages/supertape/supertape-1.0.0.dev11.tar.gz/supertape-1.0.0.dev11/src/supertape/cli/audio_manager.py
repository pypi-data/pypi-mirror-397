"""Audio management for the supertape shell."""

from __future__ import annotations

from typing import Any

from supertape.core.audio.pipeline import AudioInputPipeline, AudioPipelineFactory
from supertape.core.file.api import TapeFileListener
from supertape.core.output.api import OutputStream
from supertape.core.repository.api import TapeFileRepository


class AudioManager:
    """Manages audio operations for the tape shell.

    This class manages the lifecycle of audio operations, using the AudioPipelineFactory
    to create and configure processing pipelines. It provides a simple interface for
    starting and stopping audio listening/recording operations.
    """

    def __init__(self, repository: TapeFileRepository, device: int | None = None) -> None:
        """Initialize the audio manager.

        Args:
            repository: Repository for storing tape files
            device: Optional audio device index
        """
        self.repository = repository
        self.device = device
        self.pipeline: AudioInputPipeline | None = None
        self.is_listening = False
        self.is_recording = False

    def start_listening(
        self, file_handler: TapeFileListener | None = None, output_stream: OutputStream | None = None
    ) -> None:
        """Start listening to audio input.

        Creates an audio input pipeline and starts processing audio. Tape files
        will be printed to the output stream and optionally passed to the file handler.

        Args:
            file_handler: Optional handler for received tape files
            output_stream: Optional output stream for printers. If None, uses default print().
        """
        if self.is_listening:
            return  # Already listening

        # Build list of listeners
        listeners: list[TapeFileListener] = []
        if file_handler:
            listeners.append(file_handler)

        # Create pipeline using factory
        self.pipeline = AudioPipelineFactory.create_input_pipeline(
            tape_file_listeners=listeners,
            output_stream=output_stream,
            device=self.device,
        )

        self.pipeline.start()
        self.is_listening = True

    def start_recording(
        self, file_handler: TapeFileListener, output_stream: OutputStream | None = None
    ) -> None:
        """Start recording audio input to repository.

        Args:
            file_handler: Handler for received tape files (typically saves to repository)
            output_stream: Optional output stream for printers. If None, uses default print().
        """
        if not self.is_listening:
            self.start_listening(file_handler, output_stream)
        self.is_recording = True

    def stop_audio(self) -> None:
        """Stop all audio operations."""
        if self.pipeline:
            self.pipeline.stop()
            self.pipeline = None
        self.is_listening = False
        self.is_recording = False

    def get_status(self) -> dict[str, Any]:
        """Get current audio status.

        Returns:
            Dictionary with status information including:
            - listening: Whether audio input is active
            - recording: Whether recording mode is enabled
            - device: Audio device index or None
            - active: Whether pipeline is running
        """
        return {
            "listening": self.is_listening,
            "recording": self.is_recording,
            "device": self.device,
            "active": self.pipeline is not None and self.is_listening,
        }
