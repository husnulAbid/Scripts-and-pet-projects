event_log_items = ['application', 'security', 'error', 'input/output']
file_types_items = ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xslx', '.rtf', '.pdf', '.txt', '.jpg', '.png', '.gif', '.xml', '.html', '.zip', '.mp4', '.mov']

max_thread_invalid_msg = 'Max Threads must be either 1, 2 or 4'
server_port_not_integer_msg = 'Server Port must be Integer'
server_port_invalid_range_msg = 'Server Port must be in range from 50,000 to 50,500'
debug_mode_invalid_msg = 'Debug Mode must be boolean'
excluded_msg = 'Imported Successfully by Excluding these fields'


class Save:
    def save_task(self, values):
        save_dict = {}
        message = 'no error'  # Initializing message, if no error found then return this

        if values['maxThreads']:
            if values['maxThreads'] not in [1, 2, 4]:  # Checking if value is 1 or 2 or 4
                message = max_thread_invalid_msg
                return save_dict, message  # If invalid max thread returning with message.
            else:
                save_dict['maxThreads'] = values['maxThreads']  # If valid then saving it to dictionary

        if values['eventLogFileLocation']:
            save_dict['eventLogFileLocation'] = values['eventLogFileLocation']

        if values['debugMode']:
            save_dict['debugMode'] = values['debugMode']

        if values['serverPort']:
            try:
                server_port_val = int(values['serverPort'])  # Trying to get integer value
            except:
                message = server_port_not_integer_msg  # If value is not integer returning with message
                return save_dict, message

            if (server_port_val > 50000 - 1) and (server_port_val <= 50500):  # Checking if server port in range
                save_dict['serverPort'] = values['serverPort']
            else:
                message = server_port_invalid_range_msg
                return save_dict, message

        count = 0
        for item in event_log_items:
            if values[f'eventTypes{item}']:
                count = count + 1
                if count == 1:  # First time creating dictionary key
                    save_dict['eventTypes'] = [item]
                else:
                    save_dict['eventTypes'].append(item)  # From next, only appending in dictionary

        count = 0
        for item in file_types_items:
            if values[f'fileTypes{item}']:
                count = count + 1
                if count == 1:
                    save_dict['fileTypes'] = [item]  # First time creating dictionary key
                else:
                    save_dict['fileTypes'].append(item)

        return save_dict, message