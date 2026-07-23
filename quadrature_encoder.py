"""
quadrature_encoder.py
CircuitPython port of the Raspberry Pi pico-examples PIO quadrature encoder
(pico-examples/pio/quadrature_encoder/quadrature_encoder.pio +
quadrature_encoder.c, Copyright (c) 2023 Raspberry Pi (Trading) Ltd,
SPDX-License-Identifier: BSD-3-Clause).

The PIO program continuously samples the A/B phase pins and maintains a
running 32-bit step count entirely in hardware -- zero CPU load, and it can
track step rates up to sysclk / 10 (~12.5 Msteps/s at 125 MHz). Your code
just asks for the current count whenever it wants it.

Wiring: connect encoder phase A to `pin_a`, phase B to the *next* GPIO
(pin_a.number + 1). This is a hardware requirement of the PIO program
(IN PINS reads two consecutive pins in one shot) -- it is not adjustable
in software.

Requires: adafruit_pioasm, rp2pio 
-- adafruit_pioasm is a bundle library, rp2pio is a built-in module
"""

import array
import adafruit_pioasm
import rp2pio

# ---------------------------------------------------------------------------
# PIO assembly -- direct translation of quadrature_encoder.pio.
#
# Unlike the original .pio file, pin config (in_pin_count, shift direction,
# pull-ups, FIFO join) is NOT expressed here via .in / .fifo directives,
# because the original C init function set those purely in C, not in the
# .pio file itself. We replicate that split: labels/wrap/origin come from
# assembling this text; pin electrical config is passed explicitly to
# rp2pio.StateMachine() in QuadratureEncoder.__init__ below.
# ---------------------------------------------------------------------------
_PROGRAM = """
.program quadrature_encoder
.origin 0

; 00 state
    jmp update      ; read 00
    jmp decrement   ; read 01
    jmp increment   ; read 10
    jmp update      ; read 11

; 01 state
    jmp increment   ; read 00
    jmp update      ; read 01
    jmp update      ; read 10
    jmp decrement   ; read 11

; 10 state
    jmp decrement   ; read 00
    jmp update      ; read 01
    jmp update      ; read 10
    jmp increment   ; read 11

; 11 state (last two entries implemented in place, reused as jump targets)
    jmp update      ; read 00
    jmp increment   ; read 01
decrement:
    jmp y--, update ; read 10  (pure "decrement Y", target must be next addr)

.wrap_target
update:
    mov isr, y      ; move 
    push noblock    ; push the ISR into the FIFO, even if FIFO is full

sample_pins:
    out isr, 2      ; shift 2 bits from OSR into ISR; the 2 least significant bits of the OSR contain the previous pin value
    in pins, 2      ; shift value of 2 pins into ISR
    mov osr, isr    ; move (copy) the value from the ISR to the OSR so that next time we have the previous pin value
    mov pc, isr     ; update the program counter to the value determined by the combination of prev and current pin values

increment:          ; no native increment instruction in PIO, use 2s complement. This is the longest branch (10 instructions)
    mov y, ~y
    jmp y--, increment_cont
increment_cont:
    mov y, ~y
.wrap
"""

# compile PIO using adafruit_pioasm
_program = adafruit_pioasm.Program(_PROGRAM)


class QuadratureEncoder:
    """Hardware-tracked quadrature encoder position using RP2040/RP2350 PIO.

    :param pin_a: the phase-A pin. Phase B must be wired to the next
        consecutive GPIO (pin_a's GPIO number + 1).
    :param max_step_rate: if > 0, the state machine clock is slowed down to
        save power, sized so the program can still reliably track up to this
        many steps/sec (worst case is 10 SM cycles per step). Pass 0 (the
        default) to run the state machine at full speed.
    """

    def __init__(self, pin_a, *, max_step_rate=0):
        # if max sample frequency is known, pass to initializer to configure clock to reduce power consumption
        frequency = 0 if max_step_rate <= 0 else 10 * max_step_rate 

        self._sm = rp2pio.StateMachine(
            _program.assembled,
            frequency=frequency,
            first_in_pin=pin_a,
            in_pin_count=2,
            pull_in_pin_up=0b11,    # pull up both phase A and phase B pins
            in_shift_right=False,   # shift left: matches sm_config_set_in_shift(..., false, ...)
            auto_push=False,
            fifo_type="txrx",       # force split tx/rx buffer to keep rx buffer short
                                    # this minimizes how many stale entries we need to read through
            **_program.pio_kwargs,  # wrap_target / wrap / offset=0 from .origin 0
        )
        self._buf = array.array("l", [0])
        self._last_value = 0

    def count(self):
        """Return the current absolute step count (wraps as a signed 32-bit
        value, same two's-complement behavior as the original C code)."""
        # If the FIFO has N entries queued, read N+1 words to drain the
        # stale ones and guarantee the last word read is a fresh sample.
        n = self._sm.in_waiting + 1
        val = self._last_value
        for _ in range(n):
            self._sm.readinto(self._buf)
            val = self._buf[0]
        self._last_value = val
        return val

    def delta(self):
        """Return the change in count since the last call to count() or
        delta() (convenience wrapper -- mirrors the pico-examples main loop
        pattern of tracking old_value/new_value yourself)."""
        previous = self._last_value
        new_value = self.count()
        return new_value - previous

    def deinit(self):
        """Release the state machine."""
        self._sm.deinit()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.deinit()
