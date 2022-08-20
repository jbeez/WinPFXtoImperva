@echo off
set RANDFILE=%~dp0\.rnd
set /p KeyPass=Enter Key Password:
cls
set /p sid=Enter Numerical SiteID for your domain:

openssl pkcs12 -in %~nx1 -passin pass:"%KeyPass%" -passout pass:"%KeyPass%" -nocerts -out %~n1.key
openssl pkcs12 -in %~nx1 -passin pass:"%KeyPass%" -clcerts -nokeys -out tempcert.crt
openssl pkcs12 -in %~nx1 -passin pass:"%KeyPass%" -cacerts -nokeys -out tempcacert.crt

type tempcert.crt tempcacert.crt > %~n1.pem
cls
del tempcert.crt tempcacert.crt
echo.
echo Created %~n1.key and %~n1.pem from %~nx1
echo.
pause
cls
echo.
echo Invoking python script to upload new certs to Imperva
echo.
echo Press Enter to continue
echo.
cls
echo site_id = {%sid%} > thiscert.py
echo pemfile = "%~n1.pem" >>thiscert.py
echo keyfile = "%~n1.key" >>thiscert.py
echo pw = "%KeyPass%" >>thiscert.py
python win_PFXtoImperva.py
pause
del thiscert.py