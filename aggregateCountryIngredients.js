db.product_simplified.aggregate(
  {
    $project:
      {
        countries:1,
        ingredients:1
      }
    }, 
    {
      $unwind: "$countries"
    }, 
    {
      $unwind: "$ingredients"
    }, 
    {
      $group: {
        _id: "$countries", 
        ingredients: {$addToSet: "$ingredients"}
      }
    }, 
    {$out: "country_ingredients"}
)