import os
import textwrap

import chromadb
import langchain
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from gpt4all import GPT4All
from langchain_core.prompts import PromptTemplate
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from langchain_core.language_models.llms import LLM
from typing import Any, Dict, List, Mapping, Optional

from langchain.chains import ConversationalRetrievalChain

# --- Cấu hình ---
CSV_FILE = "model_gpt/movie_data.csv"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIRECTORY = "model_gpt/db"
MODEL_DOWNLOAD = "orca-mini-3b-gguf2-q4_0.gguf"
# MODEL_DOWNLOAD = "Llama-3.2-1B-Instruct-Q4_0.gguf" # lighter model
MODEL_PATH_CACHE = "model_gpt"

hf_embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return hf_embeddings.embed_documents(input)

embedding_function = MyEmbeddingFunction()

# --- Tạo vector store ---
client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
# collection_name = "movie_collection" # embedd: title, genres, overview, release date, revenue, vote
collection_name = "movie_1001" # embedd: title, genres, overview, release date (1001 rows)

# Check if the collection exists
if not any(collection.name == collection_name for collection in client.list_collections()):
    print("Creating embeddings and vector store...")
    df = pd.read_csv(CSV_FILE)
    df = df.head(1001)

    # Tạo cột combined_info
    df['combined_info'] = (
        "Movie: " + df['title'].fillna('') + '|' +
        "Genre: " + df['genres'].fillna('') + '|' +
        "Content: " + df['overview'].fillna('') + '|' +
        "Release Date: " + df['release_date'].fillna('').astype(str)
        # "Revenue: " + df['revenue'].fillna('').astype(str) + '|' +
        # "Rating: " + df['vote'].fillna('').astype(str)
    )

    loader = DataFrameLoader(df, page_content_column="combined_info")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = text_splitter.split_documents(data)
    
    collection = client.create_collection(name=collection_name, embedding_function=embedding_function)

    batch_size = 5461 # Maximum batch size allowed by the current chroma version
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        collection.add(
            documents=[t.page_content for t in batch],
            embeddings=hf_embeddings.embed_documents([t.page_content for t in batch]),
            metadatas=[t.metadata for t in batch],
            ids=[f"id{j}" for j in range(i, i + len(batch))]
        )
    print("Embeddings and vector store created.")
else:
    print("Loading existing vector store...")
    collection = client.get_collection(name=collection_name)
    print("Vector store loaded.")

custom_prompt_template = """You are a movie expert. Use the following information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Example:
Context: The sky is blue.
Question: What is the capital of France?
Answer: I don't know.

Context: {context}
Question: {question}

"""

# --- Tải model GPT4All ---
if not os.path.exists(os.path.join(MODEL_PATH_CACHE, MODEL_DOWNLOAD)):
    print("Downloading model...")
    GPT4All.download_model(MODEL_DOWNLOAD, model_path=MODEL_PATH_CACHE)
    print("Model downloaded!")

# --- Custom LLM ---
class CustomGPT4All(LLM):
    model: Any
    model_path: str  

    @property
    def _llm_type(self) -> str:
        return "custom_gpt4all"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.model.generate(prompt, max_tokens=1024)
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_path": self.model_path}  # Truy cập model_path từ self
print("Starting model...")
# --- Khởi tạo model GPT4All ---
model_instance = GPT4All(model_name=MODEL_DOWNLOAD, model_path=MODEL_PATH_CACHE, allow_download=False, verbose=True, n_threads=4)
print("Done init model. ")

# --- Khởi tạo custom LLM ---
llm = CustomGPT4All(model=model_instance, model_path=MODEL_PATH_CACHE)

# --- Tạo chain ---
db = Chroma(client=client, collection_name=collection_name, embedding_function=hf_embeddings)
retriever = db.as_retriever(search_kwargs={"k": 2}, score_threshold=0.4)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# --- Vòng lặp chatbot ---
print("Chatbot: Hello! I'm a movie chatbot. What do you want to know about movies?")
chat_history = []
while True:
    query = input("You: ")
    if query.lower() == "quit":
        break
    result = qa_chain.invoke({"question": query, "chat_history": chat_history})
    print("Chatbot:", result['answer'])
    chat_history.append((query, result["answer"]))