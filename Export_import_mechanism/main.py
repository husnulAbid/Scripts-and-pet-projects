from pytz import timezone
import datetime
from Layout import *
from Import import *
from Save import *

window_width = 800
window_height = 500
button_width = 8
button_height = 1

event_log_items = ['application', 'security', 'error', 'input/output']
file_types_items = ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xslx', '.rtf', '.pdf', '.txt', '.jpg', '.png', '.gif', '.xml', '.html', '.zip', '.mp4', '.mov']
debug_mode_items = ['on']
all_layout = ['menu_layout', 'import_layout', 'save_layout']

max_thread_invalid_msg = 'Max Threads must be either 1, 2 or 4'
server_port_not_integer_msg = 'Server Port must be Integer'
server_port_invalid_range_msg = 'Server Port must be in range from 50,000 to 50,500'
debug_mode_invalid_msg = 'Debug Mode must be boolean'
excluded_msg = 'Imported Successfully by Excluding these fields'
file_not_json_msg = 'Selected file is not a Json file'
json_file_invalid_msg = 'Selected  Json file is invalid'


def write_json_file(save_dict):
    # output json file name will be recent time when creating
    output_file_name = str(datetime.datetime.now(timezone('US/Eastern')).strftime("%Y_%m_%d_%H-%M-%S"))
    with open('ConfigureFiles\\' + output_file_name + '.json', 'w') as outfile:
        json.dump(save_dict, outfile)


def clear_all_save_values(window):                                     # Clearing all the values
    window['maxThreads'].update('')
    window['eventLogFileLocation'].update('')
    window['serverPort'].update('')

    window['debugMode'].update(False)

    for item in event_log_items:
        window[f'eventTypes{item}'].update(False)

    for item in file_types_items:
        window[f'fileTypes{item}'].update(False)


def clear_all_import_values(window):                                    # Clearing all the values
    window['importedFile'].update('')


def hide_other_layouts(window, current_layout):                         # Hiding other layouts
    for temp_layout in all_layout:
        if not temp_layout == current_layout:
            window[temp_layout].update(visible=False)


def menu():
    layout_1 = Layout()
    menu_layout = layout_1.menu_layout_func()
    import_layout = layout_1.import_layout_func()
    save_layout = layout_1.save_layout_func()

    # Initializing layout
    layout = [[Sg.Column(menu_layout, key=all_layout[0]), Sg.Column(import_layout, visible=False,  key=all_layout[1]), Sg.Column(save_layout, visible=False, key=all_layout[2])]]
    window = Sg.Window('Configure File App', layout, size=(window_width, window_height))

    while True:
        event, values = window.read()
        if event == 'Save Configure':
            hide_other_layouts(window, 'save_layout')
            window['save_layout'].update(visible=True)

        if event == 'Import Configure':
            hide_other_layouts(window, 'import_layout')
            window['import_layout'].update(visible=True)

        if event == 'Back' or event == 'Back ':
            clear_all_save_values(window)
            clear_all_import_values(window)

            hide_other_layouts(window, 'menu_layout')
            window['menu_layout'].update(visible=True)

        if event == 'Save':
            save_1 = Save()
            save_dict, message = save_1.save_task(values)

            if message == 'no error':
                write_json_file(save_dict)
                Sg.PopupOK('Saved Successfully', title='')

                hide_other_layouts(window, 'menu_layout')
                window['menu_layout'].update(visible=True)
                clear_all_save_values(window)
            else:
                Sg.PopupOK(message + '\n', title='')

        if event == 'Import':
            hide_other_layouts(window, 'save_layout')
            window['save_layout'].update(visible=True)

            import_1 = Import()
            message = import_1.import_task(window, values['importedFile'])
            clear_all_import_values(window)

            if message == '':
                Sg.PopupOK('Imported Successfully', title='')
            elif message == file_not_json_msg:
                Sg.PopupOK(file_not_json_msg, title='')
            elif message == json_file_invalid_msg:
                Sg.PopupOK(json_file_invalid_msg, title='')
            else:
                Sg.PopupOK(message + '\n\n' + excluded_msg + '\n', title='')

        if event == Sg.WIN_CLOSED:
            break

    window.close()


if __name__ == "__main__":
    menu()
