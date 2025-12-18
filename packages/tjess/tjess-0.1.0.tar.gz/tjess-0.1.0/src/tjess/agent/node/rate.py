"""Rate control for maintaining loop frequency."""

import asyncio
import time


class Rate:
    """
    Rate limiter for controlling loop frequency (similar to rospy.Rate).

    Example:
        rate = Rate(10)  # 10 Hz
        while True:
            # do work
            await rate.sleep()
    """

    def __init__(self, hz: float):
        """
        Args:
            hz: Desired frequency in Hz
        """
        if hz <= 0:
            raise ValueError("Rate must be positive")
        self.period = 1.0 / hz
        self._last_time = time.monotonic()

    async def sleep(self):
        """Sleep to maintain the desired rate."""
        current_time = time.monotonic()
        elapsed = current_time - self._last_time
        sleep_time = self.period - elapsed

        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

        self._last_time = time.monotonic()
