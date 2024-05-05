import io
import os
from elasticsearch import Elasticsearch
from transformers import BertTokenizer, BertModel
from nltk.corpus import wordnet as wn
import torch
from sklearn.metrics.pairwise import cosine_similarity
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload 
import chardet

# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200'], basic_auth=('elastic', '123456'))

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')
bert_model.eval()

# Set index name
index_name = 'ebook'

# Function to embed text using BERT
def embed_text(text):
    input_ids = tokenizer.encode(text, add_special_tokens=True, max_length=512, truncation=True)
    with torch.no_grad():
        outputs = bert_model(torch.tensor([input_ids]))
        embedded_text = torch.mean(outputs[0], dim=1).numpy().tolist()[0]  # Mean pooling
    return embedded_text
    
# Function to expand query with WordNet synonyms
def expand_query_with_synonyms(query):
    synonyms = []
    for synset in wn.synsets(query):
        for lemma in synset.lemmas():
            synonyms.append(lemma.name())
    return list(set(synonyms))

# Function to index documents
def index_documents(file_list, index_name , drive_service):
    for file in file_list:
        pdf_title = file['name']
        pdf_id = file['id']
        pdf_content = download_pdf_content(pdf_id, drive_service)  # Assuming you have a function to download PDF content
        if pdf_content:
            embedded_text = embed_text(pdf_content)  # Assuming you have a function to embed text using BERT
            document_body = {
                'filename': pdf_title,
                'text': pdf_content,
                'text_vector': embedded_text,
                'fileId': pdf_id
            }
            try:
                es.index(index=index_name, body=document_body)
                print(f"Indexed document: {pdf_title}")
            except Exception as e:
                raise RuntimeError(f"Error occurred while indexing {pdf_title}: {e}")
        else:
            raise RuntimeError(f"Failed to download PDF content for {pdf_title}")
        
def index_one_document(file_id,file_list, index_name, drive_service):
    try:
        for file in file_list:
            pdf_title = file['name']
            pdf_id = file['id']
            if pdf_id == file_id:
                break
        pdf_content = download_pdf_content(file_id, drive_service)
        
        if pdf_content:
            embedded_text = embed_text(pdf_content)
            document_body = {
                'filename': pdf_title,
                'text': pdf_content,
                'text_vector': embedded_text,
                'fileId': file_id
            }
            try:
                es.index(index=index_name, body=document_body)
                print(f"Indexed document: {pdf_title}")
            except Exception as e:
                raise RuntimeError(f"Error occurred while indexing {pdf_title}: {e}")
        else:
            raise RuntimeError(f"Failed to download PDF content for {pdf_title}")
    except Exception as e:
        raise RuntimeError(f"Error occurred while indexing eBook: {e}")


def download_pdf_content(file_id , drive_service):
    try:
        file = drive_service.files().get_media(fileId=file_id).execute()
        
        # Try decoding with different codecs
        for codec in ['utf-8', 'latin-1']:  # You can add more codecs to try
            try:
                content = file.decode(codec)
                return content
            except UnicodeDecodeError:
                continue
        
        # If all codecs fail, try using chardet to detect the encoding
        encoding = chardet.detect(file)['encoding']
        if encoding:
            content = file.decode(encoding)
            return content
        
        # If chardet cannot detect the encoding, print an error message
        raise RuntimeError(f"Failed to decode PDF content for file ID {file_id}: Unknown encoding")
        return None    
    except Exception as e:
        raise RuntimeError(f"Error occurred while downloading PDF content for file ID {file_id}: {e}")

def semantic_search(query):
    try:
        combined_query = query + ' ' + ' '.join(expand_query_with_synonyms(query))
        
        # Embed combined query using BERT
        query_vector = embed_text(combined_query)
        # Prepare Elasticsearch query
        es_query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        }
        # Execute Elasticsearch query
        search_results = es.search(index=index_name, body=es_query)
        # Return search results
        unique_hits = []
        encountered_texts = set()
        for hit in search_results['hits']['hits']:
            if '_source' in hit and 'filename' in hit['_source']:
                text_title = hit['_source']['filename']
                if text_title not in encountered_texts:
                    unique_hits.append(hit)
                    encountered_texts.add(text_title)
        return unique_hits
        
    except Exception as e:
        raise RuntimeError(f"Error occurred during semantic search: {e}")

def authenticate_drive_service():
    # Initialize the Google Drive API
    SCOPS = ['https://www.googleapis.com/auth/drive']
    # Path to the JSON file containing your client credentials
    SERVICE_ACCOUNT_FILE = 'search/credential.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE , scopes=SCOPS)
    return credentials

def index_eBooks():
    credentials = authenticate_drive_service()
    drive_service = build('drive', 'v3', credentials=credentials)
    # Set the index name
    index_name = 'ebook'

    # Specify the folder ID of the desired folder on Google Drive
    folder_id = '17iMoJjzjuOvF0giYCGZjfLZuoD5hp5NI'
    # Retrieve files from the folder
    results = drive_service.files().list(q=f"'{folder_id}' in parents and mimeType='application/pdf'").execute()
    file_list = results.get('files', [])
    # Index documents
    index_documents(file_list, index_name,drive_service)


def index_one_ebook(file_id):
    credentials = authenticate_drive_service()
    drive_service = build('drive', 'v3', credentials=credentials)
    index_name = 'ebook'
    # Specify the folder ID of the desired folder on Google Drive
    folder_id = '17iMoJjzjuOvF0giYCGZjfLZuoD5hp5NI'
    # Retrieve files from the folder
    results = drive_service.files().list(q=f"'{folder_id}' in parents and mimeType='application/pdf'").execute()
    file_list = results.get('files', [])

    index_one_document(file_id,file_list, index_name, drive_service)

# Perform semantic search
def search_eBook(query):
    results = semantic_search(query)
    return results
