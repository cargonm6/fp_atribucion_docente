# fp_atribucion_docente

Aplicación para obtener la atribución docente del profesorado de ciclos formativos, relacionando los módulos de una
especialidad desde la web de TodoFP.

## Funcionamiento

El programa recurre a la librería BeautifulShop para realizar una prospección del sitio web https://www.todofp.es/,
página oficial del Ministerio de Educación, Formación Profesional y Deportes de España.

La búsqueda de atribución docente se realiza a partir de un _keyword_, que se corresponde con una parte o todo el campo
de texto utilizado para referir a las diferentes especialidades del profesorado asociado a los cuerpos:

- Catedráticos/as (CAT)
- Profesores/as de Educación Secundaria (PES)
- Profesores/as Técnicos de Formación Profesional (PTFP), cuerpo a extinguir

El valor de _keyword_ se puede dejar por defecto (valor sugerido) o ser modificado al inicio del programa, introduciendo
una cadena de texto.

## Resultado

La aplicación devuelve un fichero en formato CSV, como cadena de texto separada por comas y en formato UTF-8. El título
del fichero será idéntico al _keyword_ introducido al inicio del programa, o su valor por defecto.