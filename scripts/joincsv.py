import glob, csv, json, re, copy, os, numbers

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def patchCountyNames(countyname):
    if countyname.title() in ["Tharaka-Nithi","Tharaka Nithi","Tharaka -Nithi","Tharaka - Nithi"]:
        return "Tharaka"
    elif countyname.title() in ["Elgeyo/Marakwet","Elgeyo / Marakwet", "Elgeyo /Marakwet", "Elgeyo Marakwet", "Elgeyo/ Marakwet"]:
        return "Elgeyo-Marakwet"
    elif countyname.title() in ["Garrissa"]:
        return "Garissa"
    elif countyname.title() in ["Nairobi City"]:
        return "Nairobi"
    elif countyname.title() in ["Taita /Taveta","Taita/Taveta","Taita / Taveta"]:
        return "Taita Taveta" 
    elif countyname.title() in ["Murang’a","Murang'A","Muranga","Muranga'","Murang’A"]:
        return "Murang'a"
    elif countyname.title() in ["Bus Ia"]:
        return "Busia"
    elif countyname.title() in ["Homabay"]:
        return "Homa Bay"
    elif countyname.title() in ["Kis Ii"]:
        return "Kisii"
    elif countyname.title() in ["Transnzoia","Trans-Nzoia"]:
        return "Trans Nzoia"
    elif countyname.title() in ["Kirinyag’A"]:
        return "Kirinyaga"
    return countyname.title()


path = "datasets/csv/*.csv"
outputpath = "datasets/geojson/"
jsondata = []
for fname in glob.glob(path):
    with open(fname, newline='') as f:
        fields = []
        field = {}
        fieldCount = 0
        #JSON Object to Store this Data in
        reader = csv.reader(f)
        i = next(reader)
        for o in i:
            if fieldCount == 0:
                #Create the County Code (this is the key to join with GeoJSON)
                field = {"name":"NAME","alias": "County","value":""}
                fieldCount = 1
            else:
                #fix the name 
                fieldName = "f" + re.sub(r'\W+', '', o)
                field = {"name":fieldName,"alias": o,"value":""}
            fields.append(field)

        #Now process the actual values into the Field Objects we just created
        newrows = []
        for row in reader:
            rpos = 0
            newfields = []
            for r in row:
                if rpos == 0:
                    #Repair the county name to match geojson
                    r = patchCountyNames(r)
                #Get the Field in This Position from the fields array
                newfield = copy.deepcopy(fields[rpos])
                newr = r.replace(',', '')
                if newr == "88.9":
                    print ("test")

                if newr.isnumeric() or isfloat(newr):
                    if isinstance(float(newr), float):
                        r = float(newr)
                    elif isinstance(int(newr), numbers.Integral):
                        r = int(newr)


                newfield["value"] = r
                rpos = rpos + 1
                newfields.append(newfield)
            newrows.append(newfields)
    jsontable = {"table": re.sub(r'\W+', '', os.path.basename(fname)), "data": newrows}
    jsondata.append(jsontable)

#The Structure for all the data in the CSV Files is now in a large JSON Object we can use to Join to the GeoJSON File
#read the GeoJSON Into an object
newgeojson = []

# Loop each of the data set from the JSON object created above
for datarow in jsondata:
    #Create a new copy of the GeoJSON for Output
    with open('boundaries/KEN_WILAYA_L2.geojson') as f:
        boundarydata = json.load(f)
        featuretable = copy.deepcopy(boundarydata)

        for dataobject in datarow["data"]:
            countyname = dataobject[0]['value']
            newfeature = None
            for feature in featuretable["features"]:
                if countyname == feature["properties"]["NAME"]:
                    newfeature = feature
                    #Add the values from the 
                    break
            if newfeature is None:
                print("A feature with NAME ", countyname, "was not found in the GeoJSON")
            else:
                #Apply the properties from the JSON to the GeoJSON
                for data in dataobject:
                    newfeature["properties"][data["name"]] = data["value"]
    with open(outputpath + datarow["table"] + ".geojson", 'w') as outfile:
        json.dump(featuretable, outfile)
        
print ("All Done")
