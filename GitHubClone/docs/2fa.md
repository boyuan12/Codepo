# 2-Factor Authentication
This site offer 2-Factor Authentication (2FA) for security using SMS message. To verify your phone number for 2FA, go to `/auth/2fa/`, then you should see where you can select country code, and type phone number there.
![](https://res.cloudinary.com/boyuan12/image/upload/v1604297848/Screen_Shot_2020-11-01_at_10.17.23_PM_axw7ae.png)

Then you should see "success" display on your screen. You should receive a message within 15 seconds or so (within US). The phone number it sents from +1 (916) 280-0623. You should receive a message like following:
![](https://res.cloudinary.com/boyuan12/image/upload/v1604298416/Screen_Shot_2020-11-01_at_10.26.50_PM_aulz7b.png)

Once you receive the message above, you can go to `/auth/2fa/verify/`, which you can type your code there and complete 2FA.
![](https://res.cloudinary.com/boyuan12/image/upload/v1604298531/Screen_Shot_2020-11-01_at_10.28.47_PM_a9bcub.png)

To check whether you verified your phone number, you can go to your settings (`/profile/`), and scroll down, you should see "Two-Factor Authentication". If authenticated correctly, you should see 
"Verified: Your phone number is ..."

Note that if you didn't receive your message, you can retry within 3 minutes:
![](https://res.cloudinary.com/boyuan12/image/upload/v1604298906/Screen_Recording_2020-11-01_at_10.29.57_PM_fw1ais.gif)