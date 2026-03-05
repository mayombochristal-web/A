🇬🇦 Free_Kogossa

Free_Kogossa est un réseau social expérimental léger construit avec Streamlit permettant :

- publication de posts (texte + image)
- commentaires
- messagerie privée
- profils utilisateurs
- fil social communautaire

L'application est conçue pour fonctionner sans serveur complexe, uniquement avec Streamlit et des fichiers JSON.

---

🚀 Fonctionnalités

📢 Fil social

- publier du texte
- publier une image
- commenter les publications
- affichage chronologique

💬 Messagerie

- discussion privée entre utilisateurs
- historique des conversations
- tri chronologique des messages

👤 Profil

- photo de profil
- bio
- localisation
- modification du profil

🔐 Comptes utilisateurs

- création de compte
- connexion sécurisée par mot de passe

---

🧑‍💻 Première utilisation

Lors de votre première visite :

1. ouvrir l’onglet Créer compte
2. choisir un nom d’utilisateur
3. choisir un mot de passe
4. ajouter une photo de profil (optionnel)
5. cliquer sur Créer compte

Ensuite vous pourrez utiliser l’onglet Connexion.

---

⚠️ Message "Identifiants incorrects"

Ce message signifie que :

- le nom d'utilisateur n'existe pas
- ou le mot de passe est incorrect

Si c'est votre première visite, vous devez créer un compte avant de vous connecter.

---

📂 Structure du projet

app.py
data/
   users.json
   posts.json
   messages.json

Les données sont stockées localement dans le dossier data.

---

🛠 Installation locale

Installer Streamlit :

pip install streamlit

Lancer l'application :

streamlit run app.py

---

☁️ Déploiement Streamlit Cloud

1. créer un dépôt GitHub
2. ajouter app.py
3. déployer sur Streamlit Cloud

Aucune base de données externe n'est nécessaire.

---

⚙️ Limites actuelles

- stockage JSON (pas optimisé pour très grande échelle)
- pas de notifications en temps réel
- pas de système de followers

---

🌍 Projet

Free_Kogossa est un prototype de réseau social souverain simple conçu pour expérimenter :

- interaction sociale
- communication communautaire
- publication libre

---

📜 Licence

Projet open source expérimental.