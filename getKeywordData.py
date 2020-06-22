
import time
import json
import datetime
import requests
from bs4 import BeautifulSoup

class machineLearning():
    
    @staticmethod
    def renewWeight(keyword):

        print( '学习关键字：',keyword ,'\n')

        with open('word_weights.json','r+',encoding='utf-8') as f:
            weight_json = json.loads( f.read() )
        
        # 初始化
        if not weight_json.__contains__(keyword):
            print( '关键字未学习，进行初始化...\n' )
            weight_json[keyword] = {
                'last_renew_time':0
            }

        #获得本地储存的数据中keyword_dict部分
        keyword_dict = weight_json[keyword]

        print('对关键字“%s”进行学习...\n' %( keyword ) )

        #直接把keyword_dict传给函数，让函数自己去判断，进行不同时间范围的学习，然后返回来
        keyword_dict = machineLearning.getWeight(keyword,keyword_dict)

        #然后更新last_renew_time，以时间戳的形式
        keyword_dict['last_renew_time'] = time.time()

        #最后把函数更新后的keyword_dict赋值给weight_json中的{{keyword}}键
        weight_json[keyword] = keyword_dict

        # 最后对数据进行储存
        with open('word_weights.json','r+',encoding='utf-8') as f:
      
            x = json.dumps(weight_json,ensure_ascii=False)
            f.seek(0,0)
            f.truncate()
            f.write(x)
            print('数据已储存\n')
            del x
            
     

    @staticmethod
    def getWeight(keyword,keyword_dict):   
        # keyword 要进行学习的关键字(str)
        
        # 代理地址
        # PROXY = {}
        PROXY = {'http': 'localhost:10809','https': 'localhost:10809'}

        # 最大点击数（超过这个点击数的bug点击数会取模）
        # 有很多公文点击量确实出了问题，尤其是2017年的
        MAX_CLICK_TIMES = 3000

        # 该函数只在最后做收尾
        def getThisYearWeight(keyword,keyword_dict):
            #由于今年的公文要排除掉七天内的，避免偶然性，因此要进行特殊处理

            #获取今年年份
            this_year = int( datetime.datetime.now().strftime('%Y') )

            print('搜索今年内容...')

            year_click_times = 0
            year_doc_num = 0
            week_click_times = 0
            week_doc_num = 0

            #用今年的公文减去七天内的公文,先算今年的，再减去一周内的
            for dayy in [ '7#一周内'.encode('gbk') , str(this_year)]:

                print('搜索',dayy,'内容...\n')

                respond_list = requests.post(
                    url = 'https://www1.szu.edu.cn/board/infolist.asp?',
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20120101 Firefox/33.0'},
                    proxies = PROXY,
                    data = {'dayy':dayy,'from_username':'','keyword':keyword.encode('gbk'),'searchb1':'%CB%D1%CB%F7'} 
                    )
        
                respond_list.encoding = 'gbk'
                soup = BeautifulSoup(respond_list.text,"html5lib")
            
                try:
                    father_tag = soup.find_all("table")[8].find_all("tr")[2:]                 
                except(IndexError):
                    print( '连接错误或今年未出现这个关键字\n' )
                    continue

                #今年
                if dayy == str(this_year):
                    for content in father_tag:                        
                        year_click_times += int( content.find_all("td")[6].text ) % MAX_CLICK_TIMES
                        year_doc_num += 1                     
                #本周
                else:
                    for content in father_tag:                                             
                        week_click_times += int( content.find_all("td")[6].text ) % MAX_CLICK_TIMES
                        week_doc_num += 1    

            #遍历结束后
            total_click_times = year_click_times - week_click_times
            total_doc_num = year_doc_num - week_doc_num

            print(this_year,'年点击数累计：',year_click_times,'\n年公文数累计：',year_doc_num,'\n')
            print('7天内点击数累计：',week_click_times,'\n7天内公文数累计：',week_doc_num,'\n')
            print( '减去7天内的数据,今年点击数为',total_click_times,'\n公文数累计:',total_doc_num,'\n')

            keyword_dict[str(this_year)] = {
                'click_times':total_click_times,
                'doc_num':total_doc_num
            }

            #最后进行一次总计
            total_click_times = 0
            total_doc_num = 0

            # x是'2014'到'2020'
            for x in list( keyword_dict.keys() ):
                if x in ['last_renew_time','weight','total_doc_num','total_click_times']:
                    continue

                current_k_t = keyword_dict[x]['click_times']
                current_d_n = keyword_dict[x]['doc_num']  

                total_click_times += current_k_t
                total_doc_num += current_d_n  

            else:
                if total_doc_num == 0:
                    average_click_time = 0
                else:
                    average_click_time = int( total_click_times / total_doc_num )

                keyword_dict['weight'] = average_click_time
                keyword_dict['total_doc_num'] = total_doc_num
                keyword_dict['total_click_times'] = total_click_times

                print( '学习结束，关键词“%s”的权重（平均点击数）为%s' %( keyword , average_click_time ) )
                return keyword_dict
        
        # 下面内容获取13年至今公文数据
        # 先运行下面这些代码，最后再运行getThisYearWeight函数收尾

        # 获取今年年份(int)
        this_year = int( datetime.datetime.now().strftime('%Y') )
        
        year_click_times = 0
        total_click_times = 0
        year_doc_num = 0
        total_doc_num = 0

        #遍历从2013年至去年的所有公文
        for dayy in range(2013,this_year):

            print('搜索',dayy,'年...')

            respond_list = requests.post(
                url = 'https://www1.szu.edu.cn/board/infolist.asp?',
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20120101 Firefox/33.0'},
                proxies = PROXY,
                data = {'dayy':str(dayy),'from_username':'','keyword':keyword.encode('gbk'),'searchb1':'%CB%D1%CB%F7'} 
                )
    
            respond_list.encoding = 'gbk'
            soup = BeautifulSoup(respond_list.text,"html5lib")
        
            try:
                father_tag = soup.find_all("table")[8].find_all("tr")[2:]                 
            except(IndexError):
                print( '连接错误或该关键字无公文\n' )
                continue

            for content in father_tag:  
                year_click_times += int( content.find_all("td")[6].text ) % MAX_CLICK_TIMES
                year_doc_num += 1

            keyword_dict[str(dayy)] = {
                'click_times':year_click_times,
                'doc_num':year_doc_num
            }

            print('%s年点击数累计：' %dayy ,year_click_times,'\n公文数累计：',year_doc_num,'\n')

            total_click_times += year_click_times
            total_doc_num += year_doc_num
            year_click_times = 0
            year_doc_num = 0
        
        #遍历结束后：
        else:
            keyword_dict = getThisYearWeight(keyword,keyword_dict)
            return keyword_dict
        

if __name__ == "__main__":    

    machineLearning.renewWeight( input( '输入你要分析（更新数据）的关键字：' ) )

       