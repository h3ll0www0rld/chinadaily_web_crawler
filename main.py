import requests
import re
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import time


# 获取网页内容
def get_page_content(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    pattern = re.compile(r'<[^>]+>', re.S)
    content_with_tag = str(soup.find(id='Content'))
    content = pattern.sub(' ', content_with_tag)
    return content

# 获取文章中的单词
def get_word(content):
    word_list = content.split()
    return word_list


# 获取文章中的句子
def get_sentence(content):
    sentence_list = content.split('.')
    return sentence_list


# 通过高考词库和地名词库筛选单词
def get_filtered_word(word_list):
    unknown_word_list = []
    with open('dict.txt', 'r') as f:
        dict = f.read()
        for word in word_list:
            word.lower()
            word = word.replace(".", '')
            word = word.replace("'s", '')
            word = word.replace('"', '')
            word = word.replace(',', '')
            if word in dict or 'the' in word or 'on' in word or '—' in word or '[' in word or ']' in word or '1' in word or '2' in word or '3' in word or '4' in word or '5' in word or '6' in word or '7' in word or '8' in word or '9' in word or '0' in word:
                pass
            else:
                unknown_word_list.append(word.lower())
    return unknown_word_list


# 通过句子长短筛选句子
def get_good_sentence(sentence_list):
    good_sentence_list = []
    for sentence in sentence_list:
        if len(sentence) > 10:
            good_sentence_list.append(sentence.replace('\n',''))
    return good_sentence_list


# 通过api请求进行翻译
# 目前仅提供对google translate api的支持，需要魔法，其它api请自己参考官方文档进行配置


def get_translation(list_to_translate):
    result = {}
    with Progress() as progress:
        task = progress.add_task('翻译中......', total=len(list_to_translate))
        for element in list_to_translate:
            try:
                param = f'client=at&sl=en&tl=zh-CN&dt=t&q={element}'
                try:
                    r = requests.get(api + param, timeout=5)
                except requests.exceptions.RequestException:
                    answer = ['', '获取失败']
                answer = r.text.split('"')
                result[element] = answer[1]
                time.sleep(0.1)
                progress.update(task, advance=1)
            except IndexError:
                pass
                progress.update(task, advance=1)
    return result


def study(url, console):
    # 初始化
    page_content = get_page_content(url)
    word_list = get_word(page_content)
    sentence_list = get_sentence(page_content)
    table = Table()
    table.add_column('标题')
    table.add_column(response['content'][i]['title'])

    #获取列表
    unknown_word_list = get_filtered_word(word_list)
    print('获取单词成功!')
    good_sentence_list = get_good_sentence(sentence_list)
    print('获取句子成功!')
    result_word = get_translation(unknown_word_list)
    result_sentence = get_translation(good_sentence_list)
    
    if len(unknown_word_list) == 0:
        print('无生词!')
    else:
        for word in unknown_word_list:
            try:
                table.add_row(word, result_word[word])
            except KeyError:
                table.add_row(word, '获取失败')
    if len(good_sentence_list) == 0:
        print('无好句!')
    else:
        for sentence in good_sentence_list:
            try:
                table.add_row(sentence, result_sentence[sentence])
            except KeyError:
                table.add_row(sentence, '获取失败')
    console.print(table)
    


if __name__ == '__main__':
    console = Console(color_system='256', style=None)
    api = 'http://translate.google.com/translate_a/single?'  # 翻译api
    article_number = int(input('请输入要获取的文章数目 => '))  # 获取china daily文章地址
    response = requests.get(
        'https://newssearch.chinadaily.com.cn/rest/en/search?keywords=&sort=dp&page=0&curType=story&type=&channel=&source=').json()
    # 根据文章地址进行学习
    for i in range(article_number):
        study(response['content'][i]['url'], console)
