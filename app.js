const express = require('express');
const app = express();

const routes = require('./routes/route.js');

app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));

app.get('/', routes.home);

// `port` peut changer en fonction de l'environnement ⇒ `const` est ok car assigné une fois
const port = process.env.PORT || 3000;

// `server` peut être utile plus tard (ex: pour tests), mais pas modifié ⇒ `const`
const server = app.listen(port, function () {
    console.log("Catch the action at http://localhost:" + port);
});
