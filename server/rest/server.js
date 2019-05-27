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

if(redis_uri != undefined) {
    subscriber = redis.createClient(redis_uri);
    publisher = redis.createClient(redis_uri);
}
else {
    subscriber = redis.createClient();
    publisher = redis.createClient();
}


// support for json
app.use(express.json());

/*
* Used in order to allow to make HTTP requests to the same address
*/
app.use((req,res,next) => {
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8080');
    next()
})


/**
 * Event for post request with file upload.
 * Send the request to the python server
 * */
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


/**
 * Event listener to GET request of /
 * 
*/
app.get('/' , (req , res, next) => {

    const param = req.query.txt ? req.query.txt : "defualt";

    console.log("REDIS: publishing to diarization");
    console.log("params: " + param);

    publisher.publish("diarization_py", "param:" + param);

    next();
});


/**
 * In Both cases for requests for / and /upload there is a need to 
 * send messages to the python server
*/
app.use(["/" , "/upload"] , (req, res, next) => {
    subscriber.on('message', (channel, msg) => {
        console.log("sending message: ", msg, "to ", req.path);
        res.end(channel + " : " + msg);
        next();
    })
});

/**
 * Used for returning HTTP 404 errors in case that a user tries to access a page which is not found
*/
//app.get('*', function(req, res) {
//    console.log('not found!!!@!@!')
//    res.status(404).send('Page not found.');
//});


/**
* Listens for connection in a specified port
*/
app.listen(port , () => {
    console.log("created server 📡 on port " + port)
    subscriber.subscribe("diarization_node");
});