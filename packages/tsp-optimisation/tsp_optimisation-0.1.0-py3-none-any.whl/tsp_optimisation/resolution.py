import math
from src.tsp_optimisation.voyageur import Voyageur
from src.tsp_optimisation.ville import Ville


def distance(ville1: Ville, ville2: Ville) -> float:
    """
    Calcule la distance euclidienne entre deux villes.

    Args:
        ville1 (Ville): Première ville.
        ville2 (Ville): Deuxième ville.

    Returns:
        float: Distance entre les deux villes.
    """
    return math.sqrt((ville1.x - ville2.x) ** 2 + (ville1.y - ville2.y) ** 2)


def normaliser_heure(heure: float) -> float:
    """
    Normalise une heure pour qu'elle reste dans l'intervalle 0-24.

    Args:
        heure (float): Heure en heures décimales (ex: 10.5 = 10h30).

    Returns:
        float: Heure normalisée (modulo 24).
    """
    return heure % 24


class Resolution:
    """
    Classe permettant de résoudre le problème du voyageur de commerce (TSP)
    avec contraintes : fenêtres temporelles, capacité du véhicule, routes interdites et repos.

    Toutes les heures (fenêtres, départs, arrivées) doivent être exprimées
    en heures décimales (ex: 10h30 = 10.5).

    Attributes:
        villes (list[Ville]): Liste des villes à visiter.
        voyageur (Voyageur): Objet représentant le voyageur.
        connexions_ignores (list[tuple[int,int]]): Liste de couples de villes interdites.
        temps_pour_km (float): Temps nécessaire pour parcourir 1 km (heures/km).
    """

    def __init__(self, villes: list[Ville], voyageur: Voyageur, connexions_ignores: list[tuple[int, int]],
                 temps_pour_km: float):
        """
        Initialise une instance de Resolution.

        Args:
            villes (list[Ville]): Liste des villes à visiter.
            voyageur (Voyageur): Objet représentant le voyageur.
            connexions_ignores (list[tuple[int,int]]): Liste de connexions interdites entre villes (id1, id2).
            temps_pour_km (float): Temps nécessaire pour parcourir 1 km (heures/km).
        """
        self.villes = villes
        self.voyageur = voyageur
        self.connexions_ignores = connexions_ignores
        self.temps_pour_km = temps_pour_km #heure/km

    def chercher_ville_suivante(self, voyageur : Voyageur, capacite_restant : int, ville_actuelle : Ville, villes_non_visites : list[Ville], heure_passe :float,
                                distance_sans_repo : float):
        """
        Cherche la ville suivante que le voyageur peut visiter en respectant
        toutes les contraintes : fenêtre horaire, capacité et repos.

        Args:
            voyageur (Voyageur): Le voyageur.
            capacite_restant (float): Capacité restante du véhicule.
            ville_actuelle (Ville): Ville actuelle du voyageur.
            villes_non_visites (list[Ville]): Liste des villes non encore visitées.
            heure_passe (float): Heure actuelle (heures décimales).
            distance_sans_repo (float): Distance parcourue depuis le dernier repos.

        Returns:
            Ville | None: La prochaine ville valide à visiter ou None si aucune.
        """
        condidatures = [ville for ville in villes_non_visites if
                        (ville_actuelle.id, ville.id) not in self.connexions_ignores]
        candidatures_validees = []

        for ville in condidatures:
            distance_a_parcourir = distance(ville_actuelle, ville)
            # Calcul de l'heure d'arrivée en tenant compte du temps de trajet
            heure_arrivee = heure_passe + distance_a_parcourir * self.temps_pour_km
            heure_arrivee = normaliser_heure(heure_arrivee)
            # Respect de la fenêtre horaire
            heure_arrivee = max(heure_arrivee, ville.window_start)

            if heure_arrivee > ville.window_end:
                continue

            if capacite_restant < ville.demande:
                continue

            if distance_sans_repo + distance_a_parcourir >= voyageur.distance_pour_repo:
                nbre_repos = int((distance_sans_repo + distance_a_parcourir) // voyageur.distance_pour_repo)
                heure_arrivee += voyageur.temps_de_repo * nbre_repos
                heure_arrivee = normaliser_heure(heure_arrivee)
                if heure_arrivee > ville.window_end:
                    continue

            candidatures_validees.append(ville)

        if len(candidatures_validees) > 0:
            return min(candidatures_validees, key=lambda v: distance(ville_actuelle, v))
        return None

    def chercher_parcours(self, voyageur : Voyageur, ville_depart : Ville, heure_depart :float):
        """
        Cherche un parcours complet en respectant toutes les contraintes.

        Args:
            voyageur (Voyageur): Le voyageur.
            ville_depart (Ville): Ville de départ.
            heure_depart (float): Heure de départ (heures décimales).

        Returns:
            list[Ville] | None: Liste de villes représentant le parcours ou None si impossible.
        """
        villes_non_visites = self.villes.copy()
        villes_non_visites.remove(ville_depart)
        heure_passe = heure_depart
        distance_sans_repo = 0
        capacite_restant = voyageur.capacite_vehicule
        chemins = [ville_depart]

        while True:
            ville_actuelle = chemins[-1]
            ville_suivante = self.chercher_ville_suivante(
                voyageur, capacite_restant, ville_actuelle, villes_non_visites, heure_passe, distance_sans_repo
            )
            if ville_suivante is not None:
                chemins.append(ville_suivante)
                distance_aller = distance(ville_actuelle, ville_suivante)
                capacite_restant -= ville_suivante.demande
                heure_passe += distance_aller * self.temps_pour_km
                heure_passe = normaliser_heure(heure_passe)
                distance_sans_repo += distance_aller

                if distance_sans_repo >= voyageur.distance_pour_repo:
                    nbre_repos = int(distance_sans_repo // voyageur.distance_pour_repo)
                    heure_passe += voyageur.temps_de_repo * nbre_repos
                    heure_passe = normaliser_heure(heure_passe)
                    distance_sans_repo = distance_sans_repo % voyageur.distance_pour_repo

                if heure_passe < ville_suivante.window_start:
                    heure_passe = ville_suivante.window_start

                villes_non_visites.remove(ville_suivante)
            else:
                while len(chemins) > 1:
                    if (chemins[-1].id, ville_depart.id) not in self.connexions_ignores:
                        chemins.append(ville_depart)
                        return chemins
                    else:
                        chemins.remove(chemins[-1])
                return None

    def afficher_parcours(self, voyageur : Voyageur, ville_depart : Ville, heure_depart : float):
        """
        Affiche le parcours trouvé par l'algorithme.

        Args:
            voyageur (Voyageur): Le voyageur.
            ville_depart (Ville): Ville de départ.
            heure_depart (float): Heure de départ (heures décimales).
        """
        parcours = self.chercher_parcours(voyageur, ville_depart, heure_depart)

        if parcours is None:
            print("Aucun parcours valide trouvé.")
        else:
            print("Parcours trouvé :")
            print(" → ".join(str(v.nom) for v in parcours))
