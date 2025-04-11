#!/usr/bin/env python
"""
Setup script for Agent Johnny5 system.
"""
import os
import subprocess
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Install all dependencies and set up the project."""
    print("Setting up Agent Johnny5...")
    
    # Check if venv exists, if not create it
    venv_path = project_root / "venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    
    # Determine pip path
    if os.name == "nt":  # Windows
        pip_path = venv_path / "Scripts" / "pip"
    else:  # Unix/MacOS
        pip_path = venv_path / "bin" / "pip"
    
    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    print("Installing dependencies...")
    requirements_path = project_root / "requirements.txt"
    subprocess.run([str(pip_path), "install", "-r", str(requirements_path)], check=True)
    
    # Create .env file if it doesn't exist
    env_path = project_root / ".env"
    if not env_path.exists():
        print("Creating .env file...")
        env_example_path = project_root / ".env.example"
        if env_example_path.exists():
            # Copy .env.example to .env
            with open(env_example_path, "r") as source:
                with open(env_path, "w") as target:
                    target.write(source.read())
        else:
            # Create basic .env
            with open(env_path, "w") as f:
                f.write("# API Keys\n")
                f.write("GOOGLE_API_KEY=\n\n")
                f.write("# Configuration\n")
                f.write("LOG_LEVEL=INFO\n")
                f.write("VECTOR_DB_PATH=./data/vector_db\n\n")
                f.write("# Agent settings\n")
                f.write("MAIN_AGENT_PORT=8000\n")
                f.write("MAX_TOKENS=4000\n")
                f.write("MODEL_NAME=gemini-1.5-pro\n")
    
    print("\nSetup complete!")
    print("Next steps:")
    print("1. Add your Google API key to the .env file")
    print("2. Run 'python scripts/dev.py' to start the development server")
    print("3. Develop your agents in the respective directories")

if __name__ == "__main__":
    main() 