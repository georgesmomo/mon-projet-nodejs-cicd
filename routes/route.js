// router/router.js
exports.home = function (req, res) {
  // On ajoute un log pour tracer l'accès à la page d'accueil
  console.log(
    `[INFO] - ${new Date().toISOString()} - Accès à la page /home. IP client: ${
      req.ip
    }`
  );
  res.render("home");
};

exports.login = function (req, res) {
  // On ajoute un log pour tracer l'accès à la page de login
  console.log(
    `[INFO] - ${new Date().toISOString()} - Accès à la page /login. IP client: ${
      req.ip
    }`
  );
  res.render("login");
};
