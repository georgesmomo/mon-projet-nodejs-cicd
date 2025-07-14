const request = require('supertest');
const app = require('./app'); // Assurez-vous que app.js exporte l'application express : module.exports = app;

describe('GET /', () => {
  it('should respond with Hello World!', async () => {
    const response = await request(app).get('/');
    expect(response.statusCode).toBe(200);
    expect(response.text).toContain('<html');
  });
});