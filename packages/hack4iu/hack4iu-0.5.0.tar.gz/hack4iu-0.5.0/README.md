# hack4iu Academy Courses Library

Una biblioteca Python para consultar cursos de la academia hack4iu.

## Cursos disponibles:

-Introduccion a Linux [15 horas]
-Personalizacion de Linux [3 horas]
-Introduccion al Hacking [53 horas]

## Instalacion

Instala el paquete usando `pip3`:

```python3
pip3 install hack4iu
```

## Uso basico

### Listar todos los cursos

```Python
from hack4iu import list_courses

for course in list_courses():
    print(course)
```

### Obtener un curso por nombre

```Python
from hack4iu import get_course_by_name

course = get_course_by_name("Introducion a Linux")
print()
```

### Calcular duracion total de los cursos

```python3
from hack4iu.utils import total_duration

print(f"Duracion total: {total_duration()} horas")
```


