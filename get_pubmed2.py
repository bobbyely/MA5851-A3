# Imports
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
from tqdm.notebook import tqdm

# initialising
# search query
query = "cancer"
base_url = "https://pubmed.ncbi.nlm.nih.gov"
search_portion = "/?term="
filter_portion = "&filter=datesearch.y_5"
page_portion = "&page="
citation_url = "https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid="
num_pages_to_search = 1000


# Get the data
# Init db
df = pd.DataFrame(columns = ['year', 'pmid', 'title', 'free', 'journal', 'cited_by', 'abstract'])

# Initial request
probable_articles = num_pages_to_search * 10
count = 1
for page_num in tqdm(range(num_pages_to_search)):
    print(f"Page: {page_num+1}")

    # Request url
    url = base_url + search_portion + query + filter_portion + page_portion + str(page_num+1)

    # try and get a response
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get articles links on page
        article_links = soup.find_all("a", {"class":"docsum-title"})
        
        
        # get each article information
        for link in article_links:
            print(f"Getting article {count} / {probable_articles}")
            pmid = link['href'].split('/')[1]
            new_url = f"{base_url}/{pmid}"

            # Initialise variables
            title = ''
            journal = ''
            year = ''
            abstract = ''
            free = False
            cited_by = 0

            
            try:
                response = requests.get(new_url)
                soup = BeautifulSoup(response.content, 'html.parser')

                # title
                title = soup.find("h1", {"class":"heading-title"}).text.strip()

                # year
                year = soup.find("span", {"class":"cit"}).text.strip().split(";")[0].split(" ")[0]

                # Journal
                journal = soup.find("button", {"id":"full-view-journal-trigger"}).text.strip()

                # Free
                try:
                    # Get free status
                    flag = soup.find("span", {"class":"free-label"})
                    if len(flag) > 0:
                        free = True
                except Exception as e:
                    pass


                # Abstract
                abstract = soup.find("div", {"id":"eng-abstract"})
                abstract = abstract.find('p').text.strip()


                # cited by
                cited_url = f"{citation_url}{pmid}"
                try:
                    # something
                    new_response = requests.get(cited_url)
                    new_soup = BeautifulSoup(new_response.content, 'html.parser')

                    cited_by = new_soup.find("div", {"class":"results-amount"})
                    cited_by = cited_by.find("span", {"class":"value"}).text

                    time.sleep(1) # rate limit the citation information
                except Exception as e:
                    print(f"Couldn't get citation information -- {e}")


                time.sleep(1) # rate limit articles
            except Exception as e:
                print(f"Couldn't get article page -- {e}")


            # print statement for clarity
            #print(f"{year} - {title}. {journal}. Free: {free}. Cited by: {cited_by}.PMID: {pmid}.\nAbstract:\n{abstract}-----\n\n")
            count += 1
            # fill db
            df.loc[len(df)] = [year, pmid, title, free, journal, cited_by, abstract]


        time.sleep(1) # rate limit pages 
        # save df at end of each page
        df.to_csv("pubmed-cancer.csv", index=False)   
    except Exception as e:
        print(f"Couldn't get response / article links -- {e}")

# Final save
df.to_csv("pubmed-cancer.csv", index=False)