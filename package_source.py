"""Validate local resources and package the complete front-end source."""
from pathlib import Path
import json
import re
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageOps, ImageDraw
from lxml import html

root = Path(__file__).resolve().parent
doc = html.parse(str(root / 'training.html'))
missing = []
for element in doc.xpath('//*[@src or @href]'):
    attribute = 'src' if element.get('src') else 'href'
    path = element.get(attribute)
    if not path or path.startswith(('#','http:','https:','//','mailto:','tel:')):
        continue
    if not (root / urlsplit(path).path).is_file():
        missing.append(path)
assert not missing, missing
assert len(doc.xpath('//tr[@class="course-row"]')) == 20
assert len(doc.xpath('//*[@id="pic-bt"]')) == 0
assert doc.xpath('//button[@type="reset"]')
second = html.parse(str(root / 'training-page2.html'))
assert len(second.xpath('//tr[@class="course-row"]')) == 5
for filename in ['training.html','training.php','index.html','training-page2.html','training-page2.php']:
    demo_doc = html.parse(str(root / filename))
    assert not demo_doc.xpath('//iframe | //script[not(@src)]')
    for node in demo_doc.xpath('//*[@href or @src or @action]'):
        for attr in ['href','src','action']:
            value = node.get(attr)
            if value:
                assert not urlsplit(value).scheme and not urlsplit(value).netloc, (filename,value)
                assert not value.startswith(('/', '../')), (filename,value)
for document, target in [(doc, 'training-page2.html'), (second, 'training.html')]:
    assert document.xpath('//div[@class="pagination"]/a[@href="'+target+'"]')
for element in second.xpath('//*[@src]'):
    path = element.get('src')
    if not path.startswith(('http:','https:','//')):
        assert (root / path).is_file(), path
for stylesheet in ['css/training.css','css/training-rwd.css']:
    css = (root / stylesheet).read_text(encoding='utf-8-sig')
    for path in re.findall(r'url\(\s*["\']?([^\)"\']+)',css):
        assert (root / stylesheet).parent.joinpath(path).is_file(), path

source = Image.open(root / 'reference/source-desktop.png').convert('RGB')
implementation = Image.open(root / 'reference/desktop.png').convert('RGB')
comparison = Image.new('RGB',(source.width+implementation.width, max(source.height,implementation.height)+32),'white')
comparison.paste(source,(0,32))
comparison.paste(implementation,(source.width,32))
draw = ImageDraw.Draw(comparison)
draw.text((12,8),'SOURCE / 1280 x 900',fill='black')
draw.text((source.width+12,8),'RWD / 1280 x 900',fill='black')
comparison.save(root / 'reference/desktop-comparison.png')
source2 = Image.open(root / 'reference/source-page2-desktop.png').convert('RGB')
implementation2 = Image.open(root / 'reference/page2-desktop.png').convert('RGB')
assert source2.size == implementation2.size
comparison2 = Image.new('RGB',(source2.width*2,source2.height+32),'white')
comparison2.paste(source2,(0,32))
comparison2.paste(implementation2,(source2.width,32))
draw2 = ImageDraw.Draw(comparison2)
draw2.text((12,8),'SOURCE PAGE 2',fill='black')
draw2.text((source2.width+12,8),'RWD PAGE 2',fill='black')
comparison2.save(root / 'reference/page2-comparison.png')

print(json.dumps({'sourceScreenshot':source.size,'implementationScreenshot':implementation.size,'courses':20,'missingResources':missing}))
if (root / 'design-qa.md').exists():
    files = [root / name for name in ['training.html','training.php','index.html','training-page2.html','training-page2.php','README.md','design-qa.md']]
    for directory in ['css','js','images','upload','reference']:
        files.extend(sorted((root / directory).rglob('*')))
    with ZipFile(root / 'fsi-training-rwd.zip','w',ZIP_DEFLATED) as archive:
        for file in files:
            if file.is_file():
                archive.write(file,file.relative_to(root).as_posix())
    print('Created fsi-training-rwd.zip:',(root / 'fsi-training-rwd.zip').stat().st_size,'bytes')
