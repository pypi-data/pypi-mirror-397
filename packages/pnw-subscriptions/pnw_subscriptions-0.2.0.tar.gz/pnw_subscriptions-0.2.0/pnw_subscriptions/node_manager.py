import os
import sys
import stat
import subprocess
import urllib.request
import tarfile
import zipfile
import platform

NODE_VERSION = "20.8.1"  # pick your Node version
NODE_DIR = os.path.join(os.path.dirname(__file__), "node")
NODE_BIN = os.path.join(NODE_DIR, "node")

def ensure_node():
    if os.path.exists(NODE_BIN):
        return NODE_BIN  # already downloaded

    os.makedirs(NODE_DIR, exist_ok=True)

    system = platform.system().lower()
    arch = platform.machine()

    if system == "linux":
        url = f"https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-linux-x64.tar.xz"
    elif system == "darwin":
        url = f"https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-darwin-x64.tar.gz"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    archive_path = os.path.join(NODE_DIR, os.path.basename(url))
    print(f"Downloading Node.js from {url} ...")
    urllib.request.urlretrieve(url, archive_path)

    print("Extracting Node.js ...")
    if archive_path.endswith(".tar.xz") or archive_path.endswith(".tar.gz"):
        import tarfile
        with tarfile.open(archive_path) as tar:
            tar.extractall(path=NODE_DIR)
        # Node binary is inside a versioned folder
        node_folder = os.path.join(NODE_DIR, f"node-v{NODE_VERSION}-{system}-x64")
        node_bin_path = os.path.join(node_folder, "bin", "node")
    else:
        raise RuntimeError("Unsupported archive format")

    # Move binary to NODE_DIR
    os.rename(node_bin_path, NODE_BIN)
    os.chmod(NODE_BIN, os.stat(NODE_BIN).st_mode | stat.S_IEXEC)

    # Cleanup
    import shutil
    shutil.rmtree(node_folder)
    os.remove(archive_path)

    return NODE_BIN

def run_node(*args):
    node_path = ensure_node()
    result = subprocess.run([node_path, *args], capture_output=True, text=True)
    return result
