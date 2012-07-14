#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import StringIO
import string
import web
import qrcode
from mime import ImageMIME

import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

web.config.debug = False

urls = (
    '/', 'Index',
    '/qr', 'QR',
)

if 'SERVER_SOFTWARE' in os.environ:
    # SAE
    site = 'http://%s.sinaapp.com' % (os.environ.get('APP_NAME'))
else:
    # Local
    site = 'http://127.0.0.1:8080' # TODO ��ȡ�Զ���Ķ˿�

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'templates')
render = web.template.render(templates_root)
app = web.application(urls, globals())
web.template.Template.globals['site'] = site


class Index(object):
    def GET(self):
        return render.index()

class QR(object):
    """�����������ݲ���ʾ QR Code ��ά��ͼƬ
    """
    def handle_parameter(self, chl, chld, chs):
        """������ύ�ı���
        """
        if len(chl) > 2953: # �������
            chl = chl[:2952]
            # chl = ''
        chld = string.upper(chld) # ת��Ϊ��С��ĸ
        if chld == '':
            chld = 'M|4'
        chld = chld.split('|') # chld �ǷǱ������
        if len(chld) == 2:
            try:
                border = int(chld[1])
            except:
                # raise web.badrequest()
                version = 4
        elif len(chld) == 1:
            border = 4
        if chld[0] not in ['L', 'M', 'Q', 'H']:
            chld[0] = 'M'
        if border < 0:
            # raise web.badrequest()
            border = 4
        try:
            chs = string.lower(chs) # ת��ΪСд��ĸ
            size = tuple([int(i) for i in chs.split('x')])
        except:
            raise web.badrequest()
        else:
            if (size[0] * size[1] == 0 or size[0] < 0 or size[1] < 0 or ( # ��������������
                    # size[0] < 21) or size[1] < 21 or (
                    size[0] > 800) or size[1] > 800): # ����ͼƬ��С����ֹͼƬ̫����ϵͳ����
                raise web.badrequest()
        box_size = 10
        square_size = size[0] if size[0] <= size[1] else size[1]
        # L,M,Q,H �������� 1~40 �汾���������(Binary)
        l_max = [17, 32, 53, 78, 106, 134, 154, 192, 230, 271, 321,
                367, 425, 458, 520, 586, 644, 718, 792, 858, 929,
                1003, 1091, 1171, 1273, 1367, 1465, 1528, 1628,
                1732, 1840, 1952, 2068, 2188, 2303, 2431, 2563,
                2699, 2809, 2953]
        m_max = [14, 26, 42, 62, 84, 106, 122, 152, 180, 213, 251,
                287, 331, 362, 412, 450, 504, 560, 624, 666, 711,
                779, 857, 911, 997, 1059, 1125, 1190, 1264, 1370,
                1452, 1538, 1628, 1722, 1809, 1911, 1989, 2099,
                2213, 2331]
        q_max = [11, 20, 32, 46, 60, 74, 86, 108, 130, 151, 177,
                203, 241, 258, 292, 322, 364, 394, 442, 482, 509,
                565, 611, 661, 715, 751, 805, 868, 908, 982, 1030,
                1112, 1168, 1228, 1283, 1351, 1423, 1499, 1579, 1663]
        h_max = [7, 14, 24, 34, 44, 58, 64, 84, 98, 119, 137, 155,
                177, 194, 220, 250, 280, 310, 338, 382, 403, 439,
                461, 511, 535, 593, 625, 658, 698, 742, 790, 842,
                898, 958, 983, 1051, 1093, 1139, 1219, 1273]
        level = chld[0] # ������
        # ���ݾ������ַ���ѡ���汾��
        if level == 'L':
            for i in l_max:
                if len(chl) < i:
                    version = l_max.index(i) + 1
                    break
            error_correction = qrcode.constants.ERROR_CORRECT_L
        elif level == 'M':
            for i in m_max:
                if len(chl) < i:
                    version = m_max.index(i) + 1
                    break
            error_correction = qrcode.constants.ERROR_CORRECT_M
        elif level == 'Q':
            for i in q_max:
                if len(chl) < i:
                    version = q_max.index(i) + 1
                    break
            error_correction = qrcode.constants.ERROR_CORRECT_Q
        elif level == 'H':
            for i in h_max:
                if len(chl) < i:
                    version = h_max.index(i) + 1
                    break
            error_correction = qrcode.constants.ERROR_CORRECT_H
        # print len(chl)
        # print version
        # print size, border
        # ���� qrcode Դ�롢square_size �� version ������ box_size
        box_size = square_size/((version * 4 + 17) + border * 2)
        # print box_size
        args = {'version': version,
                'error_correction': error_correction,
                'box_size': box_size,
                'border': border,
                'content': chl,
                'size': size
                }
        return args

    def show_image(self, version, error_correction, box_size, border,
                    content, size):
        """����ͼƬ MIME �� ���ݣ�������ʾͼƬ
        """
        # Try to import PIL in either of the two ways it can be installed.
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            import Image, ImageDraw
        if box_size == 0:
            im = Image.new("1", (1, 1), "white")
        else:
            qr = qrcode.QRCode(
                version = version,
                error_correction = error_correction,
                box_size = box_size,
                border = border,
            )
            qr.add_data(content)
            qr.make(fit=True)
            im = qr.make_image()
        # im.show()
        img_name = StringIO.StringIO()
        im.save(img_name, 'png')
        img_data = img_name.getvalue()
        im = Image.open(StringIO.StringIO(img_data))
        # im.show()
        x, y = im.size
        # print im.size
        # print size
        rx, ry = size
        # TODO ����̫С����ʶ������ʾ�հף��ж�ͼƬ������
        new_im = Image.new("1", (rx, ry), "white")
        paste_size = ((rx-x)/2, (ry-y)/2, (rx-x)/2 + x, (ry-y)/2 + y)
        # print paste_size
        new_im.paste(im, paste_size)
        img_name.close()
        new_im_name = StringIO.StringIO()
        new_im.save(new_im_name, 'png')
        new_im_data = new_im_name.getvalue()
        MIME = ImageMIME().get_image_type(new_im_data)
        new_im_name.close()
        return (MIME, new_im_data)

    def GET(self):
        # TODO ��� IE ������µ�ַ���������ĳ��ֱ����������
        # TODO google ��ֱ�ӽ��ڵ�ַ������Ĳ����ض���Ϊ '' , ������ô����
        # query = web.ctx.query # ���� web.input() ���ַ������������ u'%B3%B5' ���²��ܲ²���� 
        query = web.ctx.env['QUERY_STRING'] # ����� IE ������µ�ַ���������ĳ��ֵı�������
        # print query
        if query == '':
            return web.badrequest()
        else:
            query = query.split('&')
            try:
                # query = dict([tuple(i) for i in ])
                values = [x.split('=') for x in query] # �ָ����
                query = {}
                for i in values:
                    if len(i) == 1 and i[0] == 'chld': # chld �ǷǱ������
                        query.setdefault(i[0], 'M|4')
                    elif len(i) == 2 and i[0] in ['chl', 'chs', 'chld']:
                        query.setdefault(i[0], i[1])
                # print query
            except:
                return web.badrequest()
            chl = query.get('chl', '') # TODO �����������Ĭ��ֱֵ���׳�400 error
            chl = chl.replace('+', '%20') # ����ո��Ӻţ��滻�ո�Ϊ '%20'
            chs = query.get('chs', '300x300')
            chld = query.get('chld', 'M|4')
        # print repr(chl)
        import urllib2
        chl = urllib2.unquote(chl)
        # print repr(chl)
        import charset
        chl = charset.encode(chl) # ���ַ�������Ȼ�� utf8 ����
        # print repr(chl)
        # TODO ������벻�� utf8������(quote())���ض��� UTF8 ����������
        args = self.handle_parameter(chl, chld, chs)
        MIME, data = self.show_image(args['version'],
                                    args['error_correction'],
                                    args['box_size'], args['border'],
                                    args['content'], args['size'])
        web.header('Content-Type', MIME)
        return data

    def POST(self):
        """���� POST ����
        """
        query = web.input(chl='', chld='M|4', chs='300x300')
        # ��Ϊ web.input() �ķ��ص��� unicode ��������ݣ�
        # ���Խ����ݰ� utf8 �����Ա��������ɶ�ά��
        chl = query.chl.encode('utf8')
        chs = query.chs
        chld = query.chld
        args = self.handle_parameter(chl, chld, chs)
        MIME, data = self.show_image(args['version'],
                                    args['error_correction'],
                                    args['box_size'], args['border'],
                                    args['content'], args['size'])
        MIME, data = self.show_image()
        web.header('Content-Type', MIME)
        return data

if __name__ == '__main__':
    app.run()

