variable "do_token" {
  description = "DigitalOcean API token"
  sensitive   = true
}

variable "ssh_key_name" {
  description = "Name of the SSH key already registered in DigitalOcean"
}
