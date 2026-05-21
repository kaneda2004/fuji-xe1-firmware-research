#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import warnings

import pyghidra


DEFAULT_PROJECT_DIR = "pyghidra_xe1"
DEFAULT_PROJECT_NAME = "xe1"
DEFAULT_PROGRAM_NAME = "FWUP0001_ARMv7"
DEFAULT_BOOTSTRAP = [
    0x48C594,
    0x48C6BC,
    0x48C774,
    0x48C7CC,
    0x48C948,
    0x48CA24,
    0x48CCD0,
    0x48CF28,
    0x48D058,
    0x48D0F0,
]


def parse_addr(text: str) -> int:
    return int(text, 0)


def project_root(project_dir: str) -> str:
    return os.path.abspath(project_dir)


def addr(program, value: int):
    return program.getAddressFactory().getDefaultAddressSpace().getAddress(value)


def ensure_function(program, flat, start: int):
    from ghidra.app.cmd.disassemble import DisassembleCommand

    a = addr(program, start)
    listing = program.getListing()
    inst = listing.getInstructionAt(a)
    if inst is None:
        DisassembleCommand(a, None, True).applyTo(program)
    funcman = program.getFunctionManager()
    fn = funcman.getFunctionContaining(a)
    if fn is None:
        flat.createFunction(a, None)


def listing_lines(program, start: int, count: int) -> list[str]:
    listing = program.getListing()
    inst = listing.getInstructionAt(addr(program, start))
    if inst is None:
        inst = listing.getInstructionContaining(addr(program, start))
    lines: list[str] = []
    while inst is not None and count > 0:
        lines.append(f"{inst.getAddress()}: {inst}")
        inst = inst.getNext()
        count -= 1
    return lines


def callers_of(program, target: int) -> list[str]:
    refman = program.getReferenceManager()
    funcman = program.getFunctionManager()
    out: list[str] = []
    for ref in refman.getReferencesTo(addr(program, target)):
        from_addr = ref.getFromAddress()
        fn = funcman.getFunctionContaining(from_addr)
        fn_name = fn.getName() if fn else "<no function>"
        out.append(f"{from_addr} {ref.getReferenceType()} {fn_name}")
    return out


def callees_of(program, start: int) -> list[str]:
    listing = program.getListing()
    funcman = program.getFunctionManager()
    fn = funcman.getFunctionContaining(addr(program, start))
    if fn is None:
        return []
    body = fn.getBody()
    out: list[str] = []
    inst = listing.getInstructions(body, True)
    while inst.hasNext():
        ins = inst.next()
        flow = ins.getFlows()
        if flow:
            for target in flow:
                callee = funcman.getFunctionAt(target)
                callee_name = callee.getName() if callee else "<non-function>"
                out.append(f"{ins.getAddress()} -> {target} {callee_name}")
    return out


def decompile(program, start: int, timeout: int) -> str:
    from ghidra.app.decompiler import DecompInterface

    funcman = program.getFunctionManager()
    fn = funcman.getFunctionContaining(addr(program, start))
    if fn is None:
        raise SystemExit(f"no function containing {start:#x}")
    iface = DecompInterface()
    iface.openProgram(program)
    result = iface.decompileFunction(fn, timeout, None)
    if not result.decompileCompleted():
        raise SystemExit(f"decompile failed: {result.getErrorMessage()}")
    return str(result.getDecompiledFunction().getC())


def strings_near(program, start: int, limit: int) -> list[str]:
    listing = program.getListing()
    funcman = program.getFunctionManager()
    fn = funcman.getFunctionContaining(addr(program, start))
    if fn is None:
        return []
    body = fn.getBody()
    refman = program.getReferenceManager()
    out: list[str] = []
    seen: set[str] = set()
    inst_iter = listing.getInstructions(body, True)
    while inst_iter.hasNext():
        ins = inst_iter.next()
        for ref in refman.getReferencesFrom(ins.getAddress()):
            to_addr = ref.getToAddress()
            data = listing.getDefinedDataAt(to_addr)
            if data is None:
                continue
            value = data.getValue()
            if not isinstance(value, str):
                continue
            line = f"{to_addr}: {value}"
            if line in seen:
                continue
            seen.add(line)
            out.append(line)
            if len(out) >= limit:
                return out
    return out


def data_refs(program, target: int) -> list[str]:
    refman = program.getReferenceManager()
    out: list[str] = []
    for ref in refman.getReferencesTo(addr(program, target)):
        out.append(f"{ref.getFromAddress()} {ref.getReferenceType()}")
    return out


def functions_in_range(program, start: int, end: int) -> list[str]:
    funcman = program.getFunctionManager()
    out: list[str] = []
    fn_iter = funcman.getFunctions(addr(program, start), True)
    while fn_iter.hasNext():
        fn = fn_iter.next()
        entry = fn.getEntryPoint().getOffset()
        if entry >= end:
            break
        out.append(f"{fn.getEntryPoint()} {fn.getName()}")
    return out


def batch_decompile(program, addrs: list[int], timeout: int) -> str:
    parts: list[str] = []
    for start in addrs:
        parts.append(f"== {start:#010x} ==")
        parts.append(decompile(program, start, timeout).rstrip())
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def batch_disasm(program, addrs: list[int], count: int) -> str:
    parts: list[str] = []
    for start in addrs:
        parts.append(f"== {start:#010x} ==")
        parts.extend(listing_lines(program, start, count))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Query a Ghidra project headlessly")
    parser.add_argument("--project-dir", default=DEFAULT_PROJECT_DIR)
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    parser.add_argument("--program-name", default=DEFAULT_PROGRAM_NAME)
    parser.add_argument(
        "--bootstrap",
        action="append",
        type=parse_addr,
        default=[],
        help="extra function entry point to disassemble before querying",
    )
    parser.add_argument(
        "--no-default-bootstrap",
        action="store_true",
        help="skip the built-in bootstrap address list",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_decompile = sub.add_parser("decompile")
    p_decompile.add_argument("addr", type=parse_addr)
    p_decompile.add_argument("--timeout", type=int, default=60)

    p_disasm = sub.add_parser("disasm")
    p_disasm.add_argument("addr", type=parse_addr)
    p_disasm.add_argument("--count", type=int, default=24)

    p_callers = sub.add_parser("callers")
    p_callers.add_argument("addr", type=parse_addr)

    p_callees = sub.add_parser("callees")
    p_callees.add_argument("addr", type=parse_addr)

    p_strings = sub.add_parser("strings")
    p_strings.add_argument("addr", type=parse_addr)
    p_strings.add_argument("--limit", type=int, default=20)

    p_refs = sub.add_parser("refs")
    p_refs.add_argument("addr", type=parse_addr)

    p_batch_decompile = sub.add_parser("batch-decompile")
    p_batch_decompile.add_argument("addrs", nargs="+", type=parse_addr)
    p_batch_decompile.add_argument("--timeout", type=int, default=60)

    p_batch_disasm = sub.add_parser("batch-disasm")
    p_batch_disasm.add_argument("addrs", nargs="+", type=parse_addr)
    p_batch_disasm.add_argument("--count", type=int, default=24)

    p_funcs = sub.add_parser("functions")
    p_funcs.add_argument("start", type=parse_addr)
    p_funcs.add_argument("end", type=parse_addr)

    args = parser.parse_args()

    install_dir = os.environ.get("GHIDRA_INSTALL_DIR")
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    pyghidra.start(install_dir=Path(install_dir) if install_dir else None)

    with pyghidra.open_program(
        None,
        project_location=project_root(args.project_dir),
        project_name=args.project_name,
        analyze=False,
        program_name=args.program_name,
        nested_project_location=False,
    ) as flat:
        program = flat.getCurrentProgram()
        tx = program.startTransaction("bootstrap")
        try:
            base_bootstrap = [] if args.no_default_bootstrap else DEFAULT_BOOTSTRAP
            bootstrap = list(dict.fromkeys(base_bootstrap + args.bootstrap))
            if hasattr(args, "addr") and args.cmd != "refs":
                bootstrap.append(args.addr)
            if hasattr(args, "addrs"):
                bootstrap.extend(args.addrs)
            for entry in bootstrap:
                ensure_function(program, flat, entry)
        finally:
            program.endTransaction(tx, True)
        if args.cmd == "decompile":
            print(decompile(program, args.addr, args.timeout))
        elif args.cmd == "disasm":
            print("\n".join(listing_lines(program, args.addr, args.count)))
        elif args.cmd == "callers":
            print("\n".join(callers_of(program, args.addr)))
        elif args.cmd == "callees":
            print("\n".join(callees_of(program, args.addr)))
        elif args.cmd == "strings":
            print("\n".join(strings_near(program, args.addr, args.limit)))
        elif args.cmd == "refs":
            print("\n".join(data_refs(program, args.addr)))
        elif args.cmd == "batch-decompile":
            print(batch_decompile(program, args.addrs, args.timeout))
        elif args.cmd == "batch-disasm":
            print(batch_disasm(program, args.addrs, args.count))
        elif args.cmd == "functions":
            print("\n".join(functions_in_range(program, args.start, args.end)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
