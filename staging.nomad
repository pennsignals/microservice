job "project_staging" {
  datacenters = ["dc1"]

  group "default" {
    vault {
      policies = ["project_staging"]
    }

    restart {
      mode = "delay"
    }

    task "project_staging" {
      image = "quay.io/pennsignals/project:v1.0"
      command = "project"
      driver = "docker"
      env {
        CONFIGURATION="/local/.cfg"
      }
      resources {
        cpu    = 13776  # greater than half a node so it runs alone
        memory = 4096  # more if needed
      }
      template {
        data = <<EOH
{{key "project_staging/configuration.cfg"}}
EOH
        destination = "/local/.cfg"
      }
      template {
        data = <<EOH
INPUT_DSN="{{with secret "secret/mssql/project_staging/input_dsn"}}{{.Data.data}}{{end}}"
OUTPUT_URI="{{with secret "secret/mongo/project_staging/output_uri"}}{{.Data.data}}{{end}}"
EOH
        destination = "/secrets/.env"
        env         = true
      }
    }
  }
}
