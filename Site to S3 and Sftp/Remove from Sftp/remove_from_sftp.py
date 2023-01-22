import os
import re
import sys
import datetime
import pysftp as sftp

sys.tracebacklimit = 0


class Remove_Music:

    def __init__(self, sftp_host, sftp_port, sftp_username, sftp_password):
        self.sftp_host = sftp_host
        self.sftp_port = sftp_port
        self.sftp_username = sftp_username
        self.sftp_password = sftp_password
        self.log_file = 'log_failed.txt'


    def append_in_text_file(self, file_name, input_str):
        with open(file_name, 'a') as myfile:
            myfile.write(input_str + '\n')
    

    def clear_text_file(self, input_file):
        f = open(input_file, 'r+')
        f.truncate(0)


    def log_message(self, msg, filename=None):
        print(msg)

        if filename is not None:
            self.append_in_text_file(filename, msg)


    def get_file_date(self, file):
        file_name = os.path.splitext(file)[0]
        str_date = str(file_name).split()[-1]

        try:
            date = datetime.datetime.strptime(str_date, "%Y-%m-%d").date()
        except:
            # Making bigger as I don't wanna remove other files who doesn't have date
            str_date = '2500-12-31'
            date = datetime.datetime.strptime(str_date, "%Y-%m-%d").date()
        
        return date

    
    def get_removable_files_from_sftp(self, str_input_date):
        input_date = datetime.datetime.strptime(str_input_date, "%Y-%m-%d").date()
        removable_files = []

        cnopts = sftp.CnOpts()
        cnopts.hostkeys = None
        
        try:
            with sftp.Connection(host=self.sftp_host, username=self.sftp_username, password=self.sftp_password, port=self.sftp_port, cnopts=cnopts) as sftp_server:
                sftp_server.cwd('/')
                filelist = sftp_server.listdir()
        except:
            raise Exception('\n\nWrong Sftp credentials..!!')

        for file in filelist:
            file_date = self.get_file_date(file)
            if file_date < input_date:
                removable_files.append(file)
        
        return removable_files
    

    def remove_files_from_sftp(self, removable_files):
        print(f'\n\nThere are {len(removable_files)} files to delete...\n\n\nRemoving......\n\n')
        
        cnopts = sftp.CnOpts()
        cnopts.hostkeys = None

        with sftp.Connection(host=self.sftp_host, username=self.sftp_username, password=self.sftp_password, port=self.sftp_port, cnopts=cnopts) as sftp_server:
            sftp_server.cwd('/')
            for file in removable_files:
                try:
                    sftp_server.remove(file)
                except:
                    self.log_message(f'Error on removing file {file}\n', self.log_file)


    def remove_process(self, str_input_date):
        print(f'\nInput date: {str_input_date}')

        self.clear_text_file(self.log_file)
        removable_files = self.get_removable_files_from_sftp(str_input_date)

        if removable_files:
            self.remove_files_from_sftp(removable_files)
            print('\n\nRemoved successfully..!!')
        else:
            print('\n\nThere is no file to delete.')