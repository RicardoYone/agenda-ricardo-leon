from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import (ListAPIView,
                                     ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     CreateAPIView
                                     )
from .serializers import (PruebaSerializer,
                          ImportanciaSerializer,
                          ImportanciaSerializerRUD,
                          TareaSerializer,
                          TareaConImportanciaSerializer,
                          EtiquetaSerializer,
                          TareaEtiquetaSerializer,

                          )
from .models import Importancia, Tarea, Etiqueta, TareaEtiqueta
# Con esto podemos utilizar la conexion actual a nuestra base de datos, sin la necesidad de crear una nueva conexion y rebalsar el numero de conexion maximas permitidas
from django.db import connection
from datetime import datetime
from rest_framework import status
from pytz import utc
# Tipado > Indicar a dterminadas variables su tipo de dato correspondiente


@api_view(http_method_names=['GET', 'POST'])
def endpointInicial(request: Request):
    print(request.method)
    # request > Sera toda la informacion enviada por el cliente
    if request.method == 'GET':
        return Response(data={
            'message': 'Bienvenido a mi API c:'
        }, status=200)

    elif request.method == 'POST':
        print(request.data)
        return Response(data={
            'message': 'Se creo la informacion correctamente'
        })


class PruebaApiView(ListCreateAPIView):
    # 2 atributos : queryset y serializer_class
    queryset = [
        {
            'id': 1,
            'nombre': 'eduardo',
            'apellido': 'de rivero'
        },
        {
            'id': 2,
            'nombre': 'fiorella',
            'apellido': 'marquez'
        }]
    serializer_class = PruebaSerializer

    def post(self, request: Request):
        # Si quisieramos modificar el funcionamiento automatico que nos brinda las vistas genericas lo podemos hacer declarando el metodo con el mismo nombre del metodo que queremos modificar
        data = self.serializer_class(data=request.data)
        validacion = data.is_valid()
        print(validacion)

        if validacion == True:
            # La data para guardar en la BD
            print(data.validated_data)
            # La data que sera devuelta para el usuario
            print(data.data)

            return Response(data={
                'message': 'Prueba creada exitosamente'
            }, status=201)
        else:
            return Response(data={
                'message': 'Error al crear la prueba',
                'content': data.errors
            }, status=400)


class ImportanciasView(ListCreateAPIView):
    queryset = Importancia.objects.all()  # SELECT * FROM importancia;
    serializer_class = ImportanciaSerializer

    def get_queryset(self):
        # SELECT * FROM importancias where delete = false;
        return self.queryset.filter(deleted=False).all()

    def get(self, request: Request):
        instancias = self.get_queryset()
        # print(instancias[0])
        for instancia in instancias:
            print(instancia.nombre)
        # Cuando tenemos ya la informacion de la base de datos entonces seran isntancias (registros), en cambio cuando tenemos la informacion a guardar en la DB y queremos validar que este correcto lo pasaremos mediante data, intance espera uan o varias intancias, data espera informacion
        data_serializada = self.serializer_class(
            instance=instancias, many=True)

        return Response({
            'message': 'Las instancias son ',
            'content': data_serializada.data
        })

    def post(self, request: Request):
        informacion = request.data  # Informacion extraida del doby
        dataASerializar = self.serializer_class(data=informacion)

        dataASerializar.is_valid(raise_exception=True)

        # Guardar la informacion en la base de datos
        nuevaImportancia = dataASerializar.save(data_validada=request.data)

        # ###

        # #Primera forma de guardado de la informacion en la base de datos usando el modelo directamente
        # infoImportancia={'nombre':'Ejemplo'}
        # Importancia.objects.create(**infoImportancia)

        # # Segunda forma
        # nuevaImportancia = Importancia(nombre = 'Ejemplo2')
        # nuevaImportancia.save()

        # ###

        return Response({
            'message': 'Importancia creada exitosamente',
            'content': self.serializer_class(instance=nuevaImportancia).data
        }, status=201)


# GET, PUT , DELETE
class ImportanciaView(RetrieveUpdateDestroyAPIView):
    queryset = Importancia.objects.all()
    serializer_class = ImportanciaSerializerRUD

    def validarImportancia(self, pk):
        # select * from importancias where id = ... and deleted = faLse  LIMIT 1;
        resultado = Importancia.objects.filter(id=pk, deleted=False).first()

        if resultado is None:
            return Response(data={
                'message': 'La importancia no existe',
                'content': None,
            }, status=404)
        return resultado

    def get(self, request, pk):
        # Si modifico el nombre en la ruta entonces tmb lo tendre que modificar como parametro del metodo
        print(pk)
        resultado = self.validarImportancia(pk)

        if isinstance(resultado, Response):
            return resultado
        else:
            # Aca enviamos la instnacia para transformar la fata a una informacion que el cliente la pueda entender
            dataSerializada = self.serializer_class(instance=resultado).data

            return Response(data={
                'message': None,
                'content': dataSerializada
            })

    def delete(self, request, pk):
        resultado = self.validarImportancia(pk)

        if isinstance(resultado, Response):
            return resultado
        else:
            resultado.deleted = True
            resultado.save()

            return Response(data={
                'message': 'Importancia eliminada exitosamente',
                'content': None,
            })

    def update(self, request, pk):
        resultado = self.validarImportancia(pk)

        if isinstance(resultado, Response):
            return resultado
        else:
            # Pasamos la informacion enviada por el body hacia el serializador
            dataSerializada = self.serializer_class(data=request.data)
            # Validamos que la inforamcion sea valida
            dataSerializada.is_valid(raise_exception=True)
            # Aca se actualiza la informacion de la importancia
            # Retorna la instancia actualizada
            importanciaActualizada = dataSerializada.update(
                resultado, dataSerializada.validated_data)

            # Retornamos la importancia actualizada
            return Response(data={
                'message': 'Importancia actualizada exitosamente',
                # dataSerializada.data #Va a ser la informacion que e pasado al momento de llamar al serializador
                'content': self.serializer_class(instance=importanciaActualizada).data
            })


class TareasView(ListCreateAPIView):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer

    def post(self, request: Request):
        dataSerializada = self.serializer_class(data=request.data)
        dataSerializada.is_valid(raise_exception=True)

        # Validar si esa importancia existe (deleted no es true)
        # Al momento de hacer la validacion del serializadro tmb hace labusqueda de las llaves foraneas, es decir, valida que esas FK existan en la DB,  es por elllo que no tenemos que volver a hacer la busqueda de la importancia en la DB.
        importancia = dataSerializada.validated_data.get('importancia')
        # print(dataSerializada.validated_data)
        print(importancia.deleted)

        if importancia.deleted == True:
            return Response(data={
                'message': 'Importancia no existe'
            }, status=400)

        fechaHoy = utc.localize(datetime.now().utcnow())
        fechaCaducidad = dataSerializada.validated_data.get('fechaCaducidad')

        if fechaHoy > fechaCaducidad:
            return Response(data={
                'message': 'No puede haber tareas con fecha de caducidad menor a la actual'
            }, status=status.HTTP_400_BAD_REQUEST)

        nuevaTarea = dataSerializada.save()

        return Response(data={
            'message': 'Tare creada exitosamente',
            'content': self.serializer_class(instance=nuevaTarea).data
        }, status=status.HTTP_201_CREATED)

    def get(self, request: Request):
        tareas = self.get_queryset()
        dataSerializada = TareaConImportanciaSerializer(
            instance=tareas, many=True)
        
        return Response(data={
            'message': None,
            'content': dataSerializada.data,
        })


class EtiquetasView(ListCreateAPIView):
    queryset = Etiqueta.objects.all()
    serializer_class = EtiquetaSerializer


class TareaEtiquetasView(ListCreateAPIView):
    queryset = TareaEtiqueta.objects.all()
    serializer_class = TareaEtiquetaSerializer


@api_view(http_method_names=['GET'])
def usandoVista(request):
    # Uso de RAW QUERIES
    # Con la conexion usaremos un cursor
    cursor = connection.cursor()
    # Ejecutaremos una query sin utilizar los metodos definidos
    cursor.execute('SELECT * FROM listar_etiquetas_con_la_letra_A;')
    # Indicamos que solo vamos a querer la primera coincidencia
    # respuesta = cursor.fetchone()

    respuesta = cursor.fetchall()
    print(respuesta)
    # Las raw queries NUNCa me devolveran los nombres de las columnas, solamente devolveran una tupla con todos sus registros (a su vez cada registro sera tmb una tupla)
    for registro in respuesta:
        diccionario = {
            'id': registro[0],
            'nombre': registro[1],
            'estado': bool(registro[2])
        }
        print(diccionario)

    return Response(data={
        'message': 'Se uso la vista'
    })
