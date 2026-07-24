---
id: propagacion-sonido
tipo: concepto
titulo: "Velocidad de propagación"
url: "https://www.biosemiotics.net/velocidad-propagacion-ultrasonido/"

abstract: >
  El equipo convierte el tiempo de retorno de cada eco en profundidad suponiendo
  una velocidad cercana a 1540 m/s en tejido blando y dividiendo el trayecto
  entre ida y vuelta. La cifra es una calibración, no la velocidad exacta de
  todos los tejidos. Cuando el medio o el trayecto rompen el supuesto, una
  interfaz puede desplazarse, deformarse o medirse de forma incorrecta.

dominio: fisica
nivel: principiante
capitulo: 2
orden: 3
tags: [fisica]
relacionado_con: [efecto-piezoelectrico]
prerequisito_de: []
refs: [kossoff2000, feldman2009, aldrich2007, hangiandreou2003, jensen2007]
---

El sistema calcula:

```text
profundidad = velocidad asumida × tiempo de retorno / 2
```

La división por dos corresponde al viaje del pulso hasta el reflector y de
regreso. En tejido blando se usa aproximadamente **1540 m/s** para construir una
escala coherente.

## Velocidad no es frecuencia

La velocidad describe cuánto avanza la onda por unidad de tiempo. La frecuencia
describe cuántos ciclos ocurren por segundo. Se relacionan mediante
`longitud de onda = velocidad / frecuencia`; una sonda de más MHz no viaja más
rápido por el mismo tejido.

## Error de velocidad

Los tejidos no comparten una velocidad idéntica. Si el trayecto real difiere del
supuesto, el equipo puede ubicar un reflector demasiado profundo o superficial,
deformar un borde o crear un escalón entre trayectos vecinos. Refracción y
trayectos múltiples agregan otros errores.

## Dónde NO confiar

- No trates 1540 m/s como valor exacto de todos los tejidos.
- No confundas velocidad con frecuencia.
- No asumas que cada eco viajó en línea recta una sola vez.
- No midas una interfaz deformada sin cambiar de ventana y plano.
- No confundas precisión decimal con exactitud física.
