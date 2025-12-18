import time

from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup
page = ChromiumPage()
tab = page.latest_tab
# url = "https://www.baidu.com"
# url = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=asdf&fenlei=256&rsv_pq=0x9647d2090000e43c&rsv_t=09ffuUN39r6wv9%2FBqsAwZUuAJ1q9z1hppzLcl1EgmLa%2FnBOH4t5RzqAdbyDX&rqlang=en&rsv_dl=tb&rsv_enter=1&rsv_sug3=5&rsv_sug1=1&rsv_sug7=100&rsv_btype=i&prefixsug=asdf&rsp=0&inputT=894&rsv_sug4=895"
url = "https://www.nxzgh.org.cn/#/newsCenter/index2/2"
tab.get(url)
li_eles = tab.eles("css:div.pointer")
ul_ele = tab.ele("css:div.right-box")
# for li in li_eles:
#     li.set.style('backgroundColor', 'rgba(255, 255, 0, 0.3)')
ul_ele.set.style('backgroundColor', 'rgba(255, 255, 0, 0.3)')
# tab.get_screenshot('screen_shot.png')
rect_size = tab.rect.size
print(rect_size)
# tab.get_screenshot('screenshot_full.png', full_page=True, right_bottom=(1920, 1080))
tab.get_screenshot('screenshot_full.png', right_bottom=(rect_size[0] / 2, rect_size[1] / 2))
# time.sleep(50)
#   .xpath-highlight {
#     outline: 2px solid yellow !important;
#     outline-offset: 2px;
#     background-color: rgba(255, 255, 0, 0.2);
#   }
