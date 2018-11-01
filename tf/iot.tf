resource "aws_iot_topic_rule" "RichsFaceDetection" {
  name = "RichsFaceDetection"
  description = "Face Detection Rule for Rich's DeepLens"
  enabled = true
  sql = "SELECT face, thing_name FROM '$aws/things/deeplens_DUkF8LPsR3OTIuCucy2vDQ/infer' WHERE confidence > 0.8"
  sql_version = "2016-03-23"

  lambda {
    function_arn = "${aws_lambda_function.lambda_iot.arn}"
  }
}

resource "aws_iot_topic_rule" "MichellesFaceDetection" {
  name = "MichellesFaceDetection"
  description = "Face Detection Rule for Michelle's DeepLens"
  enabled = true
  sql = "SELECT face, thing_name FROM '$aws/things/deeplens_7how6uNkTuGL0A4XA-dk8g/infer' WHERE confidence > 0.8"
  sql_version = "2016-03-23"

  lambda {
    function_arn = "${aws_lambda_function.lambda_iot.arn}"
  }
}