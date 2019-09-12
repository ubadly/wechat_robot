import json,random,re,os,time,hashlib
import itchat,requests
from itchat.content import *
from urllib import parse


def create_md5(string):#生成md5值
    text= hashlib.md5()
    text.update(string.encode(encoding='utf-8'))
    hl = text.hexdigest()
    return hl



def process(info,userid):
    name = itchat.search_friends(userName=userid)['RemarkName'] if itchat.search_friends(userName=userid)['RemarkName'] != '' else itchat.search_friends(userName=userid)['NickName']
    if info == '笑话':
        print('收到了{}的笑话请求'.format(name))
        xiaohua(userid)
    elif info[-2:] == '天气':
        print('收到{}的天气请求'.format(name))
        tianqi(info,userid)
    elif info == '我的头像':
        print('收到{}的头像请求'.format(name))
        getHeadImg(userid)
    else:
        print('收到{}的翻译请求'.format(name))
        translate(info,userid)



 #功能模块
##########################################################
def translate(words,userid):#翻译单词
    ts = '' + str(int(time.time()*1000))
    salt = ts + str(random.randint(0,9))
    sign = create_md5('fanyideskweb' + words + salt + 'n%A-rKaT5fb[Gy?;N5@Tj')
    bv = create_md5('5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36')

    url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Referer':'http://fanyi.youdao.com/',
        'Cookie':'OUTFOX_SEARCH_USER_ID=-1230324205@106.34.48.35; OUTFOX_SEARCH_USER_ID_NCOO=2014994095.072274; JSESSIONID=aaaHQbw0exCA0erFGop0w; ___rl__test__cookies=1567933779347',
        'Host':'fanyi.youdao.com'
    }
    data = {
        'i':words,
        'from':'AUTO',
        'to':'AUTO',
        'smartresult':'dict',
        'client':'fanyideskweb',
        'salt':salt,
        'sign':sign,
        'ts':ts,
        'bv':bv,
        'doctype':'json',
        'version':'2.1',
        'keyfrom':'fanyi.web',
        'action':'FY_BY_REALTlME'
    }
    result = requests.post(url,data=data,headers=headers).json()
    result = result['translateResult'][0][0]['tgt']
    itchat.send(result,toUserName=userid)


def xiaohua(userid):#处理笑话请求
    try:
        url = 'https://www.apiopen.top/satinApi?type=2&page=1'
        html = requests.get(url).content.decode('utf-8')
        xh_lists = json.loads(html)
        xh_info = xh_lists['data']
        # pprint.pprint(xh)
        lists = []
        for i in xh_info:
            lists.append(i['text'])
        xh = random.choice(lists)
        itchat.send(xh,toUserName=userid)
    except:
        itchat.send('请求失败！请稍后重试！',toUserName=userid)



def tianqi(info,userid):#处理天气信息
    city = re.findall(r'(.*?)天气', info)[0]
    city = parse.quote(city)
    url = 'https://www.apiopen.top/weatherApi?city={}'.format(city)
    try:
        tq = json.loads(requests.get(url).content.decode('utf-8'))
        if tq['code'] == '201':
            itchat.send(tq['msg'], toUserName=userid)
        else:
            tq_info = tq['data']
            city_info = tq_info['city']
            date = tq_info['forecast'][0]['date']  # 日期
            fengli = re.findall('\d', tq_info['forecast'][0]['fengli'])[0]  # 风力
            fengxiang = tq_info['forecast'][0]['fengxiang']  # 风向
            high = tq_info['forecast'][0]['high']  # 最高温度
            low = tq_info['forecast'][0]['low']  # 最低温度
            type = tq_info['forecast'][0]['type']  # 天气类型
            ganmao = tq_info['ganmao']
            itchat.send(
                '{}天气信息：\n日期：{}\n温度：{},{}\n风力：{}级\n风向：{}\n天气类型：{}\n感冒指数：{}'.format(city_info, date, high, low, fengli,
                                                                                     fengxiang, type, ganmao),
                toUserName=userid)
    except:
        itchat.send('请求出错！\n请判断城市输入是否有误！', toUserName=userid)

def getHeadImg(userid):#获取头像
    head_img = itchat.get_head_img(userName=userid)
    imgName = itchat.search_friends(userName=userid)['RemarkName'] if itchat.search_friends(userName=userid)['RemarkName'] != '' else itchat.search_friends(userName=userid)['NickName']
    with open('1.jpg','wb')as f:
        f.write(head_img)
    itchat.send_image('1.jpg',toUserName=userid)
    os.remove('1.jpg')


@itchat.msg_register(TEXT,isFriendChat=True)
def getInfo(msg):
    userid = msg['FromUserName']
    info = msg['Text']
    process(info,userid)


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    itchat.run()