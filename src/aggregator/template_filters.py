from google.appengine.ext.webapp import template

register = template.create_template_register()

def split(list, sep=';') :
    list = list.split(sep)
    if list[-1] == '' :
        list = list[:-1]
    return list

register.filter(split)
