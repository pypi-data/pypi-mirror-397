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
from importlib import resources

NODE_VERSION = "20.8.1"


# =========================
# NODE BOOTSTRAP
# =========================

def ensure_node() -> str:
    """
    Ensure Node.js is downloaded and executable.
    Returns absolute path to Node binary.
    """
    base_dir = Path(__file__).parent
    node_dir = base_dir / "node"
    node_bin = node_dir / "node"

    if node_bin.exists():
        return str(node_bin)

    node_dir.mkdir(exist_ok=True)

    system = platform.system().lower()

    if system.startswith("linux"):
        filename = f"node-v{NODE_VERSION}-linux-x64.tar.xz"
    elif system == "darwin":
        filename = f"node-v{NODE_VERSION}-darwin-x64.tar.gz"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    url = f"https://nodejs.org/dist/v{NODE_VERSION}/{filename}"
    archive_path = node_dir / filename

    print(f"[pnw_subscriptions] Downloading Node.js {NODE_VERSION}")
    urllib.request.urlretrieve(url, archive_path)

    print("[pnw_subscriptions] Extracting Node.js")
    with tarfile.open(archive_path) as tar:
        tar.extractall(node_dir)

    extracted_root = next(
        p for p in node_dir.iterdir()
        if p.is_dir() and p.name.startswith(f"node-v{NODE_VERSION}")
    )

    extracted_bin = extracted_root / "bin" / "node"
    if not extracted_bin.exists():
        raise FileNotFoundError("Node binary not found after extraction")

    shutil.move(str(extracted_bin), str(node_bin))
    node_bin.chmod(node_bin.stat().st_mode | stat.S_IEXEC)

    shutil.rmtree(extracted_root)
    archive_path.unlink(missing_ok=True)

    return str(node_bin)


# =========================
# SUBSCRIPTION
# =========================

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

    def __init__(
        self,
        api_key: str,
        subscription_type: str,
        pusher_key: str = "a22734a47847a64386c8",
    ):
        if subscription_type not in self.SUBSCRIPTION_TYPES:
            raise ValueError(f"Invalid subscription_type: {subscription_type}")

        self.api_key = api_key
        self.pusher_key = pusher_key
        self.subscription_type = subscription_type
        self._process: Optional[subprocess.Popen] = None

    def start(self, callback: Callable[[Dict[str, Any]], None], blocking: bool = True) -> None:
        node_bin = ensure_node()

        # ✅ Wheel-safe JS resolution
        try:
            script_path = resources.files("pnw_subscriptions").joinpath(
                "scripts/generic_listener.js"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to resolve JS script: {e}")

        if not script_path.exists():
            raise FileNotFoundError(f"generic_listener.js not found: {script_path}")

        env = os.environ.copy()
        env["PNW_API_KEY"] = self.api_key
        env["PNW_PUSHER_KEY"] = self.pusher_key

        model_name, event_prefix = self.SUBSCRIPTION_TYPES[self.subscription_type]
        env["PNW_MODEL"] = model_name
        env["PNW_EVENT_PREFIX"] = event_prefix

        self._process = subprocess.Popen(
            [node_bin, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,
        )

        print(
            f"[pnw_subscriptions] Started {self.subscription_type} subscription",
            file=sys.stderr,
        )

        if blocking:
            self._process_events(callback)
        else:
            threading.Thread(
                target=self._process_events,
                args=(callback,),
                daemon=True,
            ).start()

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
                    print(
                        f"[pnw_subscriptions] JSON parse error: {line}",
                        file=sys.stderr,
                    )
        except Exception as e:
            print(f"[pnw_subscriptions] Error: {e}", file=sys.stderr)
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
            print("[pnw_subscriptions] Subscription stopped", file=sys.stderr)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


# =========================
# MULTI SUBSCRIPTION
# =========================

class MultiSubscription:
    def __init__(self, api_key: str, pusher_key: str = "a22734a47847a64386c8"):
        self.api_key = api_key
        self.pusher_key = pusher_key
        self.subscriptions: List[tuple[Subscription, Callable]] = []

    def add_subscription(
        self,
        subscription_type: str,
        callback: Callable[[Dict[str, Any]], None],
    ) -> Subscription:
        sub = Subscription(self.api_key, subscription_type, self.pusher_key)
        self.subscriptions.append((sub, callback))
        return sub

    def start_all(self) -> None:
        if not self.subscriptions:
            raise ValueError("No subscriptions added")

        for sub, cb in self.subscriptions[:-1]:
            sub.start(cb, blocking=False)

        last_sub, last_cb = self.subscriptions[-1]
        try:
            last_sub.start(last_cb, blocking=True)
        except KeyboardInterrupt:
            self.stop_all()

    def stop_all(self) -> None:
        for sub, _ in self.subscriptions:
            sub.stop()
