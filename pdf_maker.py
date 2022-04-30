import PySimpleGUI as sg
import re
import glob
import os
from PIL import Image
import img2pdf
import PyPDF2
import shutil

def layout_master(page, data):

    # レイアウトとかあれこれ

    # 初期画面
    if page == "first":
        layout = [
            [sg.Text('PDFにつけたい名前を入力してください。拡張子は不要です。')],
            [sg.Text('名前', size=(15, 1)), sg.InputText('私はこんなpdfが作りたい！')],
            [sg.Button('pdfを作成する', key='input_name'),sg.Button('終了する', key='yes_exit')]
        ]

    # 初期画面(戻って来た時)
    if page == "re_first":
        layout = [
            [sg.Text('PDFにつけたい名前を入力してください。拡張子は不要です。')],
            [sg.Text('名前', size=(15, 1)), sg.InputText(data["name"])],
            [sg.Button('pdfを作成する', key='input_name'),sg.Button('終了する', key='yes_exit')]
        ]
    
    # アプリケーションを終了するときの奴
    elif page == "exit":
        layout = [
            [sg.Text("アプリケーションが終了しますがよろしいですか？")],
            [sg.Button('終了する', key="yes_exit"), sg.Button('終了しない', key="no_exit")],
        ]

    # 確認画面
    elif page == "check_page":
        show_message = str(data["files"]) + "個のファイルが読み込まれました。\nPDF：" + data["name"] + '.pdf　を製作します。よろしいですか？\n作業終了には時間がかかる場合があります。\nポップアップが出たら終了です。\n'
        layout = [
            [sg.Text(show_message)],
            [sg.Button('つくる！(時間がかかる場合があります)', key='make_pdf'), sg.Button('再度入力しなおす', key='back_check_page')]
        ]

    return layout


# 取り合えず全部読み込もうぜ！

def catch_files():
    files = glob.glob("*")
    files = [s for s in files if re.match('(?!pdf_maker)', str(s))]
    return files

# 作業ファイルの中身を読みだす奴

def catch_jpgs():
    files = glob.glob("trash/*.jpg")
    files = [s for s in files if re.match('(?!pdf_maker)', str(s))]
    return files

# 90％ここが本体ネ(pdf作成部分)

def pdf_builder(data):

    title = data["name"]

    files = catch_files()

    # 作業ファイルを作成する
    os.mkdir('trash')

    # 同階層のファイルを読みだしてpdfに変換可能か調べる奴

    for file in files:
        fileType = re.findall("^(.*?).([pngifjepgwb]+)$", str(file))

        # まぁ、エラーを回避するやつですよ。
        if not fileType:
            continue

        if fileType[0][0]:
            name = fileType[0][0]
        else:
            continue

        if fileType[0][1]:
            fileType = fileType[0][1]
        else:
            continue

        # pngとwebpは一回jpgに変換しましょうね～
        # jpg=ｻﾝはそのまま作業ファイルへ
        if fileType == "png":
            image = Image.open(file).convert("RGB")
            name = "trash/" + str(name) + ".jpg"
            image.save(name)
        elif fileType == "webp":
            image = Image.open(file).convert("RGB")
            name = "trash/" + str(name) + ".jpg"
            image.save(name)
        elif fileType == "jpg":
            shutil.copy(file, 'trash')


    files = sorted(catch_jpgs())
    imageCount = len(files)
    count = 1

    # 取り合えずpdfに変換じゃい！
    for name in files:
        pdf_name = "trash/" + str(count) + ".pdf"
        imageName = name
        img = Image.open(imageName)
        cov_pdf = img2pdf.convert(imageName)
        file = open(pdf_name, "wb")
        file.write(cov_pdf)
        file.close()
        img.close()
        count += 1

    # バラバラのpdfを一つにまとめましょうね～
    merge = PyPDF2.PdfFileMerger()
    for pdf in range(1, int(imageCount + 1)):
        fragment = "trash/" + str(pdf) + ".pdf"
        merge.append(fragment)
    merge.write(str(title) + ".pdf")
    merge.close
    merge.close()
    shutil.rmtree("./trash")

def main():

    # 各種設定の初期化
    sg.theme('DarkTeal7')
    page_name = "first"
    data = {
        "name": "",
        "files": 0
    }

    # レイアウトの設定を呼び出す
    layout = layout_master(page_name, data)

    # 初期ウィンドの生成
    window = sg.Window('pdf メーカー', layout)

    # イベントを拾う奴
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            page_name = "exit"
            data = {
                "name": "",
                "files": 0
            }
            layout = layout_master(page_name, data)
            window.close()
            window = sg.Window('確認画面', layout)

        elif event == "yes_exit":
            sg.popup("アプリケーションを終了します")
            break

        elif event == "no_exit":
            page_name = "first"
            layout = layout_master(page_name, data)
            window.close()
            window = sg.Window('pdf メーカー', layout)

        elif event == "back_first_page":
            page_name = "first"
            layout = layout_master(page_name, data)
            window.close()
            window = sg.Window('pdf メーカー', layout)

        elif event == "input_name":
            files = catch_files()
            data = {
                "name": values[0],
                "files": len(files)
            }
        
            if data == "":
                sg.popup("空白はダメなんだぞ！")
                page_name = "first"
            else:
                page_name = "check_page"
            layout = layout_master(page_name, data)
            window.close()
            window = sg.Window('pdf メーカー', layout)

        elif event == "back_check_page":
            page_name = "re_first"
            layout = layout_master(page_name, data)
            window.close()
            window = sg.Window('pdf メーカー', layout)
        
        elif event == "make_pdf":
            pdf_builder(data)
            sg.popup("pdfの作成が終了しました。")
            break

# お作法？
if __name__ == '__main__':
    main()

# ファイルを分割なんてしないんだからネ///