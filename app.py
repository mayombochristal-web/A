import streamlit as st
from cryptography.fernet import Fernet
import hashlib, time, uuid, base64, json
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
# =====================================================
# CONFIGURATION PAGE
# =====================================================
st.set_page_config(
page_title="GEN-Z 🇬🇦 | Connecte-toi en toute liberté",
page_icon="🇬🇦",
layout="wide",
initial_sidebar_state="collapsed"
)
# =====================================================
# MOTEUR QUANTIQUE (Caché en arrière-plan)
# =====================================================
@dataclass
class QuantumState:
"""État quantique du système (invisible pour l'utilisateur)"""
Phi_M: float
Phi_C: float
Phi_D: float
timestamp: float
@property
def health_score(self) -> float:
"""Score de santé du système (0-100)"""
return min(100, (self.Phi_C / 0.95) * 100)
class SOVEREIGN:
"""Moteur cryptographique souverain"""
@staticmethod
def tunnel(secret: str) -> str:
return hashlib.sha256(secret.encode()).hexdigest()[:16]
@staticmethod
def key(secret: str, state: QuantumState) -> bytes:
iterations = int(150000 + state.Phi_C * 100000)
salt = f"GABON-{state.health_score:.0f}".encode()
k = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, iterations)
return base64.urlsafe_b64encode(k[:32])
@staticmethod
def encrypt(secret: str, data: bytes, state: QuantumState) -> List[str]:
key = SOVEREIGN.key(secret, state)
f = Fernet(key)
encrypted = f.encrypt(data)
n = len(encrypted)
fragments = [encrypted[:n//3], encrypted[n//3:2*n//3], encrypted[2*n//3:]]
return [base64.b64encode(frag).decode() for frag in fragments]
@staticmethod
def decrypt(secret: str, fragments: List[str], state: QuantumState) -> bytes:
try:
key = SOVEREIGN.key(secret, state)
f = Fernet(key)
combined = b"".join([base64.b64decode(frag) for frag in fragments])
return f.decrypt(combined)
except:
return None
@st.cache_resource
def get_network():
"""Initialise le réseau global"""
return {
"FEEDS": {},
"USERS": {},
"STATES": {},
"REACTIONS": {}
}
NETWORK = get_network()
# =====================================================
# DESIGN MODERNE & RASSURANT
# =====================================================
st.markdown("""
""", unsafe_allow_html=True)
# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================
def time_ago(timestamp: float) -> str:
"""Convertit timestamp en format 'il y a X'"""
now = datetime.now()
posted = datetime.fromtimestamp(timestamp)
delta = now - posted
if delta.seconds < 60:
return "À l'instant"
elif delta.seconds < 3600:
minutes = delta.seconds // 60
return f"Il y a {minutes} min"
elif delta.seconds < 86400:
hours = delta.seconds // 3600
return f"Il y a {hours}h"
else:
return posted.strftime("%d %b")
def get_initials(name: str) -> str:
"""Extrait les initiales pour l'avatar"""
parts = name.split()
if len(parts) >= 2:
return (parts[0][0] + parts[-1][0]).upper()
return name[:2].upper()
# =====================================================
# AUTHENTIFICATION
# =====================================================
def show_auth_screen():
st.markdown("""
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
nickname = st.text_input(
"📝 Ton pseudo",
placeholder="Ex: Sarah, Kevin, Amina...",
label_visibility="collapsed"
)
col_a, col_b = st.columns(2)
with col_a:
if st.button("✨ Créer un compte", use_container_width=True):
if nickname:
st.session_state.uid = f"{nickname}#{uuid.uuid4().hex[:3]}"
st.session_state.display_name = nickname
st.session_state.joined = time.time()
st.session_state.avatar_color = f"#{uuid.uuid4().hex[:6]}"
st.rerun()
with col_b:
if st.button("🔑 Se connecter", use_container_width=True):
if nickname:
st.session_state.uid = f"{nickname}#{uuid.uuid4().hex[:3]}"
st.session_state.display_name = nickname
st.session_state.joined = time.time()
st.session_state.avatar_color = f"#{uuid.uuid4().hex[:6]}"
st.rerun()
st.markdown("""
""", unsafe_allow_html=True)
if "uid" not in st.session_state:
show_auth_screen()
st.stop()
# =====================================================
# CONFIGURATION TUNNEL
# =====================================================
if "tunnel_setup" not in st.session_state:
st.markdown("""
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
secret = st.text_input(
"Code secret (4 caractères min)",
type="password",
placeholder="••••••••",
label_visibility="collapsed"
)
if st.button("🚀 Créer mon espace", use_container_width=True):
if len(secret) >= 4:
st.session_state.secret = secret
st.session_state.tunnel_id = SOVEREIGN.tunnel(secret)
st.session_state.tunnel_setup = True
if st.session_state.tunnel_id not in NETWORK["STATES"]:
NETWORK["FEEDS"][st.session_state.tunnel_id] = []
NETWORK["STATES"][st.session_state.tunnel_id] = QuantumState(
Phi_M=0.6, Phi_C=0.3, Phi_D=0.1, timestamp=time.time()
)
st.success("✅ Espace créé avec succès !")
time.sleep(1)
st.rerun()
else:
st.warning("⚠️ Le code doit contenir au moins 4 caractères")
st.stop()
# =====================================================
# RÉCUPÉRATION CONTEXTE
# =====================================================
tunnel_id = st.session_state.tunnel_id
secret = st.session_state.secret
state = NETWORK["STATES"][tunnel_id]
feed = NETWORK["FEEDS"][tunnel_id]
NETWORK["USERS"][st.session_state.uid] = {
"ts": time.time(),
"tunnel": tunnel_id,
"name": st.session_state.display_name
}
active_users = [
u for u, d in NETWORK["USERS"].items()
if time.time() - d["ts"] < 30 and d["tunnel"] == tunnel_id
]
# =====================================================
# HEADER
# =====================================================
col_logo, col_search, col_user = st.columns([2, 4, 2])
with col_logo:
st.markdown("<div class='logo'>🇬🇦 GEN-Z</div>", unsafe_allow_html=True)
with col_search:
search = st.text_input(
"Rechercher...",
placeholder="🔍 Rechercher",
label_visibility="collapsed"
)
with col_user:
st.markdown(f"""
<div class='user-avatar' style='background: {st.session_state.avatar_color};'>
{get_initials(st.session_state.display_name)}
<span class='username'>{st.session_state.display_name}</span>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
# =====================================================
# STATUS BAR
# =====================================================
st.markdown(f"""
<span style='font-weight: 500; color: #1a1a1a;'>{len(active_users)} en ligne</span>
<span style='color: #8e8e8e; margin-left: auto;'>{len(feed)} publications</span>
""", unsafe_allow_html=True)
# =====================================================
# LAYOUT
# =====================================================
col_left, col_center, col_right = st.columns([1, 2.5, 1])
with col_left:
st.markdown("""
""", unsafe_allow_html=True)
with col_center:
with st.expander("✍️ Créer une publication", expanded=False):
tab1, tab2, tab3 = st.tabs(["📝 Texte", "📷 Photo/Vidéo", "🎵 Audio"])
def publish(data: bytes, content_type: str, metadata: dict = None):
fragments = SOVEREIGN.encrypt(secret, data, state)
post = {
"id": uuid.uuid4().hex[:8],
"user": st.session_state.uid,
"display_name": st.session_state.display_name,
"avatar_color": st.session_state.avatar_color,
"fragments": fragments,
"type": content_type,
"timestamp": time.time(),
"likes": 0,
"comments": [],
"metadata": metadata or {}
}
NETWORK["FEEDS"][tunnel_id].insert(0, post)
state.Phi_M = min(1.0, state.Phi_M + 0.02)
st.success("✨ Publication partagée !")
time.sleep(0.5)
st.rerun()
with tab1:
post_text = st.text_area(
"Quoi de neuf ?",
placeholder="Partage quelque chose...",
height=120,
label_visibility="collapsed"
)
if st.button("📤 Publier", use_container_width=True, type="primary"):
if post_text:
publish(post_text.encode(), "text")
with tab2:
uploaded_media = st.file_uploader(
"Choisir",
type=['png', 'jpg', 'jpeg', 'gif', 'mp4'],
label_visibility="collapsed"
)
if uploaded_media:
if uploaded_media.type.startswith('image'):
st.image(uploaded_media, use_container_width=True)
else:
st.video(uploaded_media)
caption = st.text_input("Légende", placeholder="Description...")
if st.button("📸 Publier", use_container_width=True, type="primary"):
publish(uploaded_media.getvalue(), uploaded_media.type, {"caption": caption})
with tab3:
audio = st.audio_input("🎤 Enregistrer")
if audio:
st.audio(audio)
if st.button("🎵 Publier", use_container_width=True, type="primary"):
publish(audio.getvalue(), "audio/wav")
st.markdown("<br>", unsafe_allow_html=True)
if not feed:
st.markdown("""
""", unsafe_allow_html=True)
else:
for post in feed[:20]:
decrypted = SOVEREIGN.decrypt(secret, post["fragments"], state)
if not decrypted:
continue
st.markdown(f"""
<div class='user-avatar' style='background: {post["avatar_color"]};'>
{get_initials(post["display_name"])}
<div class='username'>{post["display_name"]}</div>
<div class='time-ago'>{time_ago(post["timestamp"])}</div>
""", unsafe_allow_html=True)
if post["type"] == "text":
st.markdown(f"<div class='post-content'>{decrypted.decode()}</div>", unsafe_allow_html=True)
elif "image" in post["type"]:
caption = post.get("metadata", {}).get("caption", "")
if caption:
st.markdown(f"<div class='post-content'>{caption}</div>", unsafe_allow_html=True)
st.image(decrypted, use_container_width=True)
elif "video" in post["type"]:
st.video(decrypted)
elif "audio" in post["type"]:
st.audio(decrypted)
col_like, col_comment, col_share = st.columns(3)
with col_like:
if st.button(f"❤️ {post['likes']}", key=f"like_{post['id']}", use_container_width=True):
post['likes'] += 1
st.rerun()
with col_comment:
st.button(f"💬 {len(post['comments'])}", key=f"comment_{post['id']}", use_container_width=True)
with col_share:
st.button("🔗", key=f"share_{post['id']}", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
with col_right:
st.markdown("""
""", unsafe_allow_html=True)
time.sleep(3)
st.rerun()
