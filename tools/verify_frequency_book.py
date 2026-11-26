"""Read back a 5 ms XLSX audit against its immediately preceding and revised CSVs."""
import argparse
import csv
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def frame_values(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return [[float(row[k]) if row[k] else None for k in ("s", "reference_Hz", "miku_Hz")]
                for row in csv.DictReader(stream)]


def verify(book, before, after, frames, notes, candidates):
    pre, post = frame_values(before), frame_values(after)
    if not len(pre) == len(post) == frames:
        raise ValueError("CSV frame count differs from expected duration")
    counts = {}
    with zipfile.ZipFile(book) as archive:
        main = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in relationships}
        for sheet in main.findall(".//{*}sheet"):
            name = sheet.get("name")
            if name not in ("全曲5ms", "音符別", "倍音候補"):
                continue
            target = targets[next(v for k, v in sheet.attrib.items() if k.endswith("}id"))]
            path = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
            n = 0
            with archive.open(path) as data:
                for _, row in ET.iterparse(data, events=("end",)):
                    if not row.tag.endswith("}row"):
                        continue
                    index = int(row.get("r"))
                    if index >= 5:
                        if index != n + 5:
                            raise ValueError(f"{name}: missing row at {n + 5}")
                        if name == "全曲5ms":
                            cells = {re.sub(r"\d", "", c.get("r")): c for c in row.findall("{*}c")}
                            expected = [n / 200, pre[n][1], pre[n][2], post[n][2]]
                            if pre[n][:2] != post[n][:2] or pre[n][0] != expected[0]:
                                raise ValueError(f"CSV sources disagree at frame {n}")
                            for col, value in zip("ADEF", expected):
                                c = cells.get(col)
                                raw = c.findtext("{*}v") if c is not None else None
                                if c is not None and c.get("t", "n") != "n":
                                    raise ValueError(f"{name}!{col}{index}: expected numeric or blank")
                                if (None if raw is None else float(raw)) != value:
                                    raise ValueError(f"{name}!{col}{index}: frequency, time or blank differs")
                        n += 1
                    row.clear()
            counts[name] = n
    if counts != {"全曲5ms": frames, "音符別": notes, "倍音候補": candidates}:
        raise ValueError(f"Unexpected sheet counts: {counts}")
    return {"rows": counts, "sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in (book, before, after)}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("book", "before", "after"):
        parser.add_argument(arg, type=Path)
    for arg in ("frames", "notes", "candidates"):
        parser.add_argument("--" + arg, required=True, type=int)
    print(json.dumps(verify(**vars(parser.parse_args())), ensure_ascii=True, indent=2))
