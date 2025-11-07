#!/usr/bin/env python3
"""
Cosmic Unicorn Emulator Runner

This script runs a Python application in an emulated terminal environment.
It mocks the Cosmic Unicorn hardware and displays output as a 32x32 character grid.

Usage:
    python3 emulator/run_emulator.py [script.py]
    python3 emulator/run_emulator.py [directory/]

If no argument is provided, runs a simple test/demo (no API keys required)
"""
import sys
import os
import argparse

# Add emulator mocks directory to Python path (before standard modules)
emulator_dir = os.path.dirname(os.path.abspath(__file__))
mocks_dir = os.path.join(emulator_dir, 'mocks')
sys.path.insert(0, mocks_dir)

# Import renderer to initialize it
from renderer import get_renderer

def main():
    parser = argparse.ArgumentParser(
        description='Cosmic Unicorn Emulator - Run MicroPython scripts in terminal',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                          # Run test_emulator.py (default demo)
  %(prog)s office/main.py           # Run office display
  %(prog)s office/                  # Run office/main.py
  %(prog)s examples/demo.py         # Run custom script
        '''
    )
    parser.add_argument(
        'script',
        nargs='?',
        default='emulator/test_emulator.py',
        help='Python script or directory to run (default: emulator/test_emulator.py)'
    )

    args = parser.parse_args()

    # Resolve script path
    script_path = resolve_script_path(args.script)
    if not script_path:
        print(f"❌ Error: Could not find script: {args.script}")
        sys.exit(1)

    # Get the directory containing the script
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)
    module_name = script_name[:-3] if script_name.endswith('.py') else script_name

    # Add script directory to Python path
    sys.path.insert(0, script_dir)

    print("🚀 Starting Cosmic Unicorn Emulator...")
    print("=" * 70)
    print(f"Running: {script_path}")
    print("This emulator mocks the Cosmic Unicorn hardware.")
    print("WiFi will use your host machine's network connection.")
    print("=" * 70)
    print()

    # Import and run
    try:
        # Change to script directory
        original_dir = os.getcwd()
        os.chdir(script_dir)

        # Import the module
        module = __import__(module_name)

        # Start the renderer
        print("\n" * 40)  # Clear some space

        # Run the main function
        if hasattr(module, 'main'):
            module.main()
        else:
            print(f"❌ Error: {script_name} does not have a main() function")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n✋ Emulator stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error running emulator: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Restore terminal
        from renderer import get_renderer
        renderer = get_renderer()
        if renderer:
            renderer.stop()
        # Restore original directory
        try:
            os.chdir(original_dir)
        except:
            pass


def resolve_script_path(path):
    """Resolve a script path to an absolute .py file"""
    # Get absolute path relative to current directory
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)

    # If it's a directory, look for main.py inside it
    if os.path.isdir(path):
        main_path = os.path.join(path, 'main.py')
        if os.path.isfile(main_path):
            return main_path
        else:
            print(f"⚠️  Warning: {path} is a directory but doesn't contain main.py")
            return None

    # If it's a file, check it exists
    if os.path.isfile(path):
        if path.endswith('.py'):
            return path
        else:
            print(f"⚠️  Warning: {path} is not a Python file")
            return None

    return None


if __name__ == '__main__':
    main()
