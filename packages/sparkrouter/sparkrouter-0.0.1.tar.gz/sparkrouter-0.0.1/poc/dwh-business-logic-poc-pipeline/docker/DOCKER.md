# DOCKER INTEGRATION TESTING



## Common Operations

```shell
docker compose up -d
```

```shell
docker compose down -v
```

```shell
docker logs -f <container_id>
```

## Common Errors

### file exists

```shell
Error response from daemon: error while creating mount source path '/run/desktop/mnt/host/wsl/docker-desktop-bind-mounts/Ubuntu-24.04/1e2fd4452ea70042ebfbc8fc44df56dbf415966a98675fcb3525bc7535fefff3': mkdir /run/desktop/mnt/host/wsl/docker-desktop-bind-mounts/Ubuntu-24.04/1e2fd4452ea70042ebfbc8fc44df56dbf415966a98675fcb3525bc7535fefff3: file exists
```

Resolution

1. WSL: Restart the Docker Desktop service:
```shell
# Powershell
wsl --shutdown
```

2. Open Docker Desktop and let it restart completely

3. If the issue persists, try cleaning up Docker resources:
```shell
docker system prune -a
docker volume prune
```

### Startup

```shell
docker exec -it databricks-local bash

cat /home/jovyan/work/logs/master.log
cat /home/jovyan/work/logs/worker.log

# starting org.apache.spark.deploy.worker.Worker, logging to /home/jovyan/work/spark-logs/spark--org.apache.spark.deploy.worker.Worker-1-c92164767082.out
cat /home/jovyan/work/spark-logs/spark--org.apache.spark.deploy.worker.Worker-1-c92164767082.out



# Check worker process status
ps aux | grep worker

curl -s http://localhost:8080/json/ | grep workerInfos

curl http://0.0.0.0:8081

apt-get update && apt-get install -y net-tools
netstat -tuln | grep 8080
ps aux | grep master

cat /home/jovyan/work/spark-logs/spark--org.apache.spark.deploy.worker.Worker-1-*.out
```

### Spark

Getting spark configured is brutal.

1. To verify that your Spark network is configured correctly in Docker Compose, here are several methods you can use:

Check if host.docker.internal is properly resolved in containers:
```shell
docker exec spark-worker ping -c 2 host.docker.internal
```
This should return successful pings, verifying that the container can reach your WSL host. 

2. Verify Spark master is accessible from your host:
```shell
curl http://localhost:8080/json/
```
You should get a JSON response with Spark master information.

3. Check connectivity from worker to master within the Docker network:
```shell
docker exec spark-worker curl http://spark-master:8080/
```

4. Inspect Docker network configuration:
```shell
docker network ls
docker network inspect $(docker network ls | grep compose | awk '{print $1}')
```

```shell
# Run netshoot diagnostic container in your Spark network
docker run --rm -it --network dwh-business-logic-poc-pipeline_default nicolaka/netshoot bash

# From inside netshoot, test connectivity to Spark master
ping spark-master
curl -s http://spark-master:8080/
curl -s http://spark-master:7077/

# Test connectivity to spark-worker
ping spark-worker
curl -s http://spark-worker:8081/

# Test host.docker.internal resolution
ping host.docker.internal
curl -s http://host.docker.internal:8080/

# Exit when done
exit
```