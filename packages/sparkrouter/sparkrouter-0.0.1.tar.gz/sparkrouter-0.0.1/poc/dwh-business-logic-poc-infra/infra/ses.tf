resource "aws_ses_email_identity" "jclark" {
  email = local.user_email
}
