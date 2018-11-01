provider "aws" {
  region     = "us-east-1"
}

terraform {
  backend "s3" {
    bucket 		   = "fyt-terraform"
    key    		   = "state"
    region 		   = "us-east-1"
    dynamodb_table = "terraform_lock"
  }
}

