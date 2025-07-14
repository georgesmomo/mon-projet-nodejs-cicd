const express = require('express');
const app = express();

const routes = require('./routes/route.js');

app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));

app.get('/', routes.home);

app.get('/healthz', (req, res) => {
  res.status(200).send('OK');
});

const port = process.env.PORT || 3000;

// 👉 Ne démarre le serveur que si le fichier est exécuté directement
if (require.main === module) {
  app.listen(port, function () {
    console.log("Catch the action at http://localhost:" + port);
  });
}

module.exports = app;
