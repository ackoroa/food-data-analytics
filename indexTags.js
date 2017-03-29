cur = db.product_simplified.aggregate(
    [
        {
            $match: {
                "packaging.0" : {$exists: true}
            }
        },
        {
            $project: {
                _id: 0,
                packaging: 1
            }
        },
        {
            $unwind: "$packaging"
        },
        {
            $group: {
                _id: "$packaging"
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
    db.packaging_idx.insert({_id: data._id, idx: i})
    i += 1
}
