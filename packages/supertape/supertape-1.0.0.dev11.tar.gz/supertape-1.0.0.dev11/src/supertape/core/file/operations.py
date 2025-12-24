"""High-level file operations for tape file creation and manipulation.

This module provides reusable operations for reading source files and compiling
them to tape file format. These functions abstract common operations that were
previously duplicated across CLI commands.
"""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from supertape.core.asm.assembler import M6803Assembler
from supertape.core.asm.encoder import create_machine_file
from supertape.core.assembly.encode import create_assembly_file
from supertape.core.basic.encode import BasicEncoder, BasicFileCompiler
from supertape.core.c.compiler import compile_c_to_assembly
from supertape.core.c.errors import CCompilerError, FCCNotFoundError
from supertape.core.file.api import TapeFile


def read_source_file(file_path: str | Path) -> str:
    """Read source file contents.

    Args:
        file_path: Path to the source file

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    f: TextIO
    with open(file_path) as f:
        source: str = f.read()

    return source


def compile_basic_source(file_name: str, source: str) -> TapeFile:
    """Compile BASIC source to tape file.

    Args:
        file_name: Name for the tape file (8 chars max)
        source: BASIC source code

    Returns:
        TapeFile containing compiled BASIC program
    """
    file_compiler: BasicFileCompiler = BasicFileCompiler()
    encoder: BasicEncoder = BasicEncoder()

    instructions = [encoder.encode(line) for line in source.splitlines()]
    outfile: TapeFile = file_compiler.compile_instructions(file_name, instructions)

    return outfile


def compile_assembly_source(file_name: str, source: str, to_machine: bool = False) -> TapeFile:
    """Compile assembly source to ASMSRC or MACHINE tape file.

    Args:
        file_name: Name for the tape file (8 chars max)
        source: Assembly source code
        to_machine: If True, compile to MACHINE code; if False, create ASMSRC file

    Returns:
        TapeFile containing assembly (ASMSRC) or machine code (MACHINE)
    """
    if to_machine:
        assembler = M6803Assembler()
        machine_code, load_addr, exec_addr = assembler.assemble(source)
        return create_machine_file(file_name, machine_code, load_addr, exec_addr)
    else:
        return create_assembly_file(file_name, source)


def compile_c_source(
    c_source_path: str | Path, cpu: str = "6803", output_stream: object | None = None
) -> tuple[TapeFile, str]:
    """Compile C source to MACHINE tape file via assembly.

    This function uses the Fuzix-Compiler-Kit (FCC) to compile C source to
    M6803 assembly, then assembles it to machine code.

    Args:
        c_source_path: Path to C source file
        cpu: Target CPU (6800, 6803, or 6303). Default is 6803.
        output_stream: Optional output stream for progress messages

    Returns:
        Tuple of (TapeFile containing compiled machine code, path to generated assembly)

    Raises:
        FCCNotFoundError: If FCC compiler not found in PATH or /opt/fcc/bin
        CCompilerError: If C compilation fails
        FileNotFoundError: If source file doesn't exist

    Example:
        >>> tape_file, asm_path = compile_c_source("program.c")
        >>> print(f"Generated assembly: {asm_path}")
    """
    c_path = Path(c_source_path)
    asm_path = c_path.with_suffix(".asm")

    # Helper for output
    def print_msg(msg: str) -> None:
        if output_stream and hasattr(output_stream, "print"):
            output_stream.print(msg)
        else:
            print(msg)

    print_msg(f"Compiling C source: {c_source_path}")

    # Compile C to assembly
    try:
        compile_c_to_assembly(c_path, asm_path, cpu)
        print_msg(f"Generated assembly: {asm_path}")
    except FCCNotFoundError as e:
        print_msg(f"ERROR: {e}")
        raise
    except CCompilerError as e:
        print_msg(f"ERROR: C compilation failed:\n{e}")
        raise

    # Read generated assembly
    with open(asm_path) as f:
        asm_code = f.read()

    print_msg("Assembling to machine code...")

    # Assemble to machine code
    tape_file = compile_assembly_source(str(c_path.name), asm_code, to_machine=True)

    return tape_file, str(asm_path)
