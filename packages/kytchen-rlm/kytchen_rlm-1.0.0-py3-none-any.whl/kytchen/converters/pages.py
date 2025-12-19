from __future__ import annotations

import re


def parse_pages(pages: str | None, page_count: int) -> list[int]:
    if page_count <= 0:
        return []

    if pages is None or not str(pages).strip():
        return list(range(page_count))

    s = str(pages).strip()
    out: set[int] = set()

    for part in re.split(r"\s*,\s*", s):
        if not part:
            continue
        if "-" in part:
            a_s, b_s = part.split("-", 1)
            a = int(a_s.strip())
            b = int(b_s.strip())
            if a <= 0 or b <= 0:
                raise ValueError("pages must be 1-indexed")
            start = min(a, b)
            end = max(a, b)
            for n in range(start, end + 1):
                idx = n - 1
                if 0 <= idx < page_count:
                    out.add(idx)
        else:
            n = int(part.strip())
            if n <= 0:
                raise ValueError("pages must be 1-indexed")
            idx = n - 1
            if 0 <= idx < page_count:
                out.add(idx)

    return sorted(out)


def join_with_boundaries(
    pieces: list[tuple[int, str]],
    separator: str = "\n\n",
) -> tuple[str, list[dict[str, int]]]:
    text_parts: list[str] = []
    boundaries: list[dict[str, int]] = []

    pos = 0
    for i, (page_index, page_text) in enumerate(pieces):
        if i > 0:
            text_parts.append(separator)
            pos += len(separator)

        start = pos
        text_parts.append(page_text)
        pos += len(page_text)
        end = pos

        boundaries.append(
            {
                "page": int(page_index) + 1,
                "start_char": int(start),
                "end_char": int(end),
                "chars": int(end - start),
            }
        )

    return "".join(text_parts), boundaries
