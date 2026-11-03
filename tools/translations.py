#!/usr/bin/env python3
"""Translation tooling for YTLocalQueue.

  translations.py extract    rewrite Localization/en.strings from the YTLPLocalizedString(@"...") calls
  translations.py check      validate Localization/*.strings (syntax, placeholders, missing/extra keys)
  translations.py generate   embed Localization/*.strings into YTLPTranslations.generated.h (used by the Makefile)

Only the Python 3 standard library is needed.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOC_DIR = os.path.join(ROOT, "Localization")
HEADER = os.path.join(ROOT, "YTLPTranslations.generated.h")
SOURCES = ["Settings.xm", "Tweak.xm", "LocalQueueManager.m", "LocalQueueViewController.m"]
CALL_RE = re.compile(r'YTLPLocalizedString\(@"((?:\\.|[^"\\])*)"\)')

# English value written to en.strings for keys that are not plain UI text
SPECIAL_DEFAULTS = {
    "ytlp.native-queue-action-titles": "add to queue|play next in queue",
}
SPECIAL_COMMENTS = {
    "ytlp.native-queue-action-titles":
        "NOT UI text. YouTube's own label(s) for its \"add to queue\" menu action in YOUR language,\n"
        "   lowercase, separated by | . The tweak uses it to find and replace that menu entry.",
}

ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}


def unescape(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            if n in ESCAPES:
                out.append(ESCAPES[n]); i += 2; continue
            if n in "uU" and re.match(r"[0-9a-fA-F]{4}", s[i + 2:i + 6]):
                out.append(chr(int(s[i + 2:i + 6], 16))); i += 6; continue
        out.append(c); i += 1
    return "".join(out)


def parse_strings(text):
    """Parse a .strings file. Returns (dict, [errors])."""
    result, errors = {}, []
    i, n = 0, len(text)

    def skip_ws_and_comments(i):
        while i < n:
            if text[i].isspace():
                i += 1
            elif text.startswith("/*", i):
                end = text.find("*/", i + 2)
                i = n if end < 0 else end + 2
            elif text.startswith("//", i):
                end = text.find("\n", i)
                i = n if end < 0 else end + 1
            else:
                break
        return i

    def read_quoted(i):
        # text[i] == '"'
        j = i + 1
        while j < n:
            if text[j] == "\\":
                j += 2
            elif text[j] == '"':
                return text[i + 1:j], j + 1
            else:
                j += 1
        return None, n

    while True:
        i = skip_ws_and_comments(i)
        if i >= n:
            break
        line = text.count("\n", 0, i) + 1
        if text[i] != '"':
            errors.append("line %d: expected a quoted key" % line)
            nl = text.find("\n", i); i = n if nl < 0 else nl + 1
            continue
        key, i = read_quoted(i)
        if key is None:
            errors.append("line %d: unterminated key" % line); break
        i = skip_ws_and_comments(i)
        if i >= n or text[i] != "=":
            errors.append("line %d: expected '=' after key" % line); continue
        i = skip_ws_and_comments(i + 1)
        if i >= n or text[i] != '"':
            errors.append("line %d: expected a quoted value" % line); continue
        value, i = read_quoted(i)
        if value is None:
            errors.append("line %d: unterminated value" % line); break
        i = skip_ws_and_comments(i)
        if i >= n or text[i] != ";":
            errors.append("line %d: missing ';' after value" % line)
        else:
            i += 1
        k = unescape(key)
        if k in result:
            errors.append("line %d: duplicate key %r" % (line, k))
        result[k] = unescape(value)
    return result, errors


def escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")


PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?(?:hh|h|ll|l|z|t|j|L)?[@dDiuUxXoOfeEgGcCsSp]")


def placeholders(s):
    return sorted(PLACEHOLDER_RE.findall(s.replace("%%", "")))


def collect_keys():
    """Keys in order of first appearance, grouped by source file."""
    seen, ordered = set(), []
    for fn in SOURCES:
        path = os.path.join(ROOT, fn)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for m in CALL_RE.finditer(f.read()):
                key = unescape(m.group(1))
                if key not in seen:
                    seen.add(key)
                    ordered.append((fn, key))
    return ordered


def cmd_extract():
    keys = collect_keys()
    lines = [
        "/* English (source) strings. Do not translate this file: copy it to <language>.strings",
        "   (see TRANSLATING.md). Regenerate with: python3 tools/translations.py extract */",
    ]
    current = None
    for fn, key in keys:
        if fn != current:
            lines.append("\n/* ---- %s ---- */" % fn)
            current = fn
        if key in SPECIAL_COMMENTS:
            lines.append("/* %s */" % SPECIAL_COMMENTS[key])
        value = SPECIAL_DEFAULTS.get(key, key)
        lines.append('"%s" = "%s";' % (escape(key), escape(value)))
    os.makedirs(LOC_DIR, exist_ok=True)
    with open(os.path.join(LOC_DIR, "en.strings"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("en.strings: %d keys" % len(keys))
    return 0


def language_files():
    return sorted(p for p in glob.glob(os.path.join(LOC_DIR, "*.strings"))
                  if os.path.basename(p) != "en.strings")


def cmd_check():
    keys = [k for _, k in collect_keys()]
    keyset = set(keys)
    failed = False

    en_path = os.path.join(LOC_DIR, "en.strings")
    if os.path.exists(en_path):
        en, errs = parse_strings(open(en_path, encoding="utf-8").read())
        for e in errs:
            print("ERROR en.strings: %s" % e); failed = True
        if set(en) != keyset:
            print("WARNING en.strings is out of date; run: python3 tools/translations.py extract")
    else:
        print("WARNING Localization/en.strings is missing; run: python3 tools/translations.py extract")

    files = language_files()
    if not files:
        print("No translations found.")
    for path in files:
        name = os.path.basename(path)
        table, errs = parse_strings(open(path, encoding="utf-8").read())
        for e in errs:
            print("ERROR %s: %s" % (name, e)); failed = True
        missing = [k for k in keys if k not in table]
        extra = [k for k in table if k not in keyset]
        for k in extra:
            print("WARNING %s: unknown key (removed/renamed in the code?): %r" % (name, k))
        for k, v in table.items():
            if k in keyset and k not in SPECIAL_DEFAULTS and placeholders(k) != placeholders(v):
                print("ERROR %s: placeholders differ from the English text: %r -> %r" % (name, k, v))
                failed = True
        done = len(keys) - len(missing)
        print("%s: %d/%d strings translated" % (name, done, len(keys)))
        for k in missing:
            print("  missing (shown in English): %r" % k)
    return 1 if failed else 0


def c_literal(data):
    """Bytes -> C string literal split per line, using only ASCII + octal escapes."""
    parts, cur = [], []
    for b in data:
        if b == 0x0A:
            cur.append("\\n"); parts.append("".join(cur)); cur = []
        elif b in (0x22, 0x5C, 0x3F) or b < 0x20 or b >= 0x7F:   # " \ ? control, non-ASCII
            cur.append("\\%03o" % b)
        else:
            cur.append(chr(b))
    if cur:
        parts.append("".join(cur))
    if not parts:
        parts = [""]
    return "\n    ".join('"%s"' % p for p in parts)


def cmd_generate():
    codes, texts = [], []
    for path in language_files():
        code = os.path.basename(path)[:-len(".strings")]
        data = open(path, "rb").read()
        table, errs = parse_strings(data.decode("utf-8"))
        if errs:
            sys.stderr.write("translations: skipping %s (%s)\n" % (os.path.basename(path), errs[0]))
            continue
        codes.append(code)
        texts.append(data)
    out = ["/* Generated by tools/translations.py from Localization/*.strings. Do not edit. */",
           "#define YTLP_TRANSLATION_COUNT %d" % len(codes)]
    if codes:
        out.append("static const char *const ytlp_translation_codes[] = {")
        out += ['    "%s",' % c for c in codes]
        out.append("};")
        out.append("static const char *const ytlp_translation_texts[] = {")
        out += ["    %s," % c_literal(t) for t in texts]
        out.append("};")
    content = "\n".join(out) + "\n"
    old = open(HEADER, encoding="utf-8").read() if os.path.exists(HEADER) else None
    if old != content:                      # keep the mtime when nothing changed (no needless rebuild)
        with open(HEADER, "w", encoding="utf-8") as f:
            f.write(content)
    return 0


def main():
    cmds = {"extract": cmd_extract, "check": cmd_check, "generate": cmd_generate}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        print(__doc__); return 2
    return cmds[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
