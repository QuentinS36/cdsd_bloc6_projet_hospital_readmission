# Projet Hospital Readmission : pilotage et prévision de l'effectif hospitalier

Certification CDSD RNCP35288 - Bloc 6 : Direction de projets de gestion de données

## Contexte

La direction d'un établissement hospitalier veut anticiper chaque jour le
nombre de patients hospitalisés (effectif) sur les 30 jours passés et les
1 à 30 jours à venir, afin d'ajuster en amont lits et personnel. L'effectif
dépend des admissions programmées, de la durée des séjours et des
**réadmissions à 30 jours**, que l'on ne connaît pas à l'avance : il faut les
prédire.

## Objectifs

1. Traduire ce besoin métier en deux problèmes d'apprentissage supervisé :
   prédire la **réadmission à 30 jours** (classification) et la **durée de
   séjour** (régression).
2. Exposer les modèles dans une **API** (FastAPI) et construire un
   **tableau de bord opérationnel** (Streamlit) : effectif journalier, flux,
   indicateurs de saturation / sous-occupation, alertes, besoin en lits.
3. Piloter le projet et **déployer** les deux services sur Render.

## Données

`data/hospital_readmission_dataset.csv` : 8 000 séjours, 17 colonnes, du
01/01/2021 au 31/12/2023 (jeu synthétique, aucune donnée de patient réel).

| Colonne | Description |
|---|---|
| `patient_id` | Identifiant du séjour (unique), jamais affiché en clair |
| `admission_date`, `length_of_stay` | Date d'admission, durée de séjour (jours) ; `discharge_date` en est déduite |
| `label` | **Cible de la classification** : réadmission à 30 jours (1) ou non (0) ; 77,3 % de 1 |
| `age`, `gender`, `region`, `season`, `insurance_type` | Profil du patient |
| `primary_diagnosis`, `treatment_type`, `comorbidities_count`, `medications_count`, `followup_visits_last_year`, `prev_readmissions`, `discharge_disposition` | Variables cliniques |
| `readmission_risk_score` | **Volontairement exclue** des modèles (corrélée à la cible, risque de fuite) |

Aucune valeur manquante. Les modèles sont suivis (runs, métriques) et
enregistrés dans MLflow hébergé sur DagsHub.

## Etapes du projet

- **Cadrage** (`docs/`) : note de cadrage, cahier des charges, retroplanning.
- **Modélisation** (`notebook/`) : `readmission_model.ipynb` (Random Forest) et
  `length_of_stay.ipynb` (XGBoost optimisé), comparés à des baselines.
- **API** (`api/`, `src/services/`) : modèles chargés une fois au démarrage
  depuis le registre DagsHub (repli sur `models/`), endpoints
  `/_readmission_predict` et `/_length_of_stay_predict`, sonde `/healthz`,
  clé d'API optionnelle, validation stricte des entrées.
- **Prévision** (`src/pipeline.py`) : historique + planning → réadmissions
  prédites (sortie + 30 j) → durées de séjour prédites → effectif journalier
  `initial + admissions + réadmissions − sorties`.
- **Dashboard** (`dashboard/`, `src/dashboard/`) : pilotage (KPIs, alertes,
  courbes, besoin en lits), exploration des données, prédiction individuelle.
  Calculs mis en cache, mode dégradé sans planning.


## Résultats

Classification de la réadmission (test, 1 600 séjours) :

| Modèle | Accuracy | Précision | Recall | F1 | PR-AUC |
|---|---|---|---|---|---|
| Dummy (toujours « réadmis ») | 0,773 | 0,773 | 1,000 | 0,872 | - |
| Random Forest (seuil 0,50) | 0,798 | 0,818 | 0,951 | 0,879 | 0,940 |

Durée de séjour (test) :

| Modèle | MAE (jours) | RMSE (jours) | R² |
|---|---|---|---|
| Dummy (moyenne) | 1,635 | 2,008 | −0,003 |
| Moyenne par diagnostic | 0,947 | 1,204 | 0,640 |
| Régression linéaire | 0,847 | 1,083 | 0,708 |
| Random Forest | 0,860 | 1,104 | 0,697 |
| **XGBoost optimisé** | **0,787** | **1,051** | **0,725** |

## Interprétations et résultats

- **Durée de séjour** : l'XGBoost réduit la MAE de 17 % par rapport à la
  simple moyenne par diagnostic (0,79 j contre 0,95 j) : le gain est modeste
  mais net.
- **Réadmission** : la classe positive est très majoritaire (77 %), donc le
  F1 du Dummy (0,872) est déjà élevé. Le Random Forest ne le dépasse que de
  0,007 en F1 ; son apport se lit surtout dans la PR-AUC (0,94) et la
  précision (0,82 contre 0,77) pour un rappel de 0,95. C'est un modèle de
  *tri du risque* plus qu'un prédicteur précis.
- **Effectif** : la prévision combine ces deux modèles ; son erreur dépend
  donc des deux et n'a pas été mesurée sur un jeu indépendant (voir Limites).
- Le dashboard est une **aide à la décision** : il ne se substitue pas au
  jugement clinique.

**Point d'attention.** Le modèle de réadmission est réglé pour un rappel de
95 % (ne manquer aucun patient à risque), ce qui est adapté au suivi
individuel mais **surestime les volumes** quand on additionne les prédictions
pour prévoir un effectif : il prédit « réadmis » pour ≈ 90 % des sorties
(déduit de sa précision et de son rappel), contre 77 % observés. Pour la prévision agrégée, une approche
par probabilités (somme des `predict_proba`) serait plus juste.


## Limites

- Jeu synthétique, 3 ans, une seule structure : pas de saisonnalité réelle ni
  de contexte multi-établissements.
- Les modèles sont entraînés avec un découpage aléatoire : la prévision de la
  démo (date J = 01/07/2023) porte sur une période que les modèles ont
  partiellement vue. Un découpage temporel et un backtest effectif prévu /
  constaté seraient plus réalistes.
- Une ligne du jeu = un séjour et une issue : les réadmissions sont
  approximées par une copie du séjour d'origine (même durée).
- Offre gratuite Render : mise en veille après 15 min, premier appel ~1 min.

## Structure du repo

```
cdsd_bloc6_projet_hospital_readmission/
├── api/                  
├── dashboard/            
├── src/
│   ├── config.py         
│   ├── pipeline.py       
│   ├── data/             
│   ├── forecasting/      
│   ├── business/         
│   ├── services/         
│   └── dashboard/                    
├── notebook/             
├── docs/                 
├── data/hospital_readmission_dataset.csv
├── models/               
├── scripts/export_models.py
├── render.yaml  docker-compose.yml  .env.example
└── requirements.txt  
```

## Installation et exécution

```powershell
conda create -n cdsd_b6_hospital python=3.11 pip -y
conda activate cdsd_b6_hospital
python -m pip install -r requirements-dev.txt
copy .env.example .env      # renseigner DAGSHUB_OWNER, DAGSHUB_REPO, DAGSHUB_USER_TOKEN


Avec Docker : `docker compose up --build` (API sur 8000, dashboard sur 8501).

Les notebooks utilisent des chemins relatifs et une graine fixe
(`RANDOM_STATE = 42`). Les versions de `requirements.txt` sont celles de
l'entraînement : un modèle sauvegardé doit être rechargé avec les mêmes
versions de scikit-learn, xgboost et numpy (déjà épinglées dans `api/`).

## Déploiement sur Render

1. Pousser le repo sur GitHub (le fichier `.env` n'est jamais versionné).
2. Render → **New → Blueprint** → choisir le repo : `render.yaml` crée
   `hospital-readmission-api` et `hospital-readmission-dashboard`.
3. Renseigner sur l'API `DAGSHUB_OWNER`, `DAGSHUB_REPO`, `DAGSHUB_USER_TOKEN`
   (`API_KEY` est générée automatiquement et transmise au dashboard).
4. Une fois l'API publiée, renseigner sur le dashboard
   `API_URL=https://<nom-de-l-api>.onrender.com`, puis redéployer.
5. Vérifier `https://<nom-de-l-api>.onrender.com/healthz` (200 + source des
   modèles) avant d'ouvrir le dashboard.

Les services gratuits ne reçoivent pas de trafic réseau privé : le dashboard
appelle donc l'API par son URL publique, protégée par `X-API-Key`. Pour une
démonstration, ouvrir `/healthz` quelques minutes avant pour réveiller l'API.
Repli si DagsHub est indisponible : `python scripts/export_models.py`, puis
versionner `models/` (l'API charge alors les copies locales).

## RGPD

Données synthétiques ici, mais conçues comme des données de santé :
minimisation (tableaux sans variable clinique), pseudonymisation HMAC des
identifiants, aucune donnée patient journalisée par l'API, secrets hors du
code, clé d'API, entrées validées.
