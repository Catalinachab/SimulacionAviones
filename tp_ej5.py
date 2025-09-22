from typing import *
from tools_visualizacion import *
import random
import pygame
import numpy as np
import json
from pathlib import Path
import sys
import os
import pygame
from claseAvion import *


#visualizacion
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AEP – Simulación + Visualización")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 16)

def guardar_run_json(output_dir, params_dict,
                     cant_arribos_por_hora,
                     cant_aviones_a_montevideo,
                     cant_detectados_por_hora, cant_congestion_por_hora,cant_retraso_por_hora, cant_aterrizajes_interrumpidos):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    p_val = params_dict.get("p", "x")
    sim_val = params_dict.get("rangoSim", "x")

    file_name = f"run_p={p_val}_sim={sim_val}_conInterrupcion.json"
    file_path = Path(output_dir, file_name)

    data = {
        "parametros": params_dict,
        "cant_arribos_por_hora": cant_arribos_por_hora.tolist(),
        "cant_aviones_a_montevideo": cant_aviones_a_montevideo.tolist(),
        "cant_detectados_por_hora": cant_detectados_por_hora.tolist(),
        "cant_congestion_por_hora": np.asarray(cant_congestion_por_hora).tolist(),
        "cant_retraso_por_hora":cant_retraso_por_hora.tolist(),
        "cant_aterrizajes_interrumpidos":cant_aterrizajes_interrumpidos.tolist()
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Guardado {file_path}")

# ========================
# PARÁMETROS DE SIMULACIÓN
# ========================

rangoSim= 50000
rangoHorario = 18
lambdas = [0.02, 0.1, 0.2, 0.5, 1]


for p in lambdas:
    print(lambdas)
    cant_arribados=0
    cant_arribos_por_hora = np.zeros((rangoSim, rangoHorario)) 
    cant_aterrizajes_interrumpidos = np.zeros((rangoSim, rangoHorario))  #nuevo
    cant_aviones_a_montevideo = np.zeros((rangoSim, rangoHorario)) 
    cant_detectados_por_hora = np.zeros((rangoSim, rangoHorario))   
    cant_congestion_por_hora =  np.zeros((rangoSim, rangoHorario),  dtype=int)
    cant_retraso_por_hora =  np.zeros((rangoSim, rangoHorario))

    for simulacion in range(rangoSim):  
        if simulacion%1000==0:
            print("arranca simulacion numero:", simulacion)
        id=1
        fila_aviones: List[Avion] = []
        acc_time = 0
        cant_detectados=0
        fueron_a_montevideo=0
        interrumpidos_en_esta_hora = 0
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

                #CÓDIGO ESPECIFICO AL EJ 5:
                #Franja 2 (15 mn -> 5 mn)
                distancia_f2_km = 10*1.852
                velocidad_f2_kmh = 200*1.852
                tiempo_f2_h = distancia_f2_km / velocidad_f2_kmh #tiempo que le demora en recorrer la 2da franja
                tiempo_f2_min = tiempo_f2_h*60

                #Franja 1 (5 mn -> 0 mn)
                distancia_f1_km = 5*1.852
                velocidad_f1_kmh = 150*1.852
                tiempo_f1_h = distancia_f1_km / velocidad_f1_kmh 
                tiempo_f1_min = tiempo_f1_h*60

                #Total tiempo bajo
                tiempo_total_min = tiempo_f1_min + tiempo_f2_min

                # Probabilidad por minuto de interrupción
                p_minuto = (1/10) / tiempo_total_min
                
                if avion.get_franja() <= 2 and avion.get_velocidad() > 0:
                    interrumpe_aterrizaje = np.random.binomial(1, p_minuto)
                    if interrumpe_aterrizaje == 1:
                        avion.set_velocidad(-200*1.852)
                        interrumpidos_en_esta_hora += 1
                
            for avion in llegados: 
                fila_aviones.remove(avion)

            fila_aviones.sort()                
             
            # 2) posible nuevo avión
            nuevo_detectado = np.random.binomial(1, p) 
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

            
            # 4) registrar por hora
            if (m+1) % 60 ==0:
                h = m//60
                cant_arribos_por_hora[simulacion][h]=cant_arribados
                cant_aviones_a_montevideo[simulacion][h]=fueron_a_montevideo
                cant_detectados_por_hora[simulacion][h]=cant_detectados
                cant_aterrizajes_interrumpidos[simulacion][h] = interrumpidos_en_esta_hora
                cant_retraso_por_hora[simulacion][h]=acum_atraso

                nuevos = len(ids_congestionados) - prev_cong_size #calculamos la diferencia de los total de congestionados - ya contamos= nuevos congestionados
                cant_congestion_por_hora[simulacion, h] = max(0, nuevos)  
                prev_cong_size = len(ids_congestionados)

                #Seteamos en 0 todo lo necesairo
                cant_arribados=0
                fueron_a_montevideo=0
                cant_detectados=0
                interrumpidos_en_esta_hora = 0
                acum_atraso=0

            

    pygame.quit()
    params = {
    "rangoSim": rangoSim,
    "p": p
    }

    guardar_run_json(
        output_dir="ej5_simulaciones",
        params_dict=params,
        cant_arribos_por_hora=cant_arribos_por_hora,
        cant_aviones_a_montevideo=cant_aviones_a_montevideo,
        cant_detectados_por_hora=cant_detectados_por_hora,
        cant_congestion_por_hora=cant_congestion_por_hora,
        cant_retraso_por_hora=cant_retraso_por_hora,
        cant_aterrizajes_interrumpidos=cant_aterrizajes_interrumpidos
    )

