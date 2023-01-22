import os
import json
import time
import glob
import shutil
from bs4 import BeautifulSoup
from selenium import webdriver


class Fetch_Music:

    def __init__(self, is_upload_to_s3, max_iteration, is_lossless_file_needed, custom_delim):
        self.is_upload_to_s3 = is_upload_to_s3 
        self.max_iteration = max_iteration 
        self.is_lossless_file_needed = is_lossless_file_needed
        self.custom_delim = custom_delim


    def append_in_text_file(self, file_name, input_str):
        with open(file_name, 'a') as myfile:
            myfile.write(input_str + '\n')
    

    def clear_text_file(self, input_file):
        f = open(input_file, 'r+')
        f.truncate(0)
    

    def wait_for_downloads(self, output_folder, track_name, download_issue_file):
        current_iteration = 0

        while any([filename.endswith(".crdownload") for filename in os.listdir(output_folder)]):
            time.sleep(5)

            current_iteration = current_iteration + 1
            if current_iteration >= self.max_iteration:
                error_msg = f"\nAborting !! Too long time for {track_name} file, change max_iteration_time.\n"
                print(error_msg)
                self.append_in_text_file(download_issue_file, error_msg)
                break


    def latest_download_file(self, folder_name):
        time.sleep(1)

        list_of_files = glob.glob(folder_name + '/*')
        latest_file = max(list_of_files, key=os.path.getctime)

        return latest_file


    def login_page(self, driver, date, email, password):
        driver.get('https://heydj.pro/#/')
        time.sleep(2)

        email_xpath = '//*[@id="login"]'
        email_field = driver.find_element('xpath', email_xpath)
        email_field.send_keys(email)
        time.sleep(1)

        password_xpath = '//*[@id="password"]'
        password_field = driver.find_element('xpath', password_xpath)
        password_field.send_keys(password)
        time.sleep(1)

        login_button_xpath = '//*[@id="rec-app"]/div/div[3]/div/div[1]/div/div[2]/span/form/button'
        login_button = driver.find_element('xpath', login_button_xpath)
        login_button.click()
        time.sleep(2)

        list_page_url = f'https://srv.heydj.pro/#/media/promo?date={date}'
        driver.get(list_page_url)
        time.sleep(5)

        if driver.current_url != list_page_url:
            return False
        
        return True
    

    def read_json(self, driver, date):
        json_url = f'https://srv.heydj.pro/a/ms/section/promo/media?date={date}&mp3prefered=true&popular_order=true'

        try:
            driver.get(json_url)
            time.sleep(5)
        
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            json_output = json.loads(soup.find('body').text)
            is_json_output = True
        except:
            json_output = ''
            is_json_output = False
        
        return is_json_output, json_output

    
    def rename_both_files(self, output_folder, latest_file, track_name, download_issue_file):
        latest_file_base = os.path.basename(latest_file)
        latest_file_name = os.path.splitext(latest_file_base)[0]

        current_path_file_1 = output_folder + latest_file_name + '.mp3'
        current_path_file_2 = output_folder + latest_file_name + '.aiff'
        
        new_path_file_1 = output_folder + track_name + '.mp3'
        new_path_file_2 = output_folder + track_name + '.aiff'
        
        try:
            os.rename(current_path_file_1, new_path_file_1)
        except:
            error_msg = f"\nWarning !! 'Mp3' file does not exist for {track_name}\n"
            print(error_msg)
            self.append_in_text_file(download_issue_file, error_msg)
        
        if self.is_lossless_file_needed:
            try:
                 os.rename(current_path_file_2, new_path_file_2)
            except:
                error_msg = f"\nWarning !! 'Aiff' file does not exist for {track_name}\n"
                print(error_msg)
                self.append_in_text_file(download_issue_file, error_msg)


    def count_tracks(self, releases):
        total_tracks = 0

        for release in releases:
            tracks = release['tracks']
            total_tracks = total_tracks + len(tracks)
        
        return total_tracks
    

    def download_track(self, driver, track_id):
        driver.get(f'https://srv.heydj.pro/dwnld/track/{track_id}.mp3')
        time.sleep(1)
            
        if self.is_lossless_file_needed:
            driver.get(f'https://srv.heydj.pro/dwnld/track/{track_id}.aiff')
            time.sleep(1)



    def download_music_process(self, driver, json_data, output_folder, download_issue_file):
        total_tracks = 0

        try:
            releases = json_data['releases']
            total_tracks = self.count_tracks(releases)
        except:
            raise Exception(f'\nNo releases attribute in json data')
        
        if not total_tracks:
            raise Exception(f'\nNo tracks available to download')

        track_count = 0
        for release in releases:
            tracks = []

            try:
                release_name = str(release['nm']).strip()
                print('\n\nCurrent Album: ', release_name)
                tracks = release['tracks']
            except:
                error_msg = f"\nError for release id: {release['id']}\n"
                print(error_msg)
                self.append_in_text_file(download_issue_file, error_msg)

            for track in tracks:
                track_count = track_count + 1

                try:
                    track_id = track['id']
                    track_artist = str(track['artist']).strip()
                    track_title = str(track['title']).strip()
                    track_subtitle = str(track['subtitle']).strip()
                    track_pubdate = str(track['pubdate']).strip()

                    if self.is_upload_to_s3:
                        if track_subtitle.lower() != 'none':
                            track_name = release_name + self.custom_delim + track_artist + ' - ' + track_title + ' (' + track_subtitle + ')' + ' ' + track_pubdate
                        else:
                            track_name = release_name + self.custom_delim + track_artist + ' - ' + track_title + ' ' + track_pubdate
                    else:
                        if track_subtitle.lower() != 'none':
                            track_name = track_artist + ' - ' + track_title + ' (' + track_subtitle + ')' + ' ' + track_pubdate
                        else:
                            track_name = track_artist + ' - ' + track_title + ' ' + track_pubdate
                            
                    print(f'Downloading {track_count} out of {total_tracks} tracks.....')

                    self.download_track(driver, track_id)
                    self.wait_for_downloads(output_folder, track_name, download_issue_file)
                    latest_file = self.latest_download_file(output_folder)
                    self.rename_both_files(output_folder, latest_file, track_name, download_issue_file)
                except:
                    error_msg = f"\nError for track: {track['fullnm']} in {release['id']}\n"
                    print(error_msg)
                    self.append_in_text_file(download_issue_file, error_msg)


    def start_process(self, chrome_driver_local_path, input_date, input_email, input_pass, output_folder, output_folder_full_path):
        
        download_issue_file = 'issue_download.txt'
        self.clear_text_file(download_issue_file)

        try:
            shutil.rmtree(output_folder)
        except:
            temp = 'do_nothing'

        try:
            os.mkdir(output_folder)
        except:
            raise Exception(f'Can not create a folder named {output_folder}')

        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : f'{output_folder_full_path}'}
        chrome_options.add_experimental_option('prefs', prefs)
        # chrome_options.add_argument('--headless')     #######################################

        driver = webdriver.Chrome(executable_path=chrome_driver_local_path, chrome_options=chrome_options)
        driver.maximize_window()
        
        print(f'\nScraping for  Date: {str(input_date)}\n\n\nLoging....')
        is_login_succssful = self.login_page(driver, date=input_date, email=input_email, password=input_pass)

        if is_login_succssful:
            print('\nLogin successful !! Processing....')
            is_json_output, json_output = self.read_json(driver, input_date)

            if is_json_output:
                print('\nFetched json !! Downloading music....')
                if json_output:
                    self.download_music_process(driver, json_output, output_folder, download_issue_file)
                    print(f'\n\n\nDownloaded tracks succesfully..!!')
                else:
                    raise Exception('\nNo json data found ...!!!')
            else:
                raise Exception('\nError !! Fetching json unsuccessful !!')
        else:
            raise Exception('\nError !! Login unsuccessful !! (username, password, date can be wrong)')

        driver.close()