from collections import deque

Node = tuple[str, str]
Graph = dict[Node, list[Node]]


def build_graph(root, neighbors, max_depth: int, exclude: str = "") -> Graph:
    graph: Graph = {}
    seen = {root}
    queue = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth == max_depth:
            graph[node] = []
            continue
        deps = [d for d in neighbors(node)
                if not (exclude and exclude in d[0])]
        graph[node] = deps
        for dep in deps:
            if dep not in seen:
                seen.add(dep)
                queue.append((dep, depth + 1))
    return graph


def load_order(graph: Graph) -> list[Node]:
    remaining = {node: len(deps) for node, deps in graph.items()}
    users: Graph = {node: [] for node in graph}
    for node, deps in graph.items():
        for dep in deps:
            users[dep].append(node)
    ready = deque(node for node, count in remaining.items() if count == 0)
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for user in users[node]:
            remaining[user] -= 1
            if remaining[user] == 0:
                ready.append(user)
    if len(order) != len(graph):
        cycle = [label(n) for n in graph if n not in order]
        raise ValueError(f"цикл зависимостей среди: {', '.join(cycle)}")
    return order


def label(node: Node) -> str:
    return f"{node[0]}@{node[1]}"


def to_mermaid(graph: Graph) -> str:
    ids = {node: f"n{i}" for i, node in enumerate(graph)}
    lines = ["flowchart LR"]
    lines += [f'    {ids[n]}["{label(n)}"]' for n in graph]
    for node, deps in graph.items():
        lines += [f"    {ids[node]} --> {ids[dep]}" for dep in deps]
    return "\n".join(lines) + "\n"
