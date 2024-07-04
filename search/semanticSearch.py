import io
import os
from elasticsearch import Elasticsearch
from transformers import BertTokenizer, BertModel
from nltk.corpus import wordnet as wn
from google.oauth2 import service_account
import torch
from PIL import Image
import pytesseract
import fitz
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload 
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class semanticSearch:
    def __init__(self, es_host='http://localhost:9200', es_user='elastic', es_password='123456', index_name='ebook', tesseract_path=None):
        self.es = Elasticsearch([es_host], basic_auth=(es_user, es_password), timeout=400)
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.bert_model.eval()
        self.index_name = index_name
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    def embed_text(self, text):
       return self.model.encode(text, convert_to_tensor=True)

    def expand_query_with_synonyms(self, query):
        synonyms = set()
        for synset in wn.synsets(query):
            synonyms.update(synset.lemma_names())
        genai.configure(api_key="AIzaSyA48Xv_OzNzB-suQBU0pwsnTlN2Equ-_GU")

        # Create the model
        # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
        generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
        )

        chat_session = model.start_chat(
        history=[
        ]
        )
        response = chat_session.send_message(f"What are some words related to {query} and the response should be a list?")
        result = response.text+ " ".join(list(synonyms)) +" "+ query
        return result

    def pad_or_truncate(self, tensor, expected_dim):
        current_dim = tensor.size(0)
        if current_dim == expected_dim:
            return tensor
        elif current_dim < expected_dim:
            padding = torch.zeros(expected_dim - current_dim)
            return torch.cat((tensor, padding))
        else:
            return tensor[:expected_dim]

    def index_documents(self, file_list, drive_service):
        for file in file_list:
            pdf_title = file['name']
            pdf_id = file['id']
            try:
                pdf_content = self.download_pdf_content(pdf_id, drive_service)
                if pdf_content:
                    text_to_embed = f"{pdf_title}\n{pdf_content}"
                    embedded_text = self.embed_text(text_to_embed)
                    padded_text_vector = self.pad_or_truncate(embedded_text, expected_dim=768)
                    embedded_text_list = padded_text_vector.tolist()

                    document_body = {
                        'filename': pdf_title,
                        'text': pdf_content,
                        'text_vector': embedded_text_list,
                        'fileId': pdf_id
                    }

                    self.es.index(index=self.index_name, body=document_body)
                    # print(f"Indexed document: {pdf_title}")
                else:
                    raise RuntimeError(f"Failed to download PDF content for {pdf_title}")
            except Exception as e:
                raise RuntimeError(f"Error occurred while indexing {pdf_title}: {e}")
    def index_one_document(self,file_id, file_list,drive_service):
        try:
            for file in file_list:
                pdf_title = file['name']
                pdf_id = file['id']
                if pdf_id == file_id:
                    break
            
            pdf_content = self.download_pdf_content(file_id, drive_service)
            
            if pdf_content:
                # Concatenate title and content
                text_to_embed = f"{pdf_title}\n{pdf_content}"
                
                # Embed text using BERT
                embedded_text = self.embed_text(text_to_embed)
                padded_text_vector = self.pad_or_truncate(embedded_text, expected_dim=768)
                # Convert embedded_text tensor to list of floats
                embedded_text_list = padded_text_vector.tolist()
                
                document_body = {
                    'filename': pdf_title,
                    'text': pdf_content,
                    'text_vector': embedded_text_list,  # Use the converted list
                    'fileId': file_id
                }
                try:
                    self.es.index(index=self.index_name, body=document_body)
                    # print(f"Indexed document: {pdf_title}")
                except Exception as e:
                    raise RuntimeError(f"Error occurred while indexing {pdf_title}: {e}")
            else:
                raise RuntimeError(f"Failed to download PDF content for {pdf_title}")
        
        except Exception as e:
            raise RuntimeError(f"Error occurred while indexing eBook: {e}")
        
    def download_pdf_content(self, file_id, drive_service):
        try:
            request = drive_service.files().get_media(fileId=file_id)
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            file_stream.seek(0)
            document = fitz.open(stream=file_stream, filetype='pdf')
            pdf_content = ''

            for page_num in range(len(document)):
                page = document.load_page(page_num)
                page_text = page.get_text()

                if page_text:
                    pdf_content += page_text + '\n'
                else:
                    pix = page.get_pixmap()
                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image_text = pytesseract.image_to_string(image)
                    pdf_content += image_text + '\n'

            document.close()

            return pdf_content.strip()
        
        except Exception as e:
            raise RuntimeError(f"Error occurred while downloading PDF content for file ID {file_id}: {e}")

    def semantic_search(self, query):
        try:
            combined_query = self.expand_query_with_synonyms(query)
            query_vector = self.embed_text(combined_query)
            padded_text_vector = self.pad_or_truncate(query_vector, expected_dim=768)
            query_vector = padded_text_vector.tolist()

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

            search_results = self.es.search(index=self.index_name, body=es_query)
            unique_hits = []
            encountered_texts = set()

            for hit in search_results['hits']['hits']:
                if '_source' in hit and 'fileId' in hit['_source']:
                    text_title = hit['_source']['fileId']
                    if text_title not in encountered_texts:
                        unique_hits.append(hit)
                        encountered_texts.add(text_title)

            return unique_hits
        
        except Exception as e:
            raise RuntimeError(f"Error occurred during semantic search: {e}")

    def authenticate_drive_service(self):
        # Initialize the Google Drive API
        SCOPS = ['https://www.googleapis.com/auth/drive']
        # Path to the JSON file containing your client credentials
        SERVICE_ACCOUNT_FILE = 'search/credential.json'
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPS)
        return credentials

    def index_eBooks(self):
        credentials = self.authenticate_drive_service()
        drive_service = build('drive', 'v3', credentials=credentials)
        # Specify the folder ID of the desired folder on Google Drive
        folder_id = '17iMoJjzjuOvF0giYCGZjfLZuoD5hp5NI'
        # Retrieve files from the folder
        results = drive_service.files().list(q=f"'{folder_id}' in parents and mimeType='application/pdf'").execute()
        file_list = results.get('files', [])
        # Index documents
        self.index_documents(file_list, drive_service)

    def index_one_ebook(self, file_id):
        credentials = self.authenticate_drive_service()
        drive_service = build('drive', 'v3', credentials=credentials)
        # Specify the folder ID of the desired folder on Google Drive
        folder_id = '17iMoJjzjuOvF0giYCGZjfLZuoD5hp5NI'
        # Retrieve files from the folder
        results = drive_service.files().list(q=f"'{folder_id}' in parents and mimeType='application/pdf'").execute()
        file_list = results.get('files', [])
        self.index_one_document(file_id, file_list, drive_service)

    def delete_index(self):
        self.es.indices.delete(index=self.index_name)
    def delete_document_by_fileid(self, file_id):
        try:
            # Search for the document by file_id
            search_query = {
                "query": {
                    "term": {
                        "fileId": file_id
                    }
                }
            }

            search_results = self.es.search(index=self.index_name, body=search_query)
            
            # Delete the document if found
            if search_results['hits']['total']['value'] > 0:
                for hit in search_results['hits']['hits']:
                    self.es.delete(index=self.index_name, id=hit['_id'])
            else:
                print(f"No document found with fileId: {file_id}")

        except Exception as e:
            raise RuntimeError(f"Error occurred while deleting document with fileId {file_id}: {e}")
    def search_eBook(self, query):
        results = self.semantic_search(query)
        return results