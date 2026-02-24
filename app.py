import streamlit as st
from cryptography.fernet import Fernet
import hashlib, time, uuid, base64, json

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="GEN-Z GABON • FREE-KONGOSSA V18",
    page_icon="🇬🇦",
    layout="centered"
)

# =====================================================
# NODE DATABASE (LOCAL SOVEREIGN NODE)
# =====================================================
@st.cache_resource
def NODE_INIT():
    return {
        "TUNNELS": {},
        "CHAIN": {},
        "PRESENCE": {},
        "PUBLIC": []
    }

NODE = NODE_INIT()

# =====================================================
# SOVEREIGN CRYPTO ENGINE
# =====================================================
class SOVEREIGN:

    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:20]

    @staticmethod
    def key(secret):
        k = hashlib.pbkdf2_hmac(
            "sha256",
            secret.encode(),
            b"GABON-SOVEREIGN",
            150000
        )
        return base64.urlsafe_b64encode(k[:32])

    @staticmethod
    def encrypt(secret, data):
        f = Fernet(SOVEREIGN.key(secret))
        c = f.encrypt(data)
        n = len(c)
        return [c[:n//3], c[n//3:2*n//3], c[2*n//3:]]

    @staticmethod
    def decrypt(secret, frags):
        f = Fernet(SOVEREIGN.key(secret))
        return f.decrypt(b"".join(frags))

# =====================================================
# SESSION
# =====================================================
if "uid" not in st.session_state:
    nick = st.text_input("Pseudo GEN-Z 🇬🇦")
    if nick:
        st.session_state.uid = f"🇬🇦{nick}#{uuid.uuid4().hex[:3]}"
        st.rerun()
    st.stop()

# =====================================================
# TUNNEL AUTH
# =====================================================
secret = st.text_input("Code Tunnel", type="password")

if not secret:
    st.stop()

sid = SOVEREIGN.tunnel(secret)

if sid not in NODE["TUNNELS"]:
    NODE["TUNNELS"][sid] = []
    NODE["CHAIN"][sid] = b"GENESIS"

# =====================================================
# PRESENCE SYSTEM
# =====================================================
now = time.time()
NODE["PRESENCE"][st.session_state.uid] = now

NODE["PRESENCE"] = {
    u: t for u, t in NODE["PRESENCE"].items()
    if now - t < 30
}

active = len(NODE["PRESENCE"])

st.title("🇬🇦 FREE-KONGOSSA — SOVEREIGN V18")
st.caption(f"🟢 {active} actifs | Node Local")

# =====================================================
# DISPLAY MESSAGES
# =====================================================
for m in reversed(NODE["TUNNELS"][sid]):
    try:
        raw = SOVEREIGN.decrypt(secret, m["f"])
        st.caption(m["u"])

        if m["t"] == "text":
            st.write(raw.decode(errors="ignore"))
        elif "image" in m["t"]:
            st.image(raw)
        elif "video" in m["t"]:
            st.video(raw)
        else:
            st.audio(raw)
    except:
        pass

# =====================================================
# PUSH MESSAGE
# =====================================================
def push(data, typ):

    frags = SOVEREIGN.encrypt(secret, data)

    prev = NODE["CHAIN"][sid]
    chain = hashlib.sha256(prev + data).digest()
    NODE["CHAIN"][sid] = chain

    NODE["TUNNELS"][sid].append({
        "u": st.session_state.uid,
        "f": frags,
        "t": typ,
        "ts": time.time()
    })

# =====================================================
# SEND UI
# =====================================================
mode = st.radio("Signal", ["Texte", "Média", "Vocal"], horizontal=True)

if mode == "Texte":
    txt = st.text_area("Message")
    if st.button("Envoyer"):
        push(txt.encode(), "text")
        st.rerun()

elif mode == "Média":
    f = st.file_uploader("Upload")
    if f and st.button("Diffuser"):
        push(f.getvalue(), f.type)
        st.rerun()

elif mode == "Vocal":
    a = st.audio_input("Micro")
    if a and st.button("Vocal"):
        push(a.getvalue(), "audio/wav")
        st.rerun()

# =====================================================
# SYNC EXPORT / IMPORT (FIX UnicodeDecodeError)
# =====================================================
st.divider()
st.subheader("🌐 Sync Souverain")

export_data = json.dumps(NODE["TUNNELS"][sid])
st.download_button(
    "⬇️ Export Tunnel",
    export_data,
    file_name="kongossa_sync.json"
)

imp = st.file_uploader("Importer Sync", type=["json"])

if imp:
    try:
        incoming = json.loads(
            imp.getvalue().decode("utf-8", errors="ignore")
        )
        NODE["TUNNELS"][sid].extend(incoming)
        st.success("Fusion Node OK")
        st.rerun()
    except Exception as e:
        st.error("Fichier invalide")

# =====================================================
# ================= V18 NETWORK ENGINE =================
# =====================================================

def build_graph(node):
    graph = {}

    for sid, msgs in node["TUNNELS"].items():
        users = set(m["u"] for m in msgs)

        for u in users:
            graph.setdefault(u, set())
            graph[u].update(users - {u})

    return graph


def centrality(graph):
    return {u: len(v) for u, v in graph.items()}


def community_energy(node):
    return sum(len(v) for v in node["TUNNELS"].values())


def dead_zones(node, timeout=60):
    now = time.time()
    return [
        u for u, t in node["PRESENCE"].items()
        if now - t > timeout
    ]


def coherence_index(graph):
    if not graph:
        return 0
    links = sum(len(v) for v in graph.values())
    nodes = len(graph)
    return links / max(nodes, 1)


def v18_control(node):

    graph = build_graph(node)
    cent = centrality(graph)
    energy = community_energy(node)
    dead = dead_zones(node)
    coh = coherence_index(graph)

    if coh < 1:
        refresh = 6
    elif coh > 5:
        refresh = 2
    else:
        refresh = 4

    return {
        "graph": graph,
        "centrality": cent,
        "energy": energy,
        "dead": dead,
        "coherence": coh,
        "refresh": refresh
    }

# =====================================================
# EXECUTE V18
# =====================================================
v18 = v18_control(NODE)

st.divider()
st.caption("🧠 V18 Network State")

st.write({
    "coherence": round(v18["coherence"], 2),
    "energy": v18["energy"],
    "active_nodes": len(v18["graph"]),
})

# =====================================================
# ADAPTIVE REFRESH
# =====================================================
time.sleep(v18["refresh"])
st.rerun()
