import os
import re
import json
import csv
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ============================================
# CONFIGURATION
# ============================================
API_KEY = "AIzaSyChwOwDewEhlgRlhJ-LyZgxw5inyxh_9l8"  # À remplacer par votre clé API

# Liste complète des 13 vidéos
VIDEO_IDS = [
    # Vidéos originales (9)
    "mOsxCje8Mzk",   # Vidéo 1
    "NagPR4sIMog",   # Vidéo 2
    "zM4ArkA5sF0",   # Vidéo 3
    "7qakRzAcTNU",   # Vidéo 4
    "WEeqhi766cA",   # Vidéo 5
    "5K_1lDVuXX4",   # Vidéo 6
    "P2e_ZiP8CCc",   # Vidéo 7
    "OsxcmqyAUNc",   # Vidéo 8
    "oaTB3dRg0P0",   # Vidéo 9
    
    # Nouvelles vidéos (3)
    "NJ7MsraapQw",   # Vidéo 10
    "pwEC0LgHMW4",   # Vidéo 11
    "nryWLjukyY4",   # Vidéo 12
    
    # Dernière vidéo ajoutée (1)
    "TUaGzqVf2iY"    # Vidéo 13
]

# ============================================
# EXPRESSIONS RÉGULIÈRES AMÉLIORÉES
# ============================================

# Patterns pour les rires en arabe (3+ ه)
PATTERN_RIRES_ARABE = re.compile(r'ه{3,}')

# Patterns pour les émoticônes de rire (une ou plusieurs)
PATTERN_EMOJIS_RIRE = re.compile(r'(😂|🤣|😹|😆|🤪)+')

# Patterns pour "nmuut" et variantes (mourir de rire)
PATTERN_NMOUT = re.compile(r'\b(nmout|kanmout|anmout|نموت|كانموت|انموت)\b', re.IGNORECASE)

# Patterns pour hhhhh (3+ h)
PATTERN_RIRES_LETTRES = re.compile(r'h{3,}', re.IGNORECASE)

# Patterns pour hahaha
PATTERN_HAHAHA = re.compile(r'(ha){2,}', re.IGNORECASE)

# Patterns pour lol/lmao/mdr/ptdr
PATTERN_RIRES_ANGLAIS = re.compile(r'\b(lol+|lmao+|mdr+|ptdr+)\b', re.IGNORECASE)

# ============================================
# DICTIONNAIRE DES MOTS COMIQUES
# ============================================
KEYWORDS_FUNNY = [
    # Émoticônes et rires
    "😂", "🤣", "😹", "😆", "😝", "🤪",
    
    # Rires en lettres
    "hhhh", "hhhhh", "hhhhhh", "hhhhhhh", "hhhhhhhh", "hhhhhhhhh", "hhhhhhhhhh"
    # Rires en arabe
    "هههه", "ههههه", "هههههه", "ههههههه", "هههههههه", "ههههههههه",
    "هههههههههه", "ههههههههههه",
    
    # Mots liés au rire
    "ضحك", "الضحك", "ضحكة", "الضحكة", "ضحكني", "ضحكتيني", "تضحكني",
    "كيضحك", "كيضحكني", "يضحك", "يضحكني",
    
    # Expressions marocaines (rire intense)
    "موت بالضحك", "متت بالضحك", "غنموت بالضحك", "نموت بالضحك", "ماتت بالضحك",
    "ناري كنموت", "نموت", "anmout", "انموت", "نموت بضحك", "كانموت بضحك",
    "ناري كرشي", "كرشي ضحكات", "كرشي تلوح", "تضحكني بدموع", "ضحك حتى دموعي",
    "بكيت بالضحك", "موت ضحك", "ضحك بزاف", "واااعر ضحك", "ضحك واعر",
    
    # Adjectifs et descriptions
    "كوميدي", "مضحك", "مضحكة", "نكتة", "نكتة زوينة", "هادشي مضحك",
    "المتعة", "المرح", "السعادة", "للفرحة", "فرحة", 
    
    # Variantes avec émoticônes
    "ضحك 😂", "هههه😂", "هههههه😂", "😂😂😂", "🤣🤣🤣", "😂🤣", "هههه🤣",
    "hhh😂", "hhh🤣", "hhhhhhh 😂", "hhhhhhh 🤣", "waaaaa hhhh", "hhhh wa3er",
    "ضحك هههه", "هههه ضحك", "ضحك بزاف 😂", "😂 ههههه", "🤣 ههههه",
    "hadchi kaydehek", "kaydehek بزاف", "kaydehek بزاف 😂"
]

# Mots sérieux pour EXCLURE (commentaires non comiques)
KEYWORDS_EXCLUDE = [
    "merci", "chokran", "شكرا", "thank", "thanks",
    "s'il vous plaît", "svp", "please", "plz",
    "question", "سؤال", "help", "مساعدة",
    "tuto", "tutorial", "كيفاش", "كيفية"
]

# ============================================
# FONCTIONS DE NETTOYAGE ET DÉTECTION
# ============================================
def nettoyer_commentaire(texte):
    """Nettoie le commentaire pour l'analyse"""
    if not texte:
        return ""
    # Supprimer les retours à la ligne
    texte = texte.replace('\n', ' ').replace('\r', ' ')
    # Supprimer les espaces multiples
    texte = re.sub(r'\s+', ' ', texte)
    return texte.strip()

def detecter_rire_par_regex(texte):
    """
    Détecte les patterns de rire avec les nouvelles regex:
    - ه{3,} (3+ ه en arabe)
    - (😂|🤣)+ (émoticônes de rire)
    - (nmout|kanmout|anmout) (mourir de rire)
    - h{3,} (3+ h)
    - (ha){2,} (hahaha)
    - lol|lmao|mdr|ptdr
    """
    texte_lower = texte.lower()
    
    # Pattern pour ه{3,} (arabe - 3+ ه)
    if PATTERN_RIRES_ARABE.search(texte):
        match = PATTERN_RIRES_ARABE.search(texte)
        return True, f"rires_arabe({match.group()})"
    
    # Pattern pour (😂|🤣)+ (émoticônes de rire)
    if PATTERN_EMOJIS_RIRE.search(texte):
        match = PATTERN_EMOJIS_RIRE.search(texte)
        return True, f"emojis_rire({match.group()})"
    
    # Pattern pour (nmout|kanmout|anmout) (mourir de rire)
    if PATTERN_NMOUT.search(texte_lower):
        match = PATTERN_NMOUT.search(texte_lower)
        return True, f"mourir_rire({match.group()})"
    
    # Pattern pour h{3,} (lettres)
    if PATTERN_RIRES_LETTRES.search(texte_lower):
        match = PATTERN_RIRES_LETTRES.search(texte_lower)
        return True, f"rires_lettres({match.group()})"
    
    # Pattern pour hahaha
    if PATTERN_HAHAHA.search(texte_lower):
        match = PATTERN_HAHAHA.search(texte_lower)
        return True, f"rires_haha({match.group()})"
    
    # Pattern pour lol/lmao/mdr/ptdr
    if PATTERN_RIRES_ANGLAIS.search(texte_lower):
        match = PATTERN_RIRES_ANGLAIS.search(texte_lower)
        return True, f"rires_anglais({match.group()})"
    
    return False, None

def est_comique(commentaire):
    """
    Détecte si un commentaire est comique
    Retourne: (est_comique, label, keyword_trouve)
    """
    commentaire_clean = nettoyer_commentaire(commentaire)
    commentaire_lower = commentaire_clean.lower()
    
    # 1. Vérifier les mots à exclure (priorité)
    for mot in KEYWORDS_EXCLUDE:
        if mot in commentaire_lower or mot in commentaire_clean:
            return False, "NON_COMIQUE", None
    
    # 2. Vérifier les patterns de rire avec regex (NOUVEAUX PATTERNS)
    est_rire, type_rire = detecter_rire_par_regex(commentaire_clean)
    if est_rire:
        return True, "FUNNY", type_rire
    
    # 3. Vérifier les mots-clés du dictionnaire
    for mot in KEYWORDS_FUNNY:
        if mot in commentaire_clean:
            return True, "FUNNY", mot
    
    # 4. Cas particulier: commentaire très court avec beaucoup de points d'exclamation
    if len(commentaire_clean) <= 10 and commentaire_clean.count('!') >= 2:
        return True, "FUNNY", "exclamations"
    
    return False, "NON_COMIQUE", None

# ============================================
# SCRAPING DES COMMENTAIRES YOUTUBE
# ============================================
def get_youtube_comments(video_id, api_key, max_comments=2000):
    """
    Récupère les commentaires d'une vidéo YouTube
    """
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        comments = []
        next_page_token = None
        
        print(f"   📥 Récupération des commentaires...")
        
        while len(comments) < max_comments:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(100, max_comments - len(comments)),
                pageToken=next_page_token,
                textFormat='plainText'
            )
            response = request.execute()
            
            for item in response['items']:
                snippet = item['snippet']['topLevelComment']['snippet']
                comment = {
                    'video_id': video_id,
                    'author': snippet.get('authorDisplayName', 'inconnu'),
                    'comment': snippet.get('textDisplay', ''),
                    'likes': snippet.get('likeCount', 0),
                    'date': snippet.get('publishedAt', ''),
                    'reply_count': item['snippet']['totalReplyCount']
                }
                comments.append(comment)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
            
            time.sleep(0.3)  # Pause pour éviter les limites
        
        print(f"   ✅ {len(comments)} commentaires récupérés")
        return comments
    
    except HttpError as e:
        if e.resp.status == 403:
            print(f"   ❌ Erreur 403: API non activée ou quota dépassé")
            print(f"   → Vérifiez que YouTube Data API v3 est activée")
        else:
            print(f"   ❌ Erreur API: {e}")
        return []
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return []

# ============================================
# FILTRAGE ET CLASSIFICATION
# ============================================
def filtrer_commentaires_comiques(tous_commentaires):
    """
    Filtre les commentaires pour ne garder que les comiques
    """
    commentaires_comiques = []
    commentaires_non_comiques = []
    
    for comment in tous_commentaires:
        texte = comment['comment']
        est_drole, label, keyword = est_comique(texte)
        
        comment['est_comique'] = est_drole
        comment['label'] = label
        comment['keyword'] = keyword if keyword else ""
        
        if est_drole:
            commentaires_comiques.append(comment)
        else:
            commentaires_non_comiques.append(comment)
    
    return commentaires_comiques, commentaires_non_comiques

# ============================================
# SAUVEGARDE EN CSV
# ============================================
def sauvegarder_csv(commentaires_comiques, output_file="dataset_comique_darija.csv"):
    """
    Sauvegarde les commentaires comiques dans un CSV avec label et keyword
    """
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['label', 'keyword', 'video_id', 'comment', 'author', 
                     'likes', 'date', 'reply_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for comment in commentaires_comiques:
            writer.writerow({
                'label': comment['label'],
                'keyword': comment['keyword'],
                'video_id': comment['video_id'],
                'comment': comment['comment'],
                'author': comment['author'],
                'likes': comment['likes'],
                'date': comment['date'],
                'reply_count': comment['reply_count']
            })
    
    print(f"\n💾 Fichier CSV sauvegardé: {output_file}")
    return output_file

def sauvegarder_stats(commentaires_comiques, commentaires_non_comiques, output_file="stats_scraping.txt"):
    """
    Sauvegarde les statistiques du scraping
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("STATISTIQUES SCRAPING COMMENTAIRES COMIQUES DARIJA\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Nombre total de vidéos: {len(VIDEO_IDS)}\n")
        f.write(f"Total commentaires comiques: {len(commentaires_comiques)}\n")
        f.write(f"Total commentaires non comiques: {len(commentaires_non_comiques)}\n")
        total = len(commentaires_comiques) + len(commentaires_non_comiques)
        if total > 0:
            f.write(f"Taux de comiques: {len(commentaires_comiques)/total*100:.1f}%\n\n")
        
        # Statistiques par vidéo
        f.write("PAR VIDÉO:\n")
        f.write("-"*40 + "\n")
        
        videos_comiques = {}
        videos_totaux = {}
        
        for c in commentaires_comiques:
            videos_comiques[c['video_id']] = videos_comiques.get(c['video_id'], 0) + 1
        for c in commentaires_non_comiques:
            videos_totaux[c['video_id']] = videos_totaux.get(c['video_id'], 0) + 1
        
        # Fusionner
        for video_id in set(list(videos_comiques.keys()) + list(videos_totaux.keys())):
            comiques = videos_comiques.get(video_id, 0)
            totaux = videos_totaux.get(video_id, 0) + comiques
            pct = (comiques / totaux * 100) if totaux > 0 else 0
            f.write(f"  {video_id}: {comiques}/{totaux} ({pct:.1f}% comiques)\n")
        
        # Top keywords
        f.write("\nTOP KEYWORDS DÉTECTÉS:\n")
        f.write("-"*40 + "\n")
        keywords_count = {}
        for c in commentaires_comiques:
            kw = c['keyword']
            if kw:
                keywords_count[kw] = keywords_count.get(kw, 0) + 1
        
        for kw, count in sorted(keywords_count.items(), key=lambda x: x[1], reverse=True)[:20]:
            f.write(f"  {kw}: {count}\n")
        
        # Statistiques par type de détection (nouveaux patterns)
        f.write("\nDÉTECTION PAR TYPE DE PATTERN:\n")
        f.write("-"*40 + "\n")
        pattern_counts = {}
        for c in commentaires_comiques:
            kw = c['keyword']
            if kw and kw.startswith(('rires_', 'emojis_', 'mourir_')):
                # Extraire le type principal
                type_pattern = kw.split('(')[0] if '(' in kw else kw
                pattern_counts[type_pattern] = pattern_counts.get(type_pattern, 0) + 1
        
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {pattern}: {count}\n")
    
    print(f"💾 Statistiques sauvegardées: {output_file}")

# ============================================
# FONCTION PRINCIPALE
# ============================================
def main():
    print("="*60)
    print("🤣 SCRAPING COMMENTAIRES COMIQUES DARIJA")
    print("="*60)
    print(f"\n📹 Nombre de vidéos: {len(VIDEO_IDS)}")
    
    # Afficher la liste des vidéos
    for i, vid in enumerate(VIDEO_IDS, 1):
        print(f"   {i}. {vid}")
    
    # Afficher les nouveaux patterns
    print("\n🔧 NOUVEAUX PATTERNS DE DÉTECTION:")
    print("   ✅ ه{3,} (rires en arabe)")
    print("   ✅ (😂|🤣)+ (émoticônes de rire)")
    print("   ✅ (nmout|kanmout|anmout) (mourir de rire)")
    
    # Vérification de la clé API
    if API_KEY == "VOTRE_CLE_API_YOUTUBE":
        print("\n❌ ERREUR: Vous devez configurer votre clé API YouTube!")
        print("  Remplacez 'VOTRE_CLE_API_YOUTUBE' par votre vraie clé API")
        return
    
    # Récupération de tous les commentaires
    tous_commentaires = []
    for i, video_id in enumerate(VIDEO_IDS, 1):
        print(f"\n🎬 Vidéo {i}/{len(VIDEO_IDS)}: {video_id}")
        comments = get_youtube_comments(video_id, API_KEY, max_comments=2000)
        tous_commentaires.extend(comments)
        time.sleep(1)  # Pause entre les vidéos
    
    print(f"\n📊 TOTAL: {len(tous_commentaires)} commentaires récupérés")
    
    if not tous_commentaires:
        print("\n❌ Aucun commentaire récupéré. Vérifiez:")
        print("   1. Votre clé API est correcte")
        print("   2. YouTube Data API v3 est activée")
        print("   3. Les vidéos sont publiques")
        return
    
    # Filtrage
    print("\n🔍 Filtrage des commentaires comiques...")
    commentaires_comiques, commentaires_non_comiques = filtrer_commentaires_comiques(tous_commentaires)
    
    print(f"\n📊 RÉSULTATS:")
    print(f"   ✅ Commentaires comiques: {len(commentaires_comiques)}")
    print(f"   ❌ Commentaires non comiques: {len(commentaires_non_comiques)}")
    
    # Sauvegarde
    if commentaires_comiques:
        csv_file = sauvegarder_csv(commentaires_comiques)
        sauvegarder_stats(commentaires_comiques, commentaires_non_comiques)
        
        # Aperçu des premiers résultats
        print("\n" + "="*60)
        print("📝 APERÇU DES COMMENTAIRES COMIQUES:")
        print("="*60)
        for i, c in enumerate(commentaires_comiques[:10], 1):
            comment_court = c['comment'][:80] + "..." if len(c['comment']) > 80 else c['comment']
            print(f"\n{i}. [{c['keyword']}] {comment_court}")
    else:
        print("\n⚠️ Aucun commentaire comique détecté!")
        print("   → Vérifiez votre dictionnaire de mots comiques")
    
    print("\n✅ Script terminé!")

# ============================================
# EXÉCUTION
# ============================================
if __name__ == "__main__":
    main()