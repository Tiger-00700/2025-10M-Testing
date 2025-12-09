terraform {
  required_version = ">= 1.0"
}

locals {
  environments = {
    dev  = { region = "us-east-1", size = "small" }
    test = { region = "us-east-1", size = "medium" }
  }
}

output "env_matrix" {
  value = local.environments
}
