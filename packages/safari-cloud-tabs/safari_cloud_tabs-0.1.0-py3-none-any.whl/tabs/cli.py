import argparse
import os
import sqlite3
import sys
import time
import webbrowser
from pathlib import Path
from typing import Iterable


DEFAULT_DB = str(Path.home() / "Library/Containers/com.apple.Safari/Data/Library/Safari/CloudTabs.db")


class CloudTabs:
    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            sys.exit(f"ERROR: database not found: {db_path}")
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            sys.exit(f"ERROR opening SQLite: {e}")

    def list_devices(self) -> list[str]:
        sql = "SELECT device_name FROM cloud_tab_devices ORDER BY device_name;"
        try:
            rows = self.conn.execute(sql).fetchall()
        except sqlite3.Error as e:
            sys.exit(f"ERROR querying devices: {e}")
        return [r["device_name"] for r in rows if r["device_name"]]

    def fetch_urls(
        self,
        device_filter: str = '',
        contains: str = '',
        limit: int = 0,
    ) -> list[tuple[str, str]]:
        clauses = ["c.url LIKE 'http%'"]
        params: list = []

        if device_filter:
            clauses.append("d.device_name LIKE ?")
            params.append(f"%{device_filter}%")

        if contains:
            clauses.append("c.url LIKE ?")
            params.append(f"%{contains}%")

        where = "WHERE " + " AND ".join(clauses) if clauses else ""

        if limit > 0:
            limit_clause = "LIMIT ?"
            params.append(limit)
        else:
            limit_clause = ""

        sql = f"""
        SELECT d.device_name AS device, c.position AS pos, c.url AS url
        FROM cloud_tabs c
        LEFT JOIN cloud_tab_devices d ON c.device_uuid = d.device_uuid
        {where}
        GROUP BY url
        ORDER BY d.device_name NULLS LAST, c.position DESC
        {limit_clause}
        ;
        """

        try:
            rows = self.conn.execute(sql, params).fetchall()
        except sqlite3.Error as e:
            sys.exit(f"ERROR querying URLs: {e}")

        return [(row["device"], row["url"]) for row in rows if row["url"]]


class Browser:
    def __init__(self, name: str = "default"):
        self._controller = self._pick_browser(name)

    def _pick_browser(self, name: str):
        name = name.lower()
        mapping = {
            "default": None,
            "safari": "safari",
            "chrome": "google-chrome" if sys.platform != "darwin" else "chrome",
            "firefox": "firefox",
        }
        key = mapping.get(name, name)
        return webbrowser.get(key)

    def open(self, urls: Iterable[str], delay: float, new_tab: bool = True):
        opener = self._controller.open
        if new_tab:
            opener = self._controller.open_new_tab

        count = 0
        for url in urls:
            try:
                opener(url)
                count += 1
            except webbrowser.Error as exc:
                print(f"Failed opening {url}: {exc}", file=sys.stderr)
            time.sleep(max(0.0, delay))
        return count


def main():
    ap = argparse.ArgumentParser(
        description="Opens Safari iCloud Tabs (CloudTabs.db) in browser."
    )
    ap.add_argument("--db", default=DEFAULT_DB, help=f"Path to CloudTabs.db (default: {DEFAULT_DB})")
    ap.add_argument("--device", help="Filter by device name (substring)")
    ap.add_argument("--contains", help="Filter by URL substring (e.g., 'docs.google.com')")
    ap.add_argument("--limit", type=int, default=0, help="Limit the number of URLs opened")
    ap.add_argument("--delay", type=float, default=0.2, help="Delay between opens (seconds, default: 0.2)")
    ap.add_argument(
        "--browser", choices=["default", "safari", "chrome", "firefox"],
        default="default", help="Choose browser (default: system default)"
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Don't open; just print URLs"
    )
    ap.add_argument(
        "--no-new-tab", dest="new_tab", action="store_false", default=True,
        help="Open in current tab instead of new tab"
    )
    ap.add_argument("--list-devices", action="store_true", help="List devices and exit")
    args = ap.parse_args()

    tabs = CloudTabs(args.db)

    if args.list_devices:
        devices = tabs.list_devices()
        if not devices:
            print("No devices found.")
            return
        print("Devices with iCloud Tabs:")
        for d in devices:
            print(f"- {d}")
        return

    rows = tabs.fetch_urls(args.device, args.contains, args.limit)
    if not rows:
        msg = "No URLs found"
        if args.device:
            msg += f" for device containing '{args.device}'"
        if args.contains:
            msg += f" with substring '{args.contains}'"
        print(msg + ".")
        return

    print(f"Found {len(rows)} URLs:")
    for dev, url in rows:
        print(f"[{dev}] {url}")

    if args.dry_run:
        return

    browser = Browser(args.browser)
    opened = browser.open((u for _, u in rows), delay=args.delay, new_tab=args.new_tab)
    print(f"Opened {opened} tabs.")


if __name__ == "__main__":
    main()
