// Run tests.js by following the instructions below:

// Run file by opening a terminal and running the following:
// $ mocha Season-2/Level-3/tests.js

// If you're inside a Codespace, the above should be running smoothly.

// In case you're running this locally, please run the following command 
// first, and then run the tests' file:
// $ npm install Season-2/Level-3/ && npm install --global mocha

const app = require("./code");
// const app = require("./solution"); // To test the solution, uncomment this line and comment the one above
const request = require('supertest');
const { expect } = require('chai');

describe('POST /ufo', () => {
  it('should respond with a successful JSON response', (done) => {

    request(app)
      .post('/ufo')
      .set('Content-Type', 'application/json')
      .expect(200)
      .end((err, res) => {
        if (err) return done(err + "\n" +  res.text);
        expect(res.body.ufo).to.equal('Received JSON data from an unknown planet.');
        done();
      });
  });

  it('should handle valid XML data', function (done) {
    const xmlData = '<?xml version="1.0" encoding="utf-8"?><ufo><location>Canada</location></ufo>';
    request(app)
      .post('/ufo')
      .set('Content-Type', 'application/xml')
      .send(xmlData)
      .expect(200)
      .end(function (err, res) {
        if (err) return done(err + "\n" +  res.text);
        expect(res.text).to.equal("Canada");
        done();
      });
  });

  it('should respond with a 400 error for invalid XML', (done) => {
    const invalidXmlPayload = 'invalid>a<xml>';

    request(app)
      .post('/ufo')
      .set('Content-Type', 'application/xml')
      .send(invalidXmlPayload)
      .expect(400)
      .end((err, res) => {
        if (err) return done(err + "\n" +  res.text);
        expect(res.text).to.include('Invalid XML');
        done();
      });
  });

  it('should respond with a 400 error for unsupported content type', (done) => {
    request(app)
      .post('/ufo')
      .set('Content-Type', 'application/octet-stream')
      .send('Some data')
      .expect(405, done);
  });
});

describe('POST /ufo/upload', () => {
  it('should return 501 Not Implemented (endpoint removed to prevent RCE)', (done) => {
    request(app)
      .post('/ufo/upload')
      .attach('file', Buffer.from('malicious content'), 'payload.admin')
      .expect(501, done);
  });
});

describe('POST /ufo - security: XXE', () => {
  it('should reject XML containing an XXE SYSTEM entity', (done) => {
    const xxePayload =
      '<?xml version="1.0"?><!DOCTYPE ufo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><ufo><location>&xxe;</location></ufo>';

    request(app)
      .post('/ufo')
      .set('Content-Type', 'application/xml')
      .send(xxePayload)
      .end((err, res) => {
        // Must not echo back /etc/passwd contents; 400 or empty content both acceptable
        if (res.status === 200) {
          expect(res.text).to.not.include('root:');
        }
        done();
      });
  });

  it('should reject XML with a .admin SYSTEM entity (command injection backdoor)', (done) => {
    const adminPayload =
      '<?xml version="1.0"?><!DOCTYPE ufo [<!ENTITY cmd SYSTEM "file://hack.admin">]><ufo><location>&cmd;</location></ufo>';

    request(app)
      .post('/ufo')
      .set('Content-Type', 'application/xml')
      .send(adminPayload)
      .end((err, res) => {
        // Must return 400 and must not execute commands
        expect(res.status).to.equal(400);
        done();
      });
  });
});

after(() => {
  app.close();
});