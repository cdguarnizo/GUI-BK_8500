#from curses.ascii import isdigit
from fileinput import close
from socket import timeout
import serial
from Funciones_Carga import*
import time
import sys
#from Archivo_CSV import GuardarCSV
from tkinter import HIDDEN
from Carga_electronica_ui import *
from Ventana_advertencia_ui import *
#import matplotlib
#matplotlib.use('Qt5Agg')
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, QObject
import os
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CargaPuertos(QObject):
    cargado = pyqtSignal()
    
    def __init__(self, ventana, parent=None):
        super().__init__(parent)
        self.ventana = ventana
    
    def run(self):
        #Esta función detecta los puestos COM disponibles en windows
        # Taken from StackOverflow, find available serial ports:
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(20)]
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        if len(result)==0:
            result.append("")
            
        self.ventana.ui.CmbPuerto.addItems(result)
        self.cargado.emit()

class Advertencia(QMainWindow,Ui_Advertencia):
    def __init__(self, parent=None):
        super().__init__()
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Advertencia()
        self.ui.setupUi(self)
        basedir=os.path.dirname(__file__)
        self.setWindowIcon(QtGui.QIcon(os.path.join(basedir,'Icono_4.png')))

class Ventana(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__()
        QtWidgets.QWidget.__init__(self, parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer = QTimer(self)
        self.ModoSelecc = "CC"
        self.T = []
        self.V = []
        self.C = []
        self.P = []
        self.Bateriaflag = False
        basedir=os.path.dirname(__file__)
        self.setWindowIcon(QtGui.QIcon(os.path.join(basedir,'Icono_4.png')))
        
        self.Cargando = Advertencia()
        self.Cargando.show()
        self.th = QThread()
        self.puertos = CargaPuertos(self)
        self.puertos.moveToThread(self.th)
        self.th.started.connect(self.puertos.run)
        self.puertos.cargado.connect(self.th.quit)
        self.puertos.cargado.connect(self.puertos.deleteLater)
        self.puertos.cargado.connect(self.Cargando.close)
        self.puertos.cargado.connect(self.show)
        self.th.finished.connect(self.th.deleteLater)
        self.th.start()
        
        # scene = QtWidgets.QGraphicsScene()
        #view = QtWidgets.QGraphicsView(scene)
        
        # self.ui.graphicsView.setScene(scene)
        # w = self.ui.graphicsView.width()
        # h = self.ui.graphicsView.height() + 20
        # global mi_aplicacion
        # dpi = mi_aplicacion.screens()[0].physicalDotsPerInch()
        # self.figure = Figure(figsize=(w/dpi, h/dpi))
        # self.Voltaje_Plot = self.figure.add_subplot(1,1,1)
        # self.Corriente_Plot = self.Voltaje_Plot.twinx()
        
        

        #view.resize(440, 240)
        # self.canvas = FigureCanvas(self.figure)
        # scene.addWidget(self.canvas)
        # or
        # proxy_widget = QtWidgets.QGraphicsProxyWidget()
        # proxy_widget.setWidget(canvas)
        # scene.addItem(proxy_widget)
        #view.show()
        
        #Para activar/desactivar y mostrar/ocultar (solo visualización)
        #Comunicación serial
        self.ui.BtnDesconectar.setEnabled(False)
        self.ui.BtnConectar.setEnabled(True)
        self.ui.BtnConectar.show()
        self.ui.BtnDesconectar.hide()
        self.ui.LblDesconectado.show()
        self.ui.LblConectado.hide()
        
        #Encender/apagar carga electrónica
        self.ui.BtnApagar.setEnabled(False)
        self.ui.BtnEncender.setEnabled(False)
        self.ui.BtnEncender.show()
        self.ui.BtnApagar.hide()
        self.ui.LblApagado.show()
        self.ui.LblEncendido.hide()
        
        #Lectura de V, C  y P
        self.ui.Txt_LeeVolt.setEnabled(False)
        self.ui.Txt_LeeCorr.setEnabled(False)
        self.ui.Txt_LeePot.setEnabled(False)
        
        #Configuración del instrumento
        self.ui.BtnEstablecerMax.setEnabled(False)
        self.ui.TextLimV.setEnabled(False)
        self.ui.TextLimC.setEnabled(False)
        self.ui.TextLimP.setEnabled(False)
        
        #Información carga electrónica
        self.ui.label_17.hide()
        self.ui.label_18.hide()
        self.ui.label_19.hide()
        
        #Modo de operación
        self.ui.Rbtn_MCC.setEnabled(False)
        self.ui.Rbtn_MCV.setEnabled(False)
        self.ui.Rbtn_MCW.setEnabled(False)
        self.ui.Rbtn_MCR.setEnabled(False)
        
        #Valor según modo de  operación
        self.ui.BtnEstablecerValMod.setEnabled(False)
        self.ui.TextVCV.setEnabled(False)
        self.ui.TextCCC.setEnabled(False)
        self.ui.TextPCW.setEnabled(False)
        self.ui.TextRCR.setEnabled(False)
        
        #Función de trabajo
        self.ui.Rbtn_Fijo.hide()
        self.ui.Rbtn_Corto.setEnabled(False)
        self.ui.Rbtn_Lista.setEnabled(False)
        self.ui.Rbtn_Bateria.setEnabled(False)
        
        #Prueba de baterías
        self.ui.BtnIniciar_PBateria.setEnabled(False)
        self.ui.BtnParar_PBateria.setEnabled(False)
        self.ui.TextCCC_Bat.setEnabled(False)
        self.ui.TextVoltmin_PBateria.setEnabled(False)
        self.ui.BtnParar_PBateria.hide()
        self.ui.BtnIniciar_PBateria.show()
        
        #Simulación de corto
        self.ui.BtnIniciar_Corto.setEnabled(False)
        self.ui.BtnParar_Corto.setEnabled(False)
        self.ui.Cmb_ModoCorto.setEnabled(False)
        self.ui.BtnParar_Corto.hide()
        self.ui.BtnIniciar_Corto.show()
        
        #Operación de lista
        self.ui.Rbtn_Unavez.setEnabled(False)
        self.ui.Rbtn_Repetir.setEnabled(False)
        self.ui.Cmb_ModoLista.setEnabled(False)
        self.ui.BtnEstablecer_OpLista.setEnabled(False)
        self.ui.BtnIniciar_Lista.setEnabled(False)
        self.ui.BtnParar_Lista.setEnabled(False)
        self.ui.Txt_Val_min.setEnabled(False)
        self.ui.Txt_NumPasos.setEnabled(False)
        self.ui.Txt_Val_max.setEnabled(False)
        self.ui.Txt_Val_tiempo.setEnabled(False)
        self.ui.BtnParar_Lista.hide()
        self.ui.BtnIniciar_Lista.show()
        self.ui.LblVmin.hide()
        self.ui.LblVmax.hide()
        self.ui.LblCmin.show()
        self.ui.LblCmax.show()
        self.ui.LblPotmin.hide()
        self.ui.LblPotmax.hide()
        self.ui.LblOhmmin.hide()
        self.ui.LblOhmmax.hide()
        self.Encendido = False
        
        #Botón conectar
        self.ui.BtnConectar.clicked.connect(self.Comunica)
        # self.ui.BtnConectar.enterEvent = self.Entrar
        # self.ui.BtnConectar.leaveEvent = self.Salir
        
        #Botón desconectar
        self.ui.BtnDesconectar.clicked.connect(self.Desconecta)
        #QmainWindow:close(self.Desconecta)  #REVISAR--------------------------------
        
        #Botón encender
        self.ui.BtnEncender.clicked.connect(self.Enciende)
        
        #Botón apagar
        self.ui.BtnApagar.clicked.connect(self.Apaga)
        
        #Botón establecer
        self.ui.BtnEstablecerMax.clicked.connect(self.Limites)
        
        #Selección modo de operación
        self.ui.Rbtn_MCC.toggled.connect(self.Seleccion_ModoOP)
        self.ui.Rbtn_MCV.toggled.connect(self.Seleccion_ModoOP)
        self.ui.Rbtn_MCW.toggled.connect(self.Seleccion_ModoOP)
        self.ui.Rbtn_MCR.toggled.connect(self.Seleccion_ModoOP)
        
        self.ui.Rbtn_Corto.toggled.connect(self.Seleccion_Funcion)
        self.ui.Rbtn_Lista.toggled.connect(self.Seleccion_Funcion)
        self.ui.Rbtn_Bateria.toggled.connect(self.Seleccion_Funcion)
        
        
        #Selección repetir o realizar una sola vez una lista
        self.ui.Rbtn_Unavez.toggled.connect(self.Seleccion_Rep_Lista)
        self.ui.Rbtn_Repetir.toggled.connect(self.Seleccion_Rep_Lista)
        
        #Establecer valores según modo de operación
        self.ui.BtnEstablecerValMod.clicked.connect(self.Poner_valores_ModoOP)
        
        #Guardar configuración de Lista de operación
        self.ui.BtnEstablecer_OpLista.clicked.connect(self.Funcion_Lista)
        
        Indice = self.ui.tabWidget.currentIndex()
        self.ui.tabWidget.currentChanged.connect(self.Funcion_Tab)
                
        #Iniciar la lista de operación
        self.ui.BtnIniciar_Lista.clicked.connect(self.Iniciar_Lista)
        
        #Iniciar la prueba de batería
        self.ui.BtnIniciar_PBateria.clicked.connect(self.Prueba_BateriaON)
        
        #Parar la prueba de batería
        self.ui.BtnParar_PBateria.clicked.connect(self.Prueba_BateriaOFF)  
        
        #Iniciar la prueba de corto
        self.ui.BtnIniciar_Corto.clicked.connect(self.Prueba_CortoOn)
        
        #Parar la prueba de corto
        self.ui.BtnParar_Corto.clicked.connect(self.Prueba_CortoOff)           
        
        self.ui.BtnParar_Lista.clicked.connect(self.Parar_Lista)
        
        #Llama a la función de verificar texto en cada cuadro de texto de entrada
        self.ui.TextLimV.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextLimV))
        self.ui.TextLimC.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextLimC))
        self.ui.TextLimP.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextLimP))
        
        self.ui.TextVCV.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextVCV))
        self.ui.TextCCC.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextCCC))
        self.ui.TextPCW.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextPCW))
        self.ui.TextRCR.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextRCR))
        
        self.ui.TextCCC_Bat.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextCCC_Bat))
        self.ui.TextVoltmin_PBateria.textChanged.connect(lambda: self.Verificacion_texto(self.ui.TextVoltmin_PBateria))
        
        self.ui.Txt_Val_min.textChanged.connect(lambda: self.Verificacion_texto(self.ui.Txt_Val_min))
        self.ui.Txt_NumPasos.textChanged.connect(lambda: self.Verificacion_texto(self.ui.Txt_NumPasos))
        self.ui.Txt_Val_max.textChanged.connect(lambda: self.Verificacion_texto(self.ui.Txt_Val_max))
        self.ui.Txt_Val_tiempo.textChanged.connect(lambda: self.Verificacion_texto(self.ui.Txt_Val_tiempo))
        
        self.ui.Cmb_ModoLista.currentIndexChanged.connect(self.CambioModoOp_Lista)
        
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.comunicacion.is_open:
            print("Desconectando...")
            self.Desconecta()
        print("Cerrando...")
        return super().closeEvent(a0)
    
    def Verificacion_texto(self, Elemento):
        texto = Elemento.text()
        if texto and not (texto[-1].isdigit() or texto[-1]=="."): 
            Elemento.setText(texto[:-1])
    
    def Ventana_Advertencia(self, mensaje):
        msg=QMessageBox()
        msg.setWindowTitle("Advertencia")
        msg.setText(mensaje)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec_()

    def Funcion_Tab(self, Indice: int):
        try:
            #Indice = self.ui.tabWidget.currentIndex()
            if Indice == 0 and hasattr(self, 'comunicacion') and self.Encendido == False:
                Selec_Funcion(self.comunicacion, 0)
                Func = Leer_Funcion(self.comunicacion)
                self.ui.LblFuncion.setText(Func)
                self.ui.Rbtn_Fijo.setChecked(True)
        except: serial.serialutil.PortNotOpenError

    #Función para comunicarse con la carga y activar el control remoto
    def Comunica(self):
        try:
            self.comunicacion = serial.Serial(timeout=1, write_timeout=1)
            self.comunicacion.baudrate = int(self.ui.CmbBaudrate.currentText())
            self.comunicacion.port = str(self.ui.CmbPuerto.currentText())
            self.comunicacion.open()
            Control_remoto_local(self.comunicacion, 1)
            Modo = Leer_Modo_operacion(self.comunicacion)

            #Al conectar se inicializa en la función fijo
            Selec_Funcion(self.comunicacion, 0)
            
            Funcion = Leer_Funcion(self.comunicacion)
            
            #Cuando se comunica muestra el  modo de operación 
            self.ui.LblModoOP.setText(Modo)
            self.ui.LblFuncion.setText(Funcion)
            
            if  Modo == "CC":
                self.ui.Rbtn_MCC.setChecked(True) #PROBAR
                self.ui.TextCCC.setEnabled(True)
            elif Modo == "CV":
                self.ui.Rbtn_MCV.setChecked(True) #PROBAR
                self.ui.TextVCV.setEnabled(True)
            elif Modo == "CP":
                self.ui.Rbtn_MCW.setChecked(True) #PROBAR
                self.ui.TextPCW.setEnabled(True)
            elif Modo == "CR":
                self.ui.Rbtn_MCR.setChecked(True) #PROBAR
                self.ui.TextRCR.setEnabled(True)
            
            #Al conectar se activa el Rbtn según la función
            elif Funcion == "Corto":
                self.ui.Rbtn_Corto.setEnabled(True)
                self.ui.Rbtn_Corto.setChecked(True)
            elif Funcion == "Lista":
                self.ui.Rbtn_Lista.setEnabled(True)
                self.ui.Rbtn_Lista.setChecked(True)
            elif Funcion == "Bateria":
                self.ui.Rbtn_Bateria.setEnabled(True)
                self.ui.Rbtn_Bateria.setChecked(True)   
            
            #Cuando se comunica muestra valores límite de voltaje, corriente y potencia
            self.LimV = Leer_Max_Valorpermitido(self.comunicacion, 0x23)
            self.LimC = Leer_Max_Valorpermitido(self.comunicacion, 0x25)
            self.LimP = Leer_Max_Valorpermitido(self.comunicacion, 0x27)
            self.ui.TextLimV.setText(str(self.LimV))
            self.ui.TextLimC.setText(str(self.LimC))
            self.ui.TextLimP.setText(str(self.LimP))
            
            #Cuando se comunica muestra valores configurados de voltaje, corriente, potencia y resistencia
            self.ui.TextCCC.setText(str(Leer_VCPR(self.comunicacion, 0x2B)))
            self.ui.TextVCV.setText(str(Leer_VCPR(self.comunicacion, 0x2D)))
            self.ui.TextPCW.setText(str(Leer_VCPR(self.comunicacion, 0x2F)))
            self.ui.TextRCR.setText(str(Leer_VCPR(self.comunicacion, 0x31)))
            
            #Cuando se comunica muestra la información y los rangos máximos de la carga
            self.ip = Informacion_producto(self.comunicacion)
            self.ui.LblModelo.setText(self.ip)
            self.Modelo_datos = {
                "8500": {"P": 300, "V": 120, "C": 30},
                "8502": {"P": 300, "V": 500, "C": 15},
                "8510": {"P": 600, "V": 120, "C": 120},
                "8512": {"P": 600, "V": 500, "C": 30},
                "8514": {"P": 1200, "V": 120, "C": 240},
                "8518": {"P": 1200, "V": 60, "C":240},
                "8520": {"P": 2400, "V": 120, "C": 240},
                "8522": {"P": 2400, "V": 500, "C": 120},
                "8524": {"P": 5000, "V": 60, "C": 240},
                "8526": {"P": 5000, "V": 500, "C": 120},
            }
            self.ui.LblRangoP.setText(str(self.Modelo_datos[self.ip]["P"]))
            self.ui.LblRangoV.setText(str(self.Modelo_datos[self.ip]["V"]))
            self.ui.LblRangoC.setText(str(self.Modelo_datos[self.ip]["C"]))
            self.ui.label_17.show()
            self.ui.label_18.show()
            self.ui.label_19.show()    

            # ruta,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Guardar archivo','','Archivos CSV (*.csv);; Todos los archvivos (*)')
            # GuardarCSV(ruta)
            
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(True)
            self.ui.BtnConectar.setEnabled(False)
            self.ui.BtnConectar.hide()
            self.ui.BtnDesconectar.show()
            self.ui.LblDesconectado.hide()
            self.ui.LblConectado.show()
            
            #Encender/apagar carga electrónica
            self.ui.BtnApagar.setEnabled(False)
            self.ui.BtnEncender.setEnabled(True)
            self.ui.BtnEncender.show()
            self.ui.BtnApagar.hide()
            self.ui.LblApagado.show()
            self.ui.LblEncendido.hide()
            
            #Configuración del instrumento
            self.ui.BtnEstablecerMax.setEnabled(True)
            self.ui.TextLimV.setEnabled(True)
            self.ui.TextLimC.setEnabled(True)
            self.ui.TextLimP.setEnabled(True)
            
            #Modo de operación
            self.ui.Rbtn_MCC.setEnabled(True)
            self.ui.Rbtn_MCV.setEnabled(True)
            self.ui.Rbtn_MCW.setEnabled(True)
            self.ui.Rbtn_MCR.setEnabled(True)
            
            #Valor según modo de  operación
            self.ui.BtnEstablecerValMod.setEnabled(True)
            
            #Función de trabajo
            self.ui.Rbtn_Corto.setEnabled(True)
            self.ui.Rbtn_Lista.setEnabled(True)
            self.ui.Rbtn_Bateria.setEnabled(True)
            
        except serial.serialutil.SerialTimeoutException:
            self.Ventana_Advertencia("No se pudo conectar, por favor intente nuevamente")
            self.Desconecta()
            #print("No se pudo conectar")
        except TimeoutError:
            self.Ventana_Advertencia("No se obtuvo respuesta de la carga")
            self.Desconecta()
            #print("No se obtuvo respuesta")
            #self.Ventana_advertencia()
        except serial.serialutil.SerialException:
            self.Ventana_Advertencia("No se ha detectado conexión")
            self.Desconecta()
            #self.Ventana_advertencia()
            #print("No se ha detectado conexión")            
    
    #Función para apagar, desconectar y cerrar la comunicación
    def Desconecta(self):
        try:
            Encender_Apagar(self.comunicacion,  0)
            #Cuando se desconecta la carga se activa el control local
            Trigger_source(self.comunicacion, 0)
            Selec_Funcion(self.comunicacion, 0)
            Control_remoto_local(self.comunicacion, 0)
            
            #Al desconectar la carga se ponen vacíos los campos de lectura
            self.ui.LblModoOP.setText('')
            self.ui.LblFuncion.setText('')
            self.ui.LblModelo.setText('')
            self.ui.LblRangoP.setText('')
            self.ui.LblRangoV.setText('')
            self.ui.LblRangoC.setText('')
            self.ui.label_17.hide()
            self.ui.label_18.hide()
            self.ui.label_19.hide()
            self.ui.TextLimV.setText(str(""))
            self.ui.TextLimC.setText(str(""))
            self.ui.TextLimP.setText(str(""))
            self.ui.TextCCC.setText(str(""))
            self.ui.TextVCV.setText(str(""))
            self.ui.TextPCW.setText(str(""))
            self.ui.TextRCR.setText(str(""))
            self.ui.Txt_LeeVolt.setText(str(""))
            self.ui.Txt_LeeCorr.setText(str(""))
            self.ui.Txt_LeePot.setText(str(""))
            self.ui.Lbl_CapAh.setText('')
            self.ui.Lbl_CapWh.setText('')
            self.ui.TextCCC_Bat.setText(str(""))
            self.ui.TextVoltmin_PBateria.setText(str(""))
            self.ui.Txt_Val_min.setText(str(""))
            self.ui.Txt_Val_max.setText(str(""))
            self.ui.Txt_NumPasos.setText(str(""))
            self.ui.Txt_Val_tiempo.setText(str(""))
            
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            
            #Encender/apagar carga electrónica
            self.ui.BtnApagar.setEnabled(False)
            self.ui.BtnEncender.setEnabled(False)
            self.ui.BtnEncender.show()
            self.ui.BtnApagar.hide()
            self.ui.LblApagado.show()
            self.ui.LblEncendido.hide()
            
            #Configuración del instrumento
            self.ui.BtnEstablecerMax.setEnabled(False)
            self.ui.TextLimV.setEnabled(False)
            self.ui.TextLimC.setEnabled(False)
            self.ui.TextLimP.setEnabled(False)
            
            #Modo de operación
            self.ui.Rbtn_MCC.setEnabled(False)
            self.ui.Rbtn_MCV.setEnabled(False)
            self.ui.Rbtn_MCW.setEnabled(False)
            self.ui.Rbtn_MCR.setEnabled(False)
            
            #Valor según modo de  operación
            self.ui.BtnEstablecerValMod.setEnabled(False)
            self.ui.TextVCV.setEnabled(False)
            self.ui.TextCCC.setEnabled(False)
            self.ui.TextPCW.setEnabled(False)
            self.ui.TextRCR.setEnabled(False)
            
            #Función de trabajo
            self.ui.Rbtn_Corto.setEnabled(False)
            self.ui.Rbtn_Lista.setEnabled(False)
            self.ui.Rbtn_Bateria.setEnabled(False)
            
            #Prueba de baterías
            self.ui.BtnIniciar_PBateria.setEnabled(False)
            self.ui.BtnParar_PBateria.setEnabled(False)
            self.ui.TextCCC_Bat.setEnabled(False)
            self.ui.TextVoltmin_PBateria.setEnabled(False)
            
            #Simulación de corto
            self.ui.BtnIniciar_Corto.setEnabled(False)
            self.ui.BtnParar_Corto.setEnabled(False)
            self.ui.Cmb_ModoCorto.setEnabled(False)
            
            #Operación de lista
            self.ui.Rbtn_Unavez.setEnabled(False)
            self.ui.Rbtn_Repetir.setEnabled(False)
            self.ui.Cmb_ModoLista.setEnabled(False)
            self.ui.BtnEstablecer_OpLista.setEnabled(False)
            self.ui.BtnIniciar_Lista.setEnabled(False)
            self.ui.BtnParar_Lista.setEnabled(False)
            self.ui.Txt_Val_min.setEnabled(False)
            self.ui.Txt_NumPasos.setEnabled(False)
            self.ui.Txt_Val_max.setEnabled(False)
            self.ui.Txt_Val_tiempo.setEnabled(False)
            
            self.comunicacion.close()
        
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
        
    #Función para encender la carga
    def Enciende(self):
        try:
            Encender_Apagar(self.comunicacion, 1)                
            
            self.Tinicial = time.time()
            
            self.timer.timeout.connect(self.ActualizaVCP)
            self.timer.start(10)
            
            #Modo de operación
            self.ui.Rbtn_MCC.setEnabled(False)
            self.ui.Rbtn_MCV.setEnabled(False)
            self.ui.Rbtn_MCW.setEnabled(False)
            self.ui.Rbtn_MCR.setEnabled(False)
            
            #Encender/apagar carga electrónica
            self.ui.BtnApagar.setEnabled(True)
            self.ui.BtnEncender.setEnabled(False)
            self.ui.BtnEncender.hide()
            self.ui.BtnApagar.show()
            self.ui.LblApagado.hide()
            self.ui.LblEncendido.show()
            
            #Función de trabajo
            self.ui.Rbtn_Corto.setEnabled(False)
            self.ui.Rbtn_Lista.setEnabled(False)
            self.ui.Rbtn_Bateria.setEnabled(False)
            
            self.Encendido = True
            
        except ValueError:
            self.Ventana_Advertencia("No se pudo encender la carga, por favor intente nuevamente")
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
        
    def ActualizaVCP(self):
        try:
            T0 = time.time()
            #global cnt #Para pruebas sin la carga
            #self.ui.Txt_LeeVolt.setText(str(cnt)) #Para pruebas sin la carga
            #cnt += 1 #Para pruebas sin la carga
            
            V, C, P = Leer_VCP_Display(self.comunicacion)
            self.ui.Txt_LeeVolt.setText(str(V))
            self.ui.Txt_LeeCorr.setText(str(C))
            self.ui.Txt_LeePot.setText(str(P))
            
            #Para graficar Voltaje y Corriente
            # self.T.append(time.time()-self.Tinicial)
            # self.V.append(V)
            # self.C.append(C)
            
            # #axes.set_title("My Plot")
            # # x = np.linspace(1, 10)
            # # y = np.linspace(1, 10)
            # # y1 = np.linspace(50, 41)
            # self.Voltaje_Plot.clear()
            # self.Corriente_Plot.clear()
            # # from random import randint
            # # self.V.append(randint(20, 100))
            # # self.C.append(randint(1,10))
            # if len(self.V) > 20:
            #     self.T.pop(0)
            #     self.V.pop(0)
            #     self.C.pop(0)
            # self.Voltaje_Plot.plot(self.T[-20:], self.V[-20:], "g", label="Voltaje")
            # self.Corriente_Plot.plot(self.T[-20:], self.C[-20:], "y", label="Corriente")
            # self.canvas.draw()
            
            # # Voltaje_Plot.legend()
            # # Corriente_Plot.legend()
            # self.Voltaje_Plot.grid(True)
            # self.Corriente_Plot.grid(True)
            
            T1 = time.time()
            TTotal = T1-T0
            
            if self.Bateriaflag==True:
                TBateria = T1 - self.Tb1
                
                self.CapacidadAh = self.CapacidadAh + TBateria*C
                self.ui.Lbl_CapAh.setText(str(self.CapacidadAh))
                self.CapacidadWh = self.CapacidadWh + TBateria*P
                self.ui.Lbl_CapWh.setText(str(self.CapacidadWh))
                self.ui.Lbl_Ah.setText(str(self.CapacidadAh))
                self.ui.Lbl_Wh.setText(str(self.CapacidadWh))
                self.Tb1 = T1
        
            # print("Tiempo transcurrido en 1 paso: ")
            # print(TTotal)
            
            self.timer.start(10)
        
        except ValueError:
            self.Ventana_Advertencia("Por favor espere un momento")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")

    def Apaga(self):
        try:
            #Se pone el control del trigger desde el panel frontal
            #Se apaga la carga
            Encender_Apagar(self.comunicacion, 0)
            #Selec_Funcion(self.comunicacion, 0)
            #Se pone en la función de fijo
            #Selec_Funcion(self.comunicacion, 0)
            
            #Encender/apagar carga electrónica
            self.ui.BtnApagar.setEnabled(False)
            self.ui.BtnEncender.setEnabled(True)
            self.ui.BtnEncender.show()
            self.ui.BtnApagar.hide()
            self.ui.LblApagado.show()
            self.ui.LblEncendido.hide()
            
            #Modo de operación
            self.ui.Rbtn_MCC.setEnabled(True)
            self.ui.Rbtn_MCV.setEnabled(True)
            self.ui.Rbtn_MCW.setEnabled(True)
            self.ui.Rbtn_MCR.setEnabled(True)
            
            # #Prueba de baterías
            # self.ui.BtnIniciar_PBateria.setEnabled(False)
            # self.ui.BtnParar_PBateria.setEnabled(False)
            # self.ui.TextCCC_Bat.setEnabled(False)
            # self.ui.TextVoltmin_PBateria.setEnabled(False)
            
            # #Simulación de corto
            # self.ui.BtnIniciar_Corto.setEnabled(False)
            # self.ui.BtnParar_Corto.setEnabled(False)
            # self.ui.Cmb_ModoCorto.setEnabled(False)
            
            # #Operación de lista
            # self.ui.Rbtn_Unavez.setChecked(False)
            # self.ui.Rbtn_Repetir.setChecked(False)
            # self.ui.Cmb_ModoLista.setEnabled(False)
            # self.ui.BtnEstablecer_OpLista.setEnabled(False)
            # self.ui.BtnIniciar_Lista.setEnabled(False)
            # self.ui.BtnParar_Lista.setEnabled(False)
            # self.ui.Txt_Val_min.setEnabled(False)
            # self.ui.Txt_NumPasos.setEnabled(False)
            # self.ui.Txt_Val_max.setEnabled(False)
            # self.ui.Txt_Val_tiempo.setEnabled(False)
            
            #Función de trabajo
            self.ui.Rbtn_Corto.setEnabled(True)
            self.ui.Rbtn_Lista.setEnabled(True)
            self.ui.Rbtn_Bateria.setEnabled(True)
            
            self.timer.stop()
            
            self.Encendido = False
        
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
        
    #Función que captura el valor ingresado en los límites  de C, V y p en la configuración
    def Limites(self):
        try:
            self.LimV = float(self.ui.TextLimV.text())
            self.LimC = float(self.ui.TextLimC.text())
            self.LimP = float(self.ui.TextLimP.text())
            
            if (self.LimV > self.Modelo_datos[self.ip]["V"] or
            self.LimC > self.Modelo_datos[self.ip]["C"] or
            self.LimP > self.Modelo_datos[self.ip]["P"]):
                raise ValueError
            
            Poner_Max_Valorpermitido(self.comunicacion, 0x22, self.LimV)
            Poner_Max_Valorpermitido(self.comunicacion, 0x24, self.LimC)
            Poner_Max_Valorpermitido(self.comunicacion, 0x26, self.LimP)
        # except serial.serialutil.SerialException:
        #     #Comunicación serial
        #     self.ui.BtnDesconectar.setEnabled(False)
        #     self.ui.BtnConectar.setEnabled(True)
        #     self.ui.BtnConectar.show()
        #     self.ui.BtnDesconectar.hide()
        #     self.ui.LblDesconectado.show()
        #     self.ui.LblConectado.hide()
        #     print("No se ha detectado conexión")
        except AttributeError:
            self.Ventana_Advertencia("No se ha establecido comunicación")
        except ValueError:
            self.Ventana_Advertencia("Por favor verifique los valores máximos en la información")
        
    def Seleccion_ModoOP (self):
        try:
            self.radioBtn = self.sender()
            if self.radioBtn.isChecked():
                
                if self.radioBtn.text() == 'CC':
                    Modo_operacion(self.comunicacion,0)
                    self.ui.TextCCC.setEnabled(True)
                    self.ui.Rbtn_MCC.setChecked(True)
                    self.ui.TextVCV.setEnabled(False)
                    self.ui.Rbtn_MCV.setChecked(False)
                    self.ui.TextPCW.setEnabled(False)
                    self.ui.Rbtn_MCW.setChecked(False)
                    self.ui.TextRCR.setEnabled(False)
                    self.ui.Rbtn_MCR.setChecked(False)
                elif self.radioBtn.text() == 'CV':
                    Modo_operacion(self.comunicacion,1)
                    self.ui.TextCCC.setEnabled(False)
                    self.ui.Rbtn_MCC.setChecked(False)
                    self.ui.TextVCV.setEnabled(True)
                    self.ui.Rbtn_MCV.setChecked(True)
                    self.ui.TextPCW.setEnabled(False)
                    self.ui.Rbtn_MCW.setChecked(False)
                    self.ui.TextRCR.setEnabled(False)
                    self.ui.Rbtn_MCR.setChecked(False)
                elif self.radioBtn.text() == 'CW':
                    Modo_operacion(self.comunicacion,2)
                    self.ui.TextCCC.setEnabled(False)
                    self.ui.Rbtn_MCC.setChecked(False)
                    self.ui.TextVCV.setEnabled(False)
                    self.ui.Rbtn_MCV.setChecked(False)
                    self.ui.TextPCW.setEnabled(True)
                    self.ui.Rbtn_MCW.setChecked(True)
                    self.ui.TextRCR.setEnabled(False)
                    self.ui.Rbtn_MCR.setChecked(False)
                elif self.radioBtn.text() == 'CR':
                    Modo_operacion(self.comunicacion,3)
                    self.ui.TextCCC.setEnabled(False)
                    self.ui.Rbtn_MCC.setChecked(False)
                    self.ui.TextVCV.setEnabled(False)
                    self.ui.Rbtn_MCV.setChecked(False)
                    self.ui.TextPCW.setEnabled(False)
                    self.ui.Rbtn_MCW.setChecked(False)
                    self.ui.TextRCR.setEnabled(True)
                    self.ui.Rbtn_MCR.setChecked(True)
            self.ui.LblModoOP.setText(Leer_Modo_operacion(self.comunicacion))
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
        
    def Poner_valores_ModoOP(self):
        try:
            Modo = Leer_Modo_operacion(self.comunicacion)
            
            if  Modo == "CC":
                C_CC = float(self.ui.TextCCC.text())
                if C_CC > self.LimC:
                    raise ValueError
                Poner_VCPR(self.comunicacion, 0x2A, C_CC)
            elif Modo == "CV":
                V_CV = float(self.ui.TextVCV.text())
                if 0.1 > V_CV or V_CV > self.LimV:
                    raise ValueError
                Poner_VCPR(self.comunicacion, 0x2C, V_CV)
            elif Modo == "CW":
                P_CW = float(self.ui.TextPCW.text()) 
                if P_CW > self.LimP:
                    raise ValueError
                Poner_VCPR(self.comunicacion, 0x2E, P_CW)
            elif Modo == "CR":
                R_CR = float(self.ui.TextRCR.text()) 
                if R_CR < 0.1:
                    raise ValueError
                Poner_VCPR(self.comunicacion, 0x30, R_CR)
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except ValueError:
            self.Ventana_Advertencia("Por favor verifique los límites en la configuración del instrumento, en el caso de el modo CV y CR el límite inferior debe ser mayor o igual a 0.1")
            
    def Seleccion_Funcion (self):
        try:
            Func = Leer_Funcion(self.comunicacion)
            
            if Func == "Fijo":
                self.ui.LblFuncion.setText(Func)
                #Botones y textos de función prueba batería
                self.ui.BtnIniciar_PBateria.setEnabled(False)
                self.ui.BtnParar_PBateria.setEnabled(False)
                self.ui.TextCCC_Bat.setEnabled(False)
                self.ui.TextVoltmin_PBateria.setEnabled(False)
                
                #Botones y textos de función lista
                self.ui.Cmb_ModoLista.setEnabled(False)
                self.ui.Rbtn_Unavez.setEnabled(False)
                self.ui.Rbtn_Repetir.setEnabled(False)
                self.ui.Txt_Val_min.setEnabled(False)
                self.ui.Txt_NumPasos.setEnabled(False)
                self.ui.Txt_Val_max.setEnabled(False)
                self.ui.Txt_Val_tiempo.setEnabled(False)
                self.ui.BtnEstablecer_OpLista.setEnabled(False)
                self.ui.BtnIniciar_Lista.setEnabled(False)
                self.ui.BtnParar_Lista.setEnabled(False)
                
                #Botones y textos de función corto
                self.ui.Cmb_ModoCorto.setEnabled(False)
                self.ui.BtnIniciar_Corto.setEnabled(False)
                self.ui.BtnParar_Corto.setEnabled(False)
            
            self.radioBtn = self.sender() 
            if self.radioBtn.isChecked():         
                    
                if self.radioBtn.text() == 'Lista':
                    Selec_Funcion(self.comunicacion, 3)
                    self.ui.LblFuncion.setText("Lista")
                    
                    #Botones y textos de función prueba batería
                    self.ui.BtnIniciar_PBateria.setEnabled(False)
                    self.ui.BtnParar_PBateria.setEnabled(False)
                    self.ui.TextCCC_Bat.setEnabled(False)
                    self.ui.TextVoltmin_PBateria.setEnabled(False)
                    
                    #Botones y textos de función lista
                    self.ui.Cmb_ModoLista.setEnabled(True)
                    self.ui.Rbtn_Unavez.setEnabled(True)
                    self.ui.Rbtn_Repetir.setEnabled(True)
                    self.ui.Txt_Val_min.setEnabled(True)
                    self.ui.Txt_NumPasos.setEnabled(True)
                    self.ui.Txt_Val_max.setEnabled(True)
                    self.ui.Txt_Val_tiempo.setEnabled(True)
                    self.ui.BtnEstablecer_OpLista.setEnabled(True)
                    self.ui.BtnIniciar_Lista.setEnabled(True)
                    self.ui.BtnParar_Lista.setEnabled(True)
                    
                    #Botones y textos de función corto
                    self.ui.Cmb_ModoCorto.setEnabled(False)
                    self.ui.BtnIniciar_Corto.setEnabled(False)
                    self.ui.BtnParar_Corto.setEnabled(False)
                    
                elif self.radioBtn.text() == 'Simulación de corto':
                    #Botones y textos de función prueba batería
                    self.ui.LblFuncion.setText("Corto")
                    self.ui.BtnIniciar_PBateria.setEnabled(False)
                    self.ui.BtnParar_PBateria.setEnabled(False)
                    self.ui.TextCCC_Bat.setEnabled(False)
                    self.ui.TextVoltmin_PBateria.setEnabled(False)
                    
                    #Botones y textos de función lista
                    self.ui.Cmb_ModoLista.setEnabled(False)
                    self.ui.Rbtn_Unavez.setEnabled(False)
                    self.ui.Rbtn_Repetir.setEnabled(False)
                    self.ui.Txt_Val_min.setEnabled(False)
                    self.ui.Txt_NumPasos.setEnabled(False)
                    self.ui.Txt_Val_max.setEnabled(False)
                    self.ui.Txt_Val_tiempo.setEnabled(False)
                    self.ui.BtnEstablecer_OpLista.setEnabled(False)
                    self.ui.BtnIniciar_Lista.setEnabled(False)
                    self.ui.BtnParar_Lista.setEnabled(False)
                    
                    #Botones y textos de función corto
                    self.ui.Cmb_ModoCorto.setEnabled(True)
                    self.ui.BtnIniciar_Corto.setEnabled(True) 
                    
                elif self.radioBtn.text() == 'Prueba de batería':
                    self.ui.LblFuncion.setText("Batería")                  
                    #Botones y textos de función prueba batería
                    self.ui.BtnIniciar_PBateria.setEnabled(True)
                    self.ui.BtnParar_PBateria.setEnabled(True)
                    self.ui.TextCCC_Bat.setEnabled(True)
                    self.ui.TextVoltmin_PBateria.setEnabled(True)
                    
                    #Botones y textos de función lista
                    self.ui.Cmb_ModoLista.setEnabled(False)
                    self.ui.Rbtn_Unavez.setEnabled(False)
                    self.ui.Rbtn_Repetir.setEnabled(False)
                    self.ui.Txt_Val_min.setEnabled(False)
                    self.ui.Txt_NumPasos.setEnabled(False)
                    self.ui.Txt_Val_max.setEnabled(False)
                    self.ui.Txt_Val_tiempo.setEnabled(False)
                    self.ui.BtnEstablecer_OpLista.setEnabled(False)
                    self.ui.BtnIniciar_Lista.setEnabled(False)
                    self.ui.BtnParar_Lista.setEnabled(False)
                    
                    #Botones y textos de función corto
                    self.ui.Cmb_ModoCorto.setEnabled(False)
                    self.ui.BtnIniciar_Corto.setEnabled(False)
                    self.ui.BtnParar_Corto.setEnabled(False)
            
            # elif Func == "Corto":
            #     self.ui.LblFuncion.setText(Func)
            #     #Botones y textos de función prueba batería
            #     self.ui.BtnIniciar_PBateria.setEnabled(False)
            #     self.ui.BtnParar_PBateria.setEnabled(False)
            #     self.ui.TextCCC_Bat.setEnabled(False)
            #     self.ui.TextVoltmin_PBateria.setEnabled(False)
                
            #     #Botones y textos de función lista
            #     self.ui.Cmb_ModoLista.setEnabled(False)
            #     self.ui.Rbtn_Unavez.setEnabled(False)
            #     self.ui.Rbtn_Repetir.setEnabled(False)
            #     self.ui.Txt_Val_min.setEnabled(False)
            #     self.ui.Txt_NumPasos.setEnabled(False)
            #     self.ui.Txt_Val_max.setEnabled(False)
            #     self.ui.Txt_Val_tiempo.setEnabled(False)
            #     self.ui.BtnEstablecer_OpLista.setEnabled(False)
            #     self.ui.BtnIniciar_Lista.setEnabled(False)
            #     self.ui.BtnParar_Lista.setEnabled(False)
                
            #     #Botones y textos de función corto
            #     self.ui.Cmb_ModoCorto.setEnabled(True)
            #     self.ui.BtnIniciar_Corto.setEnabled(True)
                
            # elif Func == "Lista":
            #     self.ui.LblFuncion.setText(Func)
            #     #Botones y textos de función prueba batería
            #     self.ui.BtnIniciar_PBateria.setEnabled(False)
            #     self.ui.BtnParar_PBateria.setEnabled(False)
            #     self.ui.TextCCC_Bat.setEnabled(False)
            #     self.ui.TextVoltmin_PBateria.setEnabled(False)
                
            #     #Botones y textos de función lista
            #     self.ui.Cmb_ModoLista.setEnabled(True)
            #     self.ui.Rbtn_Unavez.setEnabled(True)
            #     self.ui.Rbtn_Repetir.setEnabled(True)
            #     self.ui.Txt_Val_min.setEnabled(True)
            #     self.ui.Txt_NumPasos.setEnabled(True)
            #     self.ui.Txt_Val_max.setEnabled(True)
            #     self.ui.Txt_Val_tiempo.setEnabled(True)
            #     self.ui.BtnEstablecer_OpLista.setEnabled(True)
            #     self.ui.BtnIniciar_Lista.setEnabled(True)
            #     self.ui.BtnParar_Lista.setEnabled(True)
                
            #     #Botones y textos de función corto
            #     self.ui.Cmb_ModoCorto.setEnabled(False)
            #     self.ui.BtnIniciar_Corto.setEnabled(False)
            #     self.ui.BtnParar_Corto.setEnabled(False)
            
            # elif Func == "Bateria":
            #     self.ui.LblFuncion.setText(Func)
            #     #Botones y textos de función prueba batería
            #     self.ui.BtnIniciar_PBateria.setEnabled(True)
            #     self.ui.BtnParar_PBateria.setEnabled(True)
            #     self.ui.TextCCC_Bat.setEnabled(True)
            #     self.ui.TextVoltmin_PBateria.setEnabled(True)
                
            #     #Botones y textos de función lista
            #     self.ui.Cmb_ModoLista.setEnabled(False)
            #     self.ui.Rbtn_Unavez.setEnabled(False)
            #     self.ui.Rbtn_Repetir.setEnabled(False)
            #     self.ui.Txt_Val_min.setEnabled(False)
            #     self.ui.Txt_NumPasos.setEnabled(False)
            #     self.ui.Txt_Val_max.setEnabled(False)
            #     self.ui.Txt_Val_tiempo.setEnabled(False)
            #     self.ui.BtnEstablecer_OpLista.setEnabled(False)
            #     self.ui.BtnIniciar_Lista.setEnabled(False)
            #     self.ui.BtnParar_Lista.setEnabled(False)
                
            #     #Botones y textos de función corto
            #     self.ui.Cmb_ModoCorto.setEnabled(False)
            #     self.ui.BtnIniciar_Corto.setEnabled(False)
            #     self.ui.BtnParar_Corto.setEnabled(False)
                
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")              
    
    def Seleccion_Rep_Lista (self):
        try:
            radioBtn = self.sender()
            if radioBtn.isChecked():
                
                if radioBtn.text() == 'Una vez':
                    Lista_UnaVez_Repetir(self.comunicacion, 0)
                elif radioBtn.text() == 'Repetir':
                    Lista_UnaVez_Repetir(self.comunicacion, 1)
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
    
    def CambioModoOp_Lista(self):
        Lista = self.ui.Cmb_ModoLista.currentText()
        if Lista == "CC":
            self.ui.LblVmin.hide()
            self.ui.LblVmax.hide()
            self.ui.LblCmin.show()
            self.ui.LblCmax.show()
            self.ui.LblPotmin.hide()
            self.ui.LblPotmax.hide()
            self.ui.LblOhmmin.hide()
            self.ui.LblOhmmax.hide()
        elif Lista == "CV":
            self.ui.LblVmin.show()
            self.ui.LblVmax.show()
            self.ui.LblCmin.hide()
            self.ui.LblCmax.hide()
            self.ui.LblPotmin.hide()
            self.ui.LblPotmax.hide()
            self.ui.LblOhmmin.hide()
            self.ui.LblOhmmax.hide()
        elif Lista == "CW":
            self.ui.LblVmin.hide()
            self.ui.LblVmax.hide()
            self.ui.LblCmin.hide()
            self.ui.LblCmax.hide()
            self.ui.LblPotmin.show()
            self.ui.LblPotmax.show()
            self.ui.LblOhmmin.hide()
            self.ui.LblOhmmax.hide()
        elif Lista == "CR":
            self.ui.LblVmin.hide()
            self.ui.LblVmax.hide()
            self.ui.LblCmin.hide()
            self.ui.LblCmax.hide()
            self.ui.LblPotmin.hide()
            self.ui.LblPotmax.hide()
            self.ui.LblOhmmin.show()
            self.ui.LblOhmmax.show()
                           
    def Funcion_Lista(self):
        try:
            T0 = time.time()
            
            Particion_Memoria(self.comunicacion)
            
            #Selección del modo de operación dentro de la función de lista
            Lista = self.ui.Cmb_ModoLista.currentText()
            self.ModoSelecc = Lista
            if Lista == "CC":
                Modo_Lista(self.comunicacion, 0)
                opcion = 0x40
                n = 10000
            elif Lista == "CV":
                Modo_Lista(self.comunicacion, 1)
                opcion = 0x42
                n=1000
            elif Lista == "CW":   
                Modo_Lista(self.comunicacion, 2)
                opcion = 0x44
                n=1000
            elif Lista == "CR":
                Modo_Lista(self.comunicacion, 3)
                opcion = 0x46
                n=1000
            
            # Modo = Leer_Modo_operacion(self.comunicacion)
            # self.ui.LblModoOP.setText(Modo)
            
            self.ui.LblModoOP.setText(Lista)
            # LblMostrarModo = Leer_Modo_operacion(self.comunicacion)
            # self.ui.LblModoOP.setText(LblMostrarModo)
            #Modo = Leer_Modo_Lista(self.comunicacion)
            
            Valmin = float(self.ui.Txt_Val_min.text())
            Valmax = float(self.ui.Txt_Val_max.text())
            Pasos = int(self.ui.Txt_NumPasos.text())
            Poner_Pasos_Lista(self.comunicacion, Pasos)
            Tiempo = float(self.ui.Txt_Val_tiempo.text())
                    
            deltaval = (Valmax-Valmin)/(Pasos-1)
            
            Valactual = Valmin
            for i in range(1,Pasos+1):
                # print("Val actual: ", Valactual)
                Poner_Val_Lista(self.comunicacion, opcion, i, Valactual, Tiempo, n)
                Valactual += deltaval
                
            T1 = time.time()
            #grafica_voltaje = []
            #grafica_voltaje.append((time.time(), v))
            TTotal = T1-T0
            
            Guardar_Lista(self.comunicacion)
            #Selec_Funcion(self.comunicacion, 0)
            
            
            print("Tiempo transcurrido: ")
            print(TTotal)
            
        except TimeoutError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
            
    def Iniciar_Lista(self):
        try:
            Selec_Funcion(self.comunicacion, 0)
            Selec_Funcion(self.comunicacion, 3)
            Trigger_source(self.comunicacion, 2) #Verificar si se puede eliminar de acá
            Llamar_Lista(self.comunicacion)
            self.Enciende()
            #Se llama la lista que está guardada en la memoria de la carga
            #Se pone el control del trigger de forma remota
            #Se enciende el trigger para que se ponga en funcionamiento la función lista
            Encender_Trigger(self.comunicacion)
            #Se enciende la carga
            
            self.ui.BtnParar_Lista.show()
            self.ui.BtnIniciar_Lista.hide()
            self.ui.BtnEstablecer_OpLista.setEnabled(False)      
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión") 
        except TimeoutError:
            self.Ventana_Advertencia("Por favor espere mientras se carga la configuración")
        
    def Parar_Lista(self):
        try:
            # Encender_Trigger(self.comunicacion) #Agregado
            self.Apaga()
            Trigger_source(self.comunicacion, 0)
            self.ui.BtnParar_Lista.hide()
            self.ui.BtnIniciar_Lista.show()
            self.ui.BtnEstablecer_OpLista.setEnabled(True)
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
    
    def Prueba_BateriaON(self):
        try:
            Selec_Funcion(self.comunicacion,4)
            #Se pone el modo de operación en CC
            Modo_operacion(self.comunicacion,0)
            #Se establece el valor corriente desde la interfaz y se manda a la carga
            C_CC = float(self.ui.TextCCC_Bat.text())
            Poner_VCPR(self.comunicacion, 0x2A, C_CC)
            #Selec_Funcion(self.comunicacion, 4) #Se deja por el orden en manual
            #Se establece el valor mínimo de voltaje desde la interfaz y se manda a la carga
            V_min = float(self.ui.TextVoltmin_PBateria.text())
            Poner_Vmin_PBateria(self.comunicacion, V_min)
            
            self.Tb1 = time.time()
            self.Bateriaflag = True
            self.CapacidadAh = 0.0
            self.CapacidadWh = 0.0
            self.Enciende()
            self.ui.BtnParar_PBateria.show()
            self.ui.BtnIniciar_PBateria.hide()
            
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
        
    def Prueba_BateriaOFF(self):
        try:
            Selec_Funcion(self.comunicacion, 4)
            self.Apaga()
            self.ui.BtnParar_PBateria.hide()
            self.ui.BtnIniciar_PBateria.show()
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
        
    def Prueba_Corto(self):
        try:
            #Selección del modo de operación para simular el corto
            Modo = self.ui.Cmb_ModoCorto.currentText()
            self.ModoSelecc = Modo
            if Modo == "CC":
                Modo_operacion(self.comunicacion, 0)
            elif Modo == "CV":
                Modo_operacion(self.comunicacion, 1)
            elif Modo == "CW":
                Modo_operacion(self.comunicacion, 2)
            elif Modo == "CR":
                Modo_operacion(self.comunicacion, 3)
                
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
            
    def Prueba_CortoOn(self):
        try:
            self.Prueba_Corto()
            Selec_Funcion(self.comunicacion, 1)
            self.Enciende()
            self.ui.BtnParar_Corto.setEnabled(True)
            self.ui.BtnIniciar_Corto.setEnabled(False)
            self.ui.BtnParar_Corto.show()
            self.ui.BtnIniciar_Corto.hide()
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
        
    def Prueba_CortoOff(self):
        try:
            Selec_Funcion(self.comunicacion, 1)
            self.Apaga()
            self.ui.BtnParar_Corto.setEnabled(False)
            self.ui.BtnIniciar_Corto.setEnabled(True)
            self.ui.BtnParar_Corto.hide()
            self.ui.BtnIniciar_Corto.show()
            
        except ValueError:
            self.Ventana_Advertencia("Por favor intente nuevamente")
        except serial.serialutil.SerialException:
            #Comunicación serial
            self.ui.BtnDesconectar.setEnabled(False)
            self.ui.BtnConectar.setEnabled(True)
            self.ui.BtnConectar.show()
            self.ui.BtnDesconectar.hide()
            self.ui.LblDesconectado.show()
            self.ui.LblConectado.hide()
            self.Ventana_Advertencia("No se ha detectado conexión")
            
        
if __name__=="__main__":
    mi_aplicacion= QApplication(sys.argv)
    #cnt = 0 #Para pruebas sin la carga
    
    mi_app = Ventana()
    
    #mi_app.show()
    sys.exit(mi_aplicacion.exec_())