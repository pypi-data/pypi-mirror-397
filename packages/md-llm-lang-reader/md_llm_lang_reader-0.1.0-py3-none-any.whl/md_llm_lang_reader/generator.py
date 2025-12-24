import re
import html
import json
import sys
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable

import multiai


def extract_json_array(raw: str) -> str:
    """
    Extract the outermost JSON array if the model adds extra text.
    If it still fails, return the raw string (json.loads will fail).
    """
    s = raw.strip()

    if s.startswith("[") and s.endswith("]"):
        return s

    i = s.find("[")
    j = s.rfind("]")
    if i != -1 and j != -1 and j > i:
        return s[i: j + 1]

    m = re.search(r"(\[\s*\{.*\}\s*\])", s, flags=re.S)
    if m:
        return m.group(1)

    return s


def split_and_translate(paragraph: str, src: str, tgt: str, client: "multiai.Prompt") -> List[Dict[str, str]]:
    """
    Ask the model to split a paragraph into sentences and translate each.
    Retries up to 3 times if JSON parsing fails. Conversation history is kept.
    """
    first_prompt = f"""You are given a paragraph in {src}.

Task:
1) Split it into natural sentences.
   - Do NOT split on abbreviations (e.g., "Mr.", "Dr.", "etc.") or numbered list markers like "1." unless it is truly the end of a sentence.
2) For each sentence, provide a direct translation into {tgt}.

Output:
Return ONLY valid JSON (no markdown, no commentary).
The JSON must be an array of objects with exactly these keys:
- "src": the original sentence in {src}
- "tgt": its translation in {tgt}

Paragraph:
{paragraph}
"""

    raw_last = ""
    for attempt in range(1, 4):
        prompt = first_prompt if attempt == 1 else (
            "The JSON you returned could not be parsed by json.loads(). "
            "Please resend ONLY valid JSON (no markdown, no commentary), "
            'matching exactly the required schema: an array of objects with keys "src" and "tgt".'
        )

        raw = client.ask(prompt)
        raw_last = raw.strip()

        candidate = extract_json_array(raw_last)
        try:
            data = json.loads(candidate)
        except Exception:
            continue

        if not isinstance(data, list):
            continue

        out: List[Dict[str, str]] = []
        ok = True
        for item in data:
            if not isinstance(item, dict):
                ok = False
                break
            s = (item.get("src") or "").strip()
            t = (item.get("tgt") or "").strip()
            if not s or not t:
                ok = False
                break
            out.append({"src": s, "tgt": t})

        if ok and out:
            return out

    raise ValueError(
        "Could not parse valid JSON after 3 attempts. Raw output follows:\n\n" + raw_last
    )


def is_fence_line(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def fence_delim(line: str) -> str:
    stripped = line.lstrip()
    if stripped.startswith("```"):
        return "```"
    if stripped.startswith("~~~"):
        return "~~~"
    return ""


def paragraph_preview(paragraph: str, words: int = 5) -> str:
    toks = paragraph.split()
    if len(toks) <= words:
        return " ".join(toks)
    return " ".join(toks[:words]) + " ..."


@dataclass
class Options:
    input_path: str
    output_path: str
    src: str
    tgt: str
    provider: str
    model: str
    verbose: int = 1


def generate_html(opts: Options) -> str:
    """
    Generate the output HTML as a string.
    """
    def log_heading(line: str):
        if opts.verbose >= 1:
            print(line)

    def log_paragraph(paragraph: str):
        if opts.verbose == 2:
            print(paragraph_preview(paragraph))
        elif opts.verbose == 3:
            print(paragraph)

    client = multiai.Prompt()
    client.set_model(opts.provider, opts.model)

    with open(opts.input_path, encoding="utf-8") as f:
        lines = f.readlines()

    out: List[str] = []

    out.append(f"""<!DOCTYPE html>
<html lang="{html.escape(opts.src)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(opts.output_path)}</title>
<style>
body {{ font-family: sans-serif; line-height: 1.6; }}
.src {{ margin-top: 1em; }}
.tgt {{ margin-left: 1em; color: #555; }}
button.speak-btn {{ margin-left: 0.5em; }}
pre {{ background: #f6f8fa; padding: 0.75em; overflow-x: auto; }}
code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }}
</style>
<script>
(function() {{
  const SRC_LANG = {json.dumps(opts.src)};

  function chooseVoice(u) {{
    const voices = speechSynthesis.getVoices ? speechSynthesis.getVoices() : [];
    if (!voices || !voices.length) return;

    let v = voices.find(v => v.lang === u.lang);
    if (!v) {{
      v = voices.find(v => v.lang && v.lang.startsWith(u.lang));
    }}
    if (!v) {{
      const prefix = (u.lang || "").split("-")[0];
      v = voices.find(v => v.lang && v.lang.startsWith(prefix));
    }}
    if (v) u.voice = v;
  }}

  function speakText(text) {{
    if (!text) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = SRC_LANG;
    chooseVoice(u);
    speechSynthesis.speak(u);
  }}

  function wireButtons() {{
    document.querySelectorAll("button.speak-btn").forEach(btn => {{
      btn.addEventListener("click", () => {{
        speakText(btn.dataset.speak || "");
      }});
    }});
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", wireButtons);
  }} else {{
    wireButtons();
  }}
}})();
</script>
</head>
<body>
""")

    buffer: List[str] = []

    in_code_block = False
    fence = ""
    code_lines: List[str] = []

    def flush_code_block():
        if not code_lines:
            return
        code_text = "\n".join(code_lines)
        code_lines.clear()
        out.append("<pre><code>")
        out.append(html.escape(code_text))
        out.append("</code></pre>")

    def flush_paragraph():
        if not buffer:
            return
        paragraph = " ".join(buffer).strip()
        buffer.clear()
        if not paragraph:
            return

        log_paragraph(paragraph)
        pairs = split_and_translate(paragraph, opts.src, opts.tgt, client)

        for p in pairs:
            src_sent = p["src"]
            tgt_sent = p["tgt"]

            esc_src = html.escape(src_sent)
            esc_tgt = html.escape(tgt_sent)

            data_speak = html.escape(src_sent, quote=True)

            out.append('<div class="src">')
            out.append(
                f'{esc_src} <button class="speak-btn" type="button" data-speak="{data_speak}">🔊</button>'
            )
            out.append("</div>")
            out.append(f'<div class="tgt">{esc_tgt}</div>')

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        if is_fence_line(line):
            if not in_code_block:
                flush_paragraph()
                in_code_block = True
                fence = fence_delim(line)
                continue
            else:
                if fence and line.lstrip().startswith(fence):
                    in_code_block = False
                    fence = ""
                    flush_code_block()
                    continue
                code_lines.append(line)
                continue

        if in_code_block:
            code_lines.append(line)
            continue

        stripped = line.rstrip()

        if stripped.startswith("# "):
            flush_paragraph()
            out.append(f"<h1>{html.escape(stripped[2:])}</h1>")
            log_heading(stripped)
        elif stripped.startswith("## "):
            flush_paragraph()
            out.append(f"<h2>{html.escape(stripped[3:])}</h2>")
            log_heading(stripped)
        elif stripped.startswith("### "):
            flush_paragraph()
            out.append(f"<h3>{html.escape(stripped[4:])}</h3>")
            log_heading(stripped)
        elif stripped.startswith("#### "):
            flush_paragraph()
            out.append(f"<h4>{html.escape(stripped[5:])}</h4>")
            log_heading(stripped)
        elif stripped.strip() == "":
            flush_paragraph()
        else:
            buffer.append(stripped.strip())

    if in_code_block:
        in_code_block = False
        flush_code_block()

    flush_paragraph()
    out.append("</body></html>")

    return "\n".join(out)


def generate_file(opts: Options) -> None:
    """
    Generate the HTML and write it to opts.output_path.
    """
    html_text = generate_html(opts)
    with open(opts.output_path, "w", encoding="utf-8") as f:
        f.write(html_text)
