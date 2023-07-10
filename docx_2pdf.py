import os

import docx2pdf

if not os.path.exists('pdfs'):
    os.mkdir('pdfs')


def docx_2pdf(docx_file: str, save_name):
    if save_name[-4:] == '.pdf':
        save_file = 'pdfs/' + save_name
    else:
        save_file = 'pdfs/' + save_name + ".pdf"

    file = open(save_file, "w")
    file.close()
    docx2pdf.convert(docx_file, save_file)


if __name__ == "__main__":
    for i in range(101, 102):
        inputFile = 'docxs/' + str(i) + '.docx'
        docx_2pdf(inputFile, str(i))
        print(i)
