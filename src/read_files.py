import os
import re
import csv

resource_path = "../resources"
csv_file_name = "doi_and_title_text.csv"
files = os.listdir(resource_path)
mathing_files = []
csv_file = open(csv_file_name, 'w')

csv_writer = csv.writer(csv_file, delimiter=",")
csv_writer.writerow(('doi', 'title'))

for file in files:
    f = open(resource_path + "/" + file, mode="r", encoding="utf-8")
    read_f = f.read().replace('\n', '')
    doi_match = re.search("<xocs:doi>.*</xocs:doi>", read_f)
    citation_title_match = re.search("<titletext.*</titletext", read_f)
    citation_title_sup_match = re.search("<titletext.*<sup>.*</titletext>", read_f)
    citation_title_inf_match = re.search("<titletext.*<inf>.*</titletext>", read_f)
    if citation_title_inf_match or citation_title_sup_match:
        citation_title = citation_title_match.group()
        doi = "does not have doi"
        if doi_match:
            doi = doi_match.group().replace("<xocs:doi>", "").replace("</xocs:doi>", "")
        csv_writer.writerow((doi, citation_title))
        print(doi, citation_title)
    f.close()

csv_file.close()
