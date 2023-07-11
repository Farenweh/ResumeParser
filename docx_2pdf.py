import os

import doc2docx
import doc2pdf
import docx2pdf

if not os.path.exists('pdfs'):
    os.mkdir('pdfs')


def docx_2pdf(docx_file: str, save_name=''):  # doc/docx都支持，在win下面必须有ms office，在linux下面必须有libre office
    if save_name == '':
        save_name = docx_file.split('/')[-1].split('.')[0]

    if save_name[-4:] == '.pdf':
        save_file = 'pdfs/' + save_name
    else:
        save_file = 'pdfs/' + save_name + ".pdf"

    with open(save_file, "w"):
        pass

    if docx_file[-4:] == 'docx':
        docx2pdf.convert(docx_file, save_file)
        return

    if docx_file[-3:] == 'doc':
        if doc2pdf.is_windows():
            doc2docx.convert(docx_file)
            docx_file += 'x'
            docx2pdf.convert(docx_file, save_file)
            os.remove(docx_file)
            return
        else:
            doc2pdf.convert(docx_file, save_file)
            return
    else:
        raise ValueError


if __name__ == "__main__":
    print(os.listdir('docxs'))

    # for doc in os.listdir('docxs'):
    #     inputFile = 'docxs/' + doc
    #     docx_2pdf(inputFile, doc.split('.')[0])
    #     print(doc)
