import streamlit as st
from cryptography.fernet import Fernet
import hashlib, time, uuid, base64, json

# =====================================================
# CONFIGURATION ET STYLE (PRO)
# =====================================================
st.set_page_config(page_title="GEN-Z GABON", page_icon="🇬🇦", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .status-box { padding: 10px; border-radius: 10px; border: 1px solid #00ff00; background: #001a00; }
    .msg-box { padding: 15px; border-radius: 15px; background: #1e1e1e; margin-bottom: 10px; border-left: 5px solid #2e7d32; }
    </style>
""", unsafe_allow_state_with_metadata=True)

# =====================================================
# ENGINE SOUVERAIN (TON MOTEUR OPTIMISÉ)
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
        # Fragmentation pour la sécurité
        return [base64.b64encode(c[:n//3]).decode(), 
                base64.b64encode(c[n//3:2*n//3]).decode(), 
                base64.b64encode(c[2*n//3:]).decode()]

    @staticmethod
    def decrypt(secret, frags):
        try:
            f = Fernet(SOVEREIGN.key(secret))
            combined = b"".join([base64.b64decode(f) for f in frags])
            return f.decrypt(combined)
        except: return None

# =====================================================
# BASE DE DONNÉES NODE (PARTAGÉE)
# =====================================================
@st.cache_resource
def get_node():
    return {"TUNNELS": {}, "PRESENCE": {}}

NODE = get_node()

# =====================================================
# SESSION & AUTH
# =====================================================
if "uid" not in st.session_state:
    st.title("🇬🇦 GEN-Z GABON")
    nick = st.text_input("Pseudo Kongossa", placeholder="Ex: @PimentGabonais")
    if nick:
        st.session_state.uid = f"🇬🇦 {nick}#{uuid.uuid4().hex[:3]}"
        st.rerun()
    st.stop()

# --- ACCÈS AU TUNNEL ---
secret = st.sidebar.text_input("Code Tunnel Secret", type="password", help="Les utilisateurs avec le même code se voient en direct.")
if not secret:
    st.info("💡 Entre un 'Code Tunnel' pour rejoindre la discussion.")
    st.stop()

sid = SOVEREIGN.tunnel(secret)
if sid not in NODE["TUNNELS"]:
    NODE["TUNNELS"][sid] = []

# =====================================================
# LIVE PRESENCE (LE VOYANT VERT)
# =====================================================
now = time.time()
NODE["PRESENCE"][st.session_state.uid] = {"ts": now, "sid": sid}
# Nettoyage auto des inactifs (30s)
active_users = [u for u, data in NODE["PRESENCE"].items() if (now - data["ts"] < 30 and data["sid"] == sid)]

# =====================================================
# INTERFACE PRINCIPALE
# =====================================================
st.title("🏠 Flux Souverain")

# Affichage du statut en haut
col_stat1, col_stat2 = st.columns([2, 1])
with col_stat1:
    st.markdown(f"**Tunnel ID:** `{sid}`")
with col_stat2:
    st.markdown(f"<div class='status-box'>🟢 {len(active_users)} Actifs</div>", unsafe_allow_html=True)

# --- ZONE D'ENVOI ---
with st.expander("➕ PUBLIER (Texte, Photo, Vocal)", expanded=True):
    mode = st.tabs(["💬 Texte", "📸 Média", "🎙️ Vocal"])
    
    def push(data, typ):
        frags = SOVEREIGN.encrypt(secret, data)
        NODE["TUNNELS"][sid].append({
            "u": st.session_state.uid,
            "f": frags,
            "t": typ,
            "ts": time.time()
        })
        st.rerun()

    with mode[0]:
        txt = st.text_area("", placeholder="Écris ton message ici...", key="txt_area")
        if st.button("Envoyer", use_container_width=True):
            if txt: push(txt.encode(), "text")

    with mode[1]:
        f = st.file_uploader("Upload Image/Vidéo", type=['png', 'jpg', 'jpeg', 'mp4'])
        if f and st.button("Diffuser Média", use_container_width=True):
            push(f.getvalue(), f.type)

    with mode[2]:
        a = st.audio_input("Micro")
        if a and st.button("Envoyer Vocal", use_container_width=True):
            push(a.getvalue(), "audio/wav")

st.divider()

# --- FIL DE DISCUSSION (REVERSE CHRONO) ---
messages = NODE["TUNNELS"][sid]
for m in reversed(messages):
    raw = SOVEREIGN.decrypt(secret, m["f"])
    if raw:
        with st.container():
            st.markdown(f"**{m['u']}** <span style='color:gray; font-size:10px;'>{time.strftime('%H:%M', time.localtime(m['ts']))}</span>", unsafe_allow_html=True)
            
            if m["t"] == "text":
                st.markdown(f"<div class='msg-box'>{raw.decode()}</div>", unsafe_allow_html=True)
            elif "image" in m["t"]:
                st.image(raw, use_column_width=True)
            elif "video" in m["t"]:
                st.video(raw)
            elif "audio" in m["t"]:
                st.audio(raw)
    else:
        # Si le décryptage échoue (mauvais code secret)
        pass

# =====================================================
# SYNC SOUVERAINE (BACKUP)
# =====================================================
st.sidebar.divider()
st.sidebar.subheader("🌐 Synchronisation")

# Export
export_data = json.dumps(NODE["TUNNELS"][sid], ensure_ascii=False)
st.sidebar.download_button("⬇️ Exporter le Tunnel", export_data, file_name=f"sync_{sid}.json", use_container_width=True)

# Import
imp = st.sidebar.file_uploader("📂 Importer Data")
if imp:
    incoming = json.loads(imp.read().decode("utf-8"))
    # Fusion intelligente (éviter les doublons par timestamp)
    existing_ts = [m["ts"] for m in NODE["TUNNELS"][sid]]
    for msg in incoming:
        if msg["ts"] not in existing_ts:
            NODE["TUNNELS"][sid].append(msg)
    st.sidebar.success("Fusion terminée !")
    st.rerun()

# --- AUTO-REFRESH (4 secondes pour le live) ---
time.sleep(4)
st.rerun()
