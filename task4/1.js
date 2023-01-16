db = db.getSiblingDB("london");


printjson(db.taxi_rides.aggregate([
    {
        "$match": { "driver_review.text": { "$ne": null } }
    },
    {
        "$group": {
            "_id": "$driver_review.text"
        }
    },
    {
        "$addFields": {
            "length": {
                "$strLenCP": "$_id"
            }
        }
    },
    {
        "$sort": { "length": -1 }
    },
    {
        "$limit": 10
    }
], { allowDiskUse: true }));
