class Voyageur:
    """
    Représente un voyageur dans le problème du voyageur de commerce (TSP) avec contraintes.

    Le voyageur transporte des marchandises, doit se reposer après une certaine distance,
    et dispose d'une capacité maximale de transport.

    Attributs :
        capacite_vehicule (int): Capacité maximale du véhicule en unités de marchandise.
        distance_pour_repo (float): Distance maximale que le voyageur peut parcourir avant de devoir se reposer (en km).
        temps_de_repo (float): Durée d'un repos en heures.
    """

    def __init__(self, capacite_vehicule: int, distance_pour_repo: float, temps_de_repo: float):
        """
        Initialise une nouvelle instance de Voyageur.

        Args:
            capacite_vehicule (int): Capacité maximale du véhicule en unités de marchandise.
            distance_pour_repo (float): Distance maximale avant qu'un repos soit nécessaire.
            temps_de_repo (float): Durée d'un repos en heures.
        """
        self.capacite_vehicule = capacite_vehicule
        self.distance_pour_repo = distance_pour_repo
        self.temps_de_repo = temps_de_repo
