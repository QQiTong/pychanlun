from bs4 import BeautifulSoup
from bs4.element import NavigableString
import urllib.request
class sinaBlogContentTool:
    def __init__(self,page):
        self.page = page
    
    def parse(self):
        '''解析博客内容'''
        soup = BeautifulSoup(self.page)
        
        self.title = soup.body.find(attrs = {'class':'titName SG_txta'}).string
        
        self.time = soup.body.find(attrs = {'class':'time SG_txtc'}).string
        self.time = self.time[1:-1]
        print("发表日期是：", self.time, "博客题目是：", self.title)
        
        self.tags = []
        for item in soup.body.find(attrs = {'class' : 'blog_tag'}).find_all('h3'):
            self.tags.append(item.string)
        
        self.types = "未分类"
        if soup.body.find(attrs = {'class' : 'blog_class'}).a:
            self.types = soup.body.find(attrs = {'class' : 'blog_class'}).a.string

        self.contents = []
        self.rawContent = soup.body.find(attrs = {'id' : 'sina_keyword_ad_area2'})

        for child in self.rawContent.children:
            if type(child) == NavigableString:
                self.contents.append(('txt', child.strip()))
            else:
                for item in child.stripped_strings:
                    self.contents.append(('txt', item))
                if child.find_all('img'):
                    for item in child.find_all('img'):
                        if(item.has_attr('real_src')):
                            self.contents.append(('img', item['real_src']))



if __name__ == '__main__':
    url = 'http://blog.sina.com.cn/s/blog_486e105c01000crv.html'
    page = urllib.request.urlopen(url).read().decode()
    blogTool = sinaBlogContentTool(page)
    blogTool.parse()
    