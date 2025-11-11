# list-of-higher-ranked-osu-players
Will generate a list of players higher ranked than the player specificed into a .csv file (player must be in the top 10,000 for performance points(pp))


Required:
-Python 3
-pandas Python Library
-osu! account


Steps to use this file:
1) Log into your osu! account
2) Under your profile on the top right, click on your avatar and go to your settings
3) Scroll until you reach the OAuth section. If you already have your own client click on Edit and remember the ClientID and Client Secret. If not, click "New OAuth Application" and type in a name inside "Application Name". Register application and then go to edit and get remember the ClientID and Client Secret. DO NOT SHARE THESE WITH ANYBODY.
4) Open the file in an editor
5) Locate the variables "USER" and "PASSWORD". Replace the placeholder values with your ClientID and Client Secret respectively
6) Locate the variable "USER_ID". Replace the placeholder with the user's account ID (Reminder, this code will not work if the user inputted is not in the top 10,000 in pp rank.
7) After saving these values, click to run the program. This may take a while.
8) If successful, there should be a csv file in the same folder with the date of process
