Build with docker:
`docker build --platform=linux/amd64 -t flask-ascii-app .`
Run with docker:
`docker run -d -p 5000:5000 --name flask-container flask-ascii-app`

Tag and push to docker repo:
docker tag flask-ascii-app diemydiesel/testing-repo:flask-ascii-app
docker push diemydiesel/testing-repo:flask-ascii-app         
