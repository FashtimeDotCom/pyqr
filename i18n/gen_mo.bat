@echo off
echo.
echo ���� mo �ļ�
echo.
python msgfmt.py -o en_US/LC_MESSAGES/messages.mo en_US/LC_MESSAGES/messages.po
python msgfmt.py -o zh_CN/LC_MESSAGES/messages.mo zh_CN/LC_MESSAGES/messages.po
echo mo �ļ�������
echo.
pause