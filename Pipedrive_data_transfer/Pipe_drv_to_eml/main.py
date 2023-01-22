import os
import glob
import json
import string
import requests
import datetime
from pytz import timezone
from requests.api import get
from bs4 import BeautifulSoup
from urllib.request import urlopen

from email.mime.base import MIMEBase
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

import s3Operations


def get_all_deals():
    return f'{pd_base_url}/api/v1/deals'


def get_mail_msg_url(deal_id):
    return f'{pd_base_url}/api/v1/deals/{deal_id}/mailMessages'


def delete_from_local_folder():
    files = glob.glob(temp_folder + '*')

    for file in files:
        os.remove(file)


def check_parameters():
    if not aws_access_id:
        raise Exception("aws_access_id not given")
    
    if not aws_access_secret_key:
        raise Exception("aws_access_secret_key not given")

    if not aws_bucket_name:
        raise Exception("aws_bucket_name not given")


def check_s3_connection():
    if s3_operations.bucket.creation_date:
        print()
    else:
        log_file.close()
        delete_from_local_folder()
        if os.path.isdir(temp_folder_name) : os.removedirs(temp_folder_name)
        raise Exception("The bucket name, access id or key is invalid")


def get_deal_account_and_application_id(deal):
    deal_id = deal['id']
    account_id = ''
    application_id = ''

    try:
        account_id = deal[pd_guid_account_id]
        application_id = deal[pd_guid_application_id]
    except:
        print('!!! Error on fetching deal id or account or application id for deal: ', deal_id)

    return deal_id, account_id, application_id


def download_file_from_pipe_drive(deal_id, file_name, download_url):
    dowloaded_file_path = ''

    try:
        get_response = requests.get(download_url, params=token)
        f_in = get_response.content

        dowloaded_file_path = temp_folder + file_name

        with open(dowloaded_file_path, 'wb') as f_out:
            f_out.write(f_in)
    except:
        log_file.write(f'Error on deal id: {deal_id} for file downloading: {download_url}\n')
    
    return dowloaded_file_path


def get_email_name(mail_msg_date, mail_msg_subject):
    first_n_words = 5

    try:
        subject_first_words = ' '.join(mail_msg_subject.split()[:first_n_words])
        subject_first_words_without_punc = subject_first_words.translate(str.maketrans('', '', string.punctuation))
        email_name = str(mail_msg_date) + ' ; ' + subject_first_words_without_punc
    except:
        email_name = 'No Subject'
    
    return email_name


def make_s3_dir_path(deal_id, account_id, application_id, email_name):
    s3_upload_dir_path = ''
    
    if deal_id:
        if not account_id and not application_id:
            s3_upload_dir_path = s3_base_folder + 'Others' + '/' + str(deal_id) + '/' + 'No Account Id' + '/' + 'No Application Id' + '/' + 'emails' + '/' + email_name + '/'
        elif not account_id and application_id:
            s3_upload_dir_path = s3_base_folder + 'Others' + '/' + str(deal_id) + '/' + 'No Account Id' + '/' + str(application_id) + '/' + 'emails' + '/' + email_name + '/'
        elif account_id and not application_id:
            s3_upload_dir_path = s3_base_folder + str(account_id) + '/' + 'No Application Id' + '/' + 'emails' + '/' + email_name + '/'
        else:
            s3_upload_dir_path = s3_base_folder + str(account_id) + '/' + str(application_id) + '/' + 'emails' + '/' + email_name + '/'
    else:
        s3_upload_dir_path = s3_base_folder + 'Others' + '/' + 'Not In Deal' + '/' + 'emails' + '/' + email_name + '/'

    return s3_upload_dir_path


def trigger_upload_to_s3(deal_id, dowloaded_file_path, s3_upload_path):
    is_successfuly_uploaded = True

    try:
        s3_operations.upload_file(dowloaded_file_path, s3_upload_path)
    except:
        is_successfuly_uploaded = False
        log_file.write(f'Error on deal id: {deal_id} for uploading file: {s3_upload_path}\n')

    return is_successfuly_uploaded


def get_deals_data(start_item, limit):
    fetch_data_token = {
        'api_token': f'{pd_api_token}',
        'start': f'{start_item}',
        'limit': f'{limit}'
    }

    all_deals = ''
    is_more_item = True
    is_fetched_data = True
    deals_url = get_all_deals()

    try:
        get_response = requests.get(deals_url, params=fetch_data_token)
        get_content = json.loads(get_response.content)
        all_deals = get_content['data']
        is_more_item = get_content['additional_data']['pagination']['more_items_in_collection']
    except:
        is_fetched_data = False
        log_file.write(f'Error on fetching files from {start_item} to {start_item+limit}\n')
        print(f'!!! Error on fetching files from {start_item} to {start_item+limit}')
    
    return is_fetched_data, all_deals, is_more_item


def get_mail_msg_data(deal_id):
    mail_msg_url = get_mail_msg_url(deal_id)
    mail_msg = ''
    is_success = False

    try:
        get_mail_msg_response = requests.get(mail_msg_url, params=token)
        get_mail_msg_content = json.loads(get_mail_msg_response.content)
        mail_msg = get_mail_msg_content['data']
        is_success = True
    except:
        print('Error on mail msg api call')
    
    return is_success, mail_msg


def get_body_text(url):
    try:
        html = urlopen(url).read()
        soup = BeautifulSoup(html, features='html.parser')
        text = soup.get_text()
        text = text.replace('\n', '<br>')
    except:
        soup = ''
        text = ''
    
    try:
        all_links = ''
        for link in soup.find_all('a', href=True):
            all_links = all_links + link['href'] + '<br>'
    except:
        all_links =  ''
    
    try:
        text = text + '<br><br>Links from this email (not part of main mail body): <br>' + all_links
    except:
        text = text

    return text


def array_to_email_address(arr):
    all_email = ''
    for obj in arr:
        try:
            email_address = obj['email_address'] + ' ; '
        except:
            email_address = ''

        all_email = all_email + email_address
    
    return all_email


def get_email_attachments(deal_id, mail_msg_attachments):
    email_attachments_locations = []
    for attachment in mail_msg_attachments:
        try:
            file_name = attachment['name']
            download_url = attachment['url']
        except:
            file_name = ''
            download_url = ''

        if file_name and download_url:
            downloaded_path = download_file_from_pipe_drive(deal_id, file_name, download_url)
            email_attachments_locations.append(downloaded_path)
    
    return email_attachments_locations


def add_email_attachment(msg, attached_file):
    attachment = open(attached_file, "rb")
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    part.add_header('Content-Disposition', 'attachment; filename=' + attached_file)
    encoders.encode_base64(part)
    msg.attach(part)
    return msg


def make_elm_file(email_from, email_to, email_subject, email_body, email_cc, email_bcc, attached_files):    
    msg = MIMEMultipart('mixed')
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = email_subject
    msg['Cc'] = email_cc
    msg['Bcc'] = email_bcc

    part = MIMEText(email_body, 'html')
    msg.attach(part)

    for attached_file in attached_files:
        try:
            msg = add_email_attachment(msg, attached_file)
        except:
            temp = 5  # no action required; dummy except

    return msg
    

def save_email_msg_as_eml(email_elm_raw, email_name):
    email_file = temp_folder + email_name + '.eml'

    try:
        with open(email_file, 'w') as outfile:
            gen = generator.Generator(outfile)
            gen.flatten(email_elm_raw)
    except:
        email_file = ''

    return email_file


def make_email_file_and_uplaod_s3(deal_id, mail_msg_data, mail_msg_subject, email_name, s3_upload_dir_path):
    is_upload_successful = False

    email_from = array_to_email_address(mail_msg_data['from'])
    email_to = array_to_email_address(mail_msg_data['to'])
    email_cc = array_to_email_address(mail_msg_data['cc'])
    email_bcc = array_to_email_address(mail_msg_data['bcc'])

    mail_msg_body_url = mail_msg_data['body_url']
    email_body = get_body_text(mail_msg_body_url)

    mail_msg_attachments = mail_msg_data['attachments']
    email_attachments_locations = get_email_attachments(deal_id, mail_msg_attachments)

    try:
        email_elm_raw = make_elm_file(email_from, email_to, mail_msg_subject, email_body, email_cc, email_bcc, email_attachments_locations)
    except:
        email_elm_raw = ''
    
    if email_elm_raw:
        email_file_loc = save_email_msg_as_eml(email_elm_raw, email_name)
    
    if email_file_loc:
        s3_upload_full_path = s3_upload_dir_path + email_name + '.eml'
        is_upload_successful = trigger_upload_to_s3(deal_id, email_file_loc, s3_upload_full_path)

    if is_upload_successful:        # Deleting all files
        if os.path.exists(email_file_loc) : os.remove(email_file_loc)
        for attach_file in email_attachments_locations:
            if os.path.exists(attach_file) : os.remove(attach_file)


def pipe_drive_to_s3_bucket():
    start_item = 0
    limit = 100

    while True:
        is_fetched_data, all_deals, is_more_item = get_deals_data(start_item, limit)

        if is_fetched_data:
            print(f'Deal processing between {start_item} to {start_item + limit}')

            for deal in all_deals:
                deal_id, account_id, application_id = get_deal_account_and_application_id(deal)

                is_success, all_mail_msg = get_mail_msg_data(deal_id)
                if is_success:
                    for mail_msg in all_mail_msg:
                        try:
                            mail_msg_data = mail_msg['data']
                            mail_msg_subject = mail_msg_data['subject']
                            mail_msg_date = mail_msg['timestamp'].split(" ", 1)[0]
                        except:
                            mail_msg_data = ''
                            mail_msg_subject = '_not_found'
                            mail_msg_date = '1900-01-01'
                        
                        if mail_msg_data:
                            email_name = get_email_name(mail_msg_date, mail_msg_subject)
                            s3_upload_dir_path = make_s3_dir_path(deal_id, account_id, application_id, email_name)
                            
                            try:
                                make_email_file_and_uplaod_s3(deal_id, mail_msg_data, mail_msg_subject, email_name, s3_upload_dir_path)
                            except:
                                print(f'Error on deal id : {deal_id}, email name : {email_name}')

        start_item = start_item + limit
        if not is_more_item:
            break


def start_process():
    print('Start Processing.....\nPlease wait.....')
    pipe_drive_to_s3_bucket()
    print('\nFinished All. Please view the log file')


if __name__ == '__main__':

    pd_base_url = 'https://swishfund-secret.pipedrive.com'
    pd_api_token = ''

    pd_guid_account_id = ''
    pd_guid_application_id = ''

    aws_access_id = ''
    aws_access_secret_key = ''
    aws_bucket_name = ''
    aws_region = ''

    s3_base_folder = 'temp/'       # Please Put a forward-slash after the folder name '/'

    #-----------------------------------------------------------------------------------------#

    check_parameters()

    output_time = str(datetime.datetime.now(timezone('Europe/Amsterdam')).strftime("%Y_%m_%d_%H-%M-%S"))

    token = {
        'api_token': f'{pd_api_token}'
    }

    temp_folder_name = 'temporary_' + output_time
    temp_folder = temp_folder_name + '/'
    os.makedirs(temp_folder_name)

    log_file_name = temp_folder + '!log_file.txt'
    log_file = open(log_file_name,'w')

    body_url_file_name = 'body.txt'

    s3_operations = s3Operations.S3Operations(aws_access_id, aws_access_secret_key, aws_bucket_name)
    check_s3_connection()
    start_process()
