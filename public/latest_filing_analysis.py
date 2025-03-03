import ollama
from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd

def cut_string(text, sequence):
    index = text.find(sequence)
    if index != -1:
        return text[:index + len(sequence)]
    else:
        return text

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

def scrapefiling(filingnum, cik):
    """Modified to accept CIK as parameter"""
    nodash = filingnum.replace("-", "")
    header = {
        'User-Agent': 'SeverinComp severin.comp@gmail.com', 
        'Accept-Encoding': 'gzip, deflate'
    }
    urltwo = f"https://www.sec.gov/Archives/edgar/data/{cik}/{nodash}/{filingnum}.txt"
    responsetwo = requests.get(urltwo, headers=header)
    
    intermediary = responsetwo.text[0:5999999]  # Slice to exclude image data etc
    pattern = re.compile(r'\b[a-zA-Z]+\b|^\$[^\s]+|\$\d+|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b')
    responsethree = re.sub(r'<[^>]+>', '', intermediary)  # Delete HTML tags
    
    lookforstr = responsethree.split(" ")
    outputs = ""
    for text in lookforstr:
        text_words = pattern.findall(text)
        for word in text_words:
            outputs = outputs + " " + str(word)
            
    try:
        cut_version = cut_string(outputs, "SIGNATURE")
    except:
        cut_version = cut_string(outputs, "Signature")
    
    return clean_filing(cut_version)

def clean_filing(text):
    antipattern = re.compile(r'^[A-Z]*.*[A-Z]+$')
    antipatterntwo = re.compile(r'^[a-z]+[A-Z][a-z]+$')
    
    cleaninglist = text.split(' ')
    cleanwords = []
    wordlist = ['pdf', 'xml', 'html', 'xbrl', 'xml', 'hdr', 'sgml']
    
    for word in cleaninglist:
        if word in wordlist:
            continue
        elif re.search(antipattern, word) is not None:
            continue
        elif re.search(antipatterntwo, word) is not None:
            continue
        else:
            cleanwords.append(word)
            
    return " ".join(cleanwords)

def analyze_latest_filing(company_name):
    """Modified to accept company_name as parameter"""
    try:
        cik = get_company_cik(company_name)
        print(f"Found CIK: {cik} for company: {company_name}")
        latest_filing_num = getlatestfiling(cik)
        filing_text = scrapefiling(latest_filing_num, cik)
        
        # Prepare the prompt
        task = f"Please analyze this SEC filing for {company_name} and explain its key points and significance. Include any important financial details, business updates, or strategic changes mentioned in the filing."
        prompt = task + filing_text
        
        # Get analysis from LLM
        response = ollama.chat(
            model='deepseek-r1:8b',
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        
        return response['message']['content']
    except ValueError as e:
        return f"Error: {e}"

if __name__ == "__main__":
    company_name = input("Enter company name: ")
    print("\nFetching and analyzing the latest SEC filing...\n")
    analysis = analyze_latest_filing(company_name)
    print("\nAnalysis of the latest filing:\n")
    print(analysis) 