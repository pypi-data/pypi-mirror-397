#!/usr/bin/env python3
"""
Local test script for Quash MCP without full MCP protocol.
Tests the execute function directly.
"""
import asyncio
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quash_mcp.state import get_state
from quash_mcp.tools.build import build
from quash_mcp.tools.connect import connect
from quash_mcp.tools.configure import configure
from quash_mcp.tools.execute import execute


async def test_build():
    """Test the build tool"""
    print("\n" + "="*60)
    print("Testing BUILD tool")
    print("="*60)
    result = await build()
    print(json.dumps(result, indent=2))
    return result


async def test_connect(device_serial=None):
    """Test the connect tool"""
    print("\n" + "="*60)
    print("Testing CONNECT tool")
    print("="*60)
    result = await connect(device_serial=device_serial)
    print(json.dumps(result, indent=2))
    return result


async def test_configure():
    """Test the configure tool"""
    print("\n" + "="*60)
    print("Testing CONFIGURE tool")
    print("="*60)

    # Replace with your actual API key
    api_key = "mhg_AMncG3jkTtEntd8vTqJk3nHl6rnxceRr"

    result = await configure(
        quash_api_key=api_key,
        model="anthropic/claude-sonnet-4.5",
        temperature=0.2,
        max_steps=10,
        vision=False,
        reasoning=False,
        reflection=False,
        debug=True
    )
    print(json.dumps(result, indent=2))
    return result


async def test_execute(task: str):
    """Test the execute tool"""
    print("\n" + "="*60)
    print("Testing EXECUTE tool")
    print("="*60)

    def progress_callback(message):
        print(f"[PROGRESS] {message}")

    result = await execute(task=task, progress_callback=progress_callback)
    print("\n[RESULT]")
    print(json.dumps(result, indent=2))
    return result


async def main():
    """Run all tests"""
    print("🧪 Quash MCP Local Testing")
    print("="*60)

    # Test 1: Build (check dependencies)
    await test_build()

    # Test 2: Connect to device
    # Leave device_serial=None to auto-detect, or specify like "emulator-5554"
    await test_connect(device_serial=None)

    # Test 3: Configure
    await test_configure()

    # Test 4: Execute a task
    # Uncomment and modify the task you want to test:
    # task = "Open Settings"
    task = "Open Chrome and search for quashbugs.com"
    # task = "Tell me what apps are on the home screen"

    await test_execute(task)

    print("\n" + "="*60)
    print("✅ All tests completed")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())