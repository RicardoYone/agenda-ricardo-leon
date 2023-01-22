from django.db import models

# Create your models here.


class Importancia(models.Model):
    # Va a ser un entero y ademas sera autoincrementada
    # NOTA : Sola,ente puede haber una columna autoincremetable
    # Field options ( las opciones que le podemos pasar a todos tipos de datos)
    id = models.AutoField(primary_key=True, null=False)  # OPCIONAL
    nombre = models.CharField(max_length=45, unique=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        # Se usa para cuanto trabajamos con herencia para poder pasar metadatos a la clace (informacion a la clace padre)
        # Sirve para cambiar el nombre de la tabla con la relacion al modelo
        db_table = 'importancias'


class Tarea(models.Model):
    # Si no indico la columna ID Django automaticamente me la creara, se suele agregar cuando queremos cambiar el nombre
    class CategoriaOpciones(models.TextChoices):
       # El primer valor es para cuando usemos formularios, y el segudndo es el valor que se almacenara en la base de datos.
        LISTADO = ('LISTADO', 'LISTADO')
        POR_HACER = ('POR_HACER', 'POR_HACER')
        FINALIZADO = ('FINALIZADO', 'FINALIZADO')
        CANCELADO = ('CANCELADO', 'CANCELADO')
    categoria = models.CharField(
        choices=CategoriaOpciones.choices, max_length=15, default='LISTADO')
    nombre = models.CharField(max_length=250, null=False)
    descripcion = models.TextField(null=False)
    fechaCaducidad = models.DateTimeField(db_column='fecha_caducidad')

    # RELACIONES !!!
    # on_delete > Significa que va a suceder cuando se intente eliminar la tabla que tiene tareas
    # CASCADE > Primero eliminara la Importnancia y luego eliminara todas las tareas de Importancia
    # PROTECT > Evitara la eliminaicon de la importancia mientras que tenga tareas ProtectError
    # RESTRICT > Evitara la eliminacion pero emitira un error en tipo RestrictError
    # SET_NULL > Lo elimina pero todas las tareas con importancia seteara en NULL
    # SET_DEFAULT > Se elimina pero tendremos que indicar un valor por defecto par aque sea reemplazado
    # DO_NOTHING > No toma ninguna accion, elimina importnaica pero aun conserva el ID eliminado (Es el mas peligroso de todos porque puede generar la incongruencia de datos)
    Importancia = models.ForeignKey(
        to=Importancia, db_column='importancia_id', on_delete=models.PROTECT)

    class Meta:
        db_table = 'tareas'


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=45, null=False, unique=True)

    class Meta:
        db_table = 'etiquetas'


class TareaEtiqueta(models.Model):
    # El parametro realated_name sirve para poder referenciar desde la clace donde estamos creando la relacion hacia todos sus HIJOS osea creara un atributo virutal en la clace TAREA para poder acceder a todas las etiquetas TAREASETIQUETAS , sino define su valor predeterminado sera el nombre del modelo con _set osea en este caso sera TAREAETIQUETA_SET
    tarea = models.ForeignKey(
        to=Tarea, db_column='tarea_id', on_delete=models.CASCADE, related_name='tareaEtiqueta')
    etiqueta = models.ForeignKey(
        to=Etiqueta, db_column='etiqueta_id', on_delete=models.CASCADE, related_name='etiquetaTarea') #tareaetiqueta_set

    class Meta:
        db_table = 'tareas_etiquetas'
