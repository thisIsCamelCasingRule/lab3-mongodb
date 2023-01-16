cd ../task1
docker compose exec router01 mongosh --port 27017 --eval "use london;" --eval "printjson(db.taxi_rides.stats());"
