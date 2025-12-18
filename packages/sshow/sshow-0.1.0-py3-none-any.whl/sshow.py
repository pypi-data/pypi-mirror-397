import argparse
from contextlib import redirect_stderr
import os
import re
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


def supports_color() -> bool:
    return sys.stdout.isatty()


COLOR_ENABLED = supports_color()
SEARCH_KEYWORD: Optional[str] = None


def color(text: str, code: str) -> str:
    if not COLOR_ENABLED:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text: str) -> str:
    return color(text, "1")


def red(text: str) -> str:
    return color(text, "31")


def brightred(text: str) -> str:
    return color(text, "91")


def blue(text: str) -> str:
    return color(text, "34")


def yellow(text: str) -> str:
    return color(text, "33")


def dim(text: str) -> str:
    return color(text, "2")


def visible_len(s: str) -> int:
    return len(ANSI_ESCAPE_RE.sub("", s))


def highlight_bg(text: str, keyword_lower: Optional[str]) -> str:
    if not keyword_lower:
        return text
    kw = keyword_lower
    lower = text.lower()
    start = 0
    parts: List[str] = []
    while True:
        idx = lower.find(kw, start)
        if idx == -1:
            parts.append(text[start:])
            break
        if idx > start:
            parts.append(text[start:idx])
        end = idx + len(kw)
        match = text[idx:end]
        parts.append(f"\033[42m{match}\033[0m")
        start = end
    return "".join(parts)


@dataclass
class HostEntry:
    name: str
    options: Dict[str, List[str]] = field(default_factory=lambda: OrderedDict())

    def add_option(self, key: str, value: str) -> None:
        key = key.lower()
        self.options.setdefault(key, []).append(value)

    def get_first(self, key: str) -> Optional[str]:
        key = key.lower()
        vals = self.options.get(key)
        if not vals:
            return None
        return vals[0]

    def has(self, key: str) -> bool:
        return self.get_first(key) is not None


@dataclass
class Subgroup:
    name: str
    hosts: List[HostEntry] = field(default_factory=list)


@dataclass
class Group:
    name: str
    hosts: List[HostEntry] = field(default_factory=list)
    subgroups: "OrderedDict[str, Subgroup]" = field(default_factory=OrderedDict)


def parse_ssh_config(path: str) -> List[Group]:
    groups_by_name: Dict[str, Group] = OrderedDict()
    group_order: List[Group] = []

    def get_or_create_group(name: str) -> Group:
        if name not in groups_by_name:
            g = Group(name=name)
            groups_by_name[name] = g
            group_order.append(g)
        return groups_by_name[name]

    current_group: Optional[Group] = None
    current_subgroup: Optional[Subgroup] = None
    current_host: Optional[HostEntry] = None

    def finalize_host():
        nonlocal current_host, current_group, current_subgroup
        if current_host is None:
            return
        if current_group is None:
            current_group = get_or_create_group("Ungrouped")
        if current_subgroup is not None:
            current_subgroup.hosts.append(current_host)
        else:
            current_group.hosts.append(current_host)
        current_host = None

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            raw = line.rstrip("\n")
            stripped = raw.strip()

            if stripped == "":
                continue

            if stripped.startswith("####"):
                finalize_host()
                name = stripped[4:].strip().replace(" ", "")
                if not name:
                    name = "UnnamedGroup"
                current_group = get_or_create_group(name)
                current_subgroup = None
                continue

            if stripped.startswith("###") and not stripped.startswith("####"):
                finalize_host()
                name = stripped[3:].strip().replace(" ", "")
                if not name:
                    name = "UnnamedSubgroup"
                if current_group is None:
                    current_group = get_or_create_group("Ungrouped")
                if name not in current_group.subgroups:
                    current_group.subgroups[name] = Subgroup(name=name)
                current_subgroup = current_group.subgroups[name]
                continue

            if stripped.startswith("#"):
                continue

            if stripped.lower().startswith("host "):
                finalize_host()
                parts = stripped.split()
                if len(parts) >= 2:
                    host_name = parts[1]
                    current_host = HostEntry(name=host_name)
                else:
                    current_host = None
                continue

            if current_host is not None:
                parts = stripped.split(None, 1)
                if len(parts) == 1:
                    key, value = parts[0], ""
                else:
                    key, value = parts
                current_host.add_option(key, value)
            else:
                continue

    finalize_host()

    return group_order


def render_host(entry: HostEntry) -> List[str]:
    host_name_raw = entry.name or ""
    user_raw = entry.get_first("user") or "UNKNOWN"
    hostname_raw = entry.get_first("hostname") or "N/A"
    port_raw = entry.get_first("port")

    show_port = port_raw is not None and port_raw != "" and port_raw != "22"

    if SEARCH_KEYWORD:
        host_name = highlight_bg(host_name_raw, SEARCH_KEYWORD)
        user = highlight_bg(user_raw, SEARCH_KEYWORD)
        hostname = highlight_bg(hostname_raw, SEARCH_KEYWORD)
        if show_port:
            port = highlight_bg(port_raw, SEARCH_KEYWORD)
            ip_port = f"{hostname}:{port}"
        else:
            ip_port = hostname
    else:
        host_name = host_name_raw
        user = user_raw
        hostname = hostname_raw
        if show_port:
            ip_port = f"{hostname}:{port_raw}"
        else:
            ip_port = hostname

    def label(text: str) -> str:
        return bold(text)

    host_line = f"{label('Host')}: {yellow(host_name)}"
    user_line = f"{label('Username')}: {blue(user)}"
    ip_line = f"{label('IP&Port')}: {blue(ip_port)}"

    lines: List[str] = [host_line, user_line, ip_line]

    main_keys = {"user", "hostname", "port"}
    extra_lines: List[str] = []
    for key, values in entry.options.items():
        if key in main_keys:
            continue
        key_label = key.capitalize()
        for v in values:
            raw = f"{key_label}: {v}"
            if SEARCH_KEYWORD:
                raw = highlight_bg(raw, SEARCH_KEYWORD)
            extra_lines.append(dim(raw))

    if extra_lines:
        lines.append(dim("Additional Info:"))
        lines.extend(extra_lines)

    return lines


def compute_group_col_widths(hosts: List[HostEntry], col: int) -> Optional[List[int]]:
    if not hosts:
        return None
    if col < 1:
        col = 1

    maxw = 0
    for h in hosts:
        block = render_host(h)
        for line in block:
            w = visible_len(line)
            if w > maxw:
                maxw = w

    return [maxw] * col


def print_hosts(hosts: List[HostEntry], col: int, col_widths: Optional[List[int]] = None) -> None:
    if not hosts:
        return
    if col < 1:
        col = 1

    blocks_all: List[List[str]] = [render_host(h) for h in hosts]

    if col_widths is None:
        col_widths = [0] * col
        for idx, block in enumerate(blocks_all):
            col_idx = idx % col
            maxw = col_widths[col_idx]
            for line in block:
                lw = visible_len(line)
                if lw > maxw:
                    maxw = lw
            col_widths[col_idx] = maxw

    total = len(hosts)
    for row_start in range(0, total, col):
        row_end = min(row_start + col, total)
        row_blocks = blocks_all[row_start:row_end]

        heights = [len(b) for b in row_blocks]
        max_height = max(heights)

        for idx, b in enumerate(row_blocks):
            if len(b) < max_height:
                row_blocks[idx] = b + [""] * (max_height - len(b))

        for line_idx in range(max_height):
            pieces = []
            for col_idx, block in enumerate(row_blocks):
                text = block[line_idx]
                width = col_widths[col_idx]
                pad = width - visible_len(text)
                if pad < 0:
                    pad = 0
                pieces.append(text + " " * pad)
            print(" | ".join(pieces))
        print()


def host_matches(entry: HostEntry, keyword: str) -> bool:
    kw = keyword.lower()
    if kw in entry.name.lower():
        return True
    for key, values in entry.options.items():
        if kw in key.lower():
            return True
        for v in values:
            if key == "port" and v == "22":
                continue
            if kw in v.lower():
                return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="sshow",
        description="Prettify and group your ~/.ssh/config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--col",
        type=int,
        default=2,
        help="number of hosts per row (default: 2)",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default=os.path.expanduser("~/.ssh/config"),
        help="path to SSH config file (default: ~/.ssh/config)",
    )
    parser.add_argument(
        "-s",
        "--search",
        type=str,
        help="search string; show only hosts whose fields contain this string (case-insensitive)",
    )
    args = parser.parse_args(argv)

    groups = parse_ssh_config(args.file)

    title = bold("SSH Show")
    print(title)
    print("-" * 24)

    if not groups:
        print("No SSH config found or file is empty.")
        return

    if args.search:
        global SEARCH_KEYWORD
        SEARCH_KEYWORD = args.search.lower()
        hosts: List[HostEntry] = []
        for g in groups:
            hosts.extend(g.hosts)
            for sg in g.subgroups.values():
                hosts.extend(sg.hosts)
        matched = [h for h in hosts if host_matches(h, args.search)]
        if not matched:
            print(f"No hosts matched search string '{args.search}'.")
            SEARCH_KEYWORD = None
            return
        col_widths = compute_group_col_widths(matched, args.col)
        print_hosts(matched, args.col, col_widths)
        SEARCH_KEYWORD = None
        return

    first_group = True
    for group in groups:
        if not first_group:
            print()
        first_group = False

        group_header = red(group.name)
        print(group_header)

        all_hosts_for_group: List[HostEntry] = []
        all_hosts_for_group.extend(group.hosts)
        for sg in group.subgroups.values():
            all_hosts_for_group.extend(sg.hosts)

        col_widths = compute_group_col_widths(all_hosts_for_group, args.col)

        print_hosts(group.hosts, args.col, col_widths)

        for sg_name, sg in group.subgroups.items():
            print(brightred(f"{sg_name}"))
            print_hosts(sg.hosts, args.col, col_widths)
        print("-" * 24)


if __name__ == "__main__":
    main()
