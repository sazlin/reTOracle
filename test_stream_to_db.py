import json

filter_list = {"c": ['#cprogramming', '#clanguage'],
    "python": ['#python', '#django', '#pyconau', '#numpy', '@gvanrossum'],
    "java": ['java'], "javascript": ["#Javascript", "#BackboneJS", "#NodeJS"]}


json_list = json.dumps(filter_list)

return json_list