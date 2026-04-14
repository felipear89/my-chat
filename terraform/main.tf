terraform {
  cloud {
    organization = "felipear89"
    workspaces {
      name = "my-chat"
    }
  }

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "server" {
  name      = "my-chat"
  region    = "nyc1"
  size      = "s-1vcpu-1gb"
  image     = "ubuntu-22-04-x64"
  user_data = file("${path.module}/cloud-init.yml")
}
