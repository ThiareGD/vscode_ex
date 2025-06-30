# Resumen del documento: Guía uso modelo aguas subterráneas SEIA

## 5. En cualquier caso,

En cualquier caso, el aspecto fundamental reside en que el software seleccionado
incluya todos los elementos, proce- sos y condiciones que sean identificados en
el modelo conceptual, y permita así una correcta representación del sistema
hidrogeológico. 2ASPECTOS TEÓRICOS EN LA MODELACIÓN SOFTWARE RECOMENDADOS2TEORÍA
Y ESTADO DEL ARTE16 SERVICIO DE EVALUACIÓN AMBIENTALTabla 1: Ejemplos de
Software y códigos recomendados para su uso en Chile Tipo de flujo Flujo
saturado Flujo no saturado Flujo con densidad variable Flujos en acuíferos
fracturados y medios Kársticos Flujo saturado Flujo no saturadoObjetivo Software
/ Código GMS Groundwater Vistas Modelmuse Visual Modflow Feflow GMS (Femwater)
Hydrus 1D VS2DI Feflow GMS (Femwater) Seawat Sutra Feflow GMS Groundwater Vistas
Visual Modflow GMS Groundwater Vistas Modelmuse Visual Modflow Feflow GMS
(Femwater) Hydrus 1D-2D/3D VS2DI Aplicación práctica Aplicable a la mayoría de
los problemas prác - ticos en Chile, por ejemplo para flujo en los valles
transversales Puede ser importante de modelar para casos don- de sea relevante
representar la conexión entre la hidrología subterránea y superficial a través
de procesos como la infiltración y evapotranspiración Fundamental para la
representación correcta de la dinámica de flujos en salares y acuíferos costeros
Uso para condiciones muy particulares en las cuales existe una marcada
anisotropía del sis-tema que se busca representar Aplicable a la mayoría de los
problemas prác - ticos en Chile, por ejemplo para flujo en los valles
transversales Puede ser importante de modelar para casos don- de sea relevante
representar la conexión entre la hidrología subterránea y superficial a través
de procesos como la infiltración y evapotranspiraciónModelar flujo Modelar
transporte17 En el proceso para construir un modelo hidro- geológico se pueden
distinguir dos grandes eta - pas: la elaboración del modelo conceptual y la
elaboración del modelo numérico. La elaboración de un modelo conceptual debe ser
el punto de partida en la construcción de cualquier modelo hidrogeológico. En
esta etapa se representan en forma simplificada los ele-mentos más importantes
del sistema físico y su comportamiento, basándose en todos los antecedentes
técnicos disponibles (geología, hidrología, hidrogeoquímica e hidrogeología).
Asimismo, dependiendo de la cantidad y cali-dad de dichos antecedentes, quedan
definidos en esta etapa los alcances de la futura mode- lación, sus limitaciones
y la precisión esperada de los resultados.

---

## 15.  En cualquier caso, dicho

En cualquier caso, dicho problema debe ser abordado y la calidad de la so-lución
implementada puede ser evaluada a la hora de comparar el ingreso impuesto de
recarga y la recarga leída por el modelo (ver Figura 20). Por último, cabe
mencionar que un criterio de verificación útil para evitar inconsistencias en la
definición completa de la grilla consiste en confirmar la conexión de todas las
celdas del modelo numérico. Es importante destacar que existen sistemas di-
námicos donde nunca se alcanza una condición permanente y que sólo pueden ser
representa - dos mediante modelos en régimen transiente. Por otra parte, es
frecuente que los modelos de transporte se corran acoplados al respectivo modelo
de flujo en régimen permanente, dado que los efectos sobre la calidad del agua
se per - ciben típicamente a largo plazo y, por tanto, la estacionalidad -en
términos de cambios en las condiciones de flujo (velocidades por ejemplo)-
pierde relevancia. 6 Condiciones de bordeEl intervalo de tiempo considerado en
la mode - lación16 depende de los objetivos de ésta (por ejemplo corto plazo o
largo plazo) y de los fe - nómenos que se desea representar (algunos tienen
carácter estacional mientras que otros no).

---

## 17. Lo anterior

Sin embargo, en la práctica son comúnmente tratados como condiciones de borde
por lo que se incluyen como tales en esta Guía. El tipo de condición de borde
debe ser definido en concordancia a la dinámica del sistema, estable-cida en el
modelo conceptual. Su elección es de suma importancia en la construcción de un
modelo hidrogeológico, dado que permite definir los límites físicos del dominio
de modelación y, además, fija aspectos clave que inciden en su comportamiento.
Para efectos de esta Guía se clasifican las con- diciones de borde para un
modelo de flujo en dos categorías:• Condiciones impuestas: el modelador ingresa
directamente los flujos al sistema. • Condiciones calculadas: el modelo estima
los flujos a partir de variables dependientes y otros parámetros.

---

## 36. Esta

En este caso el rol de la modelación consiste en definir objetivamente, en base
a criterios cualitativos y cuantitativos, los indicadores de estado asociados a
los potenciales impactos so- bre el receptor, los criterios de decisión para im-
plementar las acciones y las características de diseño de las obras y/o acciones
que permitan cumplir los objetivos propuestos. Indicadores de estado: los
indicadores de es- tado corresponden a parámetros específicos (por ejemplo, el
nivel del agua subterránea) asociados a ciertos puntos de control ubi- cados de
tal forma de anticipar potenciales impactos. Criterios de decisión (umbrales):
Dado que el modelo debe ser capaz de representar el fun-cionamiento del sistema
hidrogeológico fren-te a diferentes condiciones, es posible deter - minar qué
condiciones en los indicadores de estado podrían dar cuenta de un comporta -
miento de las variables ambientales distinto al proyectado y, a partir de éstas
definir los criterios de decisión que permitan activar o desactivar las acciones
inmediatas necesarias para evitar la generación de impactos. Obras y/o acciones:
La utilización del modelo para diseñar las obras y/o acciones resulta im-
prescindible, ya que es posible simular el efec - to de éstas y, por lo tanto,
se puede cuantifi- car el efecto esperado y su velocidad de acción (tiempo de
respuesta). La información recopilada en el PSVA a lo largo del tiempo puede ser
utilizada para realizar mejoras en la conceptualización del sistema y actualizar
el modelo numé - rico.

---

## 37. Lo anterior permite reducir la in-

La frecuencia con la cual debería ser actualizado el modelo dependerá de cada
caso. 3OBRAS Y/O ACCIONES ASOCIADAS AL PLAN DE SEGUIMIENTO DE LAS VARIABLES
AMBIENTALES ACTUALIZACIÓN DEL MODELO Y DEL PLAN DE SEGUIMIENTO DE LAS VARIABLES
AMBIENTALES62 SERVICIO DE EVALUACIÓN AMBIENTALGLOSARIO Aguas subterráneas: aguas
que están ocultas en el seno de la tierra y no han sido alumbradas. Absorción:
disolución o mezcla de una sustancia en forma gaseosa, líquida o sólida, con
agua subterránea. Acuífero: formación geológica permeable susceptible de
almacenar agua en su interior y ceder parte de ella. Acuífero confinado: es
aquel en que el agua alojada en el interior de la zona saturada se encuentra a
una presión mayor que la atmosférica.

---

## 2. Las resoluciones de los modelos de elevación digital en

Las resoluciones de los modelos de elevación digital en general son suficientes
para la mayoría de los modelos hidrológicos, no obstante, si se requiere
analizar cuencas pequeñas y se cuenta con topografía de detalle, éstas pueden
ser trazadas gráficamente con mayor precisión. 322Una vez definidas las cuencas
hidrográficas afluentes al área del modelo hidrogeológico, es recomenda - ble
caracterizarlas en función de sus características geomorfológicas principales
tales como superficie, altura media, curvas hipsográficas, entre otras. La Tabla
6 de la Guía presenta un encabezado tipo para la caracterización de cuencas
hidrográficas en el marco de un modelo conceptual. En función de los objetivos
del modelo hidrogeológico, se debe evaluar si es necesario realizar análisis
actualizados de información hidrológica o si es posible utilizar información
disponible en estudios an-teriores. Dependiendo de los objetivos del modelo
hidrogeológico, puede ser necesario analizar información me- teorológica de
precipitaciones, temperatura, evaporación e información fluviométrica.

---

