from django.apps import AppConfig
from django.conf import settings
from haystack import Pipeline, component
from haystack.utils import Secret
from haystack.components.builders import PromptBuilder, ChatPromptBuilder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator,OllamaGenerator
from haystack.components.generators import OpenAIGenerator
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.mongodb_atlas import MongoDBAtlasEmbeddingRetriever
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from haystack.components.converters import OutputAdapter

from .chat_template import PARAPHRASER,PARAPHRASER_JP

class PipelineRAG(Pipeline):
    def __init__(self,model,lang,provider="ollama"):
        
        if lang=="en":
            collection_name = "osaka_tourism_en"
        else:
            collection_name = "osaka_tourism_jp"

        document_store = MongoDBAtlasDocumentStore(
            database_name="keisuu",
            collection_name=collection_name,
            vector_search_index="vector_index",
            full_text_search_index="vector_index",
        )

        if provider == "ollama":
            k=5
        else:
            k=10
        retriever = MongoDBAtlasEmbeddingRetriever(document_store=document_store,top_k=k)
        if lang == "en":
            embedder = SentenceTransformersTextEmbedder()
        else:
            embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
        
        embedder.warm_up()

        self.pipeline = Pipeline()
        if lang=="en":
            self.pipeline.add_component("rephraser_builder",PromptBuilder(template=PARAPHRASER))
        else:
            self.pipeline.add_component("rephraser_builder",PromptBuilder(template=PARAPHRASER_JP))

        if provider=="ollama":
            self.pipeline.add_component("rephraser_llm",OllamaGenerator(model="llama3.2:1b",url=settings.OLLAMA,generation_kwargs={
                "num_predict":-2,
                "temperature":0.9,
            },timeout=1200))
        else:
            self.pipeline.add_component("rephraser_llm",OpenAIGenerator(model="deepseek-v3",api_key=Secret.from_token(settings.API_KEY),api_base_url=settings.URL))

        self.pipeline.add_component("list_to_str",OutputAdapter(template="{{generator[0]}}",output_type=str))
        self.pipeline.add_component("embedder",embedder)

        self.pipeline.add_component("retriever",retriever)
        self.pipeline.add_component("builder",ChatPromptBuilder(variables=["query","documents", "memories"], required_variables=["documents", "memories"]))

        if provider=="ollama":
            self.pipeline.add_component("llm",OllamaChatGenerator(model=model,url=settings.OLLAMA,generation_kwargs={
                "num_predict":-2,
                "temperature":0.9,
            },timeout=1200))
        else:
            self.pipeline.add_component("llm",OpenAIChatGenerator(model=model,api_base_url=settings.URL,api_key=Secret.from_token(settings.API_KEY)))

        self.pipeline.connect("rephraser_builder","rephraser_llm")
        self.pipeline.connect("rephraser_llm.replies","list_to_str")
        self.pipeline.connect("list_to_str","embedder")
        self.pipeline.connect("embedder","retriever")
        self.pipeline.connect("retriever","builder.documents")
        self.pipeline.connect("list_to_str","builder.query")
        self.pipeline.connect("builder","llm")

    def get_pipeline(self):
        return self.pipeline

class ProcessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'process'

    def ready(self):
        self.pipeline_llama = PipelineRAG(settings.MODEL_LLAMA,"en")
        self.pipeline_deepseek = PipelineRAG(settings.MODEL_DEEPSEEK,"en")

        self.pipeline_llama_jp = PipelineRAG(settings.MODEL_LLAMA,"jp")
        self.pipeline_deepseek_jp = PipelineRAG(settings.MODEL_DEEPSEEK,"jp")

        self.pipeline_llama_api = PipelineRAG(settings.LLAMAAPI_LLAMA,"en","llamaapi")
        self.pipeline_deepseek_api = PipelineRAG(settings.LLAMAAPI_DEEPSEEK,"en","llamaapi")

        self.pipeline_llama_api_jp = PipelineRAG(settings.LLAMAAPI_LLAMA,"jp","llamaapi")
        self.pipeline_deepseek_api_jp = PipelineRAG(settings.LLAMAAPI_DEEPSEEK,"jp","llamaapi")


    def llama(self):
        return self.pipeline_llama.get_pipeline()
    
    def deepseek(self):
        return self.pipeline_deepseek.get_pipeline()
    
    def llama_jp(self):
        return self.pipeline_llama_jp.get_pipeline()
    
    def deepseek_jp(self):
        return self.pipeline_deepseek_jp.get_pipeline()
    
    def llama_api(self):
        return self.pipeline_llama_api.get_pipeline()
    
    def deepseek_api(self):
        return self.pipeline_deepseek_api.get_pipeline()
    
    def llama_api_jp(self):
        return self.pipeline_llama_api_jp.get_pipeline()
    
    def deepseek_api_jp(self):
        return self.pipeline_deepseek_api_jp.get_pipeline()    