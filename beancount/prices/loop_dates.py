#1/usr/bin/env python3


import subprocess
from datetime import timedelta, date
import sys
import fileinput

out_file = '/home/toms/d/fava/assets/prices.beancount'
data_src = 'USD:yahoo/NOKUSD=X'
bp_exe = '/home/toms/c/st/fava/src/beancount/bin/bean-price'

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2015, 6, 23)
end_date = date(2017, 6, 23)
# end_date = date.today()
for single_date in daterange(start_date, end_date):
    # print (single_date.strftime("%Y-%m-%d"))
    cmd_list = [bp_exe, '-d', single_date.strftime("%Y-%m-%d"), '--expression', str(data_src)]
    ps = subprocess.Popen(cmd_list, shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    with open(out_file, "a") as myfile:
        myfile.write(output.decode('utf8').replace('NOKUSD=X', 'NOK'))

# for line in fileinput.input(out_file, inplace=True):
#     # inside this loop the STDOUT will be redirected to the file
#     # the comma after each print statement is needed to avoid double line breaks
#     sys.stdout.write(line.replace("NOKUSD=X", "NOK"))
