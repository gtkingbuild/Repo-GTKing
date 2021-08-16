import os, xbmc, xbmcaddon

#########################################################
### Global Variables ####################################
#########################################################
PATH           = xbmcaddon.Addon().getAddonInfo('path')
ART            = os.path.join(PATH, 'resources', 'art')
#########################################################

#########################################################
### User Edit Variables #################################
#########################################################
ADDON_ID       = xbmcaddon.Addon().getAddonInfo('id')
ADDONTITLE     = 'GTKING [COLOR dodgerblue][B]WIZARD[/B][/COLOR]'
BUILDERNAME    = 'WHIZ'
EXCLUDES       = [ADDON_ID, 'plugin.program.gtking', 'plugin.video.balandro']
# Enable/Disable the text file caching with 'Yes' or 'No' and age being how often it rechecks in minutes
CACHETEXT      = 'Yes'
CACHEAGE       = 30
# Text File with build info in it.
BUILDFILE      = 'https://raw.githubusercontent.com/gtkingbuild/gtkingbuild.github.io/master/wizard/xml/autobuilds.txt'
# How often you would like it to check for build updates in days
# 0 being every startup of kodi
UPDATECHECK    = 0
# Text File with apk info in it.  Leave as 'http://' to ignore
APKFILE        = 'https://'
# Text File with Youtube Videos urls.  Leave as 'http://' to ignore
YOUTUBETITLE   = ''
YOUTUBEFILE    = ''
# Text File for addon installer.  Leave as 'http://' to ignore
ADDONFILE      = 'https://'
# Text File for advanced settings.  Leave as 'http://' to ignore
ADVANCEDFILE   = 'https://gtkingbuild.github.io/wizard/xml/Advanced.txt'  
#########################################################

#########################################################
### Theming Menu Items ##################################
#########################################################

ICONBUILDS     = 'https://i.imgur.com/0oZFQlm.png'
ICONMAINT      = 'https://i.imgur.com/Qa9aiZN.png'
ICONAPK        = 'http://'
ICONADDONS     = 'https://i.imgur.com/ixrJpUF.png'
ICONYOUTUBE    = 'http://'
ICONSAVE       = 'https://i.imgur.com/Pmdet1T.png'
ICONTRAKT      = 'http://'
ICONREAL       = 'http://'
ICONLOGIN      = 'http://'
ICONCONTACT    = 'https://i.imgur.com/3oacF0o.png'
ICONSETTINGS   = 'https://i.imgur.com/we4zQT3.png'
# Hide the ====== seperators 'Yes' or 'No'
HIDESPACERS    = 'No'
# Character used in seperator
SPACER         = '='

# You can edit these however you want, just make sure that you have a %s in each of the
# THEME's so it grabs the text from the menu item
COLOR1         = 'lime'
COLOR2         = 'white'
# Primary menu items   / %s is the menu item and is required
THEME1         = '[COLOR '+COLOR1+'][B][COLOR '+COLOR2+'][/COLOR][/B][/COLOR] [COLOR '+COLOR2+']%s[/COLOR]'
# Build Names          / %s is the menu item and is required
THEME2         = '[COLOR '+COLOR2+']%s[/COLOR]'
# Alternate items      / %s is the menu item and is required
THEME3         = '[COLOR '+COLOR1+']%s[/COLOR]'
# Current Build Header / %s is the menu item and is required
THEME4         = '[COLOR '+COLOR1+']Version GTKING Instalada:[/COLOR] [COLOR '+COLOR2+']%s[/COLOR]'
# Current Theme Header / %s is the menu item and is required
THEME5         = '[COLOR '+COLOR1+']Current Theme:[/COLOR] [COLOR '+COLOR2+']%s[/COLOR]'
# Current Theme Header / %s is the menu item and is required
THEME6         = '[COLOR '+COLOR1+']Version GTKING a instalar:[/COLOR] [COLOR '+COLOR2+']%s[/COLOR]'

# Message for Contact Page
# Enable 'Contact' menu item 'Yes' hide or 'No' dont hide
HIDECONTACT    = 'No'
# You can add \n to do line breaks
CONTACT        = 'Gracias por utilizar GTKING Build\r\n\r\nSi quieres ponerte en contacto utiliza Telegram'
#Images used for the contact window.  http:// for default icon and fanart
CONTACTICON    = 'https://i.imgur.com/JIbMO3S.png'
CONTACTFANART  = 'https://i.imgur.com/8xuyrLt.jpg'
#########################################################

#########################################################
### Auto Update                   #######################
###        For Those With No Repo #######################
#########################################################
# Enable Auto Update 'Yes' or 'No'
AUTOUPDATE     = 'Yes'
# Url to wizard version
WIZARDFILE     = 'https://raw.githubusercontent.com/gtkingbuild/gtkingbuild.github.io/master/wizard/xml/autobuilds.txt'
#########################################################

#########################################################
### Auto Install                 ########################
###        Repo If Not Installed ########################
#########################################################
# Enable Auto Install 'Yes' or 'No'
AUTOINSTALL    = 'No'
# Addon ID for the repository
REPOID         = 'repository.GTKing-LEIA'
# Url to Addons.xml file in your repo folder(this is so we can get the latest version)
REPOADDONXML   = 'https://raw.githubusercontent.com/gtkingbuild/Repo-GTKing/master/leia/addons.xml'
# Url to folder zip is located in
REPOZIPURL     = 'https://raw.githubusercontent.com/gtkingbuild/Repo-GTKing/master/leia/repository.GTKing-LEIA-2.7.5.zip/'
#########################################################

#########################################################
### Notification Window #################################
#########################################################
# Enable Notification screen Yes or No
ENABLE         = 'Yes'
# Url to notification file
NOTIFICATION   = 'https://raw.githubusercontent.com/gtkingbuild/gtkingbuild.github.io/master/wizard/xml/Notify.txt'
# Use either 'Text' or 'Image'
HEADERTYPE     = 'Text'
# Font size of header
FONTHEADER     = 'Font16'
HEADERMESSAGE  = 'GTKING WIZARD'
# url to image if using Image 424x180
HEADERIMAGE    = 'http://'
# Font for Notification Window
FONTSETTINGS   = 'Font14'
# Background for Notification Window
BACKGROUND     = 'https://i.imgur.com/8xuyrLt.jpg'
#########################################################
