cur = db.product_simplified.aggregate(
    [
        {
            $match: {
                "ingredients.0" : {$exists: true}
            }
        },
        {
            $project: {
                _id: 0,
                ingredients: 1
            }
        },
        {
            $unwind: "$ingredients"
        },
        {
            $group: {
                _id: "$ingredients"
            }
        },
        {
            $sort: {
                _id: 1
            }
        }
    ],
    {
        allowDiskUse: true
    }
)

i = 0
while (cur.hasNext()) {
    data = cur.next()
    db.ingredients_idx.insert({_id: data._id, idx: i})
    i += 1
    if (i > 5) break;
}
