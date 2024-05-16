
import boto3
import os
import sys
import warnings
from langchain_community.retrievers import WikipediaRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_community.llms import Bedrock
import logging
import traceback


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)

warnings.catch_warnings()
warnings.simplefilter('ignore')

logger.info('Creating Bedrock client')
try:
    bedrock=boto3.client(service_name='bedrock-runtime', 
                        aws_access_key_id=os.environ['aws_access_key_id'],
                        aws_secret_access_key=os.environ['aws_secret_access_key'],
                        region_name='us-east-1')
except Exception as e:
    traceback.print_exc()

CHAT_MODEL = 'amazon.titan-text-express-v1'
EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'


def prepare_vectordb1(wiki_keyword):
    return wiki_keyword


def prepare_vectordb(wiki_keyword):
    try:
        logger.info('--> Getting content from wikipedia')
        wiki_retriever = WikipediaRetriever(doc_content_chars_max=20000, top_k_results=1)
        docs = wiki_retriever.invoke(wiki_keyword)
        
        logger.info('--> Processing content')
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        doc_chunks = text_splitter.split_documents(docs)
        logger.info('Chunk Size = ' + str(len(doc_chunks)))
        
        logger.info('--> Saving content in Chroma')
        bedrock_embeddings=BedrockEmbeddings(model_id=EMBEDDING_MODEL,client=bedrock)
        Chroma.from_documents(documents=doc_chunks, 
                                embedding=bedrock_embeddings, 
                                persist_directory='./.data')
        return 'OK'
    except:
        return 'ERROR'

def load_vectordb():    
    logger.info('--> Loading content from Chroma')
    bedrock_embeddings=BedrockEmbeddings(model_id=EMBEDDING_MODEL,client=bedrock)
    vectordb = Chroma(embedding_function=bedrock_embeddings, 
                        persist_directory='./.data')
    retriever = vectordb.as_retriever()
    return retriever


def create_chain():
    logger.info('--> Creating LLM chain with RAG')
    llm = Bedrock(model_id=CHAT_MODEL, client=bedrock)
    prompt_file = open('prompt_template.txt', 'r')
    prompt_content = prompt_file.read()
    prompt = PromptTemplate(input_variables=['context', 'question'], 
                                template=prompt_content)

    vectordb = load_vectordb()
    chain = ({'context': vectordb, 'question': RunnablePassthrough()} 
            | prompt 
            | llm
            )
    logger.info('--> Langchain with RAG is ready')
    return chain


def create_chain_without_rag():
    logger.info('--> Creating LLM chain without RAG')
    llm = Bedrock(model_id=CHAT_MODEL, client=bedrock)
    chain = (llm)
    logger.info('--> Ready')
    return chain


def invoke_chain(chain, question):
    logger.info('--> Invoking LLM chain')
    logger.info('--> :: Question : ' + question)
    response = chain.invoke(question)
    logger.info('--> :: Response : ' + response)
    return response


def main():
    wiki_chain = create_chain()
    logger.info('--> Ready')
    while True:
        question = input('User: ')
        response = invoke_chain(wiki_chain, question)
        print('Bot: ' + response)


if __name__ == '__main__':
    main()
