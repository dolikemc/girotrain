# girotrain
Training app for the Girotondo web site
Setup wagtail/django
Create a Page template (Writing Pages)
Get bootstrap4 theme (Bootstrap 4)
Create a menu (Template Tags)
Header for the web site (Bootstrap4 Template)
Add Footer using snippets
Add 2-languages support (i18n, Flags)
How to send a request or application
Child Admin
Move request to Child and Parents (Custom actions)
Girotondo Calendar
Holiday for Children
Time tracking for the team
Time tracking for the team
Cookies (Cookie-Law)
Accordion Page (bootstrap-accordion.php)
User and Groups
Assignment Plan
Sending Emails (Django & Emails)
Data protection expiry
Install on Aditssystems

dumpdata --natural-foreign --indent 2 -e contenttypes -e auth.permission -e wagtailcore.groupcollectionpermission -e wagtailcore.grouppagepermission -e wagtailimages.rendition -e sessions --output dump.json
makemigrations
migrate
collectstatic --noinput
createsuperuser
loaddata dump.json