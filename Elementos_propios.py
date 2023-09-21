from PyQt5.QtWidgets import QPushButton, QStyleFactory
from PyQt5.QtCore import QPropertyAnimation, QAbstractAnimation, QRect

class BotonIluminado(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMouseTracking(True)

        self.posicionX = int
        self.posicionY = int

    def enterEvent(self, event):
        super().enterEvent(event)
        self.posicionX = self.pos().x()
        self.posicionY = self.pos().y()
        self.ancho = self.width()
        self.alto = self.height()
        self.fuente = self.font()
        self.tamaño_fuente = self.fuente.pointSize()
        self.estilos = self.styleSheet()
        
        if self.isEnabled():
            self.animacionCursor = QPropertyAnimation(self, b"geometry")
            self.animacionCursor.setDuration(100)
            start = (int(self.posicionX*0.99), int(self.posicionY*0.99))
            end = (int(self.ancho*1.1), int(self.alto*1.1))
            self.animacionCursor.setEndValue(QRect(*start, *end))
            self.animacionCursor.start(QAbstractAnimation.DeleteWhenStopped)
            
            self.fuente.setPointSize(int(self.tamaño_fuente*1.15))
            self.setStyleSheet(f"""{self.estilos} 
                                background-color: rgb(225, 255, 255);
                                border: 1.5px groove rgb(0, 128, 255);""")
            self.setFont(self.fuente)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.fuente.setPointSize(self.tamaño_fuente)
        self.setFont(self.fuente)
        self.setStyleSheet(self.estilos)
        
        self.animacionNoCursor = QPropertyAnimation(self, b"geometry")
        self.animacionNoCursor.setDuration(100)
        self.animacionNoCursor.setEndValue(QRect(self.posicionX, self.posicionY, self.ancho, self.alto))
        self.animacionNoCursor.start(QAbstractAnimation.DeleteWhenStopped)