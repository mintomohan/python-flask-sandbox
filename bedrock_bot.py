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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)

warnings.catch_warnings()
warnings.simplefilter('ignore')

bedrock=boto3.client(service_name='bedrock-runtime', 
                    aws_access_key_id=os.environ['aws_access_key_id'],
                    aws_secret_access_key=os.environ['aws_secret_access_key'],
                    region_name=os.environ['aws_region_name'])

CHAT_MODEL = 'amazon.titan-text-express-v1'
EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'


def prepare_vectordb(wiki_keyword):
    try:
        wiki_retriever = WikipediaRetriever(doc_content_chars_max=50000, top_k_results=1)
        docs = wiki_retriever.invoke(wiki_keyword)
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        doc_chunks = text_splitter.split_documents(docs)
        
        bedrock_embeddings=BedrockEmbeddings(model_id=EMBEDDING_MODEL,client=bedrock)
        Chroma.from_documents(documents=doc_chunks, 
                                embedding=bedrock_embeddings, 
                                persist_directory='./.data')
        
        logger.info('Vector DB created')
        return 'OK'
    except Exception as e:
        logger.debug(e)
        return 'ERROR'


def load_vectordb():
    bedrock_embeddings=BedrockEmbeddings(model_id=EMBEDDING_MODEL, client=bedrock)
    vectordb = Chroma(embedding_function=bedrock_embeddings, 
                        persist_directory='./.data')
    retriever = vectordb.as_retriever()
    logger.info('Vector DB loaded')
    return retriever


def create_agent():
    llm = Bedrock(model_id=CHAT_MODEL, client=bedrock)
    prompt_file = open('prompt_template.txt', 'r')
    prompt_content = prompt_file.read()
    prompt = PromptTemplate(input_variables=['context', 'question'], 
                                template=prompt_content)

    vectordb = load_vectordb()
    agent = ({'context': vectordb, 'question': RunnablePassthrough()} 
            | prompt 
            | llm
            )
    logger.info('LLM agent created')
    return agent


def create_agent_without_rag():
    llm = Bedrock(model_id=CHAT_MODEL, client=bedrock)
    agent = (llm)
    logger.info('LLM agent created')
    return agent


def main():
    wiki_agent = create_agent()
    while True:
        question = input('User: ')
        response = wiki_agent.invoke(question)
        print('Bot: ' + response)


if __name__ == '__main__':
    main()
