from pyhanlp import  *
import csv
import pandas as pd
with open("known.csv","r+") as f:
    all=csv.reader(f)

    with open("known.ttl",'w',encoding='utf-8') as out:
        for line in all:
            str0 = "<http://kbqa.com/entity/"+str(line[0])+">"
            str1 = "<http://kbqa.com/relation/"+str(line[1])+">"
            str2 = "<http://kbqa.com/entity/" + str(line[2]) + "> ."
            out.write(str0+' '+str1+' '+str2+'\n')