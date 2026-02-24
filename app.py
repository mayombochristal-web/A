import streamlit as st
from cryptography.fernet import Fernet
import hashlib, time, uuid, base64, json

# =====================================================
# CONFIGURATION ET STYLE (CORRIGÉ)
# =====================================================
st.set_page_config(page_title="GEN-Z GABON", page_icon="🇬🇦", layout="centered")

# Suppression du paramètre erroné, utilisation du standard
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
# ENGINE SOUVERAIN (TON MOTEUR ORIGINAL)
# =====================================================
class SOVEREIGN:
    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:20]

    @staticmethod
    def key(secret):
        k = hashlib.pbkdf2_hmac("sha256", secret.encode(), b"GABON-SOVEREIGN", 150000)
        return base64.urlsafe_b64encode(k[:32])

    @staticmethod
    def encrypt(secret, data):
        f = Fernet(SOVEREIGN.key(secret))
        c = f.encrypt(data)
        n = len(c)
        return [base64.b64encode(c[:n//3]).decode(), 
                base64.b64encode(c[n//3:2*n//3]).decode(), 
                base64.b64encode(c[2*n//3:]).decode()]

    @staticmethod
    def decrypt(secret, frags):
        try:
            f = Fernet(SOVEREIGN.key(secret))
            combined = b"".join([base64.b64decode(frag) for frag in frags])
            return f.decrypt(combined)
        except: return None

# =====================================================
# NODE DATABASE (SYSTÈME DE CACHE PARTAGÉ)
# =====================================================
@st.cache_resource
def get_node():
    return {"TUNNELS": {}, "PRESENCE": {}}

NODE = get_node()

# =====================================================
# SESSION & AUTHENTIFICATION
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

# =====================================================
# PRÉSENCE EN DIRECT
# =====================================================
now = time.time()
NODE["PRESENCE"][st.session_state.uid] = {"ts": now, "sid": sid}
# On filtre ceux qui sont sur le même tunnel et actifs depuis < 30s
active_now = [u for u, d in NODE["PRESENCE"].items() if (now - d["ts"] < 30 and d["sid"] == sid)]

# =====================================================
# INTERFACE DE PUBLICATION
# =====================================================
st.title("🏠 Flux Souverain")
st.markdown(f"<div class='status-box'>🟢 {len(active_now)} Membres en ligne</div>", unsafe_allow_html=True)
st.write(f"**ID Tunnel :** `{sid}`")

with st.expander("➕ PUBLIER UN MESSAGE / MÉDIA", expanded=True):
    tab1, tab2, tab3 = st.tabs(["💬 Texte", "📸 Média", "🎙️ Vocal"])
    
    def push(data, typ):
        frags = SOVEREIGN.encrypt(secret, data)
        NODE["TUNNELS"][sid].append({
            "u": st.session_state.uid,
            "f": frags,
            "t": typ,
            "ts": time.time()
        })
        st.rerun()

    with tab1:
        txt = st.text_area("Message", label_visibility="collapsed")
        if st.button("Envoyer le texte", use_container_width=True):
            if txt: push(txt.encode(), "text")

    with tab2:
        f = st.file_uploader("Choisir un fichier", type=['png', 'jpg', 'mp4'])
        if f and st.button("Diffuser le fichier", use_container_width=True):
            push(f.getvalue(), f.type)

    with tab3:
        a = st.audio_input("Enregistrer un vocal")
        if a and st.button("Envoyer le vocal", use_container_width=True):
            push(a.getvalue(), "audio/wav")

st.divider()

# =====================================================
# AFFICHAGE DU FLUX (LIVESTREAM)
# =====================================================
for m in reversed(NODE["TUNNELS"][sid]):
    raw = SOVEREIGN.decrypt(secret, m["f"])
    if raw:
        st.markdown(f"**{m['u']}** • <small>{time.strftime('%H:%M', time.localtime(m['ts']))}</small>", unsafe_allow_html=True)
        if m["t"] == "text":
            st.markdown(f"<div class='msg-box'>{raw.decode()}</div>", unsafe_allow_html=True)
        elif "image" in m["t"]:
            st.image(raw)
        elif "video" in m["t"]:
            st.video(raw)
        else:
            st.audio(raw)

# =====================================================
# SYNC & BACKUP (MENU LATÉRAL)
# =====================================================
st.sidebar.divider()
exp_json = json.dumps(NODE["TUNNELS"][sid])
st.sidebar.download_button("⬇️ Exporter (Backup)", exp_json, file_name=f"genz_{sid}.json")

imp = st.sidebar.file_uploader("📂 Importer (Sync)")
if imp:
    data = json.loads(imp.read().decode())
    # Fusion sans doublons
    current_ts = [msg["ts"] for msg in NODE["TUNNELS"][sid]]
    for msg in data:
        if msg["ts"] not in current_ts:
            NODE["TUNNELS"][sid].append(msg)
    st.rerun()

time.sleep(4)
st.rerun()
