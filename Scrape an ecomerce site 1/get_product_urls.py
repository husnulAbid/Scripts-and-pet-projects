import time
from bs4 import BeautifulSoup
from selenium import webdriver


class Get_Product_urls:

    def __init__(self, login_page, home_page, user_email, user_pass):
        self.login_page = login_page
        self.home_page = home_page
        self.user_email = user_email
        self.user_pass = user_pass


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
    
    
    def get_navbar_urls(self, driver):
        urls = []

        page = driver.page_source
        soup = BeautifulSoup(page, features='html.parser')
        
        for item in soup.findAll('ul', {'class': 'nav-desktop sticker'}):
            for link in item.findAll('a'):
                urls.append(link.get('href'))

        for item in soup.findAll('ul', {'class': 'nav-desktop vmagicmenu-narrow clearfix'}):
            for link in item.findAll('a'):
                urls.append(link.get('href'))
        
        return urls
    

    def get_product_urls_from_each_nav(self, driver, nav_url):
        urls_from_each_nav = []

        driver.get(nav_url)

        while True:
            time.sleep(2)

            page = driver.page_source
            soup = BeautifulSoup(page, features='html.parser')

            # fetching urls 
            item_grid = soup.find('div', {'class': 'category-products clearfix products wrapper grid products-grid'})

            if item_grid:
                for product_item in item_grid.findAll('li', {'class': 'item product product-item'}):
                    link = product_item.find('a', {'class': 'product-item-link'})
                    urls_from_each_nav.append(link.get('href'))
            else:
                break


            # going to next pages if exist
            toolbar_item = soup.find('div', {'class': 'toolbar-bottom'})
            if toolbar_item:
                page_item = toolbar_item.find('ul', {'class': 'items pages-items'})
                if page_item:
                    next_button = page_item.find('li', {'class': 'item pages-item-next'})
                    
                    if next_button:
                        next_page_link = next_button.find('a')
                        driver.get(next_page_link.get('href'))
                    else:
                        break
                else:
                    break
            else:
                break
        
        return urls_from_each_nav


    def get_all_product_urls(self, driver, nav_urls):
        temp_product_file = 'outputs/product_urls_temp.txt'
        self.clear_text_file(temp_product_file)
        
        all_product_urls = []
        time.sleep(3)

        _count = -1
        for nav_url in nav_urls:
            _count = _count + 1
            print(f'\nGeting all product urls for nav url {_count}')
            
            urls_from_each_nav = self.get_product_urls_from_each_nav(driver, nav_url)
            all_product_urls.extend(urls_from_each_nav)

            # write to text file
            for temp_product_urls in urls_from_each_nav:
                self.append_in_text_file(temp_product_file, temp_product_urls)

        return all_product_urls


    def start_process(self, chrome_driver_local_path, all_product_urls_file):
        self.clear_text_file(all_product_urls_file)
        all_product_urls = []

        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path=chrome_driver_local_path, chrome_options=chrome_options)
        driver.maximize_window()
        
        is_login_succssful = self.login(driver)

        if is_login_succssful:
            print('\n\nLogin successful !! Geting navbar urls....\n')
            nav_urls = self.get_navbar_urls(driver)

            if nav_urls:
                print('\n\nGeting all product urls....\n')
                all_product_urls = self.get_all_product_urls(driver, nav_urls)
            else:
                driver.close()
                raise Exception('\n\nError !! No Nav Urls')
        else:
            driver.close()
            raise Exception('\n\nError !! Login unsuccessful !! (url or username or password can be wrong)')

        # write to text file
        for product_urls in all_product_urls:
            self.append_in_text_file(all_product_urls_file, product_urls)

        driver.close()