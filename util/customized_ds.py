
class DotDict(dict):
    def __init__(self,data):
        
        for key, value in data.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)

            else:
                self[key] = value
                
    def __getattr__(self, attr):
        return self.get(attr)
    
    def __setattr__(self, attr, value):
        if isinstance(value, dict):
            self[attr] = DotDict(value)
        else:
            self[attr] = value
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            super().__setitem__(key, DotDict(value))
        elif isinstance(value, list):
            super().__setitem__(key, [])
            for item in value:
                if isinstance(item, dict):
                    self[key].append(DotDict(item))
                else:
                    self[key].append(item)
        else:
            super().__setitem__(key, value)

          
            
# the following is only for unit test
# a = "Hello and a very warm welcome to everyone joining us today! I'll be your host for this discussion. My name is {config.bots.bot1.name}"
# dd = DotDict({"config":{"bots":{"bot1":{"name":"Alice"}}}})
# d = {"config":{"bots":{"bot1":{"name":"Alice"}}}}
# print(a.format(**dd))
# print(a.format(**d)) # 报错 AttributeError: 'dict' object has no attribute 'bots'

# dd = DotDict({"config":{"bots":{"bot1":{"name":"Alice"}}}})
# dd = DotDict({"a":{"b":1}})
# print(dd.a.b)
# print(dd["a"].b)
# session = DotDict(dict())
# key = "a"
# session[key] = {"free":True}
# print(session)
# print(session.a.free)

# import json
# def read_config():
#     import yaml
#     with open('../config.yaml', 'r') as f:
#         data = yaml.load(f, Loader=yaml.SafeLoader)
#     return data

# config = DotDict(read_config())

# with open("../template/message1Bot.json") as f:
#     d = json.load(f)
#     piplineDict = DotDict(d)
# # print(d)
# print(piplineDict)
# print(config)
# print(type(piplineDict.steps[0].messages[0]))
# print(piplineDict.steps[0].messages[0].content.format(**DotDict({"config":config})))
