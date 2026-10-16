"""Prepare the public HTML snapshot using the source site's HTML/CSS/JS structure."""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qs
import sys
import re
from lxml import html, etree

ROOT = Path(__file__).resolve().parent
page = int(sys.argv[1]) if len(sys.argv) > 1 else 1
if page not in (1, 2):
    raise ValueError('Only captured pages 1 and 2 are supported')
source_name = 'source-training.html' if page == 1 else 'source-training-page2.html'
source = (ROOT / source_name).read_text(encoding='utf-8-sig')
# Correct invalid source markup before adding responsive classes.
source = source.replace('<img></a>', '</a>').replace('</img>', '')
source = re.sub(r'background: transparent url\(""\)', 'background: transparent', source)
source = source.replace('color;#ccc', 'color:#ccc')
source = source.replace('課程分類</span></h2>', '課程分類</h2>')
source = source.replace('</div>\n</li>\n</ul>\n<div class="leftbox_down_3">', '</li>\n</ul>\n</div>\n<div class="leftbox_down_3">')
source = re.sub(r'<h2 class="(left_member|leftbox)"(.*?)>(.*?)</h2>', r'<div class="\1"\2>\3</div>', source, flags=re.S)
doc = html.document_fromstring(source)
doc.set('lang', 'zh-Hant')
doc.set('data-page', str(page))
doc.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-Hant')
head = doc.find('head')
etree.SubElement(head, 'meta', name='viewport', content='width=device-width, initial-scale=1')
etree.SubElement(head, 'meta', name='description', content='暐凱國際附設職業訓練中心：食安課程、HACCP課程、衛生講習與持續教育訓練課程資訊。')
etree.SubElement(head, 'link', href='css/training-rwd.css', rel='stylesheet', type='text/css')
for s in head.findall('script'):
    head.remove(s)
body = doc.find('body')
skip = etree.Element('a', href='#main-content', attrib={'class':'skip-link'})
skip.text = '跳至課程內容'
body.insert(0, skip)
top = doc.xpath('//div[@class="top"]')[0]
top.xpath('./h3')[0].text = None
utility = top.xpath('./h3')[0]
utility[-1].tail = ''  # The public snapshot's visitor IP is not the local visitor's IP.
utility.set('class', 'utility-links')
top.xpath('.//img')[0].set('alt', '暐凱國際附設職業訓練中心')
doc.xpath('//h2[@class="banner"]/img')[0].set('alt', 'FSI數位學習平台：多國語言線上食品衛生課程')
left = doc.xpath('//div[@class="left"]')[0]
left.set('aria-label', '會員服務及課程導覽')
for elem in left.xpath('.//div[@class="leftbox_up_3"]'):
    elem.tag = 'h2'
left.xpath('.//a[@class="left_bt01"]')[0].set('aria-label', '會員中心')
left.xpath('.//a[@class="left_bt02"]')[0].set('aria-label', '會員登出')
right = doc.xpath('//div[@class="right"]')[0]
right.set('id', 'main-content')
right.set('role', 'main')
right.set('tabindex', '-1')
search = right.xpath('./form')[0]
search.set('id', 'course-search')
search.set('aria-label', '課程搜尋')
fields = ['keyword','time_start','time_end','activity_place','dc']
names = ['關鍵字','活動開始日期','活動結束日期','開課地區','課程分類']
for id_, name in zip(fields,names):
    e = doc.get_element_by_id(id_)
    e.set('aria-label', name)
    e.set('class', 'search-control')
    if id_.startswith('time_'):
        e.set('type', 'date')
        e.attrib.pop('onfocus', None)
        e.attrib.pop('size', None)
for th in search.xpath('.//th'):
    th.set('scope', 'row')
date_cell = doc.get_element_by_id('time_start').getparent()
start = doc.get_element_by_id('time_start')
end = doc.get_element_by_id('time_end')
start.tail = None
end.tail = None
date_cell.remove(start)
date_cell.remove(end)
date_row = etree.SubElement(date_cell, 'div', attrib={'class':'date-range'})
date_row.append(start)
separator = etree.SubElement(date_row, 'span', attrib={'aria-hidden':'true'})
separator.text = '～'
date_row.append(end)
hint = etree.SubElement(date_cell, 'p', id='date-hint', attrib={'class':'date-hint'})
hint.text = '若兩者未填則搜尋本月份起的課程資料'
start.set('aria-describedby','date-hint')
end.set('aria-describedby','date-hint')
buttons = search.xpath('./div')[0]
buttons.set('class','search-actions')
for node in list(buttons):
    buttons.remove(node)
for kind, text, image in [('submit','開始查詢','bt03.jpg'),('reset','清除重填','bt04.jpg')]:
    button = etree.SubElement(buttons, 'button', type=kind)
    etree.SubElement(button,'img',src='images/training/'+image,alt=text)
error = etree.SubElement(search,'p',id='search-error',attrib={'role':'alert','class':'search-error'})
error.set('hidden','hidden')
# Keep the category artwork and links exactly as on the source.
categories = etree.Element('div',attrib={'class':'course-categories','aria-label':'課程分類'})
category_links = right.xpath('./a[img]')
category_names = ['HACCP課程','3年12小時回訓課程','衛生講習','ESG永續.ISO14064溫室氣體','PCQI','隨選視訊課程FSI Foodflix','寵物食品','ISO45001']
right.insert(right.index(category_links[0]), categories)
for a, name in zip(category_links,category_names):
    a.find('img').set('alt',name)
    categories.append(a)
# A grid already ends its own line; remove the source's first manual line break.
next_element = categories.getnext()
if next_element is not None and next_element.tag == 'br':
    right.remove(next_element)
course_table = right.xpath('./form[@method="get"]/table')[0]
course_table.set('class','course-list')
course_table.set('role','presentation')
for row in course_table.xpath('./tr'):
    cells = row.xpath('./td')
    if len(cells)==2:
        row.set('class','course-row')
        cells[0].set('class','course-image')
        cells[1].set('class','course-content')
        tables = cells[1].xpath('./table')
        for table, cname in zip(tables,['course-heading','course-details','course-actions']):
            table.set('class',cname)
            table.set('role','presentation')
        title = tables[0].xpath('.//a')[0].text_content().strip()
        for img in cells[0].xpath('.//img'):
            img.set('alt', title+'課程海報')
            img.set('loading','lazy')
        for img in tables[-1].xpath('.//img'):
            img.set('alt','我要報名' if 'apply' in img.get('src','') else '匯款確認回覆')
    else:
        row.set('class','course-divider')
for img in doc.xpath('//img'):
    if 'alt' not in img.attrib:
        path = img.get('src','')
        img.set('alt', 'FSI官方Instagram' if 'instagram' in path else 'Line官方帳號QR Code' if '20241216124627' in path else '課程資訊')
    if img.get('src','').startswith('/upload/'):
        img.set('src',img.get('src').lstrip('/'))
# Closed demo: only the two captured pages may navigate.
for node in doc.xpath('//*[@href or @action]'):
    attr = 'action' if node.tag=='form' else 'href'
    value = node.get(attr)
    if value is None or value.startswith('#'):
        continue
    route = urlsplit(value)
    if attr=='href' and route.path.lstrip('/')=='training.php':
        page_num = parse_qs(route.query).get('num', ['1'])[0]
        node.set(attr,'training-page2.html' if page_num == '2' else 'training.html')
    elif attr=='href' and node.tag=='link':
        continue
    elif attr=='action':
        node.set(attr,'#demo-dialog')
        node.set('method','get')
    else:
        label = node.get('aria-label') or node.text_content().strip()
        if not label:
            label = ' / '.join(img.get('alt','') for img in node.xpath('.//img'))
        node.set('href','#demo-dialog')
        node.set('data-demo-label',label or '此功能')
        node.attrib.pop('target',None)
for a in doc.xpath('//a[@target="_blank"]'):
    a.set('rel','noopener noreferrer')
pagination = doc.xpath('//div[@class="pagination"]')[0]
pagination.set('role','navigation')
pagination.set('aria-label','課程分頁')
for a in pagination.xpath('./a'):
    if a.text_content().strip() == '第'+str(page)+'頁':
        a.set('aria-current','page')
# The source's fifth navigation item has no destination; do not invent a route.
inactive = doc.xpath('//a[@class="mouse_bt05"]')[0]
inactive.tag = 'span'
inactive.set('aria-label','課程成果')
# Do not load the third-party Facebook SDK or an external page in an iframe.
for script in list(doc.xpath('//script')):
    script.getparent().remove(script)
for widget in doc.xpath('//div[@class="fb-like-box"]'):
    widget.attrib.clear()
    widget.set('class','demo-social')
    social = etree.SubElement(widget,'a',href='#demo-dialog',attrib={'data-demo-label':'Facebook 官方社群'})
    social.text = 'FSI 暐凱國際 Facebook 官方社群'
dialog = etree.SubElement(body,'dialog',id='demo-dialog',attrib={'aria-labelledby':'demo-title','aria-describedby':'demo-message'})
etree.SubElement(dialog,'h2',id='demo-title').text = 'DEMO 功能展示'
etree.SubElement(dialog,'p',id='demo-message').text = '此頁為展示版本，不會連接外部網站或送出資料。'
close_form = etree.SubElement(dialog,'form',method='dialog')
etree.SubElement(close_form,'button',type='submit',autofocus='autofocus').text = '知道了'
etree.SubElement(body,'script',type='text/javascript',src='js/training-rwd.js')
doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
output = etree.tostring(doc, method='html', encoding='unicode', pretty_print=True, doctype=doctype)
filenames = ['training.html','training.php','index.html'] if page == 1 else ['training-page2.html','training-page2.php']
for filename in filenames:
    (ROOT / filename).write_text(output,encoding='utf-8')
print('Created', ', '.join(filenames), '; courses:',len(course_table.xpath('./tr[@class="course-row"]')))
