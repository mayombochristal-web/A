import streamlit as st
from cryptography.fernet import Fernet
import hashlib, time, uuid, base64, json, math

# =====================================================
# CONFIGURATION
# =====================================================
st.set_page_config(page_title="GEN-Z GABON", page_icon="🇬🇦", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }

.status-box {
    padding:10px;
    border-radius:10px;
    border:1px solid #00ff00;
    background:#001a00;
    text-align:center;
    font-weight:bold;
}

.msg-box{
    padding:15px;
    border-radius:15px;
    background:#1e1e1e;
    margin-bottom:10px;
    border-left:5px solid #2e7d32;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# ================= TTU FORGE ENGINE ==================
# =====================================================

PHI_CRIT = 0.5088
FORGE_THRESHOLD = 0.95

def ttu_update(rho, tick):
    K = 25 + 5 * math.sin(tick * 0.2)
    phi = 0.5 + 0.5 * math.tanh(2.5 * (rho - 0.4)) - (K / 200)
    phi = max(0.0, min(1.0, phi))
    gamma = math.exp(-4 * phi)

    if phi < PHI_CRIT:
        phase = "Dissolution"
    elif phi < 0.75:
        phase = "Résonance"
    elif phi < FORGE_THRESHOLD:
        phase = "Cohérence Forte"
    else:
        phase = "🔥 FORGE ACTIVE"

    return phi, gamma, phase, K

# =====================================================
# ENGINE SOUVERAIN
# =====================================================

class SOVEREIGN:

    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:20]

    @staticmethod
    def key(secret):
        k = hashlib.pbkdf2_hmac("sha256", secret.encode(),
                                b"GABON-SOVEREIGN", 150000)
        return base64.urlsafe_b64encode(k[:32])

    @staticmethod
    def encrypt(secret, data):
        f = Fernet(SOVEREIGN.key(secret))
        c = f.encrypt(data)
        n = len(c)
        return [
            base64.b64encode(c[:n//3]).decode(),
            base64.b64encode(c[n//3:2*n//3]).decode(),
            base64.b64encode(c[2*n//3:]).decode()
        ]

    @staticmethod
    def decrypt(secret, frags):
        try:
            f = Fernet(SOVEREIGN.key(secret))
            combined = b"".join(base64.b64decode(x) for x in frags)
            return f.decrypt(combined)
        except:
            return None

# =====================================================
# NODE GLOBAL (CACHE PARTAGÉ)
# =====================================================

@st.cache_resource
def get_node():
    return {
        "TUNNELS": {},
        "PRESENCE": {},
        "TTU": {}  # moteur forge par tunnel
    }

NODE = get_node()

# =====================================================
# LOGIN
# =====================================================

if "uid" not in st.session_state:
    st.title("🇬🇦 GEN-Z GABON")
    nick = st.text_input("Pseudo Kongossa")
    if nick:
        st.session_state.uid = f"🇬🇦 {nick}#{uuid.uuid4().hex[:3]}"
        st.rerun()
    st.stop()

secret = st.sidebar.text_input("Code Tunnel Secret", type="password")

if not secret:
    st.info("Entre un code pour activer ton tunnel.")
    st.stop()

sid = SOVEREIGN.tunnel(secret)

if sid not in NODE["TUNNELS"]:
    NODE["TUNNELS"][sid] = []

# INIT TTU UNIVERSE
if sid not in NODE["TTU"]:
    NODE["TTU"][sid] = {
        "rho": 0.2,
        "tick": 0,
        "phi": 0.55,
        "gamma": 1.0,
        "phase": "Stable"
    }

TTU = NODE["TTU"][sid]

# =====================================================
# PRESENCE
# =====================================================

now = time.time()
NODE["PRESENCE"][st.session_state.uid] = {"ts": now, "sid": sid}

active_now = [
    u for u, d in NODE["PRESENCE"].items()
    if now - d["ts"] < 30 and d["sid"] == sid
]

# =====================================================
# FRONTEND
# =====================================================

st.title("🏠 Flux Souverain")

st.markdown(
    f"<div class='status-box'>🟢 {len(active_now)} Membres en ligne</div>",
    unsafe_allow_html=True
)

st.write(f"**ID Tunnel :** `{sid}`")

# =====================================================
# PUBLICATION (INJECTION TTU)
# =====================================================

def push(data, typ):

    frags = SOVEREIGN.encrypt(secret, data)

    NODE["TUNNELS"][sid].append({
        "u": st.session_state.uid,
        "f": frags,
        "t": typ,
        "ts": time.time()
    })

    # 🔥 Injection énergie TTU
    TTU["rho"] += 0.02
    TTU["rho"] = min(1.2, TTU["rho"])

    st.rerun()

with st.expander("➕ PUBLIER UN MESSAGE / MÉDIA", expanded=True):

    tab1, tab2, tab3 = st.tabs(["💬 Texte", "📸 Média", "🎙️ Vocal"])

    with tab1:
        txt = st.text_area("Message", label_visibility="collapsed")
        if st.button("Envoyer le texte", use_container_width=True):
            if txt:
                push(txt.encode(), "text")

    with tab2:
        f = st.file_uploader("Choisir un fichier", type=['png','jpg','mp4'])
        if f and st.button("Diffuser le fichier", use_container_width=True):
            push(f.getvalue(), f.type)

    with tab3:
        a = st.audio_input("Enregistrer un vocal")
        if a and st.button("Envoyer le vocal", use_container_width=True):
            push(a.getvalue(), "audio/wav")

st.divider()

# =====================================================
# EVOLUTION TTU AUTOMATIQUE
# =====================================================

TTU["tick"] += 1

phi, gamma, phase, K = ttu_update(
    TTU["rho"],
    TTU["tick"]
)

TTU["phi"] = phi
TTU["gamma"] = gamma
TTU["phase"] = phase

# dissipation naturelle
TTU["rho"] *= 0.995

# =====================================================
# DASHBOARD FORGE (DISCRET)
# =====================================================

with st.expander("⚛️ État TTU du Tunnel", expanded=False):

    col1, col2 = st.columns(2)

    col1.metric("Φc Cohérence", f"{phi*100:.2f}%")
    col1.metric("Phase", phase)

    col2.metric("Γ Spectrale", f"{gamma:.4f}")
    col2.metric("Courbure K", f"{K:.2f}")

    st.progress(phi)

# =====================================================
# FLUX
# =====================================================

for m in reversed(NODE["TUNNELS"][sid]):
    raw = SOVEREIGN.decrypt(secret, m["f"])

    if raw:
        st.markdown(
            f"**{m['u']}** • <small>{time.strftime('%H:%M', time.localtime(m['ts']))}</small>",
            unsafe_allow_html=True
        )

        if m["t"] == "text":
            st.markdown(f"<div class='msg-box'>{raw.decode()}</div>", unsafe_allow_html=True)
        elif "image" in m["t"]:
            st.image(raw)
        elif "video" in m["t"]:
            st.video(raw)
        else:
            st.audio(raw)

# =====================================================
# SYNC
# =====================================================

st.sidebar.divider()

exp_json = json.dumps(NODE["TUNNELS"][sid])
st.sidebar.download_button("⬇️ Exporter (Backup)", exp_json,
                           file_name=f"genz_{sid}.json")

imp = st.sidebar.file_uploader("📂 Importer (Sync)")

if imp:
    data = json.loads(imp.read().decode())
    current_ts = [msg["ts"] for msg in NODE["TUNNELS"][sid]]

    for msg in data:
        if msg["ts"] not in current_ts:
            NODE["TUNNELS"][sid].append(msg)

    st.rerun()

# =====================================================
# HORLOGE TTU
# =====================================================

time.sleep(4)
st.rerun()