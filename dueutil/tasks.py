# DueUtil Async tasks.
import asyncio
import inspect
from functools import wraps

tasks = []


# A simple wrapper to create a async function that will be called forever on timeout.
# Function called from run.py
def task(timeout):
    def wrap(routine):
        @wraps(routine)
        async def wrapped_task():
            while True:
                if inspect.iscoroutinefunction(routine):
                    await routine()
                else:
                    routine()
                await asyncio.sleep(timeout)
        tasks.append(wrapped_task)
        return wrapped_task
    return wrap
