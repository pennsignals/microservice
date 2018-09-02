# Security: Development through production with Docker containers

## 1 High level plan for infrastructure and software engineering

### 1.1 Infrastructure
- Run durable production and staging environments for deployment and A/B tests of microservices
- Run durable integration environment for scalability, load, system infrastructure tests, and infrastructure evolution
- Run ephemeral test environments for production-like microservice systems tests
- Automate infrastructure as code, eliminate configuration drift, rebuild vs patch

### 1.2 Software engineering
- Automate all build, unit tests, systems tests, and **deployment** to a production-like test environment from code commit
- Easy local development environments with few dependencies
- High fidelity between local development environment and production-like test environments

## 2 Docker
### 2.1 Definitions
#### 2.1.1 Docker Image
- A unit of standardized, packaged software for development and deployment
- Similar to a virtual machine image
- Has layers similar to virtual machines images with base images
- Runnable as a Docker container
- Built from a <a id="good-dockerfile">Dockerfile</a> that specifies included software packages

```Dockerfile
#    Start with one of our base images...
FROM quay.io/pennsignals/alpine-3.7-python-3.6-engineering  
MAINTAINER pennsignals
WORKDIR /tmp
#    Copy our microservice code into our new image
COPY microservice ./microservice           
COPY requirements.txt .
COPY setup.py .
#    Install/compiles the microservice inside our new image
RUN pip install --requirement requirements.txt
```

- Examples in docker image repositories:
  - Sandboxes as a vm alternative for exploration: [hortonworks data platform](https://hub.docker.com/r/hortonworks/sandbox-hdp/tags/) at 20 GB
  - Isolated, disposable databases for development: [postgres](https://hub.docker.com/r/_/postgres/) at 25-83 MB, [mongo](https://hub.docker.com/r/_/mongo/) at 137 MB
  - Other services for development: [node](https://hub.docker.com/r/library/node/tags/) at 25-334 MB
  - Base image for microservices: [pennsignals](https://quay.io/repository/pennsignals/alpine-3.7-python-3.6-engineering?tab=tags) at 23 MB

#### 2.1.2 Docker Container
- Similar to a virtual machine with lower isolation and lower resource requirements
- Adds a final layer to a docker image that holds runtime
- Suspendible, restartable, disposable


### 2.2 Docker Security

#### 2.2.1 Embedded secrets inside docker images
- Not all files in our workspace should be copied into our image
 - secrets files and directories
 - temporary files used for build

```Dockerfile
# DO NOT USE, MAY COPY SECRETS INTO IMAGE
FROM quay.io/pennsignals/alpine-3.7-python-3.6-engineering  
MAINTAINER pennsignals
WORKDIR /tmp
COPY . .  # <-- HERE
RUN pip install --requirement requirements.txt
```
#### 2.2.2 Mitigations
- Use directory convention for `./secrets` with `.env` files and env variables
- Use judicious `COPY` in `Dockerfile` as shown in good <a href="#good-dockerfile">Dockerfile</a>
- Use `.dockerignore` to block files/directories from `COPY`

```
.cache
.coverage
.dockerignore
.egg
.git
.gitignore
.tox

**/alloc
**/build
**/dist
**/htmlcov
**/local
**/nomad
**/secrets
**/__pycache__
**/*.egg-info
**/*.egg
**/*.db
**/*.pyc
**/*.pyo
**/*.swp

!local/.pylintrc
!local/microservice.test.cfg
!local/microservice.system.test.cfg
```
- Do not build and push images from localhost to docker image repository!
  - Use image repository to check out code from version control to build images automatically
  - Applies check in, `.gitignore	` as well as `.dockerignore`

#### 2.2.3 Docker image vulnerabilities
- Number of vulnerabilities increases over time
- Attack surface increases with the number of additional packages

#### 2.2.4 Mitigations
- Review images and software packages used: [pennsignals](https://quay.io/repository/pennsignals/alpine-3.7-python-3.6-engineering/manifest/sha256:1390e7dd352ffc7e67be95185169c09d6604fde5aa472453749f5ead27689ecc?tab=layers)
- Monitor the automated docker image repository scans:
  - [pennsignals](https://quay.io/repository/pennsignals/alpine-3.7-python-3.6-engineering/manifest/sha256:1390e7dd352ffc7e67be95185169c09d6604fde5aa472453749f5ead27689ecc?tab=packages) at 23 MB
  - [node on debian](https://hub.docker.com/r/library/node/tags/10-stretch/) at 344 MB
  - [node on alpine](https://hub.docker.com/r/library/node/tags/10-alpine/) at 25 MB
  - [postgres on debian](https://hub.docker.com/r/library/postgres/tags/10.5/) at 83 MB
  - [postgres on alpine](https://hub.docker.com/r/library/postgres/tags/10.5-alpine/) at 29 MB
- Do not use typical windows or linux desktop or server operating systems as base images
  - Use minimal network appliance/security-focused base images
  - Alpine based images are not only smaller, but have a more secure implementation of `libc`
- Rebuild/redeploy images instead of patching
- Do not use containerized virtual machines in production
  - Build small-sized images that have few included packages and we may rebuild ourselves

### 2.1.3 Microservice
- Not a virtual machine nor a containerized virtual machine
- Not a monolithic application
- A micro component of a potentially distributed and scaled application
- Usually a web service or a web application
- Usually implemented as a very small docker container
- Usually does not hold durable state
- Usually scaled by running multiple docker containers from the same docker image

### Docker Compose
- A utility to run orchestrated docker containers
- Runs docker compose jobs in a virtual private network on localhost
- Usually orchestrates containerized microservices
- Usually also orchestrates containerized virtual machines for missing infrastructure or as an isolated substitutes for shared infrastructure
- Maps service volumes, ports and other resources from containers to/from locahost

```yaml
version: "3.2"
services:

  mongo:  # a disposable database for tests
    image: mongo
    stop_signal: SIGINT
    command: --noauth
    ports:
    - "27017:27017"  # allow mongo connections from localhost
    restart: always

  microservice:
    build: .
    entrypoint: ["microservice"]
    environment:
    - MONGO_URI=mongodb://mongo/tests  # "..//mongo/... see above

```

### Development and Unit Test Environments
- Local or unit test service running docker-compose
- Usually runs a containerized database for output and microservice state

### Production, Staging, Integration, and System Test Environments
- Cluster of 3 consul servers for highly available, distributed, shared state
- Cluster of 2 vault servers for reading and writing encrypted secrets to consul as well as applying security policy
- Cluster of 3 nomad servers to orchestrate docker containers as non-containerized microservices, and services
- Cluster of N nomad workers to run the docker containers, microservices, and services
- A private network to hide all cluster and intra-cluster communications
- A load balancer to expose web apps and web services to our intranet
- A shared on-premise database for persistence
- Run nomad jobs instead of docker-compose jobs, usually docker containers with microservices

![Environment](./environment.svg)


|   | Dev &amp; Unit Test | Production, Staging, Integration &amp; System Test |
|---|---|---|
| Infrastructure | Local &amp; travis-ci.com | distributed highly available cluster |
| Orchestration | docker-compose | nomad jobs |




# Docker-compose secret security:
- Use env_file clause in job: `docker-compose.yml`
```yaml
version: '2'
services:

  microservice:
    build: .
    restart: always
    env_file:             # Secrets are not in the Dockerfile
    - ./secrets/microservice.env
    ports:
    - "9999:9999" .       # map local port 9999 from port 9999 in container
    volumes:
    - ./local:/tmp/local  # map local directories into container
    - ./model:/tmp/model  # these directories are not part of the docker image
    working_dir: "/tmp"
    entrypoint: ["microservice"]
```
- Do not check `./secrets` into version control: exclude by adding `**/secrets` to `.gitignore`
- Do not accidentally add `./secrets` to the docker image: exclude by adding `**/secrets` to `.dockeringore`



## Automate docker image builds:
- Manually pushing images from localhost is problematic: `docker push quay.io.pennsignals/microservice:v2.0`
  - What version of the code is embedded in this image?
    - Not necessarily v2.0 from version control, the image was tagged `v2.0` locally
  - What files were included in the image?
    - Perhaps local files, not just those in version control
    - Perhaps local files with secrets
- Use a build trigger from version control: [pennsignals](https://quay.io/repository/pennsignals/alpine-3.7-python-3.6-engineering?tab=builds)
  - Known versions of `Dockerfile`, `.gitignore` and `.dockerignore` are applied
  - Version control tags match docker image tags

## Conclusions:
- Sign checked-in code
- Rebuild and redeploy containers instead of patching
- Automate docker image builds directly from version control
- Choose docker base images with small attack surface
- Choose to deploy microservices that install only the software that is needed to run (no development or build tools)
- Choose docker base images for network appliances like alpine instead of desktop or server operating system images like debian or windows
- Choose a base image with security-focused libraries like alpine's `muslc` instead of `glibc`
  - Caveats for vendor driver compatibility: oracle
- Actively monitor docker images for emerging vulnerabilities
- Apply vault policies for each job to control access to secrets
- Travis for unit tests?
  
## References:
- Kelsey Hightower on 12 factor apps: https://medium.com/@kelseyhightower/12-fractured-apps-1080c73d481c
- Twelve factor apps: https://12factor.net/

