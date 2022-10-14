
from os import listdir
from os.path import isdir, join

LARA = './SVN/trunk/'
mypath = LARA + 'Content'
compiled_path = LARA + 'Content'
onlydir = [f for f in listdir(mypath) if isdir(join(mypath, f))]
#global language

html_path = './SVN/trunk/compiled/'
content_loc = './SVN/trunk/Content/'
corpus_suffix = '/corpus/local_config.json'
lara_builder = LARA + 'Code/Python/lara_run.py '
lara_builder_creator = 'word_pages '
compiled_loc = LARA + 'compiled/'
folder_sufix = 'vocabpages'
index_folder_sufix = 'vocabpages'
multimedia_folder = "/multimedia/"
py_ver = 'python '
py_ver_w = 'python'
main_page_hyper = '_from_abstract_htmlvocabpages/_hyperlinked_text_.html'
hyper_page_html = '_hyperlinked_text_.html'
pic_loc = html_path + 'pic'
slash = '/'
slash_clean = '/'
language=[]


"""TODO extarct from meta data JASON the right language"""
alphaBet = "'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','r','s','t','u','v','x','w','z','a','á','b','d','ð','e','é','f','g','h','i','í','j','k','l','m','n','o','ó','p','r','s','t','u','ú','v','x','y','ý','þ','æ','ö','ð'"
