"""Drive the gg console in a pty and save screens as SVG.

usage: shoot.py <script.json> <outdir>

script.json: {"cmd": [...], "env": {...}, "rows": 34, "cols": 118,
              "steps": [["wait", 4], ["key", "\\u001b"], ["shot", "queue"], ...]}
"""
import html, json, os, pty, re, select, sys, time

import pyte

QUERIES = [
    (re.compile(rb"\x1b\[6n"), lambda m, r, c: b"\x1b[1;1R"),
    (re.compile(rb"\x1b\[0?c"), lambda m, r, c: b"\x1b[?62;1;2;6;7;8;9;15;18;21;22c"),
    (re.compile(rb"\x1b\[18t"), lambda m, r, c: f"\x1b[8;{r};{c}t".encode()),
    (re.compile(rb"\x1b\]10;\?(\x07|\x1b\\)"), lambda m, r, c: b"\x1b]10;rgb:e6e6/e6e6/e6e6\x1b\\"),
    (re.compile(rb"\x1b\]11;\?(\x07|\x1b\\)"), lambda m, r, c: b"\x1b]11;rgb:1e1e/1e1e/2424\x1b\\"),
    (re.compile(rb"\x1b\[\?u"), lambda m, r, c: b"\x1b[?0u"),
]

# The 16 ANSI colours, a calm palette.
ANSI = {
    "black": "#1e1e24", "red": "#e06c75", "green": "#98c379", "brown": "#e5c07b",
    "blue": "#61afef", "magenta": "#c678dd", "cyan": "#56b6c2", "white": "#d7dae0",
    "brightblack": "#5c6370", "brightred": "#ff7b86", "brightgreen": "#b5e890",
    "brightbrown": "#ffd68a", "brightblue": "#8cc8ff", "brightmagenta": "#de9bf0",
    "brightcyan": "#7fd6e0", "brightwhite": "#ffffff",
}
DEFAULT_FG, DEFAULT_BG = "#d7dae0", "#1e1e24"


def colour(value, default):
    if value in (None, "default"):
        return default
    if value in ANSI:
        return ANSI[value]
    if re.fullmatch(r"[0-9a-fA-F]{6}", value):
        return "#" + value.lower()
    return default


def tidy(screen):
    """Show the release number, not the local build's commit."""
    for y in range(screen.lines):
        line = "".join(screen.buffer[y][x].data for x in range(screen.columns))
        m = re.search(r" gg (\d+\.\d+\.\d+)\+[0-9a-f]+ ", line)
        if m:
            replacement = (" gg " + m.group(1) + " ").rjust(m.end() - m.start(), "┄")
            for i, ch in enumerate(replacement):
                cell = screen.buffer[y][m.start() + i]
                screen.buffer[y][m.start() + i] = cell._replace(data=ch)


def render_svg(screen, path, title):
    tidy(screen)
    cw, lh, pad, bar = 8.4, 18, 14, 30
    width = screen.columns * cw + pad * 2
    height = screen.lines * lh + pad * 2 + bar
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'role="img" aria-label="{html.escape(title)}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="14">',
        f'<rect width="100%" height="100%" rx="8" fill="{DEFAULT_BG}"/>',
        f'<rect width="100%" height="{bar}" rx="8" fill="#2b2b33"/>',
        f'<rect y="{bar - 8}" width="100%" height="8" fill="#2b2b33"/>',
        '<circle cx="18" cy="15" r="5.5" fill="#ff5f57"/><circle cx="36" cy="15" r="5.5" fill="#febc2e"/>'
        '<circle cx="54" cy="15" r="5.5" fill="#28c840"/>',
        f'<text x="{width / 2:.0f}" y="19" fill="#9da5b4" font-size="12" text-anchor="middle">{html.escape(title)}</text>',
    ]
    for y in range(screen.lines):
        row = screen.buffer[y]
        top = bar + pad + y * lh
        x = 0
        while x < screen.columns:
            ch = row[x]
            fg = colour(ch.fg, DEFAULT_FG)
            bg = colour(ch.bg, DEFAULT_BG)
            if ch.reverse:
                fg, bg = bg, fg
            bold = ch.bold
            start, text = x, []
            while x < screen.columns:
                c = row[x]
                f2, b2 = colour(c.fg, DEFAULT_FG), colour(c.bg, DEFAULT_BG)
                if c.reverse:
                    f2, b2 = b2, f2
                if (f2, b2, c.bold) != (fg, bg, bold):
                    break
                text.append(c.data or " ")
                x += 1
            left = pad + start * cw
            if bg != DEFAULT_BG:
                out.append(f'<rect x="{left:.1f}" y="{top}" width="{len(text) * cw:.1f}" height="{lh + 0.5}" fill="{bg}" shape-rendering="crispEdges"/>')
            s = "".join(text)
            if s.strip():
                weight = ' font-weight="700"' if bold else ""
                out.append(
                    f'<text x="{left:.1f}" y="{top + 13.5}" fill="{fg}"{weight} xml:space="preserve" '
                    f'textLength="{len(text) * cw:.1f}" lengthAdjust="spacingAndGlyphs">{html.escape(s)}</text>')
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out))


def main():
    script = json.load(open(sys.argv[1]))
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    rows, cols = script.get("rows", 34), script.get("cols", 118)
    screen = pyte.Screen(cols, rows)
    stream = pyte.ByteStream(screen)

    env = dict(os.environ)
    env.update(script.get("env", {}))
    env["TERM"] = "xterm-256color"
    env["COLORTERM"] = "truecolor"
    pid, fd = pty.fork()
    if pid == 0:
        import fcntl, struct, termios
        fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
        if script.get("cwd"):
            os.chdir(script["cwd"])
        os.execvpe(script["cmd"][0], script["cmd"], env)
    import fcntl, struct, termios
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

    raw = open(os.path.join(outdir, "raw.bin"), "wb")

    def pump(seconds):
        end = time.time() + seconds
        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.05)
            if fd in r:
                try:
                    data = os.read(fd, 65536)
                except OSError:
                    return False
                if not data:
                    return False
                raw.write(data)
                for pattern, answer in QUERIES:
                    for m in pattern.finditer(data):
                        os.write(fd, answer(m, rows, cols))
                stream.feed(data)
        return True

    for step in script["steps"]:
        kind, arg = step[0], step[1]
        if kind == "wait":
            if not pump(float(arg)):
                print("console exited early")
                break
        elif kind == "key":
            os.write(fd, arg.encode())
            pump(float(step[2]) if len(step) > 2 else 1.0)
        elif kind == "shot":
            title = step[2] if len(step) > 2 else "gg"
            render_svg(screen, os.path.join(outdir, f"{arg}.svg"), title)
            with open(os.path.join(outdir, f"{arg}.txt"), "w") as f:
                f.write("\n".join(screen.display))
            print(f"saved {arg}")
    try:
        os.write(fd, b"\x03")
        pump(1)
    except OSError:
        pass
    try:
        os.kill(pid, 9)
    except OSError:
        pass


if __name__ == "__main__":
    main()
