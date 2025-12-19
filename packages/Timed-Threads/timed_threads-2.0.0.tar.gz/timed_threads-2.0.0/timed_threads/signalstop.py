# -*- coding: utf-8 -*-
"""
Control the timeout of blocks or callables with a context manager or a
decorator. Based on the use of signal.SIGALRM
"""

import signal
import time
from typing import List

from timed_threads.utils import BaseTimeout, TimeoutException, base_timeoutable

ALARMS: List[tuple] = []


def handle_alarms(signum, frame):
    global ALARMS
    new_alarms = [
        (
            ctx,
            max(0, drop_dead_time),
        )
        for ctx, drop_dead_time in ALARMS
    ]
    current_time = time.time()
    expired = [
        ctx for ctx, drop_dead_time in new_alarms if current_time >= drop_dead_time
    ]

    ALARMS = [
        (
            ctx,
            drop_dead_time,
        )
        for ctx, drop_dead_time in new_alarms
        if current_time < drop_dead_time
    ]
    if ALARMS:
        signal.alarm(1)
    for task in expired:
        task.stop()
        break


class SignalTimeout(BaseTimeout):
    """Context manager for limiting in the time the execution of a block
    using signal.SIGALRM Unix signal.

    See :class:`timed_threads.utils.BaseTimeout` for more information
    """

    def __init__(self, seconds, swallow_exc=True):
        # The alarm delay for a SIGALARM MUST be an integer
        # greater than 1. Round up non-integer values.
        self.seconds = max(1, int(seconds + 0.99))
        self.drop_dead_time = time.time() + self.seconds

        super(SignalTimeout, self).__init__(self.seconds, swallow_exc)

    def stop(self):
        self.state = BaseTimeout.TIMED_OUT
        self.__class__.exception_source = self
        raise TimeoutException(
            "Block exceeded maximum timeout " "value (%d seconds)." % self.seconds
        )

    # Required overrides
    def setup_interrupt(self):
        global ALARMS

        # If we have already registered ourself, do nothing and
        # return.
        if any(ctx is self for ctx, _ in ALARMS):
            return

        # If no ALARMS have been set up before, register
        # signal.SIGALRM.
        if len(ALARMS) == 0:
            signal.signal(signal.SIGALRM, handle_alarms)
            signal.alarm(1)

        # Register our self.seconds value in the global
        # ALARMS registry.
        ALARMS.append((self, self.drop_dead_time))

    def suppress_interrupt(self):
        global ALARMS
        ALARMS = [
            (ctx, drop_dead_time) for ctx, drop_dead_time in ALARMS if ctx is not self
        ]
        if len(ALARMS) == 0:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, signal.SIG_DFL)


class signal_timeoutable(base_timeoutable):  # noqa
    """A function or method decorator that raises a ``TimeoutException`` to
    decorated functions that should not last a certain amount of time.
    this one uses ``SignalTimeout`` context manager.

    See :class:`.utils.base_timoutable`` class for further comments.
    """

    to_ctx_mgr = SignalTimeout
