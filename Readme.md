# 🌍 Free_Kogossa – Le réseau social libre et sécurisé

**Free_Kogossa** est une plateforme sociale innovante développée avec **Streamlit** et **Supabase**. Elle offre un espace d’échange communautaire où la confidentialité, la simplicité et la richesse des médias sont au cœur de l’expérience.

---

## ✨ Fonctionnalités principales

### 🔐 Sécurité et confidentialité
- **Mots de passe hachés** (SHA‑256) – aucun stockage en clair.
- **Authentification sécurisée** via Supabase.
- **Données hébergées sur le cloud** (Supabase) – contrôle total et sauvegarde automatique.
- **Absence de publicités et de pistage** – votre vie privée est respectée.

### 🗣️ Fonctionnalités sociales
- **Fil d’actualité** : publiez des messages, des images et des vidéos.
- **Commentaires** : échangez sur les publications de la communauté.
- **Messagerie privée** : conversations textuelles, vocales et vidéo en temps réel (rafraîchissement automatique).
- **Enregistrement vocal** directement depuis le navigateur (microphone).
- **Partage de fichiers** : images, vidéos, audios – le tout stocké dans le cloud.

### 👤 Gestion de profil
- **Photo de profil** (upload vers le cloud).
- **Bio et localisation** modifiables.
- **Changement de mot de passe** sécurisé.
- **Bannière personnalisée** visible sur toutes les pages.

### 📊 Statistiques communautaires
- Nombre d’utilisateurs et de publications affiché sur la page “À propos”.

### ⚡ Expérience utilisateur optimisée
- **Rafraîchissement automatique** (feed toutes les 5s, messagerie toutes les 2s) pour une sensation temps réel.
- Interface responsive, adaptée aux mobiles et ordinateurs.
- Design clair et intuitif.

---

## 🛠️ Architecture technique

- **Frontend / Backend** : [Streamlit](https://streamlit.io) – framework Python pour applications data.
- **Base de données** : [Supabase](https://supabase.com) – PostgreSQL + authentification + storage.
- **Stockage média** : Bucket `uploads` sur Supabase Storage.
- **Sécurité** : Hachage SHA‑256, politiques RLS (Row Level Security) dans Supabase.

---

## 🚀 Guide d’installation et déploiement

### 1. Prérequis
- Python 3.9 ou supérieur
- Un compte [Supabase](https://supabase.com) (gratuit)
- (Optionnel) Compte [Streamlit Cloud](https://streamlit.io/cloud) pour le déploiement

### 2. Installation locale

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/free_kogossa.git
cd free_kogossa

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows

# Installer les dépendances
pip install -r requirements.txt