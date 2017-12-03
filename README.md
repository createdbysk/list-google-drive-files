# list-google-drive-files
Determines if files are duplicated between various google accounts. The duplicates are based only on the name of the file and NOT the content.
Determines the amount of possible wasted quota bytes used due to the duplicates.

# Credentials
## One time setup
* Navigate to https://console.developers.google.com
* Login if necessary
* Choose the file-manager project
* Select the Credentials page
* Download Cloud File Manager Client JSON credentials file. Assume the download path is 
  ```/path/to/client_secret_816614257662-dacf8kk6pcve3jv0laitst90le1pmako.apps.googleusercontent.com.json```
* Follow instructions at https://cloud.google.com/iam/docs/creating-managing-service-account-keys to create a service 
  account key.
    * Choose the file-manager project
    * Choose the file-manager-application service account
    * Download the file in json format.
    * Assume the file is downloaded to ```/path/to/file-manager-1234.json```
* Move the downloaded files into the location expected by the application
    cd /path/that/contains/thisREADME.md/
    mkdir -p .credentials
    mv /path/to/client_secret_816614257662-dacf8kk6pcve3jv0laitst90le1pmako.apps.googleusercontent.com.json .credentials
    ln -s .credentials/client_secret_816614257662-dacf8kk6pcve3jv0laitst90le1pmako.apps.googleusercontent.com.json .credentials/client_secret.json
    mv /path/to/file-manager-1234.json .credentials
    ln -s .credentials/file-manager-1234.json .credentials/keyfile.json

# Local Development
## Bash on ubuntu on windows 10
* Setup bash on ubuntu on windows 10 to run graphical applications
    * https://seanthegeek.net/234/graphical-linux-applications-bash-ubuntu-windows/
## Pycharm
* Follow instructions at https://itsfoss.com/install-pycharm-ubuntu/
    * Install the community edition.
## Firefox
* Install Firefox
    sudo apt-get install firefox
## Run web server
### One time setup
Install the twisted daemon (twistd)
    sudo apt-get install python-twisted-core

### Start the server
    twistd web --wsgi web_app.app --port tcp:8081

### Access the web server
Navigate to http://localhost:8081

# Auth flows
Auth flows are based on the documentation linked below
## Login
* http://oauth2client.readthedocs.io/en/latest/_modules/oauth2client/contrib/flask_util.html
## Add accounts to manage files from
* https://developers.google.com/api-client-library/python/guide/aaa_oauth

# SSL
## Reference
The steps below are extracted from https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/

## Steps to create a CA and a self-signed certificate signed by that CA
### Create CA 
    openssl genrsa -des3 -out myCA.key 2048
    openssl req -x509 -new -nodes -key myCA.key -sha256 -days 1825 -out myCA.pem
    openssl x509 -outform der -in myCA.pem -out myCA.crt
    
Provide myCA.crt to all clients that want to connect to your server.
### Create certificate for localhost:8000
    openssl genrsa -out localhost.key 2048
    openssl req -new -key localhost.key -out localhost.csr

Create a localhost.ext with the following contents

    authorityKeyIdentifier=keyid,issuer
    basicConstraints=CA:FALSE
    keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
    subjectAltName = @alt_names

    [alt_names]
    DNS.1 = localhost
    DNS.2 = localhost:8000

Finally create the certificate

    openssl x509 -req -in localhost.csr -CA myCA.pem -CAkey myCA.key -CAcreateserial \
    -out localhost.crt -days 1825 -sha256 -extfile localhost.ext
    cat localhost.crt localhost.key > /path/to/your/webserver/root/server.pem

### Run your wsgi app with the certificate    
    PYTHONPATH=. twistd -n web --wsgi web_app.app  --port ssl:8000
    
### Alternative https mechanism to run app
This mechanism allowed the client to connect both on http and https.
    PYTHONPATH=. twistd -n  web --wsgi web_app.app  --https=8000 \    
    -c /path/to/localhost.crt -k /path/to/localhost.key    
