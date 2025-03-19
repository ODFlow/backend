<div align="center">

<h3> Quickstart </h4>

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=ODFlow_backend&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=ODFlow_backend)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ODFlow/backend/docker-build.yml?color=%233e75b5)


</div>

### Using docker
1. Install [docker](https://www.docker.com/)
2. Find the latest [package](https://github.com/ODFlow/backend/pkgs/container/backend)
3. Login to the registry <br>
  `docker login ghcr.io`

4. Pull the image <br>
   `$ docker pull ghcr.io/odflow/backend:sha-f04d1f6`
   
6. Run the image <br>
   `$ docker run -p 8000:8000 ghcr.io/odflow/backend:[sha]`

<br>

### Cloning the repository

1. Clone the repo: <br>
` git clone https://github.com/ODFlow/backend.git `

2. Navigate to the backend: <br>
` cd backend `

3. Install dependencies: <br>
` pip install -r requirements.txt `

4. Run the app: <br>
` uvicorn main:app --reload `
