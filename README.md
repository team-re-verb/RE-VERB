<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/Tralfazz/RE-VERB">
    <img src="/home/amos/Projects/re-verb/client/website/src/assets/REverb_logo.png" alt="Logo" height="120">
  </a>
</p>
<p align="center">
  <a href="https://github.com/Tralfazz/RE-VERB">
    <img src="/home/amos/Projects/re-verb/client/website/src/assets/REverb_text.png" alt="Logo" height="60">
  </a>
</p>
<br />

# About the project
RE: VERB is [speaker diarization](https://en.wikipedia.org/wiki/Speaker_diarisation) system, 
it allows the user to send/record audio of a conversation and receive timestamps of who spoke when

RE:VERB is our final project in [Magshimim](https://www.magshimim.cyber.org.il/), and consists of a web client and a server.

* The [client](#Client) can record audio and show the the timestamp results graphically

* The [server](#Server) can be used with many other clients with the simple REST API it has.



## Built With

### client
* [Vue.js](http://https://vuejs.org/) - The front end framework used
* [Wavesurfer.js](https://wavesurfer-js.org) - A library for waveform visualization 
### server

* [Pytorch](https://pytorch.org/) - library for deep learning with python that has great support for GPUs with CUDA

* [Express.js](https://maven.apache.org/) - Node.js web server framework

## Getting Started
The project contains the server and the web client(a CLI client also exists for debug purposes).

the server is located at ```./server```
and the web client is located at ```./client/website```.

***
### **Server**

The model alongside the scripts for downloading, training and the weights from our training is located at ```./server/speech_diarization/model```



we used Docker to create a cross-platform environment to run the server on.

The server is made up of:
* a container for the web server
* a container for the diarization process
* a container for a redis database that will allow the others to communicate

docker compose will run and manage all 3 at once

**Docker and docker-compose need to be installed** in order to build and run the server, all the rest will be taken care of.


### Installing

```bash
cd server
docker-compose up
```

This will run all 3 containers and install dependencies.


If you make a change in the server, use

```bash
docker-compose up --build
```
to rebuild.


>### __usage:__
>
>sending a HTTP POST request with an audio file to the server at ```http://localhost:1337/upload``` (default port and url) will return a JSON file with the timestamps in milliseconds.
>
>```json
>{"0": [[40, 120], [3060, 3460], [3480, 3560]], "1": [[1260, 1660], [1680, 1960]]}
>```
***

## __Client__
**The client needs npm or yarn to be installed**, more info about the client can be found [here](client/website/README.md).

to install:
```bash
cd client/website
npm install
```

afterwards you can use
```
npm run serve
```
to run a development server

***
## Authors

* **Ofir Naccache** - [ofirnaccache](https://github.com/ofirnaccache)
* **Matan Yesharim** - [Tralfazz](https://github.com/Tralfazz)
## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* The diarization algorithm is an implementation of [this research](https://google.github.io/speaker-id/publications/LstmDiarization/), we also used their implementation of the spectral clustering

* We took inspiration and some code from [Harry volek's implementation](https://github.com/HarryVolek/PyTorch_Speaker_Verification) of a different but similar problem - Speaker Verification

## Future Plans

* We had problems with training on the AMI corpus so we used the TIMIT corpus for the model provided. 

* We plan to train again on the [VoxCeleb 1 and 2](http://www.robots.ox.ac.uk/~vgg/data/voxceleb/) datasets which contain a lot more data and hopefully improve feature extraction
