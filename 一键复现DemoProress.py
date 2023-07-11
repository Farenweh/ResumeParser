# 假定输入的是docx或doc，这将测试（演示）所有module和流程
# ！！！请先将LLaMA放入LLaMAModel，否则LLaMA相关功能将会被禁用！！！
import OCRkit
import docx_2pdf
import extracting
import matching
import pdf_2jpg
import profiling

# txt或IO输入直接放入jpg_txt文件夹

# docx/doc转pdf功能，用以支持docx/doc输入
docx_2pdf.docx_2pdf('docxs/101.docx')

# pdf转jpg功能，用以支持jpg输入
pdf_2jpg.pdf_2jpg('pdfs/101.pdf')

# jpg转txt的ocr功能，通过移动云OCR API实现，同时整合了置信度筛查和Layout Analyze流程，从而通过版面分析来重排OCR结果，为NLP提供清洁数据
OCR_Analyzed_result = OCRkit.pics_ocr('jpgs/101')
print('------------------OCR_Analyzed_result------------------')
print(OCR_Analyzed_result)

# 从txt提取简历信息，使用LLaMA-AIpaca13B配合GPT API实现，整合了本地数据脱敏和反译，避免数据泄露
# 当LLaMA和GPT均在线时，由LLaMA进行数据脱敏，LLaMA和GPT共同进行信息抽取，LLaMA进行解密；
# 当LLaMA不在线时，在本地使用正则表达式对邮箱和电话进行数据脱敏，由GPT执行抽取，然后本地执行反译；
# 当GPT不在线时，使用LLaMA也可单独进行抽取，但极度占用本地资源，需要40G显存或64G内存，且效率非常低，当配置不满足需求时将触发报错。
print('-------运行中，请等待，耗时约60秒，但这取决于您的平台配置--------')
report = extracting.extracting(OCR_Analyzed_result)
print('------------------Analyze report------------------------')
print(report)

# 用户画像功能，可以根据教育背景和工作经验推理行业、方向、领域TAG，并提供信息摘要
profile = profiling.profiling(report)
print('------------------Profile-------------------------------')
print(profile)

# 岗位匹配功能，根据求职者信息，遍历所有岗位要求，返回其同所有岗位的匹配情况
match = matching.matching(profile)
print('------------------Match result--------------------------')
print(match)
