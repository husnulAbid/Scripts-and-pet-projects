from fetch_music import Fetch_Music
from upload_music import Upload_Music


if __name__ == '__main__':
    input_date = '2022-05-03'

    input_email = ''                    # HeyDj user email
    input_pass = ''                                     # HeyDj user password

    s3_bucket_url = ''
    s3_access_key = ''
    s3_secret_key = ''

    sftp_host = ''                                      # should be string
    sftp_port = 2222                                                # should be integer
    sftp_username = ''
    sftp_password = ''

    is_download_needed = 1                                          # 0 or 1
    is_lossless_file_needed = 1                                     # 0 or 1   
    
    is_upload_needed = 0                                            # 0 or 1
    is_upload_mp3_to_sftp = 1                                       # 0 or 1
    
    max_iteration_time = 60                                         # x * 5 sec  - any integer number
    
    custom_delim = '$__$__$'
    output_folder = 'outputs/'                                      # might be  'outputs/' in ubuntu

    chrome_driver_local_path = 'C:\chromedriver.exe'
    output_folder_full_path = '<secret_path>\\<secret name>\\1 - Song Download'             # Put the full path for the output folder


    if is_download_needed:
        Fetch_Music(is_upload_needed, max_iteration_time, is_lossless_file_needed, custom_delim).start_process(chrome_driver_local_path, input_date, input_email, input_pass, output_folder, output_folder_full_path)
    
    if is_upload_needed:
        Upload_Music(s3_bucket_url, s3_access_key, s3_secret_key,  output_folder, input_date, custom_delim, is_upload_mp3_to_sftp).upload_process(sftp_host, sftp_port, sftp_username, sftp_password)
