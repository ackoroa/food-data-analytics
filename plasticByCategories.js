db.product_simplified.aggregate(
    {$project: {categories:1}}, 
    {$unwind: "$categories"}, 
    {$group:{_id:"$categories", count:{$sum:1}}}, 
    {$out: "categories_count"}
)

db.product_simplified.aggregate(
    {$match: {packaging: {$in: ["plastic"]}}}, 
    {$project: {packaging:1, categories:1}}, 
    {$unwind: "$categories"}, 
    {$group:{_id:"$categories", count:{$sum:1}}}, 
    {$out: "plastic_categories_count"}
)

cur = db.plastic_categories_count.find().sort({count: -1})
while (cur.hasNext()) {
    data = cur.next()

    totalCount = db.categories_count.findOne({_id: data._id}).count
    ratio = data.count / totalCount
 
    db.plastic_categories_count.update(
        {
            _id: data._id
        },
        {
            $set: {
                "ratio": ratio
            }
        }, 
        {
            upsert: false,
            multi: false
        }
    )
}

db.plastic_categories_count.aggregate(
    {$match: {ratio:{$exists: true}}},
    {$sort: {count:-1}},
    {$limit: 100},
    {$sort: {ratio: -1}}
)
