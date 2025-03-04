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
from langchain.chains import RetrievalQA

from langchain_ollama import OllamaLLM
#from langchain_community.embeddings import OllamaEmbeddings
#soup = BeautifulSoup(response.text, 'html.parser') 


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
    for i in range(7):######################################## CHANGE N OF FILINGS TO FETCH
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
        
        responsetwo = requests.get(urltwo,headers = header)
        soup = BeautifulSoup(responsetwo.text, 'html.parser')
        pattern = re.compile(r'\b[a-zA-Z]+\b')#regex for normal word .compile creates a regex object that can be checked against

        souped = soup.find_all(text=lambda text: isinstance(text, str))

        outputs = ""
        for text in souped:
            text_words = pattern.findall(str(text)) #find all strings that match for each text 
            for word in text_words:  ##########3last change
                outputs = outputs + " " + str(word)  #war vorher word
        try:
            cut_version = cut_string(outputs,"SIGNATURE")

        except:
            cut_version = cut_string(outputs,"Signature")
        
        cut_version = cut_version
        print(cut_version)
        print("\nFiling "+ str(i) + " loaded\n")
        file = open('documentstore.txt','a')
        file.write(cut_version)
        file.write(',')
    file.close #now 100 filings are in this file


def clean_filings(inp):
        antipattern = re.compile(r'^[A-Z]*.*[A-Z]$')  #^at start, .* any character zero or more times(at end), .$ match all at end
        cleaninglist = inp.split(' ')
        cleanedtext = ""
        for word in cleaninglist:
            if antipattern.search(word): # we have to make sure we have only a word that we search 
                pass
            else:
                cleanedtext = cleanedtext +" "+ word
        return cleanedtext  #muessen jetzt in und out in prog machen statt in file jedes mal
        


def load_documents(filename):
    documents = []
    with open(filename, 'r') as file:
        documents.append(file.read())
    return documents



def getlatestfiling():
    url = "https://data.sec.gov/submissions/CIK0001780312.json" #format this into data that can be sent to llm 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    recent = response.json()['filings']['recent']['accessionNumber'][0]
    print(recent)
    return(recent)



def scrapefiling(filingnum):
    nodash =""
    for char in filingnum:
        nodash = filingnum.replace("-","")
    header = {
        'User-Agent': 'SeverinComp severin.comp@gmail.com', 'Accept-Encoding':'gzip, deflate'}
    urltwo = "https://www.sec.gov/Archives/edgar/data/0001780312/"+nodash+"/"+filingnum+".txt"
    responsetwo = requests.get(urltwo,headers = header)
    #print(filingnum,nodash,urltwo)
    soup = BeautifulSoup(responsetwo.text, 'html.parser')
    pattern = re.compile(r'\b[a-zA-Z]+\b')#regex for normal word .compile creates a regex object that can be checked against
    
    words = soup.find_all(text=lambda text: isinstance(text, str))

    outputs = ""
    for text in words:
        text_words = pattern.findall(str(text)) #find all strings that match for each text 
        for word in text_words:
            outputs = outputs + " " + word
    try:
        cut_version = cut_string(outputs,"SIGNATURE")

    except:
        cut_version = cut_string(outputs,"Signature")

    cut_version = cut_version
 
    #print(cut_version)
    cut_version = cut_version
    print(len(cut_version))
    file = open('financialtext.txt','w')
    file.write(cut_version)
    file.close
    return cut_version #this might not work



def proompting():
    desiredModel = 'deepseek-r1:8b'
    task = "Sum up this SEC filing and what it means in detail: "
    with open('financialtext.txt','r', encoding='utf-8') as file:
        proompt = task + file.read()
    response = Ollama.chat(
        model = desiredModel,
        messages = [{
            'role':'user',
            'content': proompt }]
        ) 
    return response['message']['content']



                            #main code for 100 filings
################################################################################
scrape_hundredfilings() #scrapes 100 SEC filings, also calls scrapehundredfilings() and writes to file
documentsaslist = load_documents('documentstore.txt') #loads from file, assigned to variable 
finaldocuments = ""
print("----------------------------Loading data done-----------------------------------")
for doc in documentsaslist:
    a = clean_filings(doc)
    finaldocuments = finaldocuments + " "+ a 
print(finaldocuments)
print("----------------------------Cleaning dataset done-----------------------------------")
textsplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#instantiates textsplitter chunks measured by n of characters

docs = textsplitter.create_documents(finaldocuments)
#split text

embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")

vectorstore = FAISS.from_documents(docs, embeddings)
#instantiate vectorstorage from split text and embeddings
#do similarity search and clustering with FAISS library

#retrieval chain
llm = OllamaLLM(model='deepseek-r1:7b')
latest =clean_filings(scrapefiling(latestfiling()))
prompttemplate = """use the following context to answer the question.
    Context: {context}
    Question: {question}
    Answer:"""
prompt = PromptTemplate.from_template(prompttemplate)
#create prompttemplate
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever(), chain_type_kwargs={"prompt": prompt})
question= "What does this latest filing mean for the company:"+str(latest)##
result = qa_chain({"query":question})
print(result['result'])


#                                   Next: clean up input, kein garbage in
#                                   dann: modelle anlegen fuer unternehmen
#                                         und rss feed abfragen, weitere 
#                                         anwendungen finden
#                                       
#
#
#

