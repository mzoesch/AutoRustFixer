import subprocess
import re
from typing import Optional
from pathlib import Path
from dataclasses import dataclass
from Source.Globals import Globals
from enum import Enum


class ENode(Enum):
    FUNCTION = 'Function'
    FIELD = 'Field'
    STRUCT = 'Struct'
    MODULE = 'Module'


@dataclass
class Node:
    kind: str
    label: str
    scoped_label: str
    parent: int | None
    detail: str | None
    nav_range: tuple[int, int]
    node_range: tuple[int, int]
    deprecated: bool

    def __str__(self) -> str:
        return (f'{self.kind}: {self.scoped_label} {'' if self.parent is None else f'[{self.parent}] '}'
                f'(@{self.node_range[0]}..{self.node_range[1]}){'' if self.detail is None else f' = {self.detail}'}')


class File:
    STRUCTURE_NODE_PATTERN = re.compile(
        r'StructureNode\s*{\s*'
            r'parent:\s*(?P<parent>\s*(None|Some\((?P<parent_id>\d+)\)))\s*,\s'
            r'label:\s*"(?P<label>(.*))",\s*'
            r'navigation_range: (?P<nav_begin>\d+)\.\.(?P<nav_end>\d+),\s*'
            r'node_range:\s*(?P<node_begin>\d+)\.\.(?P<node_end>\d+),\s*'
            r'kind:\s*SymbolKind\((?P<kind>(.*))\),\s*'
            r'detail:\s*(?P<detail>(None|Some\("(?P<detail_value>.*)"\))),\s*'
            r'deprecated:\s*(?P<deprecated>(false|true))\s*'
        r'}$'
        )

    def __init__(self, path: Path):
        self.path = path
        self.nodes: list[Optional[Node]] = []

        cmd = ['rust-analyzer', 'symbols']
        if Globals.verbose:
            print(f'[{self.path}]: Running command: {" ".join(cmd)}')
        with open(self.path, 'rb') as f:
            with subprocess.Popen(
                  cmd
                , stdin=f
                , stdout=subprocess.PIPE
                , stderr=subprocess.PIPE
                ) as p:
                stdout, stderr = p.communicate()
                lines = []
                if stdout:
                    lines.extend(stdout.decode().splitlines())
                if stderr:
                    lines.extend(stderr.decode().splitlines())

        if Globals.trace:
            for line in lines:
                print(f'[{self.path}]: {line}')
                continue

        for line in lines:
            line = line.strip()
            match = self.STRUCTURE_NODE_PATTERN.match(line)
            if not match:
                # Adding None to not invalidate indices.
                self.nodes.append(None)
                if Globals.throw_on_unknown_analysis:
                    raise ValueError(f'[{self.path}]: Unrecognized line: {line}')
                else:
                    print(f'[{self.path}]: Skipping unrecognized line: {line}')
                continue
            self.nodes.append(Node(
                kind=match.group("kind"),
                label=match.group("label"),
                scoped_label=None,
                parent=None if match.group("parent") == 'None' else int(match.group("parent_id")),
                detail=None if match.group("detail") == 'None' else match.group("detail_value"),
                nav_range=(int(match.group("nav_begin")), int(match.group("nav_end"))),
                node_range=(int(match.group("node_begin")), int(match.group("node_end"))),
                deprecated=bool(match.group('deprecated')),
                ))

        for n in self.nodes:
            if n is None:
                continue
            assert n.scoped_label is None

            scoped_label = n.label
            parent = n.parent
            while parent is not None:
                parent_node = self.nodes[parent]
                if parent_node is None:
                    raise ValueError(f'[{self.path}]: Found node as parent, which syntax this tool does not understand.')
                scoped_label = f'{parent_node.label}::{scoped_label}'
                parent = parent_node.parent
                continue
            n.scoped_label = scoped_label
            continue

        if Globals.verbose:
            for n in self.nodes:
                if n is None:
                    print('    <None>')
                else:
                    print(f'    {n}')
                continue
        return

    def __str__(self) -> str:
        return str(self.path)

    def find_all_from_parent(self, kind: str | ENode, node: Node, label: str | None) -> list[Node]:
        if isinstance(kind, ENode):
            kind = kind.value
        node_index = self.nodes.index(node)

        result = []
        for n in self.nodes:
            if n is None:
                continue
            if n.parent is None:
                continue
            if n.parent != node_index or n.kind != kind:
                continue
            if label is not None and n.label != label:
                continue
            result.append(n)
        return result


class Project:
    def __init__(self, files: list[Path]):
        self.files: list[File] = [File(path) for path in files]

    def find_all(self, kind: str | ENode, scoped_label: str) -> dict[File, list[Node]]:
        if isinstance(kind, ENode):
            kind = kind.value

        result = {}
        for f in self.files:
            for n in f.nodes:
                if n is None:
                    continue
                if n.kind == kind and n.scoped_label == scoped_label:
                    if f not in result:
                        result[f] = []
                    result[f].append(n)
                continue
            continue
        for f in self.files:
            for n in f.nodes:
                if n is None:
                    continue
                if n.kind == kind and f'{f.path.stem}::{n.scoped_label}' == scoped_label:
                    if f not in result:
                        result[f] = []
                    result[f].append(n)
                continue
            continue

        return result
