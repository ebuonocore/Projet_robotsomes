""" Strucutures du jeu robotsomes
"""
import  functools

class Plateau:
    def __init__(self, _largeur:int =0, _hauteur:int =0, _fourmis:list = None, _cases_noires:list = None, _sorties:list = None):
        self.largeur = _largeur
        self.hauteur = _hauteur
        self.grille = []
        for j in range(_hauteur+1): # Construction des toutes les cases du plateau (self.grille)
            ligne = []
            for i in range(_largeur+1):
                if i ==0 or i ==_largeur or j==0 or j==_hauteur:
                    c = Case(1)
                    ligne.append(c)
                else:
                    c = Case(0)
                    ligne.append(c)
            self.grille.append(ligne)
        num_fourmi = 0 # Place les fourmis dans le plateau
        if _fourmis != None:
            for fourmi in _fourmis:
                case = self.grille[fourmi[1]][fourmi[0]]
                case.fourmi = num_fourmi
                case.NESO = fourmi[2]
                num_fourmi += 1
        if _cases_noires != None:
            for bloc in _cases_noires: # Place les cases noires (hors bordure) dans le plateau
                case = self.grille[bloc[1]][bloc[0]]
                case.nature = 1
        if _sorties != None:
            for sortie in _sorties: # Place les sorties dans le plateau
                case = self.grille[sortie[1]][sortie[0]]
                case.nature = -1
            
    def bloquer(self, _case):
        """ Marque la case _case comme bloquée. Fixe la fourmi sur cette case.
            Bloque récursivement la case d'où vient la fourmi qui convoitait cette case.
        """
        _case.bloquée = True
        _case_source = _case.convoitée_par 
        _case.convoitée_par = _case # Fixe la fourmi sur place
        if _case_source != None: # Bloque en cascade les fourmis dépendant de la validité de ce déplacement
            self.bloquer(_case_source)
        
    
    def commande_G(self):
        """ Opère une rotation de toutes les fourmis vers leur gauche """
        for case in functools.reduce(list.__add__, self.grille): # Parcourt toutes les cases
            if case.fourmi != None:
                case.NESO = (case.NESO-1)%4       
    
    def commande_D(self):
        """ Opère une rotation de toutes les fourmis vers leur droite """
        for case in functools.reduce(list.__add__, self.grille): # Parcourt toutes les cases
            if case.fourmi != None:
                case.NESO = (case.NESO+1)%4
                      
    def commande_A(self):
        """ Tente de faire avancer toutes les fourmis """
        self.nettoyer_plateau()
        sens = [(0,1),(1,0),(0,-1),(-1,0)]
        for y in range(len(self.grille)):
            for x in range(len(self.grille[0])):
                case = self.grille[y][x]
                if case.fourmi != None: # Si cette case abrite une fourmi, il faut tenter de la faire avancer
                    # Cette fourmi doit se rendre dans la case de coordonnées (_x,_y)
                    dy = sens[case.NESO][1]
                    dx = sens[case.NESO][0]
                    case_convoitée = self.grille[y + dy][x + dx]
                    if case_convoitée.bloquée: # Cette case n'est pas accessible. Il faut bloquer notre fourmi ici
                        self.bloquer(case) # Récursivement, toutes les fourmis dépendant de ce déplacement seront bloquées
                    elif case_convoitée.convoitée_par != None: # Cette case est déjà visée par une autre fourmi
                        self.bloquer(case)
                        self.bloquer(case_convoitée.convoitée_par) # On la bloque, ainsi que toutes les autres fourmis qui dépendent de cette case
                        case_convoitée.convoitée_par = None # Personne n'entrera ici
                        case_convoitée.bloquée = True
                    else: # Cette case est libre. Notre fourmi peut prétendre à y entrer
                        case_convoitée.convoitée_par = case
        self.valider_déplacements()
        self.nettoyer_plateau()
    
    def nettoyer_plateau(self):
        """ Réinitialise les blocages des cases (uniquement les noires). Vide les attibuts convoitée_par"""
        for case in functools.reduce(list.__add__, self.grille): # Parcourt toutes les cases
            if case.nature != 1: # Débloque toutes les cases qui ne sont pas noires
                case.bloquée = False
            else:
                case.bloquée = True
            case.convoitée_par = None
    
    def valider_déplacements(self):
        """ Migre les fourmis dont le déplacement est valide. Conserve l'orientation."""
        bonnes_places = [] # Memorise les futurs emplacements des fourmis
        for case in functools.reduce(list.__add__, self.grille): # Parcourt toutes les cases
            if case.convoitée_par != None:
                bonnes_places.append((case, case.convoitée_par.fourmi, case.convoitée_par.NESO))
        for case in functools.reduce(list.__add__, self.grille): # Purge les anciens emplacements des fourmis
            case.fourmi = None
        for place in bonnes_places: # Valide les déplacements
            place[0].fourmi = place[1]
            place[0].NESO = place[2]
            
    def vérifier_sorties(self):
        """ Vérifie si des fourmis ont atteint des sortie. Renvoie le nombre de fourmis restantes."""
        nb_fourmis = 0
        for case in functools.reduce(list.__add__, self.grille): # Parcourt toutes les cases
            if case.fourmi != None:
                if case.nature == -1: # Cette fourmi a trouvé une sortie
                    case.fourmi = None
                else:
                    nb_fourmis += 1
        return nb_fourmis

    def __str__(self):
        str_tableau = ""
        for ligne in self.grille:
            str_ligne = ""
            for c in ligne:
                str_ligne += str(c)
            str_tableau = str_ligne + "\n" + str_tableau # Empile les lignes
        return str_tableau
        
class Case:
    def __init__(self, nature:int, num_fourmi:int = None, orientation:int = None):
        self.nature = nature  # 0:Caseblanche; 1:Case noire; -1:Case blanche sortie
        self.fourmi = num_fourmi # Indice de la fourmi présente sur cette case
        self.NESO = orientation #  Orientation de la fourmi présente sinon None.
        # 0: Nord; 1:Est; 2:Sud; 3:Ouest
        self.convoitée_par = None # (i,x,y,NESO):Indice de la fourmi qui souhaite entrer sur cette case, coordonnées de départ et orientation
        self.bloquée = False # True si un déplacement est impossible vers cette case
    
    def __str__(self):
        list_neso = ['A','>','V','<']
        if self.nature == 0:
            if self.fourmi == None:
                return ' . '
            else:
                return list_neso[self.NESO]
        elif self.nature == 1:
            return 'X'
        else:
            return 'S'