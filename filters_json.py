import json

filter_list = {"c/cpp": {'search_terms':
                       {'hashtags': ['#cprogramming', '#clanguage', '#clang', '#cpp11', '#cpp', '#cplusplus'],
                        'users': ['@cpluspluscom', '@c_plus_plus', '@isocpp', '@visualc', '@cpphl'],
                        'keywords': ['cplusplus', 'C++']},
                     'blacklist':
                       {'hashtags': [],
                        'users': [],
                        'keywords': ['cpp -investment']}},
"python": {'search_terms':
                {'hashtags': ['#Python', '#Django', '#pyconau', '#numpy', '#Flask', '#Grok', '#Pylons', '#Pyramid', '#TurboGears', '#web2py', '#Zope', '#CPython', '#SciPyConf', '#PyPy', '#gevent', '#pydata', '#pycoders', '#pycon', '#ipython'],
                 'users': ['@gvanrossum', '@ThePSF', '@SciPyTip', '@brandon_rhodes', '@dstuft', '@raymondh', '@PloneCMS', '@Flask', '@Grok', '@Pylons', '@Pyramid', '@TurboGears', '@web2py', '@Zope', '@RedditPython', '@SciPyConf', '@pypyproject', '@realpython'],
                 'keywords': []},
           'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': ['monty', 'snake']}},
"java": {'search_terms':
                {'hashtags': ['#Java', '#javadeveloper', '#javafx', '#java8', '#JavaEE', '#springio', '#springboot', '#springframework', '#android'],
                 'users': ['@java', '@java4iot', '@awsforjava', '@4java', '@springboot', '@springcentral', '@javafact', '@grailsframework'],
                 'keywords': ['java -coffee']},
         'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': ['java -coffee']}},
"javascript": {'search_terms':
                {'hashtags': ['#Javascript', '#BackboneJS', '#NodeJS', '#JQuery', '#spinejs', '#agilityjs', '#canjs', '#sammyjs', '#snackjs', '#qunitjs', '#serenadejs', '#amplifyjs'],
                 'users': ['@JavaScriptDaily', '@oss_js', '@badass_js', '@jasminebdd', '@nodejs', '@emberjs'],
                 'keywords': []},
        'blacklist':
                {'hashtags': [],
                 'users': [],
                 'keywords': ['']}},
"ruby": {'search_terms':
                {'hashtags': ['#Ruby', '#RubyOnRails', '#rubyconfbr', '#rails', '#merb', '#cancan'],
                 'users': ['@RubyInside', '@rubyrogues', '@rails', '@rubytoolbox'],
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
                {'hashtags': ['#objectivec', '#ios'],
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
