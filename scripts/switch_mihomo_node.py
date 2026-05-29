#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.parse
import urllib.request


def request_json(url: str):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)


def switch_node(controller: str, group: str, node: str) -> int:
    url = controller.rstrip("/") + "/proxies/" + urllib.parse.quote(group)
    request = urllib.request.Request(
        url,
        data=json.dumps({"name": node}).encode(),
        method="PUT",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status


def find_node(nodes, query: str):
    if query.isdigit():
        index = int(query)
        if 1 <= index <= len(nodes):
            return nodes[index - 1]
        raise ValueError(f"node index out of range: {index}")

    exact_matches = [node for node in nodes if node == query]
    if exact_matches:
        return exact_matches[0]

    fuzzy_matches = [node for node in nodes if query.lower() in node.lower()]
    if len(fuzzy_matches) == 1:
        return fuzzy_matches[0]
    if not fuzzy_matches:
        raise ValueError(f"no node matched: {query}")

    print("Multiple nodes matched. Use a more specific name or index:", file=sys.stderr)
    for index, node in enumerate(fuzzy_matches, 1):
        print(f"{index}. {node}", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List or switch a mihomo proxy node through the local controller API."
    )
    parser.add_argument("node", nargs="?", help="Node name, partial name, or 1-based index.")
    parser.add_argument("--list", action="store_true", help="List nodes in the proxy group.")
    parser.add_argument("--group", default="GLOBAL", help="Proxy group name. Default: GLOBAL.")
    parser.add_argument(
        "--controller",
        default="http://127.0.0.1:9090",
        help="Mihomo controller URL. Default: http://127.0.0.1:9090.",
    )
    args = parser.parse_args()

    data = request_json(args.controller.rstrip("/") + "/proxies")
    proxies = data.get("proxies", {})
    group_data = proxies.get(args.group)
    if not group_data:
        print(f"Proxy group not found: {args.group}", file=sys.stderr)
        print("Available groups:", file=sys.stderr)
        for name, value in proxies.items():
            if "all" in value:
                print(f"- {name}", file=sys.stderr)
        return 1

    nodes = group_data.get("all", [])
    print(f"GROUP: {args.group}")
    print(f"CURRENT: {group_data.get('now')}")

    if args.list or not args.node:
        for index, node in enumerate(nodes, 1):
            print(f"{index}. {node}")
        return 0

    node = find_node(nodes, args.node)
    status = switch_node(args.controller, args.group, node)
    if status != 204:
        print(f"Unexpected status while switching node: {status}", file=sys.stderr)
        return 1

    print(f"SELECTED: {node}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
