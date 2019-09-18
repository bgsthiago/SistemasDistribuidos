from resource import Resource

RESOURCES = ['A', 'B', 'C']



lista = [Resource(i) for i in RESOURCES]
while True:

    name = input('Digita ai: ')

    item = lista[lista.index(Resource(name))]

    print(item)