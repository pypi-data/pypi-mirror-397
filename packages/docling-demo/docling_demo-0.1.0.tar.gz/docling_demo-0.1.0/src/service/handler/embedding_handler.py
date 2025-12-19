import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchField,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SearchIndex,
)
from openai import AzureOpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class EmbeddingHandler:

    def __init__(self):
        self.VECTOR_DIM = 1536
        self.INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_EMBEDDINGS = os.getenv("AZURE_OPENAI_EMBEDDINGS")
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_EMBEDDING_VERSION")
        self.AZURE_SEARCH_ENDPOINT = "https://test-ragq32.search.windows.net"
        self.AZURE_SEARCH_KEY = "gr5Ps9KMDVArm2ZIxvoPQoZcFY4IC59WcKxZFmI8vbAzSeDTLO84"

        self.index_client = SearchIndexClient(endpoint=self.AZURE_SEARCH_ENDPOINT, 
                                              credential = AzureKeyCredential(self.AZURE_SEARCH_KEY))
        
        self.search_client = SearchClient(index_name=self.INDEX_NAME,
                                        endpoint=self.AZURE_SEARCH_ENDPOINT, 
                                        credential = AzureKeyCredential(self.AZURE_SEARCH_KEY))
        
        self.openai_client = AzureOpenAI(api_key=self.AZURE_OPENAI_API_KEY,
                                         api_version=self.AZURE_OPENAI_VERSION,
                                         azure_endpoint=self.AZURE_OPENAI_ENDPOINT)
        self.upload_docs = []
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add embeddings to chunks
        Input: chunks from ChunkerHandler
        Output: chunks with content_vector added
        """
        for chunk in chunks:
            embedding = self._embed_text(chunk['content'])
            chunk['content_vector'] = embedding
        
        print(f"Embedded {len(chunks)} chunks.")
        return chunks
    
    def _embed_text(self, text: str):
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.AZURE_OPENAI_EMBEDDINGS
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            raise
    
    def upload_to_search(self, chunks: List[Dict]):
        """Upload chunks to Azure Search"""
        if not chunks:
            print("No chunks to upload.")
            return

        BATCH_SIZE = 50
        total_uploaded = 0
        
        for i in range(0, len(chunks), BATCH_SIZE):
            subset = chunks[i : i + BATCH_SIZE]
            try:
                result = self.search_client.upload_documents(documents=subset)
                succeeded = sum(1 for r in result if r.succeeded)
                total_uploaded += succeeded
                print(f"Uploaded batch: {succeeded}/{len(subset)} succeeded.")
            except Exception as e:
                print(f"Error uploading batch: {e}")
                raise
        
        print(f"Total documents uploaded: {total_uploaded}")
        return f"Uploaded {total_uploaded} documents."
    
    def create_index_if_not_exists(self):
        """Create index if it doesn't exist"""
        try:
            self.index_client.get_index(self.INDEX_NAME)
            print(f"Index '{self.INDEX_NAME}' already exists.")
        except:
            print(f"Creating index '{self.INDEX_NAME}'...")
            self._create_search_index(self.INDEX_NAME)
    
    def _create_search_index(self, index_name: str):
        fields = [
            SimpleField(name="chunk_id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=self.VECTOR_DIM,
                vector_search_profile_name="default",
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="default")],
            profiles=[
                VectorSearchProfile(
                    name="default",
                    algorithm_configuration_name="default",
                    vectorizer_name="default"
                )
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    vectorizer_name="default",
                    parameters=AzureOpenAIVectorizerParameters(
                        resource_url=self.AZURE_OPENAI_ENDPOINT,
                        deployment_name=self.AZURE_OPENAI_EMBEDDINGS,
                        model_name=self.AZURE_OPENAI_EMBEDDINGS,
                        api_key=self.AZURE_OPENAI_API_KEY
                    )
                )
            ]
        )
        
        new_index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)

        try:
            self.index_client.create_or_update_index(new_index)
            print(f"Index '{index_name}' created successfully.")
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            raise
        try:
            results = self.search_client.search("*", include_total_count=True)
            count = results.get_count()
            print(f"Total documents in index (via SDK): {count}")
            for doc in results:
                print(doc)
        except Exception as e:
            print(f"Error querying index: {e}")


