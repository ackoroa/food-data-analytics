cur = db.products.aggregate(
    [
        {
            $match: {
                "packaging_clean.0" : {$exists: true}
        },
        {
            $unwind: "$packaging_clean"
        },
        {
            $group: {
                _id: "$packaging_clean"
            }
            }
        },
        {
            $project: {
                _id: 0,
                packaging_clean: 1
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
    db.pack_idx.insert({pack_tag: data._id, idx: i})
    i += 1
}
