#!/bin/bash
#
# This script simulates a Google Cloud Pub/Sub request to the LOC Cloud Function made from Make.com

id=$1

read -r -d '' payload << EOL
{
    "message": {
        "attributes": {
            "googclient_schemaencoding": "JSON",
            "googclient_schemarevisionid": "1234"
        },
        "data": "$(echo "{\"id\": \"$id\", \"dev\": true, \"local\": true}" | base64)",
        "messageId": "1234",
        "message_id": "1234",
        "publishTime": "2024-03-24T16:28:35.273Z",
        "publish_time": "2024-03-24T16:28:35.273Z"
    },
    "subscription": "projects/dummy/subscriptions/dummy"
}
EOL

curl localhost:8080 -X POST -H 'Content-Type: application/json' -d "$(echo $payload)"
