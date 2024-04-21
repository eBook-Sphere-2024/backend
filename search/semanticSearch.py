from elasticsearch import Elasticsearch
from transformers import BertTokenizer, BertModel
from nltk.corpus import wordnet as wn
import torch
import os
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor  
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rest_framework.response import Response
from rest_framework import status

# Connect to Elasticsearch
es = Elasticsearch(['https://localhost:9200'], basic_auth=('elastic', '123456'),verify_certs=False)

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')
bert_model.eval()

# Set index name
index_name = 'ebook'

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ''.join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception as e:
        raise RuntimeError(f"Error occurred while extracting text from {pdf_path}: {e}")

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
    
# Function to index a single document
def index_document(pdf_path):
    text_content = extract_text_from_pdf(pdf_path)
    if text_content:
        relative_path = os.path.relpath(pdf_path).replace("\\", "/")
        embedded_text = embed_text(text_content)
        document_body = {
            'filename': relative_path,
            'text': text_content,
            'text_vector': embedded_text
        }
        try:
            es.index(index=index_name, body=document_body)
            print(f"Indexed document: {pdf_path}")
        except Exception as e:
            raise RuntimeError(f"Error occurred while indexing {pdf_path}: {e}")

def index_documents(pdf_directory):
    with ThreadPoolExecutor() as executor:
        for filename in os.listdir(pdf_directory):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                executor.submit(index_document, pdf_path)

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

# Index documents
def index_eBook():
    pdf_directory = '././assets/Books'
    index_documents(pdf_directory)
    
# Perform semantic search
def search_eBook(query):
    results = semantic_search(query)
    return results
