import os
import glob
import uuid
import json
import requests
import datetime
from pytz import timezone
from requests.api import get

import s3Operations


def get_files_url():
    return f'{pd_base_url}/api/v1/files'


def get_deal_url(deal_id):
    return f'{pd_base_url}/api/v1/deals/{deal_id}'


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


def check_s3_connection(s3_operations):
    if s3_operations.bucket.creation_date:
        print()
    else:
        log_file.close()
        delete_from_local_folder()
        if os.path.isdir(temp_folder_name) : os.removedirs(temp_folder_name)
        raise Exception("The bucket name, access id or key is invalid")


def get_account_and_application_id(deal_id):
    account_id = ''
    application_id = ''

    if not deal_id:
        return account_id, application_id

    files_url = get_deal_url(deal_id)

    try:
        get_response = requests.get(files_url, params=token)
        get_content = json.loads(get_response.content)
        get_deal = get_content['data']

        account_id = get_deal[pd_guid_account_id]
        application_id = get_deal[pd_guid_application_id]
    except:
        print('!!! Error on fetching account or application id for deal: ', deal_id)

    return account_id, application_id


def download_file_from_pipe_drive(file_name, download_url):
    dowloaded_file_path = ''

    try:
        get_response = requests.get(download_url, params=token)
        f_in = get_response.content

        dowloaded_file_path = temp_folder + file_name

        with open(dowloaded_file_path, 'wb') as f_out:
            f_out.write(f_in)
    except:
        log_file.write(f'Error on downloading: {download_url}\n')
    
    return dowloaded_file_path


def make_s3_path(deal_id, account_id, application_id, file_name):
    if deal_id:
        if not account_id and not application_id:
            s3_upload_path = s3_base_folder + 'Others' + '/' + str(deal_id) + '/' + 'No Account Id' + '/' + 'No Application Id' + '/' + file_name
        elif not account_id and application_id:
            s3_upload_path = s3_base_folder + 'Others' + '/' + str(deal_id) + '/' + 'No Account Id' + '/' + str(application_id) + '/' + file_name
        elif account_id and not application_id:
            s3_upload_path = s3_base_folder + str(account_id) + '/' + 'No Application Id' + '/' + file_name
        else:
            s3_upload_path = s3_base_folder + str(account_id) + '/' + str(application_id) + '/' + file_name
    else:
        s3_upload_path = s3_base_folder + 'Others' + '/' + 'Not In Deal' + '/' + file_name

    return s3_upload_path


def trigger_upload_to_s3(s3_operations, dowloaded_file_path, s3_upload_path):
    is_successfuly_uploaded = True

    try:
        s3_operations.upload_file(dowloaded_file_path, s3_upload_path)
    except:
        is_successfuly_uploaded = False
        log_file.write(f'Error on uploading file: {s3_upload_path}\n')

    return is_successfuly_uploaded


def pipe_drive_to_s3_bucket():
    s3_operations = s3Operations.S3Operations(aws_access_id, aws_access_secret_key, aws_bucket_name)
    check_s3_connection(s3_operations)

    files_url = get_files_url()
    start_file_item = 0

    total_file_to_process = 0
    successfully_processed = 0

    while True:
        is_more_item = False
        is_fetched_file = True

        fetch_data_token = {
            'api_token': f'{pd_api_token}',
            'start': f'{start_file_item}'
        }

        try:
            get_response = requests.get(files_url, params=fetch_data_token)
            get_content = json.loads(get_response.content)
            all_files = get_content['data']
            is_more_item = get_content['additional_data']['pagination']['more_items_in_collection']
        except:
            is_fetched_file = False
            log_file.write(f'Error on fetching files from {start_file_item} to {start_file_item+100}\n')
            print(f'!!! Error on fetching files from {start_file_item} to {start_file_item+100}')

        if is_fetched_file:
            for i, file in enumerate(all_files):
                file_name = ''
                download_url = ''
                deal_id = ''

                try:
                    file_name = file['name']
                    download_url = file['url']
                    deal_id = file['deal_id']
                except:
                    print('!!! Error for file no: ', start_file_item+i+1, '\n')

                if deal_id and file_name and download_url:
                    account_id, application_id = get_account_and_application_id(deal_id)
 
                    #If account_id and application_id:
                    total_file_to_process = total_file_to_process + 1
                    dowloaded_file_path = download_file_from_pipe_drive(file_name, download_url)
                    
                    if dowloaded_file_path:
                        s3_upload_path = make_s3_path(deal_id, account_id, application_id, file_name)
                        is_successfuly_uploaded = trigger_upload_to_s3(s3_operations, dowloaded_file_path, s3_upload_path)

                        if is_successfuly_uploaded:
                            successfully_processed = successfully_processed + 1

                            if os.path.exists(dowloaded_file_path) : os.remove(dowloaded_file_path)
                        else:
                            print(f'!!! Can not upload for {dowloaded_file_path} with account id: {account_id} and application id: {application_id}')
                    else:
                        print(f'!!! Can not download for {download_url}')
                        
                    #END for if account_id and application_id

            print(f'\nCompleted process for files from id {start_file_item} to {start_file_item+100}')
            print(f'Successfully relocated {successfully_processed} out of {total_file_to_process}')

        start_file_item = start_file_item + 100
        
        if not is_more_item:
            print('\n\nTotal file need to process: ', total_file_to_process)
            print('Total file sucessfully processed: ', successfully_processed)
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

    start_process()
