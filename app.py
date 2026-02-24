import streamlit as st
import requests
import uuid
import json
import time

# =====================================================
# V19 NODE NETWORK — AUTO SYNC + SUBSCRIPTIONS
# =====================================================

st.set_page_config(page_title="TTU Node V19", layout="wide")

# -----------------------------
# SAFE JSON HELPERS
# -----------------------------

def now():
    return float(time.time())

def safe_json(data):
    """Guarantee JSON serializable"""
    return json.loads(json.dumps(data))


# -----------------------------
# INIT NODE
# -----------------------------

if "NODE" not in st.session_state:

    st.session_state.NODE = {
        "ID": str(uuid.uuid4()),
        "CREATED": now(),
        "TUNNELS": {},
        "SUBSCRIPTIONS": {},   # nodes we follow
        "LAST_SYNC": 0.0
    }

NODE = st.session_state.NODE


# -----------------------------
# CREATE TUNNEL
# -----------------------------

def create_tunnel():

    tid = str(uuid.uuid4())

    NODE["TUNNELS"][tid] = {
        "id": tid,
        "created": now(),
        "messages": [],
        "version": 1
    }


# -----------------------------
# ADD MESSAGE
# -----------------------------

def add_message(tid, msg):

    tunnel = NODE["TUNNELS"][tid]

    tunnel["messages"].append({
        "msg": msg,
        "time": now()
    })

    tunnel["version"] += 1


# -----------------------------
# MERGE TUNNELS (AUTO FUSION)
# -----------------------------

def merge_tunnels(remote):

    for tid, rtunnel in remote.items():

        if tid not in NODE["TUNNELS"]:
            NODE["TUNNELS"][tid] = safe_json(rtunnel)
            continue

        local = NODE["TUNNELS"][tid]

        if rtunnel["version"] > local["version"]:
            NODE["TUNNELS"][tid] = safe_json(rtunnel)


# -----------------------------
# SUBSCRIBE NODE
# -----------------------------

def subscribe_node(url):

    NODE["SUBSCRIPTIONS"][url] = {
        "url": url,
        "added": now(),
        "last_seen": 0.0
    }


# -----------------------------
# FETCH REMOTE NODE
# -----------------------------

def fetch_remote(url):

    try:
        r = requests.get(url + "?api=state", timeout=3)

        if r.status_code == 200:
            return r.json()

    except:
        pass

    return None


# -----------------------------
# AUTO SYNC ENGINE
# -----------------------------

def auto_sync():

    if now() - NODE["LAST_SYNC"] < 5:
        return

    for url in list(NODE["SUBSCRIPTIONS"].keys()):

        data = fetch_remote(url)

        if not data:
            continue

        merge_tunnels(data["TUNNELS"])

        NODE["SUBSCRIPTIONS"][url]["last_seen"] = now()

    NODE["LAST_SYNC"] = now()


# -----------------------------
# API MODE (NODE EXPORT)
# -----------------------------

query = st.query_params

if "api" in query and query["api"] == "state":

    st.json(safe_json({
        "ID": NODE["ID"],
        "TUNNELS": NODE["TUNNELS"]
    }))

    st.stop()


# -----------------------------
# AUTO SYNC LOOP
# -----------------------------

auto_sync()


# =====================================================
# UI
# =====================================================

st.title("🌐 TTU NODE V19 — Sovereign Network")

st.markdown("Node ID:")
st.code(NODE["ID"])


# -----------------------------
# CREATE TUNNEL
# -----------------------------

if st.button("➕ Create Tunnel"):
    create_tunnel()


# -----------------------------
# SUBSCRIBE UI
# -----------------------------

st.subheader("🔗 Subscribe to another Node")

url = st.text_input(
    "Node URL (Streamlit app link)",
    placeholder="https://xxxxx.streamlit.app"
)

if st.button("Subscribe") and url:
    subscribe_node(url)


# -----------------------------
# SHOW SUBSCRIPTIONS
# -----------------------------

st.subheader("📡 Subscriptions")

for u, info in NODE["SUBSCRIPTIONS"].items():
    st.write(
        f"✅ {u} | last seen: "
        f"{round(now()-info['last_seen'],1)}s ago"
    )


# -----------------------------
# DISPLAY TUNNELS
# -----------------------------

st.subheader("🧠 Tunnels")

for tid, tunnel in NODE["TUNNELS"].items():

    with st.expander(f"Tunnel {tid[:8]} | v{tunnel['version']}"):

        for m in tunnel["messages"]:
            st.write("•", m["msg"])

        msg = st.text_input(
            "Message",
            key=f"msg_{tid}"
        )

        if st.button("Send", key=f"send_{tid}"):
            add_message(tid, msg)
            st.rerun()


# -----------------------------
# DEBUG PANEL
# -----------------------------

with st.expander("⚙️ Debug State"):
    st.json(safe_json(NODE))
