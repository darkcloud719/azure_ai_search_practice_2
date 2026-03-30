"""
FILE: azure_ai_search_vector_search.py
DESCRIPTION:
    This script demonstrates how to use Azure AI Search with vector search capabilities. It includes functions to create an index,
    upload documents with vector embeddings, and perform various types of searches including similarity search, cross-field search,
    multi-vector search, hybrid search, and semantic hybrid search. The script uses the Azure Search SDK for Python and OpenAI's API
    to generate embeddings for the documents. The results of the searches are displayed in a formatted table using the Rich Library.
USAGE:
    1. Ensure you have the necessary environment variables set in a .env file:
        AZURE_SEARCH_SERVICE_ENDPOINT=<your-azure-search-service-endpoint>
        AZURE_SEARCH_API_KEY=<your-azure-search-api-key>
        AZURE_OPENAI_API_KEY=<your-azure>
        AZURE_OPENAI_API_VERSION=<your-azure-openai-api-version>
        AZURE_OPENAI_API_ENDPOINT=<your-azure-openai-api-endpoint>
        AZURE_OPENAI_DEPLOYMENT_EMBEDDING=<your-azure-openai-deployment-name-for-embedding>
    2. Run the script to create the index, upload documents, and perform searches. You can uncomment the desired function calls in the main
         block to execute specific operations.
    3. The search results will be displayed in the console in a tabular format.
"""
import os, json, logging, sys, openai 
from openai import AzureOpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, SearchIndexingBufferedSender
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType, QueryCaptionResult, QueryAnswerResult, VectorizedQuery, VectorizableTextQuery, VectorFilterMode
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    EntityRecognitionSkill,
    SentimentSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
    SearchableField,
    IndexingParameters,
    SearchIndexerDataSourceConnection,
    IndexingParametersConfiguration,
    IndexingSchedule,
    CorsOptions,
    SearchIndexer,
    FieldMapping,
    ScoringProfile,
    ComplexField,
    ImageAnalysisSkill,
    OcrSkill,
    VisualFeature,
    TextWeights,
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters
)
from typing import List
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from pathlib import Path

# --------------------------------------------------------------------------
# Load environment variables from .env file
# --------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

console_handler = RichHandler()
console_handler.setLevel(logging.WARNING)

file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

console = Console()

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "azure-ai-search-vector-index"

openai.api_key = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
openai.azure_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")

def print_search_results(results):
    table = Table(show_header=True, header_style="bold magenta", title="Search Results")
    table.add_column("Id", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Content", style="white")
    table.add_column("Title_vector", style="yellow")
    table.add_column("Content_vector", style="yellow")

    for r in results:
        table.add_row(
            str(r.get("id", "")),
            r.get("title",""),
            r.get("category",""),
            r.get("content","")[:100] + "..." if r.get("content","") else "",
            str(r.get("titleVector",""))[:10] + "..." if r.get("titleVector", "") else "",
            str(r.get("contentVector",""))[:10] + "..." if r.get("contentVector", "") else ""
        )

    console.print(table)

def _delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.delete_index(index_name)
            pprint(f"[yellow]Index '{index_name}' deleted successfully.[/yellow]")
    except Exception as ex:
        pprint(f"[red]Error deleting index '{index_name}': {ex}[/red]")

def _create_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="category", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SearchField(
                    name="titleVector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="my-vector-search-profile"
                ),
                SearchField(
                    name="contentVector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="my-vector-search-profile"
                )
            ]

            vector_search = VectorSearch(
                profiles=[VectorSearchProfile(name="my-vector-search-profile", algorithm_configuration_name="my-hnsw-algorithm")],
                algorithms=[HnswAlgorithmConfiguration(name="my-hnsw-algorithm")]
            )

            scoring_profiles:List[ScoringProfile] = []
            scoring_profile = ScoringProfile(
                name="my-scoring-profile",
                text_weights=TextWeights(weights={"title": 3, "category":1, "content": 1})
            )

            scoring_profiles.append(scoring_profile)
            cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
            suggester = [{"name":"sg", "source_fields":["title", "content"]}]

            semantic_config = SemanticConfiguration(
                name="my-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    keywords_fields=[SemanticField(field_name="category")],
                    content_fields=[SemanticField(field_name="content")]
                )
            )

            semantic_search = SemanticSearch(configurations=[semantic_config])

            with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
                index = SearchIndex(
                    name=index_name,
                    fields=fields,
                    cors_options=cors_options,
                    semantic_search=semantic_search,
                    vector_search=vector_search
                )

                resutl = search_index_client.create_index(index)
                pprint(f"[green]Index '{index_name}' created successfully.[/green]")

    except Exception as ex:
        pprint(f"[red]Error creating index '{index_name}': {ex}[/red]")
        logger.error(f"Error creating index '{index_name}': {ex}")

def export_embeddings_to_json():
    try:
        path = Path.cwd() / "text-sample.json"
        with open(path, "r", encoding="utf-8") as file:
            input_data = json.load(file)

            titles = [item["title"] for item in input_data]
            contents = [item["content"] for item in input_data]
            titles_response = openai.embeddings.create(input=titles, model=os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING"))
            titles_embeddings = [item.embedding for item in titles_response.data]
            content_response = openai.embeddings.create(input=contents, model=os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING"))
            content_embeddings = [item.embedding for item in content_response.data]

            for i, item in enumerate(input_data):
                title = item["title"]
                content = item["content"]
                item["titleVector"] = titles_embeddings[i]
                item["contentVector"] = content_embeddings[i]

            output_path = Path.cwd() / "text-sample-with-embeddings.json"
            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(input_data, output_file, ensure_ascii=False, indent=4)
    except Exception as ex:
        pprint(f"[red]Error exporting embeddings to json: {ex}[/red]")
        logger.error(f"Error exporting embeddings to json: {ex}")

def upload_documents():
    try:
        output_path = Path.cwd() / "text-sample-with-embeddings.json"

        with open(output_path, "r", encoding="utf-8") as file:
            documents = json.load(file)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            reuslt = search_client.upload_documents(documents=documents)
            pprint(f"[green]Documents uploaded successfully.[/green]")
    except Exception as ex:
        pprint(f"[red]Error uploading documents: {ex}[/red]")
        logger.error(f"Error uploading documents: {ex}")

def upload_documents_by_indexingbufferedsender():
    try:
        output_path = Path.cwd() / "text-sample-with-embeddings.json"
        with open(output_path, "r", encoding="utf-8") as file:
            documents = json.load(file)

        with SearchIndexingBufferedSender(
            endpoint=service_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(key)
        ) as batch_client:
            batch_client.upload_documents(documents=documents)

        pprint(f"[green]Documents uploaded successfully using SearchIndexingBufferedSender.[/green]")
    except Exception as ex:
        pprint(f"[red]Error uploading documents using SearchIndexingBufferedSender: {ex}[/red]")
        logger.error(f"Error uploading documents using SearchIndexingBufferedSender: {ex}")

def search_documents_by_similarity():

    try:
        query = "tools for software development"
        embedding = openai.embeddings.create(
            input=query,
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING")
        ).data[0].embedding

        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=3,
            fields="contentVector"
        )

        with SearchClient(service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            result = search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=["title","content","category","titleVector","contentVector"]
            )

            all_records = list(result)
            # pprint(all_records)
            print_search_results(all_records)
    except Exception as ex:
        pprint(f"[red]Error searching documents by similarity: {ex}[/red]")
        logger.error(f"Error searching documents by similarity: {ex}")


def search_documents_by_cross_fields():
    try:
        query = "tools for software development"
        embedding = openai.embeddings.create(
            input=query,
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING")
        ).data[0].embedding

        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=3,
            fields="titleVector,contentVector"
        )

        # pprint(vector_query)

        with SearchClient(service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=["title","content","category","titleVector","contentVector"]
            )

            all_records = list(results)
            
            print_search_results(all_records)

    except Exception as ex:
        pprint(f"[red]Error searching documents by cross fields: {ex}[/red]")
        logger.error(f"Error searching documents by cross fields: {ex}")


def search_documents_by_multi_vector():
    try:
        query1 = "tools for software development"
        query2 = "artificial intelligence in software development"

        embedding1 = openai.embeddings.create(
            input=query1,
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING")
        ).data[0].embedding

        embedding2 = openai.embeddings.create(
            input=query2,
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING")
        ).data[0].embedding

        vector_query_1 = VectorizedQuery(
            vector=embedding1,
            k_nearest_neighbors=3,
            fields="titleVector"
        )

        vector_query_2 = VectorizedQuery(
            vector=embedding2,
            k_nearest_neighbors=3,
            fields="contentVector"
        )

        with SearchClient(service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                search_text=None,
                vector_queries=[vector_query_1, vector_query_2],
                select=["title","content","category","titleVector","contentVector"],
                top=2
            )

            all_records = list(results)
            print_search_results(all_records)

    except Exception as ex:
        pprint(f"[red]Error searching documents by multi vector: {ex}[/red]")
        logger.error(f"Error searching documents by multi vector: {ex}")

def hybrid_search_documents():
    try:
        query = "scalable storage solutions"

        embedding = openai.embeddings.create(
            input=query,
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING")
        ).data[0].embedding


        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=3,
            fields="contentVector"
        )

        with SearchClient(service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SIMPLE,
                search_text=query,
                vector_queries=[vector_query],
                select=["title","content","category","titleVector","contentVector"],
                top=3
            )

            all_records = list(results)

            print_search_results(all_records)

    except Exception as ex:
        pprint(f"[red]Error performing hybrid search: {ex}[/red]")
        logger.error(f"Error performing hybrid search: {ex}")

def semantic_hybrid_search_documents():
    try:
        query = "What is azure search ?"

        embedding = openai.embeddings.create(
            input=query,
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING")
        ).data[0].embedding

        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=5,
            fields="contentVector,titleVector"
        )

        with SearchClient(service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SEMANTIC,
                semantic_configuration_name="my-semantic-config",
                query_caption=QueryCaptionType.EXTRACTIVE,
                query_answer=QueryAnswerType.EXTRACTIVE,
                search_text=query,
                vector_queries=[vector_query],
                select=["title","content","category","titleVector","contentVector"],
                top=1
            )

            all_records = list(results)
            print_search_results(all_records)


    except Exception as ex:
        pprint(f"[red]Error performing semantic hybrid search: {ex}[/red]")
        logger.error(f"Error performing semantic hybrid search: {ex}")



if __name__ == "__main__":
    # _delete_index()
    # _create_index()
    # export_embeddings_to_json()
    # upload_documents()
    # search_documents_by_similarity()
    # search_documents_by_cross_fields()
    # search_documents_by_multi_vector()
    # hybrid_search_documents()
    semantic_hybrid_search_documents()

        








