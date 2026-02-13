# app/ui/handlers/html/tokens_status_badge.py
#
# Tokens status badge renderer
#

def render_token_status_badge(token_status: dict) -> str:
    
    session_used = token_status["session_used"]
    session_limit = token_status["session_limit"]
    daily_used = token_status["daily_used"]
    daily_limit = token_status["daily_limit"]

    session_pct = session_used / session_limit if session_limit else 0
    daily_pct = daily_used / daily_limit if daily_limit else 0

    def get_color(pct: float) -> str:
        if pct > 0.8:
            return "#dc2626"  # red
        elif pct > 0.6:
            return "#f59e0b"  # amber
        else:
            return "#22c55e"  # green

    session_color = get_color(session_pct)
    daily_color = get_color(daily_pct)
    
    
    return f"""
        <div style="
            padding:10px;
            border-radius:10px;
            background:#111827;
            font-size:12px;
            color:#e5e7eb;
            line-height:1.5;
        ">
        <b>Token Usage</b><br><br>
        <span style="color:{session_color}; font-weight:600;">
            Session: {session_used:,} / {session_limit:,} ({session_pct:.0%})
        </span><br>
        <span style="color:{daily_color}; font-weight:600;">
            Daily: {daily_used:,} / {daily_limit:,} ({daily_pct:.0%})
        </span>
    </div>
    """
