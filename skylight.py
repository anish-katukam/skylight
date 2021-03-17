import codecs
import os
import sys
import argparse


#          |\
#          | \
#()########|  =================================================*
#          | /
#          |/

projectPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(projectPath+"/lib")

import paramiko

#set private key
key = paramiko.RSAKey.from_private_key_file("resources\key.pem", "")

#set useful constants
host = ""
username = ""

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", help = "In testing mode, indextest.html, not index.html, is edited.", action = "store_true")
parser.add_argument("-l", "--local", help = "In local mode, no files are pushed to the server.", action = "store_true")

args = parser.parse_args()

#if test is true, it will update indextest and not index
test = args.test

#if local is true, it won't push any files to the server
local = args.local

#print current active modes
if test or local:
    print ("Currently in " + ("", "testing mode")[test] + ("", " and ")[test and local] + (".", "local mode.")[local])

#text title, date, and subtitle
TITLE = input("Title: ")
DATE = " " + input("Date: ")
SUBTITLE = input("Subtitle: ")

#url title, used in index
TITLEURL = TITLE.replace(" ", "%20") + ".html"

#used for remote transferring the file
FILENAME = TITLE + ".html"
FILEPATH = "/var/www/html/posts/" + FILENAME.replace(" ", "\ ")

if (test):
    INDEXPATH = "/var/www/html/indextest.html"
else:
    INDEXPATH = "/var/www/html/index.html"

#to replace the index


#open SSH connection
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname = host, username = username, pkey = key)

#open SFTP client
sftp_client = client.open_sftp()

#convert post

#do what you gotta do
tab = "      "

#open post (input file) and tag (google analytics script)
post = codecs.open('post.txt', encoding='utf-8')
tag = codecs.open('resources\\tag.txt', encoding='utf-8')

#conversion to html
with codecs.open("output.html", "w", "utf-8-sig") as doc:

    #write GA tag
    for line in tag:
        doc.write(line)

    #document specific tags
    doc.write("<div><h2 class=\"title\">" + TITLE + "</h2>\n")
    doc.write(tab + "<br>\n")
    doc.write(tab + "<p class=\"date\">" + DATE + "</p>\n")
    doc.write(tab + "<div class=\"content\">\n")


    #copy content
    doc.write(2 * tab + "<p> \n")
    for line in post:
        if line == "\r\n" or line == "\n":
            doc.write(2 * tab + "<p> \n")
        else:
            doc.write(3 * tab + line)

    #write ending tags
    doc.write("\n\n")
    doc.write(tab + "</div>\n")
    doc.write("</div>\n")
    doc.write("</body>\n")
    doc.write("</html>\n")

#pull index for update
if (test):
    sftp_client.get("/var/www/html/indextest.html", "index.html")
else:
    sftp_client.get("/var/www/html/index.html", "index.html")

#convert index

#do what you gotta do
tab = "  "

#open index
index = codecs.open('index.html', encoding='utf-8')

#conversion to html
with codecs.open("newIndex.html", "w", "utf-8-sig") as doc:

    for line in index:
        doc.write(line)
        if "<!--Skylight content starts here-->" in line:
            doc.write("\n\n")
            doc.write(3 * tab + "<div class=\"media\">\n")
            doc.write(4 * tab + "<div class=\"media-body\">\n")
            doc.write(5 * tab + "<a class=\"media-heading\" href=\"posts/" + TITLEURL + "\">" + TITLE + "</a>\n")
            doc.write(5 * tab + "<span class=\"date\">" + DATE + "</span>\n")
            doc.write(5 * tab + "<div class=\"media-content\">" + SUBTITLE + "</div>\n")
            doc.write(4 * tab + "</div>\n")
            doc.write(3 * tab + "</div>")

#push converted index
if (not local):
    #push converted post
    sftp_client.put("output.html", "/var/www/html/posts/" + FILENAME)
    if (test):
        sftp_client.put("newIndex.html", "/var/www/html/indextest.html")
    else:
        sftp_client.put("newIndex.html", "/var/www/html/index.html")




#convert pushed index to unix text file
stdin, stdout, stderr = client.exec_command("dos2unix " + INDEXPATH + " " + INDEXPATH)

#convert pushed file to unix text file
stdin, stdout, stderr = client.exec_command("dos2unix " + FILEPATH + " " + FILEPATH)

#sanitation
index.close()
stdin.close()
os.remove("newIndex.html")
os.remove("output.html")
os.remove("index.html")
sftp_client.close()
client.close()
