import sys
import json
import ast

#data_to_pass_back = 'send this to node process.'

input = ast.literal_eval(sys.argv[1])
output = input
with open('file.txt', 'w') as file:
    file.write(input)
output.append('send this to js')
print(json.dumps(output))

sys.stdout.flush()