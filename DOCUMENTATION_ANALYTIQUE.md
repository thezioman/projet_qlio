# Documentation analytique — T'EleFan MES 4.0

## Pourquoi ces indicateurs ? Justification et pertinence

Ce document explique le choix de chaque indicateur affiche dans le dashboard T'EleFan, leur pertinence dans le contexte d'une ligne de production automatisee FESTO, et ce qu'ils permettent de piloter.

---

## 1. TRS — Taux de Rendement Synthetique

**Definition :** TRS = Disponibilite x Qualite (en %). Dans notre cas, le TRS est calcule comme le produit du taux de disponibilite et du taux de qualite, par ressource et par jour.

**Pourquoi cet indicateur ?**
Le TRS est l'indicateur de reference en production industrielle (norme NF E60-182). Il synthetise en un seul chiffre les trois dimensions de la performance d'un equipement : est-il disponible ? produit-il au bon rythme ? les pieces sont-elles conformes ?

**Pertinence pour la ligne FESTO :**
La ligne FESTO comporte plusieurs postes (ressources) en serie. Un TRS bas sur un poste identifie immediatement le goulot d'etranglement de la ligne. Le seuil cible de 85% correspond au standard "World Class Manufacturing".

**Decisions qu'il permet :**
- Identifier les ressources sous-performantes
- Prioriser les actions d'amelioration continue
- Suivre l'evolution globale de la ligne dans le temps

---

## 2. Disponibilite

**Definition :** Pourcentage du temps ou la machine est en marche par rapport au temps total de releves.

**Pourquoi cet indicateur ?**
La disponibilite mesure les pertes liees aux arrets (pannes, reglages, attentes). C'est la premiere composante du TRS et souvent la plus impactante sur une ligne automatisee.

**Pertinence pour la ligne FESTO :**
Les donnees `Surveillance_machine` enregistrent l'etat de chaque ressource (en marche / en arret / reset) avec un horodatage precis. Cela permet de calculer la disponibilite reelle de chaque poste.

**Decisions qu'il permet :**
- Detecter les postes avec des arrets frequents
- Justifier un investissement en maintenance preventive
- Evaluer l'impact d'une panne sur le flux global

---

## 3. Cadence / Taux de performance

**Definition :** Nombre de pieces produites par heure de production effective.

**Pourquoi cet indicateur ?**
La cadence mesure les pertes de vitesse : micro-arrets, ralentissements, ecarts par rapport au temps de cycle theorique. Une cadence en baisse peut signaler une usure d'outil ou un probleme de reglage.

**Pertinence pour la ligne FESTO :**
Chaque operation sur chaque piece est tracee avec un horodatage debut/fin. On peut donc calculer la cadence reelle et la comparer entre ressources et dans le temps.

**Decisions qu'il permet :**
- Comparer la vitesse reelle a la vitesse theorique
- Detecter les derives de performance avant qu'elles ne causent des arrets
- Equilibrer la charge entre postes

---

## 4. Taux de qualite et rebuts

**Definition :**
- Taux de qualite = pieces conformes / pieces totales (%)
- Rebuts = pieces non conformes, classees par type d'erreur

**Pourquoi ces indicateurs ?**
La qualite est la troisieme composante du TRS. Les rebuts representent un cout direct (matiere perdue, retravail) et un risque pour le client final. Le classement par type d'erreur (Pareto) permet d'identifier les causes les plus frequentes.

**Pertinence pour la ligne FESTO :**
Chaque etape de production enregistre si la piece est conforme (`ETAPE_EST_CONFORME`) et le code d'erreur associe. Le Pareto des erreurs oriente les actions correctives.

**Decisions qu'il permet :**
- Prioriser les actions qualite sur les erreurs les plus frequentes (loi de Pareto : 20% des causes produisent 80% des defauts)
- Suivre l'evolution du taux de qualite apres une action corrective
- Identifier les postes generant le plus de rebuts

---

## 5. MTBF et MTTR — Fiabilite et maintenabilite

**Definition :**
- **MTBF** (Mean Time Between Failures) : temps moyen entre deux pannes, en minutes
- **MTTR** (Mean Time To Repair) : temps moyen de reparation apres une panne, en minutes

**Pourquoi ces indicateurs ?**
Le MTBF mesure la fiabilite de l'equipement (plus il est eleve, plus la machine est fiable). Le MTTR mesure la maintenabilite (plus il est bas, plus les reparations sont rapides). Ensemble, ils permettent de planifier la maintenance.

**Pertinence pour la ligne FESTO :**
Les evenements de surveillance (arret -> reset -> marche) permettent de reconstituer les sequences de panne et de reparation pour chaque ressource. On calcule le MTBF comme le temps moyen entre un reset et l'arret suivant, et le MTTR comme le temps moyen entre un arret et le reset suivant.

**Decisions qu'il permet :**
- Planifier la maintenance preventive (intervenir avant le MTBF)
- Evaluer l'efficacite de l'equipe maintenance (reduire le MTTR)
- Comparer la fiabilite des differentes ressources
- Justifier le remplacement d'un equipement vieillissant

---

## 6. Lead Time

**Definition :** Duree totale entre le debut et la fin d'une commande, en minutes.

**Pourquoi cet indicateur ?**
Le lead time mesure le temps de traversee du systeme de production du point de vue du client. C'est un indicateur cle du Lean Manufacturing : un lead time court signifie une production agile et reactive.

**Pertinence pour la ligne FESTO :**
Chaque commande a une date de debut (`Start`) et de fin (`End`). Le lead time inclut le temps de production, les temps d'attente inter-postes et les temps de stockage intermediaire.

**Decisions qu'il permet :**
- Identifier les commandes anormalement longues
- Detecter les goulots d'etranglement dans le flux
- Estimer les delais de livraison pour les nouvelles commandes

---

## 7. OTD — On-Time Delivery

**Definition :** Pourcentage de commandes terminees avant ou a la date planifiee.

**Pourquoi cet indicateur ?**
L'OTD est l'indicateur de service par excellence. Il mesure la capacite de la production a respecter les engagements de delai. Un OTD faible entraine des penalites, de l'insatisfaction client et une perte de confiance.

**Pertinence pour la ligne FESTO :**
Chaque commande a une date de fin planifiee (`PlannedEnd`) et une date de fin reelle (`End`). On compare les deux pour determiner si la commande est "a l'heure".

**Note sur les donnees FESTO :** Dans les jeux de donnees fournis, l'OTD est souvent a 0% car toutes les commandes sont terminees apres la date planifiee. Cela reflète une caracteristique des donnees de test, mais l'indicateur reste pertinent pour un deploiement en production reelle.

**Decisions qu'il permet :**
- Alerter en cas de derive des delais
- Ajuster la planification en fonction des capacites reelles
- Negocier des delais realistes avec les clients

---

## 8. WIP — Work In Progress (en-cours)

**Definition :** Taux d'occupation des buffers (zones de stockage intermediaire) entre les postes, exprime en pourcentage.

**Pourquoi cet indicateur ?**
Le WIP mesure la quantite de pieces en attente dans le systeme. Un WIP eleve signale un desequilibre entre les postes (un poste lent accumule des pieces en amont). Selon la loi de Little, le WIP est directement lie au lead time.

**Pertinence pour la ligne FESTO :**
Chaque poste possede des buffers avec une capacite definie. Les donnees enregistrent le nombre de positions occupees. La heatmap binaire (libre/occupe) permet de visualiser l'occupation de chaque ligne de production au fil du temps.

**Decisions qu'il permet :**
- Detecter les postes goulots (buffers amont satures)
- Optimiser les tailles de lots
- Reduire le lead time en reduisant le WIP (approche Lean)

---

## 9. Taux de charge

**Definition :** Pourcentage du temps ou la ressource est effectivement sollicitee (en marche) par rapport au temps total.

**Pourquoi cet indicateur ?**
Le taux de charge mesure l'utilisation effective des equipements. Un taux de charge faible peut indiquer un surdimensionnement ou un probleme d'approvisionnement. Un taux trop eleve empeche toute maintenance preventive.

**Pertinence pour la ligne FESTO :**
Calcule a partir des memes donnees de surveillance que la disponibilite, mais interprete differemment : on cherche ici a savoir si la ressource est suffisamment utilisee, pas seulement si elle est disponible.

**Decisions qu'il permet :**
- Equilibrer la charge entre ressources
- Identifier les ressources sous-utilisees (candidates a une reaffectation)
- Planifier les plages de maintenance preventive sur les postes les moins charges

---

## 10. Cycle moyen

**Definition :** Duree moyenne d'une operation sur une ressource, en secondes.

**Pourquoi cet indicateur ?**
Le cycle moyen est la brique elementaire du dimensionnement de ligne. Il permet de calculer la cadence theorique et d'identifier les postes les plus lents (goulots).

**Pertinence pour la ligne FESTO :**
Chaque etape de production est tracee avec un horodatage debut/fin. Le cycle moyen est calcule par ressource et par type d'operation, ce qui permet de comparer les postes entre eux.

**Decisions qu'il permet :**
- Identifier le poste goulot (cycle le plus long)
- Detecter les derives de temps de cycle (usure, mauvais reglage)
- Dimensionner la cadence cible de la ligne

---

## 11. Stock

**Definition :** Quantite totale de pieces en stock, par reference.

**Pourquoi cet indicateur ?**
Le stock immobilise du capital et de l'espace. Un Pareto du stock permet d'identifier les references les plus presentes et de verifier la coherence avec les besoins de production.

**Pertinence pour la ligne FESTO :**
Les donnees `tblbufferpos` fournissent la quantite de chaque piece dans chaque buffer. Le graphique Pareto permet de visualiser la repartition et d'identifier les sur-stocks.

**Decisions qu'il permet :**
- Reduire les stocks excedentaires
- Verifier que les matieres premieres sont disponibles pour la production
- Anticiper les ruptures de stock

---

## Synthese : couverture des axes de pilotage

| Axe de pilotage | Indicateurs | Page |
|---|---|---|
| **Efficacite globale** | TRS, Disponibilite, Cadence, Taux de charge | Performance |
| **Qualite produit** | Taux de qualite, Rebuts (Pareto), MTBF/MTTR | Qualite |
| **Flux et delais** | Lead Time, OTD, WIP (heatmap), Stock (Pareto) | Logistique |
| **Fiabilite equipement** | Erreurs, MTBF, MTTR, repartition erreurs | Maintenance |
| **Vue consolidee** | Synthese de tous les KPIs, donnees brutes, export | Donnees |

Cette repartition couvre les 4 piliers du pilotage industriel :
1. **Performance** — est-ce que je produis efficacement ?
2. **Qualite** — est-ce que je produis bien ?
3. **Logistique** — est-ce que je livre a temps ?
4. **Maintenance** — est-ce que mes equipements sont fiables ?

Chaque indicateur a ete choisi pour etre calculable a partir des donnees disponibles dans l'export FESTO MES, et pour apporter une information actionnable pour le responsable de production.

---

IUT Lumiere Lyon 2 — BUT Science des Donnees — SAE MES 4.0
