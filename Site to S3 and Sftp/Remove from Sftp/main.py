from remove_from_sftp import Remove_Music


if __name__ == '__main__':
    input_date = '2022-05-04'               # Delete all files before this date (yyyy-mm-dd)

    sftp_host = ''              # should be string
    sftp_port = 2222                        # should be integer
    sftp_username = ''
    sftp_password = ''

    Remove_Music(sftp_host, sftp_port, sftp_username, sftp_password).remove_process(input_date)
