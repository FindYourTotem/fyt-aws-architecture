resource "aws_lambda_function" "lambda_rekognition" {
  filename         = "../lambda_functions/lambda_rekognition.zip"
  function_name    = "lambda_rekognition"
  role             = "arn:aws:iam::041767885136:role/DL-Lambda-Role"
  handler          = "lambda_function.lambda_handler"
  source_code_hash = "${base64sha256(file("../lambda_functions/lambda_rekognition.zip"))}"
  runtime          = "python2.7"
  description      = "[Terraform] Lambda function for lambda rekognition"
}

resource "aws_lambda_permission" "s3_invoke_rekognition" {
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.lambda_rekognition.arn}"
    principal = "s3.amazonaws.com"
    source_arn = "arn:aws:s3:::deeplens-sagemaker-402c2722-4ba9-49c8-bc6d-1484ff6d9288"
}

resource "aws_s3_bucket_notification" "s3_invoke_rekognition" {
  bucket = "deeplens-sagemaker-402c2722-4ba9-49c8-bc6d-1484ff6d9288"
  lambda_function {
    lambda_function_arn = "${aws_lambda_function.lambda_rekognition.arn}"
    events              = ["s3:ObjectCreated:*"]
  }
}
