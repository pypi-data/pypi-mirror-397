"""Audio control commands for the tape shell.

This module contains commands for playing, listening, and recording audio.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from rich.progress import Progress

from supertape.cli.commands.base import ShellCommand
from supertape.core.audio.progress import RichProgressObserver
from supertape.core.file.load import container_load
from supertape.core.file.play import play_file

if TYPE_CHECKING:
    from supertape.cli.shell import TapeShell


class PlayCommand(ShellCommand):
    """Play a tape file or K7 container to audio output."""

    @property
    def name(self) -> str:
        return "play"

    @property
    def description(self) -> str:
        return "Play a tape file to audio output"

    @property
    def usage(self) -> str:
        return "play <filename>"

    @property
    def help_text(self) -> str:
        return """Play a tape file or K7 container to audio output

Usage: play <filename>

Supported sources:
  • Files in database: BASIC, MACHINE, ASMSRC, DATA
  • K7 files on disk: .k7 extension

For K7 containers with multiple files:
  • Displays list of all files
  • Plays files sequentially
  • Pauses between files for confirmation
  • Shows progress with animated progress bar

Examples:
  play GAME.BAS              Play file from database
  play /path/to/multi.k7     Play K7 container from disk"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute play command."""
        if not args:
            shell.ui.show_error("Usage: play <filename>")
            return

        filename = args[0]
        tape_files = shell.repository.get_tape_files()

        # First check if it's a K7 file on disk
        file_path = Path(filename)
        if file_path.exists() and file_path.suffix.lower() == ".k7":
            # Load the K7 container from disk
            try:
                container = container_load(str(file_path))
                shell._play_k7_container(container)
                return
            except Exception as e:
                shell.ui.show_error(f"Failed to load K7 file: {e}")
                return

        # Otherwise, find the file in the repository
        target_file = None
        for tape_file in tape_files:
            if tape_file.fname.lower() == filename.lower():
                target_file = tape_file
                break

        if target_file is None:
            shell.ui.show_error(f"File not found: {filename}")
            shell._suggest_similar_files(filename, tape_files)
            return

        # Play the tape file to audio output with animated progress bar
        try:
            with Progress() as progress:
                # Create progress task
                task_id = progress.add_task(f"[magenta]Playing {target_file.fname}...", total=100)

                # Create observer with progress bar
                observer = RichProgressObserver(progress, task_id, post_delay=0.5)

                # Start playback
                play_file(file=target_file, observer=observer, device=shell.audio_manager.device)

                # Wait for playback to complete before returning to prompt
                observer.wait_for_completion()

            # Show completion message after progress bar is done
            shell.ui.show_success(f"Playback complete: {target_file.fname}")
        except Exception as e:
            shell.ui.show_error(f"Playback failed: {e}")


class ListenCommand(ShellCommand):
    """Start listening to audio input (passive monitoring)."""

    @property
    def name(self) -> str:
        return "listen"

    @property
    def description(self) -> str:
        return "Start listening to audio input"

    @property
    def help_text(self) -> str:
        return """Start listening to audio input (passive monitoring)

Usage: listen

Starts monitoring the audio input:
  • Displays received data in real-time
  • Shows block information and file headers
  • Does NOT save files to database

Use 'record' instead if you want to save received files.
Use 'stop' to halt listening.

Tip: The prompt shows 🔴 when listening is active"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute listen command."""
        if shell.audio_manager.is_listening:
            shell.ui.show_warning("Audio listening is already active")
            return

        try:
            shell.audio_manager.start_listening(output_stream=shell.output_stream)
            shell.ui.show_success("Started listening to audio input")
            shell.ui.show_info("Audio data will be processed and displayed. Use 'stop' to halt.")
        except Exception as e:
            shell.ui.show_error(f"Failed to start listening: {e}")


class RecordCommand(ShellCommand):
    """Start recording from audio input to database."""

    @property
    def name(self) -> str:
        return "record"

    @property
    def description(self) -> str:
        return "Start recording from audio input"

    @property
    def help_text(self) -> str:
        return """Start recording from audio input to database

Usage: record

Starts recording from audio input:
  • Listens for incoming tape files
  • Automatically saves received files to database
  • Displays progress and file information

Difference from 'listen':
  • listen: Passive monitoring, does NOT save
  • record: Active recording, SAVES to database

Use 'stop' to halt recording.

Tip: The prompt shows 🔴 when recording is active"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute record command."""
        if shell.audio_manager.is_recording:
            shell.ui.show_warning("Audio recording is already active")
            return

        try:
            from supertape.cli.shell import TapeFileHandler

            file_handler = TapeFileHandler(shell.repository)
            shell.audio_manager.start_recording(file_handler, output_stream=shell.output_stream)
            shell.ui.show_success("Started recording from audio input")
            shell.ui.show_info("Received tape files will be automatically saved to the database.")
            shell.ui.show_info("Use 'stop' to halt recording.")
        except Exception as e:
            shell.ui.show_error(f"Failed to start recording: {e}")


class StopCommand(ShellCommand):
    """Stop all audio operations."""

    @property
    def name(self) -> str:
        return "stop"

    @property
    def description(self) -> str:
        return "Stop all audio operations"

    @property
    def help_text(self) -> str:
        return """Stop all audio operations

Usage: stop

Stops:
  • Audio listening (started with 'listen')
  • Audio recording (started with 'record')

Safe to use anytime, even if no audio operations are active.

Tip: The prompt shows ⚫ when audio is inactive"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute stop command."""
        if not shell.audio_manager.is_listening:
            shell.ui.show_warning("No audio operations are currently active")
            return

        try:
            shell.audio_manager.stop_audio()
            shell.ui.show_success("Stopped all audio operations")
        except Exception as e:
            shell.ui.show_error(f"Failed to stop audio operations: {e}")
