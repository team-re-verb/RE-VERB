const express = require('express');
const app = express(); 
const port = 4040;

app.use(express.json());


app.get('/' , (req , res) => {
    console.log(req.body);
    res.send(req.body);
});

app.listen(port , () => console.log("created server 📡 on port ${port}"));