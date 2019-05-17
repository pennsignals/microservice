job "project_staging_ping" {
  datacenters = ["dc1"]

  type = "batch"

  periodic {
    cron             = "* * * * *"
    prohibit_overlap = true
    time_zone        = "America/New_York"
  }

  group "default" {
    vault {
      policies = ["project_staging"]
    }

    restart {
      attempts = 90
      delay    = "5s"
      interval = "24h"
      mode     = "fail"
    }

    task "project" {
      image = "quay.io/pennsignals/project:1.0"
      command = "project"
      driver = "docker"
      env {
        CONFIGURATION="/local/configuration.yml"
      }
      resources {
        cpu    = 2048  # more if needed
        memory = 1024  # more if needed
      }
      template {
        data = <<EOH
{{key "project_staging/configuration.yml"}}
EOH
        destination = "/local/configuration.yml"
      }
      template {
        data = <<EOH
INPUT_URI="{{with secret "secret/mssql/project_staging/input_uri"}}{{.Data.value}}{{end}}"
OUTPUT_URI="{{with secret "secret/mongo/project_staging/output_uri"}}{{.Data.value}}{{end}}"
EOH
        destination = "/secrets/.env"
        env         = true
      }
    }
  }
}
