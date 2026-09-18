"""Run the Homework 4 review app from analysis/review_app/.

The API and state management live in analysis.server so the review workflow
continues to use analysis/state/. This wrapper serves the adapted submission UI
from analysis/review_app/ui/.
"""

from __future__ import annotations

import argparse
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analysis.server as review_server  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8020)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--replay",
        metavar="PATH",
        help="canned annotations file to replay on a timer, relative to analysis/",
    )
    parser.add_argument("--replay-interval", type=float, default=4.0)
    args = parser.parse_args()

    review_server.UI_DIR = HERE / "ui"
    review_server.STATE_DIR.mkdir(parents=True, exist_ok=True)

    if args.replay:
        replay_path = Path(args.replay)
        if not replay_path.is_absolute():
            replay_path = review_server.HERE / replay_path
        thread = threading.Thread(
            target=review_server._replay_annotations,
            args=(replay_path, args.replay_interval),
            daemon=True,
        )
        thread.start()

    server = ThreadingHTTPServer((args.host, args.port), review_server.ReviewHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"review interface on {url}")
    print(f"serving UI from {review_server.UI_DIR}")
    print(f"serving state from {review_server.STATE_DIR}")
    print("open the URL, read a trace, select the failing text, type a note.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
