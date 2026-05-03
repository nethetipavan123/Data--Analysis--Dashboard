"""
app.py — CrashRespond Emergency Response Tool
Run: streamlit run app.py
Make sure you have run database.py first!
"""

import streamlit as st
import sqlite3
import time
import json
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CrashRespond",
    page_icon="🚨",
    layout="wide",
)

DB_FILE = "emergency_data.db"

# ── Check DB exists ───────────────────────────────────────────────────────────
if not os.path.exists(DB_FILE):
    st.error("⚠️ Database not found! Please run: `python database.py` first.")
    st.stop()

# ── Database functions ────────────────────────────────────────────────────────
def get_connection():
    return sqlite3.connect(DB_FILE)

def fetch_all_countries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, flag, region, emergency, ambulance, police, fire FROM countries")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: {
        "flag": row[1], "region": row[2],
        "emergency": row[3], "ambulance": row[4],
        "police": row[5], "fire": row[6]
    } for row in rows}

def fetch_all_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, label, icon FROM categories")
    rows = cursor.fetchall()
    conn.close()
    return [("all", "📋 All")] + [(r[0], f"{r[2]} {r[1]}") for r in rows]

def fetch_services(category="all", search=""):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, type, name, dist, phone, eta, rating, avail, priority, map_x, map_y FROM services WHERE 1=1"
    params = []

    if category != "all":
        query += " AND type = ?"
        params.append(category)

    if search:
        query += " AND (LOWER(name) LIKE ? OR id IN (SELECT service_id FROM service_tags WHERE LOWER(tag) LIKE ?))"
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])

    query += " ORDER BY dist ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    services = []
    for row in rows:
        sid = row[0]
        services.append({
            "id": sid, "type": row[1], "name": row[2],
            "dist": row[3], "phone": row[4], "eta": row[5],
            "rating": row[6], "avail": row[7], "priority": row[8],
            "map_x": row[9], "map_y": row[10],
            "tags": fetch_tags(sid),
            "caps": fetch_caps(sid),
        })
    return services

def fetch_tags(service_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tag FROM service_tags WHERE service_id = ?", (service_id,))
    tags = [r[0] for r in cursor.fetchall()]
    conn.close()
    return tags

def fetch_caps(service_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT capability FROM service_capabilities WHERE service_id = ?", (service_id,))
    caps = [r[0] for r in cursor.fetchall()]
    conn.close()
    return caps

def fetch_service_by_id(sid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, type, name, dist, phone, eta, rating, avail, priority, map_x, map_y
        FROM services WHERE id = ?
    """, (sid,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "type": row[1], "name": row[2],
        "dist": row[3], "phone": row[4], "eta": row[5],
        "rating": row[6], "avail": row[7], "priority": row[8],
        "map_x": row[9], "map_y": row[10],
        "tags": fetch_tags(row[0]),
        "caps": fetch_caps(row[0]),
    }

def get_db_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM services WHERE type='hospital'")
    h = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM services WHERE type='ambulance'")
    a = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM services WHERE type='police'")
    p = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM services")
    total = cursor.fetchone()[0]
    conn.close()
    return h, a, p, total

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background:#0a0e1a; color:#f1f5f9; }
[data-testid="stSidebar"]          { background:#111827; border-right:1px solid #1e2d45; }
[data-testid="stHeader"]           { background:#111827; }

.em-card {
    background:#161d2e; border:1px solid #1e2d45;
    border-radius:10px; padding:14px; margin-bottom:10px;
}
.em-card.critical { border-left:4px solid #ef4444; }
.em-card.warning  { border-left:4px solid #f59e0b; }
.em-card.safe     { border-left:4px solid #10b981; }
.em-card-name     { font-weight:600; font-size:14px; color:#f1f5f9; }

.em-dist-close { color:#10b981; font-weight:700; font-size:12px; }
.em-dist-med   { color:#f59e0b; font-weight:700; font-size:12px; }
.em-dist-far   { color:#ef4444; font-weight:700; font-size:12px; }

.em-tag {
    background:#1e2d45; padding:2px 7px; border-radius:4px;
    font-size:11px; color:#94a3b8; margin-right:4px;
}
.avail-24h { background:rgba(59,130,246,0.15); color:#3b82f6; padding:2px 6px; border-radius:4px; font-size:11px; }
.avail-yes { background:rgba(16,185,129,0.15); color:#10b981; padding:2px 6px; border-radius:4px; font-size:11px; }
.avail-no  { background:rgba(239,68,68,0.15);  color:#ef4444; padding:2px 6px; border-radius:4px; font-size:11px; }

.detail-stat {
    background:#161d2e; border-radius:8px;
    padding:10px; text-align:center;
}
.detail-stat-label { font-size:10px; color:#64748b; text-transform:uppercase; letter-spacing:1px; }
.detail-stat-val   { font-size:17px; font-weight:700; color:#f1f5f9; }

.status-bar {
    background:#0f1929; padding:8px 16px;
    display:flex; gap:18px; align-items:center;
    font-size:12px; border-bottom:1px solid #1e2d45;
    border-radius:8px; margin-bottom:12px;
}
.status-live { color:#10b981; font-weight:600; }
.status-item { color:#94a3b8; }

.gh-bar {
    background:linear-gradient(135deg,rgba(245,158,11,0.12),rgba(239,68,68,0.08));
    border:1px solid rgba(245,158,11,0.2); border-radius:8px;
    padding:10px 16px; display:flex; align-items:center; gap:12px;
    margin-bottom:12px;
}
.gh-timer { font-size:20px; font-weight:700; color:#f59e0b; }

.map-container {
    background:#111827; border:1px solid #1e2d45;
    border-radius:10px; padding:16px; text-align:center;
}
.map-legend {
    background:#161d2e; border-radius:8px;
    padding:10px 14px; display:inline-block; text-align:left;
}
.legend-item { font-size:12px; color:#94a3b8; margin-bottom:4px; }

.db-badge {
    background:rgba(139,92,246,0.15); color:#8b5cf6;
    border:1px solid rgba(139,92,246,0.3);
    padding:2px 8px; border-radius:4px; font-size:11px;
}
</style>
""", unsafe_allow_html=True)

# ── Load data from DB ─────────────────────────────────────────────────────────
COUNTRIES   = fetch_all_countries()
CATEGORIES  = fetch_all_categories()
hosp_count, amb_count, police_count, total_count = get_db_stats()

# ── Session state ─────────────────────────────────────────────────────────────
if "country"     not in st.session_state: st.session_state.country     = "India"
if "category"    not in st.session_state: st.session_state.category    = "all"
if "selected_id" not in st.session_state: st.session_state.selected_id = None
if "gh_active"   not in st.session_state: st.session_state.gh_active   = False
if "gh_start"    not in st.session_state: st.session_state.gh_start    = None
if "show_sos"    not in st.session_state: st.session_state.show_sos    = False
if "toast"       not in st.session_state: st.session_state.toast       = None

# ── Helpers ───────────────────────────────────────────────────────────────────
TYPE_ICONS = {
    "hospital": "🏥", "ambulance": "🚑", "police": "🚔",
    "towing": "🚗", "puncture": "🔧", "petrol": "⛽"
}
TYPE_COLORS = {
    "hospital": "#8b5cf6", "ambulance": "#10b981", "police": "#3b82f6",
    "towing": "#f59e0b", "puncture": "#06b6d4", "petrol": "#06b6d4"
}

def dist_class(d):
    return "em-dist-close" if d < 1.5 else ("em-dist-med" if d < 3 else "em-dist-far")

def avail_label(a):
    return "24/7" if a == "24h" else a

def avail_cls(a):
    return "avail-24h" if a == "24h" else ("avail-yes" if a == "yes" else "avail-no")

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
col_logo, col_loc, col_sos = st.columns([3, 4, 1])
with col_logo:
    st.markdown("### 🚨 **CrashRespond.**")
with col_loc:
    st.markdown(
        "<div style='color:#94a3b8;font-size:12px;padding-top:8px'>"
        "📍 Mumbai, Maharashtra &nbsp;&nbsp;"
        "<span style='color:#10b981'>Demo location</span> &nbsp;&nbsp;"
        "<span class='db-badge'>🗄️ SQLite DB</span>"
        "</div>",
        unsafe_allow_html=True
    )
with col_sos:
    if st.button("🆘 SOS", type="primary", use_container_width=True):
        st.session_state.show_sos = True

st.divider()

# ── Status bar ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="status-bar">
  <span class="status-live">● Live</span>
  <span class="status-item">📍 19.076, 72.877</span>
  <span class="status-item">🏥 {hosp_count} hospitals</span>
  <span class="status-item">🚑 {amb_count} ambulances</span>
  <span class="status-item">🚔 {police_count} police</span>
  <span class="status-item">📊 {total_count} total services</span>
  <span style="margin-left:auto;background:rgba(245,158,11,0.15);color:#f59e0b;
        padding:2px 8px;border-radius:4px;font-size:11px">📦 Offline Ready</span>
</div>
""", unsafe_allow_html=True)

# ── Country switcher ──────────────────────────────────────────────────────────
st.markdown("**Region:**")
ccols = st.columns(len(COUNTRIES))
for i, (cname, cdata) in enumerate(COUNTRIES.items()):
    with ccols[i]:
        active = st.session_state.country == cname
        if st.button(f"{cdata['flag']} {cname}", key=f"country_{cname}",
                     type="primary" if active else "secondary",
                     use_container_width=True):
            st.session_state.country = cname
            st.session_state.toast   = f"Switched to {cname} — emergency numbers updated"
            st.rerun()

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
#  SOS MODAL
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.show_sos:
    country = COUNTRIES[st.session_state.country]
    nearest = fetch_services(category="hospital")

    st.error("## 🆘 EMERGENCY SOS")
    st.markdown("Quick-call the nearest emergency service. Your location is ready to share.")
    st.success("📍 Location ready — Mumbai, Maharashtra")

    sos_items = [
        ("🚑", "Ambulance",        country["ambulance"]),
        ("🚔", "Police",           country["police"]),
        ("🏥", "Nearest Hospital", nearest[0]["phone"] if nearest else "108"),
        ("🔥", "Fire & Rescue",    country["fire"]),
    ]
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, (icon, label, num) in zip([sc1, sc2, sc3, sc4], sos_items):
        with col:
            st.markdown(
                f"<div style='text-align:center;background:#161d2e;border:1px solid #1e2d45;"
                f"border-radius:10px;padding:14px'>"
                f"<div style='font-size:28px'>{icon}</div>"
                f"<div style='font-weight:700;font-size:13px;color:#f1f5f9'>{label}</div>"
                f"<div style='font-size:12px;color:#64748b'>{num}</div></div>",
                unsafe_allow_html=True
            )
            if st.button(f"📞 {num}", key=f"sos_{label}", use_container_width=True):
                st.session_state.toast   = f"Calling {label} — {num}"
                st.session_state.show_sos = False
                st.rerun()

    if st.button("✕ Cancel — I'm Safe", use_container_width=True):
        st.session_state.show_sos = False
        st.rerun()

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
#  GOLDEN HOUR TIMER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.gh_active and st.session_state.gh_start:
    elapsed   = int(time.time() - st.session_state.gh_start)
    remaining = max(0, 3600 - elapsed)
    mm, ss    = divmod(remaining, 60)
    pct       = remaining / 3600

    st.markdown(f"""
    <div class="gh-bar">
      <span style='color:#f59e0b;font-weight:500'>⏱ Golden Hour</span>
      <div style='flex:1;height:6px;background:#1e2d45;border-radius:3px;overflow:hidden'>
        <div style='height:100%;width:{pct*100:.1f}%;
             background:linear-gradient(90deg,#10b981,#f59e0b,#ef4444);border-radius:3px'>
        </div>
      </div>
      <span class="gh-timer">{mm:02d}:{ss:02d}</span>
    </div>
    """, unsafe_allow_html=True)

    if remaining == 0:
        st.session_state.gh_active = False

# ── Toast ─────────────────────────────────────────────────────────────────────
if st.session_state.toast:
    st.success(st.session_state.toast)
    st.session_state.toast = None

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([1, 2])

# ════════ LEFT — Service List ════════════════════════════════════════════════
with left_col:
    search = st.text_input("🔍 Search by name, tag, or type...", key="search_input")

    # Category tabs
    cat_cols = st.columns(len(CATEGORIES))
    for i, (cid, clabel) in enumerate(CATEGORIES):
        with cat_cols[i]:
            active = st.session_state.category == cid
            if st.button(clabel, key=f"cat_{cid}",
                         type="primary" if active else "secondary",
                         use_container_width=True):
                st.session_state.category = cid
                st.rerun()

    # Fetch from DB
    filtered = fetch_services(
        category=st.session_state.category,
        search=search
    )

    st.markdown(f"**Nearby Emergency Services** — {len(filtered)} found")

    for s in filtered:
        dist_c    = dist_class(s["dist"])
        tags_html = " ".join(f'<span class="em-tag">{t}</span>' for t in s["tags"][:2])
        avail_h   = f'<span class="{avail_cls(s["avail"])}">{avail_label(s["avail"])}</span>'
        icon      = TYPE_ICONS.get(s["type"], "📍")

        st.markdown(f"""
        <div class="em-card {s['priority']}">
          <div style='display:flex;justify-content:space-between;align-items:flex-start'>
            <div class='em-card-name'>{icon} {s['name']}</div>
            <div class='{dist_c}'>{s['dist']} km</div>
          </div>
          <div style='margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;align-items:center;font-size:11px'>
            {avail_h} {tags_html}
            <span style='color:#f59e0b'>★ {s['rating']}</span>
            <span style='color:#64748b'>ETA {s['eta']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        bcol1, bcol2 = st.columns([3, 1])
        with bcol1:
            if st.button(f"📞 Call {s['phone']}", key=f"call_{s['id']}", use_container_width=True):
                st.session_state.toast = f"Calling {s['name']} — {s['phone']}"
                st.rerun()
        with bcol2:
            if st.button("🗺", key=f"nav_{s['id']}", use_container_width=True):
                st.session_state.toast = f"Navigating to {s['name']}"
                st.rerun()

        if st.button(f"ℹ Details", key=f"details_{s['id']}", use_container_width=True):
            st.session_state.selected_id = s["id"]
            st.rerun()

# ════════ RIGHT — Map + Detail ════════════════════════════════════════════════
with right_col:

    # Map controls
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        if st.button("⏱ Start Golden Hour", use_container_width=True):
            st.session_state.gh_active = True
            st.session_state.gh_start  = time.time()
            st.session_state.toast     = "Golden hour timer started — coordinate care now"
            st.rerun()
    with mc2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.toast = f"Data refreshed — {total_count} services loaded from DB"
            st.rerun()
    with mc3:
        country_info = COUNTRIES[st.session_state.country]
        export_data  = {
            "country":          st.session_state.country,
            "total_services":   total_count,
            "emergency_numbers": {
                "emergency": country_info["emergency"],
                "ambulance": country_info["ambulance"],
                "police":    country_info["police"],
                "fire":      country_info["fire"],
            },
            "services": [
                {"name": s["name"], "type": s["type"],
                 "phone": s["phone"], "dist": s["dist"], "eta": s["eta"]}
                for s in fetch_services()
            ]
        }
        st.download_button(
            "📤 Export JSON",
            data=json.dumps(export_data, indent=2),
            file_name="emergency_data_export.json",
            mime="application/json",
            use_container_width=True,
        )
    with mc4:
        if st.button("📍 Share Location", use_container_width=True):
            st.session_state.toast = "Location shared: Mumbai, Maharashtra (19.076, 72.877)"
            st.rerun()

    # ── SVG Map ───────────────────────────────────────────────────────────────
    all_services  = fetch_services()
    filtered_ids  = {s["id"] for s in filtered}

    markers_svg = ""
    for s in all_services:
        opacity = 1.0 if s["id"] in filtered_ids else 0.18
        icon    = TYPE_ICONS.get(s["type"], "📍")
        col     = TYPE_COLORS.get(s["type"], "#94a3b8")
        x, y    = s["map_x"], s["map_y"]
        sel_stroke = 'stroke="#fff" stroke-width="2.5"' if s["id"] == st.session_state.selected_id else ""

        markers_svg += f"""
        <g opacity="{opacity}">
          <circle cx="{x}" cy="{y}" r="18" fill="{col}" opacity="0.15"/>
          <circle cx="{x}" cy="{y}" r="11" fill="{col}" {sel_stroke}/>
          <text x="{x}" y="{y+4}" text-anchor="middle" font-size="11">{icon}</text>
          <rect  x="{x-26}" y="{y-30}" width="52" height="15" rx="3" fill="#111827" opacity="0.85"/>
          <text  x="{x}" y="{y-20}" text-anchor="middle" font-size="9"
                 fill="#94a3b8" font-family="sans-serif">{s['dist']}km</text>
        </g>"""

    svg_map = f"""
    <div class="map-container">
    <svg viewBox="0 0 700 450" xmlns="http://www.w3.org/2000/svg" width="100%">
      <rect width="700" height="450" fill="#0a0e1a" rx="8"/>
      <!-- Roads -->
      <line x1="0"   y1="225" x2="700" y2="225" stroke="#1e2d45" stroke-width="8"/>
      <line x1="350" y1="0"   x2="350" y2="450" stroke="#1e2d45" stroke-width="8"/>
      <line x1="0"   y1="80"  x2="700" y2="350" stroke="#161d2e" stroke-width="5"/>
      <line x1="0"   y1="350" x2="700" y2="80"  stroke="#161d2e" stroke-width="5"/>
      <line x1="0"   y1="225" x2="700" y2="225" stroke="#2a3d5a" stroke-width="2" stroke-dasharray="20,15"/>
      <text x="10"  y="220" fill="#2a3d5a" font-size="9" font-family="sans-serif">NH 48</text>
      <text x="345" y="15"  fill="#2a3d5a" font-size="9" font-family="sans-serif">NH 66</text>
      <!-- User location -->
      <circle cx="350" cy="225" r="24" fill="rgba(59,130,246,0.08)"/>
      <circle cx="350" cy="225" r="15" fill="rgba(59,130,246,0.15)"/>
      <circle cx="350" cy="225" r="7"  fill="#3b82f6"/>
      <circle cx="350" cy="225" r="3"  fill="#fff"/>
      <text   x="362" y="214" fill="#3b82f6" font-size="10" font-family="sans-serif" font-weight="600">YOU</text>
      <!-- Markers -->
      {markers_svg}
    </svg>
    <div class="map-legend" style="margin-top:10px">
      <div class="legend-item">🟣 Hospitals / Trauma</div>
      <div class="legend-item">🟢 Ambulance Services</div>
      <div class="legend-item">🔵 Police Stations</div>
      <div class="legend-item">🟡 Towing / Rescue</div>
      <div class="legend-item">🩵 Petrol / Puncture</div>
    </div>
    </div>
    """
    st.markdown(svg_map, unsafe_allow_html=True)

    # ── Detail Panel ──────────────────────────────────────────────────────────
    if st.session_state.selected_id:
        sel = fetch_service_by_id(st.session_state.selected_id)
        if sel:
            st.divider()
            dh1, dh2 = st.columns([4, 1])
            with dh1:
                icon = TYPE_ICONS.get(sel["type"], "📍")
                st.markdown(f"#### {icon} {sel['name']}")
            with dh2:
                if st.button("✕ Close", key="close_detail"):
                    st.session_state.selected_id = None
                    st.rerun()

            d1, d2, d3 = st.columns(3)
            for col, label, val in [
                (d1, "Distance", f"{sel['dist']} km"),
                (d2, "ETA",      sel["eta"]),
                (d3, "Rating",   f"★ {sel['rating']}"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="detail-stat">
                      <div class="detail-stat-label">{label}</div>
                      <div class="detail-stat-val">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(
                "**Capabilities:** " + " &nbsp; ".join(
                    f'<span style="background:#1e2d45;padding:4px 10px;'
                    f'border-radius:20px;font-size:12px;color:#94a3b8">{c}</span>'
                    for c in sel["caps"]
                ),
                unsafe_allow_html=True
            )

            da1, da2, da3 = st.columns(3)
            with da1:
                if st.button(f"📞 Call {sel['phone']}", key="dp_call",
                             use_container_width=True, type="primary"):
                    st.session_state.toast = f"Calling {sel['name']} — {sel['phone']}"
                    st.rerun()
            with da2:
                if st.button("🗺 Navigate", key="dp_nav", use_container_width=True):
                    st.session_state.toast = "Navigation started in your maps app"
                    st.rerun()
            with da3:
                if st.button("📲 Share", key="dp_share", use_container_width=True):
                    st.session_state.toast = "Location shared with emergency contacts"
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    "<div style='text-align:center;color:#64748b;font-size:11px'>"
    "🚨 CrashRespond — Road Accident Emergency Response Tool &nbsp;|&nbsp; "
    "Powered by SQLite &nbsp;|&nbsp; Works Offline &nbsp;|&nbsp; "
    "Data sourced from structured database"
    "</div>",
    unsafe_allow_html=True
)
