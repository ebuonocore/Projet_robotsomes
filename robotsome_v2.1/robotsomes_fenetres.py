# ********** Bibliothèques **********
from robotsomes_class import *
import sys
import json
import time
# Bibliothèques qtpy pour les graphiques
from qtpy import QtGui
from qtpy.QtWidgets import (QLabel, QWidget, QHBoxLayout)
from qtpy.QtWidgets import (QMainWindow, QDesktopWidget, QVBoxLayout)
from qtpy.QtWidgets import (QPushButton, QSpinBox, QTextEdit, QCheckBox,QGroupBox)
from qtpy.QtWidgets import (QRadioButton, QFileDialog)
from qtpy.QtGui import QPainter, QColor, QPixmap, QImage
from qtpy.QtCore import Qt
# ********** Classes **********
class ZoneDessin(QWidget):
    """ZoneDessin construit le widget qui accueille le dessin
    Programmation événementielle: Lors de l'appel de la methode repaint(),
    les éléments sont redessines
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Echelle du dessin, recalculee lors de l'appel à self.paint()
        self.echelleDessin = 30
        self.monde = "fleche1"
        self.marge = 0.4
        self.P = Plateau()
        # Definit une couleur de fond blanche
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(palette)
        # Definition des images (flèches)
        self.persoN = QPixmap()
        self.persoN_redim = QPixmap()
        self.persoE_redim = QPixmap()
        self.persoS_redim = QPixmap()
        self.persoO_redim = QPixmap()
        self.bloc = QPixmap()
        self.bloc_redim = QPixmap()
        self.sortie = QPixmap()
        self.sortie_redim = QPixmap()

    def dessine_tableau(self, qp:QPainter):
        """ Definition de toutes les étapes du dessin dans le QPainter
        """
        ech = self.echelleDessin
        grille = self.P.grille
        j_max = self.P.hauteur
        i_max = self.P.largeur
        if j_max > 0:
            for j  in range(j_max+1):
                for i in range(i_max+1):
                    x = self.indice_vers_pixels(i) - ech//3
                    y = self.indice_vers_pixels(j_max-j) - ech//3
                    if str(grille[j][i]) == 'X':
                        image = self.bloc_redim
                    elif str(grille[j][i]) == 'A':
                        image = self.persoN_redim
                    elif str(grille[j][i]) == '>':
                        image = self.persoE_redim
                    elif str(grille[j][i]) == 'V':
                        image = self.persoS_redim
                    elif str(grille[j][i]) == '<':
                        image = self.persoO_redim
                    elif str(grille[j][i]) == 'S':
                        image = self.sortie_redim
                    else:
                        image = None
                    if image != None:
                        qp.drawPixmap(x, y, image)
            color = QtGui.QColor(200, 200, 200)
            qp.setBrush(QColor(200, 200, 200))
            pen = QtGui.QPen(color, ech//20, Qt.DashDotLine)
            qp.setPen(pen)
            x_min = self.indice_vers_pixels(0) - ech//3
            x_max = self.indice_vers_pixels(i_max+1) - ech//3
            y_min = self.indice_vers_pixels(0) - ech//3
            y_max = self.indice_vers_pixels(j_max+1) - ech//3
            for j  in range(j_max):
                y = self.indice_vers_pixels(j_max-j) - ech//3
                qp.drawLine(x_min, y, x_max, y)
            for i in range(2,i_max+2):
                x = self.indice_vers_pixels(i-1) - ech//3
                qp.drawLine(x, y_min, x, y_max)
                    

    def indice_vers_pixels(self, indice: int) -> int:
        """ Prend l'indice d'une position dans le tableau et le traduit en
        position ecran (pixel) en fonction de l'attribut self.echelleDessin
        """
        echelle = self.echelleDessin
        return (indice+1) * echelle - echelle*self.marge//2

    def paintEvent(self,event):
        """ Lance le dessin des differents objets (flèches, cases, lignes)
        dans la zone de dessin
        """
        qp = QPainter()
        qp.begin(self)
        self.dessine_tableau(qp)
        qp.end()

class Fenetre(QMainWindow):
    """Fenêtre graphique principale.
    Elle contient widgetP qui sera affiche, constitue d'un layout horizontal
    (zoneP) contenant, à gauche le dessin et à droite, widgetD, la structure
    des boutons, cases et spinbox...
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dessin = ZoneDessin()
        self.setWindowTitle("robotsomes")

        self.widgetP = QWidget()  # Widget principal
        self.zoneP = QHBoxLayout()  # Cadre principal
        self.widgetD = QWidget()  # Widget droit
        self.colonneD = QVBoxLayout()  # Cadre droit pour widgetD
        # Elements de la partie 'Parametrages'
        self.radios_group = QGroupBox('Choix du monde')
        self.radios_vbox = QVBoxLayout() 
        self.radio_monde1 = QRadioButton('Flèche')
        self.radio_monde1.setChecked(True)
        self.radio_monde1.clicked.connect(self.choix_monde1)
        self.radio_monde2 = QRadioButton('Fourmi')
        self.radio_monde2.clicked.connect(self.choix_monde2)
        self.radio_monde3 = QRadioButton('Fourmi_robot')
        self.radio_monde3.clicked.connect(self.choix_monde3)
        self.radio_monde4 = QRadioButton('Robot')
        self.radio_monde4.clicked.connect(self.choix_monde4)
        self.radio_monde5 = QRadioButton('Drone')
        self.radio_monde5.clicked.connect(self.choix_monde5)
        self.buttonNiveau = QPushButton('Niveau')
        self.buttonNiveau.clicked.connect(self.choisir_niveau)
        self.message = QTextEdit()
        self.message.setReadOnly(True)
        self.message.setPlainText("Veuillez sélectionner un niveau")
        self.labelCommandes = QLabel('Commandes')
        self.commandes = QTextEdit()
        self.buttonLancer = QPushButton('Lancer')
        self.buttonLancer.clicked.connect(self.lancer)
        self.buttonQuit = QPushButton('Quitter')
        self.buttonQuit.clicked.connect(sys.exit)
        
        dim = self.taille_ecran()
        self.redimensionne_images()
        
        self.radios_vbox.addWidget(self.radio_monde1)
        self.radios_vbox.addWidget(self.radio_monde2)
        self.radios_vbox.addWidget(self.radio_monde3)
        self.radios_vbox.addWidget(self.radio_monde4)
        self.radios_vbox.addWidget(self.radio_monde5)
        self.radios_group.setLayout(self.radios_vbox)
        self.colonneD.addWidget(self.radios_group)
        self.colonneD.addWidget(self.message)
        self.colonneD.addWidget(self.buttonNiveau)
        self.colonneD.addWidget(self.labelCommandes)
        self.colonneD.addWidget(self.commandes)
        self.colonneD.addWidget(self.buttonLancer)
        self.colonneD.addWidget(self.buttonQuit)
        self.widgetD.setLayout(self.colonneD)
        self.widgetD.setMaximumWidth(200)
        self.zoneP.addWidget(self.dessin)
        self.zoneP.addWidget(self.widgetD)
        self.widgetP.setLayout(self.zoneP)
        self.widgetP.setGeometry(25, 40, dim[0]*2//3, dim[1]*2//3)


    def calculEchelle(self, largeur, hauteur)->tuple:
        """ A partir de la taille de la zone de dessin ou des paramètres de 
        la sauvegarde souhaitee, met à jour self.dessin.echelleDessin
        Renvoie en pixels la largeur et la hauteur reelles de l'image produite
        """
        D = self.dessin
        # Largeur de la fenêtre / nombre de lignes plus marges
        h_max = hauteur // (D.P.hauteur + 1 + D.marge*2)
        l_max = largeur // (D.P.largeur + 1 + D.marge*2)
        ech  = min(h_max, l_max)
        D.echelleDessin = ech
        largeurReelle = int((D.P.hauteur + 1 + D.marge*2) * ech)
        hauteurReelle = int((D.P.largeur + 1 + D.marge*2) * ech)
        return largeurReelle, hauteurReelle

    def choisir_niveau(self):
        chemin, extension = QFileDialog.getOpenFileName(self, "Choisir un niveau", "",
                                                        "Niveaux (*.json)")
        with open(chemin) as json_data:
            data_dict = json.load(json_data)
        # jeu_1.json: Solution = "AGAAAAAADDAGAAA"
        # jeu_2.json: Solution = "DAAAAAADAGAGAAAAAAA"
        largeur = data_dict["largeur"]
        hauteur = data_dict["hauteur"]
        fourmis = data_dict["fourmis"]
        cases_noires = data_dict["cases_noires"]
        sorties = data_dict["sorties"]
        # Création du plateau de jeu
        self.dessin.P = Plateau(largeur, hauteur, fourmis, cases_noires, sorties)
        self.redimensionne_images()
        self.dessin.repaint()
        return
    
    def choix_monde1(self):
        self.dessin.monde = "fleche1"
        self.redimensionne_images()
        self.dessin.repaint()
        
    def choix_monde2(self):
        self.dessin.monde = "fourmi1"
        self.redimensionne_images()
        self.dessin.repaint()
        
    def choix_monde3(self):
        self.dessin.monde = "fourmi2"
        self.redimensionne_images()
        self.dessin.repaint()
        
    def choix_monde4(self):
        self.dessin.monde = "robot1"
        self.redimensionne_images()
        self.dessin.repaint()
        
    def choix_monde5(self):
        self.dessin.monde = "drone1"
        self.redimensionne_images()
        self.dessin.repaint()
        
    def lancer(self):
        commandes = self.commandes.toPlainText()
        for commande in commandes:
            if commande == 'A':
                self.dessin.P.commande_A()
            elif commande == 'G':
                self.dessin.P.commande_G()
            elif commande == 'D':
                self.dessin.P.commande_D()
            time.sleep(0.5)
            self.taille_ecran()
            self.dessin.repaint()
            reste = self.dessin.P.vérifier_sorties()
        if reste == 0:
            self.message.setPlainText("Vous avez gagné")
        else:
            texte = "Il reste encore "+str(reste)+self.dessin.monde[:-1]
            self.message.setPlainText(texte)

    def redimensionne_images(self):
        self.taille_ecran()
        D = self.dessin
        ech = D.echelleDessin
        transform = QtGui.QTransform().rotate(90)
        # Chargement des images
        D.persoN.load("monde_"+D.monde+".png")
        D.bloc.load("monde_"+D.monde+"_bloc.png")
        D.sortie.load("monde_"+D.monde+"_sortie.png")
        # Redimension des images de base
        D.persoN_redim = D.persoN.scaled(ech, ech)
        D.bloc_redim = D.bloc.scaled(ech, ech)
        D.sortie_redim = D.sortie.scaled(ech, ech)
        # Création des autres images par rotation
        D.persoE_redim = D.persoN_redim.transformed(transform, Qt.SmoothTransformation)
        D.persoS_redim = D.persoE_redim.transformed(transform, Qt.SmoothTransformation)
        D.persoO_redim = D.persoS_redim.transformed(transform, Qt.SmoothTransformation)

    def taille_ecran(self) -> tuple:
        """ Renvoie un n-uplet constitue de :
        largeur de la fenêtre, hauteur de la fenêtre, largeur dessin , hauteur dessin
        Recalcule la valeur de self.dessin.echelleDessin
        genère les images miniatures des flèches
        """
        D = self.dessin
        dimensions_ecran = QDesktopWidget().screenGeometry()
        largeur_ecran = dimensions_ecran.width()
        hauteur_ecran = dimensions_ecran.height()
        # Recupère les paramètres de la zone de dessin
        # largeur utile de la zone de dessin
        largeurDessin = D.size().width()
        # hauteur utile de la zone de dessin
        hauteurDessin = D.size().height()
        largeur, hauteur = self.calculEchelle(largeurDessin, hauteurDessin)
        return (largeur_ecran, hauteur_ecran, largeurDessin, hauteurDessin)
