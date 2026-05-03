
import xmlrpc.client
import os

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
ODOO_URL      = "http://localhost:8019"
ODOO_DB       = "Adm"          # Nom de ta base de données
ODOO_USER     = "amrn.sd2005@outlook.fr"           # Ton login Odoo
ODOO_PASSWORD = "admin123"           # Ton mot de passe Odoo

CIS_FILE      = "CIS_bdpm.txt"
COMPO_FILE    = "CIS_COMPO_bdpm.txt"
# ──────────────────────────────────────────────────────────────────────────────


def load_medications():
    """Charge et filtre les médicaments commercialisés avec leur substance active."""
    print("Lecture des fichiers BDPM...")

    # Médicaments commercialisés
    meds = {}
    with open(CIS_FILE, 'r', encoding='latin-1') as f:
        for line in f:
            cols = line.strip().split('\t')
            if len(cols) >= 7 and cols[6] == 'Commercialisée':
                meds[cols[0]] = cols[1]

    print(f"  → {len(meds)} médicaments commercialisés trouvés")

    # Substances actives
    compo = {}
    with open(COMPO_FILE, 'r', encoding='latin-1') as f:
        for line in f:
            cols = line.strip().split('\t')
            if len(cols) >= 7 and cols[6] == 'SA' and cols[0] not in compo:
                compo[cols[0]] = cols[3]

    print(f"  → {len(compo)} substances actives trouvées")

    # Dédupliquer par substance active
    seen_substances = set()
    unique_meds = []
    for cis, nom in meds.items():
        substance = compo.get(cis, '')
        if substance and substance not in seen_substances:
            seen_substances.add(substance)
            unique_meds.append((nom, substance))

    print(f"  → {len(unique_meds)} médicaments uniques (par substance active)\n")
    return unique_meds


def connect_odoo():
    """Connexion à Odoo via XML-RPC."""
    print("🔌 Connexion à Odoo...")
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise Exception("Connexion échouée. Vérifiez vos identifiants.")
    print(f"  → Connecté (uid={uid})\n")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models


def import_medications(uid, models, medications):
    """Importe les médicaments dans Odoo."""
    print("Import des médicaments...")

    # Récupérer les médicaments déjà existants pour éviter les doublons
    existing = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'medical.medication', 'search_read',
        [[]], {'fields': ['name'], 'limit': 0}
    )
    existing_names = {r['name'] for r in existing}
    print(f"  → {len(existing_names)} médicaments déjà présents dans Odoo")

    # Filtrer ceux à importer
    to_import = [
        (nom, substance)
        for nom, substance in medications
        if nom not in existing_names
    ]
    print(f"  → {len(to_import)} médicaments à importer\n")

    if not to_import:
        print("Aucun médicament à importer (tous déjà présents).")
        return

    # Import par batch de 100
    batch_size = 100
    total = len(to_import)
    imported = 0
    errors = 0

    for i in range(0, total, batch_size):
        batch = to_import[i:i + batch_size]
        vals_list = [
            {'name': nom, 'active_ingredient': substance}
            for nom, substance in batch
        ]
        try:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'medical.medication', 'create',
                [vals_list]
            )
            imported += len(batch)
            print(f"  ✔ {imported}/{total} importés...", end='\r')
        except Exception as e:
            errors += len(batch)
            print(f"\n  ⚠ Erreur batch {i}: {e}")

    print(f"\n\n✅ Import terminé: {imported} médicaments importés, {errors} erreurs.")


def main():
    print("=" * 55)
    print("  Import BDPM → Odoo | medical.medication")
    print("=" * 55 + "\n")

    if not os.path.exists(CIS_FILE) or not os.path.exists(COMPO_FILE):
        print("Fichiers BDPM introuvables. Mets les fichiers dans le même dossier que ce script.")
        return

    medications = load_medications()
    uid, models = connect_odoo()
    import_medications(uid, models, medications)


if __name__ == "__main__":
    main()