from qtpy.QtWidgets import (QApplication, QFrame)
from robotsomes_fenetres import *
import json
import sys

if __name__ == "__main__":
    # ********** Corps du programme **********
    # Lance l'application
    app=QApplication(sys.argv)
    # Création de la fenêtre princiale de type Fenetre
    frame = Fenetre()
    # Affichhe le composant principale de frame
    frame.widgetP.show()
    sys.exit(app.exec_())
