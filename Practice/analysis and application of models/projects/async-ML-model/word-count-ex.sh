kafka-topics.sh --create \
                --bootstrap-server localhost:9092  \
                --replication-factor 1 \
                --partitions 1 \
                --topic streams-plaintext-input

kafka-topics.sh --create \
                --bootstrap-server localhost:9092  \
                --replication-factor 1 \
                --partitions 1 \
                --topic streams-plaintext-output

echo -e "all streams lead to kafka\nhello kafka streams\njoin kafka summit" > /tmp/file-input.txt

cat /tmp/file-input.txt | ./bin/kafka-console-producer --broker-list localhost:9092 --topic streams-plaintext-input
