const express = require('express');
const app = express(); 
const port = 4040;

app.use(express.json());


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

app.post('/' , (req , res) => {
    console.log(req.body);
    res.send(req.body);
});

app.listen(port , () => console.log("created server 📡 on port ${port}"));