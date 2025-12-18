import subprocess
import json
import sys
import os
import threading
from typing import Callable, Optional, Dict, Any, List
from pathlib import Path
import platform
import stat
import urllib.request
import tarfile
import shutil

NODE_VERSION = "20.8.1"

def ensure_node() -> str:
    """
    Ensure Node.js is downloaded and executable.
    Returns path to Node binary.
    Downloads Node if missing.
    """
    node_dir = Path(__file__).parent / "node"
    node_bin = node_dir / "node"

    if node_bin.exists():
        return str(node_bin)

    node_dir.mkdir(exist_ok=True)

    system = platform.system().lower()
    arch = platform.machine()

    if system.startswith("linux"):
        url = f"https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-linux-x64.tar.xz"
    elif system == "darwin":
        url = f"https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-darwin-x64.tar.gz"
    else:
        raise RuntimeError(f"Unsupported OS for Node download: {system}")

    archive_path = node_dir / Path(url).name
    print(f"[pnw_subscriptions] Downloading Node.js from {url} ...")
    urllib.request.urlretrieve(url, archive_path)

    print(f"[pnw_subscriptions] Extracting Node.js ...")
    with tarfile.open(archive_path) as tar:
        tar.extractall(path=node_dir)

    # Find the extracted directory (skip archive itself)
    node_folder = next(
        f for f in node_dir.iterdir()
        if f.is_dir() and f.name.startswith(f"node-v{NODE_VERSION}-")
    )
    extracted_bin = node_folder / "bin" / "node"

    if not extracted_bin.exists():
        raise FileNotFoundError(f"Extracted Node binary not found at {extracted_bin}")

    # Move binary to node_dir
    shutil.move(str(extracted_bin), str(node_bin))
    node_bin.chmod(node_bin.stat().st_mode | stat.S_IEXEC)

    # Cleanup
    shutil.rmtree(node_folder)
    archive_path.unlink()

    return str(node_bin)

def run_node(*args) -> subprocess.CompletedProcess:
    """
    Run Node.js with given arguments using bundled binary.
    """
    node_bin = ensure_node()
    return subprocess.run([node_bin, *args], capture_output=True, text=True)


class Subscription:
    """
    Subscribe to Politics and War real-time events.
    """

    SUBSCRIPTION_TYPES = {
        "nations": ("nation", "NATION"),
        "trades": ("trade", "TRADE"),
        "wars": ("war", "WAR"),
        "alliances": ("alliance", "ALLIANCE"),
        "cities": ("city", "CITY"),
        "banks": ("bankrec", "BANKREC"),
        "treaties": ("treaty", "TREATY"),
        "bounties": ("bounty", "BOUNTY"),
        "baseball_games": ("baseball_game", "BASEBALL_GAME"),
        "treasure_trades": ("treasure_trade", "TREASURE_TRADE"),
        "embargoes": ("embargo", "EMBARGO"),
        "attacks": ("war_attack", "WAR_ATTACK"),
    }

    def __init__(self, api_key: str, subscription_type: str, pusher_key: str = "a22734a47847a64386c8"):
        if subscription_type not in self.SUBSCRIPTION_TYPES:
            raise ValueError(f"Invalid subscription_type. Must be one of: {list(self.SUBSCRIPTION_TYPES.keys())}")

        self.api_key = api_key
        self.pusher_key = pusher_key
        self.subscription_type = subscription_type
        self._process: Optional[subprocess.Popen] = None
        self._script_path = Path(__file__).parent / "scripts" / "generic_listener.js"

    def start(self, callback: Callable[[Dict[str, Any]], None], blocking: bool = True) -> None:
        node_bin = ensure_node()

        if not self._script_path.exists():
            raise FileNotFoundError(f"Script not found: {self._script_path}")

        env = os.environ.copy()
        env["PNW_API_KEY"] = self.api_key
        env["PNW_PUSHER_KEY"] = self.pusher_key

        model_name, event_prefix = self.SUBSCRIPTION_TYPES[self.subscription_type]
        env["PNW_MODEL"] = model_name
        env["PNW_EVENT_PREFIX"] = event_prefix

        self._process = subprocess.Popen(
            [node_bin, str(self._script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,
        )

        print(f"[Python] Started {self.subscription_type} subscription", file=sys.stderr)

        if blocking:
            self._process_events(callback)
        else:
            thread = threading.Thread(target=self._process_events, args=(callback,), daemon=True)
            thread.start()

    def _process_events(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        try:
            for line in self._process.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    callback(event)
                except json.JSONDecodeError:
                    print(f"[Python] Warning: Could not parse JSON: {line}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\n[Python] Shutting down...", file=sys.stderr)
            self.stop()
        except Exception as e:
            print(f"[Python] Error: {e}", file=sys.stderr)
            self.stop()
            raise

    def stop(self) -> None:
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
            print("[Python] Subscription stopped", file=sys.stderr)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


class MultiSubscription:
    """
    Manage multiple subscriptions simultaneously.
    """

    def __init__(self, api_key: str, pusher_key: str = "a22734a47847a64386c8"):
        self.api_key = api_key
        self.pusher_key = pusher_key
        self.subscriptions: List[Subscription] = []

    def add_subscription(self, subscription_type: str, callback: Callable[[Dict[str, Any]], None]) -> Subscription:
        sub = Subscription(self.api_key, subscription_type, self.pusher_key)
        self.subscriptions.append((sub, callback))
        return sub

    def start_all(self) -> None:
        if not self.subscriptions:
            raise ValueError("No subscriptions added. Use add_subscription() first.")
        print(f"[Python] Starting {len(self.subscriptions)} subscription(s)...", file=sys.stderr)
        for sub, callback in self.subscriptions[:-1]:
            sub.start(callback=callback, blocking=False)
        last_sub, last_callback = self.subscriptions[-1]
        try:
            last_sub.start(callback=last_callback, blocking=True)
        except KeyboardInterrupt:
            print("\n[Python] Shutting down all subscriptions...", file=sys.stderr)
            self.stop_all()

    def stop_all(self) -> None:
        for sub, _ in self.subscriptions:
            sub.stop()
        print("[Python] All subscriptions stopped", file=sys.stderr)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_all()
        return False
