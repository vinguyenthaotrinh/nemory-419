import os
import time

import chromadb
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from gpt4all import GPT4All
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from langchain_core.language_models.llms import LLM
from typing import Any, Dict, List, Mapping, Optional

from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough, RunnableSequence

# --- Cấu hình ---
CSV_FILE = "model_gpt/movie_data.csv"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIRECTORY = "model_gpt/db"
MODEL_DOWNLOAD = "Llama-3.2-1B-Instruct-Q4_0.gguf"  # Changed model
MODEL_PATH_CACHE = "model_gpt"

hf_embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return hf_embeddings.embed_documents(input)

embedding_function = MyEmbeddingFunction()

# --- Tạo vector store ---
client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection_name = "movie_1001"  # embedd: title, genres, overview, release date (1001 rows)

# Check if the collection exists
if not any(collection.name == collection_name for collection in client.list_collections()):
    print("Creating embeddings and vector store...")
    df = pd.read_csv(CSV_FILE)
    df = df.head(1001)

    df['combined_info'] = (
        "Movie: " + df['title'].fillna('') + '\n' +
        "Genre: " + df['genres'].fillna('') + '\n' +
        "Content: " + df['overview'].fillna('') + '\n' +
        "Release Date: " + df['release_date'].fillna('').astype(str)
    )
    
    loader = DataFrameLoader(df, page_content_column="combined_info")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = text_splitter.split_documents(data)

    collection = client.create_collection(
        name=collection_name, embedding_function=embedding_function
    )

    batch_size = 5461  # Maximum batch size allowed by the current chroma version
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        collection.add(
            documents=[t.page_content for t in batch],
            embeddings=hf_embeddings.embed_documents([t.page_content for t in batch]),
            metadatas=[t.metadata for t in batch],
            ids=[f"id{j}" for j in range(i, i + len(batch))],
        )
    print("Embeddings and vector store created.")
else:
    print("Loading existing vector store...")
    collection = client.get_collection(name=collection_name)
    print("Vector store loaded.")

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
        response = self.model.generate(
            prompt,
            max_tokens=256,
            temp=0.2,
            top_k=40,
            top_p=0.7,
            repeat_penalty=1.18,
            repeat_last_n=64,
            n_batch=9,
            n_predict=256,
        )  # Adjusted generate config for Llama-3 (optional)
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_path": self.model_path}

print("Starting model...")
# --- Khởi tạo model GPT4All ---
model_instance = GPT4All(
    model_name=MODEL_DOWNLOAD,
    model_path=MODEL_PATH_CACHE,
    allow_download=False,
    verbose=True,
    device="cpu",
    n_threads=4,
)
print("Done init model. ")

# --- Khởi tạo custom LLM ---
llm = CustomGPT4All(model=model_instance, model_path=MODEL_PATH_CACHE)

# --- Tạo chain ---
db = Chroma(
    client=client, collection_name=collection_name, embedding_function=hf_embeddings
)
retriever = db.as_retriever(search_kwargs={"k": 3})

# --- Prompt Template for Llama-3 ---
template = """<|start_header_id|>user<|end_header_id|>\n\nShort answer based on the following context: {context}
Question: {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"""
prompt = PromptTemplate(input_variables=["context", "question"], template=template)

# --- Create retrieval chain ---
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
)

print("Chatbot: Hello! I'm a movie chatbot. What do you want to know about movies?")
chat_history = []
while True:
    query = input("You: ")
    if query.lower() == "quit":
        break

    start_time = time.time()
    
    # Use only the last 2 turns of chat history as context
    if len(chat_history) > 1:
        context = "\n".join([f"User: {q}\nChatbot: {a}" for q, a in chat_history[-2:]])
        full_query = f"Previous conversation:\n{context}\n\nNew question: {query}"
    elif len(chat_history) > 0:
        context = "\n".join([f"User: {q}\nChatbot: {a}" for q, a in chat_history])
        full_query = f"Previous conversation:\n{context}\n\nNew question: {query}"
    else:
        full_query = query
    
    result = rag_chain.invoke(full_query)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Chatbot:", result)
    print(f"Time taken to generate response: {elapsed_time:.2f} seconds")

    # Get feedback from user
    while True:
        feedback = input("Was this answer helpful? (Y/N): ")
        if feedback.upper() == "Y":
            print("Chatbot: Glad to hear that!")
            chat_history.append((query, result))
            break
        else:
            clarification = input("Chatbot: Could you please specify what information you're looking for? ")
            new_query = f"Original question: {query}\nUser clarification: {clarification}"

            start_time = time.time()
            # Combine new query with previous context for a more comprehensive search
            if len(chat_history) > 0:
                context = "\n".join([f"User: {q}\nChatbot: {a}" for q, a in chat_history[-2:]])
                full_query = f"Previous conversation:\n{context}\n\n{new_query}"
            else:
                full_query = new_query
            
            result = rag_chain.invoke(full_query)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("Chatbot:", result)
            print(f"Time taken to generate response: {elapsed_time:.2f} seconds")
            chat_history.append((query, result))