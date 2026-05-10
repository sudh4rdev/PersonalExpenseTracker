import os
import csv
import flet as ft
from datetime import datetime

APP_CONFIG = {
'CSV_FILE_PATH' : 'expenses.csv',
'CURRENT_BALANCE' : 2500.00,
'CURRENT_EXPESESES' : 0.0
}

def initialise_csv_storage():
    '''
    Create the CSV file with the headers if the file doesn't exists
    '''
    if not os.path.exists(APP_CONFIG['CSV_FILE_PATH']):
        with open(APP_CONFIG['CSV_FILE_PATH'], mode='w',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Description','Amount', 'Payment Method'])

def calculate_current_balance() -> float:
    '''
    Calculate the current balance
    '''
    if not os.path.exists(APP_CONFIG['CSV_FILE_PATH']):
        return APP_CONFIG['CURRENT_BALANCE']
    
    total_expenses = 0.0
    with open(APP_CONFIG['CSV_FILE_PATH'], mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                total_expenses += float(row['Amount'])
            except (ValueError, TypeError):
                continue

    CURRENT_EXPESESES = total_expenses            
    return APP_CONFIG['CURRENT_BALANCE'] - total_expenses

def main(page : ft.Page):
    page.title = 'Personal Expense Tracker'
    page.window.width = 450
    page.window.height = 700
    # page.theme_mode = ft.ThemeMode.LIGHT
    page.window.resizable = False
    page.padding = 24

    initialise_csv_storage()

    desc_input = ft.TextField(
        label = 'Expense Description',
        hint_text = 'e.g., Tesco Shopping GWR',
        icon = ft.Icons.SHOPPING_BAG,
        label_style=ft.TextStyle(color = ft.Colors.GREEN_ACCENT_700),
        hint_style=ft.TextStyle(color= ft.Colors.GREEN_ACCENT_700),
        border_color=ft.Colors.GREEN_ACCENT_700,
        focused_border_color=ft.Colors.GREEN_ACCENT_700,
        width = 300
    )
    # HOME SCREEN - START

    amount_input = ft.TextField(
        label = 'Amount Spent',
        hint_text = '£ 0.00',
        icon = ft.Icons.ATTACH_MONEY,
        keyboard_type= ft.KeyboardType.NUMBER,
        label_style=ft.TextStyle(color = ft.Colors.GREEN_ACCENT_700),
        hint_style=ft.TextStyle(color= ft.Colors.GREEN_ACCENT_700),
        border_color=ft.Colors.GREEN_ACCENT_700,
        focused_border_color=ft.Colors.GREEN_ACCENT_700,
        width = 300
    )

    payment_input = ft.TextField(
        label= 'Payment Method',
        hint_text= 'e.g., Apple Pay',
        icon = ft.Icons.CREDIT_CARD,
        label_style=ft.TextStyle(color = ft.Colors.GREEN_ACCENT_700),
        hint_style=ft.TextStyle(color= ft.Colors.GREEN_ACCENT_700),
        border_color=ft.Colors.GREEN_ACCENT_700,
        focused_border_color=ft.Colors.GREEN_ACCENT_700,
        width = 300
    )

    date_picker = ft.DatePicker(
        first_date=datetime(2025, 1, 1),
        last_date=datetime(2030, 12, 31)
    )

    page.overlay.append(date_picker)

    date_input = ft.TextField(
        label='Expense Date',
        value=datetime.now().strftime('%d-%m-%Y'),
        width=300,
        icon=ft.Icons.CALENDAR_TODAY,
        color=ft.Colors.GREEN_ACCENT_700,
        label_style=ft.TextStyle(color = ft.Colors.GREEN_ACCENT_700),
        hint_style=ft.TextStyle(color= ft.Colors.GREEN_ACCENT_700),
        border_color=ft.Colors.GREEN_ACCENT_700,
        focused_border_color=ft.Colors.GREEN_ACCENT_700,
        suffix=ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_DOWN,
            icon_color=ft.Colors.GREEN_ACCENT_700,
            on_click=lambda e: page.show_dialog(date_picker)  # Opens the picker above
        )
    )

    def handle_date_picker_change(e):
        if date_picker.value:
            raw_date = date_picker.value
            
            if raw_date.tzinfo is not None:
                local_date = raw_date.astimezone().date()
            else:
                local_date = raw_date.date()
                
            date_input.value = local_date.strftime('%d-%m-%Y')
            page.update()
    
    date_picker.on_change = handle_date_picker_change

    balance_value = calculate_current_balance()
    balance_label = ft.Text(
        value=f'Current Balance: £{balance_value:,.2f}',
        size=20,
        weight=ft.FontWeight.NORMAL,
        color=ft.Colors.GREEN_ACCENT_700 if balance_value >= 0 else ft.Colors.RED_700
    )
    
    status_msg = ft.Text(value='', size=12, italic=True)

    def handle_banner_close(e: ft.Event[ft.TextButton]):
        page.pop_dialog()

    action_button_style = ft.ButtonStyle(color=ft.Colors.GREEN_ACCENT_700)
    banner = ft.Banner(
    leading=ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.GREEN_ACCENT_700),
    content=status_msg,
    actions=[ft.TextButton("Dismiss",on_click=handle_banner_close, style=action_button_style)],
    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
    open= False
    )

    def commit_expense_record(e):
        date_text = date_input.value.strip()
        desc_text = desc_input.value.strip()
        amount_text = amount_input.value.strip()
        payment_text = payment_input.value.strip()
        
        
        if not date_text or not desc_text or not amount_text or not payment_text:
            status_msg.value = 'Error: All text fields must be populated.'
            status_msg.color = ft.Colors.RED_600
            page.update()
            page.show_dialog(banner)
            return
            
        
        try:
            parsed_amount = float(amount_text)
            if parsed_amount <= 0:
                raise ValueError()
        except ValueError:
            status_msg.value = 'Validation Fail: Amount must be a positive number.'
            status_msg.color = ft.Colors.RED_600
            page.update()
            return

        
        with open(APP_CONFIG['CSV_FILE_PATH'], mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([date_text, desc_text, f'{parsed_amount:.2f}', payment_text])
            
        
        new_balance = calculate_current_balance()
        balance_label.value = f'Current Balance: £{new_balance:,.2f}'
        balance_label.color = ft.Colors.GREEN_700 if new_balance >= 0 else ft.Colors.RED_700
        
       
        desc_input.value = ''
        amount_input.value = ''
        payment_input.value = ''
        date_input.value = datetime.now().strftime('%d-%m-%Y')
        
        status_msg.value = 'Success: Transaction record safely written to CSV!'
        status_msg.color = ft.Colors.GREEN_600
        page.show_dialog(banner)
        page.update()

    
    submit_button = ft.Button(
        content='Save Expense',
        icon=ft.Icons.SAVE,
        on_click=commit_expense_record,
        width=300,
        height=45,
        color = ft.Colors.GREEN_ACCENT_700
    )

    # HOME SCREEN - END 

    # SETTINGS SCREEN - START
    path_label = ft.Text(
        value = os.path.abspath(APP_CONFIG['CSV_FILE_PATH']),
        size = 11,
        color=ft.Colors.GREEN_ACCENT_400,
        text_align=ft.TextAlign.CENTER,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS
    )

    async def handle_get_directory_path(e:ft.Event[ft.Button]):
        try:
            files = await ft.FilePicker().pick_files(allow_multiple=False, allowed_extensions=['csv'])
            path_label.value = files[0].path
        except:
            pass

    file_picker_button = ft.Button(
        content='Choose File',
        icon = ft.Icons.FOLDER_OPEN,
        on_click= handle_get_directory_path
    )

    def handle_theme_switch_change(e: ft.Event[ft.Switch]):
        page.theme_mode = ft.ThemeMode.LIGHT if e.control.value else ft.ThemeMode.DARK

    theme_switch = ft.Switch(
        on_change= handle_theme_switch_change

    )   

    # SETTINGS SCREEN - END

    # MENU LAYOUT - START

    home_layout = ft.Column(
                controls=[
                    ft.Text('Expense Tracker', size=28, weight=ft.FontWeight.W_800, color=ft.Colors.GREEN_ACCENT_700),
                    ft.Divider(height=20, thickness=1, color=ft.Colors.GREEN_ACCENT_700),
                    ft.Container(height=15),
                    date_input,
                    desc_input,
                    amount_input,
                    payment_input,
                    balance_label,
                    ft.Container(height=10),
                    submit_button,
                    ft.Container(height=5),
                    banner
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
    
    insight_layout = ft.Column(
        controls=[
            ft.Text('Insights Screen', size=28, weight=ft.FontWeight.W_800, color=ft.Colors.GREEN_ACCENT_700),
            ft.Divider(height=20, thickness=1, color=ft.Colors.GREEN_ACCENT_700),
            ft.Text('Placeholder for historical analytics charts & distributions.')
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    settings_layout = ft.Column(
        controls=[
            ft.Text('Settings Screen', size=28, weight=ft.FontWeight.W_800, color=ft.Colors.GREEN_ACCENT_700),
            ft.Divider(height=20, thickness=1, color=ft.Colors.GREEN_ACCENT_700),
            ft.Row(controls = [file_picker_button , path_label], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand= True),
            ft.Row(controls = [ft.Text('Enable Light Mode', color=ft.Colors.GREEN_ACCENT_700), theme_switch], 
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand= True)
        ]
    )
    
    def change_active_tab(e):
        if e.control.selected_index == 0:
            active_view_wrapper.content = home_layout
        elif e.control.selected_index == 1:
            active_view_wrapper.content = insight_layout
        elif e.control.selected_index == 2:
            active_view_wrapper.content = settings_layout
        page.update()

        
    page.navigation_bar = ft.NavigationBar(
        selected_index= 0,
        on_change= change_active_tab,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label='Home'),
            ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS, label='Insight'),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS,label='Settings')
        ]
    )

    # MENU LAYOUT - END

    active_view_wrapper = ft.Container(
            content=home_layout,
            alignment=ft.alignment.Alignment.TOP_CENTER,
            padding=10
    )

    page.add(active_view_wrapper)
    
if __name__ == '__main__':
    ft.run(main = main)