import json

filter_list = {"c": {'search_terms':
                       {'hashtags': ['#cprogramming', '#clanguage'],
                        'users': [],
                        'keywords': []},
                     'blacklist':
                       {'hashtags': [],
                        'users': [],
                        'keywords': []}},
"python": {'search_terms':
                {'hashtags': ['#Python', '#Django', '#pyconau', '#numpy', '#Flask'],
                 'users': ['@gvanrossum', '@ThePSF', '@SciPyTip', '@brandon_rhodes'],
                 'keywords': []},
           'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': ['monty', 'snake']}},
"java": {'search_terms':
                {'hashtags': ['#Java', '#javadeveloper', '#javafx', '#java8', '#JavaEE'],
                 'users': ['@java', '@java4iot', '@awsforjava', '@4java'],
                 'keywords': ['java -coffee']},
         'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': ['coffee']}},
"javascript": {'search_terms':
                {'hashtags': ['#Javascript', '#BackboneJS', '#NodeJS', '#JQuery'],
                 'users': ['@JavaScriptDaily', '@oss_js', '@badass_js', '@jasminebdd', '@nodejs'],
                 'keywords': []},
        'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': ['java ']}},
"ruby": {'search_terms':
                {'hashtags': ['#Ruby', '#RubyOnRails', '#rubyconfbr', '#rails'],
                 'users': ['@RubyInside', '@rubyrogues', '@rails'],
                 'keywords': ['ruby -jewelry', 'ruby -ring', 'ruby -gift']},
        'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': []}},
"php": {'search_terms':
                {'hashtags': ['#PHP'],
                 'users': ['@php_net', '@awsforphp', '@phpc', '@phpizer'],
                 'keywords': []},
           'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': []}},
"csharp": {'search_terms':
                {'hashtags': ['#CSharp'],
                 'users': ['@csharp_projects', '@CHharpStack', '@CsharpCorner', '@oss_csharp'],
                 'keywords': []},
           'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': []}},
"objectivec": {'search_terms':
                {'hashtags': ['#objectivec'],
                 'users': ['@objective', '@ObjectiveCDaily', '@idObjectiveC', '@ObjConSO'],
                 'keywords': []},
           'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': []}},
"swift": {'search_terms':
                {'hashtags': ['#swiftlang'],
                 'users': ['@SwiftLang'],
                 'keywords': []},
           'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': ['Taylor ']}},
"visual_basic": {'search_terms':
                {'hashtags': ['#VBA', '#VB', '#VB.NET'],
                 'users': ['@visualbasic_net'],
                 'keywords': []},
           'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': []}}}
