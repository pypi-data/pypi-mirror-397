import os
from typing import Any

import pyaudio

AUDIO_CHUNKSIZE: int = 2048
AUDIO_FORMAT: int = pyaudio.paInt16
AUDIO_CHANNELS: int = 1

AUDIO_TARGET_LEVEL: int = 25000


class AudioDevice:
    def __init__(self) -> None:
        # Suppress ALSA/JACK errors during PyAudio initialization
        # These errors come from C libraries, so we need to redirect the actual stderr file descriptor
        stderr_fd = 2
        saved_stderr = os.dup(stderr_fd)
        try:
            devnull_fd = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull_fd, stderr_fd)
            os.close(devnull_fd)
            self.p: pyaudio.PyAudio = pyaudio.PyAudio()
        finally:
            os.dup2(saved_stderr, stderr_fd)
            os.close(saved_stderr)

    def __del__(self) -> None:
        self.p.terminate()

    def get_sample_rate(self, device: int | None = None) -> int:
        if device is None:
            device = self.get_default_device()

        device_info: dict[str, Any] = self.p.get_device_info_by_host_api_device_index(0, device)

        # TODO: Remove this hack related to a specific USB audio interface
        if "USB Audio Device: - (hw:" in device_info["name"]:
            return 48000

        sample_rate = device_info.get("defaultSampleRate")
        if sample_rate is None:
            raise ValueError(f"No sample rate found for device {device}")
        return int(sample_rate)

    def open_stream(
        self,
        input: bool | None = None,
        output: bool | None = None,
        input_device_index: int | None = None,
        output_device_index: int | None = None,
        stream_callback: Any | None = None,
    ) -> pyaudio.Stream:
        rate: int = (
            self.get_sample_rate(input_device_index)
            if input_device_index is not None
            else self.get_sample_rate(output_device_index)
        )

        return self.p.open(
            format=AUDIO_FORMAT,
            channels=AUDIO_CHANNELS,
            rate=rate,
            input_device_index=input_device_index,
            output_device_index=output_device_index,
            input=input,
            output=output,
            stream_callback=stream_callback,
            frames_per_buffer=AUDIO_CHUNKSIZE,
        )

    def get_default_device(self) -> int:
        info: dict[str, Any] = self.p.get_host_api_info_by_index(0)
        device_id = info.get("defaultInputDevice")
        if device_id is None:
            raise ValueError("No default input device found")
        return int(device_id)

    def get_audio_devices(self) -> list[list[int | str]]:
        info: dict[str, Any] = self.p.get_host_api_info_by_index(0)
        device_count = info.get("deviceCount")
        if device_count is None:
            raise ValueError("No device count found")
        device_info: list[dict[str, Any]] = [
            self.p.get_device_info_by_host_api_device_index(0, i) for i in range(0, device_count)
        ]

        return [
            [
                d["index"],
                f"{d['name']} (Inputs: {d['maxInputChannels']}, Outputs: {d['maxOutputChannels']})",
            ]
            for d in device_info
        ]


def resolve_device(device_spec: int | str | None) -> int | None:
    """Resolve device specification to device index.

    Supports:
    - None: Use system default device
    - int: Use device by index (backward compatible)
    - str (numeric): Try as index first, then name if invalid
    - str (non-numeric): Match by case-insensitive substring

    Args:
        device_spec: Device index, name substring, or None

    Returns:
        Device index or None for default device

    Raises:
        ValueError: If no devices match or multiple devices match
        ValueError: If device index is out of range

    Examples:
        >>> resolve_device(None)  # Use default
        None
        >>> resolve_device(4)  # Use device 4
        4
        >>> resolve_device("USB")  # Match device with "USB" in name
        4
        >>> resolve_device("usb")  # Case-insensitive
        4
    """
    if device_spec is None:
        return None

    device = get_device()
    info: dict[str, Any] = device.p.get_host_api_info_by_index(0)
    device_count: int = info.get("deviceCount", 0)

    # If it's already an int, validate and return
    if isinstance(device_spec, int):
        if device_spec < 0 or device_spec >= device_count:
            raise ValueError(
                f"Device index {device_spec} is out of range. Available devices: 0-{device_count-1}.\n"
                "Use 'supertape devices' to list available devices."
            )
        return device_spec

    # It's a string - try parsing as int first
    try:
        device_index = int(device_spec)
        # If it parses as int, try to use it as device index
        if 0 <= device_index < device_count:
            return device_index
        # If out of range, fall through to name matching
    except ValueError:
        # Not a valid integer, continue to name matching
        pass

    # Do case-insensitive substring matching on device names
    device_spec_lower = device_spec.lower()
    matches: list[tuple[int, str]] = []

    for i in range(device_count):
        device_info: dict[str, Any] = device.p.get_device_info_by_host_api_device_index(0, i)
        device_name: str = device_info["name"]

        if device_spec_lower in device_name.lower():
            matches.append((i, device_name))

    if len(matches) == 0:
        raise ValueError(
            f"No device found matching '{device_spec}'.\n"
            "Use 'supertape devices' to list available devices."
        )
    elif len(matches) > 1:
        device_list = "\n".join([f"  - Device {idx}: {name}" for idx, name in matches])
        raise ValueError(f"Multiple devices match '{device_spec}':\n{device_list}\nPlease be more specific.")

    return matches[0][0]


# Suppress verbose ALSA/JACK errors during PyAudio singleton initialization
_device: AudioDevice = AudioDevice()


def get_device() -> AudioDevice:
    return _device
