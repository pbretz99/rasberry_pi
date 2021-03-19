'''Email functions

Contains code for sending emails for 
various projects.
'''

# Libraries
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import Secure_Data # Code containing my personal information

# Send email with times, temperature, and wind speed for biking
def send_biking_email(intervals, temp, wind_speed):
  
  # Email Information
  port = 465  # For SSL
  smtp_server = "smtp.gmail.com"
  sender_email = Secure_Data.sender_email
  receiver_email = Secure_Data.receiver_email
  password = Secure_Data.password
  
  # The email message
  # Sentence detailing good times
  if len(intervals) == 1:
    interval_text = "A good time is " + intervals[0] + "."
  elif len(intervals) == 2:
    interval_text = "Some good times are " + intervals[0] + " and " + intervals[1] + "."
  else:
    interval_text = "Some good times are "
    for i in range(len(intervals)-1):
      interval_text += intervals[i] + ", "
    interval_text += " and " + intervals[-1] + "."
  # Full html message
  html = """\
  <html>
    <body>
      <p>Hi, Philip!<br><br>
         How is your day going? 
         You should know that today is an excellent day for biking.<br><br> """ + interval_text + """<br><br>
         The temperature is """ + str(temp) + """ degrees and the wind speed is """ + str(wind_speed) + """ mph.<br><br>
         Hit the road, if you can!
      </p>
    </body>
  </html>
  """
  
  # Convert message to MIME
  message = MIMEMultipart()
  message["Subject"] = "Go Biking!"
  message["From"] = sender_email
  message["To"] = receiver_email
  message.attach(MIMEText(html, "html"))
  
  # Send the email
  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())