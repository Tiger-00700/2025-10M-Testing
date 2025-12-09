terraform {
  required_version = ">= 1.0"
}

provider "local" {}

# Minimal placeholder to demonstrate IaC wiring
resource "local_file" "env_readme" {
  content  = "env: minimal placeholder"
  filename = "./env_minimal_generated.txt"
}
