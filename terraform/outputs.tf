output "ip" {
  description = "Public IP of the droplet"
  value       = digitalocean_droplet.server.ipv4_address
}
