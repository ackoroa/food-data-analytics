db.products.mapReduce(
    function() {
        for (var ing in this.ingredients) {
            if (!this.ingredients[ing].id) continue;
            emit(this.ingredients[ing].id, 1);
 
        }
    },
    function (key, values) {
        return Array.sum(values);
    },
    {
        out: "ingredientCount"
    }
)