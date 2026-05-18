import os
import re
import csv
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ============================================
# CONFIGURATION
# ============================================
API_KEY = "AIzaSyChwOwDewEhlgRlhJ-LyZgxw5inyxh_9l8"

VIDEO_IDS = [
    "-1zlgFgWyiI",
    "TLf7wGzmQ1w",
    "L_MKlTeZdl0",
    "b0DdeofxFoc",
    "FbxJsCGKeho",
    "c2tvGA9BDQ4",
    "hgvgxiEA7vQ",
    "21Z-LDGVZ2w",
    "AwoKr-IMu_g",
    "Ytm_ySdHkCk",
    "i3dZPHMsV_s",
    "SLw4ZszmOow",
    "98ytd2WQ0k4"
    "98ytd2WQ0k4"
    "8xGSctgALTk"
    "2VIOv5aGqN0"
]

# ============================================
# DICTIONNAIRE SENTIMENT LOVE (AMOUR/ADMIRATION)
# ============================================
KEYWORDS_LOVE = {
    # --- Émoticônes simples ---
    
   
    

    # --- Darija - كنبغي / نبغي ---
    "كنبغيك": "darija",
    "كنبغيك بزاف": "expression",
    "كنبغيكي": "darija",
    "نبغيك": "expression",
    "نبغيكي": "expression",
    "بغيتك": "expression",
    "بغيتكي": "expression",
    "كيبغيها": "expression",
    "كيبغيك": "expression",
    "كتبغيه": "expression",
    "كنبغيو": "expression",
    "كنبغيها": "expression",
    "بغاها": "expression",
    "بغاك": "expression",

    # --- Darija - mourir d'amour ---
    "كنموت عليك": "expression",
    "نموت عليك": "expression",
    "كنموت فيك": "expression",
    "نموت فيك": "expression",
    "كنموت عليها": "expression",
    "كنموت عليه": "expression",
    "نموت عليها": "expression",
    "نموت فيها": "expression",
    "كتموت عليك": "expression",
    "تموت عليك": "expression",

    # --- Arabe classique / MSA - حب / عشق ---
    "الحب": "arabic",
    "الحب ديالي": "expression",
    "العشق": "arabic",
    "عشقتك": "arabic",
    "عشقتكي": "arabic",
    "عاشق": "arabic",
    "عاشقة": "arabic",
    "عشاق": "word",
    "معشوق": "arabic",
    "معشوقة": "arabic",
    "هوى": "arabic",
    "غرام": "arabic",
    "شوق": "arabic",
    "مشتاق": "arabic",
    "مشتاقة": "arabic",

    # --- Je t'aime ---
    "نحبك": "arabic",
    "أحبك": "arabic",
    "نحبكي": "arabic",
    "احبكي": "arabic",
    "نحبك بزاف": "expression",
    "احبك بزاف": "expression",
    "أحبكِ": "arabic",
    "نحبو": "arabic",
    "نحبها": "arabic",
    "حبيبي": "word",
    "حبيبتي": "word",
    "حبيبي والله": "expression",
    "حبي": "word",
    "يا حبي": "expression",

    # --- Darija - termes tendres ---
    "روحي": "darija",
    "يا روحي": "expression",
    "قلبي": "darija",
    "يا قلبي": "expression",
    "عيني": "darija",
    "يا عيني": "expression",
    "نوري": "darija",
    "يا نوري": "expression",
    "حياتي": "darija",
    "يا حياتي": "expression",
    "عمري": "darija",
    "يا عمري": "expression",
    "غالي": "word",
    "غالية": "word",
    "يا غالية": "expression",

    # --- Admiration intense ---
    "مجنون بيك": "expression",
    "مجنونة بيك": "expression",
    "هائم بيك": "expression",
    "هائمة بيك": "expression",
    "ولهان بيك": "expression",
    "ولهانة بيك": "expression",
    "فاتنتي": "word",
    "فتنتيني": "expression",
    "سحرتيني": "expression",
    "سحرتني": "expression",

    # --- Expressions francophones mélangées (code-switching) ---
    "je t'aime": "french",
    "je t'adore": "french",
    "t'es trop belle": "french",
    "mon amour": "french",
    "ma chérie": "french",
    "mon coeur": "french",
    "t'es magnifique": "french",
}

# ============================================
# DICTIONNAIRE SENTIMENT POSITIVE (COMPLIMENT/ADMIRATION)
# ============================================
KEYWORDS_POSITIVE = {
    # --- Darija - qualités physiques / apparence ---
    "زوين": "darija",
    "زوينة": "darija",
    "زوينين": "darija",
    "مزيان": "darija",
    "مزيانة": "darija",
    "غزالة": "darija",
    "الغزالة": "darija",
    "غزاال": "darija",
    "غزاالة": "darija",
    "منورة": "darija",
    "منور": "darija",
    "منورين": "darija",
    "عزيزة": "word",
    "عزيز": "word",
    "بهية": "darija",
    "فنة" : "darija",
    "حبييت" : "darija",
    "بهي": "darija",
    "قنبولة": "darija",
    "قمر": "word",
    "يا قمر": "expression",
    "بنت الحلال": "expression",
    "ولد الحلال": "expression",
     "شكرا" : "expression",

    # --- Darija - intensité / excellence ---
    "واعر": "darija",
    "واعرة": "darija",
    "واعرين": "darija",
    "واعر بزاف": "expression",
    "مذاق واعر": "expression",
    "هضرة واعرة": "expression",
    "مشا واعر": "expression",
    "طلعت واعر": "expression",
    "هاشومة واعرة": "expression",
    "شحال واعر": "expression",
    "ها الخدمة واعرة": "expression",

    # --- Arabe - élégance / beauté ---
    "رائع": "arabic",
    "رائعة": "arabic",
    "رائعين": "arabic",
    "جميل": "arabic",
    "جميلة": "arabic",
    "جميلين": "arabic",
    "روعة": "arabic",
    "ولا اروع": "expression",
    "ولا أروع": "expression",
    "متألقة": "expression",
    "متألق": "expression",
    "ممتاز": "arabic",
    "ممتازة": "arabic",
    "أنيق": "arabic",
    "أنيقة": "arabic",
    "راقي": "arabic",
    "راقية": "arabic",
    "راقيين": "arabic",
    "فاخر": "word",
    "فاخرة": "word",
    "هادف": "word",
    "هادفة": "word",

    # --- Darija - goût / qualité culinaire ou contenu ---
    "بنينة": "expression",
    "بنين": "darija",
    "لذيذة": "word",
    "لذيذ": "word",
    "كتشهي": "expression",
    "يتشهى": "expression",
    "واش كتشهي": "expression",
    "كتجيب لي الشهية": "expression",
    "مذاق بنين": "expression",
    "شهيوة": "darija",
    "شهيو": "darija",

    # --- Darija - expressions de félicitation ---
    "كتحمق": "expression",
    "جات فنة كتحمق": "expression",
    "جات غزالة": "expression",
    "حادكة": "expression",
    "هماوية": "expression",
    "ناجحة": "expression",
    "ناجح": "expression",
    "مبدع": "word",
    "مبدعة": "word",
    "مبدعين": "word",
    "محترفة": "word",
    "محترف": "word",
    "مهضومة": "darija",
    "مهضوم": "darija",
    "مهضوما": "darija",

    # --- Bénédictions islamiques ---
    "تبارك الله": "expression",
    "ماشاء الله": "expression",
    "ما شاء الله": "expression",
    "اللهم بارك": "expression",
    "الله يبارك": "expression",
    "الله يكمل بالخير": "expression",
    "الله يتمم على خير": "expression",
    "الله يسر الأمور": "expression",
    "الله يعطيك الصحة": "expression",
    "الله يحفظك": "expression",
    "الله يحفظك ويسعدك": "expression",
    "الله ينورك ويفرحك": "expression",
    "الله يرزقك": "expression",
    "الله يعطيك ما تتمنى": "expression",
    "بارك الله فيك": "expression",
    "بارك الله فيكم": "expression",
    "حفظك الله": "expression",
    "ربي يحفظك": "expression",
    "ربي يسعدك": "expression",
    "ربي يعطيك الصحة": "expression",
    "ربي يوفقك": "expression",
    "يسلامو": "darija",
    "يسلمو": "darija",
    "يعطيك الصحة": "expression",
    "يعطيكم الصحة": "expression",

    # --- Félicitations générales ---
    "مبروك": "expression",
    "مبارك": "expression",
    "مبارك عليك": "expression",
    "ألف مبروك": "expression",
    "الف مبروك": "expression",
    "تهانينا": "arabic",
    "أحسنت": "arabic",
    "برافو": "word",
    "bravo": "french",
    "سعيد": "expression",

    # --- Appréciation du contenu ---
    "عجبني": "expression",
    "عجبني بزاف": "expression",
    "عجبنا": "expression",
    "هاد شي زوين": "expression",
    "هاد شي راقي": "expression",
    "هاد المحتوى زوين": "expression",
    "كنحب هاد النوع": "expression",
    "زيدو فهاد النوع": "expression",
    "زيدو من هاد": "expression",
    "هاد الفيديو واعر": "expression",
    "كنتيبع هاد": "expression",
    "مزيان بزاف": "expression",
    "شكرا بزاف": "expression",
    "شكرا جزيلا": "arabic",
    "شكرا على المحتوى": "expression",
    "مرسي بزاف": "darija",
    "مرسي": "darija",
    "merci": "french",
    "استمتعت": "arabic",
    "استمتعنا": "arabic",

    # --- Style / élégance ---
    "ستايل واعر": "expression",
    "ستايل مزيان": "expression",
    "اللباس واعر": "expression",
    "التيمة واعرة": "expression",
    "الديكور واعر": "expression",
    "الألوان واعرة": "expression",

    # --- Francophones mélangées (code-switching) ---
    "trop belle": "french",
    "trop beau": "french",
    "magnifique": "french",
    "superbe": "french",
    "parfait": "french",
    "excellent": "french",
    "incroyable": "french",
    "c'est beau": "french",
    "c'est bien": "french",
    "top": "french",
    "chapeau": "french",
}

# ============================================
# EXPRESSIONS RÉGULIÈRES (rires - à ignorer)
# ============================================
PATTERNS_TO_IGNORE = [
    re.compile(r'ه{3,}'),
    re.compile(r'h{3,}', re.I),
    re.compile(r'(ha){2,}', re.I),
    re.compile(r'(😂|🤣|😭|😹)+'),
    re.compile(r'\b(lol+|lmao+|mdr+|ptdr+)\b', re.I),
    re.compile(r'\b(nmout|kanmout|anmout)\b', re.I)
]

def est_rire_seulement(commentaire):
    commentaire_clean = commentaire.strip()
    if len(commentaire_clean) < 2:
        return False
    for pattern in PATTERNS_TO_IGNORE:
        if pattern.search(commentaire_clean):
            sans_pattern = pattern.sub('', commentaire_clean).strip()
            if len(sans_pattern) == 0 or len(sans_pattern) < 3:
                return True
    return False

# ============================================
# FONCTIONS DE DÉTECTION
# ============================================
def detecter_sentiments(commentaire):
    love_detected = False
    love_keyword = ""
    love_type = ""
    positive_detected = False
    positive_keyword = ""
    positive_type = ""

    for keyword, kw_type in KEYWORDS_LOVE.items():
        if keyword in commentaire:
            love_detected = True
            love_keyword = keyword
            love_type = kw_type
            break

    for keyword, kw_type in KEYWORDS_POSITIVE.items():
        if keyword in commentaire:
            positive_detected = True
            positive_keyword = keyword
            positive_type = kw_type
            break

    return love_detected, love_keyword, love_type, positive_detected, positive_keyword, positive_type

# ============================================
# SCRAPING DES COMMENTAIRES YOUTUBE
# ============================================
def get_youtube_comments(video_id, api_key, max_comments=500):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        comments = []
        next_page_token = None

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
            time.sleep(0.3)

        return comments

    except HttpError as e:
        print(f"   ❌ Erreur API: {e}")
        return []
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return []

# ============================================
# SAUVEGARDE DES CSV
# ============================================
def sauvegarder_csv_love(commentaires, output_file="amour_admiration.csv"):
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['label', 'keyword', 'type', 'video_id', 'comment', 'author', 'likes', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for comment in commentaires:
            writer.writerow({
                'label': 'LOVE',
                'keyword': comment['keyword'],
                'type': comment['type'],
                'video_id': comment['video_id'],
                'comment': comment['comment'],
                'author': comment['author'],
                'likes': comment['likes'],
                'date': comment['date']
            })
    print(f"\n💾 Fichier CSV LOVE: {output_file} ({len(commentaires)} commentaires)")

def sauvegarder_csv_positive(commentaires, output_file="positif_compliment.csv"):
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['label', 'keyword', 'type', 'video_id', 'comment', 'author', 'likes', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for comment in commentaires:
            writer.writerow({
                'label': 'POSITIVE',
                'keyword': comment['keyword'],
                'type': comment['type'],
                'video_id': comment['video_id'],
                'comment': comment['comment'],
                'author': comment['author'],
                'likes': comment['likes'],
                'date': comment['date']
            })
    print(f"💾 Fichier CSV POSITIVE: {output_file} ({len(commentaires)} commentaires)")

def sauvegarder_stats(commentaires_love, commentaires_positive, output_file="stats_scraping.txt"):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("STATISTIQUES SCRAPING COMMENTAIRES DARIJA\n")
        f.write("="*60 + "\n\n")
        f.write(f"Nombre de vidéos: {len(VIDEO_IDS)}\n")
        f.write(f"Commentaires LOVE (amour/admiration): {len(commentaires_love)}\n")
        f.write(f"Commentaires POSITIVE (compliment): {len(commentaires_positive)}\n")

        f.write("\nTYPES LOVE:\n" + "-"*40 + "\n")
        types_love = {}
        for c in commentaires_love:
            t = c['type']
            types_love[t] = types_love.get(t, 0) + 1
        for t, count in sorted(types_love.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {t}: {count}\n")

        f.write("\nTYPES POSITIVE:\n" + "-"*40 + "\n")
        types_positive = {}
        for c in commentaires_positive:
            t = c['type']
            types_positive[t] = types_positive.get(t, 0) + 1
        for t, count in sorted(types_positive.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {t}: {count}\n")

        f.write("\nTOP KEYWORDS LOVE:\n" + "-"*40 + "\n")
        keywords_love = {}
        for c in commentaires_love:
            kw = c['keyword']
            keywords_love[kw] = keywords_love.get(kw, 0) + 1
        for kw, count in sorted(keywords_love.items(), key=lambda x: x[1], reverse=True)[:20]:
            f.write(f"  {kw}: {count}\n")

        f.write("\nTOP KEYWORDS POSITIVE:\n" + "-"*40 + "\n")
        keywords_positive = {}
        for c in commentaires_positive:
            kw = c['keyword']
            keywords_positive[kw] = keywords_positive.get(kw, 0) + 1
        for kw, count in sorted(keywords_positive.items(), key=lambda x: x[1], reverse=True)[:20]:
            f.write(f"  {kw}: {count}\n")

        f.write("\nPAR VIDÉO:\n" + "-"*40 + "\n")
        videos_love = {}
        videos_positive = {}
        for c in commentaires_love:
            videos_love[c['video_id']] = videos_love.get(c['video_id'], 0) + 1
        for c in commentaires_positive:
            videos_positive[c['video_id']] = videos_positive.get(c['video_id'], 0) + 1
        for video_id in VIDEO_IDS:
            love_count = videos_love.get(video_id, 0)
            pos_count = videos_positive.get(video_id, 0)
            f.write(f"  {video_id}: LOVE={love_count}, POSITIVE={pos_count}\n")

    print(f"💾 Statistiques: {output_file}")

# ============================================
# FONCTION PRINCIPALE
# ============================================
def main():
    print("="*60)
    print("💖 SCRAPING COMMENTAIRES DARIJA - LOVE & POSITIVE")
    print("="*60)
    print(f"\n📹 Nombre de vidéos: {len(VIDEO_IDS)}")
    print(f"📚 Mots-clés LOVE: {len(KEYWORDS_LOVE)}")
    print(f"📚 Mots-clés POSITIVE: {len(KEYWORDS_POSITIVE)}")

    print("\n📋 Liste des vidéos:")
    for i, vid in enumerate(VIDEO_IDS, 1):
        print(f"   {i}. https://youtu.be/{vid}")

    if API_KEY == "VOTRE_CLE_API_YOUTUBE":
        print("\n❌ ERREUR: Configurez votre clé API YouTube!")
        return

    tous_commentaires = []
    for i, video_id in enumerate(VIDEO_IDS, 1):
        print(f"\n🎬 Vidéo {i}/{len(VIDEO_IDS)}: {video_id}")
        comments = get_youtube_comments(video_id, API_KEY, max_comments=500)
        tous_commentaires.extend(comments)
        time.sleep(1)

    print(f"\n📊 TOTAL: {len(tous_commentaires)} commentaires récupérés")

    if not tous_commentaires:
        print("\n❌ Aucun commentaire récupéré.")
        return

    print("\n🔍 Classification des sentiments...")

    commentaires_love = []
    commentaires_positive = []
    commentaires_ignores = 0

    for comment in tous_commentaires:
        texte = comment['comment']
        if est_rire_seulement(texte):
            commentaires_ignores += 1
            continue

        love_detected, love_kw, love_type, positive_detected, positive_kw, positive_type = detecter_sentiments(texte)

        if love_detected:
            commentaires_love.append({
                'video_id': comment['video_id'],
                'author': comment['author'],
                'comment': texte,
                'likes': comment['likes'],
                'date': comment['date'],
                'keyword': love_kw,
                'type': love_type
            })

        if positive_detected:
            commentaires_positive.append({
                'video_id': comment['video_id'],
                'author': comment['author'],
                'comment': texte,
                'likes': comment['likes'],
                'date': comment['date'],
                'keyword': positive_kw,
                'type': positive_type
            })

    print(f"\n📊 RÉSULTATS FINAUX:")
    print(f"   💖 LOVE (amour/admiration): {len(commentaires_love)} commentaires")
    print(f"   👍 POSITIVE (compliment): {len(commentaires_positive)} commentaires")
    print(f"   🚫 Ignorés (rires seulement): {commentaires_ignores}")

    if commentaires_love:
        sauvegarder_csv_love(commentaires_love)
    else:
        print("\n⚠️ Aucun commentaire LOVE détecté")

    if commentaires_positive:
        sauvegarder_csv_positive(commentaires_positive)
    else:
        print("⚠️ Aucun commentaire POSITIVE détecté")

    sauvegarder_stats(commentaires_love, commentaires_positive)

    if commentaires_love:
        print("\n" + "="*60)
        print("📝 APERÇU COMMENTAIRES LOVE (5 premiers):")
        print("="*60)
        for i, c in enumerate(commentaires_love[:5], 1):
            comment_court = c['comment'][:60] + "..." if len(c['comment']) > 60 else c['comment']
            print(f"{i}. [{c['keyword']}] {comment_court}")

    if commentaires_positive:
        print("\n" + "="*60)
        print("📝 APERÇU COMMENTAIRES POSITIVE (5 premiers):")
        print("="*60)
        for i, c in enumerate(commentaires_positive[:5], 1):
            comment_court = c['comment'][:60] + "..." if len(c['comment']) > 60 else c['comment']
            print(f"{i}. [{c['keyword']}] {comment_court}")

    print("\n✅ Script terminé!")
    print(f"\n📁 Fichiers générés:")
    print(f"   - amour_admiration.csv")
    print(f"   - positif_compliment.csv")
    print(f"   - stats_scraping.txt")

if __name__ == "__main__":
    main()