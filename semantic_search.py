from sentence_transformers import SentenceTransformer
import os
import logging
import numpy as np
from pinecone import Pinecone, ServerlessSpec, Index
from config import *
from models import db, MercorUsers, Skills, MercorUserSkills, UserResume, PersonalInformation, WorkExperience, Education

# Assuming you're setting PINECONE_API_KEY as an environment variable for security reasons
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Initialize the Pinecone service
pc = Pinecone(api_key='a657e241-7481-4764-b6df-0209ca6f75b9')


# Access the index
index = Index(host='https://mercor-osx9mbf.svc.gcp-starter.pinecone.io',api_key='a657e241-7481-4764-b6df-0209ca6f75b9')
# Initialize the embedding model
model = SentenceTransformer(HUGGINGFACE_MODEL_NAME)

def generate_embedding(text):
    text = str(text)
    embedding = model.encode([text])[0]
    # No need to adjust the dimensionality as it matches the Pinecone index setting
    return embedding

def upsert_user_to_vector_database(user_id, embedding):
    try:
        index.upsert(vectors=[(user_id, embedding.tolist())])
    except Exception as e:
        logger.exception("Error upserting to Pinecone: {}".format(e))

def query_vector_database(query_embedding, top_k=5):
    try:
        # Ensure the query embedding is a list of floats
        query_vector = query_embedding.tolist()

        # Perform the query with the correctly formatted vector
        result = index.query(
            vector=query_vector,
            top_k=top_k,
            include_values=True
        )

        return result
    except Exception as e:
        logger.exception(f"Error querying Pinecone: {e}")
        return None

def search_by_prompt(prompt, top_k=5):
    prompt_embedding = generate_embedding(prompt)
    return query_vector_database(prompt_embedding, top_k=top_k)