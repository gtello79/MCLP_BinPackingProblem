# MCLP_BPP

## Reunión 22-12-2020
Faltaría:

* Cargar la instancia en python (cajas con sus dimensiones) (Listo)
* Implementar algoritmo. (Listo)

A grandes rasgos el algoritmo hace los siguiente:
1. Generación de bins iniciales usando **BSG**
2. Selección de bin a desarmar y almacenar cajas en $C$
3. Mientras $C$ no quede vacío o máximo de iteraciones:

   1. Seleccionar caja $c$ de $C$
   2. Seleccionar bin de destino $B$
   3. Usar **BSG** para generar bin $B'$ usando cajas $B \cup \{c\}$, priorizando $c$. Es posible que **BSG** retorne conjunto de cajas residuales $R$
   4. Si $R$ es mejor que $c$, $B$ se reemplaza por $B'$ en el conjunto de bins y $C \gets C \cup R$
   
 4. Volver a 2 (seleccionar otro bin para desarmar)

## Reunion 29-12-2020
- Verificar la solucion
    * La solución necesitaba ser ajustada, borraba un conjunto completo de cajas (esencialmente el que sería el bin a eliminar), fue verificado y arreglado.

- Calcular el volumen de los bins (Porcentaje de llenado)
    * Aqui necesitamos saber el % de llenado de cada bin, por ende, sera necesario guardar la respuesta del bsg.(id_bin + %llenado)    
    * Done

- Generar alguna gráfica que pueda ser util para analizar el cambio del volumen.
    * Listo

- Modularizar el código que funciona correctamente

- Corres pruebas con distintas características
    * idClass = 1, boxSize = 200, id_Instance = 0 : No ocurren cambios hasta el momento

- Ajustar el iterador de persistencia (en Reduce bins) para que sea coherente a la cantidad de cajas que se tiene por cada bin, es decir, un valor que me permita reintentar ingresar la caja.

- Graficar los bins (codigo en Matlab) (Pendiente, Profe Ignacio elaborará el generador de posiciones)

## Reunión 05-01-2021
- 