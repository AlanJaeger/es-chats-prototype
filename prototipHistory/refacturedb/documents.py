from django.contrib.auth.models import User
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Document, Text, Integer, Nested
from django_elasticsearch_dsl import Index
from elasticsearch_dsl import Document, Date, Boolean, Text, InnerDoc, Object, Keyword, connections


from refacturedb.models import *

@registry.register_document
class MessageDocument(Document):
    room = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'contact': fields.TextField(),
        # Adicione outros campos relevantes do modelo Room aqui
    })

    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'username': fields.TextField(),
        # Adicione outros campos relevantes do modelo User aqui
    })
    
    contact = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        # Adicione outros campos relevantes do modelo Contact aqui
    })

    text = fields.TextField()
    seen = fields.BooleanField()

    class Index:
        name = 'message_text'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    class Django:
        model = MessageText
    
    def get_queryset(self):
        return MessageText.objects.all()
    
    def get_indexing_queryset(self):
        """Método para especificar quais objetos do modelo devem ser indexados."""
        return self.get_model().objects.all()
    
    def get_model(self):
        return MessageText  # Substitua com o nome do seu modelo
    
    def get_instances_from_related(self, related_instance):
        # Este método é usado para indexar objetos relacionados, se necessário
        return related_instance.messages.all()