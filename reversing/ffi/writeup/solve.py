#!/usr/bin/env python3

from collections import defaultdict
from collections import deque

from fontTools.ttLib.ttFont import TTFont


def solve(ttf):
    rules = get_subs_rules(ttf)

    prev_glyph_map = defaultdict(list)
    for (backglyph, inputglyph), subsglyph in rules.items():
        prev_glyph_map[subsglyph].append((backglyph, inputglyph))

    start = "glyph00346"  # "} is correct" glyph
    goal = "T"
    path = bfs(prev_glyph_map, start, goal)
    answer = glyph_names_to_chars(ttf, path)
    print(answer)


def get_subs_rules(ttf):
    lookups = ttf["GSUB"].table.LookupList.Lookup
    rules = {}
    for subtable in lookups[-1].SubTable:
        backglyph = subtable.BacktrackCoverage[0].glyphs[0]
        inputglyphs = subtable.InputCoverage[0].glyphs
        lookup = lookups[subtable.SubstLookupRecord[0].LookupListIndex]
        for inputglyph in inputglyphs:
            subsglyph = lookup.SubTable[0].mapping[inputglyph]
            rules[backglyph, inputglyph] = subsglyph
    return rules


def bfs(graph, start, goal):
    visited = {start}
    queue = deque([(start, [])])
    while queue:
        vertex, input_glyphs = queue.popleft()
        edges = graph[vertex]
        for (next_vertex, input_glyph) in edges:
            if next_vertex == goal:
                return [next_vertex, input_glyph] + input_glyphs
            if next_vertex in visited:
                continue
            visited.add(next_vertex)
            queue.append((next_vertex, [input_glyph] + input_glyphs))


def glyph_names_to_chars(ttf, glyphnames):
    rev_cmap = ttf["cmap"].buildReversed()
    return "".join(
        chr(list(rev_cmap[glyphname])[0])
        for glyphname in glyphnames
    )


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("font")
    args = parser.parse_args()
    solve(TTFont(args.font))


if __name__ == "__main__":
    main()
