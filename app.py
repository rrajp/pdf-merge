from PyPDF2 import PdfFileWriter, PdfFileReader
from flask import Flask, render_template, request, current_app, send_from_directory
import os
import logging

app = Flask(__name__)
app.static_folder = 'static'
i = 0


@app.route('/', methods = ['GET', 'POST'])
def front():
    global i
    i += 1
    if request.method == "POST":
        try:
            get_dict = dict()
            flag = True
            for k, v in request.files.items():
                number = k.split("_")[1]
                pages_range = k.split("_")[2]
                priority = k.split("_")[3]
                file = v
                if priority == "":
                    flag = False

            for k, v in request.files.items():
                if flag:
                    priority = k.split("_")[3]
                else:
                    priority = k.split("_")[1]
                get_dict[int(priority)] = dict()
                get_dict[int(priority)]['file'] = v
                pages = k.split("_")[2].split(",")
                if len(pages) == 1 and pages[0] == '':
                    get_dict[int(priority)]['pages'] = ['all']
                else:
                    get_dict[int(priority)]['pages'] = []
                    for page in pages:
                        if '-' in page:
                            start = int(page.split("-")[0])
                            end = int(page.split("-")[1])
                            get_dict[int(priority)]['pages'] += list(range(start, end + 1))
                        else:
                            get_dict[int(priority)]['pages'].append(int(page))

            pd_w = PdfFileWriter()
            for key in sorted(list(get_dict.keys())):
                read = PdfFileReader(get_dict[key]['file'])
                for pg in get_dict[key]['pages']:
                    if pg == 'all':
                        for allpage in range(read.getNumPages()):
                            pd_w.addPage(read.getPage(allpage))
                    else:
                        pd_w.addPage(read.getPage(pg - 1))
            with open(os.path.join(current_app.root_path, f'static/download/result_{i}.pdf'), 'wb') as out:
                pd_w.write(out)
            app.logger.info(f"Saved 'result_{i}.pdf'")
            return f'result_{i}.pdf'
        except Exception as e:
            return "Invalid Input"
    return render_template("pdf.html")


@app.route('/download/<path:filename>', methods = ['GET', 'POST'])
def merge(filename):
    folder = os.path.join(current_app.root_path, 'static/download/')
    return send_from_directory(directory = folder, filename = filename)
    # return send_file(os.path.join(folder, 'result_0.pdf'), as_attachment = True)


@app.route('/list/', methods = ['GET'])
def list():
    folder = os.path.join(current_app.root_path, 'static/download/')
    return str(os.listdir(folder))


@app.route('/del/<path:filename>', methods = ['GET'])
def delete(filename):
    folder = os.path.join(current_app.root_path, 'static/download/')
    os.remove(os.path.join(folder, filename))
    return f'deleted {filename}'



if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run()
