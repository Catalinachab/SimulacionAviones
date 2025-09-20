
class Avion:
    def __init__(self,id ,velocidad:float, distancia:float, franja:int, t:float, m_atterizaje:float,congestion:bool, aterrizo:bool, tiempo_viajado:float):
        self.id=id
        self.velocidad= velocidad
        self.distancia= distancia
        self.franja_temporal = franja
        self.tiempoAep=t
        self.m_atterizaje=m_atterizaje
        self.congestion=congestion
        self.aterrizo = aterrizo
        self.tiempo_viajado = tiempo_viajado

    def get_velocidad(self):
        return self.velocidad
    
    def get_distancia(self):
        return self.distancia
    
    def get_franja(self):
        return self.franja_temporal
    
    def get_tiempo_viajado(self):
        return self.tiempo_viajado
    
    def get_aterrizo(self):
        return self.aterrizo
    
    def set_tiempo_viajado(self, tiempo:float):
        self.tiempo_viajado = tiempo
        return
    def set_aterrizo(self, aterrizo:bool):
        self.aterrizo = aterrizo
        return
    
    def set_velocidad(self, vel:float):
        self.velocidad = vel 
        return

    def set_distancia(self, dist:float):
        self.distancia=dist
        return
    def set_congestion(self, congestion:bool):
        self.congestion=congestion
        return
    def get_congestion(self):
        return self.congestion
    
    def __lt__(self, other):
        return self.distancia < other.distancia
    
    def actualizar(self):
        avance = self.velocidad * 1/60
        self.distancia = max(0,self.distancia - avance)

        if self.distancia  >= (100*1.852):
            self.franja_temporal = 5
        elif self.distancia < (100*1.852) and self.distancia >= (50*1.852):
             self.franja_temporal = 4
        elif self.distancia < (50*1.852) and self.distancia >= (15*1.852):
             self.franja_temporal = 3
        elif self.distancia < (15*1.852) and self.distancia >= (5*1.852):
             self.franja_temporal = 2
        elif self.distancia < (5*1.852): 
             self.franja_temporal = 1

    def actualizar_velocidad(self):
        if self.franja_temporal  == 4:
            self.set_velocidad(300*1.852)
        if self.franja_temporal  == 3:
            self.set_velocidad(250*1.852)
        elif self.franja_temporal  == 2:
            self.set_velocidad(200*1.852)
        elif self.franja_temporal  == 1:
            self.set_velocidad(150*1.852)
     
    
    def set_tiempoAep(self, t: float):
        self.tiempoAep = t

    def get_tiempoAep(self):
        return self.tiempoAep
    
    def get_aterrizaje(self):
        return self.m_atterizaje
    
    def set_aterrizaje(self, m:float):
        self.m_atterizaje = m
    

def calcular_tiempo_aep(avion):
    tiempos_franjas=[(5/150)*60, (10/200)*60, (35/250)*60,(50/300)*60]
    franjas=[0,5,15,50,100]
    tiempo=0
    for i in range(avion.get_franja()):
        if i+1 == avion.get_franja():
            print("velocidad del avion",avion.id , "velocidad: ",avion.get_velocidad())
            tiempo += (((avion.get_distancia()-franjas[i])/avion.get_velocidad())*60)
        
        else:
            tiempo+=tiempos_franjas[i]
    
    avion.set_tiempoAep(tiempo)
    return tiempo
       
def calcular_dist_entre_aviones(lista):
    distancias=[]
    deben_ser_reubicados=[]
    for elem in range(len(lista)):
       if elem ==0: # primer avion
            distancias.append(calcular_tiempo_aep(lista[elem]))

       else:
            distancias.append(calcular_tiempo_aep(lista[elem]))
            if (abs(lista[elem-1].get_tiempoAep() - lista[elem].get_tiempoAep()))<4:
                deben_ser_reubicados.append(elem)
             
    return distancias, deben_ser_reubicados   

def debajo_minimo_de_franja(avion):
    f=avion.get_franja()
    v=avion.get_velocidad()
    ret=False
    if f==1 and v<120*1.852:
        ret=True
    elif f==2 and v<150*1.852:
        ret=True
    elif f==3 and v<200*1.852:
        ret=True
    elif f==4 and v<250*1.852:
        ret = True
    return ret

def minimo_de_franja(avion):
    f=avion.get_franja()
    ret=0
    if f==1:
        ret=120*1.852
    elif f==2:
        ret=150*1.852
    elif f==3:
        ret=200*1.852
    elif f==4:
        ret = 250*1.852
    elif f ==5:
        ret=500*1.852
    return ret

def marcar_congestion(av, ids_congestionados: set) -> bool:
    """
    Si el avión nunca había tenido congestión, lo marca (flag histórico)
    y devuelve True. Si ya estaba marcado, devuelve False.
    """
    if not av.get_congestion():
        av.set_congestion(True)        # flag histórico en el objeto
        ids_congestionados.add(av.id)  # set para deduplicar por simulación
        return True
    return False

franjas_y_vel_maxima={1:150*1.852, 2:200*1.852,3:250*1.852,4:300*1.852,5:500*1.852}

def reubicar(fila_aviones, deben_ser_reubicados, ids_congestionados):
    """
    Aplica reubicación y devuelve la cantidad de aviones que
    quedaron marcados en congestión por PRIMERA VEZ en este minuto.
    """
    aviones_que_se_eliminan=[]

    for i in deben_ser_reubicados:
        fila_aviones[i].set_velocidad((fila_aviones[i].get_velocidad() - 20*1.852))
        # Si cae por debajo del mínimo ⇒ retroceso
        if(debajo_minimo_de_franja(fila_aviones[i])):
            fila_aviones[i].set_velocidad(-200*1.852)
        else:
            # BAJA por congestión: -20 kt ⇒ marca 1 sola vez
            if fila_aviones[i].get_velocidad() >= 0 and not fila_aviones[i].get_congestion():
                fila_aviones[i].set_congestion(True)
                ids_congestionados.add(fila_aviones[i].id) 
            
                                                
        if not (i==0 or i==len(fila_aviones)-1): 
            if((fila_aviones[i+1].get_tiempoAep()-fila_aviones[i].get_tiempoAep())>5 and fila_aviones[i].get_tiempoAep()-fila_aviones[i-1].get_tiempoAep()>5):
                vel_max_de_franja=franjas_y_vel_maxima[fila_aviones[i].get_franja()]
                fila_aviones[i].set_velocidad(vel_max_de_franja)
        elif i==len(fila_aviones)-1: 
            if( fila_aviones[i].get_tiempoAep()-fila_aviones[i-1].get_tiempoAep()>5):
                vel_max_de_franja=franjas_y_vel_maxima[fila_aviones[i].get_franja()]
                fila_aviones[i].set_velocidad(vel_max_de_franja)

        if(fila_aviones[i].get_distancia() > 100*1.852): #va a montevideo
            aviones_que_se_eliminan.append(fila_aviones[i])
    
    for av in aviones_que_se_eliminan:
        if av in fila_aviones:
            fila_aviones.remove(av)
            
    return 