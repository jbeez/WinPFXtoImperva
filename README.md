Requirements:

1) Windows python installed, openssl installed, the batch file, python scripts, and certificate in the same directory.
2) Your API creds and ID in the apikey.py file.
3) Password for certificate.
4) Numerical siteid from the imperva portal for the domain you're trying to update the certificate on.
5) Certificate file, which you just drag and drop onto the batch file to start the process.

A successful result will show a timestamp string with the certificate expiry along with error check results.

To-Do: Write fully in python, but I think the python environment on our enterprise windows laptops is very limited and lacking openssl features.
