# Projet Hospital Readmission & Bed Management - Note de cadrage

## 1. Objet du document
Ce cahier des charges détaille les exigences fonctionnelles et techniques du système de prévision de l'effectif hospitalier introduit dans la note de cadrage. Il sert de référence contractuelle entre le porteur du projet et le sponsor métier, et de support d'évaluation pour le jury de certification quant à la maîtrise de la conception d'une solution data répondant à un besoin métier formalisé.
Il précise : le périmètre fonctionnel module par module, les données utilisées, les exigences non fonctionnelles, l'architecture technique retenue, les critères d'acceptation et les modalités de recette.

## 2. Rappel du besoin métier
Le service hospitalier a besoin d'anticiper, sur un horizon glissant J → J+N, l'effectif de patients présents afin d'ajuster ses ressources en lits et en personnel. Cette anticipation doit intégrer trois composantes : l'effectif de patients déjà présents dont le séjour se prolonge, les admissions déjà programmées, et les réadmissions non planifiées de patients suivis antérieurement.
Le détail de la traduction du besoin en problématique data (classification des réadmissions, régression de la durée de séjour, agrégation de l'effectif) figure dans la note de cadrage et n'est pas répété ici.

## 3. Périmètre fonctionnel

### 3.1 Modules du système
Le système se décompose en huit modules fonctionnels, correspondant chacun à un ensemble de responsabilités clairement délimité :

- M1 — Ingestion	Chargement et normalisation des CSV historique, planning et réadmission (typage des dates, calcul de la date de sortie)
- M2 — Effectif historique	Calcul de l'effectif journalier réel sur la fenêtre J-30/J-60 → J-1 (entrées, sorties, réadmissions constatées)
- M3 — Prédiction réadmission	Application du modèle de classification aux patients sortis à D-30 pour chaque jour de l'horizon de prévision
- M4 — Prédiction durée de séjour	Application du modèle de régression aux patients du planning et aux réadmissions prédites
- M5 — Prévision de l'effectif	Agrégation de l'effectif prévisionnel J → J+N à partir des sorties de M3/M4 et de l'historique en cours
- M6 — Indicateurs (KPI)	Calcul des indicateurs de saturation, sous-occupation, moyenne/min/max sur la période sélectionnée
- M7 — Alertes	Déclenchement d'une alerte visuelle lorsque le nombre de jours en saturation dépasse le seuil défini
- M8 — Visualisation	Restitution graphique : effectif journalier (aire empilée), flux entrées/sorties, besoin en lits, tableau détaillé

### 3.2 Paramètres pilotables par l'utilisateur
- Date de référence J.
- Nombre de jours à analyser (horizon de prévision, de 1 à 30 jours).
- Vue réduite (J-7 → J+N) ou vue étendue (J-30 → J+N).
- Capacité nominale du service (nombre de lits).
- Plage de tolérance autour de la capacité nominale (seuils bas et haut d'alerte, en %).
- Sources de données (URL ou chemin des trois fichiers CSV d'entrée).

### 3.3 Exigences fonctionnelles et critères d'acceptation

- F01	Charger l'historique patient et calculer la date de sortie à partir de la durée de séjour	
- F02	Restreindre l'historique à une fenêtre glissante avant la date J	
- F03	Prédire la réadmission des patients sortis à D-30 pour chaque jour de l'horizon	
- F04	Prédire la durée de séjour du planning et des réadmissions prédites	
- F05	Calculer l'effectif prévisionnel J → J+N	
- F06	Afficher les KPIs (effectif moyen, jours de saturation, jours de sous-occupation, min/max)	
- F07	Déclencher une alerte visuelle si la saturation dépasse un seuil de jours	
- F08	Restituer un graphique d'effectif distinguant la partie historique et la partie prévue	
- F09	Restituer le flux journalier entrées/sorties	
- F10	Restituer le besoin en lits et en personnel par rapport à la capacité nominale	
- F11	Fonctionner en mode dégradé sans planning fourni (historique seul)	
- F12	Permettre la comparaison entre prévision et réalisé a posteriori


## 4. Spécifications des données

### 4.1 Sources d'entrée

- Historique patients : Séjours passés avec issue connue (sortie, réadmission éventuelle), utilisé pour l'entraînement des modèles et le calcul de l'effectif réel
- Planning d'admissions : Admissions programmées sur l'horizon J → J+N, sans durée de séjour ni date de sortie connues à l'avance
- Historique de réadmission : Complément à l'historique patients pour la fenêtre récente, utilisé pour fiabiliser l'effectif réel avant J

### 4.2 Qualité et validation des données
●	Contrôle de typage des dates à l'ingestion, avec échec explicite en cas de format non conforme.
●	Détection des valeurs manquantes sur les colonnes utilisées par les modèles avant inférence.
●	Vérification de la cohérence temporelle (discharge_date postérieure à admission_date).


## 5. Exigences de conformité RGPD
Le système traite des données de santé à caractère personnel au sens de l'article 9 du RGPD (diagnostics, traitements, comorbidités). Les exigences suivantes s'appliquent en complément de l'analyse d'impact (AIPD) à produire séparément :
●	Pseudonymisation de patient_id avant tout traitement hors environnement sécurisé de production.
●	Minimisation : seules les variables strictement nécessaires aux modèles (FEATURES_READ, FEATURES_LOS) sont transmises aux étapes d'inférence.
●	Limitation de la durée de conservation des fichiers sources chargés par l'application.
●	Traçabilité des accès aux données et aux modèles (journalisation).
●	Absence d'exposition de données patient identifiables dans les visualisations partagées à des tiers.

## 6. Architecture technique

### 6.1 Stack technique
- Langage : Python.
- Interface applicative : Streamlit (application multipage : tableau de bord opérationnel + dashboard exploratoire).
- Traitement de données : pandas.
- Visualisation : Plotly (graphiques interactifs).
- Machine Learning : scikit-learn, versionné et servi via MLflow, hébergé sur DagsHub.

### 6.2 Organisation cible du dépôt
- data/ — jeux de données bruts et traités.
- src/models/ — scripts d'entraînement et de suivi des expériences MLflow.
- src/app/ — application Streamlit (pages, composants).
- utils/ — fonctions métier réutilisables (ingestion, calcul de l'effectif, KPIs, prédiction).
- visualisations/ — modules de rendu graphique.
- config/ — configuration centralisée et gestion des secrets via variables d'environnement.
- docs/ — cadrage, cahier des charges.


## 7. Modalités de recette
- Recette fonctionnelle : vérification de chaque exigence F01 à F11 sur un jeu de données de test dédié, distinct des données d'entraînement des modèles.
- Recette non régressive : exécution de la suite de tests automatisés avant toute mise à jour du dépôt.
- Recette métier : présentation du tableau de bord au sponsor métier et validation de la lisibilité des indicateurs et alertes.
- Recette RGPD : vérification de l'absence de données identifiantes en clair dans les journaux et les exports.

## 8. Hors périmètre
- Ré-entraînement automatique et continu des modèles (MLOps complet).
- Intégration temps réel avec le système d'information hospitalier.
- Extension multi-services.
- Module de comparaison prédiction/réel (prototype non activé, cf. exigence F12).


