resource "aws_lambda_function" "test_lambda" {
  filename         = "../lambda_functions/lambda_iot/lambda_function.py.zip"
  function_name    = "lambda_iot2"
  role             = "arn:aws:iam::041767885136:role/DL-Lambda-Role"
  handler          = "lambda_function.lambda_handler"
  source_code_hash = "${base64sha256(file("../lambda_functions/lambda_iot/lambda_function.py.zip"))}"
  runtime          = "python3.6"
}