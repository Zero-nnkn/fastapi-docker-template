<p align="center">
  <a href="https://fastapi.tiangolo.com"><img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI"></a>
</p>

<p align="center">
My template for building API with FastAPI. Use MongoDB to save data and deploy with Docker
</p>


# Quickstart
We build segmentation API with Mask-RCNN
## Run
```
docker-compose up -d
```
The above command will both create the images and start the containers (one for **FastAPI** and one for the **MongoDB**).

Testing the API, open up your browser and enter: http://127.0.0.1/docs

**View mongoDB**
```
docker exec -it <CONTAINER_ID> bash

mongo

show dbs
```

<!-- ## 2. Request
Please use Postman to import this collection and test: [request](https://www.postman.com/collections/10094bbbf0ce3cf2102a) -->


## Stop
Stop and remove containers, networks and remove images used by services
```
docker-compose down --rmi
```

Remove
```
docker rm -f < Container_ID>

docker rmi -f <Image_name>
```

# File structure
```
.
├── api
│   ├── Dockerfile
│   ├── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   ├── db
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   └── src
│       ├── __init__.py
│       ├── appServer.py
│       ├── modelServer.py
│       ├── utils.py
│       ├── imageHandler
│       ├── maskRCNN
│       └── static/images 
├── imagedb
├── docker-compose.yml
└── README.md
```

