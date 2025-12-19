import json
from src.tsp_optimisation.ville import Ville
from src.tsp_optimisation.voyageur import Voyageur

def charger_donnees(fichier_json: str):
    """
    Charge les données du problème depuis un fichier JSON.

    Le fichier JSON doit contenir :
        - "villes" : liste des villes avec leurs coordonnées, fenêtre horaire et demande.
        - "voyageur" : informations sur le véhicule (capacité, distance avant repos, durée de repos).
        - "connexions_ignores" : liste des routes interdites entre villes (id1, id2).
        - "temps_pour_km" : temps nécessaire pour parcourir 1 km (heures/km).
        - "heure_depart" : heure de départ du voyageur en heures décimales.
        - "ville_depart_id" : id de la ville de départ.

    Attention : toutes les heures doivent être exprimées en heures décimales.
                Par exemple, 10h30 doit être écrit 10.5.

    Args:
        fichier_json (str): Chemin vers le fichier JSON.

    Returns:
        tuple:
            villes (list[Ville]) : Liste d'objets Ville.
            voyageur (Voyageur) : Objet représentant le voyageur.
            connexions_ignores (list[tuple[int,int]]) : Liste de couples de villes interdites.
            temps_pour_km (float) : Temps pour parcourir 1 km (heures/km).
            heure_depart (float) : Heure de départ du voyageur (heures décimales).
            ville_depart_id (int) : ID de la ville de départ.
    """
    with open(fichier_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    villes = [
        Ville(
            id_ville=v["id"],
            nom=v["nom"],
            x=v["x"],
            y=v["y"],
            window_start=v["window_start"],
            window_end=v["window_end"],
            demande=v["demande"]
        )
        for v in data["villes"]
    ]

    voyageur = Voyageur(
        capacite_vehicule=data["voyageur"]["capacite_vehicule"],
        distance_pour_repo=data["voyageur"]["distance_pour_repo"],
        temps_de_repo=data["voyageur"]["temps_de_repo"]
    )

    connexions_ignores = [(c[0], c[1]) for c in data["connexions_ignores"]]

    return (
        villes,
        voyageur,
        connexions_ignores,
        data["temps_pour_km"],
        data["heure_depart"],
        data["ville_depart_id"]
    )
