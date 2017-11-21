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