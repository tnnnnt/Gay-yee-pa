"""
爬取指定标签的e站本子的增量式爬虫
"""
import json
import os
import re
import socket
from tqdm import tqdm
import Reptile.reptile_function as rf


def ids_download(ides):
    for ID in ides:
        if ID in ex_id_flag or ID in ex_dislike_flag:
            continue
        id_url = "https://exhentai.org/g/" + ID + "/"
        id_html = rf.get_html(id_url, headers)
        while id_html[:4] == "Your":
            id_html = rf.get_html(id_url, headers)
        this_tags = re.findall('href="https://exhentai.org/tag/(.*?)"', id_html)
        is_white = False  # 判断是否为非常喜欢的标签
        for super_like_tag in super_like_tags:
            if super_like_tag in this_tags:
                is_white = True
                break
        is_hate = False  # 判断是否属于讨厌的标签
        if not is_white:
            for hate_tag in hate_tags:
                if hate_tag in this_tags:
                    is_hate = True
                    break
        if is_hate:
            ex_dislike_flag.append(ID)
            with open('ex_dislike_flag.json', 'w') as f:
                json.dump(ex_dislike_flag, f)
            continue
        if ID not in ex_pic_flag:
            ex_pic_flag[ID] = 0
            with open('ex_pic_flag.json', 'w') as f:
                json.dump(ex_pic_flag, f)
        title = re.compile(r'[/:*?"<>|\\\t]').sub('_', re.findall('<title>(.*?) - ExHentai.org</title>', id_html)[0])  # 标题
        path = rootpath + title
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            directory, filename = os.path.split(path)
            if filename not in os.listdir(directory):
                os.mkdir(path + '_')
        id_pages = int(re.findall('onclick="return false">(.*?)</a>', id_html)[-2])  # 总页数
        num_of_pages = len(re.findall(get_pics_and_rank_t, id_html))  # 每页的图数
        all_rank = (id_pages - 1) * num_of_pages + len(re.findall(get_pics_and_rank_t, rf.get_html(id_url + "?p=" + str(id_pages - 1), headers)))  # 该作品总图数
        pics_and_rank = [[]] * id_pages
        for id_page in range(id_pages):
            pics_and_rank[id_page] = re.findall(get_pics_and_rank_t,
                                                rf.get_html(id_url + "?p=" + str(id_page), headers))
        for real_rank in tqdm(range(all_rank), desc=title):
            pr = pics_and_rank[real_rank // num_of_pages][real_rank % num_of_pages]
            rank = str(pr[1])
            if int(rank) <= ex_pic_flag[ID]:
                continue
            pic_url = "https://exhentai.org/s/" + str(pr[0])
            while True:
                while True:
                    pic_html = rf.get_html(pic_url, headers)
                    while pic_html[:4] == "Your":
                        pic_html = rf.get_html(pic_url, headers)
                    down_url = re.findall('<img id="img" src="(.*?)"', pic_html)[0]
                    if down_url != "https://exhentai.org/img/509.gif":  # 509配额不足
                        break
                pic_type = "." + down_url.split(".")[-1]  # .jpg or .png
                pic_path = path + '/' + rank + pic_type  # 本地图片
                response = rf.get_response(down_url, headers)
                with open(pic_path, 'wb+') as f:
                    f.write(response.content)
                if rf.is_valid(pic_path):  # 下载成功
                    ex_pic_flag[ID] += 1
                    with open('ex_pic_flag.json', 'w') as f:
                        json.dump(ex_pic_flag, f)
                    break
        ex_id_flag.append(ID)
        with open('ex_id_flag.json', 'w') as f:
            json.dump(ex_id_flag, f)
        ex_pic_flag.pop(ID)
        with open('ex_pic_flag.json', 'w') as f:
            json.dump(ex_pic_flag, f)
        with open(path + '/' + 'fin.txt', 'w') as f:
            f.write('url: ' + id_url + '\ntags: [')
            for i in range(len(this_tags)):
                f.write(this_tags[i] + ', ')
            f.write(']\n')


def exd():
    socket.setdefaulttimeout(20)  # 参考了blog——六脉神贱
    print("优先下载之前未完成的作品...")
    ids_download(ex_pic_flag.copy().keys())
    for like_tag in like_tags:
        tag_url = "https://exhentai.org/tag/" + like_tag + "?prev=1"
        page = 0
        while tag_url != "":
            page += 1
            print('标签: ', like_tag, ', 第 ', page, ' 页')
            tag_html = rf.get_html(tag_url, headers)
            while tag_html[:4] == "Your":
                tag_html = rf.get_html(tag_url, headers)
            ids_download(re.findall('<a href="https://exhentai.org/g/(.*?)/">', tag_html)[0::2])
            tag_url = re.findall('var prevurl="(.*?)";', tag_html)[0]  # 获取上一页url
    print('我滴任务完成啦啊哈哈哈哈哈！')
    rf.over_tip()
    exit()


# 以下需要自行设置
headers = {
    # 用开发者工具找自己的headers
           }
like_tags = []  # 填入喜欢的标签
hate_tags = []  # 填入讨厌的标签
super_like_tags = []  # 填入非常喜欢的标签，不受讨厌的标签的限制
rootpath = "E://ex/"  # 路径自己改
# 以上需要自行设置

get_pics_and_rank_t = '<a href="https://exhentai.org/s/(.*?)"><img alt="(.*?)"'

with open('ex_id_flag.json') as f_obj:  # 加载已下载作品列表
    ex_id_flag = json.load(f_obj)
with open('ex_pic_flag.json') as f_obj:  # 加载已下载单图列表
    ex_pic_flag = json.load(f_obj)
with open('ex_dislike_flag.json') as f_obj:  # 加载不喜欢作品列表
    ex_dislike_flag = json.load(f_obj)
exd()
