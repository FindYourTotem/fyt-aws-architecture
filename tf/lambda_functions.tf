resource "aws_lambda_function" "lambda_iot" {
  filename         = "../lambda_functions/lambda_iot.zip"
  function_name    = "lambda_iot"
  role             = "arn:aws:iam::041767885136:role/DL-Lambda-Role"
  handler          = "lambda_function.lambda_handler"
  source_code_hash = "${base64sha256(file("../lambda_functions/lambda_iot.zip"))}"
  runtime          = "python3.6"
  description      = "[Terraform] Lambda function for lambda iot"
}

