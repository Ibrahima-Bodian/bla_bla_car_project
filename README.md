# BlaBlaCar — Analyse de Données & Dashboard Power BI

> Analyse de trajets, demandes, membres, véhicules et notes pour comprendre l’activité, la conversion et les leviers d’amélioration.  
> **Stack** : PostgreSQL · Power BI (DAX/Power Query) · GitHub

---

## Objectifs
- Construire un **modèle en étoile** robuste (faits/dimensions) à partir de CSV/PostgreSQL.
- Mesurer l’activité (trajets, demandes), la **conversion** (taux d’acceptation), le **pricing** (contribution), la **qualité** (notes).
- Livrer un **dashboard Power BI** clair (KPI & visuels variés) pour l’exploration: temps, géographie, routes, segments membres/véhicules.

---

## Stack & contenus
- **Power BI Desktop** : modélisation (relations, dims de rôle), DAX, visuels.
- **Power Query** : typage, jointures, nettoyage.
- **PostgreSQL** : stockage, requêtes SQL (aggrégations métier).
- **GitHub** : versioning, documentation, suivi.


Projet_blablacar/
├─ donnees_csv/ # CSV sources (nettoyés)
├─ sql/
│ ├─ blabla_creation tables.sql # requetes de création des tables (cars, cities, members, rides...)
│ └─ blabla_données_exportées.sql # bdd exporté depuis postgresql
├─ rapport_&_powerbi/
│ ├─ blablacar_pwbi.pbix # Dashboard Power BI
│ └─ blablacar_pwbi.pdf/ # rapport-dashbord (aperçu)
├─ README.md
└─ LICENSE




---

## Modèle de données (star schema)

**Faits**
- `FactRides` : trajets (ride_id, dates/horaires, villes départ/arrivée, sièges, contribution, membre-voiture)
- `FactRequests` : demandes (request_id, ride_id, requester, statut)
- `FactRatings` : avis (rating_id, giver, receiver, grade)

**Dimensions**
- `DimMembers` (members) : identité, genre, dates (naissance/inscription), préférences
- `DimCars` (cars) : marque, année, couleur, co2_code
- `DimCities_Start` & `DimCities_Dest` (copies de `cities`, rôles départ/arrivée)
- `DimLuggage` (luggage_types)
- `DimRequestStatus` (Accepted/Pending/Refused)
- `DimDate` (CALENDAR min/max trajets, Année/Mois/MoisNo/Jour, etc.)

**Relations clés** (sens Dim ➜ Fact)
- `DimDate[Date]` → `FactRides[departure_date]`
- `DimDate[Date]` → `FactRequests[request_date]` *(colonne dérivée de rides)*
- `DimCities_Start[city_id]` → `FactRides[starting_city_id]`
- `DimCities_Dest[city_id]` → `FactRides[destination_city_id]`
- `DimRequestStatus[request_status_id]` → `FactRequests[request_status_id]`
- `FactRides[ride_id]` → `FactRequests[ride_id]`

---

## KPI principaux (exemples)
- **Activité** : Nombre de trajets, Nombre de demandes, Demandes par trajet (moy.)
- **Conversion** : Taux d’acceptation (= Accepted / Total), Passagers acceptés
- **Pricing** : Contribution moyenne (€), Revenu moyen / trajet (€) *(approx. min(sièges, accepted) × prix)*
- **Géo & routes** : Ville départ/arrivée **TOP1** (nom + volume), Routes distinctes
- **Population** : % femmes, % hommes, Âge moyen, Ancienneté moyenne, Nombre de voitures
- **Qualité** : Note moyenne

> **Remarque** : pour l’analyse temporelle des demandes, `FactRequests` reçoit `request_date = RELATED(FactRides[departure_date])` pour connecter `DimDate`.

---

## Pages du dashboard (structure)
1. **Accueil & KPI** — vue globale, combo *Trajets & Taux (mensuel)*, Top routes, funnel statuts.  
2. **Temps (Jour/Mois/Année)** — séries quotidiennes/mensuelles, waterfall variation, heatmap Mois×Jour, KPI “jour/mois le plus actif”.  
3. **Géo Départ** — carte départ, Top 10 villes départ, matrice Origine→Destination, KPI ville départ TOP1.  
4. **Géo Destination** — miroir de la page départ, KPI ville arrivée TOP1.  
5. **Routes** — Top routes, scatter *Contribution vs Taux*, revenu moyen par route.  
6. **Membres & Véhicules** — genre/âge, conducteurs/inscription, trajets & contribution par marque, histogramme contribution.  
7. **Trajet & Impact** — arbre de **Décomposition** du *Taux d’acceptation*, KPI d’efficacité.

---


## SQL — requêtes métier (extraits)
-- Taux d’acceptation mensuel
#
SELECT DATE_TRUNC('month', r.departure_date) AS mois,
       SUM(CASE WHEN rs.status='Accepted' THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*),0) AS taux_acceptation
FROM requests rq
JOIN rides r ON r.ride_id = rq.ride_id
JOIN request_status rs ON rs.request_status_id = rq.request_status_id
GROUP BY 1 ORDER BY 1;

-- Top routes
#
SELECT cs.city_name || ' → ' || cd.city_name AS route, COUNT(*) AS nb_trajets
FROM rides r
JOIN cities cs ON cs.city_id = r.starting_city_id
JOIN cities cd ON cd.city_id = r.destination_city_id
GROUP BY 1 ORDER BY nb_trajets DESC LIMIT 15;

-- Revenu moyen / trajet (approx)
#
WITH acc AS (
  SELECT r.ride_id, r.number_seats, r.contribution_per_passenger AS price,
         COUNT(*) FILTER (WHERE rs.status='Accepted') AS accepted
  FROM rides r
  LEFT JOIN requests rq ON rq.ride_id = r.ride_id
  LEFT JOIN request_status rs ON rs.request_status_id = rq.request_status_id
  GROUP BY r.ride_id
)
SELECT AVG(LEAST(number_seats, accepted) * price) AS revenu_moyen_trajet
FROM acc;
