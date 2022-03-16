import os
import xmlschema
import requests

STATUS_NONE = '0'
STATUS_FULL = '1'
STATUS_REPOSITORY = '2'

OUTPUT_FILE_NAME = "scopus-open-access-analysert.txt"
EXCEPTION_FILE_NAME = "scopus-open-access-exceptions.txt"

PDF_LINK_KEY_NAME = 'xocs:upw-url_for_pdf'

number_open_access_none = 0
number_open_access_repository = 0
number_open_access_full = 0

has_pdf_link = 0
content_types = {'application/pdf'}
licenses = {'cc-by'}
content_lengths = []
dead_pdf_link = 0
does_not_have_pdf_link = 0
has_license_set = 0


def no_access():
  global number_open_access_none
  number_open_access_none = number_open_access_none + 1
  return False


def has_open_access(meta_object):
  if 'xocs:open-access' not in meta_object:
    return no_access()
  xocs_open_access_field = meta_object['xocs:open-access']
  if 'xocs:oa-article-status' not in xocs_open_access_field:
    return no_access()
  status_object = xocs_open_access_field['xocs:oa-article-status']
  if '@is-open-access' not in status_object:
    return no_access()
  status = status_object['@is-open-access']
  if status == STATUS_NONE:
    return no_access()
  elif status == STATUS_FULL:
    global number_open_access_full
    number_open_access_full = number_open_access_full + 1
    return True
  else:
    global number_open_access_repository
    number_open_access_repository = number_open_access_repository + 1
    return True


def get_file_url(best_open_access_location):
  if PDF_LINK_KEY_NAME in best_open_access_location and \
      best_open_access_location[PDF_LINK_KEY_NAME] is not None:
    global has_pdf_link
    has_pdf_link = has_pdf_link + 1
    return best_open_access_location[PDF_LINK_KEY_NAME]
  else:
    global does_not_have_pdf_link
    does_not_have_pdf_link = does_not_have_pdf_link + 1
    return best_open_access_location['xocs:upw-url']


def fetch_file_information(file_url):
  info = requests.head(file_url, allow_redirects=True)
  print(info)
  if info.status_code != 200:
    global dead_pdf_link
    dead_pdf_link = dead_pdf_link + 1
  else:
    if 'Content-length' in info.headers:
      content_length = info.headers['Content-length']
      content_lengths.append(int(content_length))
    if 'Content-Type' in info.headers:
      content_type = info.headers['Content-Type']
      content_types.add(content_type)


def check_license(open_access_object):
  license = open_access_object['xocs:upw-license']
  if license is not None:
    global has_license_set
    has_license_set = has_license_set + 1
    licenses.add(license)


def read_file_from_open_access(open_access_object):
  upw = open_access_object['xocs:upw-open-access']
  best_open_access_location = upw['xocs:upw-best_oa_location']
  file_url = get_file_url(best_open_access_location)
  check_license(best_open_access_location)
  fetch_file_information(file_url)


def print_summary():
  f = open(OUTPUT_FILE_NAME, "a")
  total_files = 'Total files: ' + str(number_of_files) + "\n"
  access_full = 'Percentage open access Full: ' + str(
    (number_open_access_full / number_of_files) * 100) + "%\n"
  access_repository = 'Percentage open access Repository: ' + str(
    (number_open_access_repository / number_of_files) * 100) + '\n'
  access_none = 'Percentage open access None: ' + str(
    (number_open_access_none / number_of_files) * 100) + '%\n'
  supplied_pdf_link = 'Percentage of all files that has pdf link: ' + str(
    (has_pdf_link / number_of_files) * 100) + '%\n'
  content_types_in_files = 'Actual content type of pdf links: '
  for content_type in content_types:
    content_types_in_files = content_types_in_files + ', ' + content_type
  dead_links = '\nDead pdf links (not including redirecting links, percentage of ' + 'pdf_links ' + str(
    (dead_pdf_link / has_pdf_link) * 100) + '\n'
  percentage_license = 'Percentage of open access files with license: ' + str(
    (has_license_set / (
        number_open_access_full + number_open_access_repository)) * 100) + '%\n'
  licenses_used = 'License used: '
  for license in licenses:
    licenses_used = licenses_used + ', ' + license
  mean_content_length = '\nMean content lengt in bytes: ' + str(
    sum(content_lengths) / len(content_lengths)) + '\n'
  f.write(total_files)
  f.write(access_full)
  f.write(access_repository)
  f.write(access_none)
  f.write(supplied_pdf_link)
  f.write(content_types_in_files)
  f.write(dead_links)
  f.write(percentage_license)
  f.write(licenses_used)
  f.write(mean_content_length)
  f.close()


def process_file(file):
  xs.validate(file)
  doc_tp = xs.to_dict(file)
  meta_object = doc_tp['xocs:meta']
  if has_open_access(meta_object):
    open_access_object = meta_object['xocs:open-access']
    read_file_from_open_access(open_access_object)


def store_exception(inst, file):
  f = open(EXCEPTION_FILE_NAME, "a")
  f.write('Exception in file' + file)
  f.write(str(inst))
  f.write('\n\n\n')
  f.close()
  print('exception in file', file)
  print(inst)


'''resource_path = "../resources"
csv_file_name = "doi_and_title_text.csv"
files = os.listdir(resource_path)
'''

print('starting')
resource_path = "../resources"
files = os.listdir(resource_path)
number_of_files = len(files)
xs = xmlschema.XMLSchema(
  'https://schema.elsevier.com/dtds/document/abstracts/xocs-ani515.xsd')

for file in files:
  try:
    file_path = resource_path + "/" + file
    process_file(file_path)
  except Exception as inst:
    store_exception(inst, file)

print_summary()

print('done')
