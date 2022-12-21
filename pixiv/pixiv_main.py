"""
pixiv爬虫
模式0：指定标签
模式1：指定画师
模式2: 指定作品
"""
import imghdr
import json
import os
import random
import socket
import time
import zipfile
import imageio.v2 as imageio
from tqdm import tqdm
import Reptile.reptile_function as rf


# 下载gif
def downloadGIF(pid, path):
    gif_info = json.loads(rf.get_html("https://www.pixiv.net/ajax/illust/" + pid + "/ugoira_meta", headers))
    delay = [item["delay"] for item in gif_info["body"]["frames"]]
    delay = sum(delay) / len(delay)
    zip_url = gif_info["body"]["originalSrc"]
    # 下载压缩包
    gif_data = rf.get_response(zip_url, headers).content
    zip_path = os.path.join(path, "temp.zip")
    with open(zip_path, "wb+") as fp:
        fp.write(gif_data)
    # 生成文件
    temp_file_list = []
    zipo = zipfile.ZipFile(zip_path, "r")
    for file in zipo.namelist():
        temp_file_list.append(os.path.join(path, file))
        zipo.extract(file, path)
    zipo.close()
    # 读取所有静态图片，合成gif
    image_data = []
    for file in temp_file_list:
        image_data.append(imageio.imread(file))
    imageio.mimsave(os.path.join(path, str(pid) + ".gif"), image_data, "GIF", duration=delay / 1000)
    # 清除所有中间文件
    for file in temp_file_list:
        os.remove(file)
    os.remove(zip_path)


# 下载单组作品
def download(path, illust):
    if json.loads(rf.get_html("https://www.pixiv.net/ajax/illust/" + illust + "/ugoira_meta", headers))["error"]:
        if illust not in p_pic_flag:
            p_pic_flag[illust] = 0
            with open('p_pic_flag.json', 'w') as f:
                json.dump(p_pic_flag, f)
        all_pic_urls = json.loads(rf.get_html("https://www.pixiv.net/ajax/illust/" + illust + "/pages", headers))['body']
        pageCount = len(all_pic_urls)
        pn = p_pic_flag[illust]
        for p in tqdm(range(pn, pageCount), desc=illust):
            time.sleep(random.randint(2, 10))  # 随机等待时间
            urls = all_pic_urls[p]['urls']
            url = urls['original']
            pic_name = url.split('/')[-1]
            pic_path = path + pic_name
            response = rf.get_response(url, headers)
            with open(pic_path, 'wb+') as f:
                f.write(response.content)
            if not rf.is_valid(pic_path):  # 下载失败
                pic_path_l = pic_name.split('.')[-2]
                pic_path_r = pic_name.split('.')[-1]
                pic_path = path + pic_path_l + '_1.' + pic_path_r
                url = urls['regular']
                response = rf.get_response(url, headers)
                with open(pic_path, 'wb+') as f:
                    f.write(response.content)
                if not rf.is_valid(pic_path):
                    pic_path = path + pic_path_l + '_2.' + pic_path_r
                    url = urls['small']
                    response = rf.get_response(url, headers)
                    with open(pic_path, 'wb+') as f:
                        f.write(response.content)
                    if not rf.is_valid(pic_path):
                        pic_path = path + pic_path_l + '_3.' + pic_path_r
                        url = urls['thumb_mini']
                        response = rf.get_response(url, headers)
                        with open(pic_path, 'wb+') as f:
                            f.write(response.content)
            p_pic_flag[illust] += 1
            with open('p_pic_flag.json', 'w') as f:
                json.dump(p_pic_flag, f)
        p_id_flag.append(illust)
        with open('p_id_flag.json', 'w') as f:
            json.dump(p_id_flag, f)
        p_pic_flag.pop(illust)
        with open('p_pic_flag.json', 'w') as f:
            json.dump(p_pic_flag, f)
    else:
        while True:
            # noinspection PyBroadException
            try:
                downloadGIF(illust, path)
                if imghdr.what(path + str(illust) + ".gif") == "gif":
                    p_id_flag.append(illust)
                    with open('p_id_flag.json', 'w') as f:
                        json.dump(p_id_flag, f)
                    print('成功下载  图片：', str(illust) + ".gif")
                    break
            except Exception:
                pass


# 指定画师爬取
def by_users():
    for user in users:
        print('给爷爬！user: ', user)
        illusts = json.loads(rf.get_html("https://www.pixiv.net/ajax/user/" + user + "/profile/all", headers))['body'][
            'illusts'].keys()
        path = rootpath + user + "/"
        if not os.path.exists(path):
            os.mkdir(path)
        for illust in illusts:
            if illust in p_id_flag:
                continue
            download(path, illust)


# 指定标签爬取
def by_tags():
    for tag in tags:
        print('给爷爬！tag: ', tag)
        page = 1
        while True:
            url = "https://www.pixiv.net/ajax/search/artworks/" + tag + "?word=" + tag + "&order=date_d&mode=all&p=" + str(
                page) + "&s_mode=s_tag_full&type=all&lang=zh"
            illdatas = json.loads(rf.get_html(url, headers))['body']['illustManga']['data']
            if len(illdatas) == 0:
                print('tag: ', tag, '爬完了！')
                break
            for illdata in illdatas:
                illust = illdata['id']
                if illust in p_id_flag:
                    continue
                download(rootpath, illust)
            page += 1


# 指定作品爬取
def by_illusts():
    for illust in needs:
        if illust in p_id_flag:
            continue
        download(rootpath, illust)


# 以下需要自行设置
pattern = 0  # 选择模式 0：指定标签;1：指定画师;2: 指定作品
rootpath = "E://pixiv/"
users = []  # 画师ID
tags = []  # 标签
needs = []  # 作品ID
headers = {
    # 使用开发者工具获取自己的headers
}
# 以上需要自行设置

socket.setdefaulttimeout(20)  # 参考了blog——六脉神贱
with open('p_id_flag.json') as f_obj:  # 加载已下载作品集列表
    p_id_flag = json.load(f_obj)
with open('p_pic_flag.json') as f_obj:  # 加载已下载单图列表
    p_pic_flag = json.load(f_obj)
if pattern == 0:
    by_tags()
elif pattern == 1:
    by_users()
elif pattern == 2:
    by_illusts()
print('我滴任务完成啦啊哈哈哈哈哈！')
rf.over_tip()
exit()
