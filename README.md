<h1>The prototipe of microservice application made by djangorestframework.</h1><br>
Three microservices send each other POST with message. Each microservice add timestamp to the message. The message go by ring. First microservice inits sending and save to database the message from last microsevice.
You need to have docker and docker-compose (I used docker v.19.03.14 and docker-compose v.3)
To run application you need to do next steps:<br>
1) do clone of repository https://github.com/popovpp/ring2.git;<br>
2) do migrate by command in the root folder of project (there is docker-compose.yml here):<br>
docker-compose run web python manage.py migrate<br>
3) create superuser by:<br>
docker-compose run web python manage.py superuser<br>
4) in the root folder of project run:<br>
docker-compose up<br>
5) in the address bar your browser enter:<br>
http://0.0.0.0:8000/messages/start/?duration=5<br>
duration - this is a duration of session from start to finish sending messages.<br>
You will get output to the console:<br>

START 2021-08-21 16:15:29.235648+00:00<br>
web1_1       | HTTP POST /messages/ 200 [0.02, 172.26.0.8:59564]<br>
web2_1       | [21/Aug/2021 16:15:29] "POST /messages/ HTTP/1.1" 200 169<br>
web_1        | HTTP GET /messages/start/?duration=2 200 [0.06, 172.26.0.1:55140]<br>
web2_1       | [21/Aug/2021 16:15:29] "POST /messages/ HTTP/1.1" 200 169<br>
web1_1       | HTTP POST /messages/ 200 [0.05, 172.26.0.8:59568]<br>
web2_1       | [21/Aug/2021 16:15:29] "POST /messages/ HTTP/1.1" 200 169<br>
web1_1       | HTTP POST /messages/ 200 [0.06, 172.26.0.8:59572]<br>
web2_1       | [21/Aug/2021 16:15:29] "POST /messages/ HTTP/1.1" 200 169<br>
.......................<br>
HTTP POST /messages/ 200 [0.03, 172.26.0.8:59700]<br>
web2_1       | [21/Aug/2021 16:15:31] "POST /messages/ HTTP/1.1" 200 169<br>
web1_1       | HTTP POST /messages/ 200 [0.03, 172.26.0.8:59704]<br><br>
web_1        | Session duration: 2 seconds<br>
web_1        | Count of messages: 36<br>

This application may to use for meseuring transmission speed your environment of microservices.<br>
Further I will make the ring with WebSocket and Kafka channels (I mean the exchange messages by Kafka broker), and to make traicing by Jaeger.<br>
