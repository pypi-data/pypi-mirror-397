import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

from supertape.core.audio.duration import calculate_duration, format_duration
from supertape.core.audio.progress import BasePlaybackObserver, RichProgressObserver
from supertape.core.basic.minification import minify_basic
from supertape.core.basic.preprocess import preprocess_basic
from supertape.core.file.api import (
    FILE_TYPE_NAMES,
    TapeFile,
)
from supertape.core.file.container import K7Container
from supertape.core.file.load import container_load
from supertape.core.file.operations import (
    compile_assembly_source,
    compile_basic_source,
    compile_c_source,
    read_source_file,
)
from supertape.core.file.play import play_file
from supertape.core.ui.constants import FILE_TYPE_COLORS

# Console for Rich output
console = Console()


def play_tape(device: int | None, tape_file: TapeFile) -> None:
    # Calculate and display duration
    duration = calculate_duration(tape_file)
    duration_str = format_duration(duration)
    print(f"Estimated duration: {duration_str}")

    obs = BasePlaybackObserver(poll_interval=0.5, post_delay=0.5)
    play_file(device=device, file=tape_file, observer=obs)
    obs.wait_for_completion()


def play_k7_file(device: int | None, k7_path: str) -> None:
    """Play a K7 file, handling multi-file containers with interactive prompts.

    Args:
        device: Audio device index (None for default)
        k7_path: Path to the K7 file
    """
    # Load the K7 container
    container: K7Container = container_load(k7_path)

    # ASCII art for K7 cassette tape
    cassette_art = r"""
    ┌───────────────────────────────────────┐
    │   ╔═══════════════════════════════╗   │
    │   ║      ▄▄▄           ▄▄▄        ║   │
    │   ║     █   █  <<<<<  █   █       ║   │
    │   ║      ▀▀▀           ▀▀▀        ║   │
    │   ╚═══════════════════════════════╝   │
    └───────────────────────────────────────┘
    """

    # Display cassette banner
    console.print()
    banner = Panel(
        Text(cassette_art, style="red bold", justify="center"),
        title=f"[bold white]K7 Container: {Path(k7_path).name}[/bold white]",
        subtitle=f"[white]{len(container)} file(s)[/white]",
        border_style="bright_black",
        padding=(0, 2),
    )
    console.print(banner)

    # Create a table showing all files in the container
    table = Table(show_header=True, header_style="bold bright_white", border_style="bright_black")
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Filename", style="bright_white", width=20)
    table.add_column("Type", width=10)
    table.add_column("Status", width=15)

    # Add all files to the table
    for i, tape_file in enumerate(container):
        file_type = FILE_TYPE_NAMES.get(tape_file.ftype, f"0x{tape_file.ftype:02X}")
        file_type_color = FILE_TYPE_COLORS.get(tape_file.ftype, "white")
        table.add_row(
            str(i + 1),
            tape_file.fname,
            f"[{file_type_color}]{file_type}[/{file_type_color}]",
            "[dim]Queued[/dim]",
        )

    console.print(table)
    console.print()

    # Play each file with pause in between
    for i, tape_file in enumerate(container):
        file_type = FILE_TYPE_NAMES.get(tape_file.ftype, f"0x{tape_file.ftype:02X}")
        file_type_color = FILE_TYPE_COLORS.get(tape_file.ftype, "white")

        # Calculate and display duration
        duration = calculate_duration(tape_file)
        duration_str = format_duration(duration)

        # Display current file info
        console.print(
            f"[bold bright_white]▶ Playing [{i+1}/{len(container)}]:[/bold bright_white] "
            f"[bold]{tape_file.fname}[/bold] "
            f"([{file_type_color}]{file_type}[/{file_type_color}]) "
            f"[dim]│ {duration_str}[/dim]"
        )

        # Play with animated progress bar
        with Progress() as progress:
            task_id = progress.add_task("[magenta]🎵 Transmitting audio...", total=100)
            observer = RichProgressObserver(progress, task_id)
            play_file(device=device, file=tape_file, observer=observer)
            observer.wait_for_completion()

        console.print(f"[bright_green]✓[/bright_green] Playback complete: {tape_file.fname}")

        # Check if there are more files
        if i < len(container) - 1:
            console.print()

            # Ask user if they want to continue
            while True:
                try:
                    response = (
                        console.input(
                            f"[bright_yellow]→[/bright_yellow] Continue with next file [{i+2}/{len(container)}]? (Y/n): "
                        )
                        .strip()
                        .lower()
                    )

                    if response in ["y", "yes", ""]:
                        console.print("[dim]Continuing...[/dim]")
                        console.print()
                        break
                    elif response in ["n", "no"]:
                        console.print(
                            f"[bright_yellow]■[/bright_yellow] Stopped after file {i+1}/{len(container)}."
                        )
                        return
                    else:
                        console.print("[red]Please enter 'y' or 'n'.[/red]")
                except KeyboardInterrupt:
                    console.print("\n[bright_yellow]■[/bright_yellow] Playback interrupted by user.")
                    return

    # All files completed
    console.print()
    console.print(
        f"[bold bright_green]✓ All files completed![/bold bright_green] ({len(container)}/{len(container)})"
    )
    console.print()


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Play a local file to the audio interface."
    )
    parser.add_argument("--device", help="Select a device by index or name substring.")
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile .asm files to MACHINE code instead of ASMSRC",
    )
    parser.add_argument(
        "--cpu",
        choices=["6800", "6803", "6303"],
        default="6803",
        help="Target CPU for C compilation (default: 6803)",
    )
    parser.add_argument("file", type=str)
    args: argparse.Namespace = parser.parse_args()

    # Use config default device if --device not specified
    if args.device is None:
        from supertape.core.config import get_config

        device = get_config().audio.default_device
    else:
        device = args.device

    # Resolve device spec to actual device index
    from supertape.core.audio.device import resolve_device

    try:
        device_index = resolve_device(device)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    file_ext = args.file.lower()

    if file_ext.endswith(".k7"):
        # K7 file - handle multi-file containers
        play_k7_file(device=device_index, k7_path=args.file)
    elif file_ext.endswith(".bas"):
        basic_code: str = read_source_file(args.file)
        basic_code = preprocess_basic(basic_code)
        basic_code = minify_basic(basic_code)
        tape_file = compile_basic_source(args.file, basic_code)
        play_tape(device=device_index, tape_file=tape_file)
    elif file_ext.endswith(".asm"):
        asm_code: str = read_source_file(args.file)
        # Compile to MACHINE code if --compile flag, otherwise ASMSRC
        tape_file = compile_assembly_source(args.file, asm_code, to_machine=args.compile)
        play_tape(device=device_index, tape_file=tape_file)
    elif file_ext.endswith(".c"):
        # C source file - compile to MACHINE code
        tape_file, asm_path = compile_c_source(args.file, args.cpu)
        print("Creating MACHINE tape file...")
        play_tape(device=device_index, tape_file=tape_file)
    else:
        print(f"ERROR: Unsupported file type: {args.file}")
        print("Supported types: .bas, .asm, .c, .k7")
        return


if __name__ == "__main__":
    main()
