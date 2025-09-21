from typing import *
from tools_visualizacion import *
import random
import pygame
import numpy as np
import json
from pathlib import Path
import sys
from claseAvion import *

#visualizacion
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AEP – Simulación + Visualización")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 16)

# ========================
# PARÁMETROS DE SIMULACIÓN
# ========================
rangoSim= 50000
rangoHorario = 18
lambda_ = 1/60

for simulacion in range(rangoSim):  
    id=1
    fila_aviones: List[Avion] = []
    acc_time = 0
    cant_detectados=0
    fueron_a_montevideo=0
    ids_congestionados = set()   # guardamos todos los que ALGUNA VEZ bajaron vel (AEP o MVD)
    prev_cong_size = 0
    acum_atraso=0
    for m in range(round(rangoHorario/(1/60))):
        # 1) actualizar todos
        llegados=[]
        for avion in fila_aviones:
            avion.actualizar()
            if avion.get_tiempoAep()==0 or avion.get_distancia()<=0:
                avion.set_aterrizo(True)
                acum_atraso+=max(0,avion.get_tiempo_viajado()-23.4)
                llegados.append(avion)
                cant_arribados+=1
        
        for avion in llegados: 
            fila_aviones.remove(avion)

        fila_aviones.sort()

        # 2) posible nuevo avión
        nuevo_detectado = np.random.binomial(1, lambda_) 
        if nuevo_detectado==1:
            a = Avion(id, 300*1.852, 100*1.852, 4, 23.4, None, False, False, 0.0)
            id+=1
            fila_aviones.append(a)
            fila_aviones.sort()
            cant_detectados+=1   

        # 3) reubicar si hace falta
        distancias, deben_ser_reubicados = calcular_dist_entre_aviones(fila_aviones) 
        pre_montevideo=len(fila_aviones)
        reubicar(fila_aviones, deben_ser_reubicados, ids_congestionados)
        fueron_a_montevideo += (pre_montevideo-len(fila_aviones))
        
        for idx, avion in enumerate(fila_aviones):
            avion.set_tiempo_viajado(avion.get_tiempo_viajado()+1)
            if (idx not in deben_ser_reubicados) and (avion.get_velocidad() >= 0):
                avion.actualizar_velocidad()

        for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.display.quit()  # Cierra la ventana de visualización
                    sys.exit()             # Termina la ejecución del programa

        screen.fill((20, 22, 28)) #borra lo que había dibujado en el frame anterior
        draw_marks(screen, font) #Traza marcas verticales en las posiciones de 5, 15, 50 y 100 millas náuticas.
        
        
        draw_planes(screen, font, fila_aviones) #dibuja los aviones de la fila con su id, color segun velocidad,ect.

        #para mostrar la hora
        hora_str = format_time_hhmm(acc_time)
        screen.blit(font.render(f"Hora simulada: {hora_str}", True, (255,255,255)), (WIDTH-220, 20))

        pygame.display.flip()#para que se vea todo en la pantalla
        clock.tick(30)  # para que no resfresque tan seguis y consuma mucha cpu

        # avanzar tiempo simulado en 1 min
        acc_time += 1      
           

pygame.quit()


