import requests
import os
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
# from requests_html import HTMLSession


headers = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}
def writelog(logstring):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    with open('./error_log_nettruyentop.txt', 'a', encoding='utf8') as f:
        f.write(current_time + '\t' + logstring+'\n')
    f.close()

def dumpData(data):
    with open('./nettruyentop.json', 'w') as f:
        json.dump(data, f)
    f.close()
def dumpData1(data,filePath):
    with open(filePath, 'w') as f:
        json.dump(data, f)
    f.close()
# get all information of item --lấy data chi tiết từng chap truyện
def getDetailItem(address,categogyId,comicsId):
    print("---> get data từng chap")
    print("Address: ", address)
    time.sleep(10);
    em = requests.get(address,headers=headers)
    # time.sleep(100);
    # em.html.render
    
    print(em.status_code)
    print("Content-type:", em.headers['content-type'])
    page = BeautifulSoup(em.text, 'html.parser')
    try:
        t1 = page.find('div',{'class':'profile-manga'}).find('div', {"class": "container"}).find('div', {"class": "summary_image"}).find('img').attrs['src'] 
        if t1 is None:
            t1=""
        else:
            t1 = t1
    except (ValueError, AttributeError):
        t1 =""
    try:
        t2 = page.find('div',{'class':'profile-manga'}).find('div', {"class": "container"}).find('div',{'class':'summary_content'}).find('div',{'class':'post-rating'}).find('span',{'class':'total_votes'})
        if t2 is None:
            t2 =""
        else:
            t2=t2.text.strip()
    except (ValueError,AttributeError):
        t2=""
    try:
        t3 =page.find('div',{'class':'profile-manga'}).find('div', {"class": "container"}).find('div',{'class':'summary_content'}).find('div',{'class':'author-content'})
        if t3 is None:
            t3 = ""
        else:
            t3=t3.text.strip()
    except (ValueError,AttributeError):
        t3 =""
    try:
        t4 =page.find('div',{'class':'profile-manga'}).find('div',{'class':'tab-summary '}).find('div',{'class':'summary_content_wrap'}).find('div',{'class':'post-status'}).find('div',{'class':'post-content_item'}).findAll('div')[2]
        if t4 is None:
            t4 =""
        else:
            t4 = t4.text.strip()
    except (ValueError,AttributeError):
        t4=""
    try:
        t5 =page.find('div',{'class':'content-area'}).find('div', {"class": "container"}).find('div',{'class':'description-summary'}).find('div',{'class':'summary__content'}).find('p')
        if t5 is None:
            t5=""
        else:
            t5 = t5.text.strip()
    except (ValueError,AttributeError):
        t5 =""
    detail = {
        # "title": page.find('main', {"class": "main"}).find('div', {"class": "container"}).find('h1').get_text().strip(),
        "thumnail-image": t1,
        "rating":t2,
        "author": t3,
        "status": 'On Going',

        # "genres": [x.text.strip() for x in page.find('div',{'class':'profile-manga'}).find('div', {"class": "container"}).find('div',{'class':'post-content'}).find('div',{'class':'post-content_item'}).find('div',{'class':'genres-content'}).findAll('a').text],
        "sumary":t5 
        }
    episode_list = page.find('div',{'class':'content-area'}).find('div', {"class": "container"}).find('div',{'class':'c-page__content'}).find('div', {"class": "listing-chapters_wrap"}).findAll('li')[2:]
    episode_list.reverse() #reverse để lấy vài chap đầu
    episode_links = []
    episode_index = 0
    for episode in episode_list:
        episode_index = episode_index +1;
        #giới hạn chỉ lấy 3 chap trên 1 truyện
        if episode_index <= 3: 
            episode_links.append({
                "name": episode.find('a').text.strip(),
                "link": episode.find('a').attrs['href'].strip(),
                "local-path":"/"+str(categogyId)+"/"+str(comicsId)+"/"+str(episode.find('a').text.strip()).replace(" ","")
                # "update":episode.find('span',{'class':'chapter-release-date'}).find('i').content
            })
            episode_links[episode_index-1]["img-Inventory"] = getAllLinkImagePerChapter(episode_links[episode_index-1]["link"],episode_links[episode_index-1]["name"])
        else:
            break;
    
    detail["episodes"] = episode_links
  
    return detail
def getAllLinkImagePerChapter(address, chapterId):
    print("lấy ảnh theo chap----->" + str(chapterId).upper()+"============")
    time.sleep(10);
    em = requests.get(address,headers=headers)
    print(em.status_code)
    print("Content-type:", em.headers['content-type'])
    time.sleep(10)
    page = BeautifulSoup(em.text, 'html.parser')
    image_list = page.find('div',{'class':'reading-content'}).findAll('div')
    image_inven =[]
    for item in image_list:
        img = item.find('img',{'class':'wp-manga-chapter-img'})
        try:
            d1 = img.attrs['id']
            if d1 is None:
                d1 ="error"
        except (ValueError, AttributeError):
            d1 ="error"
        try:
            d2 = img.attrs['src']
            if d2 is None:
                d2 ="error"
        except (ValueError, AttributeError):
            d2 ="error"
        if d1 !='error' or d2 != 'error':
            image_inven.append({
                "img-Id":d1.strip(),
                "img-Link":d2.strip()
            })
    print("========lấy xog ảnh chapter" + str(chapterId).upper())
    return image_inven
        

# download 1 episode
def DownloadImages(address, folder): # folder name episode
    page_soup = BeautifulSoup(requests.get(address,headers=headers).content, 'html.parser')
    image_list = page_soup.find('main', {"class": "main"}).find('div', {"class": "reading-detail box_doc"}).findAll('div', {"class": "page-chapter"})
    images = []
    for image in image_list:
        item = {
            "alt": image.find('img').attrs['alt'],
            "data-original": image.find('img').attrs['data-original'],
            "src": image.find('img').attrs['src'],
            "data-index": image.find('img').attrs['data-index'],
        }
        images.append(item)

        # download to folder:
        if "http" in item['src'][:5]:
            download_image(item['alt'], folder, item['src'])
        else:
            download_image(item['alt'], folder, "http:"+item['src'])

    return images

def download_image(namefile, folder, url):
    fixed_name = folder+"/" + "".join(x for x in namefile if (x.isalnum() or x=='.' or x == '_' or x == ' '))
    with open(fixed_name + '.jpg', 'wb') as handle:
        try:
            response = requests.get(url, headers={'referer': 'http://www.nettruyentop.com/'})
            if not response.ok:
                print("Warning response!")
                print(response)
                writelog(response)

            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
            handle.close()
        except Exception as e:
            print("Exception: ", e)
            handle.close()
    

# Download All Episode in 1 Comic
def DownloadAllEpisodes(parent_folder, episodes_list):
    # make folder
    for episode in episodes_list:
        episode_folder = parent_folder + '/' +  "".join(x for x in episode['name'] if (x.isalnum() or x=='.' or x == '_' or x == ' '))
        if not os.path.isdir(episode_folder):
            os.mkdir(episode_folder)
        try:
            print("Start download: ", episode['name'])
            DownloadImages(episode['link'], episode_folder)
        except Exception as e:
            print(episode['name'])
            print(e)
            print("Download Episode Error")
            writelog(episode['name'] + ":\t" + str(e))

def DownloadEpisodeWithIndex(parent_folder, episodes_list, index): # index is index of episode in episodes_list
    episode_folder = parent_folder + '/' +  "".join(x for x in episodes_list[index]['name'] if (x.isalnum() or x=='.' or x == '_' or x == ' '))
    print("Scan special 1 episode: ", episode_folder)

    if not os.path.isdir(episode_folder):
        os.mkdir(episode_folder)
    try:
        DownloadImages(episodes_list[index]['link'], episode_folder)
    except Exception as e:
        print(episodes_list[index]['name'])
        print(e)
        print("Download Episode Error")
        writelog(e)

def DownloadComicsWithName(name): # using with has nettruyentop.json file
    
    root_path = "E:/Project/crawl-project/src/nettruyentop/www.nettruyentop.com/"
    if not os.path.isdir(root_path):
        os.mkdir(root_path)

    # load file data
    with open('./nettruyentop.json', 'r') as f:
        all_items = json.load(f)
    f.close()
    
    for item in all_items:
        if name.lower() in item['title'].lower():
            print(item['title'])
            # Call download
            parent_folder = root_path + "/" + name + "/"
            if not os.path.isdir(parent_folder):
                os.mkdir(parent_folder)
            parent_folder += "".join(x for x in item['title'] if (x.isalnum() or x=='.' or x == '_' or x == ' ' or x == '-'))
            if not os.path.isdir(parent_folder):
                os.mkdir(parent_folder)

            DownloadAllEpisodes(parent_folder, item['detail']['episodes'])

# Call by thread
def DownloadAllEpisodesThread(item):
    print("Scan comic: ", item["title"])

    root_path = "D:\learning_code\lap_trinh_frontend\crawldataNettruyen\data"
    if not os.path.isdir(root_path):
        os.mkdir(root_path)

    parent_folder = root_path + "".join(x for x in item['title'] if (x.isalnum() or x=='.' or x == '_' or x == ' '))
    if not os.path.isdir(parent_folder):
        os.mkdir(parent_folder)

    DownloadAllEpisodes(parent_folder, item['detail']['episodes'])
#Run once -->lấy tất cả chap truyện theo cate
def GetPageItems(address,categogyId):
   
    items = []
    index = 0
    # print(requests.get(address,headers=headers).status_code)
    reppage =requests.get(address,headers)
    page = BeautifulSoup(reppage.content, 'html.parser')
    
    items_content = page.find('div', {"class": "page-content-listing"}).findAll('div', {"class": "page-item-detail"})
    for item in items_content:
        index = index +1;
        if index <= 4: #lấy 4 truyện trên 1 cate
            comicsId = 'CAT'+str(categogyId) +'-COM'+str(index);
            item_info = {
                'id':comicsId,
                "categogyId":categogyId,
                "link": item.find('div', {"class": "item-thumb"}).find('a').attrs['href'],
                "meta-thumnail-img": item.find('div', {"class": "item-thumb"}).find('img').attrs['src'],
                "title": item.find('div', {"class": "item-summary"}).find("div",{"class":"post-title"}).find('h3').find('a').text.strip()
                # "message_main": {
                    # "genres": item.find('div', {"class": "message_main"}).findAll('p')[0].text.split(":")[1],
                    # "status": item.find('div', {"class": "message_main"}).findAll('p')[1].text.split(":")[1],
                    # "view": item.find('div', {"class": "message_main"}).findAll('p')[2].text.split(":")[1],
                    # "comment": item.find('div', {"class": "message_main"}).findAll('p')[3].text.split(":")[1],
                    # "subscriber": item.find('div', {"class": "message_main"}).findAll('p')[4].text.split(":")[1],
                    # "update_time": item.find('div', {"class": "chapter-item"}).findAll('span')[5].text.split(":")[1],
                # }
                # "description": item.find('div', {"class": "box_text"}).text.strip()
            }

            # download description and detail, list episode link
            print("------------>LINK"+item_info["link"])
            item_info["detail"] = getDetailItem(item_info["link"],categogyId,comicsId=item_info["id"])
        else:
            break;
        items.append(item_info)

    return items

# Run once 
def GetItems(index):
    address_sub = "https://www.nettruyentt.com/tim-truyen?id={page_index}"

    if index == 1:
        address = "https://www.nettruyentt.com/tim-truyen"
    else:
        address = address_sub.format(page_index=index)

    items = []
    page = BeautifulSoup(requests.get(address,headers=headers).content, 'html.parser')
    items_content = page.find('div', {"class": "items"}).findAll('div', {"class": "item"})
    for item in items_content:
        
        item_info = {
            "link": item.find('div', {"class": "image"}).find('a').attrs['href'],
            "image": item.find('div', {"class": "image"}).find('img').attrs['data-original'],
            "title": item.find('div', {"class": "title"}).text.strip(),
            "message_main": {
                "genres": item.find('div', {"class": "message_main"}).findAll('p')[0].text.split(":")[1],
                "status": item.find('div', {"class": "message_main"}).findAll('p')[1].text.split(":")[1],
                "view": item.find('div', {"class": "message_main"}).findAll('p')[2].text.split(":")[1],
                "comment": item.find('div', {"class": "message_main"}).findAll('p')[3].text.split(":")[1],
                "subscriber": item.find('div', {"class": "message_main"}).findAll('p')[4].text.split(":")[1],
                "update_time": item.find('div', {"class": "message_main"}).findAll('p')[5].text.split(":")[1],
            },
            "description": item.find('div', {"class": "box_text"}).text.strip()
        }

        # download description and detail, list episode link
        item_info["detail"] = getDetailItem(item_info["link"])

        items.append(item_info)

    return items

# reun once --> lấy truyện trong categogy
def getCategogy():
    index =0
    categogy = []
    address1 ="https://kunmanga.com/"
    page = BeautifulSoup(requests.get(address1,headers=headers).content, 'html.parser')
    item_content = page.find('div', {"class": "sub-nav_content"}).find('ul',{"class":'sub-nav_list'}).findAll('li',{"class":"menu-item-type-taxonomy"})
    print(item_content)
    for item in item_content:
        index = index +1
        item_infor = {
            "id": index,
            "name":item.find('a').text.strip(),
            "link":item.find('a').attrs['href']
        }
        categogy.append(item_infor)
    dumpData1(categogy,'./categogy.json');
    return categogy
    
def GetPageDataByCategogy():
    index = 0
    
    cateaddress = []
    res =[]
    with open('./categogy.json','r',  encoding="utf8") as f:
        cateaddress = json.load(f)
    f.close()
    max_index = 29
    for index in range(0, max_index+1):
        print("=======categogy:" + cateaddress[index]['name']+"==========++++++=========")
        result = GetPageItems(cateaddress[index]["link"],cateaddress[index]['id'])
        res += result
    # print("SO luong truyen của categogy : ", len(cateaddress))
    dumpData1(res,'./categogyComics.json') 
# Run Once
def GetNettruyenData():
    index = 1
    max_index = 539
    all_items = []
    for index in range(1, max_index+1):
        result = GetItems(index)
        all_items += result
    print("SO luong truyen : ", len(all_items))
    dumpData(all_items)

# Main entry point
def DownloadNettruyenNet(): 
    # get from Pages
    all_items = GetNettruyenData()

    # get from JSON
    # with open('./nettruyentop.json', 'r') as f:
    #     all_items = json.load(f)
    # f.close()

    root_path = "D:\learning_code\lap_trinh_frontend\crawldataNettruyen\data"
    if not os.path.isdir(root_path):
        os.mkdir(root_path)

    # set start and end item index
    start_index = 0
    end_index = 20
    # Download Image to Local server
    for item in all_items[start_index:end_index]:
        print("Scan comic: ", item["title"])
        writelog("\n" + item["title"])

        beginTime = datetime.now()

        parent_folder = root_path + "".join(x for x in item['title'] if (x.isalnum() or x=='.' or x == '_' or x == ' '))
        if not os.path.isdir(parent_folder):
            os.mkdir(parent_folder)
        # danh sach item gom list episodes (nhieu episdie) moi episode tao 1 thu muc
        DownloadAllEpisodes(parent_folder, item['detail']['episodes'])

        writelog("Done: spendTime: " + str(datetime.now() - beginTime))
        print("SpendTime: ", datetime.now() - beginTime)
    
if __name__ == '__main__':
    # print(getCategogy());
    # GetPageDataByCategogy();
    GetPageItems("https://kunmanga.com/manga-genre/romance/page/3/",0)
    # getDetailItem("https://kunmanga.com/manga/the-beastly-count-after-dark/",1,0)
    # getAllLinkImagePerChapter("https://kunmanga.com/manga/noises-comeback/chapter-1/",0)
    
    # DownloadNettruyenNet()

    # Download error episode(chapter)
    # root_path = "D:\learning_code\lap_trinh_frontend\crawldataNettruyen\data"
    # with open('./nettruyentop.json', 'r') as f:
    #     all_items = json.load(f)
    # f.close()
    # with open('./categogy.json', encoding="UTF-8") as f:
    #     all_items = json.load(f)
    # f.close()
    # print(all_items[0]["id"])
    # DownloadEpisodeWithIndex(parent_folder=root_path + "Long Hổ 5 Thế", episodes_list=all_items[0]['detail']['episodes'], index=1)
    # DownloadComicsWithName('Conan - Bộ Đặc Biệt')