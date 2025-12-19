"""
setup_model.py
~~~~~~~~~~~~~~

Automates the acquisition of the AI Brain for UPIF.
Downloads 'ProtectAI/deberta-v3-base-prompt-injection' and exports it to ONNX.

Requires:
    pip install optimum[onnxruntime]
"""

import os
import shutil
import subprocess
import sys

def main():
    print("UPIF: AI Model Setup 🧠")
    print("-----------------------")
    
    # 1. Check Dependencies
    try:
        import optimum.onnxruntime
    except ImportError:
        print("❌ Missing dependency: 'optimum[onnxruntime]'")
        print("   Please run: pip install optimum[onnxruntime]")
        sys.exit(1)

    # 2. Define Paths
    # We want the model in upif/data/
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(root_dir, "upif", "data")
    model_name = "ProtectAI/deberta-v3-base-prompt-injection"
    
    print(f"Target Directory: {target_dir}")
    print(f"Model ID: {model_name}")

    # 3. Export to ONNX
    print("\n[1/2] Downloading and Converting Model (This may take a minute)...")
    try:
        # Use optimum-cli to handle the heavy lifting
        cmd = [
            "optimum-cli", "export", "onnx",
            "--model", model_name,
            target_dir,
            "--task", "text-classification"
        ]
        subprocess.check_call(cmd)
        print("✅ Conversion Complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion Failed: {e}")
        sys.exit(1)

    # 4. Cleanup & Rename
    print("\n[2/2] Organizing Files...")
    # Optimum creates 'model.onnx'. We need 'guard_model.onnx' if that's what hardcoded,
    # OR we update NeuralGuard to look for 'model.onnx'.
    # NeuralGuard default is "guard_model.onnx". Let's rename.
    
    original_model = os.path.join(target_dir, "model.onnx")
    final_model = os.path.join(target_dir, "guard_model.onnx")
    
    if os.path.exists(original_model):
        if os.path.exists(final_model):
            os.remove(final_model)
        os.rename(original_model, final_model)
        print(f"✅ Renamed to {os.path.basename(final_model)}")
    else:
        print("⚠️ 'model.onnx' not found. conversion might have produced different name.")

    print("\n🎉 Success! Neural Guard is ready.")

if __name__ == "__main__":
    main()
