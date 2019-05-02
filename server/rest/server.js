// YOU NEED REDIS SERVER RUNNING FIRST
//
// to run use environment variables:
// PORT and REDIS_URI
// run: # PORT=[port] REDIS_URI=[redis_uri] npm start
//   or # npm start [port] [redis_uri]
//
// however it is advised you use 'docker compose up' on the entire server to avoid compatibility issues


const express = require('express');
const redis = require('redis');
const multer = require('multer');
const fs = require('fs');


const app = express();
const port = process.env.PORT || process.argv[2] || 4040; //default 4040

const DIR_PATH = "/upload";
const upload = multer({ dest: DIR_PATH }); 


// redis initialization
let subscriber;
let publisher;

const redis_uri = process.env.REDIS_URI || process.argv[3];

if(redis_uri != undefined)
{
    subscriber = redis.createClient(redis_uri);
    publisher = redis.createClient(redis_uri);
}
else
{
    subscriber = redis.createClient();
    publisher = redis.createClient();
}


// server
app.use(express.json());


app.post('/upload' , upload.single('file') , (req,res, next) => {

    console.log(req.body);
    console.log("path: " , req.file.path);

    fs.readFile(req.file.path, (err, data) => {
        if (err) throw err;
        console.log(data);
        
        publisher.publish("diarization_py", "file:" + req.file.path);
    })

    next();
})


app.get("/recordings/:id/text", (req,res) => {
    //TODO wit.ai speech-to-text
    res.send("wowowoww");
})


app.get("/recordings", (req, res) => {

    fs.readdir(DIR_PATH , (err, files) => {
        if (err) throw err;
        res.send(files);
    });
})

app.get('/' , (req , res, next) => {

    const param = req.query.txt ? req.query.txt : "defualt";

    console.log("REDIS: publishing to diarization");
    console.log("params: " + param);

    publisher.publish("diarization_py", "param:" + param);

    next();
});



app.use(["/" , "/upload"] , (req, res, next) => {
    subscriber.on('message', (channel, msg) => {
        console.log("sending message: ", msg, "to ", req.path);
        res.end(channel + " : " + msg);
        next();
    })
});

app.listen(port , () => {
    console.log("created server 📡 on port " + port)
    subscriber.subscribe("diarization_node");
});