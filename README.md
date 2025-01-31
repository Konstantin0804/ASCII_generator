Converts an image into ASCII symbols with a minimalistic interface

Build with docker:
```bash
$ docker build --platform=linux/amd64 -t flask-ascii-app .
```

```bash
Run with docker:
$ docker run -d -p 5000:5000 --name flask-container flask-ascii-app
```
Navigate to http://127.0.0.1:5000

Tag and push to docker repo:
```bash
$ docker tag flask-ascii-app diemydiesel/testing-repo:flask-ascii-app
```

```bash
$ docker push diemydiesel/testing-repo:flask-ascii-app         
```