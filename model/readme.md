Model files go here.

Only this file should be checked into version control. See `**/model` excluded with this select inclusion in `../.gitignore`.
No files here should be added to the docker container. See `**/model` excluded without inclusions in `../.dockerignore`.

Nomad jobs should contain a config clause to mount a single asset directory from the fileshare:

    config {
      image = "quay.io/pennsignals/microservice:v1.0"
      command = "microservice"

      volumes = [
        "/share/models/microservice.v1.0/:/tmp/model:ro"
      ]
    }
