import asyncio
import pytest
from aiocoalesce import Coalescer

@pytest.mark.asyncio
async def test_basic_execution():
    c = Coalescer()
    
    async def work():
        return 42
        
    result = await c.run("key", work())
    assert result == 42
    
@pytest.mark.asyncio
async def test_coalescing_behavior():
    c = Coalescer()
    counter = 0
    event = asyncio.Event()
    
    async def slow_work():
        nonlocal counter
        counter += 1
        await event.wait()
        return counter

    # Start the first one
    t1 = asyncio.create_task(c.run("key", slow_work()))
    
    # Give it a moment to start
    await asyncio.sleep(0.01)
    
    # Start the second one
    t2 = asyncio.create_task(c.run("key", slow_work()))
    
    # Start a third one
    t3 = asyncio.create_task(c.run("key", slow_work()))
    
    # Let them proceed
    event.set()
    
    r1 = await t1
    r2 = await t2
    r3 = await t3
    
    assert r1 == 1
    assert r2 == 1
    assert r3 == 1
    assert counter == 1  # Crucial: only executed once

@pytest.mark.asyncio
async def test_sequential_execution_restarts():
    c = Coalescer()
    counter = 0
    
    async def work():
        nonlocal counter
        counter += 1
        return counter
        
    r1 = await c.run("key", work())
    assert r1 == 1
    
    r2 = await c.run("key", work())
    assert r2 == 2
    assert counter == 2
