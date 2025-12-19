from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


Signature = Tuple[str, ...]


@dataclass(frozen=True)
class Candidate:
    ea: int
    score: float


def _has_ida() -> bool:
    try:
        import idc  # noqa: F401

        return True
    except Exception:
        return False


class IdaSignatureBackend:
    """
    Minimal interface so the main updater can work either:
    - inside IDA (direct API), or
    - via a remote bridge (e.g. ida-domain), implemented later.
    """

    def get_imagebase(self) -> int:  # pragma: no cover - interface
        raise NotImplementedError

    def get_function_start(self, ea: int) -> Optional[int]:  # pragma: no cover - interface
        raise NotImplementedError

    def iter_function_starts_in_text(self) -> Iterable[int]:  # pragma: no cover - interface
        raise NotImplementedError

    def signature_at(self, func_start_ea: int, insn_count: int) -> Signature:  # pragma: no cover
        raise NotImplementedError

    def iter_insn_eas(self, start_ea: int, insn_count: int) -> List[int]:  # pragma: no cover
        raise NotImplementedError

    def get_operand_value(self, ea: int, op_index: int) -> int:  # pragma: no cover
        raise NotImplementedError

    def get_insn_mnem(self, ea: int) -> str:  # pragma: no cover
        raise NotImplementedError


class IdaLocalBackend(IdaSignatureBackend):
    def __init__(self) -> None:
        if not _has_ida():
            raise RuntimeError("IdaLocalBackend must run inside IDA (idc/idaapi unavailable).")

        import idaapi
        import idautils
        import ida_ua
        import idc

        self._idaapi = idaapi
        self._idautils = idautils
        self._ida_ua = ida_ua
        self._idc = idc

    def get_imagebase(self) -> int:
        return int(self._idaapi.get_imagebase())

    def get_function_start(self, ea: int) -> Optional[int]:
        f = self._idaapi.get_func(ea)
        return int(f.start_ea) if f else None

    def iter_function_starts_in_text(self) -> Iterable[int]:
        # Prefer the ".text" segment if present, else fall back to all functions.
        text_seg = self._idaapi.get_segm_by_name(".text")
        if text_seg:
            start = int(text_seg.start_ea)
            end = int(text_seg.end_ea)
            for ea in self._idautils.Functions(start, end):
                yield int(ea)
            return

        for ea in self._idautils.Functions():
            yield int(ea)

    def signature_at(self, func_start_ea: int, insn_count: int) -> Signature:
        insn = self._ida_ua.insn_t()
        ea = int(func_start_ea)
        tokens: List[str] = []

        for _ in range(insn_count):
            size = self._ida_ua.decode_insn(insn, ea)
            if size <= 0:
                break
            mnem = self._idc.print_insn_mnem(ea)
            op_kinds: List[str] = []
            for op in insn.ops:
                if op.type == self._ida_ua.o_void:
                    break
                # We intentionally ignore concrete values; only keep "shape".
                if op.type == self._ida_ua.o_reg:
                    op_kinds.append("reg")
                elif op.type == self._ida_ua.o_imm:
                    op_kinds.append("imm")
                elif op.type == self._ida_ua.o_mem:
                    op_kinds.append("mem")
                elif op.type == self._ida_ua.o_phrase:
                    op_kinds.append("phrase")
                elif op.type == self._ida_ua.o_displ:
                    op_kinds.append("displ")
                elif op.type == self._ida_ua.o_near:
                    op_kinds.append("near")
                elif op.type == self._ida_ua.o_far:
                    op_kinds.append("far")
                else:
                    op_kinds.append(f"op{int(op.type)}")
            tokens.append(mnem + ":" + ",".join(op_kinds))
            ea += int(size)

        return tuple(tokens)

    def iter_insn_eas(self, start_ea: int, insn_count: int) -> List[int]:
        insn = self._ida_ua.insn_t()
        ea = int(start_ea)
        out: List[int] = []
        for _ in range(insn_count):
            size = self._ida_ua.decode_insn(insn, ea)
            if size <= 0:
                break
            out.append(int(ea))
            ea += int(size)
        return out

    def get_operand_value(self, ea: int, op_index: int) -> int:
        return int(self._idc.get_operand_value(int(ea), int(op_index)))

    def get_insn_mnem(self, ea: int) -> str:
        return str(self._idc.print_insn_mnem(int(ea)))


def signature_similarity(a: Signature, b: Signature) -> float:
    """
    Simple similarity: prefix match ratio. Good enough as a cheap tie-breaker.
    """
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    same = 0
    for i in range(n):
        if a[i] != b[i]:
            break
        same += 1
    return same / max(len(a), len(b))
