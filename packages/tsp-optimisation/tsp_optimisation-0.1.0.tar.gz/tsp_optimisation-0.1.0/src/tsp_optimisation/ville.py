class Ville:
    """
    Représente une ville pour le problème du voyageur de commerce (TSP) avec contraintes.

    Chaque ville possède des coordonnées dans un plan, une fenêtre horaire pour les visites,
    et une demande en marchandises.

    Attributs :
        id (int) : Identifiant unique de la ville.
        nom (str) : Nom de la ville.
        x (int) : Coordonnée X de la ville.
        y (int) : Coordonnée Y de la ville.
        window_start (float) : Heure d'ouverture de la ville (en heures décimales, ex: 8.5 = 8h30).
        window_end (float) : Heure de fermeture de la ville (en heures décimales).
        demande (int) : Quantité de marchandise à livrer dans cette ville.
    """

    def __init__(self, id_ville: int, nom: str, x: int, y: int, window_start: float, window_end: float, demande: int):
        """
        Initialise une nouvelle instance de Ville.

        Args:
            id_ville (int): Identifiant unique de la ville.
            nom (str): Nom de la ville.
            x (int): Coordonnée X de la ville.
            y (int): Coordonnée Y de la ville.
            window_start (float): Heure d'ouverture de la ville en heures décimales.
            window_end (float): Heure de fermeture de la ville en heures décimales.
            demande (int): Quantité de marchandise à livrer dans cette ville.
        """
        self.id = id_ville
        self.nom = nom
        self.x = x
        self.y = y
        self.window_start = window_start
        self.window_end = window_end
        self.demande = demande
