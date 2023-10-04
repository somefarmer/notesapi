from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data["email_subject"], body=data["email_body"], from_email=data["sender"], to=[data["recipient"]])
        email.send()

    def email_subject(type=0):
        if type == 0:
            return f"Verify your email" 
        return f"Reset your password"
    
    def email_body(site_name, recipient=None, confirmation_link=None, type="activate_account"):
        if type == "activate_account":
            return f"""
            Hi {recipient},

            You are receiving this email inorder to complete registration of your account on {site_name}.
            Please click the following link to confirm activate your new account 
            {confirmation_link}

            Regards,

            {site_name.capitalize()} Team
            """
        
        return f"""
            Hi {recipient},

            You are receiving this email because you requested to reset your {site_name} password.
            Please click the following link to reset your account password
            {confirmation_link}

            Regards,

            {site_name.capitalize()} Team
            """
    
