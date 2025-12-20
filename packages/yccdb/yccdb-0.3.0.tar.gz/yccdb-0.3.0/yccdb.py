import requests
import ast
def isonline():
    return requests.get("https://yorksoncoding.bloodcircuit.org/debugapi?dbg=return hello").text == "hello"
def getdb(tkn : str, file : str = None):
    if not isonline():
        print("api is not online. please contact support@bloodcircuit.org")
        return None
    db = requests.get(f"http://yorksoncoding.bloodcircuit.org/db/__api__?req=get&tkn={tkn}&dbfile={file}")
    return ast.literal_eval(db.text)
def pushdb(tkn : str, file : str, pkey : str, pval):
    if not isonline():
        print("api is not online. please contact support@bloodcircuit.org")
        return None
    o = requests.get(f"http://yorksoncoding.bloodcircuit.org/db/__api__?req=push&tkn={tkn}&dbfile={file}&pkey={pkey}&pval={str(pval)}")
def dumpdb(tkn : str, file : str, data : dict):
    if not isonline():
        print("api is not online. please contact support@bloodcircuit.org")
        return None
    o = requests.get(f"http://yorksoncoding.bloodcircuit.org/db/__api__?req=dump&tkn={tkn}&dbfile={file}&data={str(data)}")
def deldb(tkn : str, file : str, dkey):
    if not isonline():
        print("api is not online. please contact support@bloodcircuit.org")
        return None
    o = requests.get(f"http://yorksoncoding.bloodcircuit.org/db/__api__?req=del&tkn={tkn}&dbfile={file}&del={str(dkey)}")
def clrdb(tkn : str, file : str):
    if not isonline():
        print("api is not online. please contact support@bloodcircuit.org")
        return None
    o = requests.get(f"http://yorksoncoding.bloodcircuit.org/db/__api__?req=clr&tkn={tkn}&dbfile={file}")