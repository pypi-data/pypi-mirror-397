"""Timers used for performance testing malcarve."""

from enum import IntEnum
from time import perf_counter_ns


class TimerVerbosityEnum(IntEnum):
    """Flags for what information to track as part of timing."""

    NONE: int = 0
    TIME: int = 1
    TOTAL_COUNT: int = 2
    AVE_MIN_MAX: int = 3


class Timer:
    """Timer for timing malcarve functionality."""

    name: str
    verbosity: TimerVerbosityEnum

    start_ns: int = 0
    finish_ns: int = 0
    total_ms: int = 0
    min_ms: int = 0
    max_ms: int = 0
    count: int = 0

    def __init__(self, name: str, verbosity: TimerVerbosityEnum):
        self.name = name
        self.verbosity = verbosity


def timerStart(timer: Timer):
    """Start the timer."""
    timer.start_ns = perf_counter_ns()


def timerEnd(timer: Timer):
    """End the timer and print stats."""
    if timer.start_ns == 0:
        raise Exception("Timer ended before started.")
    timer.finish_ns = perf_counter_ns()
    time_ms: int = (timer.finish_ns - timer.start_ns) / 1000 / 1000
    timer.total_ms += time_ms
    timer.count += 1
    if time_ms < timer.min_ms or timer.min_ms == 0:
        timer.min_ms = time_ms
    if time_ms > timer.max_ms:
        timer.max_ms = time_ms
    if timer.verbosity >= TimerVerbosityEnum.TIME:
        print(f"{timer.name}:\n    time: {time_ms:.2f}ms")
    if timer.verbosity >= TimerVerbosityEnum.TOTAL_COUNT:
        print(f"    total: {timer.total_ms:.2f}ms\n    count: {timer.count}")
    if timer.verbosity >= TimerVerbosityEnum.AVE_MIN_MAX:
        print(
            f"    min: {timer.min_ms:.2f}ms\n    max: {timer.max_ms:.2f}ms\n"
            + f"    average: {timer.total_ms / timer.count:.2f}ms"
        )


def timerStats(timer: Timer, total: int):
    """Print the current stats of a timer."""
    print(f"{timer.name}:\n    total: {timer.total_ms:.2f}ms\n    count: {timer.count}")
    if timer.count > 0:
        print(
            f"    min: {timer.min_ms:.2f}ms\n    max: {timer.max_ms:.2f}ms\n"
            + f"    average: {timer.total_ms / timer.count:.2f}ms"
        )
        print(f"    percent: {timer.total_ms / total * 100:.2f}%")


class Timers:
    """Bundle of timers for monitoring all the different functionality of malcarve."""

    total = Timer("total malcarve", TimerVerbosityEnum.TIME)

    unobfuscated_find = Timer("unobfuscated find", TimerVerbosityEnum.NONE)
    xor_find = Timer("xor find", TimerVerbosityEnum.NONE)
    rolling_xor_find = Timer("rolling xor find", TimerVerbosityEnum.NONE)
    rol_find = Timer("rol find", TimerVerbosityEnum.NONE)
    add_find = Timer("add find", TimerVerbosityEnum.NONE)

    xor_check = Timer("xor checks", TimerVerbosityEnum.NONE)
    rolling_xor_check = Timer("rolling xor checks", TimerVerbosityEnum.NONE)
    rol_check = Timer("rol checks", TimerVerbosityEnum.NONE)
    add_check = Timer("add checks", TimerVerbosityEnum.NONE)

    charcode_find = Timer("charcode find", TimerVerbosityEnum.NONE)
    hex_find = Timer("hex find", TimerVerbosityEnum.NONE)
    base64_find = Timer("base64 find", TimerVerbosityEnum.NONE)
    deflate_find = Timer("deflate find", TimerVerbosityEnum.NONE)
    reverse_find = Timer("reverse find", TimerVerbosityEnum.NONE)


timers = Timers()
