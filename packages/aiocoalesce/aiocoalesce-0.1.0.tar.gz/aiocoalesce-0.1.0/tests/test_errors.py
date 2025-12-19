import asyncio
import pytest
from aiocoalesce import Coalescer

@pytest.mark.asyncio
async def test_exception_propagation():
    c = Coalescer()
    
    async def failing_work():
        await asyncio.sleep(0.01)
        raise ValueError("boom")
        
    t1 = asyncio.create_task(c.run("key", failing_work()))
    t2 = asyncio.create_task(c.run("key", failing_work()))
    
    with pytest.raises(ValueError, match="boom"):
        await t1
        
    with pytest.raises(ValueError, match="boom"):
        await t2
        
    # Ensure key is removed so we can try again
    async def success_work():
        return "ok"
        
    res = await c.run("key", success_work())
    assert res == "ok"

@pytest.mark.asyncio
async def test_cancellation_of_waiter():
    c = Coalescer()
    started = asyncio.Event()
    finish = asyncio.Event()
    
    async def work():
        started.set()
        await finish.wait()
        return "done"
        
    task_main = asyncio.create_task(c.run("key", work()))
    await started.wait()
    
    # Second waiter joins
    task_waiter = asyncio.create_task(c.run("key", work()))
    
    # Give it a moment to enter run() so we don't get "coroutine never awaited" warning on the thrown-away work() arg
    await asyncio.sleep(0)
    
    # Cancel the waiter
    task_waiter.cancel()
    try:
        await task_waiter
    except asyncio.CancelledError:
        pass
        
    # Main task should still succeed
    finish.set()
    res = await task_main
    assert res == "done"

@pytest.mark.asyncio
async def test_cancellation_of_creator():
    c = Coalescer()
    started = asyncio.Event()
    finish = asyncio.Event()
    
    async def work():
        started.set()
        await finish.wait()
        return "survived"
        
    # Creator starts it
    task_creator = asyncio.create_task(c.run("key", work()))
    await started.wait()
    
    # Joiner joins
    task_joiner = asyncio.create_task(c.run("key", work()))
    
    # Cancel the creator!
    task_creator.cancel()
    try:
        await task_creator
    except asyncio.CancelledError:
        pass
        
    # Ensure work continues for joiner
    finish.set()
    res = await task_joiner
    assert res == "survived"
