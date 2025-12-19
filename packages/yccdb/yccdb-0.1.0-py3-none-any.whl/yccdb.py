import requests
import ast
def getdb(tkn : str, file : str = None):
    db = requests.get(f"http://yorksoncoding.bloodcircuit.org/db/__api__?req=get&tkn={tkn}&dbfile={file}")
    return ast.literal_eval(db.text)
def pushdb(tkn : str, file : str, pkey : str, pval):
    o = requests.get(f"http://yorksoncoding.bloodcircuit.org/db/__api__?req=push&tkn={tkn}&dbfile={file}&pkey={pkey}&pval={str(pval)}")
    print(o.text)
