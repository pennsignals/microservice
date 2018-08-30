Only `microservice.test.cfg`, and `microservice.system.test.cfg` are available to docker-compose. This contents of this directory are not available to nomad. See `../.dockerignore` and the nomad jobs.

Nomad jobs should contain template stanzas for insecure configuration from consul.

    template {
      data = <<EOH
    {{key "microservice/integration/microservice.cfg"}}{{.Data.value}}{{end}}
    EOH
      destination = "/local/microservice.cfg"
    }

Whitespace within the EOH will mangle the data.
There should be no whitespace before or after the `{{...}}...{{end}}` clauses.
