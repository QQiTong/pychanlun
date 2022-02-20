import requests
import urllib
import re
import os

from spidersina.sinaBlogContentTool import sinaBlogContentTool


class Spider:
    '''
    功能：用于下载sina博客内容。
    初始输入：类别为“全部博文”的页面URL
            自动解析页面，获取所有类别
            用户可按照分类类别来下载博客内容
    最终结果：博文文字+图片均保存到本地，为markdown格式文件
    '''

    def __init__(self, indexUrl):
        print('Spider')
        self.indexUrl = indexUrl
        content = indexUrl.split('/')[-1].split('_')
        self.userID = content[1]
        self.defaultPage = self.getPage(self.indexUrl)

    def getPage(self, indexUrl):
        '''获取indexUrl页面'''
        response = urllib.request.urlopen(indexUrl)
        # decode = response.read().decode("utf-8")

        return response.read().decode("utf-8")

    def getPageNum(self, page):
        '''计算有几页博客目录'''
        pattern = re.compile('<li class="SG_pgnext">', re.S)
        result = re.search(pattern, page)
        if result:
            print("目录有多页，正在计算……")
            pattern2 = re.compile('<li class="SG_pgnext">.*?>共(.*?)页', re.S)
            num = re.search(pattern2, page)
            pageNum = str(num.group(1))
            print("共有", pageNum, "页")
        else:
            print("只有1页目录")
            pageNum = 1
        return int(pageNum)

    def getTypeNum(self):
        '''计算有几种分类'''
        pattern = re.compile('<span class="SG_dot">.*?<a href="(.*?)".*?>(.*?)</a>.*?<em>(.*?)</em>', re.S)
        result = re.findall(pattern, self.defaultPage)
        pattern2 = re.compile('<strong>全部博文</strong>.*?<em>(.*?)</em>', re.S)
        result2 = re.search(pattern2, self.defaultPage)
        self.allType = {}
        i = 0
        self.allType[i] = (self.indexUrl, "全部博文", result2.group(1)[1:-1])
        for item in result:
            i += 1
            self.allType[i] = (item[0], item[1], item[2][1:-1])
        print("本博客共有以下", len(self.allType), "种分类：")
        for i in range(len(self.allType)):
            print("ID: %-2d  Type: %-30s Qty: %s" % (i, self.allType[i][1], self.allType[i][2]))

    #             , self.allType[i][0]

    def getBlogList(self, page):
        '''获取一页内的博客URL列表'''
        pattern = re.compile(
            '<div class="articleCell SG_j_linedot1">.*?<a title="" target="_blank" href="(.*?)">(.*?)</a>', re.S)
        result = re.findall(pattern, page)
        blogList = []
        for item in result:
            blogList.append((item[0], item[1].replace('&nbsp;', ' ')))
        return blogList

    def mkdir(self, path):
        isExist = os.path.exists(path)
        if isExist:
            # print ("名为", path, "的文件夹已经存在")
            return False
        else:
            print("正在创建名为", path, "的文件夹")
            os.makedirs(path)

    def saveBlogContent(self, path, url):
        '''保存url指向的博客内容'''
        page = self.getPage(url)
        blogTool = sinaBlogContentTool(page)
        blogTool.parse()

        # filename =  path + '/' + blogTool.time + '  ' + blogTool.title.replace('/', '斜杠') + '.markdown'
        # print("bug", blogTool.title, blogTool.title.replace('/', '斜杠'))
        processBlogTitle = path + '/' + blogTool.time.replace(':', '_')[:-3] + ' 【' + blogTool.title.replace('/',
                                                                                                             '斜杠') + '】.markdown'
        imgfiledir = path + '/' + blogTool.title.replace('/', '斜杠')
        with open(processBlogTitle, 'w+', encoding="utf-8") as f:
            f.write("URL: " + url)
            # f.write("标签：")
            for item in blogTool.tags:
                print(item)
                f.write(item)
                f.write(' ')
            f.write('\n')
            f.write("类别：")
            f.write(blogTool.types)
            f.write('\n')
            picNum = 0
            for item in blogTool.contents:
                if item[0] == 'txt':
                    f.write('\n')
                    if item[1] != '':
                        f.write("<h1>" + item[1] + "</h1>")
                elif item[0] == 'img':
                    picNum += 1
                    self.mkdir(imgfiledir)
                    originArr = item[1].split('/')
                    imgcode = originArr[4][:-4]
                    targetBigImg = "http://" + originArr[2] + "/orignal/" + imgcode
                    f.write('\n')
                    f.write('\n')
                    f.write('![' + str(picNum) + '](' + blogTool.title.replace('/', '斜杠') + '/' + str(
                        picNum) + ".png" + ')')
                    download_img(targetBigImg, imgfiledir + '/' + str(picNum) + ".png")
        print("下载成功")

    def getBlogName(self, page):
        '''获取博客名字，暂未调用'''
        pattern = re.compile('<span id="blognamespan">(.*?)</span>', re.S)
        result = re.search(pattern, page)
        print(result.group(1))
        return result.group(1)

    def run(self):
        self.getTypeNum()
        i = input("请输入需要下载的类别ID(如需要下载类别为“全部博文”类别请输入0):")
        page0 = self.getPage(self.allType[int(i)][0])
        pageNum = self.getPageNum(page0)
        urlHead = self.allType[int(i)][0][:-6]
        typeName = self.allType[int(i)][1]
        typeBlogNum = self.allType[int(i)][2]
        if typeBlogNum == '0':
            print("该目录为空")
            return
        self.mkdir(typeName)
        for j in range(pageNum):
            print("------------------------------------------正在下载类别为", typeName, "的博客的第", str(j + 1),
                  "页------------------------------------------")
            url = urlHead + str(j + 1) + '.html'
            page = self.getPage(url)
            blogList = self.getBlogList(page)
            print("本页共有博客", len(blogList), "篇")
            for item in blogList:
                print("正在下载博客《", item[1], "》中……")
                self.saveBlogContent(typeName, item[0])
        print("全部下载完毕")


def download_img(img_url, filename):
    header = {"Referer": "http://blog.sina.com.cn/",
              "User-Agent":
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
    r = requests.get(img_url, headers=header, stream=True)
    with open(filename, 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    # indexUrl = sys.argv[1]
    indexUrl = 'http://blog.sina.com.cn/s/articlelist_2384425442_0_1.html'
    spider = Spider(indexUrl)
    #     spider.getBlogName(spider.defaultPage)
    #     print spider.getPage(indexUrl)
    #     spider.getPageNum()
    #     spider.getIndexPageUrl(0, 2)
    #     spider.getTypeNum()
    spider.run()
