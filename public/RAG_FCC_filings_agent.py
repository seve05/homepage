import ollama
import base64
from bs4 import BeautifulSoup
import requests
import re 
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA, MapReduceChain, LLMChain,ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain_ollama import OllamaLLM
#from langchain_community.embeddings import OllamaEmbeddings
import json
import pandas as pd


def cut_string(text, sequence):
    index = text.find(sequence) #reads string to find sequence
    
    # If the sequence is found, return the part of the string before the sequence plus the sequence itself
    if index != -1:
        return text[:index + len(sequence)]#slices string 
    else:
        # If the sequence isn't found, return the original text or handle it as needed
        return text



def load_filings_csv():
    all_filings = []
    with open('documentstore.txt','r', encoding='utf-8') as file:
        all_filings = file.read().split(',')
        file.close()
    return all_filings



def load_hundred_filingnum():
    time.sleep(1/10)
    url = "https://data.sec.gov/submissions/CIK0001780312.json" #format this into data that can be sent to llm 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    training_a = ""
    training_b = []
    for i in range(25):######################################## CHANGE Number OF FILINGS TO FETCH 
        training_a = response.json()['filings']['recent']['accessionNumber'][i]
        training_b.append(training_a)
    print("\nfilingsnums loaded\n")###########DEBUG
    return(training_b)  
    


def scrape_hundredfilings():
    filingnumbers = load_hundred_filingnum()
    nodash =""
    for i in range(len(filingnumbers)):
        for char in filingnumbers[i]:
            nodash = filingnumbers[i].replace("-","")
        header = {
            'User-Agent': 'SeverinComp severin.comp@gmail.com', 'Accept-Encoding':'gzip, deflate'}
        urltwo = "https://www.sec.gov/Archives/edgar/data/0001780312/"+nodash+"/"+filingnumbers[i]+".txt"
        print(urltwo) 
        responsetwo = requests.get(urltwo,headers = header)
        # cut the response bc we might get overwhelmed by bloated dataset containing images etc
        intermediary = responsetwo.text[0:5999999]
        pattern = re.compile(r'\b[a-zA-Z]+\b|^\$[^\s]+|\$\d+|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b') #..... regex for normal word of any length or symbol with leading dollar sign .compile creates a regex object that can be checked against
        responsethree = re.sub(r'<[^>]+>', '', intermediary) #deletes all content inbetween <> tags 
        lookforstr = responsethree.split(" ")
        newlist = []
        for element in lookforstr:
            newlist.append(element)
        
        outputs = ""
        for text in newlist:

            text_words = pattern.findall(text) #find all strings that match for each text 
            for word in text_words: 
                outputs = outputs + " " + str(word)  
        try:
            cut_version = cut_string(outputs,"SIGNATURE")
        except:
            cut_version = cut_string(outputs,"Signature")

        cut_version = cut_version
        print("\nFiling "+ str(i) + " loaded\n")
        file = open('documentstore.txt','a')
        file.write(cut_version)
        file.write(',')
    file.close #now 100 filings are in this file
        


def clean_filings(inp): #input is text in list of size one element
    antipattern = re.compile(r'^[A-Z]*.*[A-Z]+$')  #^at start, .*any character one or more times(at end), .$ denotes the end of string
    antipatterntwo = re.compile(r'^[a-z]+[A-Z][a-z]+$')
    antipatternthree = re.compile(r'^[A-Z]+[a-z]+[A-Z]+[a-z]')
    cleanwords = []
    text = inp[0]
    words = text.split(" ")
    for word in words:
        print(word)
        print(type(word))
        if re.search(antipattern,word):  
            pass
        elif re.search(antipatterntwo,word):
            pass
        elif re.search(antipatternthree,word):
            pass
        else:
            cleanwords.append(word)
    cleanedtext = " ".join(cleanwords)
    outputlist = []
    outputlist = cleanedtext.split(" ", 1) 
    return outputlist #returns list of size:1 as that is needed
        # this curiously needs to return a list with a single element in order for
        # our next function to generate the correct embeddings, string returns letters as embeddings
        # list of words returns words as embeddings


################SINGLE FILING CLEANING DO NOT USE  FOR MULTIPLE FILINGS
def clean_filings_single(inp):
    antipattern  = re.compile(r'^[A-Z]*.*[A-Z]+$')
    antipatterntwo = re.compile(r'^[a-z]+[A-Z][a-z]+$')
    cleaningstr = inp    
    cleaninglist = cleaningstr.split(' ')
    cleanedtext = ""
    cleanwords = []
    wordlist = ['pdf','xml','html','xbrl','xml','hdr','sgml']
    for word in cleaninglist:
        if word in wordlist:
            pass
        elif re.search(antipattern, word) is not None:
            pass
        elif re.search(antipatterntwo,word)is not None:
            pass
        else:
            cleanwords.append(word)
    cleanedtext = " ".join(cleanwords)
    return cleanedtext 


def load_documents(filename):
    documents = []
    with open(filename, 'r') as file:
        documents.append(file.read())
    return documents



def get_company_cik(company_name):
    """Get CIK number for a company name from SEC's company tickers json."""
    # Download and cache the company tickers data if not already present
    try:
        df = pd.read_json('company_tickers.json').T
    except FileNotFoundError:
        # Fetch and save the data if not cached
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        df = pd.read_json(response.text).T
        df.to_json('company_tickers.json')
    
    # Convert company names to lowercase for case-insensitive matching
    df['title'] = df['title'].str.lower()
    company_name = company_name.lower()
    
    # Try to find an exact match first
    matches = df[df['title'] == company_name]
    if len(matches) == 0:
        # If no exact match, try partial matching
        matches = df[df['title'].str.contains(company_name, case=False, na=False)]
    
    if len(matches) == 0:
        raise ValueError(f"No company found matching '{company_name}'")
    elif len(matches) > 1:
        print("Multiple matches found:")
        for _, row in matches.iterrows():
            print(f"- {row['title']} (CIK: {row['cik_str']})")
        raise ValueError("Please provide a more specific company name")
    
    # Pad CIK with leading zeros to 10 digits
    cik = str(matches.iloc[0]['cik_str']).zfill(10)
    return cik

def getlatestfiling(cik):
    """Modified to accept CIK as parameter"""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    recent = response.json()['filings']['recent']['accessionNumber'][0]
    return recent

#######################SINGLE FILE FUNCTION DO NOT USE FOR MULTI FILINGS
def scrapefiling(filingnum, cik):
    """Modified to accept CIK as parameter"""
    nodash = filingnum.replace("-", "")
    header = {
        'User-Agent': 'SeverinComp severin.comp@gmail.com', 
        'Accept-Encoding': 'gzip, deflate'
    }
    urltwo = f"https://www.sec.gov/Archives/edgar/data/{cik}/{nodash}/{filingnum}.txt"
    responsetwo = requests.get(urltwo,headers = header)
    #print(filingnum,nodash,urltwo)
    intermediary = responsetwo.text[0:5999999]# slice after this size to exclude image data etc
    pattern = re.compile(r'\b[a-zA-Z]+\b|^\$[^\s]+|\$\d+|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b') #..... regex for normal word of any length or symbol with leading dollar sign .compile creates a regex object that can be checked against
    responsethree = re.sub(r'<[^>]+>', '', intermediary) #deletes all content inbetween <> tags 
    lookforstr = responsethree.split(" ")
    newlist = []
    for element in lookforstr:
        newlist.append(element)
    
    outputs = ""
    for text in newlist:

        text_words = pattern.findall(text) #find all strings that match for each text 
        for word in text_words: 
            outputs = outputs + " " + str(word)
    try:
        cut_version = cut_string(outputs,"SIGNATURE")
    except:
        cut_version = cut_string(outputs,"Signature")

    cut_version = cut_version 
    file = open('financialtext.txt','w')
    file.write(cut_version)
    file.close
    return cut_version #this might not work



def proompting():
    desiredModel = 'deepseek-r1:8b'
    task = "Sum up this SEC filing and what it means in detail: "
    with open('financialtext.txt','r', encoding='utf-8') as file:
        proompt = task + file.read()
    response = ollama.chat(
        model = desiredModel,
        messages = [{
            'role':'user',
            'content': proompt }]
        ) 
    return response['message']['content']



                            #main code for 100 filings
################################################################################
def RAG_pipeline(company_name):
    """Modified to accept company_name as parameter"""
    try:
        cik = get_company_cik(company_name)
        print(f"Found CIK: {cik} for company: {company_name}")
        scrape_hundredfilings()
        documentsaslist = load_documents('documentstore.txt')
        finaldocuments = clean_filings(documentsaslist)
        print("----------------------------Loading data done-----------------------------------")
        
        print("----------------------------Splitting into chunks----------------------------------")
        # Smaller chunk size for better processing
        textsplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = textsplitter.create_documents(finaldocuments)
        
        print("----------------------------Creating word embeddings----------------------------------")
        embeddings = OllamaEmbeddings(model="all-minilm:l6-v2")
        
        print("----------------------------Saving to vector db----------------------------------")
        vectorstore = FAISS.from_documents(docs, embeddings)

        # Set up the LLM
        llm = OllamaLLM(model='deepseek-r1:7b')

        # Map prompt - for processing individual chunks
        map_template = """Summarize the key points from this section of SEC filings:
        {context}
        
        Key points:"""
        map_prompt = PromptTemplate.from_template(map_template)

        # Reduce prompt - for combining summaries
        reduce_template = """Given these summaries from different sections of SEC filings, provide a comprehensive analysis addressing the following question:
        Question: {question}
        
        Summaries:
        {context}
        
        Comprehensive analysis:"""
        reduce_prompt = PromptTemplate.from_template(reduce_template)

        # Create the map chain
        map_chain = LLMChain(llm=llm, prompt=map_prompt)

        # Create the reduce chain
        reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

        # Combine documents chain
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain,
            document_variable_name="context"
        )

        # Create the final reduce documents chain
        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=combine_documents_chain,
            token_max=4000,  # Adjust based on your model's context window
        )

        # Create the final map reduce chain
        map_reduce_chain = MapReduceChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            document_variable_name="context",
            return_intermediate_steps=False
        )

        # Set up the retrieval chain with map reduce
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="map_reduce",
            retriever=vectorstore.as_retriever(search_kwargs={'k': 50}),
            chain_type_kwargs={
                "question_prompt": map_prompt,
                "combine_prompt": reduce_prompt,
                "return_intermediate_steps": False
            }
        )

        print("----------------------------Generation, RAG----------------------------------")
        question = "Explain what the company is about and mention any important milestones"
        result = qa_chain({"query": question})
        print(result['result'])
    except ValueError as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    company_name = input("Enter company name: ")
    RAG_pipeline(company_name)

#
#        -   Make company name variable 
#
#        -   store the company-specific database locally long-term
#
#        -   add in stocks and shareprice, revenue  as context for more robust answer
#
#        -   use larger model for the output generation 
#
#
