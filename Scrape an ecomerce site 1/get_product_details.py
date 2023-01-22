import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


class Get_Product_details:

    def __init__(self, login_page, home_page, user_email, user_pass, output_csv_file):
        self.login_page = login_page
        self.home_page = home_page
        self.user_email = user_email
        self.user_pass = user_pass
        self.output_csv_file = output_csv_file
        self.is_new_file = True


    def read_from_text_file(self, input_file):
        all_lines = []
        with open(input_file) as f:
            all_lines = [line.rstrip() for line in f]
        
        return all_lines


    def append_in_text_file(self, file_name, input_str):
        with open(file_name, 'a') as myfile:
            myfile.write(input_str + '\n')
    

    def clear_text_file(self, input_file):
        f = open(input_file, 'r+')
        f.truncate(0)


    def login(self, driver):
        driver.get(self.login_page)
        time.sleep(3)

        email_xpath = '//*[@id="email"]'
        email_field = driver.find_element_by_xpath(email_xpath)
        email_field.send_keys(self.user_email)
        time.sleep(1)

        password_xpath = '//*[@id="pass"]'
        password_field = driver.find_element_by_xpath(password_xpath)
        password_field.send_keys(self.user_pass)
        time.sleep(1)

        login_button_xpath = '//*[@id="send2"]'
        login_button = driver.find_element_by_xpath(login_button_xpath)
        login_button.click()
        time.sleep(3)

        if driver.current_url == self.home_page:
            return True

        return False
    

    def get_and_write_unique_product_urls(self, all_product_urls, unique_product_urls_file):
        self.clear_text_file(unique_product_urls_file)
        unique_product_urls = set(all_product_urls)
        
        for product_urls in unique_product_urls:
            self.append_in_text_file(unique_product_urls_file, product_urls)
        
        return unique_product_urls
    

    def clean_text(self, input_str):
        output_str = str(input_str).strip()
        output_str = output_str.replace(u'\xa0', '')

        if output_str[0] == '=':
            output_str = output_str[1:]

        return output_str


    def get_text_after_string(self, delim, input_str):
        output_str = input_str.split(delim, 1)[1]
        return output_str
    

    def get_text_before_string(self, delim, input_str):
        output_str = input_str.split(delim, 1)[0]
        return output_str

    
    def get_product_title(self, soup):
        product_title = '-'

        try:
            product_title_div = soup.find('div', {'class': 'page-title-wrapper'})
            product_title = product_title_div.find('span', {'class': 'base'}).text
            product_title = self.clean_text(product_title)
        except:
            product_title = '-'
        
        return product_title
    

    def get_temp_product_descripton(self, soup):
        temp_product_descripton = ''

        try:
            product_desc_div = soup.find('div', {'class': 'product attribute overview'})

            for temp_p_div in product_desc_div.findAll('p'):
                temp_product_descripton = temp_product_descripton + '\n' + temp_p_div.text

            temp_product_descripton = self.clean_text(temp_product_descripton)
        except:
            temp_product_descripton = '-'
        
        return temp_product_descripton


    def get_product_desc_and_ean(self, temp_product_description):
        product_ean = '-'
        product_description = '-'

        try:
            if 'EAN' in temp_product_description:
                product_ean_str = self.get_text_after_string('EAN', temp_product_description)
                product_description = self.get_text_before_string('EAN', temp_product_description)
            elif 'ean' in temp_product_description:
                product_ean_str = self.get_text_after_string('ean', temp_product_description)
                product_description = self.get_text_before_string('ean', temp_product_description)
            elif 'EAN-code' in temp_product_description:
                product_ean_str = self.get_text_after_string('EAN-code', temp_product_description)
                product_description = self.get_text_before_string('EAN-code', temp_product_description)
            elif 'EAN-Code' in temp_product_description:
                product_ean_str = self.get_text_after_string('EAN-Code', temp_product_description)
                product_description = self.get_text_before_string('EAN-Code', temp_product_description)
            elif 'EAN-CODE' in temp_product_description:
                product_ean_str = self.get_text_after_string('EAN-CODE', temp_product_description)
                product_description = self.get_text_before_string('EAN-CODE', temp_product_description)
            elif 'ean-code' in temp_product_description:
                product_ean_str = self.get_text_after_string('ean-code', temp_product_description)
                product_description = self.get_text_before_string('ean-code', temp_product_description)
            else:
                product_ean_str = '-'
                product_description = temp_product_description

            product_ean_str = str(product_ean_str).replace(':', '').strip()
            product_ean = re.findall(r'\d+', product_ean_str)[0]
        except:
            product_ean = '-'
            product_description = temp_product_description
        
        return product_description, product_ean


    def get_product_sku(self, soup):
        product_sku = '-'

        try:
            product_sku_div = soup.find('div', {'class': 'product attribute sku'})

            product_sku = product_sku_div.find('div', {'class': 'value'}).text
            product_sku = self.clean_text(product_sku)
        except:
            product_sku = '-'
        
        return product_sku
    

    def get_product_price_1(self, soup):
        product_price_1 = '-'

        try:
            product_price_1_div = soup.find('span', {'class': 'price-container price-final_price tax weee'})
            product_price_1 = product_price_1_div.find('span', {'data-price-type':'finalPrice'})['data-price-amount']
        except:
            product_price_1 = '-'
        
        return product_price_1
    

    def get_product_price_2(self, soup):
        product_price_2 = '-'

        try:
            product_price_2_div = soup.find('div', {'class': 'product attibute weergave_prijs'})
            product_price_2_str = product_price_2_div.find('div', {'class': 'value'}).text
            product_price_2 = re.findall(r'\d+\.\d+', product_price_2_str)[0]

            if not product_price_2:
                product_price_2 = re.findall(r'\d+', product_price_2_str)[0]
        except:
            product_price_2 = '-'
        
        return product_price_2
    

    def get_image_urls(self, soup):
        image_urls_list = []
        image_urls_str = '-'

        try:
            image_urls_div = soup.find('div', {'class': 'fotorama__stage'})

            for image_div in image_urls_div.findAll('img'):
                image_url = image_div.get('src')
                if image_url not in image_urls_list:
                    image_urls_list.append(image_url)
                
            image_urls_str = ' , '.join(image_urls_list)
        except:
            image_urls_str = '-'

        return image_urls_str


    def fetch_and_process_product_details(self, soup, product_url):

        product_title = self.get_product_title(soup)
        temp_product_description = self.get_temp_product_descripton(soup)
        product_description, product_ean = self.get_product_desc_and_ean(temp_product_description)
        product_sku = self.get_product_sku(soup)
        price_1 = self.get_product_price_1(soup)
        price_2 = self.get_product_price_2(soup)
        image_urls = self.get_image_urls(soup)

        product_dict = {
            "Title": f"{product_title}",
            "EAN": f"{str(product_ean)}",
            "SKU": f"{str(product_sku)}",
            "price_1": f"{price_1}",
            "price_2": f"{price_2}",
            "URL": f"{product_url}",
            "Description": f"{product_description}",
            "image_urls": f"{image_urls}"
        }

        df = pd.DataFrame([product_dict])
        df.to_csv(self.output_csv_file, mode='a', header=self.is_new_file, index=False)
        self.is_new_file = False


    def fetch_all_product_details(self, driver, all_product_urls_file, unique_product_urls_file):
        issue_file = 'outputs/product_details_issue.txt'
        done_file = 'outputs/product_details_done.txt'
        self.clear_text_file(issue_file)
        self.clear_text_file(done_file)

        all_product_urls = self.read_from_text_file(all_product_urls_file)
        unique_product_urls = self.get_and_write_unique_product_urls(all_product_urls, unique_product_urls_file)
        
        print('\n\ntoatl unique products: ', len(unique_product_urls))

        _count = -1
        for product_url in unique_product_urls:
            _count = _count + 1
            print(f'\nGeting product details for url: {_count}')

            driver.get(product_url)
            time.sleep(4)
            
            page = driver.page_source
            soup = BeautifulSoup(page, features='html.parser')

            try:
                self.fetch_and_process_product_details(soup, product_url)
                self.append_in_text_file(done_file, product_url)
            except:
                self.append_in_text_file(issue_file, product_url)


    def start_process(self, chrome_driver_local_path, all_product_urls_file, unique_product_urls_file):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path=chrome_driver_local_path, chrome_options=chrome_options)
        driver.maximize_window()
        
        is_login_succssful = self.login(driver)

        if is_login_succssful:
            print('\n\nLogin successful !! Geting product details....\n')
            self.fetch_all_product_details(driver, all_product_urls_file, unique_product_urls_file)
        else:
            driver.close()
            raise Exception('\n\nError !! Login unsuccessful !! (url or username or password can be wrong)')

        driver.close()