import httplib
import urllib
import json
import time
import getpass
import Tkinter, Tkconstants, tkFileDialog

#
# Script that generates a set of groups in ArcGIS Online from a list in a txt file
#

# Open Group File
def openGroupFileDialog():
    root = Tkinter.Tk()    
    return tkFileDialog.askopenfilename(filetypes = (("Txt File","*.txt"),("All Files","*.*")))

# Generate Token
def generateToken(portal,username,password):
    parameters = urllib.urlencode({'username': username, 'password': password, 'client':'requestip','f':'json'})    
    request = portal + '/sharing/rest/generateToken?'
    response = json.loads(urllib.urlopen(request, parameters).read())

    if not 'token' in response:
        print "Bad user or password"
        exit()
        
    token = response['token']
    tokenExpires = response['expires']
    tokenExpiresReadable = time.strftime('%Y-%m-%d %I:%M:%S %p (%Z)', time.localtime(tokenExpires/1000))
    print "Token generated. Expires " +tokenExpiresReadable
    return token

# Create group
def createGroup(portal, groupTitle, groupDescription, token):
    params = urllib.urlencode({'title': groupTitle, 
        'description': groupDescription,
        'tags':'destacado,contenido,demo,esri,spain', #cambiar por un array
        'access':'org', 'token': token, 'f':'json'})
    request = portal + '/sharing/rest/community/createGroup?'
    response = json.loads(urllib.urlopen(request, params).read())
    data = urllib.urlopen(request, params).read()

##    if not 'group' in response:
##        print "Can't create group" + data
##        #exit()

    groupID = response['group']['id']
    print "Created Group #" + groupID    

# add Items to the organizations
def addItemsToGroup(portal, groupID, items, token):
    params = urllib.urlencode({'groups': groupID, 'token': token, 'f':'json'})
    for item in items:
        request = portal + '/sharing/rest/content/items/' + item + '/share'
        response = json.loads(urllib.urlopen(request, params).read())
        print "Added Item #" + item

# Get organization ID
def getOrganizationId(portal, token):
    params = urllib.urlencode({'token': token, 'f':'json'})
    request = portal + '/sharing/rest/portals/self?'
    response = json.loads(urllib.urlopen(request, params).read())
    myID = response['id']
    print "Org ID: " + myID
    return myID

# Change organization properties
def setOrganizationProperties(portal, organizationId, properties,token):
    properties['token'] = token
    properties['f'] = 'json'
    params = urllib.urlencode(properties)
    request = portal + '/sharing/rest/portals/' + organizationId + '/update?'
    response = json.loads(urllib.urlopen(request, params).read())

def readGroupsFromTxt(path):        
    grupo = [line.strip() for line in open(path)]
    return grupo


#
# Program Start
#
def main():
    portal = 'https://www.arcgis.com'

    #solicitar entrada al usuario
    customer = raw_input("Customer Name [{0}]: ".format(customer)) or customer
    username = raw_input("Username [{0}]: ".format(username)) or username
    password = getpass.getpass() or raw_input("Password [{0}]: ".format("fomentofomento"))
        
    # Generate Token
    token = generateToken(portal,username,password)

    grupos = readGroupsFromTxt(openGroupFileDialog())
    # Crear grupo
    for grupo in grupos:
        print grupo
        groupID = createGroup(portal, grupo, 
            'Grupo de ' + grupo + ' del Ayuntamiento de Viladecans ' + customer, token)

    myID = getOrganizationId(portal,token)

    properties = {
        'name': customer + ' - Portal demostrativo',
        'homePageFeaturedContent': groupID,
    }
    setOrganizationProperties(portal, myID, properties, token)

    print "Done"

main()
