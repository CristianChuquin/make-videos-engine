## ANIMACIÓN — la gramática completa (extraída de `design` v3.4 el 1-nov-2026)

Esta sección es la **fuente única** de cómo se anima una slide. `design` se retiró: escribía prompts para Seedance, y aquí sus reglas se cumplen con los verbos del motor. Se conserva su numeración de principios (2-bis, 2-ter…) porque la tabla de verbos los cita.

**Lo que NO se trajo**, porque era de Seedance y no aplica al render por código: elección de modelo y ramas (2.0 Mini, 2.5, H3, Flux, Kling), parámetros de job y créditos, header y formato de etapas del prompt, conteo de palabras y caracteres, vocabulario para «forzar» al modelo, anclas de estilo del prompt y el aviso de roles `start_image`/`end_image` invertidos. Aquí el orden y el tiempo los fija el código, así que esos riesgos no existen.

### La transición A → B

Cada clip es una transición del **Frame A** (el fondo, lo que ya está en la slide al entrar) al **Frame B** (la slide terminada, el último frame, el que queda congelado). El código anima **solo la diferencia** entre A y B.

### 📌 Regla del Frame A — lo que ya existe se sostiene

Lo que está en el Frame A (fondo, textura, reglas finas, marcos, un título vertical heredado) **no se anima y jamás se redibuja**. En código va dentro de `.frame-a`, y el lint lo acepta sin verbo.

Procedimiento antes de escribir la línea de tiempo:
1. Listar qué hay en el Frame A.
2. Listar qué hay en el Frame B.
3. **La resta es la animación.** Nada de la lista de A recibe verbo.

El primer frame del clip es además la portada del video y el fondo de la slide en el PPTX (F5): si algo de A se anima, la slide «salta» al entrar.

### 🚶 Regla fundamental — NADA SOLO APARECE

**Manda sobre todas las demás.** Lo que en el mundo real se mueve por sí mismo **no se materializa: llega**. Una rueda entra rodando, un organismo entra con sus flagelos ya batiendo, una pieza cae y rebota en su sitio. **El reveal y el movimiento son el mismo evento, no dos.** El defecto a evitar es el fundido o la máscara pasiva: el objeto aparece quieto en su lugar y después empieza a moverse. Eso lee como stock.

- **A qué aplica:** todo lo que tiene locomoción o movimiento propio (organismos, vehículos, piezas que caen o ruedan, líquidos, humo; personas solo si Cris las pide).
- **A qué no:** texto, barras, líneas, gráficos, iconos planos (Dominio 1). Ahí el reveal **ya es** su movimiento: un `type` es esta regla aplicada a una palabra.
- **En código:** el verbo de entrada es el verbo de la acción, y la posición final del Frame B es donde termina. `arrive` desde el borde con su movimiento propio corriendo a la vez (`spin` para lo que rueda, un tween de idle para lo que bate o late), nunca `pop` ni `autoAlpha` sobre un objeto con locomoción.

Tres condiciones, o la regla se vuelve en contra:
1. **La acción tiene destino.** Entrar moviéndose no cancela el aterrizaje: se llega, se ejecuta, se encaja en la pose exacta del Frame B, y no queda movimiento residual.
2. **Un gesto por objeto.** Llegar **es** ese gesto; no se le encadena un segundo.
3. **El movimiento vive en las partes y en el objeto, no en el contorno entero.**

> **El precio:** si un recorrido largo se ve torpe en el clip, la salida es **un recorrido más corto** (menos distancia en `arrive`), nunca volver a la aparición pasiva. Se juzga sobre el clip, no sobre el código.

### 🗂️ Catálogo de movimiento por elemento

**No es una lista de opciones: es lo que hace cada cosa, siempre.**

| Elemento en el Frame B | Lo que hace | Verbo del motor |
|---|---|---|
| **Ilustración de línea sin relleno** | Se dibuja **línea por línea**, en el orden en que la construiría una mano, con ~0,10 s entre trazos. La maquinaria interna densa se descubre por máscara sobre trazo fijo | `draw` (el orden del DOM es el orden de la mano); lo denso, `wipe` |
| **SVG del banco** | Pieza por pieza, de lo grande a lo pequeño: contorno trazado y luego relleno | `AX.build` |
| **Herramienta sobre una pieza** | **Actúa sobre lo que toca**: la llave gira la tuerca y la tuerca gira con ella; la pesa hunde el platillo. Nunca es atrezzo quieto | `spin`/tween de las dos piezas a la vez (parentadas en un `<g>`) |
| **Aparato mecánico** | **Se ve funcionando**: engranajes en malla, pistones, palancas, poleas. Sobre trazo ya fijo (Etapa 2), y se asienta en el estado del Frame B | `draw` en Etapa 1 → `spin` en Etapa 2 |
| **Célula, organismo, cuerpo vivo** | **Se ve vivo**: orgánulos derivando, membrana ondulando, flagelos batiendo, núcleo con pulso mínimo. Ya en movimiento **mientras** se dibuja, y sigue hasta el último frame | `draw` + tween de idle desde el mismo instante (ver Dominio 2) |
| **Dona, pastel, rueda de sectores** | **Gira sobre su propio eje** en sentido horario, los sectores **naciendo del giro** y las cifras contando durante la vuelta. Frena en registro exacto | `ring` + `count` (2-sexies) |
| **Barras, columnas, pilas** | **Crecen desde abajo**, ancladas a su base. Relleno sólido: escala desde cero. Pila: **ítem por ítem** con ~0,10 s | `grow` (sólido) · `pop`/`arrive` por ítem (pila) · `wipe` dir `up` si tienen trama (2-quater) |
| **Números** | Los que **miden** cuentan desde cero **durante** el crecimiento de su elemento; los **nominales** tipean. Parentados a su elemento si este se desplaza | `count` · `type` · `ride` (2-bis, 2-ter) |
| **Flechas, líneas guía, llaves, corchetes, cotas** | **Se trazan de origen a destino**, con la punta llegando al final del recorrido. Nunca enteras de golpe | `draw` sobre el path; la punta, `pop` al terminar el trazo (no `marker-end`, que aparece al inicio) |
| **Texto** | Ver Principio 3 | `type` · golpes de Cosmos en títulos |
| **Tramas, rayado, halftone** | Máscara viajando sobre patrón fijo, **nunca escalado** | `wipe` (2-quater) |
| **Rellenos sólidos** | Inundan desde su borde de anclaje | `flood` · `wipe` |

> **La prueba del código terminado: ningún elemento entra sin verbo propio.** Si algo «aparece» o simplemente «está», le falta fila en esta tabla. El lint de `render_clip.js` lo comprueba sobre el DOM real. Lo único exento es lo heredado del Frame A.

**Cuándo se recorta.** Nunca se recorta el *tipo* de movimiento (una flecha no pasa a fundido por falta de tiempo): se recortan **elementos enteros**. Lo primero que cae son cotas, barras de escala, arcos y anotaciones secundarias que el Frame B ya muestra y el ojo no necesita ver dibujarse. Con 5 o más elementos iguales, se animan con el mismo verbo, el mismo timing y un stagger.

### 🎯 Dominios de movimiento

**Dominio 1 · datos, gráficos y texto → motion graphics puro.** Barras, pasteles, donas, flechas, nodos, curvas, líneas guía, tablas, números, títulos, cuerpo, rótulos, destellos, halftones, siluetas planas, formas isométricas e ilustración vectorial de línea. Reveals por trazo, máscara, escala desde cero, inundación o barrido radial; easing `ease-out`, `ease-in-out`, asentamiento elástico, `snap`. **Cámara siempre estática:** nunca acercamientos, paneos ni zooms; el contenido es el que se anima.

**Dominio 2 · elementos vivos naturalistas → reveal + idle orgánico persistente.** Seres o fenómenos con movimiento propio **y** dibujados con detalle naturalista (bacterias con flagelos, corazón anatómico, células en corte con orgánulos, agua, fuego).
- **En una estructura interna, el movimiento es interno:** la célula no se desplaza por el cuadro, se ve viva por dentro.
- **El reveal ocurre ya moviéndose:** los flagelos baten mientras el trazo se completa, nunca después.
- **El idle persiste** hasta el final mientras todo lo demás se congela, y hay que programarlo explícitamente o el hold lo mata.
- **En código (por implementar como verbo `idle`):** hoy se escribe con un tween propio en `S.tl` (`repeat`, `yoyo`, amplitud pequeña) marcando el elemento con `__sc = true` para el lint. Como el clip se congela en su último frame, **el idle tiene que verse bien congelado**: amplitud mínima y el último frame en una pose limpia.

**Juicio estilístico — cuándo algo «vivo» es en realidad geométrico. El estilo visual manda, no el referente:**
- Silueta plana, flat, isométrica o vectorial de línea → Dominio 1, aunque represente un cuerpo.
- Acuarela naturalista o ilustración científica con textura → idle orgánico.
- Esfera negra con halftone (Harper) → Dominio 1: es abstracción gráfica.
- Icono plano de pulmón → Dominio 1. No se simula respiración.
- **El grabado denso es Dominio 1 pese a su detalle:** una figura de línea blanca con achurado cerrado no se anima anatómicamente (la línea se desarma). El movimiento va a lo mecánico que la acompaña.

**Dominio 3 · figura que ejecuta su acción.** Solo existe si Cris pide figuras para un deck (por defecto no hay figuras humanas). La figura plana ejecuta **la acción que el Frame B la muestra ejecutando**, como aterrizaje: entra, ejecuta, encaja en su pose final y no sigue.
- Solo la acción que el Frame B evidencia; no se inventan gestos.
- **Un gesto por figura.** La locomoción (caminar, subir peldaño a peldaño) **es** ese gesto. Un objeto en su mano **viaja con ella**: soltarlo sería un segundo gesto.
- El objeto manipulado se anima **con** la figura, nunca antes.
- Entra moviéndose desde un sitio de origen legible, no por máscara.
- Se mueve la articulación nombrada (rodilla, codo) y el objeto, no el contorno entero.
- Con dos figuras, una ejecuta y la otra sostiene su pose.

### 🎬 Orden canónico de etapas — line work primero, acción y texto después

Cada clip de 12 s tiene **dos etapas**. El reparto no se decide por slide: es este.

| Etapa | Tramo aproximado | Qué ocurre |
|---|---|---|
| **Etapa 1 · el escenario se dibuja** | 0 – ~5,5 s | **Todo** el line work sin relleno se traza línea por línea; los gráficos crecen con sus cifras; los rellenos sólidos aterrizan al final de su trazo. Ni tipografía de cuerpo ni figuras todavía |
| **Etapa 2 · acción y texto** | ~5,5 – 11 s | Los mecanismos se ponen en marcha, las figuras (si las hay) ejecutan su acción, los rótulos se trazan y el texto tipea. Primero lo que ancla, después lo que rotula |
| **Hold** | 11 – 12 s | Todo quieto y asentado, **sin movimiento residual**. Es lo que garantiza que el último frame sea la slide terminada |

- **Por qué ese orden:** el line work es el escenario. Una acción sobre algo que todavía no está dibujado no tiene destino. El texto va al final porque no depende de nada.
- **El título puede abrir la Etapa 1** con un golpe de Cosmos (`rise`, `drop`, `stamp`, `tracking`) cuando la slide lo pide; el cuerpo, los rótulos y los pies van en la Etapa 2.
- **Una etapa, un cambio primario.** Si el evento principal tiene dos partes fuertes, se le da más tiempo, no una etapa extra.
- **Secuencia narrativa explícita** dentro de cada etapa: izquierda→derecha, arriba→abajo o la numeración de la fuente.
- **Una etapa puede mezclar dominios:** el verbo cambia por elemento, no por etapa.

**Dibujar un mecanismo no es ponerlo en marcha, y son dos etapas distintas.** Si la ilustración es una máquina que la slide muestra funcionando (engranajes, balanza, palanca, polea):
- **Etapa 1: se traza quieto**, en su posición final. Nada gira mientras se dibuja.
- **Etapa 2: se mueve** sobre el trazo ya fijo y **se asienta en el estado del Frame B** (nivelado, encajado, en registro).

Girar mientras se traza deforma el dibujo; trazar y no moverlo nunca desperdicia el único movimiento que la lámina pedía.

### 🎯 Principios

**1 · Orden secuencial explícito.** Los elementos entran en orden narrativo claro, nunca todos a la vez.

**2 · Los números animan con su elemento**, en sincronía, no después. ✅ el sector se abre mientras su porcentaje cuenta. ❌ el sector se abre y luego aparece el porcentaje.

**2-bis · Nominal vs medido.** Un número que **etiqueta** en vez de **medir** (la concentración que da nombre a una formulación, un pH, un código, un año) **no cuenta**: un conteo afirma una magnitud que no existe. Tipea. *Prueba:* si dos elementos de distinto tamaño llevaran el mismo número, o dos iguales números distintos, es nominal. Un `0.05%` que nombra una formulación es nominal; un `25%` que es la porción de su sector o un `86.14 Nm` medido cuentan.

**2-ter · El número va parentado a su elemento.** Si el elemento se desplaza al animarse, su cifra **viaja con él**; no se queda flotando esperando a que llegue. En código: `ride` con el mismo `t`, `dur` y `stagger` que el `grow` de su barra.

**2-quater · La trama no se escala, se revela.** Una barra con achurado, rayado o patrón **no se escala**: las rayas se estirarían y el paso dejaría de coincidir entre barras. Se revela con **máscara subiendo sobre el patrón fijo** (`wipe` dir `up`). Las barras de relleno sólido sí escalan (`grow`) o inundan.

**2-quinquies · Lo que gira aterriza en registro.** Una rueda, dona o pastel que rota para **exactamente** en la posición del Frame B, o los sectores quedan desalineados con sus líneas guía. La pieza entra sólida y sin cortes, gira, los separadores salen del centro mientras el giro desacelera, y frena sin rotación residual. `ring` y `spin` terminan en `rotation: 0`, que es la posición del Frame B.

**2-sexies · Lo redondo gira sobre su propio eje.** Una dona, pastel o rueda de sectores no se monta quieta: gira en sentido horario sobre su centro y frena en registro. Tres casos:
- **Gira revelando (caso por defecto de un gráfico con datos):** la pieza rota y **los sectores nacen del giro** mientras cada cifra cuenta durante la vuelta. Un solo evento. → `ring` + `count`.
- **Gira sin revelar:** el anillo ya está lleno en el Frame B y es **motivo gráfico**, no dato: rota entero sobre su centro, con su degradado. → `spin`.
- **Barre sin girar:** solo cuando el arco es lo único que se mueve y **mide** una proporción que hay que leer. → `draw` sobre el arco.

*Prueba entre los dos primeros:* si el relleno es idéntico en toda la fila de anillos, es motivo y solo gira; si cada uno lleva su proporción y su cifra, gira revelando. ❌ Barrer un anillo que ya está lleno (se vaciaría para volver a llenarse). ❌ Montar el gráfico quieto y girarlo después (dos eventos donde hay uno).

**3 · El texto siempre es motion graphics, nunca un fundido.**
- **Cuerpo, rótulos, pies, notas y cifras nominales:** letra por letra, de izquierda a derecha, como máquina de escribir (`type`).
- **Párrafo de varias líneas:** línea por línea con 0,08 s entre líneas, cada una de izquierda a derecha.
- **Títulos:** `type` o un golpe de Cosmos (`rise`, `drop`, `stamp`, `tracking`, `wipeIn`), según RC-5. Ninguno es un fundido.
- **Wordmark o tipografía en contorno:** se **traza** (`draw`), porque es line work.
- **Líneas guía, flechas y llaves que acompañan al texto:** se trazan de origen a destino (`rotulo` lo hace en un solo verbo).
- **Salvo el texto heredado del Frame A**, que no se toca.

**4 · Stagger declarado en segundos.**

| Qué | Stagger |
|---|---|
| Letras de un título | 0,04 s (0,05 s si es enorme) |
| Líneas de un párrafo | 0,08 s |
| Elemento a elemento en gráficos | 0,10–0,15 s |
| Raya a raya en patrones | 0,02 s |
| Trazos de una ilustración | ~0,10 s |

Los defaults del motor (`type` 0,035 s por letra, `grow` 0,12 s, `draw` 0,08 s) caen en estas bandas.

**5 · Elementos vivos = reveal + idle orgánico persistente** (ver Dominio 2).

**6 · Easing de motion graphics:** `ease-out` para entradas, `ease-in-out` para trazos y máscaras, rebote o asentamiento elástico solo en lo que aterriza (`pop`, `stamp`, golpe del contador). Nunca movimientos «cinemáticos» ni dramáticos.

### 😴 Frame de descanso visual (el break)

La slide de `BREAKS` no revela nada nuevo. Su contrato es distinto en todo:

| | Slide normal | **Descanso** |
|---|---|---|
| Reveals y texto | sí | **ninguno** (nada se dibuja, nada se borra) |
| Movimiento | transición A → B | **idle cíclico lento a ritmo constante, que a los 12 s vuelve exactamente a su posición inicial** |
| Hold final | obligatorio | **no aplica**: termina «exactamente como empezó» |

- **Primer y último frame iguales:** como el PPTX muestra el primer frame al entrar y congela el último, el descanso no tiene salto en ninguno de los dos extremos.
- **Qué se mueve:** engranajes, palancas, lo mecánico, un pulso de escala mínimo en marcos; en Harper, destellos que titilan y halftone que respira. **Nunca** el trazo denso ni la tipografía.
- **Nada entra ni sale de cuadro.** Como todo está presente desde el frame 1, la ilustración va en `.frame-a` y solo lo que se mueve recibe su tween de idle.

### 🔇 Sonido — solo si Cris lo pide

Por defecto los clips son **mudos** (RC-1). Si Cris pide sonido para un deck: **música prohibida siempre** (ni score, ni sting, ni swell, ni pad, ni tono ascendente, ni percusión rítmica, ni drone), máximo 3-4 efectos por clip (uno por familia de movimiento) y todos por debajo de la voz. Los efectos describen la mecánica, nunca el ánimo de la slide:

| Elemento | Efecto |
|---|---|
| Texto que tipea | tic seco y tenue de tecla siguiendo el stagger |
| Trazo de línea o eje | trazo seco de pluma sobre papel |
| Barra que se llena o sube | crecida suave y grave de tinta |
| Trama revelándose | rayado de lápiz repetido, muy bajo |
| Nodo o punto que escala | chasquido leve de papel |
| Destello | tic seco y diminuto de brillo |
| Halftone o máscara | barrido suave de grano de papel |
| Elemento que asienta o figura que aterriza | golpe sordo de fieltro |
| Pieza que encaja | clic suave y grave |
| Engranaje en idle | tic mecánico lento |
| Balanza que se nivela | golpe sordo de fieltro al asentar cada platillo |
| Organismos | aleteo húmedo de flagelo, casi inaudible; movimiento fluido lento |
| Reposo | solo tono de sala |

### 📝 Ejemplos traducidos a código (12 s)

**1 · Barras editoriales (Dominio 1).** Cuatro barras alternando negro sólido y trama diagonal, un porcentaje Didone grande sobre cada una (son **nominales**: nombran la concentración, no miden la altura), rótulo sans debajo, título en dos líneas, nota al pie. Frame A: el papel con sus dos reglas finas.

```js
SC.build((S) => {
  // Etapa 1 — las barras crecen; las reglas del papel están en .frame-a
  let e = S.grow("#b1, #b3", 0.4, { stagger: 0.3 });          // sólidas: escalan desde la base
  S.wipe("#b2, #b4", 0.55, { dir: "up", stagger: 0.3 });       // con trama: máscara sobre patrón fijo (2-quater)
  S.ride(".pct", [-260, -180, -320, -140], 0.4, { stagger: 0.15 }); // la cifra viaja con el borde (2-ter)
  // Etapa 2 — rótulos, título y nota
  e = S.type(".lbl", 5.6);
  e = S.rise("#title", e + 0.1);
  S.type("#foot", e + 0.2, { letter: 0.02 });
});
```
*(Si los porcentajes fueran medidos, además de viajar con su barra contarían con `count` durante la subida.)*

**2 · Rueda de tres sectores sin cifras (Dominio 1).** Título vertical y su regla heredados del Frame A. La rueda entra sólida, **gira revelando** sus sectores (`ring`), los radios se trazan desde el centro mientras el giro desacelera (`draw`), frena en registro; en la Etapa 2 las líneas guía se trazan y los rótulos tipean (`rotulo`). Sin cifras, no hay conteo inventado.

**3 · Mecanismo en marcha.** Etapa 1: el tren de engranajes y la balanza se trazan **quietos** (`draw`). Etapa 2: los engranajes giran (`spin`) y los platillos se mecen y **se asientan nivelados**, el estado del Frame B; las cifras medidas cuentan y el texto tipea. Hold sin rotación residual.

**4 · Descanso.** Toda la lámina en `.frame-a`. Los engranajes giran a ritmo constante (360° exactos en 12 s, así el último frame coincide con el primero) y la palanca se mece un grado y vuelve. Nada entra, nada se redibuja.

**5 · Organismos (Dominio 2).** Cada bacteria se traza (`draw`) **mientras** sus flagelos ya baten (tween de idle desde el mismo instante), y sigue moviéndose con amplitud mínima hasta el final; el resto se congela en el hold.

### ✅ Checklist de animación (antes de renderizar)

1. ¿Se hizo el inventario A vs B, y todo lo heredado está en `.frame-a` sin verbo?
2. **¿Nada solo aparece?** Todo lo que se mueve por sí mismo entra ejecutando su movimiento, con pose final.
3. ¿Cada elemento del Frame B tiene su verbo del catálogo? (El lint lo confirma.)
4. ¿Etapa 1 con **todo** el line work y los gráficos; Etapa 2 con mecanismos, figuras y texto; hold desde los 11 s?
5. ¿Los números que miden cuentan, los nominales tipean, y los que acompañan a un elemento que se desplaza viajan con él?
6. ¿Las tramas se revelan por máscara en vez de escalarse? ¿Lo que gira aterriza en registro?
7. ¿Lo redondo gira sobre su eje, eligiendo bien entre girar revelando, girar sin revelar y barrer?
8. ¿Todo el texto tipea o entra con un golpe de Cosmos, y nada entra con fundido?
9. ¿El mecanismo se traza quieto y se mueve después?
10. ¿El juicio «vivo vs geométrico» es correcto (grabado denso y vectorial de línea = Dominio 1)?
11. ¿Cámara estática?
12. En el descanso: ¿cero reveals, idle cíclico y último frame igual al primero?
