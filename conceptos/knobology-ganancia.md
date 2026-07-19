---
id: knobology-ganancia
tipo: concepto
titulo: "Ganancia"
dominio: knobology
nivel: principiante
capitulo: 6
orden: 1
tags: [knobology, optimizacion]
relacionado_con: [knobology-profundidad, ecogenicidad]
prerequisito_de: []
refs:
  - zander2020
  - pye1992
  - duggan2022
  - abuzidan2011
  - hangiandreou2003
  - aldrich2007
---

La **ganancia** amplifica electrónicamente los ecos recibidos y modifica el brillo
de la imagen. Actúa en la recepción: no aumenta la energía transmitida, la
penetración acústica ni la resolución espacial. Una ganancia insuficiente puede
ocultar ecos débiles; una excesiva amplifica también ruido y speckle, satura los
graises y reduce el contraste útil.

La ganancia global actúa sobre toda la imagen. La **compensación de ganancia en el
tiempo** (TGC) modifica la amplificación según el tiempo de retorno y, por tanto,
la profundidad, para compensar parcialmente la atenuación. Los ajustes deben formar
una transición suave: una curva escalonada puede crear bandas artificiales. La TGC
no recupera información que se perdió durante la propagación.

La optimización comienza con sonda, preset, frecuencia, ventana, profundidad y foco.
Después se ajusta la ganancia hasta conservar textura y límites sin llenar de ruido
una referencia verdaderamente anecoica; finalmente se corrige la TGC si tejidos
comparables cambian de brillo solo por la profundidad. Ganancia, potencia de salida,
rango dinámico y profundidad son controles distintos, y no existe un valor numérico
universal entre equipos o presets.
