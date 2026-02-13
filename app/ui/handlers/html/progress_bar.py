# app/ui/handlers/html/progress_bar.py
#
# Progress bar renderer
#

def render_progress_bar(width: str, color: str) -> str:
    return f"""
    <div style="width:100%; background:#e5e7eb; border-radius:8px; overflow:hidden;">
      <div style="
        width:{width};
        height:12px;
        background:{color};
        transition: width 0.4s ease, background-color 0.4s ease;
      "></div>
    </div>
    """
