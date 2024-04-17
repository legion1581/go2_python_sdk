import os
import sys
import asyncio
import importlib.util


async def run_test_script(script_name):
    """
    Dynamically imports and runs perform_test from a given script.
    """
    script_path = os.path.join('test', script_name)
    spec = importlib.util.spec_from_file_location("module.name", script_path)
    test_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_module)

    await test_module.perform_test()

async def main():
    test_scripts = [
        # "testAck.py",
        "testReq.py",
        # "testSub.py",
        # Add other test script filenames as needed.
    ]

    for script in test_scripts:
        print(f"Running {script}...")
        await run_test_script(script)

if __name__ == "__main__":
    asyncio.run(main())