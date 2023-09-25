from tempfile import NamedTemporaryFile
import tempfile
from openpyxl import Workbook
from openpyxl.styles import PatternFill,Font, Alignment, Border, Side
from sqlalchemy import create_engine, text


def create_csv():
    engine = create_engine("sqlite:///C:\\Users\\HPpc\\PycharmProjects\\ShopProject\\app.db")

    deliveries_query="SELECT * FROM Deliveries " #запросы к каждой из таблиц
    expenses_query = "SELECT * FROM Expenses"
    product_query = "SELECT * FROM Product"
    receipt_query = "SELECT * FROM Receipt"


    with engine.connect() as connection:
        deliv_result = connection.execute(text(deliveries_query))
        exp_result = connection.execute(text(expenses_query))
        prod_result = connection.execute(text(product_query))
        receipt_result = connection.execute(text(receipt_query))


    wb = Workbook()

    ws1=wb.active # work with default worksheet
    ws1.title = "Deliveries"
    l1=[r for r in deliv_result.keys()] # List of column headers
    ws1.append(l1) # adding column headers at first row

    ws2 = wb.create_sheet("Expenses")
    l2 = [r for r in exp_result.keys()] # List of column headers
    ws2.append(l2) # adding column headers at first row

    ws3 = wb.create_sheet("Product")
    l3 = [r for r in prod_result.keys()] # List of column headers
    ws3.append(l3) # adding column headers at first row

    ws4 = wb.create_sheet("Receipt")
    l4 = [r for r in receipt_result.keys()]  # List of column headers
    ws4.append(l4)  # adding column headers at first row

    ws_list = [ws1,ws2,ws3,ws4]
    my_font=Font(size=12,bold=True) # font styles
    # my_fill=PatternFill(fill_type='solid',start_color='FFFF00') #Background color
    my_border = Border(left=Side(border_style='dotted',color='000000'),
                       right=Side(border_style='dotted',color='000000'),
                       top=Side(border_style='dotted', color='000000'),
                       bottom=Side(border_style='dotted', color='000000'))



    for i in ws_list:
        for column in i.columns:
            max_length = 0
            column_letter = column[0].column_letter
            i.border = my_border
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            i.column_dimensions[column_letter].width = adjusted_width


    for cell in ws_list:
        for i in cell["1:1"]:
            i.font = my_font
            i.alignment = Alignment(horizontal="center")
            i.border = my_border

    r, c = 2, 0  # row=2 and column=0

##############################################################
    for row_data in deliv_result: # Поставки

        d = [r for r in row_data]
        ws1.append(d)

    for row_data in exp_result: # Траты

        d = [r for r in row_data]
        ws2.append(d)


    for row_data in prod_result: #Product

        d = [r for r in row_data]
        ws3.append(d)

    for row_data in receipt_result:  # Receipt

        d = [r for r in row_data]
        ws4.append(d)
###########################################################





    # print('Я работаю')

    # wb.save("C:\\Users\\HPpc\\PycharmProjects\\ShopProject\\app\\test-table3.xlsx") #сохранить файл локально

####################Save file as Stream ####################################
    with NamedTemporaryFile(delete=False) as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        create_csv.stream = tmp.read()
        # print(tmp.name)
        create_csv.csv_path = tmp.name


create_csv()

