import re
with open('Tool.html') as f:
    h = f.read()
m = re.search(r'<script>(.*?)</script>', h, re.DOTALL)
s = m.group(1)
o = s.count('{')
c = s.count('}')
print('open:', o, 'close:', c, 'diff:', o-c)
