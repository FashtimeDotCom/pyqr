@echo off
echo.
echo ���� po �ļ�
echo.
python pygettext.py -a -v -d locals -o messages.po ../*.py ../templates/*.html
echo.
echo po �ļ�������
echo.
pause