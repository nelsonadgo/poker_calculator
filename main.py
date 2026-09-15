from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import random
import itertools
from collections import Counter

app = FastAPI(
    title="Poker Odds Calculator API",
    description="Simulador Monte Carlo para probabilidades de Texas Hold'em",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PokerRequest(BaseModel):
    player_cards: List[str]  # Ejemplo: ["Ah", "Kd"]
    board_cards: List[str]   # Ejemplo: ["2s", "9c", "Tc"]
    num_opponents: int = 1

# Mapeo de valores de cartas para el evaluador
RANK_VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

def parse_card(card_str):
    """Convierte un string 'Ah' a una tupla (14, 'h')"""
    return (RANK_VALUES[card_str[0]], card_str[1])

def evaluate_5cards(cards):
    """
    Evalúa una combinación de 5 cartas exactas.
    Retorna un 'score' (0 al 8) y los valores de desempate.
    """
    ranks = sorted([c[0] for c in cards], reverse=True)
    suits = [c[1] for c in cards]
    is_flush = len(set(suits)) == 1

    # Verificar Escalera (Straight)
    is_straight = False
    if ranks == [14, 5, 4, 3, 2]: # Caso especial: Escalera A-2-3-4-5
        is_straight = True
        ranks = [5, 4, 3, 2, 1]
    elif len(set(ranks)) == 5 and ranks[0] - ranks[4] == 4:
        is_straight = True

    # Contar repeticiones para pares, tríos, poker
    counts = Counter(ranks).most_common()
    # Ordenar por frecuencia descendente, y luego por valor de carta descendente
    counts.sort(key=lambda x: (x[1], x[0]), reverse=True)

    # 8: Straight Flush (Escalera de color)
    if is_flush and is_straight:
        return 8, ranks
    # 7: Four of a Kind (Poker)
    if counts[0][1] == 4:
        return 7, [counts[0][0], counts[1][0]]
    # 6: Full House
    if counts[0][1] == 3 and counts[1][1] == 2:
        return 6, [counts[0][0], counts[1][0]]
    # 5: Flush (Color)
    if is_flush:
        return 5, ranks
    # 4: Straight (Escalera)
    if is_straight:
        return 4, ranks
    # 3: Three of a Kind (Trío)
    if counts[0][1] == 3:
        return 3, [counts[0][0], counts[1][0], counts[2][0]]
    # 2: Two Pair (Doble Par)
    if counts[0][1] == 2 and counts[1][1] == 2:
        return 2, [counts[0][0], counts[1][0], counts[2][0]]
    # 1: Pair (Par)
    if counts[0][1] == 2:
        return 1, [counts[0][0], counts[1][0], counts[2][0], counts[3][0]]
    # 0: High Card (Carta Alta)
    return 0, ranks

def evaluate_7cards(cards):
    """Busca la mejor combinación de 5 cartas dentro de las 7 disponibles (Texas Hold'em)"""
    best_rank = -1
    best_tie_breaker = []
    
    # Evaluar todas las combinaciones posibles de 5 cartas de las 7 dadas (21 combinaciones)
    for combo in itertools.combinations(cards, 5):
        r, t = evaluate_5cards(combo)
        if r > best_rank or (r == best_rank and t > best_tie_breaker):
            best_rank = r
            best_tie_breaker = t
            
    return (best_rank, best_tie_breaker)

def run_monte_carlo(player_cards_str, board_cards_str, num_opponents, iterations=3000):
    """
    Simula miles de partidas aleatorias para estimar las probabilidades.
    """
    full_deck = [r+s for r in '23456789TJQKA' for s in 'shdc']
    
    # Validar duplicados
    known_cards = player_cards_str + board_cards_str
    if len(known_cards) != len(set(known_cards)):
        raise ValueError("Existen cartas duplicadas en la entrada.")

    # Remover cartas conocidas del mazo
    deck = [c for c in full_deck if c not in known_cards]
    
    player_hole = [parse_card(c) for c in player_cards_str]
    board_parsed = [parse_card(c) for c in board_cards_str]
    
    wins = 0
    ties = 0
    losses = 0

    for _ in range(iterations):
        # Clonar mazo y mezclar para esta simulación
        sim_deck = list(deck)
        random.shuffle(sim_deck)
        
        # Repartir las cartas comunitarias faltantes (hasta llegar a 5)
        cards_needed_for_board = 5 - len(board_parsed)
        sim_board = list(board_parsed)
        for _ in range(cards_needed_for_board):
            sim_board.append(parse_card(sim_deck.pop()))
            
        # Evaluar la mano de nuestro jugador
        player_score = evaluate_7cards(player_hole + sim_board)
        
        # Simular oponentes
        is_win = True
        is_tie = False
        
        for _ in range(num_opponents):
            opp_hole = [parse_card(sim_deck.pop()), parse_card(sim_deck.pop())]
            opp_score = evaluate_7cards(opp_hole + sim_board)
            
            # Comparar scores (Tuplas en Python se comparan elemento por elemento, ideal para desempates)
            if opp_score > player_score:
                is_win = False
                is_tie = False
                break
            elif opp_score == player_score:
                is_tie = True
                is_win = False
                
        if is_win:
            wins += 1
        elif is_tie:
            ties += 1
        else:
            losses += 1

    return {
        "win_pct": round((wins / iterations) * 100, 2),
        "tie_pct": round((ties / iterations) * 100, 2),
        "loss_pct": round((losses / iterations) * 100, 2),
        "iterations": iterations
    }

@app.post("/api/poker/probabilidad")
def calculate_odds(req: PokerRequest):
    try:
        # Validaciones de reglas de Poker
        if len(req.player_cards) != 2:
            raise ValueError("El jugador debe tener exactamente 2 cartas.")
            
        if len(req.board_cards) not in [0, 3, 4, 5]:
            raise ValueError("La mesa debe tener 0 (Pre-flop), 3 (Flop), 4 (Turn) o 5 (River) cartas.")
            
        if req.num_opponents < 1 or req.num_opponents > 9:
            raise ValueError("El número de oponentes debe estar entre 1 y 9.")

        # Ejecutar el motor predictivo
        resultados = run_monte_carlo(
            player_cards_str=req.player_cards,
            board_cards_str=req.board_cards,
            num_opponents=req.num_opponents,
            iterations=3000 # 3000 iteraciones da una excelente precisión en <0.5 segundos
        )
        
        return resultados

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))