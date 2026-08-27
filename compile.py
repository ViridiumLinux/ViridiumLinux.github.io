import os, re, shutil

wiki_dir = os.path.expanduser("~/Viridium-Linux.wiki")
repo_dir = os.path.expanduser("~/Viridium-Linux")

def md_to_html(md_text):
    # Basic Markdown Parser
    html = md_text
    html = re.sub(r"```(.*?)\n(.*?)```", r"<pre><code>\2</code></pre>", html, flags=re.S)
    html = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html, flags=re.M)
    html = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html, flags=re.M)
    html = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html, flags=re.M)
    html = re.sub(r"`(.*?)`", r"<code>\1</code>", html)
    html = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r'<a href="https://github.io\2/">\1</a>', html)
    html = re.sub(r"\[\[([^\]]+)\]\]", r'<a href="https://github.io\1/">\1</a>', html)
    return html

order = ["Home", "Installation", "Configuration", "vbuild", "viridium", "Architecture", "Boot and UEFI", "Development", "Networking", "Package management", "Troubleshooting", "FAQ"]
files = {f.replace(".md", "").replace("-", " ").lower(): f for f in os.listdir(wiki_dir) if f.endswith(".md")}

sidebar = "".join([f'<li><a href="https://github.io{ "" if t=="home" else t.replace(" ", "-").lower() + "/" }">{t}</a></li>' for t in order])

for t in order:
    fname = files.get(t.lower()) or files.get("archetecture" if t=="Architecture" else "")
    if not fname: continue
    with open(os.path.join(wiki_dir, fname), "r") as f: content = md_to_html(f.read())
    
    template = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{t}</title><style>:root {{ --bg-main: #141210; --bg-sidebar: #1f1a16; --text-main: #f5f2eb; --accent: #ff8838; --border: #382414; }} body {{ font-family: sans-serif; margin: 0; display: flex; background: var(--bg-main); color: var(--text-main); min-height: 100vh; }} aside {{ width: 280px; background: var(--bg-sidebar); border-right: 1px solid var(--border); padding: 25px; position: fixed; height: 100vh; }} aside ul {{ list-style: none; padding: 0; }} aside li {{ margin-bottom: 10px; }} aside a {{ color: #bcada1; text-decoration: none; }} .download-btn {{ display: block; background: #ff8838; color: #141210 !important; font-weight: bold; padding: 12px; border-radius: 8px; margin-top: 20px; text-align: center; text-decoration: none; }} main {{ flex: 1; padding: 40px 60px; margin-left: 280px; }} h1, h2, h3 {{ color: var(--accent); }} pre {{ background: #0c0a09; padding: 15px; border-radius: 8px; border: 1px solid var(--border); overflow-x: auto; }}</style></head><body><aside><h2>Viridium Wiki</h2><ul>{sidebar}</ul><a href="https://github.com" class="download-btn">INSTALL VIRIDIUM ISO</a></aside><main>{content}</main></body></html>"""
    
    path = os.path.join(repo_dir, "index.html" if t=="Home" else f"{t.replace(' ', '-').lower()}/index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as out: out.write(template)
print("🎉 Done!")
