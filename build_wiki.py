import os
import re

def md_to_html(md_text):
    code_blocks = []
    def save_code_block(match):
        code_blocks.append(match.group(2))
        return f"<!--CODEBLOCK_{len(code_blocks)-1}-->"
    
    html = re.sub(r"```(.*?)\n(.*?)```", save_code_block, md_text, flags=re.S)

    lines = html.split("\n")
    inside_table = False
    table_html = []
    processed_lines = []
    
    for line in lines:
        stripped = line.strip()
        is_table_line = stripped.startswith("|") and stripped.endswith("|") and not ("/" in stripped or "\\" in stripped)
        
        if is_table_line:
            if re.match(r"^[\s\-\|:]+$", stripped):
                continue
            if not inside_table:
                inside_table = True
                table_html = ['<div class="table-container"><table>']
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if cells:
                is_header = "Command" in cells or "Description" in cells or "Component" in cells or "Responsibility" in cells
                row_type = 'th' if is_header else 'td'
                row_str = '<tr>' + ''.join(f'<{row_type}>{cell}</{row_type}>' for cell in cells) + '</tr>'
                table_html.append(row_str)
        else:
            if inside_table:
                inside_table = False
                table_html.append('</table></div>')
                processed_lines.append("\n".join(table_html))
                table_html = []
            processed_lines.append(line)
            
    if inside_table:
        table_html.append('</table></div>')
        processed_lines.append("\n".join(table_html))

    html = "\n".join(processed_lines)

    # Clean un-nested hash link selectors
    def fix_pipe_wikilink(match):
        label, page = match.group(1).strip(), match.group(2).strip()
        target = page.replace(" ", "-").replace("_", "-").lower()
        return f'<a href="#{target}" onclick="showPage(\x27{target}\x27)">{label}</a>'
    html = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", fix_pipe_wikilink, html)

    def fix_simple_wikilink(match):
        page = match.group(1).strip()
        target = page.replace(" ", "-").replace("_", "-").lower()
        return f'<a href="#{target}" onclick="showPage(\x27{target}\x27)">{page}</a>'
    html = re.sub(r"\[\[([^\]]+)\]\]", fix_simple_wikilink, html)

    html = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html, flags=re.M)
    html = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html, flags=re.M)
    html = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html, flags=re.M)
    html = re.sub(r"`(.*?)`", r"<code>\1</code>", html)
    html = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', html)
    html = re.sub(r"^\* (.*?)$", r"<li>\1</li>", html, flags=re.M)
    html = re.sub(r"^- (.*?)$", r"<li>\1</li>", html, flags=re.M)
    
    paragraphs = html.split("\n\n")
    for i, p in enumerate(paragraphs):
        p_stripped = p.strip()
        if not p_stripped.startswith("<") and not p_stripped.startswith("<!--") and p_stripped:
            paragraphs[i] = f"<p>{p_stripped.replace('\n', '<br>')}</p>"
    html = "\n".join(paragraphs)

    for idx, block_content in enumerate(code_blocks):
        if "|" in block_content or "/" in block_content or "\\" in block_content:
            replacement = f'<pre class="diagram-block">{block_content}</pre>'
        else:
            replacement = f'<pre><code>{block_content}</code></pre>'
        html = html.replace(f"<!--CODEBLOCK_{idx}-->", replacement)

    return html

desired_order = ["Home", "Installation", "Configuration", "vbuild", "viridium", "Architecture", "Boot and UEFI", "Development", "Networking", "Package management", "Troubleshooting", "FAQ"]
available_files = os.listdir(".")
file_mapping = {f.replace(".md", "").replace("-", " ").replace("_", " ").strip().lower(): f for f in available_files if f.endswith(".md")}

sidebar_links = []
for title in desired_order:
    norm_title = title.lower()
    matched_filename = file_mapping.get(norm_title)
    if not matched_filename and title == "Architecture": 
        matched_filename = file_mapping.get("archetecture")
    if matched_filename:
        sidebar_links.append((title, matched_filename.replace(".md", "").lower(), matched_filename))

sidebar_html = ""
content_blocks_html = ""

for title, target_id, matched_filename in sidebar_links:
    sidebar_html += f'<li><a href="#{target_id}" id="link-{target_id}" onclick="showPage(\x27{target_id}\x27)">{title}</a></li>\n'
    
    with open(matched_filename, "r", encoding="utf-8") as file: 
        parsed_content = md_to_html(file.read())
    
    content_blocks_html += f'<div id="page-{target_id}" class="wiki-page-content" style="display:none;">{parsed_content}</div>\n'

# Hardcode output directly into a clean root index.html asset template block
master_template = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Viridium Linux Wiki</title><style>:root {{ --bg-main: #141210; --bg-sidebar: #1f1a16; --text-main: #f5f2eb; --text-muted: #bcada1; --accent: #ff8838; --accent-light: #ffd4b8; --border: #382414; }} body {{ font-family: system-ui, sans-serif; margin: 0; display: flex; background: var(--bg-main); color: var(--text-main); min-height: 100vh; line-height: 1.6; }} aside {{ width: 280px; background: var(--bg-sidebar); border-right: 1px solid var(--border); padding: 25px 20px; position: fixed; height: 100vh; display: flex; flex-direction: column; box-sizing: border-box; }} .sidebar-content {{ flex: 1; overflow-y: auto; }} aside h2 {{ font-size: 1.15rem; margin-top: 0; display: flex; align-items: center; gap: 8px; color: var(--accent-light); font-weight: 600; text-transform: uppercase; }} aside ul {{ list-style: none; padding: 0; margin: 0; }} aside li {{ margin-bottom: 8px; }} aside a {{ color: var(--text-muted); text-decoration: none; font-size: 0.95rem; display: block; padding: 6px 10px; border-radius: 6px; cursor: pointer; }} aside a:hover, aside a.active-link {{ color: var(--accent); background: rgba(255, 136, 56, 0.08); font-weight: bold; }} .download-btn {{ display: flex; align-items: center; justify-content: center; gap: 10px; background: linear-gradient(135deg, #ff8838 0%, #d45d00 100%); color: #141210 !important; font-weight: bold; text-decoration: none; padding: 12px; border-radius: 8px; margin-top: 20px; font-size: 0.95rem; text-align: center; }} main {{ flex: 1; padding: 40px 60px; margin-left: 280px; max-width: 850px; }} h1 {{ color: var(--accent); font-size: 2.2rem; margin-top: 0; background: linear-gradient(135deg, #ff8838 0%, #ffd4b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }} h2 {{ color: var(--accent); font-size: 1.6rem; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-top: 40px; }} code {{ background: rgba(255, 136, 56, 0.1); color: var(--accent-light); padding: 3px 6px; border-radius: 4px; font-family: monospace; border: 1px solid rgba(255, 136, 56, 0.2); }} pre {{ background: #0c0a09; padding: 18px; border-radius: 8px; border: 1px solid var(--border); overflow-x: auto; margin: 20px 0; }} pre code {{ color: var(--text-main); background: none; padding: 0; }} .diagram-block {{ background: #0c0a09; color: var(--text-main); font-family: monospace; line-height: 1.4; border: 1px solid var(--border); padding: 15px; border-radius: 8px; white-space: pre; overflow-x: auto; margin: 20px 0; }} .diagram-block a {{ border-bottom: none; }} main a {{ color: var(--accent); text-decoration: none; border-bottom: 1px dashed var(--accent); }} main a:hover {{ border-bottom-style: solid; }} p {{ margin: 16px 0; color: #e4ded5; }} .table-container {{ overflow-x: auto; margin: 25px 0; border: 1px solid var(--border); border-radius: 8px; }} table {{ width: 100%; border-collapse: collapse; background: var(--bg-sidebar); }} th {{ background: #1a1512; color: var(--accent); padding: 12px 16px; border-bottom: 2px solid var(--border); text-align: left; }} td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); color: #e4ded5; text-align: left; }}</style></head><body><aside><div class="sidebar-content"><h2>Viridium Wiki</h2><ul>{sidebar_html}</ul></div><a href="https://github.com" class="download-btn">INSTALL VIRIDIUM ISO</a></aside><main>{content_blocks_html}</main><script>function showPage(pageId){{document.querySelectorAll(".wiki-page-content").forEach(p=>p.style.display="none");document.querySelectorAll("aside a").forEach(l=>l.classList.remove("active-link"));const targetPage=document.getElementById("page-"+pageId);if(targetPage){{targetPage.style.display="block";document.getElementById("link-"+pageId).classList.add("active-link");window.scrollTo(0,0);}}}}window.addEventListener("DOMContentLoaded",()=>{{const hash=window.location.hash.replace("#","")||"home";showPage(hash);}});window.addEventListener("hashchange",()=>{{const hash=window.location.hash.replace("#","")||"home";showPage(hash);}});</script></body></html>"""

with open("../Viridium-Linux/index.html", "w", encoding="utf-8") as f: 
    f.write(master_template)

print("🎉 Complete! Perfect unified single-file index compiled directly to your repository folder.")
