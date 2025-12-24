import re
from pathlib import Path

# ======================================================
# AST Nodes
# ======================================================

class Node:
    pass

class Program(Node):
    def __init__(self):
        self.statements = []

class Statement(Node):
    def __init__(self, kind, data=None):
        self.kind = kind
        self.data = data or {}
        self.children = []

# ======================================================
# AST Helper
# ======================================================

def add_statement(parent, stmt):
    if isinstance(parent, Program):
        parent.statements.append(stmt)
    else:
        parent.children.append(stmt)

# ======================================================
# Error System
# ======================================================

class SharkSyntaxError(Exception):
    def __init__(self, message, lineno=None, line=None, hint=None):
        self.message = message
        self.lineno = lineno
        self.line = line
        self.hint = hint
        super().__init__(self.__str__())

    def __str__(self):
        lines = ["🦈 SharkTankLang Error"]

        if self.lineno is not None:
            lines.append(f"→ Line {self.lineno}: {self.line}")

        lines.append(f"✖ {self.message}")

        if self.hint:
            lines.append(f"💡 Hint: {self.hint}")

        return "\n".join(lines)

# ======================================================
# Catchphrases
# ======================================================

CATCHPHRASES = {
    # Ashneer
    "sab_bekaar_hai": ("Ashneer", "Sab bekaar hai"),
    "doglapan_alert": ("Ashneer", "DOGALPAN ALERT"),
    "chalu_kar_de": ("Ashneer", "Chalu kar de"),

    # Namita
    "for_that_reason_im_out": ("Namita", "For that reason, I am out"),
    "pharma_sahi_kar_lo": ("Namita", "Pharma sahi kar lo"),
    "build_brand_value": ("Namita", "Build brand value"),

    # Aman
    "kya_kar_raha_hai_tu": ("Aman", "Kya kar raha hai tu?"),
    "boAt_waala_offer": ("Aman", "boAt waala offer"),
    "brand_banao": ("Aman", "Brand banao"),

    # Peyush
    "i_believe_in_you": ("Peyush", "I believe in you"),
    "founder_first": ("Peyush", "Founder first"),
    "lets_fix_this": ("Peyush", "Let’s fix this"),

    # Anupam
    "yeh_dhandha_nahi_chalega": ("Anupam", "Yeh dhandha nahi chalega"),
    "lets_be_practical": ("Anupam", "Let’s be practical"),
    "main_equity_king": ("Anupam", "Main equity king hoon"),

    # Vineeta
    "hustle_harder": ("Vineeta", "Hustle harder"),
    "dil_se_pitch_karo": ("Vineeta", "Dil se pitch karo"),
    "emotional_equity": ("Vineeta", "Emotional equity"),
}

# ======================================================
# Parser
# ======================================================

def parse_lines(lines):
    program = Program()
    stack = [program]

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        current = stack[-1]

        # end
        if line == "end":
            if len(stack) == 1:
                raise SharkSyntaxError(
                    "Unexpected 'end'.",
                    lineno=lineno,
                    line=line,
                    hint="There is no open block to close."
                )
            stack.pop()
            continue

        # pitch
        m = re.match(r'^pitch\((.+)\)$', line)
        if m:
            add_statement(current, Statement("pitch", {"text": m.group(1)}))
            continue

        # ask
        m = re.match(r'^ask\((.+),(.+)\)$', line)
        if m:
            add_statement(
                current,
                Statement(
                    "ask",
                    {"amount": m.group(1).strip(), "equity": m.group(2).strip()}
                )
            )
            continue

        # valuation
        m = re.match(r'^valuation\((.+)\)$', line)
        if m:
            add_statement(
                current,
                Statement("valuation", {"value": m.group(1).strip()})
            )
            continue

        # shark block
        m = re.match(r'^shark\s+(\w+)\s*->$', line)
        if m:
            stmt = Statement("shark", {"name": m.group(1)})
            add_statement(current, stmt)
            stack.append(stmt)
            continue

        # offer
        m = re.match(r'^offer\((.+),(.+)\)$', line)
        if m:
            add_statement(
                current,
                Statement(
                    "offer",
                    {"amount": m.group(1).strip(), "equity": m.group(2).strip()}
                )
            )
            continue

        # counter
        m = re.match(r'^counter\((.+),(.+)\)$', line)
        if m:
            add_statement(
                current,
                Statement(
                    "counter",
                    {"amount": m.group(1).strip(), "equity": m.group(2).strip()}
                )
            )
            continue

        # deal / no_deal
        if line == "deal()":
            add_statement(current, Statement("deal"))
            continue

        if line == "no_deal()":
            add_statement(current, Statement("no_deal"))
            continue

        # catchphrases
        matched = False
        for key, meta in CATCHPHRASES.items():
            m = re.match(rf'^{key}\((.*)\)$', line)
            if m:
                arg = m.group(1).strip()
                add_statement(
                    current,
                    Statement(
                        "catchphrase",
                        {
                            "shark": meta[0],
                            "label": meta[1],
                            "text": arg if arg else None,
                        },
                    ),
                )
                matched = True
                break

        if matched:
            continue

        raise SharkSyntaxError(
            "Unknown syntax.",
            lineno=lineno,
            line=line,
            hint="Use pitch(), ask(), offer(), deal(), or shark catchphrases.",
        )

    if len(stack) != 1:
        raise SharkSyntaxError(
            "Missing 'end' for a block.",
            hint="Every 'shark ->' block must be closed with 'end'.",
        )

    return program

# ======================================================
# Translator
# ======================================================

def translate(program):
    out = []
    out.append("last_offer = None")

    def emit(statements):
        for stmt in statements:
            k = stmt.kind

            if k == "pitch":
                out.append(f"print({stmt.data['text']})")

            elif k == "ask":
                out.append(
                    f"print('Ask:', {stmt.data['amount']}, 'for', {stmt.data['equity']}, '%')"
                )

            elif k == "valuation":
                out.append(f"print('Valuation:', {stmt.data['value']})")

            elif k == "shark":
                out.append(f"print('--- Shark: {stmt.data['name']} ---')")
                emit(stmt.children)

            elif k == "offer":
                out.append(f"last_offer = ({stmt.data['amount']}, {stmt.data['equity']})")
                out.append("print('[OFFER]', last_offer)")

            elif k == "counter":
                out.append(f"last_offer = ({stmt.data['amount']}, {stmt.data['equity']})")
                out.append("print('[COUNTER]', last_offer)")

            elif k == "deal":
                out.append("print('[DEAL]', last_offer)")

            elif k == "no_deal":
                out.append("print('[NO DEAL] Founder walked away')")

            elif k == "catchphrase":
                if stmt.data["text"] is None:
                    out.append(f"print('{stmt.data['label']}')")
                else:
                    out.append(
                        f"print('{stmt.data['label']} →', {stmt.data['text']})"
                    )

    emit(program.statements)
    return "\n".join(out)

# ======================================================
# Execution
# ======================================================

def safe_exec(code):
    exec(code, {"__builtins__": {"print": print}})

# ======================================================
# Public API
# ======================================================

def compile_source(text):
    program = parse_lines(text.splitlines())
    return translate(program)

def run_file(path):
    src = Path(path).read_text()
    py = compile_source(src)
    print("---- Translated Python ----")
    print(py)
    print("---- Output ----")
    safe_exec(py)

def repl():
    print("SharkTankLang REPL (type runbuf to execute)")
    buf = []

    while True:
        try:
            line = input(">>> ")
        except EOFError:
            break

        if line.strip() == "exit":
            break

        if line.strip() == "runbuf":
            py = compile_source("\n".join(buf))
            safe_exec(py)
            buf.clear()
        else:
            buf.append(line)
