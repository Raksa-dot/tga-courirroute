"""
Modul `automata.py`
Implementasi Deterministic Finite Automaton (DFA / FSM) 5-tupel M = (Q, Sigma, delta, q0, F)
untuk memvalidasi transisi status pengiriman paket oleh kurir.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass
class TransitionLog:
    """Catatan hasil eksekusi satu transisi state pada FSM."""
    previous_state: str
    event: str
    next_state: str
    is_valid: bool
    is_accepting: bool
    message: str


class DeliveryStatusFSM:
    """
    Deterministic Finite Automaton (DFA) Status Pengiriman Paket:
    - Q     : {'IDLE', 'ASSIGNED', 'EN_ROUTE', 'DELIVERED', 'FAILED'}
    - Sigma : {'terima_pesanan', 'mulai_jalan', 'paket_diterima', 'gagal_kirim', 'jadwalkan_ulang'}
    - q0    : 'IDLE'
    - F     : {'DELIVERED'}
    """

    STATES: Set[str] = {"IDLE", "ASSIGNED", "EN_ROUTE", "DELIVERED", "FAILED"}
    ALPHABET: Set[str] = {
        "terima_pesanan",
        "mulai_jalan",
        "paket_diterima",
        "gagal_kirim",
        "jadwalkan_ulang",
    }
    INITIAL_STATE: str = "IDLE"
    ACCEPTING_STATES: Set[str] = {"DELIVERED"}

    TRANSITION_TABLE: Dict[Tuple[str, str], str] = {
        ("IDLE", "terima_pesanan"):     "ASSIGNED",
        ("ASSIGNED", "mulai_jalan"):    "EN_ROUTE",
        ("EN_ROUTE", "paket_diterima"): "DELIVERED",
        ("EN_ROUTE", "gagal_kirim"):    "FAILED",
        ("FAILED", "jadwalkan_ulang"):  "ASSIGNED",
    }

    def __init__(self) -> None:
        self.current_state: str = self.INITIAL_STATE
        self.history: List[TransitionLog] = []

    def reset(self) -> None:
        """Mengembalikan state mesin ke state awal (q0 = IDLE)."""
        self.current_state = self.INITIAL_STATE
        self.history.clear()

    def trigger(self, event: str) -> TransitionLog:
        """Mengeksekusi fungsi transisi delta(current_state, event)."""
        key = (self.current_state, event)
        if key not in self.TRANSITION_TABLE:
            log = TransitionLog(
                previous_state=self.current_state,
                event=event,
                next_state=self.current_state,
                is_valid=False,
                is_accepting=self.current_state in self.ACCEPTING_STATES,
                message=(
                    f"[DITOLAK] Transisi δ({self.current_state}, {event}) tidak terdefinisi. "
                    f"State tetap di '{self.current_state}'."
                ),
            )
            self.history.append(log)
            return log

        old_state = self.current_state
        self.current_state = self.TRANSITION_TABLE[key]
        accepted = self.current_state in self.ACCEPTING_STATES
        suffix = " [FINAL STATE / ACCEPTED]" if accepted else ""

        log = TransitionLog(
            previous_state=old_state,
            event=event,
            next_state=self.current_state,
            is_valid=True,
            is_accepting=accepted,
            message=f"[VALID] δ({old_state}, {event}) -> {self.current_state}{suffix}",
        )
        self.history.append(log)
        return log
