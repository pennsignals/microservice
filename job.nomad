job "microservice" {
  datacenters = ["dc1"]

  group "microservice" {
    vault {
      policies = ["microservice"]
    }

    restart {
      mode = "delay"
    }

    task "stream_a" {
      driver = "docker"
      config = {
        labels = "stream_a"
      }
      env {
        ZMQ = "tcp://0.0.0.0:${NOMAD_PORT}_events" data"
      }
      port_map = {
        events = 9001
      }
      resources {
        network {
          port "events" {}
        }
        memory = 128
      }
      template {
        data = <<EOH
MONGO_URI="{{with secret "secret/mongo/microservice/writable_a_uri"}}{{.Data.value}}{{end}}"
EOH
        destination = "/secrets/stream_a.env"
        env         = true
      }
    }

    task "stream_b" {
      driver = "docker"
      config = {
        labels = "stream_b"
      }
      env {
        ZMQ = "tcp://0.0.0.0:${NOMAD_PORT}_events" data"
      }
      image = "pennsignals/microservice"
      port_map = {
        events = 9002
      }
      resources {
        network {
          port "events" {}
        }
        memory = 128
      }
      template {
        data = <<EOH
MONGO_URI="{{with secret "secret/mongo/microservice/writable_b_uri"}}{{.Data.value}}{{end}}"
EOH
        destination = "/secrets/microservice_stream_b.env"
        env         = true
      }
    }

    task "microservice" {
      driver = "docker"
      config = {
        labels = "microservice"
      }
      env {
        A_ZMQ  = "tcp://${NOMAD_ADDR_stream_a_events} data"
        B_ZMQ  = "tcp://${NOMAD_ADDR_stream_b_events} data"
        C_ZMQ = "tcp://0.0.0.0:${NOMAD_PORT}_c_events" data"
        D_ZMQ = "tcp://0.0.0.0:${MONAD_PORT}_d_events" data""
      }
      image = "pennsignals/microservice"
      port_map = {
        c_events = 9003
        d_events = 9004
      }
      resources {
        network {
          port "c_events"{}
          port "d_events"{}
        }
        cpu    = 13776
        memory = 4096
      }
      service {
        name = "microservice-check"
        port = "c_events"

        check {
          name     = "microservice-check"
          type     = "tcp"
          interval = "60s"
          timeout  = "60s"
        }
      }
      template {
        data = <<EOH
A_URI="{{with secret "secret/mongo/microservice/a_uri"}}{{.Data.value}}{{end}}"
B_URI="{{with secret "secret/mongo/microservice/b_uri"}}{{.Data.value}}{{end}}"
C_URI="{{with secret "secret/mongo/microservice/c_uri"}}{{.Data.value}}{{end}}"
D_URI="{{with secret "secret/mongo/microservice/d_uri"}}{{.Data.value}}{{end}}"
EOH
        destination = "/secrets/microservice.env"
        env         = true
      }
    }
  }
}
