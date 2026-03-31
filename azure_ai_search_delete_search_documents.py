import os
import json
import logging
from pathlib import Path
from typing import List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult, VectorizedQuery
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    EntityRecognitionSkill,
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
    SemanticSearch
)
from dotenv import load_dotenv
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console

logger = logging.getLogger()
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



def delete_documents_by_filename():
    try:
        target_filename = "UD0056_1_PiMonitor_User''s_Guide.pdf"
        
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            filter_str  =f"filename eq '{target_filename}'"

            logger.info(f"Filter: {filter_str}")

            results = search_client.search(
                search_text="*",
                filter=filter_str,
                include_total_count=True,
                select="filename,id"
            )

            docs_to_delete = []

            for r in results:
                docs_to_delete.append(
                    {"id": r["id"]}
                )

            if not docs_to_delete:
                pprint("[yellow]No documents found to delete.[/yellow]")
                return 
            
            print(docs_to_delete)
            
            delete_result = search_client.delete_documents(documents=docs_to_delete)

            pprint(f"[green]Deleted {len(docs_to_delete)} documents.[/green]")
            logger.info(f"Delete result: {delete_result}")

    except Exception as e:
        logger.error(f"Error deleting documents: {e}")

if __name__ == "__main__":
    delete_documents_by_filename()