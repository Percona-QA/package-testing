db.inventory.aggregate({$group: { _id: {details: "$details",item: "$item"}}})
db.serverStatus().storageEngine
