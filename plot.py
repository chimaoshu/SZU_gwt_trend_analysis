#coding:utf-8
import matplotlib.pyplot as plt
import json

def generatePic(keyword):

    with open('word_weights.json','r+',encoding='utf-8') as f:
        try:
            keyword_dict = json.loads( f.read() )[keyword]
        except KeyError:
            print( '不存在该关键字数据，请先运行 getKeyword.py 更新数据，校外需要连接vpn使用。' )
            return

    #用来正常显示中文标签
    plt.rcParams['font.sans-serif']=['SimHei'] 

    # 年份
    x_asis_year = [2013,2014,2015,2016,2017,2018,2019,2020]

    # 每年总公文数
    y1_asis_doc_num = []

    # 每年总点击数
    y2_asis_click_times = []

    # 遍历每一年
    for year in x_asis_year:

        # 若无这年的记录
        if not keyword_dict.__contains__( str( year ) ):
            
            y1_asis_doc_num.append( 0 )
            y2_asis_click_times.append( 0 )

        else:
            y1_asis_doc_num.append( keyword_dict[ str( year ) ]['doc_num'] )
            y2_asis_click_times.append( keyword_dict[ str( year ) ]['click_times'] )
    
    plt.subplot( 121 )
    plt.plot(x_asis_year, y1_asis_doc_num ,label='公文数量')
    plt.xlabel('年份')
    plt.ylabel('公文发布数量')
    plt.title('关于关键词 \'%s\' 的公文发布数趋势分析' %keyword)
    plt.legend()
    plt.grid()

    plt.subplot( 122 )
    plt.plot(x_asis_year, y2_asis_click_times ,label='点击数量')
    plt.xlabel('年份')
    plt.ylabel('公文点击数')
    plt.title('关于关键词 \'%s\' 的点击数趋势分析' %keyword)
    plt.legend()
    plt.grid()
    
    plt.show()

if __name__ == "__main__":
    generatePic( input( '输入要分析的关键字:' ) )