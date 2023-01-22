import json

max_thread_invalid_msg = 'Max Threads must be either 1, 2 or 4'
server_port_not_integer_msg = 'Server Port must be Integer'
server_port_invalid_range_msg = 'Server Port must be in range from 50,000 to 50,500'
debug_mode_invalid_msg = 'Debug Mode must be boolean'
excluded_msg = 'Imported Successfully by Excluding these fields'
file_not_json_msg = 'Selected file is not a Json file'
json_file_invalid_msg = 'Selected  Json file is invalid'

event_log_items = ['application', 'security', 'error', 'input/output']
file_types_items = ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xslx', '.rtf', '.pdf', '.txt', '.jpg', '.png', '.gif', '.xml', '.html', '.zip', '.mp4', '.mov']


class Import:
    def dict_to_form(self, window, imported_dict):
        message = ''

        if 'maxThreads' in imported_dict:
            max_thread_value = imported_dict['maxThreads']  # Taking value from dictionary
            if max_thread_value in [1, 2, 4]:  # Checking if value is 1 or 2 or 4
                window['maxThreads'].update(max_thread_value)
            else:
                message = message + max_thread_invalid_msg + '\n'

        if 'eventLogFileLocation' in imported_dict:
            window['eventLogFileLocation'].update(imported_dict['eventLogFileLocation'])

        if 'serverPort' in imported_dict:
            try:
                server_port_value = int(imported_dict['serverPort'])  # Trying to get integer value

                if (server_port_value > 50000 - 1) and (server_port_value <= 50500):  # Checking range
                    window['serverPort'].update(server_port_value)
                else:
                    message = message + server_port_invalid_range_msg + '\n'
            except:  # If not integer value, sending a message
                message = message + server_port_not_integer_msg + '\n'

        if 'debugMode' in imported_dict:
            if type(imported_dict['debugMode']) == bool:  # Checking whether it's boolean value
                if imported_dict['debugMode']:
                    window['debugMode'].update(True)
            else:
                message = message + debug_mode_invalid_msg + '\n'  # If not boolean sending a message

        if 'eventTypes' in imported_dict:
            imported_event_types = imported_dict['eventTypes']

            for item in imported_event_types:  # Iterate through imported_event_types
                if item in event_log_items:  # If matched with event_log_items, only updating then
                    window[f'eventTypes{item}'].update(True)

        if 'fileTypes' in imported_dict:
            file_types = imported_dict['fileTypes']

            for item in file_types:  # Iterate through file_types
                if item in file_types_items:  # If matched with file_types_items, only updating then
                    window[f'fileTypes{item}'].update(True)

        return message

    def import_task(self, window, file_path):
        input_json = ''

        file_extension = str(file_path).split('.')[-1]  # Fetching file_extension by taking last substring after '.'

        if file_extension != 'json':
            message = file_not_json_msg
            return message

        with open(file_path, 'r') as input_file:
            input_json = input_file.read()

        try:
            imported_dict = json.loads(input_json)
        except:
            message = json_file_invalid_msg
            return message

        message = self.dict_to_form(window, imported_dict)

        return message
