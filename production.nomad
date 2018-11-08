job "project" {
  datacenters = ["dc1"]

  group "default" {
    vault {
      policies = ["project"]
    }

    restart {
      mode = "delay"
    }

    task "microservice" {
      image = "quay.io/pennsignals/project:v1.0"
      command = "project"
      driver = "docker"
      env {
        CONFIGURATION="/local/configuration.cfg"
      }
      resources {
        cpu    = 13776  # greater than half a node so it runs alone
        memory = 4096
      }
      template {
        data = <<EOH
{{key "project/configuration.cfg"}}
EOH
        destination = "/local/configuration.cfg"
      }
      template {
        data = <<EOH
INPUT_DSN="{{with secret "secret/mssql/project/clarity"}}{{.Data.data}}{{end}}"
OUTPUT_URI="{{with secret "secret/mongo/project/predict"}}{{.Data.data}}{{end}}"
EOH
        destination = "/secrets/secrets.env"
        env         = true
      }
    }
  }
}
