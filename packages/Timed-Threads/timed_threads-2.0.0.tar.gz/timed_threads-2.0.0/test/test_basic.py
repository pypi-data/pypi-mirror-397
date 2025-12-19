# -*- coding: utf-8 -*-
import os
import time

from timed_threads import (
    SignalTimeout,
    ThreadingTimeout,
    TimeoutException,
    signal_timeoutable,
    threading_timeoutable,
)

# We run twice the same doctest with two distinct sets of globs
# This one is for testing signals based timeout control
signaling_globs = {"Timeout": SignalTimeout, "timeoutable": signal_timeoutable}

# And this one is for testing threading based timeout control
threading_globs = {"Timeout": ThreadingTimeout, "timeoutable": threading_timeoutable}


handlers = (
    (
        SignalTimeout,
        ThreadingTimeout,
    )
    if os.name == "posix"
    else (ThreadingTimeout,)
)


def aware_wait(duration):
    remaining = duration * 100
    t_start = time.time()
    while remaining > 0:
        time.sleep(0.01)
        if time.time() - t_start > duration:
            return 0
        remaining = remaining - 1
    return 0


def check_nest(t1, t2, duration, HandlerClass):
    try:
        with HandlerClass(t1, swallow_exc=False) as to_ctx_mgr1:
            assert to_ctx_mgr1.state == to_ctx_mgr1.EXECUTING
            with HandlerClass(t2, swallow_exc=False) as to_ctx_mgr2:
                assert to_ctx_mgr2.state == to_ctx_mgr2.EXECUTING
                aware_wait(duration)
                return "success"
    except TimeoutException:
        if HandlerClass.exception_source is to_ctx_mgr1:
            return "outer"
        elif HandlerClass.exception_source is to_ctx_mgr2:
            return "inner"
        else:
            print(HandlerClass.exception_source)
            return "unknown source"


def check_nest_swallow(t1, t2, duration, HandlerClass):
    with HandlerClass(t1) as to_ctx_mgr1:
        assert to_ctx_mgr1.state == to_ctx_mgr1.EXECUTING
        with HandlerClass(t2) as to_ctx_mgr2:
            assert to_ctx_mgr2.state == to_ctx_mgr2.EXECUTING
            aware_wait(duration)
            return "success"
        return "inner"
    return "outer"


def test_nested_long_inner():
    for handler in handlers:
        assert check_nest(1.0, 10.0, 5.0, handler) == "outer"
        assert check_nest_swallow(1.0, 10.0, 5.0, handler) == "outer"


def test_nested_success():
    for handler in handlers:
        assert check_nest_swallow(5.0, 10.0, 1.0, handler) == "success"
        assert check_nest(5.0, 10.0, 1.0, handler) == "success"


def test_nested_long_outer():
    for handler in handlers:
        assert check_nest(10.0, 1.0, 5.0, handler) == "inner"
        assert check_nest_swallow(10.0, 1.0, 5.0, handler) == "inner"


if os.name == "posix":  # Other OS have no support for signal.SIGALRM

    def test_signal_handler():
        for settime, expect_time in ((-1.5, 1), (0, 1), (0.5, 1), (3, 3), (3.2, 4)):
            assert SignalTimeout(settime).seconds == expect_time
