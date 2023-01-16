cd ../task1

docker compose cp "../task4/1.js" router01:"1.js"
docker compose exec router01 mongosh --port 27017 1.js
