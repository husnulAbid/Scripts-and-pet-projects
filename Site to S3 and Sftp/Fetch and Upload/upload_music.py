import os
import glob
import pysftp as sftp
from boto3.session import Session


class Upload_Music:

    def __init__(self, s3_bucket_url, s3_access_key, s3_secret_key, output_folder, input_date, custom_delim, is_upload_mp3_to_sftp):
        self.s3_bucket_url = s3_bucket_url
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key
        self.output_folder = output_folder
        self.input_date = input_date
        self.custom_delim = custom_delim
        self.is_upload_mp3_to_sftp = is_upload_mp3_to_sftp

        self.bucket = self.connect_S3_bucket()


    def connect_S3_bucket(self):
        session = Session(
            aws_access_key_id=self.s3_access_key,
            aws_secret_access_key=self.s3_secret_key
        )

        s3 = session.resource('s3', endpoint_url=self.s3_bucket_url)
        connected_bucket = s3.Bucket(self.input_date)

        return connected_bucket


    def clear_text_file(self, input_file):
        f = open(input_file, 'r+')
        f.truncate(0)


    def append_in_text_file(self, file_name, input_str):
        with open(file_name, 'a') as myfile:
            myfile.write(input_str + '\n')


    def upload_process(self, sftp_host, sftp_port, sftp_username, sftp_password):
        print('\n\nAt upload process....')

        upload_S3_issue_file = 'issue_s3_upload.txt'
        upload_Sftp_issue_file = 'issue_sftp_upload.txt'
        self.clear_text_file(upload_S3_issue_file)
        self.clear_text_file(upload_Sftp_issue_file)
        
        all_files = glob.glob(self.output_folder + '*')
        total_files = len(all_files)
        
        file_count = 0
        for file in all_files:
            file_count = file_count + 1
            both_upload = True
            filename, file_extension = os.path.splitext(file)


            ################ upload to S3 #################

            try:
                file_basename = os.path.basename(file)
                s3_file_path = str(file_basename).replace(self.custom_delim, '/')
            except:
                file_basename - ''
                s3_file_path = ''

            if s3_file_path:
                print(f'\nUploading {file_extension} file to S3 {file_count} out of {total_files}')
                try:
                    self.bucket.upload_file(file, s3_file_path)
                except:
                    both_upload = False
                    error_msg = f"\nError S3 !! can not upload {file} file"
                    print(error_msg)
                    self.append_in_text_file(upload_S3_issue_file, error_msg)
            else:
                both_upload = False
                error_msg = f"\nError S3 !! can not change filename for {file}"
                print(error_msg)
                self.append_in_text_file(upload_S3_issue_file, error_msg)
            

            ################ upload to sftp #################

            if file_extension == '.mp3' and self.is_upload_mp3_to_sftp:
                try:
                    print(f'\nUploading {file_extension} file to Sftp {file_count} out of {total_files}')

                    cnopts = sftp.CnOpts()
                    cnopts.hostkeys = None
                        
                    with sftp.Connection(host=sftp_host, username=sftp_username, password=sftp_password, port=sftp_port, cnopts=cnopts) as sftp_server:
                        sftp_server.cwd('/')
                        sftp_server.put(file)
                except:
                    both_upload = False
                    error_msg = f"\nError Sftp !! can not upload {file} file"
                    print(error_msg)
                    self.append_in_text_file(upload_Sftp_issue_file, error_msg)
            

            ################ remove from local #################

            if both_upload:
                os.remove(file)
        
        print('\n\n\nFile uploaded ...!!')
