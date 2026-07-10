#!/usr/bin/env python3
"""Setup script to verify and install dependencies."""
import sys
import os
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_warning(text):
    print(f"[WARN] {text}")

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} detected. Python 3.8+ required")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print_header("Checking FFmpeg")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_success(f"FFmpeg found: {version}")
            return True
    except FileNotFoundError:
        pass
    
    print_error("FFmpeg not found. Please install it:")
    print("  Windows: choco install ffmpeg")
    print("  macOS: brew install ffmpeg")
    print("  Linux: sudo apt-get install ffmpeg")
    return False

def check_env_file():
    """Check if .env file exists."""
    print_header("Checking Environment Variables")
    env_file = Path(".env")
    
    if env_file.exists():
        print_success(".env file found")
        
        # Check required keys
        with open(env_file, "r") as f:
            content = f.read()
        
        required_keys = ["OPENAI_API_KEY", "PEXELS_API_KEY"]
        missing_keys = []
        
        for key in required_keys:
            if key in content:
                print(f"  [OK] {key} present")
            else:
                print(f"  [MISSING] {key}")
                missing_keys.append(key)
        
        return len(missing_keys) == 0
    else:
        print_error(".env file not found")
        print("Create .env with:")
        print("  OPENAI_API_KEY=sk-your-key")
        print("  PEXELS_API_KEY=your-pexels-key")
        return False

def check_directories():
    """Check if required directories exist."""
    print_header("Checking Directories")
    
    required_dirs = ["Scripts", "Assets", "Output", "Logs", "Prompts"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  [EXISTS] {dir_name}/")
        else:
            print(f"  [CREATING] {dir_name}/")
            dir_path.mkdir(exist_ok=True)

def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Python Dependencies")
    
    try:
        print("Running: pip install -r requirements.txt")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print_success("All dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    print_header("Testing Module Imports")
    
    modules = [
        ("dotenv", "python-dotenv"),
        ("openai", "openai"),
        ("requests", "requests"),
        ("moviepy", "moviepy"),
        ("google_auth_oauthlib", "google-auth-oauthlib"),
        ("googleapiclient", "google-api-python-client"),
        ("schedule", "schedule"),
    ]
    
    all_ok = True
    
    for module_name, package_name in modules:
        try:
            __import__(module_name)
            print(f"  [OK] {module_name}")
        except ImportError:
            print(f"  [MISSING] {module_name} (from {package_name})")
            all_ok = False
    
    return all_ok

def main():
    """Run all setup checks."""
    print("\n" + "=" * 60)
    print("  YouTube Shorts Automation - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("FFmpeg", check_ffmpeg),
        ("Environment Variables", check_env_file),
        ("Directories", check_directories),
        ("Python Dependencies", install_dependencies),
        ("Module Imports", test_imports),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Error during {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print_header("Setup Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {check_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print_success("\nAll checks passed! Ready to generate videos.")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Or schedule daily: python scheduler.py --time 09:00")
        return 0
    else:
        print_error("\nSome checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
