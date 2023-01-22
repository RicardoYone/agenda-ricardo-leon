from rest_framework import serializers
from .models import Importancia, Tarea, Etiqueta, TareaEtiqueta


class PruebaSerializer(serializers.Serializer):
    # Ahora vamos a definir la informacion que va a llegar y/o salir
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(
        required=True, trim_whitespace=True, max_length=20)
    apellido = serializers.CharField(
        required=True, trim_whitespace=True, max_length=15)
    password = serializers.CharField(write_only=True)

    def create(self, data_validada):
        print('Aca se debera de guardar la info en la BD')
        print(data_validada)
        # Aca se deberia de retorna esa informacion guardad en la BD
        return


class ImportanciaSerializer(serializers.ModelSerializer):

    def save(self, data_validada):
        # Modifico el nombre de la data_validada y la convierto en mayusculas
        data_validada['nombre'] = self.validated_data.get('nombre').lower()
        nuevaImportancia = Importancia.objects.create(**self.validated_data)
        return nuevaImportancia

    class Meta:
        model = Importancia  # Para poder setear todos los fields de mi modelo  en el serializador
        # fields > Sirve para idnicar que coluumnas del modelo vamos a utilizar en este serializer
        # fields = '__all__'
        # fields=['id','nombre'] #Restringiendo que la columna delted ya no se va a utilizar
        # Tambien podemos definir el atribututo eclude en el cual se define las columnas que no se quiere mostrar
        exclude = ['deleted']
        # NOTA : No puede ir declados los atributos fields y eclude al mismo tiempo o es uno o es el otro ... !


class ImportanciaSerializerRUD(serializers.ModelSerializer):
    class Meta:
        model = Importancia
        fields = '__all__'


class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'


class ImportanciaSinDeletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Importancia
        exclude = ['deleted']


class TareaEtiquetaConEtiquetasSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaEtiqueta
        # fields = '__all__'
        exclude = ['tarea','id']
        depth = 1
        # extra_kwargs = {
        #     'tarea': {
        #         'write_only': True
        #     }
        # }


class TareaConImportanciaSerializer(serializers.ModelSerializer):
    # Anidamiento de serializadores (nested serializer)
    # Si nosotors queremos utilizar un serializardor personalizado con las columnas que queremos mostrar entonces en vez de utilizar el DEPTH podemos llamar el atributo que es la FK y asignarlo otro serializador, ademas, si queremos cambiar el nombre de ese atributo por troo, entonces en serializador debemos de colocar el parametro SOURCE con el nombre del atributo FK
    # importanciaALaQuePertenece = ImportanciaSinDeletedSerializer(
    #     source='importancia')
    importancia = ImportanciaSinDeletedSerializer()
    etiquetas = TareaEtiquetaConEtiquetasSerializer()

    class Meta:
        model = Tarea
        fields = '__all__'
        # detph > es el nivel que nosostros queremos ingresar desde este modelo hacia los demas, esto solamente servira para las relaciones donde tengamos la FK > PK ,osea solamente a la relaciones en la cual este modelo tenga FK (llaves foraneas)
        # depth = 1


class EtiquetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etiqueta
        fields = '__all__'


class TareaEtiquetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaEtiqueta
        fields = '__all__'
