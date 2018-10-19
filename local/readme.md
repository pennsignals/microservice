Configuration files go here.

Only this file and select configuration files should be checked into version control. See `**/local` excluded with select inclusions in `../.gitignore`.
Only configuration files used by travis for unit testing should be added to the docker container referenced from docker-compose files for unit testing. See `**/local` excluded with select inclusions in `.dockerignore`.

Nomad jobs should contain template stanzas for insecure configuration from consul.

    env {
      MICROSERVICE_CONFIGURATION="/local/microservice.cfg"
    }

    template {
      data = <<EOH
    {{key "microservice/integration/microservice.cfg"}}{{.Data.value}}{{end}}
    EOH
      destination = "/local/microservice.cfg"
    }

Whitespace within the EOH will mangle the data.
There should be no whitespace before or after the `{{...}}...{{end}}` clauses.
