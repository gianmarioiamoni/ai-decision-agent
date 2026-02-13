# app/ui/handlers/html/tokens_status_badge.py
#
# Tokens status badge renderer
#

def render_token_status_badge(token_status: dict) -> str:
    return f"""
        <div style="
            padding:8px;
            border-radius:8px;
            background:#1f2937;
            color:#e5e7eb;
            font-size:12px;
        ">
        <b>Token Usage</b><br>
        Session: {token_status['session_used']} / {token_status['session_limit']}<br>
        Daily: {token_status['daily_used']} / {token_status['daily_limit']}
        </div>
    """
