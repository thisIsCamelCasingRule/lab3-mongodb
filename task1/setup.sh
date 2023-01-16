docker compose up -d

# init config server
docker compose exec configsvr01 sh -c "mongosh < /scripts/config-server-init.js"

# init shards
docker compose exec shard01-a sh -c "mongosh < /scripts/shard01-init.js"
docker compose exec shard02-a sh -c "mongosh < /scripts/shard02-init.js"
docker compose exec shard03-a sh -c "mongosh < /scripts/shard03-init.js"

sleep 10

docker compose exec router01 sh -c "mongosh < /scripts/router-init.js"

docker compose exec router01 mongosh --port 27017 --eval "sh.status()"
