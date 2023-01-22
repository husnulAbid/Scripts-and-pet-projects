import PySimpleGUI as Sg


window_width = 800
window_height = 500
button_width = 8
button_height = 1

event_log_items = ['application', 'security', 'error', 'input/output']
file_types_items = ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xslx', '.rtf', '.pdf', '.txt', '.jpg', '.png', '.gif', '.xml', '.html', '.zip', '.mp4', '.mov']


class Layout:
    @staticmethod
    def save_layout_func():  # Creating layout for save page
        first_half_file_types_items = file_types_items[:12]  # dividing to make checkboxes in two line
        second_half_file_types_items = file_types_items[12:]

        layout = [[Sg.Text('Here to Save', pad=((5, 0), (5, 5)))],
                  [Sg.Text('Max Threads: ', pad=((5, 65), (5, 5))),
                   Sg.Combo([1, 2, 4], readonly=True, size=(15, 5), key='maxThreads', enable_events=True)],
                  [Sg.Text('Event Log File Location: ', pad=((5, 5), (5, 5))),
                   Sg.Input(key='eventLogFileLocation', disabled=True, size=(70, 1)),
                   Sg.FileBrowse(key='eventLogFileBrowse', size=(button_width, button_height))],

                  [Sg.Text('\nTypes of Event Log: ')],
                  [Sg.Checkbox(item, key=f'eventTypes{item}') for item in event_log_items[:10]],

                  [Sg.Text('\nSupported File Types: ')],
                  [Sg.Checkbox(item, key=f'fileTypes{item}') for item in first_half_file_types_items],
                  [Sg.Checkbox(item, key=f'fileTypes{item}') for item in second_half_file_types_items],

                  [Sg.Text('Debug Mode: ', pad=((5, 5), (15, 5))),
                   Sg.Checkbox('on', key='debugMode', pad=((5, 5), (15, 5)))],

                  [Sg.Text('Server Port: ', pad=((5, 5), (15, 5))),
                   Sg.Input(key='serverPort', size=(15, 5), pad=((15, 5), (15, 5)))],

                  [Sg.Button('Save', size=(button_width, button_height), pad=((5, 0), (15, 5)))],
                  [Sg.Button('Back ', size=(button_width, button_height), pad=((5, 0), (25, 5)))]]

        return layout

    @staticmethod
    def import_layout_func():  # Creating layout for import page
        layout = [[Sg.Text('Choose a File: ', pad=((5, 0), (50, 5)))],
                  [Sg.Input(disabled=True, size=(80, 1), key='importedFile'),
                   Sg.FileBrowse(key='importedFilePath', size=(button_width, button_height)),
                   Sg.Button('Import', size=(button_width, button_height))],
                  [Sg.Button('Back', size=(button_width, button_height), pad=((5, 0), (340, 5)))]]

        return layout

    @staticmethod
    def menu_layout_func():  # Creating layout for menu page
        layout = [[Sg.Text('', pad=((300, 0), (100, 20)))],
                  [Sg.Button('Import Configure', size=(13, 2), pad=((300, 0), (0, 0))),
                   Sg.Button('Save Configure', size=(13, 2))]]
        # [Sg.Text('Hello, Please select what you want: ', pad=((300, 0), (100, 20)))],

        return layout
