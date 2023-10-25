const express = require('express');
const app = express();
const port = 8080; // Porta que o aplicativo será executado

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html'); // Envia o arquivo HTML quando alguém acessa o caminho raiz "/"
});

app.listen(port, () => {
    console.log(`Aplicativo Node.js está rodando em http://localhost:${port}`);
});
