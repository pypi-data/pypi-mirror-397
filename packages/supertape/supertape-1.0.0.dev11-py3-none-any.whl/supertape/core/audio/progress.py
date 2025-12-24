"""Standard progress reporting implementations for audio playback.

This module provides base classes for tracking audio playback progress and
completion, eliminating duplication across different user interfaces.
"""

from __future__ import annotations

import time

from rich.progress import Progress, TaskID

from supertape.core.audio.signal_out import AudioPlayerObserver, AudioPlayerProgress


class BasePlaybackObserver(AudioPlayerObserver):
    """Base observer with completion tracking and configurable wait logic.

    This base class provides common functionality for tracking playback
    completion and blocking until playback finishes. It eliminates duplication
    across different observer implementations by centralizing the core logic.

    Args:
        poll_interval: How often to check for completion (seconds). Default: 0.1
        post_delay: Delay after completion before returning (seconds). Default: 0.0

    Example:
        >>> observer = BasePlaybackObserver(poll_interval=0.5, post_delay=0.5)
        >>> # ... pass to audio player ...
        >>> observer.wait_for_completion()  # Blocks until done
    """

    def __init__(self, poll_interval: float = 0.1, post_delay: float = 0.0) -> None:
        """Initialize the observer with configurable timing.

        Args:
            poll_interval: How often to check for completion (seconds)
            post_delay: Delay after completion before returning (seconds)
        """
        self._completed = False
        self._poll_interval = poll_interval
        self._post_delay = post_delay

    def on_progress(self, progress: AudioPlayerProgress) -> None:
        """Track completion status.

        Called by audio player to report progress. Marks as complete when
        progress reaches target.

        Args:
            progress: Progress information from audio player
        """
        if progress.progress == progress.target:
            self._completed = True

    def is_complete(self) -> bool:
        """Check if playback is complete.

        Returns:
            True if playback has finished, False otherwise
        """
        return self._completed

    def wait_for_completion(self) -> None:
        """Block until playback completes.

        Polls completion status at the configured interval, then applies
        the post-completion delay if configured.
        """
        while not self._completed:
            time.sleep(self._poll_interval)

        if self._post_delay > 0:
            time.sleep(self._post_delay)


class RichProgressObserver(BasePlaybackObserver):
    """Observer with Rich progress bar integration.

    This observer extends the base completion tracking with Rich library
    progress bar updates. It guards against division by zero and provides
    visual feedback during playback.

    Args:
        progress: Rich Progress instance
        task_id: Task ID for the progress bar
        poll_interval: How often to check for completion (seconds). Default: 0.1
        post_delay: Delay after completion before returning (seconds). Default: 0.0

    Example:
        >>> from rich.progress import Progress
        >>> with Progress() as progress:
        ...     task = progress.add_task("Playing...", total=100)
        ...     observer = RichProgressObserver(progress, task)
        ...     # ... pass to audio player ...
        ...     observer.wait_for_completion()
    """

    def __init__(
        self, progress: Progress, task_id: TaskID, poll_interval: float = 0.1, post_delay: float = 0.0
    ) -> None:
        """Initialize the Rich progress observer.

        Args:
            progress: Rich Progress instance
            task_id: Task ID for the progress bar
            poll_interval: How often to check for completion (seconds)
            post_delay: Delay after completion before returning (seconds)
        """
        super().__init__(poll_interval, post_delay)
        self.progress = progress
        self.task_id = task_id

    def on_progress(self, progress_info: AudioPlayerProgress) -> None:
        """Update Rich progress bar and track completion.

        Guards against division by zero and updates the progress bar
        with current playback position.

        Args:
            progress_info: Progress information from audio player
        """
        # Guard against division by zero
        if progress_info.target == 0:
            return

        # Update progress bar
        self.progress.update(self.task_id, completed=progress_info.progress, total=progress_info.target)

        # Track completion (via parent class)
        super().on_progress(progress_info)
