# -*- coding: utf-8 -*-
"""Генерация схемы алгоритма бота (.drawio) по уточнённым Н.У.

Координаты задаются в сантиметрах (как в TikZ-версии отчёта) и переводятся
в пиксели draw.io коэффициентом 40 px/см.
"""
import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'scheme', 'shema_avtomata.drawio')

K = 40.0          # px на сантиметр
OX, OY = 7.0, 1.2  # сдвиг начала координат (см)

FONT = 'fontFamily=Times New Roman;fontSize=12;'
STYLE = {
    'term': 'ellipse;whiteSpace=wrap;html=1;' + FONT + 'fontStyle=1;strokeWidth=1.5;',
    'proc': 'rounded=0;whiteSpace=wrap;html=1;' + FONT + 'strokeWidth=1.5;',
    'io': ('shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;'
           'fixedSize=1;' + FONT + 'strokeWidth=1.5;'),
    'dec': 'rhombus;whiteSpace=wrap;html=1;' + FONT + 'strokeWidth=1.5;',
    'legend': ('rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=8;'
               + FONT + 'fontSize=11;strokeWidth=1;'),
}

cells = []
_id = [10]


def nid(p='c'):
    _id[0] += 1
    return '%s%d' % (p, _id[0])


def px(x):
    return int(round((x + OX) * K))


def py(y):
    return int(round((y + OY) * K))


def node(kind, text, cx, cy, w, h):
    i = nid('n')
    cells.append(
        '<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
        '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
        % (i, escape(text).replace('\n', '&#10;'), STYLE[kind],
           px(cx - w / 2.0), py(cy - h / 2.0), int(round(w * K)), int(round(h * K))))
    return i


def edge(src, dst, label='', ex=(0.5, 1.0), en=(0.5, 0.0), pts=()):
    i = nid('e')
    style = ('edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;endFill=1;'
             'startArrow=none;' + FONT + 'labelBackgroundColor=#ffffff;'
             'exitX=%s;exitY=%s;exitDx=0;exitDy=0;entryX=%s;entryY=%s;entryDx=0;entryDy=0;'
             % (ex[0], ex[1], en[0], en[1]))
    geo = '<mxGeometry relative="1" as="geometry">'
    if pts:
        geo += '<Array as="points">' + ''.join(
            '<mxPoint x="%d" y="%d"/>' % (px(x), py(y)) for x, y in pts) + '</Array>'
    geo += '</mxGeometry>'
    cells.append('<mxCell id="%s" value="%s" style="%s" edge="1" parent="1" '
                 'source="%s" target="%s">%s</mxCell>'
                 % (i, escape(label), style, src, dst, geo))
    return i


def dot(cx, cy):
    i = nid('d')
    cells.append('<mxCell id="%s" value="" style="ellipse;fillColor=#000000;'
                 'strokeColor=#000000;" vertex="1" parent="1">'
                 '<mxGeometry x="%d" y="%d" width="8" height="8" as="geometry"/></mxCell>'
                 % (i, px(cx) - 4, py(cy) - 4))


# ---------------------------------------------------------------- блоки
MAIN, A, B = 0.0, 4.6, 7.4

start = node('term', 'НАЧАЛО', MAIN, 0.0, 3.2, 0.85)
init = node('proc', 'Н.У.\nНР := 0;   СП := 0;   СН := 0\nС := 0;   ИСТ := ∅',
            MAIN, -1.45, 5.4, 1.35)
srv1 = node('io', 'Ответ сервера:\nначало раунда', MAIN, -3.1, 5.4, 0.8)
inc = node('proc', 'НР := НР + 1', MAIN, -4.5, 5.4, 0.8)
d1 = node('dec', 'НР = 1 ?', MAIN, -5.9, 3.4, 1.15)
mxk = node('proc', 'МХ := К', A, -5.9, 2.4, 0.8)
io1 = node('io', 'Вывод МХ\n(ввод ХС — ответ сервера)', MAIN, -7.5, 5.4, 0.9)
rz = node('proc', 'РЗ := табл. 3 (МХ, ХС)', MAIN, -9.0, 5.4, 0.8)
dp = node('dec', 'РЗ = П ?', MAIN, -10.4, 3.4, 1.15)
sp = node('proc', 'СП := СП + 1', A, -10.4, 2.6, 0.8)
dn = node('dec', 'РЗ = Н ?', MAIN, -11.8, 3.4, 1.15)
sn = node('proc', 'СН := СН + 1', A, -11.8, 2.6, 0.8)
ist = node('proc', 'ИСТ := ИСТ ∪ {НР, ХС, МХ, РЗ}', MAIN, -13.4, 5.4, 0.9)
d5 = node('dec', 'НР = 5 ?', MAIN, -14.9, 3.4, 1.15)
out2 = node('io', 'Вывод СП, СН', A, -14.9, 2.6, 0.8)
end = node('term', 'КОНЕЦ', A, -16.3, 2.2, 0.8)
dsw = node('dec', 'СП + СН ≥ 2 ?', MAIN, -17.3, 4.4, 1.2)
cs1 = node('proc', 'С := 1', A, -17.3, 2.2, 0.8)
kx1 = node('proc', 'КХ := табл. 1 (по ХС)', MAIN, -19.1, 4.6, 0.8)
search = node('proc', 'Поиск паттерна в ИСТ\n(табл. 5) → СХС', A, -19.1, 2.9, 1.1)
dpatt = node('dec', 'Паттерн найден ?', A, -20.9, 3.0, 1.15)
kx2 = node('proc', 'КХ := табл. 2 (по СХС)', A, -22.6, 2.9, 0.8)
kx1b = node('proc', 'КХ := табл. 1 (по ХС)', B, -20.9, 2.6, 0.8)
mx = node('proc', 'МХ := КХ', MAIN, -23.6, 4.0, 0.8)

# ---------------------------------------------------------------- связи
edge(start, init)
edge(init, srv1)
edge(srv1, inc)
edge(inc, d1)
edge(d1, mxk, 'да', ex=(1, 0.5), en=(0, 0.5))
edge(d1, io1, 'нет')
edge(mxk, io1, '', ex=(0.5, 1), en=(1, 0.5), pts=[(A, -7.5)])
edge(io1, rz)
edge(rz, dp)
edge(dp, sp, 'да', ex=(1, 0.5), en=(0, 0.5))
edge(dp, dn, 'нет')
edge(dn, sn, 'да', ex=(1, 0.5), en=(0, 0.5))
edge(dn, ist, 'нет')
# слияние ветвей СП / СН
edge(sp, ist, '', ex=(1, 0.5), en=(1, 0.5),
     pts=[(6.6, -10.4), (6.6, -13.4)])
edge(sn, ist, '', ex=(1, 0.5), en=(1, 0.5), pts=[(6.6, -11.8), (6.6, -13.4)])
dot(6.6, -11.8)
edge(ist, d5)
edge(d5, out2, 'да', ex=(1, 0.5), en=(0, 0.5))
edge(out2, end)
edge(d5, dsw, 'нет')
edge(dsw, cs1, 'да', ex=(1, 0.5), en=(0, 0.5))
edge(dsw, kx1, 'нет')
edge(cs1, search)
edge(search, dpatt)
edge(dpatt, kx2, 'да')
edge(dpatt, kx1b, 'нет', ex=(1, 0.5), en=(0, 0.5))
edge(kx2, mx, '', ex=(0.5, 1), en=(1, 0.5), pts=[(A, -23.6)])
edge(kx1b, mx, '', ex=(0.5, 1), en=(1, 0.5),
     pts=[(B, -23.6), (A, -23.6)])
dot(A, -23.6)
edge(kx1, mx)
# возврат на начало раунда
edge(mx, inc, '', ex=(0, 0.5), en=(0, 0.5),
     pts=[(-4.6, -23.6), (-4.6, -4.5)])

# ---------------------------------------------------------------- легенда
legend = node('legend',
              'ОБОЗНАЧЕНИЯ\n'
              'МХ — мой ход\n'
              'ИСТ — история (табл. 4)\n'
              'НР — номер раунда\n'
              'ХС — ход соперника\n'
              'СХС — следующий ход соперника\n'
              'РЗ — результат раунда\n'
              'КХ — контрход\n'
              'СП — счётчик поражений\n'
              'СН — счётчик ничьих\n'
              'С — стратегия\n'
              '\n'
              'Н.У.:  НР := 0;  СП := 0;  СН := 0;\n'
              'С := 0;  ИСТ := ∅\n'
              '\n'
              'ТАБЛИЦЫ\n'
              '1 — контрход стратегии 1 (по ХС)\n'
              '2 — контрход стратегии 2 (по СХС)\n'
              '3 — определение результата\n'
              '4 — история\n'
              '5 — поиск паттерна',
              11.6, -6.2, 8.4, 7.6)

page = ('<diagram id="p1" name="Схема алгоритма (ГОСТ 19.701)">'
        '<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" '
        'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1654" '
        'pageHeight="1169" math="0" shadow="0"><root>'
        '<mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(cells) +
        '</root></mxGraphModel></diagram>')

xml = ('<mxfile host="app.diagrams.net" type="device" version="24.7.17">'
       + page + '</mxfile>')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(xml)
print('Сохранено:', OUT, len(xml), 'байт')
