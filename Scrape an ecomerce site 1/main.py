from get_product_urls import Get_Product_urls
from get_product_details import Get_Product_details


if __name__ == '__main__':

    login_page = '<page_url>'
    home_page = '<home_page>'
    user_email = ''    
    user_pass = ''

    chrome_driver_local_path = 'C:\chromedriver.exe'
    output_folder_path = 'outputs/'
    all_product_urls_file = 'outputs/product_urls.txt'
    unique_product_urls_file = 'outputs/unique_product_urls.txt'
    output_csv_file = 'outputs/products_1.csv'

    is_get_product_urls_needed = 1
    is_product_details_needed = 1

    if is_get_product_urls_needed:
        Get_Product_urls(login_page, home_page, user_email, user_pass).start_process(chrome_driver_local_path, all_product_urls_file)
    
    if is_product_details_needed:
        Get_Product_details(login_page, home_page, user_email, user_pass, output_csv_file).start_process(chrome_driver_local_path, all_product_urls_file, unique_product_urls_file)
