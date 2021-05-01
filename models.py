from pydantic import BaseModel, Extra, Field, ValidationError
from typing import Optional

class Document(BaseModel, extra=Extra.allow):
    docid: Optional[str] = None

class Node(Document):
    pass

class Edge(Node):
    source: str
    target: str

def validation_error(model,datadict):
    try:
        model.validate(datadict)
    except ValidationError as e:
        return e

if __name__ == '__main__':
    data = dict(foo='bar')
    errors = validation_error(Edge,data)
    print(errors)

