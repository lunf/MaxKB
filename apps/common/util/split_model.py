# coding=utf-8
"""
    @project: qabot
    @Author:The Tiger
    @file: split_model.py
    @date:2023/9/1 15:12
    @desc:
"""
import re
from functools import reduce
from typing import List, Dict

import jieba


def get_level_block(text, level_content_list, level_content_index, cursor):
    """
    Obtain blocks of data from the text.
    :param text: The text
    :param level_content_list: SeparatedtitleNumber of groups
    :param level_content_index: The indicated subset.
    :return: Text Data After Division
    """
    start_content: str = level_content_list[level_content_index].get('content')
    next_content = level_content_list[level_content_index + 1].get("content") if level_content_index + 1 < len(
        level_content_list) else None
    start_index = text.index(start_content, cursor)
    end_index = text.index(next_content, start_index + 1) if next_content is not None else len(text)
    return text[start_index:end_index].lstrip(level_content_list[level_content_index]['content']), end_index


def to_tree_obj(content, state='title'):
    """
    Transformed into a tree-shaped object
    :param content: Text data
    :param state:   state of: title block
    :return: Data after conversion
    """
    return {'content': content, 'state': state}


def remove_special_symbol(str_source: str):
    """
    Remove special characters.
    :param str_source: Text data needed to be deleted.
    :return: Data after deletion
    """
    return str_source


def filter_special_symbol(content: dict):
    """
    Special characters in the filtered text.
    :param content: Objects needed to filter.
    :return: Return after filtering.
    """
    content['content'] = remove_special_symbol(content['content'])
    return content


def flat(tree_data_list: List[dict], parent_chain: List[dict], result: List[dict]):
    """
    Structural structural data
    :param tree_data_list: The tree interface data
    :param parent_chain:   The Father's Data Translated[] Used for storage data.
    :param result:         Reacting data Translated[] Used for storage data.
    :return: result Data after climbing.
    """
    if parent_chain is None:
        parent_chain = []
    if result is None:
        result = []
    for tree_data in tree_data_list:
        p = parent_chain.copy()
        p.append(tree_data)
        result.append(to_flat_obj(parent_chain, content=tree_data["content"], state=tree_data["state"]))
        children = tree_data.get('children')
        if children is not None and len(children) > 0:
            flat(children, p, result)
    return result


def to_paragraph(obj: dict):
    """
    Convert to paragraphs.
    :param obj: Objects needed to be converted.
    :return: Subjects of paragraph
    """
    content = obj['content']
    return {"keywords": get_keyword(content),
            'parent_chain': list(map(lambda p: p['content'], obj['parent_chain'])),
            'content': ",".join(list(map(lambda p: p['content'], obj['parent_chain']))) + content}


def get_keyword(content: str):
    """
    obtainedcontentKeywords in
    :param content: The text
    :return: Number of keywords
    """
    stopwords = [':', '“', '！', '”', '\n', '\\s']
    cutworms = jieba.lcut(content)
    return list(set(list(filter(lambda k: (k not in stopwords) | len(k) > 1, cutworms))))


def titles_to_paragraph(list_title: List[dict]):
    """
    The same class of fathers.titleConvert to a block.
    :param list_title: with Father class.title
    :return: block of paragraphs.
    """
    if len(list_title) > 0:
        content = "\n,".join(
            list(map(lambda d: d['content'].strip("\r\n").strip("\n").strip("\\s"), list_title)))

        return {'keywords': '',
                'parent_chain': list(
                    map(lambda p: p['content'].strip("\r\n").strip("\n").strip("\\s"), list_title[0]['parent_chain'])),
                'content': ",".join(list(
                    map(lambda p: p['content'].strip("\r\n").strip("\n").strip("\\s"),
                        list_title[0]['parent_chain']))) + content}
    return None


def parse_group_key(level_list: List[dict]):
    """
    The same level with the father.titleCreate paragraphs.,In addition to paragraph data itself, new data is formed.
    :param level_list: title n level data
    :return: based ontitleThe data generated + Paragraph data
    """
    result = []
    group_data = group_by(list(filter(lambda f: f['state'] == 'title' and len(f['parent_chain']) > 0, level_list)),
                          key=lambda d: ",".join(list(map(lambda p: p['content'], d['parent_chain']))))
    result += list(map(lambda group_data_key: titles_to_paragraph(group_data[group_data_key]), group_data))
    result += list(map(to_paragraph, list(filter(lambda f: f['state'] == 'block', level_list))))
    return result


def to_block_paragraph(tree_data_list: List[dict]):
    """
    Convert to a block item.
    :param tree_data_list: The Tree Data
    :return: block of paragraphs.
    """
    flat_list = flat(tree_data_list, [], [])
    level_group_dict: dict = group_by(flat_list, key=lambda f: f['level'])
    return list(map(lambda level: parse_group_key(level_group_dict[level]), level_group_dict))


def parse_title_level(text, content_level_pattern: List, index):
    if len(content_level_pattern) == index:
        return []
    result = parse_level(text, content_level_pattern[index])
    if len(result) == 0 and len(content_level_pattern) > index + 1:
        return parse_title_level(text, content_level_pattern, index + 1)
    return result


def parse_level(text, pattern: str):
    """
    Get the text that match the rule.
    :param text: Required corresponding text.
    :param pattern:  The rule
    :return: Text in accordance with the rules.
    """
    level_content_list = list(map(to_tree_obj, re_findall(pattern, text)))
    return list(map(filter_special_symbol, level_content_list))


def re_findall(pattern, text):
    result = re.findall(pattern, text, flags=0)
    return list(filter(lambda r: r is not None and len(r) > 0, reduce(lambda x, y: [*x, *y], list(
        map(lambda row: [*(row if isinstance(row, tuple) else [row])], result)),
                                                                      [])))


def to_flat_obj(parent_chain: List[dict], content: str, state: str):
    """
    Convert the tree-shaped properties into flat objects
    :param parent_chain:
    :param content:
    :param state:
    :return:
    """
    return {'parent_chain': parent_chain, 'level': len(parent_chain), "content": content, 'state': state}


def flat_map(array: List[List]):
    """
    Convert a two-bit group into one-dimensional group
    :param array: Two-dimensional group
    :return: One-dimensional group
    """
    result = []
    for e in array:
        result += e
    return result


def group_by(list_source: List, key):
    """
    Divide the numbers.
    :param list_source: Number of groups needed.
    :param key: Division functions
    :return: key->[]
    """
    result = {}
    for e in list_source:
        k = key(e)
        array = result.get(k) if k in result else []
        array.append(e)
        result[k] = array
    return result


def result_tree_to_paragraph(result_tree: List[dict], result, parent_chain):
    """
    Convert to Division Objects
    :param result_tree: Analysis of text trees
    :param result:      Translated[]  Used for delivery.
    :param parent_chain: Translated[] User sends data to storage.
    :return: List[{'problem':'xx','content':'xx'}]
    """
    for item in result_tree:
        if item.get('state') == 'block':
            result.append({'title': " ".join(parent_chain), 'content': item.get("content")})
        children = item.get("children")
        if children is not None and len(children) > 0:
            result_tree_to_paragraph(children, result, [*parent_chain, item.get('content')])
    return result


def post_handler_paragraph(content: str, limit: int, with_filter: bool):
    """
       The maximum part of the text.
       :param with_filter: Filtering special characters.
       :param content: Required text fields.
       :param limit:   The maximum part of the character.
       :return: Data after section.
       """
    split_list = content.split('\n')
    result = []
    temp_char = ''
    for split in split_list:
        if len(temp_char + split) > limit:
            result.append(temp_char)
            temp_char = ''
        temp_char = temp_char + split + '\n'
    if len(temp_char) > 0:
        result.append(temp_char)
    pattern = "[\\S\\s]{1," + str(limit) + '}'
    # If\n Exceeding the limit.,Continue to split.
    s = list(map(lambda row: filter_special_char(row) if with_filter else row, list(
        reduce(lambda x, y: [*x, *y], list(map(lambda row: list(re.findall(pattern, row)), result)), []))))
    return s


replace_map = {
    re.compile('\n+'): '\n',
    re.compile('\\s+'): ' ',
    re.compile('#+'): "",
    re.compile("\t+"): ''
}


def filter_special_char(content: str):
    """
    Filtering special fields.
    :param content: The text
    :return: After filtering fields.
    """
    items = replace_map.items()
    for key, value in items:
        content = re.sub(key, value, content)
    return content


class SplitModel:

    def __init__(self, content_level_pattern, with_filter=True, limit=4096):
        self.content_level_pattern = content_level_pattern
        self.with_filter = with_filter
        if limit is None or limit > 4096:
            limit = 4096
        if limit < 50:
            limit = 50
        self.limit = limit

    def parse_to_tree(self, text: str, index=0):
        """
         Analysis of text
        :param text: Text needed to be analyzed.
        :param index: Starting with that rule.
        :return: Analysis of Tree Form Results
        """
        if len(self.content_level_pattern) == index:
            return
        level_content_list = parse_title_level(text, self.content_level_pattern, 0)
        cursor = 0
        for i in range(len(level_content_list)):
            block, cursor = get_level_block(text, level_content_list, i, cursor)
            children = self.parse_to_tree(text=block,
                                          index=index + 1)
            if children is not None and len(children) > 0:
                level_content_list[i]['children'] = children
            else:
                if len(block) > 0:
                    level_content_list[i]['children'] = list(
                        map(lambda row: to_tree_obj(row, 'block'),
                            post_handler_paragraph(block, with_filter=self.with_filter, limit=self.limit)))
        if len(level_content_list) > 0:
            end_index = text.index(level_content_list[0].get('content'))
            if end_index == 0:
                return level_content_list
            other_content = text[0:end_index]
            children = self.parse_to_tree(text=other_content,
                                          index=index)
            if len(children) > 0:
                level_content_list = [*level_content_list, *children]
            else:
                if len(other_content.strip()) > 0:
                    level_content_list = [*level_content_list, *list(
                        map(lambda row: to_tree_obj(row, 'block'),
                            post_handler_paragraph(other_content, with_filter=self.with_filter, limit=self.limit)))]
        else:
            if len(text.strip()) > 0:
                level_content_list = [*level_content_list, *list(
                    map(lambda row: to_tree_obj(row, 'block'),
                        post_handler_paragraph(text, with_filter=self.with_filter, limit=self.limit)))]
        return level_content_list

    def parse(self, text: str):
        """
        Analysis of text
        :param text: Text data
        :return: Data after analysis. {content:Paragraph data,keywords:['Paragraph Keywords'],parent_chain:['Paragraph of Father's Link']}
        """
        text = text.replace('\r', '\n')
        text = text.replace("\0", '')
        result_tree = self.parse_to_tree(text, 0)
        result = result_tree_to_paragraph(result_tree, [], [])
        return [item for item in [self.post_reset_paragraph(row) for row in result] if
                'content' in item and len(item.get('content').strip()) > 0]

    def post_reset_paragraph(self, paragraph: Dict):
        result = self.filter_title_special_characters(paragraph)
        result = self.sub_title(result)
        result = self.content_is_null(result)
        return result

    @staticmethod
    def sub_title(paragraph: Dict):
        if 'title' in paragraph:
            title = paragraph.get('title')
            if len(title) > 255:
                return {**paragraph, 'title': title[0:255], 'content': title[255:len(title)] + paragraph.get('content')}
        return paragraph

    @staticmethod
    def content_is_null(paragraph: Dict):
        if 'title' in paragraph:
            title = paragraph.get('title')
            content = paragraph.get('content')
            if (content is None or len(content.strip()) == 0) and (title is not None and len(title) > 0):
                return {'title': '', 'content': title}
        return paragraph

    @staticmethod
    def filter_title_special_characters(paragraph: Dict):
        title = paragraph.get('title') if 'title' in paragraph else ''
        for title_special_characters in title_special_characters_list:
            title = title.replace(title_special_characters, '')
        return {**paragraph,
                'title': title}


title_special_characters_list = ['#', '\n', '\r', '\\s']

default_split_pattern = {
    'md': [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
           re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
           re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
           re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
           re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
           re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*")],
    'default': [re.compile("(?<!\n)\n\n+")]
}


def get_split_model(filename: str, with_filter: bool = False, limit: int = 4096):
    """
    Obtaining a section model according to the file name
    :param limit:        Each size.
    :param with_filter: Filtering special characters.
    :param filename: Name of document
    :return: Part Model
    """
    if filename.endswith(".md"):
        pattern_list = default_split_pattern.get('md')
        return SplitModel(pattern_list, with_filter=with_filter, limit=limit)

    pattern_list = default_split_pattern.get('md')
    return SplitModel(pattern_list, with_filter=with_filter, limit=limit)


def to_title_tree_string(result_tree: List):
    f = flat(result_tree, [], [])
    return "\n│".join(list(map(lambda r: title_tostring(r), list(filter(lambda row: row.get('state') == 'title', f)))))


def title_tostring(title_obj):
    f = "│ ".join(list(map(lambda index: " ", range(0, len(title_obj.get("parent_chain"))))))
    return f + "├───" + title_obj.get('content')
