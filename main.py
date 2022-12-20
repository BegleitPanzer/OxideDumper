import datetime
import requests
import os
import subprocess
import re
import json

pattern = r"(public|private|protected|internal)\s(\w+\.?\w*\.?\w*)\s(\w+);\s\/\/\s(0x[0-9a-fA-F]+)?"

def writeoffset(file, classname, definition):
    for line in dumpcs.split(definition)[1].split("}")[0].split("\n"):
        if re.search(pattern, line):
            file.write("\troffset " + classname + "_" + re.search(pattern, line).group(3) + " = " + re.search(pattern, line).group(4) + "; \n")

if not os.path.exists("steamcmd"):
    os.makedirs("steamcmd")
    
if not os.path.exists("il2cppdumper"):
    os.makedirs("il2cppdumper")

if not os.path.exists("steamcmd/steamcmd.exe"):
    print("Downloading SteamCMD...")
    url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
    r = requests.get(url, allow_redirects=True)
    open('steamcmd/steamcmd.zip', 'wb').write(r.content)
    import zipfile
    with zipfile.ZipFile("steamcmd/steamcmd.zip", 'r') as zip_ref:
        zip_ref.extractall("steamcmd")
    os.remove("steamcmd/steamcmd.zip")
    print("Finished downloading SteamCMD")

if not os.path.exists("il2cppdumper/Il2CppDumper.exe"):
    print("Downloading Il2CppDumper...")
    url = "https://github.com/Perfare/Il2CppDumper/releases/download/v6.7.25/Il2CppDumper-v6.7.25.zip"
    r = requests.get(url, allow_redirects=True)
    open('il2cppdumper/il2cppdumper.zip', 'wb').write(r.content)
    import zipfile
    with zipfile.ZipFile("il2cppdumper/il2cppdumper.zip", 'r') as zip_ref:
        zip_ref.extractall("il2cppdumper")
    os.remove("il2cppdumper/il2cppdumper.zip")
    print("Done downloading Il2CppDumper")
    
print("Checking for updates...")
process = subprocess.Popen(["steamcmd/steamcmd.exe", "+login", "anonymous", "+app_info_print", "252490", "+quit"], stdout=subprocess.PIPE)
output, error = process.communicate()
output = "{" + output.decode("utf-8").split("{", 1)[1].rsplit("}", 1)[0] + "}"
manifestid = output.split("\"252495\"")[1].split("\"last-month\"")[0].split("\"public\"\t\t\"")[1].split("\"")[0]
if not os.path.exists("manifestid"):
    os.open("manifestid", os.O_CREAT)
if open("manifestid", "r").read() != manifestid:
    print("Update found!")
    

    os.system(os.getcwd() + "/steamcmd/steamcmd.exe +login " + os.getenv("USERPASS").split(":")[0] + " " + os.getenv("USERPASS").split(":")[1] + " +download_depot 252490 252495 " + manifestid + " +quit")
    
    os.system("il2cppdumper\Il2CppDumper.exe steamcmd/steamapps/content/app_252490/depot_252495/GameAssembly.dll steamcmd/steamapps/content/app_252490/depot_252495/RustClient_Data/il2cpp_data/Metadata/global-metadata.dat")
    
    if os.path.exists("offsets.h"):
        os.remove("offsets.h")
    os.open("offsets.h", os.O_CREAT)
    offsetfile = open("offsets.h", "w")
    scriptjson = open("il2cppdumper/script.json", "r", encoding="utf8").read()
    dumpcs = open("il2cppdumper/dump.cs", "r", encoding="utf8").read()
    offsetfile.write("//Dumped with Oxide Dumper https://github.com/LabGuy94/OxideDumper \n#include <cstdint> \n#define roffset static uintptr_t\nnamespace offsets \n{\n")
        
    scriptjsonobject = json.loads(scriptjson) 
    
    offsetfile.write("\t//script.json offsets\n")
    
    for function in scriptjsonobject["ScriptMetadata"]:
        if function["Signature"] == "BaseNetworkable_c*":
            offsetfile.write("\troffset BaseNetworkable_c = " + hex(int(function["Address"])) + "; \n")
        if function["Signature"] == "BaseEntity_c*":
            offsetfile.write("\troffset BaseEntity_c = " + hex(int(function["Address"])) + "; \n")
        if function["Signature"] == "ConVar_Graphics_c*":
            offsetfile.write("\troffset Graphics_c = " + hex(int(function["Address"])) + "; \n")
        if function["Signature"] == "MainCamera_c*":
            offsetfile.write("\troffset MainCamera_c = " + hex(int(function["Address"])) + "; \n")
        
        
            
    
    #Literally George Orwell's 1984
    offsetfile.write("\t//Base Player\n")
    writeoffset(offsetfile, "BasePlayer", "public class BasePlayer : BaseCombatEntity")
    offsetfile.write("\t//Player Inventory\n")
    writeoffset(offsetfile, "PlayerInventory", "public class PlayerInventory : EntityComponent")
    offsetfile.write("\t//Base Entity\n")
    writeoffset(offsetfile, "BaseEntity", "public class BaseEntity : BaseNetworkable")
    offsetfile.write("\t//Base Combat Entity\n")
    writeoffset(offsetfile, "BaseCombatEntity", "public class BaseCombatEntity : BaseEntity")
    offsetfile.write("\t//Base Projectile\n")
    writeoffset(offsetfile, "BaseProjectile", "public class BaseProjectile : AttackEntity")
    offsetfile.write("\t//Magazine\n")
    writeoffset(offsetfile, "Magazine", "public class BaseProjectile.Magazine")
    offsetfile.write("\t//Item\n")
    writeoffset(offsetfile, "Item", "public class Item ")
    
    offsetfile.write("} \n")
        
    
    
    open("manifestid", "w").write(manifestid)
else:
    print("No update.")