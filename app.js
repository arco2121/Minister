const express = require("express");
const http = require("node:http");
const ejs = require("ejs");
const render = (res,page) => {
    res.render("index", {
        page: page
    });
}

const app = express();
const server = http.createServer(app);

app.use(express.static("./public"));
app.use(express.urlencoded({ extended: true }));
app.set("view engine", "ejs");
app.set('trust proxy', 1);
app.use(express.json());

app.get("/", (_, res) => render('output'));
app.get("/test", (_, res) => render('test'));

server.listen(7460, (err) => {
    if(err) console.error(err);
    console.log("Minister Online => http://localhost:7460/");
});