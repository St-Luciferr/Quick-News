import math
# import os
# import random
# import re
# import sys

def encryption(s):
    str_list=s.split()
    space_less="".join(str_list)
    L=len(space_less)
    root=math.sqrt(L)
    rows=math.floor(root)
    column=math.ceil(root)
    i=0
    ls=[]
    while(i<L):
        ls.append(space_less[i:i+column])
        i+=column
    output=""
    for i in range(column):
        for item in ls:
            try:
                output=output+item[i]
            except:
                pass
        output=output+" "
    return output

str="if man was meant to stay on the ground god would have given us roots"
encryption(str)