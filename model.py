class Product:
    id:int
    name:str
    decription:str
    price:float
    quanity:int

    def __init__(self, id:int, name:str, decription:str, price:float, quanity:int):
        self.id = id
        self.name = name
        self.decription = decription
        self.price = price
        self.quanity = quanity