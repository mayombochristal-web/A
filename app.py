import streamlit as st
from cryptography.fernet import Fernet
import hashlib, time, uuid, base64, json

# =====================================================
# ENGINE SOUVERAIN (Invisible pour l'utilisateur)
# =====================================================
class SovereignEngine:
    @staticmethod
    def get_key(secret):
        k = hashlib.pbkdf2_hmac("sha256", secret.encode(), b"GABON-V21", 100000)
        return base64.urlsafe_b64encode(k[:32])

    @staticmethod
    def encrypt(secret, data):
        f = Fernet(SovereignEngine.get_key(secret))
        return base64.b64encode(f.encrypt(data)).decode()

    @staticmethod
    def decrypt(secret, token):
        try:
            f = Fernet(SovereignEngine.get_key(secret))
            return f.decrypt(base64.b64decode(token))
        except: return None

# =====================================================
# DATABASE LOCALE (Simulée en cache)
# =====================================================
if "db" not in st.session_state:
    st.session_state.db = {"posts": [], "users": {}}
if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# INTERFACE : CONNEXION INSTANTANÉE
# =====================================================
st.set_page_config(page_title="GEN-Z GABON", page_icon="🇬🇦", layout="wide")

if not st.session_state.user:
    st.title("🇬🇦 Bienvenue sur GEN-Z")
    col1, col2 = st.columns(2)
    with col1:
        pseudo = st.text_input("Choisis ton pseudo", placeholder="Ex: Petit_Piment")
    with col2:
        code = st.text_input("Ton Code Secret (Pass)", type="password")
    
    if st.button("Entrer dans le Game 🚀", use_container_width=True):
        if pseudo and code:
            st.session_state.user = {"name": f"🇬🇦 {pseudo}", "secret": code}
            st.rerun()
    st.stop()

# =====================================================
# NAVIGATION (STYLE INSTAGRAM)
# =====================================================
menu = st.sidebar.radio("Menu", ["🏠 Accueil", "➕ Publier", "📩 Messages Privés", "⚙️ Sync & Backup"])
user = st.session_state.user

st.sidebar.divider()
st.sidebar.caption(f"Connecté en tant que : {user['name']}")

# =====================================================
# ONGLET 1 : ACCUEIL (FEED)
# =====================================================
if menu == "🏠 Accueil":
    st.title("Fil d'actualité")
    if not st.session_state.db["posts"]:
        st.info("Aucune publication pour le moment. Sois le premier !")
    
    for p in reversed(st.session_state.db["posts"]):
        with st.container(border=True):
            raw_content = SovereignEngine.decrypt(user['secret'], p['data'])
            if raw_content:
                st.subheader(f"{p['author']}")
                if p['type'] == "text":
                    st.write(raw_content.decode())
                elif "image" in p['type']:
                    st.image(raw_content)
                st.caption(f"Publié à {time.strftime('%H:%M', time.localtime(p['ts']))}")
            else:
                st.caption("🔒 Message crypté (Code secret différent)")

# =====================================================
# ONGLET 2 : PUBLIER (COMME TIKTOK/IG)
# =====================================================
elif menu == "➕ Publier":
    st.title("Créer un Post")
    tab1, tab2 = st.tabs(["📝 Texte", "📸 Photo/Vidéo"])
    
    with tab1:
        msg = st.text_area("Quoi de neuf ?", placeholder="Écris ici...")
        if st.button("Poster le message"):
            encrypted = SovereignEngine.encrypt(user['secret'], msg.encode())
            st.session_state.db["posts"].append({
                "author": user['name'], "data": encrypted, "type": "text", "ts": time.time()
            })
            st.success("Posté !")
            
    with tab2:
        file = st.file_uploader("Choisir un média", type=['png', 'jpg', 'mp4'])
        if file and st.button("Diffuser le média"):
            encrypted = SovereignEngine.encrypt(user['secret'], file.getvalue())
            st.session_state.db["posts"].append({
                "author": user['name'], "data": encrypted, "type": file.type, "ts": time.time()
            })
            st.success("Média diffusé !")

# =====================================================
# ONGLET 4 : SYNC (LE COEUR DU SYSTÈME)
# =====================================================
elif menu == "⚙️ Sync & Backup":
    st.title("Gestion de ton Node")
    st.write("Le réseau GEN-Z est **souverain**. Tu possèdes tes données.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Exporter")
        data_str = json.dumps(st.session_state.db["posts"])
        st.download_button("Télécharger ma Database (.json)", data_str, file_name="genz_data.json")
    
    with col2:
        st.subheader("Importer")
        imp_file = st.file_uploader("Fusionner avec un ami")
        if imp_file:
            new_data = json.loads(imp_file.read().decode())
            st.session_state.db["posts"].extend(new_data)
            st.success("Fusion réussie ! Retourne à l'accueil.")

# Auto-refresh discret
time.sleep(2)
