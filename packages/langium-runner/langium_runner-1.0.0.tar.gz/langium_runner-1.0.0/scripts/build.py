#!/usr/bin/env python3
"""
Simple build script for langium_runner protobuf generation.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run command and return success status."""
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        return False


def main():
    """Main build function."""
    project_root = Path(__file__).parent.parent
    langium_runner_dir = project_root / "langium_runner"
    generated_dir = langium_runner_dir / "generated"
    proto_file = langium_runner_dir / "node_modules" / "langium-ai-tools" / "dist" / "interface.proto"
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Build langium_runner")
    parser.add_argument("--clean", action="store_true", help="Clean generated files")
    parser.add_argument("--generate", action="store_true", help="Generate protobuf classes")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    args = parser.parse_args()
    
    if args.clean or args.generate:
        print("Cleaning generated files...")
        if generated_dir.exists():
            shutil.rmtree(generated_dir)
        generated_dir.mkdir(exist_ok=True)
    
    if args.install_deps:
        print("Installing dependencies...")
        if not run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], cwd=project_root):
            return False
        
        # Install Node.js dependencies if package.json exists
        if (langium_runner_dir / "package.json").exists():
            if not run_command(["npm", "install"], cwd=langium_runner_dir):
                return False
    
    if args.generate:
        print("Generating protobuf classes...")
        if not proto_file.exists():
            print(f"Error: Proto file not found at {proto_file}")
            print("Run with --install-deps first to install Node.js dependencies")
            return False
        
        proto_path = proto_file.parent
        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"--python_betterproto_out={generated_dir}",
            f"--proto_path={proto_path}",
            str(proto_file)
        ]
        
        if not run_command(cmd, cwd=project_root):
            return False
        
        print("Protobuf classes generated successfully!")
    
    if not any([args.clean, args.generate, args.install_deps]):
        parser.print_help()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
