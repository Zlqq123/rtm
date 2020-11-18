Option Explicit

Sub select_MEB()



Dim SH1 As Worksheet
Dim SH2 As Worksheet
Set SH1 = Sheets("Detail")

Sheets.Add After:=ActiveSheet
Set SH2 = ActiveSheet
SH2.Name = "Select"


Dim Nr_col1 As Integer
Dim source_col1 As Integer
Dim rate_col1 As Integer
Dim content_col1 As Integer
Dim analyse_col1 As Integer
Dim responsible_col1 As Integer
Dim kpm_col1 As Integer
Dim duratin_col1 As Integer

Dim project_col1 As Integer
Dim group_col1 As Integer
Dim status_col1 As Integer
Dim dateENI_col As Integer
Dim dateENX_col As Integer



Application.ScreenUpdating = False  '关闭屏幕更新

Nr_col1 = 1
source_col1 = 11
rate_col1 = 7
content_col1 = 14
analyse_col1 = 19
responsible_col1 = 22
kpm_col1 = 27

project_col1 = 4
group_col1 = 12
status_col1 = 33


dateENI_col = 2
dateENX_col = 3


Dim i As Integer
Dim r As Integer
Dim m As Integer
Dim c As Integer



c = 1
SH2.Cells(1, c).Value = "Nr."
c = c + 1
SH2.Cells(1, c).Value = "Project"
c = c + 1
SH2.Cells(1, c).Value = "Fehlei Sys."
c = c + 1
SH2.Cells(1, c).Value = "Status"

c = c + 1
SH2.Cells(1, c).Value = "Source"
c = c + 1
SH2.Cells(1, c).Value = "Rating"
c = c + 1
SH2.Cells(1, c).Value = "Problem Describe"
Columns(c).ColumnWidth = 35
c = c + 1
SH2.Cells(1, c).Value = "Analysis"
Columns(c).ColumnWidth = 55
c = c + 1
SH2.Cells(1, c).Value = "Resp."
c = c + 1
SH2.Cells(1, c).Value = "KPM Nr."
c = c + 1
SH2.Cells(1, c).Value = "Suspended"
c = c + 1

Dim status As String
Dim CurrentDate
CurrentDate = Date

i = 7
'detail sheet rownumber

r = 1
'select sheet rownumber

Do While SH1.Cells(i, 1).Value <> ""
    status = SH1.Cells(i, status_col1).Value
    If status = "Analyzing" Then
        r = r + 1
        c = 1
        SH2.Cells(r, c).Value = SH1.Cells(i, 1).Value
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, project_col1).Value
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, group_col1).Value
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, status_col1).Value
        
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, source_col1).Value
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, rate_col1).Value
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, content_col1).Value
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, analyse_col1).Value
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, responsible_col1).Value
        c = c + 1
        SH2.Cells(r, c).Value = SH1.Cells(i, kpm_col1).Value
        c = c + 1
        If SH1.Cells(i, dateENX_col).Value <> "" Then
            SH2.Cells(r, c).Value = CurrentDate - SH1.Cells(i, dateENX_col).Value
        Else
            SH2.Cells(r, c).Value = CurrentDate - SH1.Cells(i, dateENI_col).Value
        End If
        SH2.Cells(r, c).Value = Int(SH2.Cells(r, c).Value / 7)
        SH2.Cells(r, c).Value = SH2.Cells(r, c).Value & " weeks"
    End If
    i = i + 1
Loop


Dim x
x = Range("A65536").End(xlUp).Row
Rows("2:" & x).Select
ActiveWindow.SmallScroll Down:=0
Rows("2:" & x).EntireRow.AutoFit

Range("A1:M" & x).Select
 With Selection
    .VerticalAlignment = xlCenter
    .HorizontalAlignment = xlCenter
    .Borders(xlEdgeLeft).LineStyle = xlContinuous
    .Borders(xlEdgeTop).LineStyle = xlContinuous
    .Borders(xlEdgeBottom).LineStyle = xlContinuous
    .Borders(xlEdgeRight).LineStyle = xlContinuous
    .Borders(xlInsideHorizontal).LineStyle = xlContinuous
    .Borders(xlInsideVertical).LineStyle = xlContinuous
    .Font.Name = "微软雅黑"
    .Font.Size = 8
End With

Columns("G:H").Select
With Selection
    .HorizontalAlignment = xlLeft
End With


Rows("1:1").Select
With Selection
    .HorizontalAlignment = xlCenter
    .Font.Bold = True
End With


Application.ScreenUpdating = True

End Sub



