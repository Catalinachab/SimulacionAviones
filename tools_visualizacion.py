import pygame
from typing import *
NM = 1.852  # km por milla náutica

# --------- Colores por franja ----------
def color_por_dist(dist_km: float):
    if dist_km < 5*NM:      return (70, 200, 70)   # 0–5 mn
    elif dist_km < 15*NM:   return (70, 130, 255)  # 5–15 mn
    elif dist_km < 50*NM:   return (255, 165, 0)   # 15–50
    elif dist_km < 100*NM:  return (255, 80, 80)   # 50–100
    else:                   return (180, 180, 180) # >100

# ====== Parámetros de visual ======
WIDTH, HEIGHT = 1200, 420
MARGIN_L, MARGIN_R = 80, 40
TRACK_LEN = WIDTH - (MARGIN_L + MARGIN_R)  # largo de "cola" en pixeles

def x_from_dist_km(dist_km: float) -> int:
    # 0 mn = AEP (x=MARGIN_L), 100 mn = extremo derecho
    frac = max(0.0, min(1.0, dist_km / (100*NM)))
    return int(MARGIN_L + frac * TRACK_LEN)

def draw_marks(screen, font):
    # pista
    pygame.draw.line(screen, (230, 230, 230), (MARGIN_L, 60), (MARGIN_L, HEIGHT-60), 4)
    screen.blit(font.render("AEP", True, (230, 230, 230)), (MARGIN_L-24, 25))
    # marcas 5/15/50/100 mn
    for mn, label in [(5, "5 mn"), (15, "15 mn"), (50, "50 mn"), (100, "100 mn")]:
        x = x_from_dist_km(mn*NM)
        pygame.draw.line(screen, (120,120,120), (x, 80), (x, HEIGHT-80), 1)
        screen.blit(font.render(label, True, (160,160,160)), (x-20, HEIGHT-30))

def draw_planes(screen, font, fila_aviones: List):
    # Y por fila (separados)
    y0, dy = 110, 26
    for i, av in enumerate(fila_aviones):
        d = av.get_distancia()
        x = x_from_dist_km(d)
        y = y0 + i*dy
        v = av.get_velocidad()
        en_retroceso = False
        if v<0:
            en_retroceso = True
        col = (255, 255, 255) if en_retroceso else color_por_dist(d)
        # Cambiar dirección del polígono si va en retroceso
        if en_retroceso:
            # Punta a la izquierda
            if av.get_distancia() < 100*1.852:
                pygame.draw.polygon(screen, col, [(x, y), (x-15, y-8), (x-15, y+8)])
                screen.blit(font.render(f"ID {av.id}", True, (255,255,0)), (x-15, y-20))
        
        else:
            # Punta a la derecha
            pygame.draw.polygon(screen, col, [(x, y), (x+15, y-8), (x+15, y+8)])
            screen.blit(font.render(f"ID {av.id}", True, (255,255,0)), (x-15, y-20))
        

        
        # velocidad y distancia (opcional)
        v = int(av.get_velocidad()/NM)  # en kt

def format_time_hhmm(total_minutes: float) -> str:
    mins = int(total_minutes)
    # ciclo de 18h, arrancando a las 06:00
    mins_in_window = mins % (18*60)       # 0..1079
    h = 6 + mins_in_window // 60          # 6..23
    m = mins_in_window % 60
    return f"{h:02d}:{m:02d}"

