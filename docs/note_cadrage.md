# Projet Hospital Readmission & Bed Management - Note de cadrage

## 1. Contexte et enjeux métier

Le service hospitalier concerné doit anticiper, jour après jour, le nombre de patients présents afin d'ajuster ses ressources en lits et en personnel soignant. Aujourd'hui, ce pilotage repose principalement sur l'expérience des équipes et une lecture rétrospective de l'activité, sans outil de projection formalisé sur les prochains jours.
Deux phénomènes rendent cette anticipation difficile : les réadmissions de patients déjà suivis, dont le risque n'est pas visible a priori, et la variabilité de la durée de séjour, qui conditionne la date de sortie réelle et donc la libération des lits. Sans visibilité sur ces deux facteurs, le service s'expose à des situations de sur-occupation (saturation, dégradation de la qualité de prise en charge, tension sur le personnel) ou de sous-occupation (lits disponibles non anticipés, allocation sous-optimale des ressources).
Le projet vise à outiller le service d'un système de prévision d'effectif à horizon J → J+N, combinant l'historique des séjours, le planning des admissions programmées, et des modèles prédictifs de réadmission et de durée de séjour, restitué sous la forme d'un tableau de bord opérationnel.

## 2. Objectifs du projet
Les objectifs poursuivis, formulés selon une logique SMART, sont les suivants :
●	Fournir une projection quotidienne de l'effectif hospitalier sur un horizon paramétrable (par défaut J → J+7), actualisée à chaque nouvelle date de référence.
●	Détecter en amont les périodes à risque de saturation ou de sous-occupation, au regard d'une capacité nominale et d'une plage de tolérance définies par le service.
●	Réduire le temps d'analyse manuelle actuellement consacré à l'estimation empirique de la charge à venir.
●	Fournir aux équipes un support de décision lisible (KPIs, alertes visuelles, détail journalier) ne nécessitant aucune compétence data pour être exploité.
●	Garantir un traitement des données de santé conforme au RGPD tout au long du cycle de vie du projet.

## 3. Traduction du besoin métier en problématique data
Le besoin métier — anticiper l'effectif — se décompose en trois sous-problèmes data traités séquentiellement :

### 3.1 Prévision des réadmissions (classification binaire)
Pour chaque patient sorti à une date D-30, prédire s'il sera réadmis. Modèle de classification supervisée, restitué comme patient à risque avec une date de réadmission estimée (discharge_date + 30 jours).

### 3.2 Prévision de la durée de séjour (régression)
Pour tout patient entrant — planning programmé ou réadmission prédite — estimer sa durée de séjour afin d'en déduire une date de sortie prévisionnelle. Modèle de régression supervisée.

### 3.3 Simulation du stock journalier (règles métier)
Agrégation, jour par jour, des entrées (admissions programmées + réadmissions prédites), des sorties (dates de sortie réelles ou prédites) et du stock en cours, pour produire l'effectif total prévisionnel comparé à la capacité nominale du service.
Ce découpage permet de traiter séparément l'incertitude sur qui va revenir, l'incertitude sur combien de temps chacun va rester, et le calcul déterministe du solde d'occupation qui en découle — plutôt que de chercher à prédire directement l'effectif total par une série temporelle globale, moins interprétable et plus difficile à auditer pour les équipes métier.

## 4. Périmètre du projet

### 4.1 Inclus
- Chargement et consolidation de l'historique patients, du planning d'admissions et de l'historique de réadmission.
- Entraînement, versionning et chargement des modèles de réadmission et de durée de séjour via MLflow / DagsHub.
- Calcul de l'effectif journalier réel et prévisionnel, des KPIs de saturation, et des alertes visuelles associées.
- Application Streamlit multipage : tableau de bord opérationnel et dashboard exploratoire des données patients.

### 4.2 Exclus (hors périmètre à ce stade)
- Ré-entraînement automatique et continu des modèles (MLOps complet avec déclenchement automatique).
- Intégration temps réel avec le système d'information hospitalier (le projet fonctionne sur import de fichiers CSV).
- Extension à d'autres services.
- Module de comparaison prédiction/réel sur données réelles post-période, actuellement à l'état de prototype non activé.


## 5. Livrables attendus
- Note de cadrage (ce document).
- Cahier des charges détaillé (spécifications fonctionnelles et techniques, critères d'acceptation).
- Rétroplanning et budget prévisionnel.
- Dépôt de code restructuré (data / modèles / application / documentation).
- Note d'analyse d'impact sur la protection des données (AIPD) et mesures de conformité RGPD.
- Application Streamlit déployée : tableau de bord de pilotage et dashboard exploratoire.
- Support de présentation.

## 6. Contraintes

### 6.1 Contraintes réglementaires
- Données de santé à caractère personnel : application des principes de minimisation, de pseudonymisation et de limitation de la durée de conservation.
- Traçabilité des accès et des traitements réalisés sur les données patients.

### 6.2 Contraintes techniques
- Disponibilité de l'infrastructure MLflow / DagsHub pour le chargement des modèles en production.
- Cohérence temporelle stricte entre les fenêtres d'historique, de planning et de prévision (gestion des dates J, J-30, J+N).
- Isolation des secrets d'accès (identifiants DagsHub) hors du code source versionné.

### 6.3 Contraintes organisationnelles
- Deux semaines de préparation du projet final de formation.

## 7. Risques identifiés et mesures de mitigation
Risque	Criticité	Mesure de mitigation
Sur-confiance dans une prévision erronée (faux négatif de saturation)	Élevée	Afficher un intervalle de confiance et positionner l'outil en aide à la décision, non en substitut du jugement clinique
Non-conformité RGPD sur des données de santé	Élevée	AIPD formalisée avant mise en production, pseudonymisation systématique
Dérive du modèle dans le temps (data drift)	Moyenne	Suivi périodique des indicateurs de performance des modèles versionnés dans MLflow
Indisponibilité des identifiants / de l'infrastructure DagsHub	Moyenne	Gestion des secrets via variables d'environnement et procédure de repli documentée
Retard sur le calendrier de certification	Moyenne	Rétroplanning avec jalons intermédiaires et marges tampon

## 8. Gouvernance et prochaines étapes
Ce document de cadrage constitue la première étape du projet et sera complété par un cahier des charges détaillé (spécifications fonctionnelles, exigences techniques, critères d'acceptation) ainsi que par un rétroplanning, faisant l'objet de livrables séparés.
