# lambda-file-generator
Serverless function for a file generation on CloudStorage

#### Deployment command:
``` 
gcloud functions deploy serverless-generator --entry-point handle --runtime python37 --trigger-http
```

#### POST request's params
- bucket
- filename
- size

JMeter project to request a file generation on Cloud Storage
```
generation_load.jmx
```
