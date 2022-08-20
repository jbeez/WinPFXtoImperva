@echo off&setlocal enableextensions
set RANDFILE=%~dp0\.rnd
set /p KeyPass=Enter Key Password:
cls

mkdir sites 2> nul

if exist sites/%~n1.site_id goto exists

set /p sid=Enter Numerical SiteID for your domain:
echo %sid%>sites/%~n1.site_id
goto ssl

:exists
set /p sid=<sites/%~n1.site_id

:ssl
openssl pkcs12 -in %~nx1 -passin pass:"%KeyPass%" -passout pass:"%KeyPass%" -nocerts -out %~n1.key
openssl pkcs12 -in %~nx1 -passin pass:"%KeyPass%" -clcerts -nokeys -out tempcert.crt
openssl pkcs12 -in %~nx1 -passin pass:"%KeyPass%" -cacerts -nokeys -out tempcacert.crt

type tempcert.crt tempcacert.crt > %~n1.pem
cls
del tempcert.crt tempcacert.crt
echo.
echo Created %~n1.key and %~n1.pem
echo.
echo.
echo Invoking python script to upload %~n1.pem to Imperva
echo.
echo Press Enter to continue
echo.
pause
cls
echo site_id = {%sid%} > thiscert.py
echo pemfile = "%~n1.pem" >>thiscert.py
echo keyfile = "%~n1.key" >>thiscert.py
echo pw = "%KeyPass%" >>thiscert.py
python PFX_Upload_To_Imperva.py
del thiscert.py
echo Complete
pause
