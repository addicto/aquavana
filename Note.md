# Use Google Cloud run for deployment

*** https://cloud.google.com/python/django/run ****

#### Authenticate and acquire credentials for the API:
> gcloud auth application-default login :: atthachet@mbc.co.th



## How to run

#### Start the Cloud SQL Auth proxy (using new terminal):
> ./cloud_sql_proxy -instances="dev-server-330909:us-central1:prod-db-primary"=tcp:5432 

#### Set up Cloud SQL connection (using new terminal):
###### MacOS
> export GOOGLE_CLOUD_PROJECT=dev-server-330909

> export USE_CLOUD_SQL_AUTH_PROXY=true

###### Window
> set GOOGLE_CLOUD_PROJECT=dev-server-330909

> set USE_CLOUD_SQL_AUTH_PROXY=true


> python manage.py runserver

#### Run the Django migrations to set up your models and assets:
> python manage.py makemigrations

> python manage.py makemigrations polls

> python manage.py migrate

> python manage.py collectstatic



## Creating Google Cloud - Django

Create the PostgreSQL instance:
> gcloud sql instances create prod-db-primary \
    --project dev-server-330909 \
    --database-version POSTGRES_13 \
    --tier db-f1-micro \
    --region us-central1 
>>  instance-name: prod-db-primary \
    region: us-central1 \
    project-id: dev-server-330909

Create the database within the recently created instance:
> gcloud sql databases create aquavana \
    --instance prod-db-primary
>>  sql-database-name: aquavana 

Create the user within the recently created instance:
> gcloud sql users create atthachet \
    --instance prod-db-primary \
    --password ArM1234
>>  instance-name: prod-db-primary \
    username: atthachet \
    password: ArM1234 


Create a Cloud Storage bucket:
> gsutil mb -l us-central1 gs://dev-server-330909_aquavana-bucket
>> storage-media-bucket: aquavana-bucket 


Create a file called .env, defining the database connection string, the media bucket name, and a new SECRET_KEY value:
> echo DATABASE_URL=postgres://atthachet:ArM1234@//cloudsql/dev-server-330909:us-central1:prod-db-primary/aquavana > .env

> echo GS_BUCKET_NAME=dev-server-330909_aquavana-bucket >> .env

> echo SECRET_KEY=$(cat /dev/urandom | LC_ALL=C tr -dc '[:alpha:]'| fold -w 50 | head -n1) >> .env

Store the secret in Secret Manager:
> gcloud secrets create aquavana_settings --data-file .env

To confirm the creation of the secret, check it:
> gcloud secrets describe aquavana_settings
>>  createTime: '2023-04-24T08:11:27.451881Z' \
    etag: '"15fa108db56ee9"' \
    name: projects/951025859598/secrets/aquavana_settings \
    replication:
      automatic: {} 

> gcloud secrets versions access latest --secret aquavana_settings
>>  DATABASE_URL=postgres://atthachet:ArM1234@//cloudsql/dev-server-330909:us-central1:prod-db-primary/aquavana-db \
    GS_BUCKET_NAME=dev-server-330909_aquavana-bucket \
    SECRET_KEY=SBfWLkCVDAIxCqsGTXxtisfdeVYcivFLzIrLgOcWdSeIbPsOKU


Get the value of the Project Number (PROJECTNUM): 
> export PROJECTNUM=$(gcloud projects describe dev-server-330909 --format='value(projectNumber)')
> gcloud projects describe 951025859598 --format='value(projectNumber)'
>>  PROJECTNUM: 951025859598

Delete the local file to prevent local setting overrides:
> rm .env

Grant access to the secret to the Cloud Run service account:
> gcloud secrets add-iam-policy-binding aquavana_settings \
    --member serviceAccount:951025859598-compute@developer.gserviceaccount.com \
    --role roles/secretmanager.secretAccessor

Grant access to the secret to the Cloud Build service account:
> gcloud secrets add-iam-policy-binding aquavana_settings \
    --member serviceAccount:951025859598@cloudbuild.gserviceaccount.com \
    --role roles/secretmanager.secretAccessor


Create a new secret, superuser_password, from a randomly generated password:
> echo -n "$(cat /dev/urandom | LC_ALL=C tr -dc '[:alpha:]'| fold -w 30 | head -n1)" | gcloud secrets create superuser_password --data-file -

Grant access to the secret to Cloud Build:
> gcloud secrets add-iam-policy-binding superuser_password --member serviceAccount:951025859598@cloudbuild.gserviceaccount.com --role roles/secretmanager.secretAccessor


Grant permission for Cloud Build to access Cloud SQL:
> gcloud projects add-iam-policy-binding dev-server-330909 --member serviceAccount:951025859598@cloudbuild.gserviceaccount.com --role roles/cloudsql.client


Use the gsutil cors command to configure CORS on the bucket
> gsutil cors set django-cors.json gs://dev-server-330909_aquavana-bucket

View CORS settings
> gsutil cors get gs://dev-server-330909_aquavana-bucket


### Running Django - Local

*** Start the Cloud SQL Auth proxy:
> ./cloud_sql_proxy -instances="dev-server-330909:us-central1:prod-db-primary"=tcp:5432

Set the Project ID locally (used by the Secret Manager API):
> export GOOGLE_CLOUD_PROJECT=dev-server-330909

Set an environment variable to indicate you are using Cloud SQL Auth proxy (this value is recognised in the code):
> export USE_CLOUD_SQL_AUTH_PROXY=true

Run the Django migrations to set up your models and assets:
> python manage.py makemigrations

> python manage.py makemigrations polls

> python manage.py migrate

> python manage.py collectstatic

Start the Django web server:
> python manage.py runserver



### 1st Time - Deploy the app to Cloud Run 

Using the supplied cloudmigrate.yaml, use Cloud Build to build the image, run the database migrations, and populate the static assets:
> gcloud builds submit --config cloudmigrate.yaml \
    --substitutions _INSTANCE_NAME=prod-db-primary,_REGION=us-central1

When the build is successful, deploy the Cloud Run service for the first time, setting the service region, base image, and connected Cloud SQL instance:
> gcloud run deploy aquavana-service     --platform managed     --region us-central1     --image gcr.io/dev-server-330909/aquavana-service     --add-cloudsql-instances dev-server-330909:us-central1:prod-db-primary     --allow-unauthenticated


### Updating - Deploy the app to Cloud Run

Updating the application:
> gcloud builds submit --config cloudmigrate.yaml --substitutions _INSTANCE_NAME=prod-db-primary,_REGION=us-central1

Deploy the service, specifying only the region and image:
> gcloud run deploy aquavana-service --platform managed --region us-central1 --image gcr.io/dev-server-330909/aquavana-service



### Configuring for production 
[More config go to :: https://cloud.google.com/python/django/run](https://cloud.google.com/python/django/run)


Start a connection to the SQL instance:
> gcloud sql connect prod-db-primary --user postgres