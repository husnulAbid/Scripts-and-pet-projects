import os
import glob
import json
import requests
import datetime
from pytz import timezone
from requests.api import get
from bs4 import BeautifulSoup
from urllib.request import urlopen

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


def get_email_name(mail_msg_subject):
    first_n_words = 6

    try:
        if mail_msg_subject:
            email_name = ' '.join(mail_msg_subject.split()[:first_n_words])
        else:
            email_name = 'No Subject'
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

        ############################### temp data ####################################
        mail_msg = json.load(open('temp_data.json'))['data']

        is_success = True
    except:
        print('Error on mail msg api call')
    
    return is_success, mail_msg


def make_file_from_body_url(url):
    body_url_file_path = temp_folder + body_url_file_name
    is_successful = False

    try:
        html = urlopen(url).read()
        soup = BeautifulSoup(html, features='html.parser')
        text = soup.get_text()
        is_successful = True
    except:
        text = 'Unable to parse'
        is_successful = False

    with open(body_url_file_path, 'w') as text_file:
        text_file.write(text)

    return is_successful, body_url_file_path


def process_mail_msg_body(deal_id, mail_msg_body_url, s3_upload_dir_path):
    s3_upload_full_path = s3_upload_dir_path + body_url_file_name

    #################################### temp url ########################################
    #mail_msg_body_url = 'https://www.york.ac.uk/teaching/cws/wws/webpage1.html'
    
    is_successful, body_url_file_path = make_file_from_body_url(mail_msg_body_url)

    if is_successful:
        is_upload_successful = trigger_upload_to_s3(deal_id, body_url_file_path, s3_upload_full_path)

        if is_upload_successful:
            if os.path.exists(body_url_file_path) : os.remove(body_url_file_path)
        else:
            print(f'Error on deal id: {deal_id} for uploading file: {s3_upload_full_path}\n')
    else:
        log_file.write(f'Error on deal id: {deal_id} for parsing mail body: {mail_msg_body_url}\n')
        print(f'Error on deal id: {deal_id} for parsing mail body: {mail_msg_body_url}\n')


def process_mail_msg_attachments(deal_id, mail_msg_attachments, s3_upload_dir_path):
    for attachment in mail_msg_attachments:
        try:
            file_name = attachment['name']
            download_url = attachment['url']
        except:
            file_name = ''
            download_url = ''

        if file_name and download_url:
            s3_upload_full_path = s3_upload_dir_path + file_name

            downloaded_path = download_file_from_pipe_drive(deal_id, file_name, download_url)
            if downloaded_path:
                is_upload_successful = trigger_upload_to_s3(deal_id, downloaded_path, s3_upload_full_path)

                if is_upload_successful:
                    if os.path.exists(downloaded_path) : os.remove(downloaded_path)
                else:
                    print(f'Error on deal id: {deal_id} for uploading file: {s3_upload_full_path}\n')
            else:
                print(f'Error on deal id: {deal_id} for file downloading: {download_url}\n')


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
                            mail_msg_body_url = mail_msg_data['body_url']
                            mail_msg_attachments = mail_msg_data['attachments']
                            mail_msg_subject = mail_msg_data['subject']
                        except:
                            mail_msg_body_url = ''
                            mail_msg_attachments = ''
                            mail_msg_subject = ''
                        
                        email_name = get_email_name(mail_msg_subject)
                        s3_upload_dir_path = make_s3_dir_path(deal_id, account_id, application_id, email_name)

                        if mail_msg_body_url:
                            process_mail_msg_body(deal_id, mail_msg_body_url, s3_upload_dir_path)

                        if mail_msg_attachments:
                            process_mail_msg_attachments(deal_id, mail_msg_attachments, s3_upload_dir_path)
        
        start_item = start_item + limit
        if not is_more_item:
            break


def start_process():
    print('Start Processing.....\nPlease wait.....')
    pipe_drive_to_s3_bucket()
    print('\nFinished All. Please view the log file')


if __name__ == '__main__':

    pd_base_url = 'https://swishfund-<secret>.pipedrive.com'
    pd_api_token = ''

    pd_guid_account_id = ''
    pd_guid_application_id = ''

    ################################# temp aws access ########################################
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
