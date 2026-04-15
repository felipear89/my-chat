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

data "digitalocean_ssh_key" "default" {
  name = var.ssh_key_name
}

resource "digitalocean_droplet" "server" {
  name      = "my-chat"
  region    = "nyc1"
  size      = "s-2vcpu-2gb"
  image     = "ubuntu-22-04-x64"
  ssh_keys  = [data.digitalocean_ssh_key.default.id]
  user_data = file("${path.module}/cloud-init.yml")
}

