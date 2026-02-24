import streamlit as st
import uuid
import time

# =============================
# INITIALISATION NODE V22
# =============================

if "NODE" not in st.session_state:

    st.session_state.NODE = {
        "users": {},
        "messages": {},
        "subscriptions": {},
        "discover": {},
        "profile": None
    }

NODE = st.session_state.NODE


# =============================
# OUTILS
# =============================

def pair_id(a, b):
    """Anti duplication conversation"""
    return "_".join(sorted([a, b]))


def ensure_profile():
    if NODE["profile"] is None:
        NODE["profile"] = {
            "id": str(uuid.uuid4())[:8],
            "name": "Utilisateur",
            "bio": "",
            "photo": None
        }
        NODE["users"][NODE["profile"]["id"]] = NODE["profile"]


ensure_profile()
ME = NODE["profile"]["id"]


# =============================
# SIDEBAR NAVIGATION
# =============================

st.sidebar.title("🌐 NDOLÔ V22")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "🔎 Découverte", "💬 Messages", "👤 Profil"]
)

# =============================
# ACCUEIL
# =============================

if page == "🏠 Accueil":

    st.title("Bienvenue sur NDOLÔ")

    st.write("Réseau social conversationnel.")

    if st.button("Publier mon profil dans Découverte"):
        NODE["discover"][ME] = NODE["profile"]
        st.success("Profil publié ✔")


# =============================
# DECOUVERTE (SOCIAL STYLE)
# =============================

elif page == "🔎 Découverte":

    st.title("Découvrir des utilisateurs")

    for uid, user in NODE["discover"].items():

        if uid == ME:
            continue

        col1, col2 = st.columns([1,4])

        with col1:
            st.write("👤")

        with col2:
            st.subheader(user["name"])
            st.caption(user["bio"])

            subscribed = uid in NODE["subscriptions"]

            if not subscribed:
                if st.button("S'abonner", key=f"sub{uid}"):
                    NODE["subscriptions"][uid] = True
                    st.success("Abonné ✔")
                    st.rerun()
            else:
                if st.button("Se désabonner", key=f"unsub{uid}"):
                    del NODE["subscriptions"][uid]
                    st.rerun()

        st.divider()


# =============================
# MESSAGERIE
# =============================

elif page == "💬 Messages":

    st.title("Messages")

    if not NODE["subscriptions"]:
        st.info("Abonne-toi à quelqu’un pour discuter.")
    else:

        target = st.selectbox(
            "Choisir une conversation",
            list(NODE["subscriptions"].keys())
        )

        cid = pair_id(ME, target)

        if cid not in NODE["messages"]:
            NODE["messages"][cid] = []

        chat_box = st.container(height=400)

        with chat_box:
            for msg in NODE["messages"][cid]:
                if msg["sender"] == ME:
                    st.markdown(f"**Moi :** {msg['text']}")
                else:
                    st.markdown(f"**{msg['sender']} :** {msg['text']}")

        message = st.text_input("Message")

        if st.button("Envoyer") and message:

            NODE["messages"][cid].append({
                "sender": ME,
                "text": message,
                "time": time.time()
            })

            st.rerun()


# =============================
# PROFIL
# =============================

elif page == "👤 Profil":

    st.title("Mon profil")

    name = st.text_input("Nom", NODE["profile"]["name"])
    bio = st.text_area("Bio", NODE["profile"]["bio"])

    photo = st.file_uploader("Photo de profil", type=["png","jpg","jpeg"])

    if st.button("Sauvegarder"):
        NODE["profile"]["name"] = name
        NODE["profile"]["bio"] = bio
        NODE["profile"]["photo"] = photo
        NODE["users"][ME] = NODE["profile"]
        st.success("Profil mis à jour ✔")

    st.divider()

    st.subheader("Identité publique")
    st.code(ME)
