import argparse

from supertape.core.audio.file_in import FileInput
from supertape.core.audio.modulation import AudioDemodulator
from supertape.core.file.api import ByteListener
from supertape.core.file.bytes import ByteDecoder
from supertape.core.file.load import container_load
from supertape.core.file.save import _serialize_tape_file
from supertape.core.log.dump import dump


class ByteListenerStub(ByteListener):
    def __init__(self) -> None:
        self.values: list[int] = []

    def process_byte(self, value: int) -> None:
        self.values.append(value)

    def process_silence(self) -> None:
        """Process silence event - no-op for stub."""
        pass  # Silence is not accumulated


def dump_bytes(bytes_data: list[int]) -> None:
    """Dump bytes as hex output.

    Args:
        bytes_data: List of byte values to dump
    """
    for line in dump(bytes_data):
        print(line)


def dump_k7_file(filepath: str, index: int | None = None) -> None:
    """Dump k7 file contents.

    Args:
        filepath: Path to .k7 file
        index: Optional file index to dump (None = dump all files)
    """
    container = container_load(filepath)

    if index is not None:
        # Dump specific file by index
        if index < 0 or index >= len(container):
            raise IndexError(f"File index {index} out of range (container has {len(container)} files)")

        tape_file = container[index]
        tape_bytes = _serialize_tape_file(tape_file)
        dump_bytes(list(tape_bytes))
    else:
        # Dump all files with headers
        print(f"K7 Container: {container.format.value} format")
        print(f"Total files: {len(container)}")
        print("=" * 60)
        print()

        for i, tape_file in enumerate(container):
            if i > 0:
                print()  # Blank line between files

            # Show file header
            print("=" * 60)
            print(f"File {i + 1} of {len(container)}: {tape_file.fname}")
            print("=" * 60)
            print()

            # Dump file bytes
            tape_bytes = _serialize_tape_file(tape_file)
            dump_bytes(list(tape_bytes))


def dump_wav_file(filepath: str) -> None:
    """Dump .wav audio file contents.

    Args:
        filepath: Path to .wav file
    """
    byte_accumulator = ByteListenerStub()
    byte_decoder = ByteDecoder([byte_accumulator])
    demodulation = AudioDemodulator([byte_decoder], rate=44100)
    file_in = FileInput(filepath, [demodulation])
    file_in.run()
    dump_bytes(byte_accumulator.values)


def main() -> None:
    """Main entry point for the dump command."""
    parser = argparse.ArgumentParser(description="Dump tape file contents as hex")
    parser.add_argument("file", help="Tape file (.k7) or audio file (.wav) to dump")
    parser.add_argument(
        "--index",
        type=int,
        default=None,
        help="Show specific file by index from multi-file k7 (0-based). If not specified, shows all files.",
    )
    args = parser.parse_args()

    try:
        if args.file.endswith(".k7"):
            dump_k7_file(args.file, index=args.index)
        elif args.file.endswith(".wav"):
            if args.index is not None:
                print("Warning: --index flag is ignored for .wav files")
            dump_wav_file(args.file)
        else:
            raise ValueError(f"Unsupported file format: {args.file}. Expected .k7 or .wav")

    except FileNotFoundError:
        print(f"Error: File not found: {args.file}")
        exit(1)
    except IndexError as e:
        print(f"Error: {e}")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except (OSError, RuntimeError) as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
