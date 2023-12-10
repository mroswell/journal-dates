import requests
from lxml import html
import pandas as pd
from datetime import datetime


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, '%d %B %Y').strftime('%m/%d/%Y')
    except ValueError:
        return None


def calculate_date_diff(date1, date2):
    if date1 and date2:
        d1 = datetime.strptime(date1, '%m/%d/%Y')
        d2 = datetime.strptime(date2, '%m/%d/%Y')
        return (d2 - d1).days
    return None


def get_data_from_link(link):
    if 1:
        response = requests.get(link)
        tree = html.fromstring(response.content)

        title = tree.xpath('//div[@id="full-view-heading"]/h1[1]/text()')
        author = tree.xpath('//div[@class="inline-authors"]/div[1]/div[1]/span[1]/a[1]/text()')
        doi_link = tree.xpath(
            '//*[@data-ga-action="DOI" and contains(concat(" ", normalize-space(@class), " "), " id-link ")]/@href')

        if doi_link:
            doi_response = requests.get(doi_link[0])
            doi_tree = html.fromstring(doi_response.content)
            breadcrumbs = doi_tree.xpath('//ol[@class="c-breadcrumbs"]/li[2]/a[1]/span[1]/text()')

            bib_info = doi_tree.xpath('//ul[@class="c-bibliographic-information__list"]')
            if bib_info:
                received = parse_date(doi_tree.xpath(
                    '//ul[@class="c-bibliographic-information__list"]/li[1]/p[1]/span[2]/time[1]/text()')[0])
                accepted = parse_date(doi_tree.xpath(
                    '//ul[@class="c-bibliographic-information__list"]/li[2]/p[1]/span[2]/time[1]/text()')[0])
                published = parse_date(doi_tree.xpath(
                    '//ul[@class="c-bibliographic-information__list"]/li[3]/p[1]/span[2]/time[1]/text()')[0])
                issue = parse_date(doi_tree.xpath(
                    '//ul[@class="c-bibliographic-information__list"]/li[4]/p[1]/span[2]/time[1]/text()')[0])
            else:
                published = parse_date(
                    doi_tree.xpath('//ul[@class="c-article-identifiers"]/li[2]/time[1]/text()')[0])
                received =  ''
                accepted = ''
                issue = ''

            return {
                "Link": link,
                "Title": title[0].strip() if title else None,
                "Author": author[0] if author else None,
                "DOI": doi_link[0] if doi_link else None,
                "Breadcrumbs": breadcrumbs[0] if breadcrumbs else None,
                "Received": received,
                "Accepted": accepted,
                "Published": published,
                "Issue": issue,
                "Accepted - Received (days)": calculate_date_diff(received, accepted),
                "Published - Accepted (days)": calculate_date_diff(accepted, published),
                "Received to Published (days)": calculate_date_diff(received, published)
            }
    #except Exception as e:
        #print(f"Error processing link {link}: {e}")
        #return None


def main():
#   target_url = "https://pubmed.ncbi.nlm.nih.gov/?term=Nature%5BJournal%5D+NOT+%28SARS-COV-2+OR+COVID-19%29&filter=pubt.classicalarticle&filter=pubt.clinicalstudy&filter=pubt.clinicaltrialphasei&filter=pubt.clinicaltrialphaseii&filter=pubt.clinicaltrialphaseiii&filter=pubt.clinicaltrialphaseiv&filter=pubt.comparativestudy&filter=pubt.controlledclinicaltrial&filter=pubt.evaluationstudy&filter=pubt.multicenterstudy&filter=pubt.observationalstudy&filter=pubt.pragmaticclinicaltrial&filter=pubt.technicalreport&size=100"  # Replace with the URL of the webpage you want to scrape

    target_url = "https://pubmed.ncbi.nlm.nih.gov/?term=Nature%5BJournal%5D+NOT+%28SARS-COV-2+OR+COVID-19%29&filter=pubt.classicalarticle&filter=pubt.clinicalstudy&filter=pubt.clinicaltrialphasei&filter=pubt.clinicaltrialphaseii&filter=pubt.clinicaltrialphaseiii&filter=pubt.clinicaltrialphaseiv&filter=pubt.comparativestudy&filter=pubt.controlledclinicaltrial&filter=pubt.evaluationstudy&filter=pubt.multicenterstudy&filter=pubt.observationalstudy&filter=pubt.pragmaticclinicaltrial&filter=pubt.technicalreport&filter=years.2020-2023&size=100"
    response = requests.get(target_url)
    tree = html.fromstring(response.content)

    # Extract href attributes from elements with class "docsum-title"
    links = tree.xpath('//a[contains(@class, "docsum-title")]/@href')

    # Prepend the base URL if the extracted links are relative paths
    base_url = "https://pubmed.ncbi.nlm.nih.gov"  # Replace with the base URL of the website if needed
    full_links = [base_url + link if not link.startswith('https://') else link for link in links]

    data = []
    for link in full_links:
        result = get_data_from_link(link)
        if result is not None:
            data.append(result)

    df = pd.DataFrame(data)
    df.to_excel('pubmed_nature_dates_non_covid.xlsx', index=False)


if __name__ == "__main__":
    main()
