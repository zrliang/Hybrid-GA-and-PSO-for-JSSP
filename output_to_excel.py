# 首先需要import openpyxl這個套件
import openpyxl
from openpyxl import Workbook

# 用python建立一個Excel空白活頁簿
excel_file = Workbook()

# 建立一個工作表
sheet = excel_file.active

# 先填入第一列的欄位名稱
sheet['A1'] = 'columnA'
sheet['B1'] = 'columnB'
sheet['C1'] = 'columnC'
sheet['D1'] = 'columnD'

# 使用迴圈逐列增加，這邊為了讓大家看清楚才用2開始跑，我們實際上是用append的方式往下新增資料，所以從0開始讀取資料即可
i = 2
while i < 10:

    columnA = 'A'+str(i)
    columnB = 'B'+str(i)
    columnC = 'C'+str(i)
    columnD = 'D'+str(i)

#     實際將資料寫入每一列
    sheet.append([columnA, columnB, columnC, columnD])
    i = i + 1

# 儲存成XLSX檔

excel_file.save('sample.xlsx')