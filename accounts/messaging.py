import boto3
from django.contrib.auth.models import User


class EmailService:
    """Service for sending emails using AWS SES"""

    def __init__(self):
        self.ses = boto3.client('ses')

    def send_invite_email(self, user: User):
        """Send an invite email to a user with a registration token"""
        if not user.email:
            raise ValueError(
                'User must have an email address to send an invite')
        if not user.profile.registration_token:
            raise ValueError(
                'User must have a registration token to send an invite')
        self.verify_email(user.email)

        try:
            res = self.ses.send_email(
                Source="capitalize.learning@gmail.com",
                Destination={'ToAddresses': [user.email]},
                Message={
                    "Subject": {
                        "Data": "You're invited to join our platform",
                        "Charset": "UTF-8"
                    },
                    "Body": {
                        "Text": {
                            "Data":
                            f"Hi {user.first_name},\n\nYou're invited to join our platform. Please click the link below to complete your registration:\n\nhttps://capitalizelearn.com/auth/register/?token={user.profile.registration_token}\n\nThanks,\n\nThe Capitalize Team",
                            "Charset": "UTF-8"
                        },
                    }
                },
                ReplyToAddresses=["no-reply@capitalizelearning.com"])
            print(res)
            return res
        except Exception as e:
            print(e)
            raise e 

    def verify_email(self, email: str):
        """Adds an email address to the list of verified email addresses"""
        res = self.ses.verify_email_identity(EmailAddress=email)
        print(res)
        return res
