import streamlit as st
import uuid, time, json, base64

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="GEN-Z SOCIAL V22",
    page_icon="🌍",
    layout="centered"
)

# =====================================================
# GLOBAL SHARED STORE (STREAMLIT SAFE)
# =====================================================

@st.cache_resource
def HUB():
    return {
        "users":{},
        "posts":[],
        "tunnels":{}
    }

HUB = HUB()

# =====================================================
# UTILS
# =====================================================

def enc(b):
    return base64.b64encode(b).decode()

def dec(s):
    return base64.b64decode(s.encode())

# =====================================================
# USER INIT
# =====================================================

if "user" not in st.session_state:

    name = st.text_input("Choisis ton pseudo")

    if name:
        st.session_state.user={
            "id":uuid.uuid4().hex[:8],
            "name":name,
            "bio":"",
            "photo":None,
            "public":True,
            "subs":[]
        }
        st.rerun()

    st.stop()

USER=st.session_state.user

# =====================================================
# REGISTER USER
# =====================================================

HUB["users"][USER["id"]] = USER

# =====================================================
# UI
# =====================================================

st.title("🌍 GEN-Z SOCIAL")

tabs=st.tabs([
    "🏠 Accueil",
    "➕ Publier",
    "👥 Découvrir",
    "🔒 Tunnels",
    "👤 Profil"
])

# =====================================================
# ACCUEIL
# =====================================================

with tabs[0]:

    feed=[p for p in HUB["posts"]
          if p["user"] in USER["subs"]
          or p["user"]==USER["id"]]

    feed=sorted(feed,key=lambda x:x["ts"],reverse=True)

    if not feed:
        st.info("Abonne-toi à quelqu’un dans Découvrir 👥")

    for p in feed:

        u=HUB["users"].get(p["user"],{})

        st.subheader(u.get("name","?"))

        if p["type"]=="text":
            st.write(p["data"])

        elif p["type"]=="image":
            st.image(dec(p["data"]))

        elif p["type"]=="audio":
            st.audio(dec(p["data"]))

        st.divider()

# =====================================================
# PUBLIER
# =====================================================

with tabs[1]:

    visibility=st.radio("Visibilité",["Public","Privé"])

    mode=st.radio("Type",["Texte","Image","Vocal"],horizontal=True)

    def publish(data,typ):
        HUB["posts"].append({
            "id":uuid.uuid4().hex,
            "user":USER["id"],
            "type":typ,
            "data":data,
            "visibility":visibility,
            "ts":time.time()
        })

    if mode=="Texte":
        txt=st.text_area("Exprime toi...")
        if st.button("Publier"):
            publish(txt,"text")
            st.rerun()

    elif mode=="Image":
        f=st.file_uploader("Image")
        if f and st.button("Publier image"):
            publish(enc(f.getvalue()),"image")
            st.rerun()

    elif mode=="Vocal":
        a=st.audio_input("Vocal")
        if a and st.button("Publier vocal"):
            publish(enc(a.getvalue()),"audio")
            st.rerun()

# =====================================================
# DECOUVRIR
# =====================================================

with tabs[2]:

    st.subheader("🌍 Utilisateurs visibles")

    for uid,u in HUB["users"].items():

        if uid==USER["id"] or not u["public"]:
            continue

        col1,col2,col3=st.columns([4,1,1])

        with col1:
            st.write("👤",u["name"])

        with col2:
            if uid not in USER["subs"]:
                if st.button("S'abonner",key=uid):
                    USER["subs"].append(uid)
                    st.rerun()

        with col3:
            if uid in USER["subs"]:
                if st.button("Se désabonner",key=uid+"un"):
                    USER["subs"].remove(uid)
                    st.rerun()

# =====================================================
# TUNNELS
# =====================================================

with tabs[3]:

    name=st.text_input("Nom du tunnel")

    if st.button("Créer tunnel"):

        tid=uuid.uuid4().hex[:6]

        HUB["tunnels"][tid]={
            "owner":USER["id"],
            "members":[USER["id"]],
            "messages":[]
        }

        st.success(f"Tunnel créé : {tid}")

    st.divider()

    for tid,t in HUB["tunnels"].items():

        if USER["id"] in t["members"]:

            st.subheader(f"Tunnel {tid}")

            msg=st.text_input("Message",key=tid)

            if st.button("Envoyer",key=tid+"send"):
                t["messages"].append({
                    "user":USER["name"],
                    "text":msg
                })
                st.rerun()

            for m in t["messages"]:
                st.write(f"{m['user']} : {m['text']}")

# =====================================================
# PROFIL
# =====================================================

with tabs[4]:

    st.subheader("Profil")

    USER["bio"]=st.text_input("Bio",USER["bio"])

    photo=st.file_uploader("Photo / Logo")

    if photo:
        USER["photo"]=enc(photo.getvalue())

    USER["public"]=st.toggle("Profil public",USER["public"])

    st.write("ID public :",USER["id"])

    st.success("Profil mis à jour automatiquement ✅")
