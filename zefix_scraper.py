import requests
import json
import csv
import os
from bs4 import BeautifulSoup as bs


def saveData(dataset):
    with open('data.csv', mode='a+', encoding='utf-8-sig', newline='') as csvFile:
        #  company name, company street, postal code, city, c/o, last name, first name, linkedin profile
        fieldnames = ["Company Name", "Company Street", "Postal Code", "City", "C/O", "Last Name", "First Name", "Linkedin Profile"
                      ]
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames,
                                delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if os.stat('data.csv').st_size == 0:
            writer.writeheader()
        writer.writerow({
            "Company Name": dataset[0],
            "Company Street": dataset[1],
            "Postal Code": dataset[2],
            "City": dataset[3],
            "C/O": dataset[4],
            "Last Name": dataset[5],
            "First Name": dataset[6],
            "Linkedin Profile": dataset[7]
        })


def searchZefix(publication_start, publication_end):
    link = "https://www.zefix.ch/ZefixREST/api/v1/shab/search.json"
    headers = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    data = {
        "maxEntries": 5000,
        "offset": 0,
        # "mutationTypes": [2],
        "publicationDate": publication_start,
        "publicationDateEnd": publication_end,
        # "registryOffices": [20]
    }

    try:
        resp = requests.post(link, headers=headers, data=json.dumps(data)).json()
    except:
        print("Failed to open {}".format(link))
        return
    # resp = json.loads(open('resp.json', mode='r', encoding='utf-8').read())

    all_records = resp.get('list')
    print("Records detected: {}".format(len(all_records)))
    for record in all_records:
        company_name = record.get('name')
        company_street = record.get('address').get('street')
        if record.get('address').get('houseNumber'):
            company_street = company_street + " " + record.get('address').get('houseNumber')
        postal_code = record.get('address').get('swissZipCode')
        city = record.get('address').get('town')
        c_o = record.get('address').get('careOf')
        shabPub_records = record.get('shabPub')
        for shab in shabPub_records:
            shab_message = shab.get('message', '')
            if shab_message:
                soup = bs('<html>' + shab_message + '</html>', 'html.parser')
                shab_message = soup.text.strip()
            try:
                shab_messages = shab_message.split('Eingetragene Personen:')[
                    1].split(';')
            except:
                continue
            for contents in shab_messages:
                names = contents.split(',')
                fname = ""
                lname = ""
                for name in names:
                    name = name.strip()
                    if lname == "" and name[0].isupper():
                        lname = name
                    elif name[0].isupper():
                        fname = name
                    else:
                        break
                print("Company Name: {}".format(company_name))
                print("Company Street: {}".format(company_street))
                print("Postal Code: {}".format(postal_code))
                print("City: {}".format(city))
                print("C/O: {}".format(c_o))
                print("First Name: {}".format(fname))
                print("Last Name: {}".format(lname))
                dataset = [company_name, company_street, postal_code, city, c_o, lname, fname, ""]
                saveData(dataset)


if __name__ == "__main__":
    publication_start = "2024-12-01"
    publication_end = "2024-12-08"
    searchZefix(publication_start, publication_end)
