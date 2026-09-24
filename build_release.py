"""
Automated Build and Release Script for SkinRate Calculator Pro v3.0.0.
Builds both the Standalone Single-file EXE and the Portable ZIP distribution,
runs live window verification, computes SHA256 checksums, and prepares artifacts.
"""

import os
import sys
import time
import shutil
import hashlib
import subprocess
import zipfile
from pathlib import Path

# Support UTF-8 in Windows consoles if available
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
VERSION = "3.0.0"


def sha256_file(filepath: Path) -> str:
    """Compute the SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_tests():
    print("=" * 60)
    print("STEP 1: Running unit tests...")
    print("=" * 60)
    test_script = ROOT_DIR / "tests" / "test_engine.py"
    res = subprocess.run([sys.executable, str(test_script)], cwd=ROOT_DIR)
    if res.returncode != 0:
        print("[FAIL] Tests failed! Aborting release build.")
        sys.exit(1)
    print("[OK] All unit tests passed!\n")


def clean_dirs():
    print("=" * 60)
    print("STEP 2: Cleaning build and dist directories...")
    print("=" * 60)
    for d in (BUILD_DIR, DIST_DIR):
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    print("[OK] Directories cleaned.\n")


def verify_executable(exe_path: Path):
    """Launch the executable and verify the GUI window opens with no error dialogs."""
    print(f"Verifying runtime execution of {exe_path.name}...")
    import psutil
    import ctypes
    user32 = ctypes.windll.user32

    proc = subprocess.Popen([str(exe_path)])
    time.sleep(2.5)

    pids = [proc.pid]
    try:
        parent = psutil.Process(proc.pid)
        pids += [c.pid for c in parent.children(recursive=True)]
    except Exception:
        pass

    window_titles = []
    def enum_proc(hwnd, lParam):
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids:
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            if buff.value:
                window_titles.append(buff.value)
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(WNDENUMPROC(enum_proc), 0)

    # Terminate tested processes
    for pid in pids:
        try:
            psutil.Process(pid).kill()
        except Exception:
            pass

    for title in window_titles:
        if "unhandled exception" in title.lower() or "error" in title.lower():
            print(f"[FAIL] Error dialog detected in {exe_path.name}: {title}")
            sys.exit(1)

    has_main = any("skinrate" in t.lower() for t in window_titles)
    if not has_main:
        print(f"[FAIL] Main window for {exe_path.name} was not detected! Windows found: {window_titles}")
        sys.exit(1)

    print(f"[OK] {exe_path.name} opened main window '{[t for t in window_titles if 'skinrate' in t.lower()][0]}' with 0 errors.\n")


def build_single_exe():
    print("=" * 60)
    print("STEP 3: Building Standalone Single EXE...")
    print("=" * 60)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(ROOT_DIR / "SkinRateCalculator_single.spec"),
    ]
    res = subprocess.run(cmd, cwd=ROOT_DIR)
    if res.returncode != 0:
        print("[FAIL] Standalone EXE build failed!")
        sys.exit(1)

    src_exe = DIST_DIR / "SkinRate Calculator.exe"
    target_exe = DIST_DIR / f"SkinRate-Calculator-v{VERSION}-Windows.exe"
    root_exe = ROOT_DIR / "SkinRate Calculator.exe"
    if src_exe.exists():
        # Copy to dist/ with version tag
        shutil.copy2(src_exe, target_exe)
        # Copy directly to main project folder as requested
        shutil.copy2(src_exe, root_exe)
        print(f"[OK] Standalone EXE generated: {target_exe.name} ({target_exe.stat().st_size / (1024*1024):.2f} MB)")
        print(f"[OK] Placed convenient EXE in main folder: {root_exe.name}")
        verify_executable(src_exe)
    else:
        print(f"[FAIL] Output executable not found at {src_exe}")
        sys.exit(1)


def build_portable_zip():
    print("=" * 60)
    print("STEP 4: Building Fast-Launch Portable Folder & ZIP...")
    print("=" * 60)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        str(ROOT_DIR / "main.spec"),
    ]
    res = subprocess.run(cmd, cwd=ROOT_DIR)
    if res.returncode != 0:
        print("[FAIL] Portable folder build failed!")
        sys.exit(1)

    folder_dir = DIST_DIR / "SkinRate Calculator"
    if not folder_dir.exists():
        print(f"[FAIL] Output folder not found at {folder_dir}")
        sys.exit(1)

    inner_exe = folder_dir / "SkinRate Calculator.exe"
    if inner_exe.exists():
        verify_executable(inner_exe)

    zip_path = DIST_DIR / f"SkinRate-Calculator-v{VERSION}-Portable.zip"
    print(f"Packaging {folder_dir.name} into {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_dir):
            for file in files:
                file_path = Path(root) / file
                archive_name = file_path.relative_to(DIST_DIR)
                zipf.write(file_path, archive_name)

    print(f"[OK] Portable ZIP created: {zip_path.name} ({zip_path.stat().st_size / (1024*1024):.2f} MB)\n")


def generate_checksums():
    print("=" * 60)
    print("STEP 5: Generating SHA256 Checksums...")
    print("=" * 60)
    checksums = []
    for f in DIST_DIR.glob("*"):
        if f.is_file() and f.suffix in [".exe", ".zip"]:
            h = sha256_file(f)
            checksums.append(f"{h}  {f.name}")
            print(f"{f.name:<45} : {h}")

    checksum_file = DIST_DIR / "checksums.txt"
    checksum_file.write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(f"[OK] Checksums saved to {checksum_file.name}\n")


def print_summary():
    print("=" * 60)
    print(">>> RELEASE BUILD SUCCESSFUL & VERIFIED! <<<")
    print("=" * 60)
    print(f"Artifacts ready in: {DIST_DIR}")
    for item in DIST_DIR.glob("*"):
        if item.is_file():
            size_mb = item.stat().st_size / (1024 * 1024)
            print(f"  * {item.name:<42} ({size_mb:6.2f} MB)")
    print("\nNext step: Upload these artifacts to your GitHub Release (v" + VERSION + ").")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
    clean_dirs()
    build_single_exe()
    build_portable_zip()
    generate_checksums()
    print_summary()
