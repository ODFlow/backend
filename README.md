<div align="center">

<h3> Quickstart </h3>

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=ODFlow_backend&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=ODFlow_backend)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ODFlow/backend/docker-build.yml?color=%233e75b5)


</div>

### Using docker
1. Install [docker](https://www.docker.com/)
2. Find the latest [package](https://github.com/ODFlow/backend/pkgs/container/backend)
3. Login to the registry <br>
  `docker login ghcr.io`

4. Pull the image <br>
Command can be found here: [click](https://github.com/ODFlow/backend/pkgs/container/backend)<br>
   `$ docker pull ghcr.io/odflow/backend:sha-[...]`
5. Download docker compose [file](docker-compose.yml)
6. Run the image <br>
   `cd backend` =>
   `docker-compose up`

<br>

### Cloning the repository

1. Clone the repo: <br>
` git clone https://github.com/ODFlow/backend.git `

2. Navigate to the backend: <br>
` cd backend `

3. Install dependencies: <br>
` pip install -r requirements.txt `

4. Run the redis server (port 6379): <br>
` redis-server `

5. Run the app: <br>
` uvicorn main:app --reload `
