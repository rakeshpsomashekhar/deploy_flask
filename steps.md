### to Dockerize
- install docker in linux server
- eg, yum install docker -y
- to start: systemctl start docker
- execute below givern commands

### to Create Docker images
```bash
docker build -t flask_project .
```

### to Create Docker container
```bash
docker run -it -d -p 5000:5000 flask_project
```
