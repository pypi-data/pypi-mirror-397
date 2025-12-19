"""
upif.cli
~~~~~~~~

Command Line Interface for UPIF.
Allows utilizing the security layer directly from the terminal.

Usage:
    upif scan "your prompt here"
    upif interactive      (Start a testing session)
    upif setup-ai         (Download Neural Model)
    upif activate KEY     (Activate Pro License)
    upif check            (System Status)
"""

import argparse
import sys
import json
import os
import subprocess
from upif import guard

def setup_ai_model():
    """Downloads the AI model using optimum-cli."""
    print("UPIF: AI Model Setup 🧠")
    print("-----------------------")
    
    # Check if 'optimum' is installed
    try:
        import optimum
    except ImportError:
        print("❌ Missing AI dependencies.")
        print("   Please run: pip install optimum[onnxruntime]")
        return

    # Define paths relative to the INSTALLED package
    # This works even when installed via pip in site-packages
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, "data")
    model_name = "ProtectAI/deberta-v3-base-prompt-injection"

    print(f"Target: {target_dir}")
    print("Downloading Model (400MB+)...")
    
    try:
        # Run export command
        cmd = [
            "optimum-cli", "export", "onnx",
            "--model", model_name,
            target_dir,
            "--task", "text-classification"
        ]
        subprocess.check_call(cmd)
        
        # Renaissance logic
        original = os.path.join(target_dir, "model.onnx")
        final = os.path.join(target_dir, "guard_model.onnx")
        if os.path.exists(original):
            if os.path.exists(final): os.remove(final)
            os.rename(original, final)
            print("✅ AI Brain Installed Successfully.")
    except Exception as e:
        print(f"❌ Failed: {e}")

def run_interactive():
    """REPL for testing patterns."""
    print("UPIF Interactive Firewall (Ctrl+C to exit)")
    print("------------------------------------------")
    while True:
        try:
            prompt = input(">> ")
            if not prompt: continue
            
            # Neural Only check logic
            heuristic = guard.process_input(prompt)
            if heuristic != prompt:
                print(f"🚫 BLOCKED (Heuristic): {heuristic}")
            elif "[BLOCKED_BY_AI]" in heuristic:
                print(f"🤖 BLOCKED (Neural): {heuristic}")
            else:
                print(f"✅ PASSED")
                
        except KeyboardInterrupt:
            print("\nExiting.")
            break

def main():
    parser = argparse.ArgumentParser(description="UPIF: Universal Prompt Injection Firewall CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Commands
    subparsers.add_parser("scan", help="Scan a single string").add_argument("text", help="Text to scan")
    subparsers.add_parser("activate", help="Activate License").add_argument("key", help="License Key")
    subparsers.add_parser("check", help="System Status")
    subparsers.add_parser("setup-ai", help="Download AI Model (Requires upif[pro])")
    subparsers.add_parser("interactive", help="Start interactive testing session")
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "version":
        from upif import __version__
        print(f"UPIF v{__version__} (Gold Master)")
        
    elif args.command == "scan":
        result = guard.process_input(args.text)
        print(f"Result: {result}")
        
    elif args.command == "interactive":
        run_interactive()
        
    elif args.command == "setup-ai":
        setup_ai_model()

    elif args.command == "activate":
        print(f"Activating: {args.key}...")
        if guard.license_manager.activate(args.key):
            print("✅ Success!")
        else:
            print("❌ Failed.")
            sys.exit(1)

    elif args.command == "check":
        tier = guard.license_manager.get_tier()
        ai_status = "Active" if getattr(guard.neural_guard, "enabled", False) else "Disabled"
        print(f"Status: {tier} | Neural: {ai_status}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
