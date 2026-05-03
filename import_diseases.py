
import xmlrpc.client

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
ODOO_URL      = "http://localhost:8019"
ODOO_DB       = "Adm"
ODOO_USER     = "amrn.sd2005@outlook.fr"
ODOO_PASSWORD = "admin123"
# ──────────────────────────────────────────────────────────────────────────────

# Maladies CIM-10 avec leurs substances actives associées
DISEASES = [
    # (code, nom, description, [substances_actives])
    ("A09",  "Diarrhée et gastro-entérite infectieuse",     "Infection intestinale aiguë",                          ["LOPÉRAMIDE", "RACÉCADOTRIL", "NIFUROXAZIDE"]),
    ("A15",  "Tuberculose respiratoire",                     "Infection pulmonaire à Mycobacterium tuberculosis",    ["ISONIAZIDE", "RIFAMPICINE", "PYRAZINAMIDE", "ÉTHAMBUTOL"]),
    ("A37",  "Coqueluche",                                   "Infection respiratoire bactérienne très contagieuse", ["AZITHROMYCINE", "CLARITHROMYCINE"]),
    ("A39",  "Infection à méningocoque",                     "Méningite bactérienne grave",                         ["CEFTRIAXONE", "PÉNICILLINE G"]),
    ("A41",  "Septicémie",                                   "Infection bactérienne généralisée dans le sang",      ["AMOXICILLINE", "CEFTRIAXONE", "VANCOMYCINE"]),
    ("A46",  "Érysipèle",                                    "Infection cutanée streptococcique",                   ["AMOXICILLINE", "ÉRYTHROMYCINE"]),
    ("A54",  "Infection gonococcique",                       "Infection sexuellement transmissible à gonocoque",    ["CEFTRIAXONE", "AZITHROMYCINE"]),
    ("A60",  "Infection herpétique anogénitale",             "Herpès génital causé par HSV-2",                      ["ACICLOVIR", "VALACICLOVIR", "FAMCICLOVIR"]),
    ("A90",  "Dengue",                                       "Maladie virale transmise par les moustiques",         ["PARACÉTAMOL"]),
    ("B00",  "Infection à virus herpès",                     "Herpès labial ou cutané",                             ["ACICLOVIR", "VALACICLOVIR"]),
    ("B01",  "Varicelle",                                    "Infection virale avec éruption cutanée vésiculeuse",  ["ACICLOVIR", "CALAMINE"]),
    ("B02",  "Zona",                                         "Réactivation du virus varicelle-zona",                ["VALACICLOVIR", "ACICLOVIR", "FAMCICLOVIR"]),
    ("B05",  "Rougeole",                                     "Maladie virale infantile contagieuse",                ["PARACÉTAMOL", "VITAMINE A"]),
    ("B15",  "Hépatite aiguë A",                             "Inflammation du foie causée par le virus HAV",        ["PARACÉTAMOL"]),
    ("B16",  "Hépatite aiguë B",                             "Inflammation du foie causée par le virus HBV",        ["TÉNOFOVIR", "ENTÉCAVIR", "LAMIVUDINE"]),
    ("B18",  "Hépatite virale chronique",                    "Hépatite B ou C chronique",                           ["TÉNOFOVIR", "ENTÉCAVIR", "SOFOSBUVIR", "RIBAVIRINE"]),
    ("B20",  "Maladie par VIH",                              "Infection par le virus de l'immunodéficience humaine",["ABACAVIR", "LAMIVUDINE", "TÉNOFOVIR", "EFAVIRENZ"]),
    ("B37",  "Candidose",                                    "Infection fongique à Candida",                        ["FLUCONAZOLE", "MICONAZOLE", "NYSTATINE"]),
    ("B50",  "Paludisme à Plasmodium falciparum",            "Paludisme grave transmis par les moustiques",         ["ARTÉMÉTHER", "QUININE", "CHLOROQUINE"]),
    ("B86",  "Gale",                                         "Infection cutanée parasitaire",                       ["PERMÉTHRINE", "IVERMECTINE", "BENZOATE DE BENZYLE"]),
    ("C34",  "Tumeur maligne des bronches et du poumon",     "Cancer du poumon primitif",                           ["CARBOPLATINE", "PACLITAXEL", "ERLOTINIB", "PEMBROLIZUMAB"]),
    ("C50",  "Tumeur maligne du sein",                       "Cancer du sein",                                      ["TAMOXIFÈNE", "TRASTUZUMAB", "LETROZOLE", "DOCÉTAXEL"]),
    ("C61",  "Tumeur maligne de la prostate",                "Cancer de la prostate",                               ["LEUPRORÉLINE", "BICALUTAMIDE", "ABIRATÉRONE"]),
    ("C92",  "Leucémie myéloïde",                            "Cancer des cellules souches hématopoïétiques",        ["IMATINIB", "DASATINIB", "CYTARABINE"]),
    ("E03",  "Hypothyroïdie",                                "Insuffisance de production d'hormones thyroïdiennes", ["LÉVOTHYROXINE"]),
    ("E05",  "Hyperthyroïdie",                               "Excès d'hormones thyroïdiennes",                      ["CARBIMAZOLE", "PROPYLTHIOURACILE", "PROPRANOLOL"]),
    ("E10",  "Diabète de type 1",                            "Diabète insulinodépendant auto-immun",                ["INSULINE GLARGINE", "INSULINE ASPARTE", "INSULINE LISPRO"]),
    ("E11",  "Diabète de type 2",                            "Diabète non insulinodépendant",                       ["METFORMINE", "GLIBENCLAMIDE", "SITAGLIPTINE", "EMPAGLIFLOZINE"]),
    ("E66",  "Obésité",                                      "Excès de masse corporelle avec IMC ≥ 30",             ["ORLISTAT"]),
    ("E78",  "Hyperlipidémie",                               "Excès de cholestérol ou triglycérides dans le sang",  ["ATORVASTATINE", "SIMVASTATINE", "ROSUVASTATINE", "FÉNOFIBRATE"]),
    ("F00",  "Maladie d'Alzheimer",                          "Démence neurodégénérative progressive",               ["DONÉPÉZIL", "RIVASTIGMINE", "MÉMANTINE"]),
    ("F10",  "Troubles liés à l'alcool",                     "Dépendance ou abus d'alcool",                         ["NALTREXONE", "ACAMPROSATE", "DISULFIRAME"]),
    ("F20",  "Schizophrénie",                                "Trouble psychotique chronique",                       ["HALOPÉRIDOL", "RISPÉRIDONE", "CLOZAPINE", "OLANZAPINE"]),
    ("F31",  "Trouble bipolaire",                            "Alternance d'épisodes maniaques et dépressifs",       ["LITHIUM", "VALPROATE", "LAMOTRIGINE", "QUÉTIAPINE"]),
    ("F32",  "Épisode dépressif",                            "Dépression unipolaire",                               ["SERTRALINE", "FLUOXÉTINE", "VENLAFAXINE", "ESCITALOPRAM"]),
    ("F40",  "Troubles phobiques anxieux",                   "Anxiété et phobies",                                  ["SERTRALINE", "ALPRAZOLAM", "DIAZÉPAM", "BUSPIRONE"]),
    ("F51",  "Insomnie",                                     "Troubles du sommeil non organiques",                  ["ZOLPIDEM", "ZOPICLONE", "MÉLATONINE"]),
    ("G20",  "Maladie de Parkinson",                         "Trouble neurodégénératif du mouvement",               ["LÉVODOPA", "PRAMIPEXOLE", "ROPINIROLE", "SÉLÉGILINE"]),
    ("G35",  "Sclérose en plaques",                          "Maladie auto-immune du système nerveux central",      ["INTERFÉRON BÊTA", "NATALIZUMAB", "FINGOLIMOD"]),
    ("G40",  "Épilepsie",                                    "Troubles convulsifs récurrents",                      ["VALPROATE", "LÉVÉTIRACÉTAM", "CARBAMAZÉPINE", "LAMOTRIGINE"]),
    ("G43",  "Migraine",                                     "Céphalées récurrentes sévères",                       ["SUMATRIPTAN", "PARACÉTAMOL", "IBUPROFÈNE", "PROPRANOLOL"]),
    ("G47",  "Troubles du sommeil",                          "Insomnie, hypersomnie ou apnée du sommeil",           ["ZOLPIDEM", "MÉLATONINE", "MODAFINIL"]),
    ("H10",  "Conjonctivite",                                "Inflammation de la conjonctive oculaire",             ["CHLORAMPHÉNICOL", "AZITHROMYCINE", "TOBRAMYCINE"]),
    ("H52",  "Troubles de la réfraction",                    "Myopie, hypermétropie, astigmatisme",                 []),
    ("H91",  "Perte d'audition",                             "Hypoacousie ou surdité",                              []),
    ("I10",  "Hypertension artérielle",                      "Pression artérielle chroniquement élevée",            ["AMLODIPINE", "RAMIPRIL", "BISOPROLOL", "HYDROCHLOROTHIAZIDE", "LOSARTAN"]),
    ("I20",  "Angine de poitrine",                           "Douleur thoracique par insuffisance coronarienne",    ["TRINITRINE", "BISOPROLOL", "AMLODIPINE", "ASPIRINE"]),
    ("I21",  "Infarctus aigu du myocarde",                   "Nécrose du muscle cardiaque par obstruction coronaire",["ASPIRINE", "CLOPIDOGREL", "HÉPARINE", "ATORVASTATINE"]),
    ("I48",  "Fibrillation auriculaire",                     "Trouble du rythme cardiaque",                         ["WARFARINE", "APIXABAN", "BISOPROLOL", "DIGOXINE", "AMIODARONE"]),
    ("I50",  "Insuffisance cardiaque",                       "Incapacité du cœur à pomper suffisamment de sang",    ["FUROSÉMIDE", "RAMIPRIL", "BISOPROLOL", "SPIRONOLACTONE"]),
    ("I63",  "Infarctus cérébral",                           "AVC ischémique par obstruction d'une artère cérébrale",["ASPIRINE", "CLOPIDOGREL", "ALTÉPLASE", "WARFARINE"]),
    ("I64",  "AVC sans précision",                           "Accident vasculaire cérébral",                        ["ASPIRINE", "RAMIPRIL", "ATORVASTATINE"]),
    ("J00",  "Rhinopharyngite aiguë",                        "Rhume commun",                                        ["PARACÉTAMOL", "IBUPROFÈNE", "PSEUDOÉPHÉDRINE"]),
    ("J02",  "Pharyngite aiguë",                             "Infection de la gorge",                               ["AMOXICILLINE", "PARACÉTAMOL", "IBUPROFÈNE"]),
    ("J03",  "Amygdalite aiguë",                             "Infection des amygdales",                             ["AMOXICILLINE", "PARACÉTAMOL", "ÉRYTHROMYCINE"]),
    ("J06",  "Infection aiguë des voies respiratoires supérieures","Infection ORL aiguë",                           ["PARACÉTAMOL", "IBUPROFÈNE", "AMOXICILLINE"]),
    ("J10",  "Grippe",                                       "Infection virale respiratoire saisonnière",           ["PARACÉTAMOL", "IBUPROFÈNE", "OSELTAMIVIR"]),
    ("J18",  "Pneumonie",                                    "Infection pulmonaire aiguë",                          ["AMOXICILLINE", "CEFTRIAXONE", "AZITHROMYCINE", "LÉVOFLOXACINE"]),
    ("J20",  "Bronchite aiguë",                              "Inflammation aiguë des bronches",                     ["PARACÉTAMOL", "IBUPROFÈNE", "AMOXICILLINE"]),
    ("J30",  "Rhinite allergique",                           "Allergie nasale saisonnière ou persistante",          ["CÉTIRIZINE", "LORATADINE", "BÉCLOMÉTASONE NASALE", "MONTÉLUKAST"]),
    ("J32",  "Sinusite chronique",                           "Inflammation chronique des sinus",                    ["AMOXICILLINE", "BÉCLOMÉTASONE NASALE", "IBUPROFÈNE"]),
    ("J44",  "Bronchopneumopathie chronique obstructive",    "BPCO - maladie respiratoire chronique",               ["SALBUTAMOL", "TIOTROPIUM", "FORMOTÉROL", "FLUTICASONE"]),
    ("J45",  "Asthme",                                       "Maladie respiratoire chronique avec obstruction bronchique",["SALBUTAMOL", "BÉCLOMÉTASONE", "MONTÉLUKAST", "FORMOTÉROL"]),
    ("K21",  "Reflux gastro-oesophagien",                    "Remontée acide de l'estomac vers l'œsophage",         ["OMÉPRAZOLE", "PANTOPRAZOLE", "ÉSOMÉPRAZOLE", "RANITIDINE"]),
    ("K25",  "Ulcère gastrique",                             "Lésion de la paroi de l'estomac",                     ["OMÉPRAZOLE", "AMOXICILLINE", "CLARITHROMYCINE"]),
    ("K29",  "Gastrite",                                     "Inflammation de la muqueuse gastrique",               ["OMÉPRAZOLE", "HYDROXYDE D'ALUMINIUM", "MÉTRONIDAZOLE"]),
    ("K35",  "Appendicite aiguë",                            "Inflammation de l'appendice",                         ["AMOXICILLINE", "MÉTRONIDAZOLE", "CEFTRIAXONE"]),
    ("K40",  "Hernie inguinale",                             "Saillie de tissu abdominal dans l'aine",              []),
    ("K57",  "Diverticulose intestinale",                    "Formation de petites poches dans le côlon",           ["MÉTRONIDAZOLE", "CIPROFLOXACINE", "AMOXICILLINE"]),
    ("K58",  "Syndrome de l'intestin irritable",             "Trouble fonctionnel intestinal chronique",            ["LOPÉRAMIDE", "MÉBÉVÉRINE", "TRIMÉBUTINE"]),
    ("K70",  "Maladie alcoolique du foie",                   "Atteinte hépatique liée à l'alcool",                  ["THIAMINE", "ACIDE FOLIQUE"]),
    ("K80",  "Lithiase biliaire",                            "Calculs dans la vésicule biliaire",                   ["ACIDE URSODÉSOXYCHOLIQUE"]),
    ("L20",  "Dermatite atopique",                           "Eczéma chronique allergique",                         ["HYDROCORTISONE", "TACROLIMUS", "CÉTIRIZINE", "BÉCLOMÉTASONE"]),
    ("L40",  "Psoriasis",                                    "Maladie inflammatoire chronique de la peau",          ["MÉTHOTREXATE", "CICLOSPORINE", "ADALIMUMAB", "CALCIPOTRIOL"]),
    ("L50",  "Urticaire",                                    "Réaction allergique cutanée avec plaques",            ["CÉTIRIZINE", "LORATADINE", "DESLORATADINE"]),
    ("M05",  "Polyarthrite rhumatoïde séropositive",         "Maladie auto-immune des articulations",               ["MÉTHOTREXATE", "ADALIMUMAB", "LÉFLUNOMIDE", "HYDROXYCHLOROQUINE"]),
    ("M10",  "Goutte",                                       "Dépôt de cristaux d'acide urique dans les articulations",["COLCHICINE", "ALLOPURINOL", "IBUPROFÈNE", "FÉBUXOSTAT"]),
    ("M15",  "Arthrose",                                     "Dégénérescence du cartilage articulaire",             ["PARACÉTAMOL", "IBUPROFÈNE", "DICLOFÉNAC", "GLUCOSAMINE"]),
    ("M40",  "Cyphose et lordose",                           "Déformation de la colonne vertébrale",                ["PARACÉTAMOL", "IBUPROFÈNE"]),
    ("M48",  "Autres spondylopathies",                       "Pathologies de la colonne vertébrale",                ["PARACÉTAMOL", "IBUPROFÈNE", "DICLOFÉNAC"]),
    ("M54",  "Dorsalgie / Lombalgie",                        "Douleurs du dos",                                     ["PARACÉTAMOL", "IBUPROFÈNE", "DICLOFÉNAC", "TRAMADOL"]),
    ("M79",  "Fibromyalgie",                                 "Douleurs musculaires chroniques diffuses",            ["DULOXÉTINE", "PRÉGABALINE", "AMITRIPTYLINE"]),
    ("N10",  "Néphrite tubulo-interstitielle aiguë",         "Infection rénale aiguë",                              ["CIPROFLOXACINE", "CEFTRIAXONE", "COTRIMOXAZOLE"]),
    ("N18",  "Insuffisance rénale chronique",                "Dégradation progressive de la fonction rénale",       ["RAMIPRIL", "FUROSÉMIDE", "ÉRYTHROPOÏÉTINE"]),
    ("N20",  "Calcul du rein et de l'uretère",              "Lithiase urinaire (colique néphrétique)",              ["IBUPROFÈNE", "PARACÉTAMOL", "TAMSULOSINE"]),
    ("N30",  "Cystite",                                      "Infection bactérienne de la vessie",                   ["FOSFOMYCINE", "NITROFURANTOÏNE", "COTRIMOXAZOLE"]),
    ("N39",  "Infection urinaire",                           "Infection des voies urinaires",                       ["FOSFOMYCINE", "CIPROFLOXACINE", "COTRIMOXAZOLE", "AMOXICILLINE"]),
    ("N40",  "Hyperplasie de la prostate",                   "Adénome prostatique bénin",                           ["TAMSULOSINE", "FINASTÉRIDE", "DUTASTÉRIDE"]),
    ("O00",  "Grossesse extra-utérine",                      "Implantation de l'œuf en dehors de l'utérus",         ["MÉTHOTREXATE"]),
    ("O14",  "Pré-éclampsie",                                "Hypertension gravidique avec protéinurie",            ["LABÉTALOL", "NIFÉDIPINE", "SULFATE DE MAGNÉSIUM"]),
    ("R05",  "Toux",                                         "Symptôme respiratoire",                               ["DEXTROMÉTHORPHANE", "CODÉINE", "BUTAMIRATE"]),
    ("R50",  "Fièvre",                                       "Élévation de la température corporelle",              ["PARACÉTAMOL", "IBUPROFÈNE"]),
    ("R51",  "Céphalée",                                     "Mal de tête",                                         ["PARACÉTAMOL", "IBUPROFÈNE", "ASPIRINE", "SUMATRIPTAN"]),
    ("S00",  "Traumatismes superficiels de la tête",         "Plaies et contusions crâniennes",                     ["PARACÉTAMOL", "IBUPROFÈNE"]),
    ("S52",  "Fracture de l'avant-bras",                     "Fracture du radius ou du cubitus",                    ["PARACÉTAMOL", "TRAMADOL", "IBUPROFÈNE"]),
    ("T14",  "Traumatisme sans précision",                   "Blessure non spécifiée",                              ["PARACÉTAMOL", "IBUPROFÈNE"]),
    ("T36",  "Intoxication aux antibiotiques",               "Surdosage ou réaction adverse aux antibiotiques",     ["CHARBON ACTIVÉ"]),
    ("Z23",  "Vaccination",                                  "Immunisation préventive",                             []),
    ("Z30",  "Contraception",                                "Méthodes contraceptives",                             ["LÉVONORGESTREL", "ÉTHINYLESTRADIOL", "DÉSOGESTREL"]),
]


def connect_odoo():
    print("🔌 Connexion à Odoo...")
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise Exception("Connexion échouée. Vérifiez vos identifiants.")
    print(f"  → Connecté (uid={uid})\n")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models


def get_medication_ids(uid, models, substance_names):
    """Récupère les IDs des médicaments par nom de substance active."""
    if not substance_names:
        return []
    med_ids = []
    for substance in substance_names:
        ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'medical.medication', 'search',
            [[['active_ingredient', 'ilike', substance]]]
        )
        med_ids.extend(ids)
    return list(set(med_ids))


def import_diseases(uid, models):
    print("Import des maladies CIM-10...\n")

    # Maladies déjà existantes
    existing = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'medical.disease', 'search_read',
        [[]], {'fields': ['code']}
    )
    existing_codes = {r['code'] for r in existing if r['code']}

    imported = 0
    updated = 0
    errors = 0

    for code, name, description, substances in DISEASES:
        try:
            # Récupérer les IDs médicaments associés
            med_ids = get_medication_ids(uid, models, substances)
            vals = {
                'code': code,
                'name': name,
                'description': description,
                'medication_ids': [(6, 0, med_ids)],
            }

            if code in existing_codes:
                # Mettre à jour si déjà existant
                disease_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'medical.disease', 'search',
                    [[['code', '=', code]]]
                )[0]
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'medical.disease', 'write',
                    [[disease_id], vals]
                )
                updated += 1
                print(f"  ↻ [{code}] {name} mis à jour ({len(med_ids)} médicaments)")
            else:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'medical.disease', 'create',
                    [vals]
                )
                imported += 1
                print(f"  ✔ [{code}] {name} importé ({len(med_ids)} médicaments)")

        except Exception as e:
            errors += 1
            print(f"   Erreur [{code}] {name}: {e}")

    print(f"\nTerminé: {imported} importées, {updated} mises à jour, {errors} erreurs.")


def main():
    print("=" * 60)
    print("  Import maladies CIM-10 + liaisons médicaments → Odoo")
    print("=" * 60 + "\n")
    uid, models = connect_odoo()
    import_diseases(uid, models)


if __name__ == "__main__":
    main()