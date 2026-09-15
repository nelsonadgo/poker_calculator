♠️ Texas Hold'em - Calculadora de Probabilidades (Monte Carlo)

Una aplicación web Mobile-First full-stack diseñada para calcular en tiempo real las probabilidades de ganar, empatar o perder en una mano de Poker Texas Hold'em.

La herramienta utiliza un motor matemático desarrollado en Python que aplica simulaciones Monte Carlo para predecir los posibles resultados de la mesa frente a múltiples oponentes.

📱 Interfaz de Usuario (Mobile-First)

El frontend fue diseñado con un enfoque nativo para dispositivos móviles, priorizando la ergonomía y la velocidad de uso durante una partida real:

Bottom Sheet UI: La selección de cartas no utiliza menús desplegables (<select>) genéricos. En su lugar, despliega un panel modal desde la parte inferior de la pantalla adaptado para el uso con el pulgar.

Selección en Dos Pasos: Primero se selecciona el valor de la carta (A, K, Q...) y luego el palo (Corazones, Picas...), minimizando los errores de pulsación.

Validación en Tiempo Real: El sistema impide seleccionar cartas duplicadas (cartas que ya están en tu mano o en la mesa comunitaria).

Feedback Visual: Barras de progreso animadas que muestran de un vistazo el porcentaje de Éxito (Verde), Empate (Amarillo) y Derrota (Rojo).

🧠 ¿Cómo funciona la Predicción? (El Motor Matemático)

A diferencia de otras calculadoras que utilizan bases de datos pre-calculadas (Lookup Tables) que pesan gigabytes, esta API utiliza una Simulación Monte Carlo desarrollada 100% en Python.

1. El Evaluador de Manos

El núcleo del backend incluye un algoritmo combinatorio que recibe 7 cartas (las 2 del jugador + las 5 comunitarias) y encuentra la mejor combinación posible de 5 cartas.
Asigna un Score numérico (Ej: 8 para Escalera de Color, 0 para Carta Alta) y una lista de Kickers (desempates) ordenados por importancia.

2. Simulación Monte Carlo

Cuando se realiza una consulta (ej. Tengo As-Rey, en el Flop hay 2-7-J y juego contra 3 oponentes), el sistema no calcula todas las combinaciones exactas (lo cual tardaría demasiado). En su lugar, realiza un muestreo aleatorio masivo:

Depuración del Mazo: Retira las cartas conocidas (jugador y mesa) de la baraja estándar de 52 cartas.

Miles de Futuros Posibles: Se ejecuta un bucle de 3000 iteraciones.

Repartición Aleatoria: En cada iteración, se baraja el mazo restante y se reparten las cartas comunitarias faltantes (Turn y River) y 2 cartas aleatorias a cada oponente.

Enfrentamiento: El algoritmo evalúa la mano del jugador contra las de los oponentes. Si el jugador tiene el mayor Score (o gana por Kicker), se anota una victoria.

Convergencia Estadística: Al finalizar las 3000 simulaciones, la Ley de los Grandes Números asegura que el porcentaje de victorias/empates obtenido en la muestra sea extremadamente cercano a la probabilidad matemática real (margen de error < 1.5%), devolviendo el resultado en menos de 0.3 segundos.

🚀 Stack Tecnológico

Backend: Python + FastAPI

Operaciones asíncronas para máxima velocidad de respuesta.

Lógica matemática utilizando la librería estándar itertools y collections.

Frontend: HTML5 + JavaScript Vainilla + TailwindCSS

Inyección de estilos vía CDN.

Funciones asíncronas (async/await) para consumir la API REST.

🛠️ Instalación y Uso Local

Clonar el repositorio:

git clone https://github.com/tu-usuario/poker-calculator.git
cd poker-calculator


Levantar el Backend (API):

python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
pip install fastapi uvicorn pydantic
uvicorn main_poker:app --reload


Ejecutar el Frontend:
Abre el archivo index.html en cualquier navegador web moderno, o sírvelo localmente usando Node.js:

npx serve
