const express = require('express');
const redis = require('redis')


const app = express();
const port = process.argv[2]; //4040

app.use(express.json());


const subscriber = redis.createClient();
const publisher = redis.createClient();


app.post('/upload' , (req,res) => {

    console.log(req.body)

    switch(req.body["result"])
    {
        case "record":
            res.send(JSON.stringify({
                person1: ["record1.wav", "record2.wav"],
                person2: ["record1.wav", "record2.wav"]

            }));
            break;
        
        case "timestamp":
            res.send(JSON.stringify({
                person1 : [
                    "0:00-0:24",
                    "1:00-1:21"
                ],
                person2: [
                    "0:25-1:00",
                    "1:22-1:44"
                ]
            }));
            break;
    }
})


app.get("/recordings/:id/text", (req,res) => {
    //TODO wit.ai speech-to-text
    res.send("wowowoww");
})


app.get("/recordings", (req, res) => {

    const _recordings = ["record1.wav" , "record2.wav"]
    res.send(_recordings);
})

app.get('/' , (req , res) => {

    console.log("REDIS: publishing to diarization");
    console.log("params: " + req.query.txt)

    publisher.publish("diarization_py", req.query.txt);

    subscriber.on('message', (channel, msg) => {
        res.end(channel + " : " + msg);
    })
});

app.listen(port , () => {
    console.log("created server 📡 on port ${port}")
    subscriber.subscribe("diarization_node");
});