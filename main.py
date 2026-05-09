import os
import csv
import flet as ft
from datetime import datetime

CSV_FILE_PATH = 'expenses.csv'
CURRENT_BALANCE = 2500.00
CURRENT_EXPESESES = 0.0

def initialise_csv_storage():
    '''
    Create the CSV file with the headers if the file doesn't exists
    '''
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode='w',newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Description","Amount", "Payment Method"])

def calculate_current_balance() -> float:
    '''
    Calculate the current balance
    '''
    if not os.path.exists(CSV_FILE_PATH):
        return CURRENT_BALANCE
    
    total_expenses = 0.0
    with open(CSV_FILE_PATH, mode='r', newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                total_expenses += float(row['Amount'])
            except (ValueError, TypeError):
                continue

    CURRENT_EXPESESES = total_expenses            
    return CURRENT_BALANCE - total_expenses

def main(page : ft.Page):
    page.title = 'Personal Expense Tracker'
    page.window.width = 450
    page.window.height = 650
    # page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 24

    initialise_csv_storage()

    desc_input = ft.TextField(
        label = 'Expense Description',
        hint_text = 'e.g., Tesco Shopping GWR',
        icon = ft.Icons.SHOPPING_BAG,
        width = 300
    )

    amount_input = ft.TextField(
        label = 'Amount Spent',
        hint_text = '£ 0.00',
        icon = ft.Icons.ATTACH_MONEY,
        keyboard_type= ft.KeyboardType.NUMBER,
        width = 300
    )

    payment_input = ft.TextField(
        label= 'Payment Method',
        hint_text= 'e.g., Apple Pay',
        icon = ft.Icons.CREDIT_CARD,
        width = 300
    )

    date_picker = ft.DatePicker(
        first_date=datetime(2025, 1, 1),
        last_date=datetime(2030, 12, 31)
    )

    page.overlay.append(date_picker)

    date_input = ft.TextField(
        label="Expense Date",
        value=datetime.now().strftime("%d-%m-%Y"),
        width=300,
        icon=ft.Icons.CALENDAR_TODAY,
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
                
            date_input.value = local_date.strftime("%d-%m-%Y")
            page.update()
    
    date_picker.on_change = handle_date_picker_change

    balance_value = calculate_current_balance()
    balance_label = ft.Text(
        value=f"Current Balance: £{balance_value:,.2f}",
        size=22,
        weight=ft.FontWeight.NORMAL,
        color=ft.Colors.GREEN_ACCENT_700 if balance_value >= 0 else ft.Colors.RED_700
    )
    
    status_msg = ft.Text(value="", size=12, italic=True)

    def commit_expense_record(e):
        # Extract raw strings from inputs
        date_text = date_input.value.strip()
        desc_text = desc_input.value.strip()
        amount_text = amount_input.value.strip()
        payment_text = payment_input.value.strip()
        
        
        if not date_text or not desc_text or not amount_text or not payment_text:
            status_msg.value = "Error: All text fields must be populated."
            status_msg.color = ft.Colors.RED_600
            page.update()
            return
            
        
        try:
            parsed_amount = float(amount_text)
            if parsed_amount <= 0:
                raise ValueError()
        except ValueError:
            status_msg.value = "Validation Fail: Amount must be a positive number."
            status_msg.color = ft.Colors.RED_600
            page.update()
            return

        
        with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([date_text, desc_text, f"{parsed_amount:.2f}", payment_text])
            
        
        new_balance = calculate_current_balance()
        balance_label.value = f"Current Balance: £{new_balance:,.2f}"
        balance_label.color = ft.Colors.GREEN_700 if new_balance >= 0 else ft.Colors.RED_700
        
       
        desc_input.value = ""
        amount_input.value = ""
        payment_input.value = ""
        date_input.value = datetime.now().strftime("%d-%m-%Y")
        
        status_msg.value = "Success: Transaction record safely written to CSV!"
        status_msg.color = ft.Colors.GREEN_600
        page.update()

    
    submit_button = ft.ElevatedButton(
        content="Save Expense",
        icon=ft.Icons.SAVE,
        on_click=commit_expense_record,
        width=300,
        height=45
    )


   
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Expense Tracker", size=28, weight=ft.FontWeight.W_800),
                    ft.Divider(height=20, thickness=1),
                    balance_label,
                    ft.Container(height=15),
                    date_input,
                    desc_input,
                    amount_input,
                    payment_input,
                    ft.Container(height=10),
                    submit_button,
                    ft.Container(height=5),
                    status_msg
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.alignment.Alignment.TOP_CENTER,
            padding=10
        )
    )

# App target execution setup
if __name__ == "__main__":
    ft.app(target=main)