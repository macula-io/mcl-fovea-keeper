"""Generate mcl-fovea-keeper's two C4 diagrams into assets/.

Run:  python3 architecture/c4_diagrams.py

  c4-context.svg     Level 1: the keeper, who runs it, who checks what it keeps,
                     and every system it talks to
  c4-components.svg  Level 3: inside the keeper image (keep.sh, main.go's parts,
                     the released fovea, macula-go) and what is mounted into it

Every element is traceable to this repository: main.go, keep.sh, Containerfile,
systemd/ and .github/workflows/build-push.yml. The drawing helpers, colours and
legend are mcl-fovea's (architecture/c4_diagrams.py there), so the two models
read alike.

Colours are plain classes with a prefers-color-scheme: dark block, no CSS
custom properties (rsvg-convert renders those black), so the SVGs render the
same on GitHub, in IDE previews and through rsvg-convert. After a change,
render each (rsvg-convert -w 1400 assets/c4-context.svg -o /tmp/c.png) and
look at it; keep architecture/README.md's tables in step.
"""
import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

SANS = '"Atkinson Hyperlegible", "Segoe UI", system-ui, -apple-system, Helvetica, Arial, sans-serif'
MONO = '"JetBrains Mono", ui-monospace, Menlo, Consolas, monospace'

# Element kinds, each (light fill, light stroke, dark fill, dark stroke).
KINDS = {
    "b-sys": ("#F5E9CC", "#A56F0A", "#3A2E13", "#E3AA3C"),   # in scope
    "b-per": ("#E3EBF2", "#3B5B7A", "#1D2A36", "#8EB4D8"),   # person
    "b-mac": ("#E6E4EE", "#5E5A78", "#26243A", "#A9A4C8"),   # Macula infrastructure
    "b-ext": ("#ECEFED", "#8A9791", "#1C2421", "#7D8B85"),   # external system
    "b-cmp": ("#FFFFFF", "#8A9791", "#171F1C", "#7D8B85"),   # component or container
}

STYLE = f"""<style>
.t-name {{ font-family: {SANS}; font-size: 15px; font-weight: 700; }}
.t-desc {{ font-family: {SANS}; font-size: 12.5px; }}
.t-rel {{ font-family: {SANS}; font-size: 11.5px; paint-order: stroke; stroke-width: 4px; stroke-linejoin: round; }}
.t-code {{ font-family: {MONO}; font-size: 13px; font-weight: 600; }}
.t-type {{ font-family: {MONO}; font-size: 11.5px; }}
.t-bound {{ font-family: {MONO}; font-size: 12px; font-weight: 600; }}
.t-leg {{ font-family: {SANS}; font-size: 12px; }}
.edge {{ fill: none; stroke-width: 1.25; }}
.edge-later {{ fill: none; stroke-width: 1.25; stroke-dasharray: 5 4; }}
.bg {{ fill: #FFFFFF; }}
""" + "".join(f".{k} {{ fill: {v[0]}; stroke: {v[1]}; stroke-width: {2 if k == 'b-sys' else 1.25}; }}\n" for k, v in KINDS.items()) + """\
.b-later { fill: none; stroke: #8A9791; stroke-width: 1.25; stroke-dasharray: 5 4; }
.bound { fill: none; stroke: #B3BDB8; stroke-width: 1; }
.head { fill: #3B5B7A; }
.t-name, .t-code { fill: #16201D; }
.t-type, .t-bound, .t-leg { fill: #66736E; }
.t-desc { fill: #34413C; }
.t-rel { fill: #66736E; stroke: #FFFFFF; }
.edge, .edge-later { stroke: #8A9791; }
.arrowhead { fill: #8A9791; }
@media (prefers-color-scheme: dark) {
.bg { fill: #171F1C; }
""" + "".join(f".{k} {{ fill: {v[2]}; stroke: {v[3]}; }}\n" for k, v in KINDS.items()) + """\
.b-later { stroke: #7D8B85; }
.bound { stroke: #4A5752; }
.head { fill: #8EB4D8; }
.t-name, .t-code { fill: #E6ECE9; }
.t-type, .t-bound, .t-leg { fill: #93A09A; }
.t-desc { fill: #C3CDC8; }
.t-rel { fill: #93A09A; stroke: #171F1C; }
.edge, .edge-later { stroke: #7D8B85; }
.arrowhead { fill: #7D8B85; }
}
</style>"""

DEFS = ('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path class="arrowhead" d="M0 0L10 5L0 10z"/></marker></defs>')

LEGEND = [("b-sys", "In scope"), ("b-per", "Person"), ("b-mac", "Macula infrastructure"),
          ("b-ext", "External system"), ("b-cmp", "Container or component"), ("b-later", "Planned, not built")]
BOUNDARY = ("bound", "Boundary")


class Diagram:
    def __init__(self, name, title, w, h):
        self.name, self.title, self.w, self.h, self.parts = name, title, w, h, []

    def text(self, cls, x, y, s, anchor=None, rotate=None):
        a = f' text-anchor="{anchor}"' if anchor else ""
        r = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
        self.parts.append(f'<text class="{cls}" x="{x}" y="{y}"{a}{r}>{escape(s)}</text>')

    def box(self, cls, x, y, w, h, name, kind, desc, person=False, code=False):
        self.parts.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>')
        tx = x + 16
        if person:
            self.parts.append(f'<circle class="head" cx="{x + 26}" cy="{y + 24}" r="9"/>')
            tx = x + 44
        self.text("t-code" if code else "t-name", tx, y + 28, name)
        self.text("t-type", tx, y + 46, kind)
        for i, line in enumerate(desc):
            self.text("t-desc", x + 16, y + 70 + 16 * i, line)

    def bound(self, x, y, w, h, label):
        self.parts.append(f'<rect class="bound" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>')
        self.text("t-bound", x + 16, y + 22, label)

    def edge(self, d, later=False):
        self.parts.append(f'<path class="{"edge-later" if later else "edge"}" d="{d}" marker-end="url(#a)"/>')

    def legend(self, y, boundary=True):
        x = 24
        for cls, label in LEGEND + ([BOUNDARY] if boundary else []):
            self.parts.append(f'<rect class="{cls}" x="{x}" y="{y}" width="22" height="14" rx="3"/>')
            self.text("t-leg", x + 30, y + 12, label)
            x += 34 + 6.6 * len(label)

    def write(self):
        svg = [(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-label="{escape(self.title)}">'), f"<title>{escape(self.title)}</title>", STYLE, DEFS,
               f'<rect class="bg" x="0" y="0" width="{self.w}" height="{self.h}"/>'] + self.parts + ["</svg>", ""]
        with open(os.path.join(OUT, self.name), "w") as f:
            f.write("\n".join(svg))



def context():
    d = Diagram("c4-context.svg", "mcl-fovea-keeper system context", 1000, 640)
    d.box("b-per", 40, 30, 270, 96, "Keeper operator", "[Person]",
          ["Runs the systemd units on their", "machine; holds the deploy key"], person=True)
    d.box("b-ext", 365, 30, 270, 96, "ghcr.io", "[External: GitHub Actions, registry]",
          ["CI builds, signs and attests the", "image; the machine runs a digest"])
    d.box("b-per", 690, 30, 270, 96, "Anyone who checks", "[Person]",
          ["Clones the records and runs", "fovea verify --chain on them"], person=True)
    d.box("b-ext", 40, 210, 270, 120, "mcl-fovea-assessments", "[External: public git]",
          ["The assessments each record", "names; cloned fresh every run"])
    d.box("b-sys", 365, 210, 270, 120, "mcl-fovea-keeper", "[Go program in a signed OCI image]",
          ["One run every 15 minutes: fetches", "each slot, keeps what fovea verify", "accepts, logs every fetch"])
    d.box("b-ext", 690, 210, 270, 120, "mcl-fovea-records", "[External: public git]",
          ["keeper.json (the policy), kept", "records, endorsements, fetch logs,", "each slot's chain verdict"])
    d.box("b-ext", 40, 420, 270, 120, "mcl-fovea observer", "[Software system, ours]",
          ["Signs one 0x23 verdict per claim", "and station, chains it, puts it in", "the mesh DHT"])
    d.box("b-mac", 365, 420, 270, 120, "Macula stations, mesh DHT", "[Macula infrastructure]",
          ["Hold the latest verdict per slot", "and the realm's endorsement of", "the observer"])
    d.edge("M175 126V166H420V210"); d.text("t-rel", 183, 158, "runs every 15 minutes (podman)")
    d.edge("M560 126V210"); d.text("t-rel", 568, 186, "image, by digest")
    d.edge("M825 126V210"); d.text("t-rel", 833, 162, "clones; verifies")
    d.edge("M365 270H310"); d.text("t-rel", 337, 260, "clones", anchor="middle"); d.text("t-rel", 337, 290, "HTTPS", anchor="middle")
    d.edge("M635 270H690"); d.text("t-rel", 662, 260, "pulls,", anchor="middle"); d.text("t-rel", 662, 290, "pushes", anchor="middle")
    d.text("t-rel", 662, 304, "SSH", anchor="middle")
    d.edge("M500 330V420"); d.text("t-rel", 508, 364, "QUIC to the first station"); d.text("t-rel", 508, 380, "that proves its node id;"); d.text("t-rel", 508, 396, "finds records")
    d.edge("M310 480H365"); d.text("t-rel", 337, 470, "puts", anchor="middle")
    d.legend(590, boundary=False)
    d.write()


def components():
    d = Diagram("c4-components.svg", "mcl-fovea-keeper components", 1060, 840)
    d.box("b-cmp", 64, 30, 290, 96, "fovea-keeper.timer, .service", "[systemd user units]",
          ["7, 22, 37, 52 past each hour;", "podman run of KEEPER_IMAGE"])
    d.box("b-cmp", 385, 30, 290, 96, "Mounts", "[podman volumes]",
          ["/records (a clone, read-write);", "deploy_key, known_hosts (ro)"])
    d.box("b-ext", 706, 30, 290, 96, "mcl-fovea-assessments", "[External: public git]",
          ["Cloned to /tmp/assessments", "on every run"])
    d.bound(40, 156, 980, 474, "Keeper container")
    d.box("b-cmp", 64, 200, 451, 104, "keep.sh", "[entrypoint, /bin/sh]",
          ["Pulls /records, clones the assessments, runs keeper,", "commits records-wire1/, endorsements/, pushes (3 tries)"], code=True)
    d.box("b-sys", 545, 200, 451, 104, "run, dial", "[main.go]",
          ["Reads keeper.json; a throwaway identity; links to the", "first station that proves its node id; each slot in turn"], code=True)
    d.box("b-cmp", 64, 344, 290, 120, "keepEndorsement", "[main.go]",
          ["Finds the realm's member", "endorsement of the observer;", "keeps it once, by digest"], code=True)
    d.box("b-cmp", 385, 344, 290, 120, "keepSlot", "[main.go]",
          ["FindRecord on the slot; 0x23", "to the chain by seq, other types", "apart; flags a late record"], code=True)
    d.box("b-cmp", 706, 344, 290, 120, "verify, writeChain", "[main.go, exec]",
          ["fovea verify per record (refused", "ones apart); --chain over the", "slot into chain.txt"], code=True)
    d.box("b-cmp", 64, 492, 290, 112, "logFetch, lastFetch", "[fetches.log]",
          ["One line per fetch, with its", "time; a failed dial is logged", "into every slot"], code=True)
    d.box("b-ext", 385, 492, 290, 112, "fovea v0.5.0", "[released binary, macula-fovea]",
          ["Built into the image from", "its release tag; the only", "judge of a record"])
    d.box("b-mac", 706, 492, 290, 112, "macula-go v0.28.0", "[Macula infrastructure, Go SDK]",
          ["identity, profile, record,", "stationlink, transport"])
    d.box("b-ext", 64, 664, 451, 96, "mcl-fovea-records", "[External: public git, over SSH]",
          ["The clone mounted at /records; its origin", "takes the keeper's commits"])
    d.box("b-mac", 545, 664, 451, 96, "Macula stations, mesh DHT", "[Macula infrastructure]",
          ["The stations in keeper.json; IPv6 only,", "reached on the podman network fovea-keeper"])
    d.edge("M260 126V200"); d.text("t-rel", 268, 186, "runs")
    d.edge("M530 126V156"); d.text("t-rel", 538, 146, "mounted")
    d.edge("M851 126V176H480V200"); d.text("t-rel", 666, 172, "git clone, HTTPS", anchor="middle")
    d.edge("M515 252H545"); d.text("t-rel", 530, 244, "runs", anchor="middle")
    d.edge("M640 304V344"); d.text("t-rel", 648, 330, "each slot")
    d.edge("M385 404H354"); d.text("t-rel", 370, 396, "first", anchor="middle")
    d.edge("M675 404H706"); d.text("t-rel", 690, 396, "then", anchor="middle")
    d.edge("M460 464V478H209V492"); d.text("t-rel", 330, 474, "logs", anchor="middle")
    d.edge("M851 464V478H600V492"); d.text("t-rel", 726, 474, "execs", anchor="middle")
    d.edge("M996 252H1008V548H996"); d.text("t-rel", 1036, 400, "links, finds", anchor="middle", rotate=90)
    d.edge("M851 604V664"); d.text("t-rel", 859, 646, "QUIC")
    d.edge("M64 252H24V712H64"); d.text("t-rel", 16, 480, "pull, commit, push", anchor="middle", rotate=-90)
    d.legend(796)
    d.write()


if __name__ == "__main__":
    for make in (context, components):
        make()
