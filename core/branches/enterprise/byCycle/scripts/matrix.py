from byCycle.model import db, portlandor
region = portlandor.Region()
db = db.DB(region)
db.createAdjacencyMatrix()

