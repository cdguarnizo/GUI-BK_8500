def cmd8500(cmd , ser):
    print("Command:", cmd)
    ser.write(cmd)
    resp = ser.read(26)
    print(resp)
    if len(resp) == 0:
        raise TimeoutError("No se pudo leer")
    
    if resp[3] != 0x80:
        raise ValueError("No se pudo encender la carga")
    # print("Lectura: ")
    # print(resp[3])
    # print("Lectura respuesta: ")
    # print(salida)
    #print("Respuesta:", resp)

def csum(thing):
    sum = 0
    for i in range(len(thing)):
        sum+=thing[i]
    return 0xFF&sum

def Encender_Apagar(comunicacion,  opcion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x21
    cmd[3]=opcion
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Control_remoto_local(comunicacion, opcion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x20
    cmd[3]=opcion
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Modo_operacion(comunicacion, opcion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x28
    cmd[3]=opcion
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Leer_Modo_operacion(comunicacion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x29
    cmd[3]=0
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    lectura = comunicacion.read(26)
    
    if lectura[3] == 0:
        Modo = "CC"
    elif lectura[3] == 1:
        Modo = "CV"
    elif lectura[3] == 2:
        Modo = "CW"
    elif lectura[3] == 3:
        Modo = "CR"

    return Modo

def Informacion_producto(comunicacion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x6A
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    lectura = comunicacion.read(26)
    print("Lectura información prod: ")
    print(lectura)
    dato = chr(lectura[3]) + chr(lectura[4]) + chr(lectura[5]) + chr(lectura[6])
    
    print(dato)
    return dato

def Poner_Max_Valorpermitido(comunicacion, opcion, Lim):
    
    if opcion == 0x24:
        n=10000
    else:
        n=1000
    
    dato = '0x{0:08X}'.format(int(Lim*n)) #Se manda 0.1V,W o P, si se envía en mV o 
    #mW se multiplica por 1000, si es en mA se multiplica por 10000
    #dato = [2:4] a[4:6] a[6:8] a[8:10]
    print((dato))
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=opcion
    cmd[3] = int(dato[8:10], 16)
    cmd[4] = int(dato[6:8], 16)
    cmd[5] = int(dato[4:6], 16)
    cmd[6] = int(dato [2:4], 16)
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    escritura = comunicacion.write(26)
    lectura = comunicacion.read(26)
    
def Leer_Max_Valorpermitido(comunicacion, opcion):
    
    if opcion == 0x25:
        n=10000
    else:
        n=1000
    
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=opcion
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    lectura = comunicacion.read(26)
    dato = f'0x{lectura[6]:02x}{lectura[5]:02x}{lectura[4]:02x}{lectura[3]:02x}'
    dato = int(dato, 16)/n
    print(lectura)
    
    if opcion == 0x25:
        print(dato, 'A')
    elif opcion == 0x23:
        print(dato, 'V')
    elif opcion == 0x27:
        print(dato, 'W')

    return dato

def Poner_VCPR(comunicacion, opcion, Valor):
    
    if opcion == 0x2A:
        n=10000
    else:
        n=1000
    
    dato = '0x{0:08X}'.format(int(Valor*n)) #Se manda 0.2A, V o P, como se envía en mV se multiplica por 1000
    #dato = [2:4] a[4:6] a[6:8] a[8:10]
    print((dato))
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=opcion
    cmd[3] = int(dato[8:10], 16)
    cmd[4] = int(dato[6:8], 16)
    cmd[5] = int(dato[4:6], 16)
    cmd[6] = int(dato [2:4], 16)
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    escritura = comunicacion.write(26)
    lectura = comunicacion.read(26)
    
def Leer_VCPR(comunicacion, opcion):
    
    if opcion == 0x2B:
        n=10000
    else:
        n=1000
    
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=opcion
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    lectura = comunicacion.read(26)
    dato = f'0x{lectura[6]:02x}{lectura[5]:02x}{lectura[4]:02x}{lectura[3]:02x}'
    print(dato)
    dato = int(dato, 16)/n
    print("Lectura VCPR: ")
    print(lectura)
    
    if opcion == 0x2B:
        print(dato, 'A')
    elif opcion == 0x2D:
        print(dato, 'V')
    elif opcion == 0x2F:
        print(dato, 'W')
    elif opcion == 0x31:
        print(dato, 'Ω')

    return dato
    
def Modo_Lista(comunicacion, opcion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x3A
    cmd[3]=opcion
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Lista_UnaVez_Repetir(comunicacion, opcion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x3C
    cmd[3]=opcion
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Poner_Pasos_Lista(comunicacion, Pasos):
    dato = '0x{0:08X}'.format(int(Pasos))
    #dato = [2:4] a[4:6] a[6:8] a[8:10]
    print((dato))
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x3E
    cmd[3] = int(dato[8:10], 16)
    cmd[4] = int(dato[6:8], 16)
    #cmd[5] = int(dato[4:6], 16)
    #cmd[6] = int(dato [2:4], 16)
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    escritura = comunicacion.write(26)
    lectura = comunicacion.read(26)
    
#Para actualizar los valores que se muestran en pantalla    
def Leer_VCP_Display(comunicacion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x5F
    #cmd[3]=0x8
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    lectura = comunicacion.read(26)
    print(lectura)
    if len(lectura) == 26:
        datoV = f'0x{lectura[6]:02x}{lectura[5]:02x}{lectura[4]:02x}{lectura[3]:02x}'
        datoV = int(datoV, 16)/1000
        #print(datoV, 'V')
        datoC = f'0x{lectura[10]:02x}{lectura[9]:02x}{lectura[8]:02x}{lectura[7]:02x}'
        datoC = int(datoC, 16)/10000
        #print(lectura)
        #print(datoC, 'C')
        datoP = f'0x{lectura[14]:02x}{lectura[13]:02x}{lectura[12]:02x}{lectura[11]:02x}'
        datoP = int(datoP, 16)/1000
    else:
        datoV, datoC, datoP = Leer_VCP_Display(comunicacion)
    
    # print("lectura VCP: ")
    # print(lectura)
    # print(datoP, 'W')
    return datoV, datoC, datoP

def Poner_Val_Lista(comunicacion, opcion, Paso, Val, Tiempo, n=1000):
    
    if opcion == 0x40:
        n=10000
    else:
        n=1000
    
    Pasohex = '0x{0:08X}'.format(int(Paso))
    Valhex = '0x{0:08X}'.format(int(Val*n))
    Tiempohex = '0x{0:08X}'.format(int(Tiempo*10000))

    #dato = [2:4] a[4:6] a[6:8] a[8:10]
    #print((Valhex))
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=opcion
    
    cmd[3] = int(Pasohex[8:10], 16)
    cmd[4] = int(Pasohex[6:8], 16)
    
    cmd[5] = int(Valhex[8:10], 16)
    cmd[6] = int(Valhex[6:8], 16)
    cmd[7] = int(Valhex[4:6], 16)
    cmd[8] = int(Valhex [2:4], 16)
    
    cmd[9] = int(Tiempohex[8:10], 16)
    cmd[10] = int(Tiempohex[6:8], 16)
    
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    escritura = comunicacion.write(26)
    lectura = comunicacion.read(26)
    
def Leer_Modo_Lista(comunicacion):
    
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x3B
    cmd[3]=0
    cmd[25]=csum(cmd)
    #cmd8500(cmd, comunicacion)
    comunicacion.write(cmd)
    lectura = comunicacion.read(26)
    
    if lectura[3] == 0:
        Modo = "CC"
    elif lectura[3] == 1:
        Modo = "CV"
    elif lectura[3] == 2:
        Modo = "CW"
    elif lectura[3] == 3:
        Modo = "CR"
    print(Modo)
    
    return Modo
    
def Guardar_Lista(comunicacion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x4C
    cmd[3]=1
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Particion_Memoria(comunicacion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x4A
    cmd[3]=1
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Llamar_Lista(comunicacion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x4D
    cmd[3]=1
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Trigger_source(comunicacion, opcion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x58
    cmd[3]=opcion
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Encender_Trigger(comunicacion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x5A
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Selec_Funcion(comunicacion, opcion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x5D
    cmd[3]=opcion
    cmd[25]=csum(cmd)
    cmd8500(cmd, comunicacion)
    
def Leer_Funcion(comunicacion):
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x5E
    cmd[3]=0
    cmd[25]=csum(cmd)
    #cmd8500(cmd, comunicacion)
    comunicacion.write(cmd)
    lectura = comunicacion.read(26)
    
    if lectura[3] == 0:
        Modo = "Fijo"
    elif lectura[3] == 1:
        Modo = "Corto"
    elif lectura[3] == 3:
        Modo = "Lista"
    elif lectura[3] == 4:
        Modo = "Bateria"
    print(Modo)
    
    return Modo
    
def Poner_Vmin_PBateria(comunicacion, Voltaje):
    dato = '0x{0:08X}'.format(int(Voltaje*1000))
    #dato = [2:4] a[4:6] a[6:8] a[8:10]
    print((dato))
    cmd=[0]*26
    cmd[0]=0xAA
    cmd[2]=0x4E
    cmd[3] = int(dato[8:10], 16)
    cmd[4] = int(dato[6:8], 16)
    cmd[25]=csum(cmd)
    comunicacion.write(cmd)
    escritura = comunicacion.write(26)
    lectura = comunicacion.read(26)