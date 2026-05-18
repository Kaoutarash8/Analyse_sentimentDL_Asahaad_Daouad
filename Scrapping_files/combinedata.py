import pandas as pd
import re
import emoji
import os

# ============================================
# CONFIGURATION
# ============================================
# Chemins des fichiers
base_path = r'C:\Users\asmae\Desktop\datasets_analyse_sentiment\love'

fichiers_a_fusionner = [
    os.path.join(base_path, 'amour_instagram.csv'),
    os.path.join(base_path, 'amour_admiration.csv')
]

output_file = os.path.join(base_path, 'data_amour.csv')

# ============================================
# FONCTIONS DE NETTOYAGE
# ============================================

def est_commentaire_vide(texte):
    """Vérifie si le commentaire est vide ou nul"""
    if pd.isna(texte):
        return True
    if not isinstance(texte, str):
        return True
    texte = texte.strip()
    return len(texte) == 0 or texte == '' or texte == 'nan' or texte == 'NaN'

def contient_seulement_emojis_ou_rires(texte):
    """
    Vérifie si le commentaire ne contient QUE:
    - des émojis
    - des rires (haha, hhh, lol, etc.)
    - des combinaisons des deux
    """
    if not isinstance(texte, str):
        return True
    
    texte = texte.strip()
    if len(texte) == 0:
        return True
    
    # 1. Vérifier les rires en lettres (hhh, haha, lol, lmao, mdr, ptdr)
    pattern_rires = re.compile(r'^(h{3,}|(ha){2,}|lol+|lmao+|mdr+|ptdr+)$', re.IGNORECASE)
    if pattern_rires.match(texte):
        return True
    
    # 2. Vérifier les rires en arabe (ههه)
    pattern_rires_arabe = re.compile(r'^ه{3,}$')
    if pattern_rires_arabe.match(texte):
        return True
    
    # 3. Vérifier les émojis uniquement
    try:
        texte_sans_emoji = emoji.replace_emoji(texte, '')
        texte_sans_emoji = texte_sans_emoji.strip()
        
        # Supprimer aussi les espaces, points, virgules
        texte_sans_emoji = re.sub(r'[\s\.\,\!\?]+', '', texte_sans_emoji)
        
        if len(texte_sans_emoji) == 0:
            return True
    except:
        pass
    
    # 4. Vérifier combinaison émojis + rires courts
    pattern_rires_emoji = re.compile(r'^(h{2,}|ه{2,}|lol+|😂|🤣|😭|😹|😍|❤️|💕)+$', re.IGNORECASE)
    if pattern_rires_emoji.match(texte):
        return True
    
    # 5. Vérifier si le texte ne contient que des émoticônes spécifiques
    only_emojis_pattern = re.compile(r'^[😂🤣😍❤️💕😘🥰😭😹😆😝🤪👍👏✨⭐🌟]+$')
    if only_emojis_pattern.match(texte):
        return True
    
    return False

def nettoyer_commentaire(texte):
    """Nettoie le commentaire"""
    if not isinstance(texte, str):
        return ""
    texte = texte.replace('\n', ' ').replace('\r', ' ').strip()
    texte = re.sub(r'\s+', ' ', texte)
    return texte

# ============================================
# CHARGEMENT ET FUSION
# ============================================

print("="*60)
print("🔄 FUSION DES FICHIERS CSV")
print("="*60)

# Lire et fusionner tous les fichiers
df_list = []
total_lignes = 0

for fichier in fichiers_a_fusionner:
    if os.path.exists(fichier):
        print(f"\n📁 Chargement: {os.path.basename(fichier)}")
        df_temp = pd.read_csv(fichier, encoding='utf-8-sig')
        print(f"   📊 {len(df_temp)} lignes trouvées")
        print(f"   📋 Colonnes: {list(df_temp.columns)}")
        df_list.append(df_temp)
        total_lignes += len(df_temp)
    else:
        print(f"\n⚠️ Fichier non trouvé: {fichier}")

if not df_list:
    print("\n❌ Aucun fichier trouvé!")
    exit()

# Fusionner
df = pd.concat(df_list, ignore_index=True)
print(f"\n📊 TOTAL AVANT NETTOYAGE: {len(df)} lignes")

# ============================================
# NETTOYAGE
# ============================================

print("\n🔍 Nettoyage des données...")

# S'assurer que la colonne 'comment' existe
if 'comment' not in df.columns:
    # Chercher une colonne qui contient 'comment'
    for col in df.columns:
        if 'comment' in col.lower():
            df.rename(columns={col: 'comment'}, inplace=True)
            print(f"✅ Colonne renommée: {col} -> comment")
            break

# S'assurer que la colonne 'label' existe
if 'label' not in df.columns:
    # Chercher une colonne qui contient 'label'
    for col in df.columns:
        if 'label' in col.lower():
            df.rename(columns={col: 'label'}, inplace=True)
            print(f"✅ Colonne renommée: {col} -> label")
            break

if 'comment' not in df.columns:
    raise Exception("Impossible de trouver la colonne des commentaires")

# Statistiques
stats = {
    'total': len(df),
    'supprimes_vides': 0,
    'supprimes_emojis_rires': 0,
    'gardes': 0
}

# Filtrer les lignes
lignes_a_garder = []
for idx, row in df.iterrows():
    commentaire = row['comment']
    
    # 1. Supprimer les commentaires vides
    if est_commentaire_vide(commentaire):
        stats['supprimes_vides'] += 1
        continue
    
    # 2. Supprimer les commentaires avec seulement émojis ou rires
    if contient_seulement_emojis_ou_rires(str(commentaire)):
        stats['supprimes_emojis_rires'] += 1
        continue
    
    # 3. Nettoyer le commentaire
    commentaire_clean = nettoyer_commentaire(str(commentaire))
    
    # 4. Vérifier si après nettoyage ce n'est pas vide
    if len(commentaire_clean) == 0:
        stats['supprimes_vides'] += 1
        continue
    
    # Garder la ligne
    row['comment'] = commentaire_clean
    lignes_a_garder.append(row)
    stats['gardes'] += 1

# Créer le nouveau DataFrame
df_clean = pd.DataFrame(lignes_a_garder)

# ============================================
# SAUVEGARDE
# ============================================

# Sauvegarder en CSV
df_clean.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n💾 Fichier sauvegardé: {output_file}")

# Sauvegarder aussi en Excel
output_excel = os.path.join(base_path, 'data_amour.xlsx')
df_clean.to_excel(output_excel, index=False)
print(f"💾 Aussi sauvegardé en Excel: {output_excel}")

# ============================================
# STATISTIQUES
# ============================================
print("\n" + "="*60)
print("📊 STATISTIQUES")
print("="*60)
print(f"📥 Lignes totales avant nettoyage: {stats['total']}")
print(f"🗑️  Supprimés (commentaires vides): {stats['supprimes_vides']}")
print(f"🗑️  Supprimés (seulement émojis/rires): {stats['supprimes_emojis_rires']}")
print(f"✅ Lignes gardées: {stats['gardes']}")

# Statistiques par label
if 'label' in df_clean.columns:
    print("\n📋 RÉPARTITION PAR LABEL:")
    for label, count in df_clean['label'].value_counts().items():
        print(f"   🏷️  {label}: {count}")

# ============================================
# APERÇU
# ============================================
print("\n" + "="*60)
print("📝 APERÇU DES DONNÉES (10 premiers)")
print("="*60)
for i, row in df_clean.head(10).iterrows():
    comment_court = row['comment'][:60] + "..." if len(row['comment']) > 60 else row['comment']
    label = row.get('label', 'N/A')
    print(f"{i+1}. [{label}] {comment_court}")

# ============================================
# EXEMPLES DE COMMENTAIRES SUPPRIMÉS
# ============================================
print("\n" + "="*60)
print("🗑️ EXEMPLES DE COMMENTAIRES SUPPRIMÉS")
print("="*60)

exemples_supprimes = []
for idx, row in df.iterrows():
    if len(exemples_supprimes) >= 10:
        break
    commentaire = row['comment']
    if not est_commentaire_vide(commentaire) and contient_seulement_emojis_ou_rires(str(commentaire)):
        comment_court = str(commentaire)[:50] + "..." if len(str(commentaire)) > 50 else str(commentaire)
        exemples_supprimes.append(comment_court)

for i, ex in enumerate(exemples_supprimes, 1):
    print(f"{i}. {ex}")

print("\n✅ Script terminé!")