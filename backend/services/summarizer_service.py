import pymupdf
from sentence_transformers import SentenceTransformer
import numpy as np
import os
from sklearn.cluster import KMeans
from typing import List, Tuple, Dict, Optional
from models.llm_model import llm_model

_embedder=SentenceTransformer('all-MiniLM-L6-v2')
model=llm_model

def _split_into_chunks(text, chunk_size=500, overlap=50):
    '''
    input: text in the form of  a string
    output: list of chunks of text, each of size chunk_size
    '''
    
    chunks=[]
    for i in range(0, len(text), chunk_size-overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks

def _embed_text(text:str)-> Tuple[List[str], np.ndarray]:
    # embed the text using the sentence transformer model
    '''
    input: text in the form of a string
    output: embedding of the text in the form of a numpy array and the relevant chunks
    '''

    chunks=_split_into_chunks(text)
    vectors=_embedder.encode(chunks)
    return chunks, vectors

def _extract_text_from_pdf(filepath: str)-> str:
    '''
    input: filepath of pdf
    output: text extracted from the pdf
    '''
    doc=pymupdf.open(filepath)
    full_text=""
    for page in doc:
        full_text+=page.get_text()
    return full_text

async def _process_files_for_summarization(filepaths: list[str])-> tuple[list[str], np.ndarray]:
    '''
    input: list of filepaths
    processes files for text extraction and embedding
    output: extracted chunks and embeddings
    '''
    all_chunks=[]
    all_vectors=[]
    for path in filepaths:
        if path.endswith('.pdf'):
            text=_extract_text_from_pdf(path)

        else:
            continue
        chunks, vectors=_embed_text(text)
        all_chunks.extend(chunks)
        all_vectors.append(vectors)

    if all_vectors:
        print("Vectorisation succesful")
        return all_chunks, np.vstack(all_vectors)

    else:
        raise ValueError('No text extracted')
def _clustering(vectors, num_clusters):
    """
    input: embeddings from given pdf text as vectors
    output: clusters of similar vectors
    """
    if len(vectors)<num_clusters:
        return list(range(len(vectors)))
    
    k=num_clusters
    kmeans=KMeans(n_clusters=k, random_state=42, n_init=10).fit(vectors)
    labels=kmeans.labels_
    closest_indices=[]

    for i in range(num_clusters):
        cluster_indices=np.where(labels==i)[0]
        if len(cluster_indices)>0:
            distances=np.linalg.norm(vectors[cluster_indices]-kmeans.cluster_centers_[i], axis=1)

            closest_index=np.argmin(distances)

            closest_indices.append(cluster_indices[closest_index])

    selected_indices=sorted(list(set(closest_indices)))
    return selected_indices

async def _summary_creater(selected_indices, chunks):
    """
    input: indices of selected chunks and chunks themselves
    output: summary list of selected chunks
    """
    summary_list=[]
    for i in selected_indices:
        section=chunks[i]
        map_prompt=f"""
        Act as a concise summariser.
        Summarise the given text into 2-3 lines, no more. Ensure you completely cover the content of the text. This text will be enclosed in triple backticks (```)
        The output should be the summary of the user supplied text.
        Be concise and precise in your behaviour.

        ```{section}```
        SUMMARY: 
        """
        temp=0.7
        max_tokens=150

        response=model.create_completion(
        prompt=map_prompt,
        temperature=temp,
        max_tokens=max_tokens
        )

        summary=response['choices'][0]['text']
        summary=summary.replace("[/INST]", "")
        print(summary)
        print(i)
        summary_list.append(summary)
        print(f"Summary for chunk{i} is ready")

    return summary_list

async def _collate_summaries(individual_summaries: list[str], max_tokens: int)->str:
    '''
    input: list of individual summaries and max_tokens to decide output length
    output: summary as a string
    '''
    summaries="\n".join(individual_summaries)
    final_prompt = f"""<|im_start|>system
    You are a precise and concise summariser.
    You will be given a series of summaries from a book. The summaries will be enclosed in triple backticks (```).
    Your task is to write a verbose summary of what was covered in the book.

    The output should be a detailed and coherent summary that captures all the key information present in the provided summaries. Combine each summary into one whole summary 
    The goal is to help a reader understand the entire content of the book from this single collated summary. 

    Do not add any external information. Base your answer only on what is provided. Ensure it is a single stream of text, and not split up. Combine parts to form a bigger whole.
    Capture the sentiment of the book.
    Structure your response in markdown.
    <|im_end|>
    <|im_start|>user
    ```{summaries}```
    Question:
    Provide a detailed summary of the book based on the provided summaries.
    <|im_end|>
    <|im_start|>assistant
    SUMMARY:
    Here is the detailed summary of the book:
    """

    temp=0.7

    response=model.create_completion(
        prompt=final_prompt,
        temperature=temp,
        max_tokens=max_tokens
    )
    assistant_reply=response['choices'][0]['text']
    collated_summary=assistant_reply.replace("[/INST]", "")
    return collated_summary

async def generate_document_summary(filepaths: List[str], num_clusters: int, max_tokens: int) -> str:
    """
    main public output function for document summarization
    returns summary as string
    """
    all_chunks, all_vectors=await _process_files_for_summarization(filepaths)

    selected_indices=_clustering(all_vectors, num_clusters)

    individual_summaries=await _summary_creater(selected_indices, all_chunks)

    # Step 4: Collate individual summaries into a single, comprehensive summary
    collated_summary=await _collate_summaries(individual_summaries, max_tokens)

    return collated_summary

