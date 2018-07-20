db.inventory.insert(
   {
     item: "ABC1",
     details: {
        model: "14Q3",
        manufacturer: "XYZ Company"
     },
     stock: [ { size: "S", qty: 25 }, { size: "M", qty: 50 } ],
     category: "clothing"
   }
)

db.inventory.insert(
   {
     item: "BAC9",
     details: {
        model: "14Q3",
        manufacturer: "XYZ Company"
     },
     stock: [ { size: "L", qty: 73 }, { size: "M", qty: 99 } ],
     category: "clothing"
   }
)

db.inventory.insert(
   {
     item: "BC1",
     details: {
        model: "14Q3",
        manufacturer: "YZX Company"
     },
     stock: [ { size: "XL", qty: 5 }, { size: "S", qty: 502 } ],
     category: "clothing"
   }
)

db.inventory.find()
