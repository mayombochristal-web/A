import streamlit as st
from cryptography.fernet import Fernet
import hashlib, time, uuid, base64, json
from pathlib import Path

# =====================================================
# CONFIGURATION & STYLE
# =====================================================
st.set_page_config(page_title="GEN-Z GABON", page_icon="🇬🇦", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
.status-box {
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #00ff00;
    background: #001a00;
    text-align: center;
    font-weight: bold;
}
.msg-box {
    padding: 15px;
    border-radius: 15px;
    background: #1e1e1e;
    margin-bottom: 10px;
    border-left: 5px solid #2e7d32;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# ENGINE SOUVERAIN (CHIFFREMENT)
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
# STOCKAGE PERSISTANT (MULTI-UTILISATEURS RÉELS)
# =====================================================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def tunnel_file(sid):
    return DATA_DIR / f"{sid}.json"

def load_tunnel(sid):
    f = tunnel_file(sid)
    if f.exists():
        return json.loads(f.read_text())
    return []

def save_tunnel(sid, data):
    tunnel_file(sid).write_text(json.dumps(data))

# =====================================================
# AUTHENTIFICATION UTILISATEUR
# =====================================================
if "uid" not in st.session_state:
    st.title("🇬🇦 GEN-Z GABON")

    nick = st.text_input("Pseudo Kongossa")

    if nick:
        st.session_state.uid = f"🇬🇦 {nick}#{uuid.uuid4().hex[:3]}"
        st.rerun()

    st.stop()

# =====================================================
# TUNNEL SECRET
# =====================================================
secret = st.sidebar.text_input("Code Tunnel Secret", type="password")

if not secret:
    st.info("Entre un code pour activer ton tunnel.")
    st.stop()

sid = SOVEREIGN.tunnel(secret)
MESSAGES = load_tunnel(sid)

# =====================================================
# PRÉSENCE SIMPLE (LOCALE SESSION)
# =====================================================
if "last_seen" not in st.session_state:
    st.session_state.last_seen = time.time()

st.session_state.last_seen = time.time()

# estimation simple
online_estimate = max(1, len(MESSAGES) // 5)

# =====================================================
# INTERFACE
# =====================================================
st.title("🏠 Flux Souverain")

st.markdown(
    f"<div class='status-box'>🟢 {online_estimate} Membres actifs</div>",
    unsafe_allow_html=True
)

st.write(f"**ID Tunnel :** `{sid}`")

# =====================================================
# ENVOI MESSAGE
# =====================================================
def push(data, typ):
    global MESSAGES

    frags = SOVEREIGN.encrypt(secret, data)

    msg = {
        "u": st.session_state.uid,
        "f": frags,
        "t": typ,
        "ts": time.time()
    }

    MESSAGES.append(msg)
    save_tunnel(sid, MESSAGES)

    st.rerun()

# =====================================================
# PUBLICATION
# =====================================================
with st.expander("➕ PUBLIER UN MESSAGE / MÉDIA", expanded=True):

    tab1, tab2, tab3 = st.tabs(["💬 Texte", "📸 Média", "🎙️ Vocal"])

    with tab1:
        txt = st.text_area("Message", label_visibility="collapsed")

        if st.button("Envoyer le texte", use_container_width=True):
            if txt:
                push(txt.encode(), "text")

    with tab2:
        f = st.file_uploader("Choisir un fichier", type=["png","jpg","jpeg","mp4"])

        if f and st.button("Diffuser le fichier", use_container_width=True):
            push(f.getvalue(), f.type)

    with tab3:
        a = st.audio_input("Enregistrer un vocal")

        if a and st.button("Envoyer le vocal", use_container_width=True):
            push(a.getvalue(), "audio/wav")

st.divider()

# =====================================================
# AFFICHAGE FLUX
# =====================================================
MESSAGES = load_tunnel(sid)

for m in reversed(MESSAGES):

    raw = SOVEREIGN.decrypt(secret, m["f"])

    if raw:

        st.markdown(
            f"**{m['u']}** • "
            f"<small>{time.strftime('%H:%M', time.localtime(m['ts']))}</small>",
            unsafe_allow_html=True
        )

        if m["t"] == "text":
            st.markdown(
                f"<div class='msg-box'>{raw.decode()}</div>",
                unsafe_allow_html=True
            )

        elif "image" in m["t"]:
            st.image(raw)

        elif "video" in m["t"]:
            st.video(raw)

        else:
            st.audio(raw)

# =====================================================
# BACKUP & SYNC
# =====================================================
st.sidebar.divider()

exp_json = json.dumps(MESSAGES)

st.sidebar.download_button(
    "⬇️ Exporter (Backup)",
    exp_json,
    file_name=f"genz_{sid}.json"
)

imp = st.sidebar.file_uploader("📂 Importer (Sync)")

if imp:
    data = json.loads(imp.read().decode())

    existing = {m["ts"] for m in MESSAGES}

    for msg in data:
        if msg["ts"] not in existing:
            MESSAGES.append(msg)

    save_tunnel(sid, MESSAGES)
    st.rerun()

# =====================================================
# AUTO REFRESH
# =====================================================
time.sleep(4)
st.rerun()