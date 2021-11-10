#The prototipe of microservice application made by djangorestframework.<br>
Three microservices send each other messages through Kafka broker. Each microservice add timestamp to the message. The message go by ring. First microservice inits sending and save to database the message from last microsevice.
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
web1_1  ..............<br>     
.......................<br>
web_1        | Session duration: 2 seconds<br>
web_1        | Count of messages: 36<br>

This application may to use for meseuring transmission speed your environment of microservices.
