import { Buffer } from 'buffer';
var asn1 = require('asn1.js');

export const pemToBuffer = (pemString) => {
    const pemRegex = /-----BEGIN [A-Z ]+-----([\s\S]+?)-----END [A-Z ]+-----/;
    let base64Content;

    const match = pemString.match(pemRegex);
    if (match) {
        base64Content = match[1];
    } else {
        base64Content = pemString;
    }

    base64Content = base64Content.replace(/\s+/g, '');

    return Buffer.from(base64Content, 'base64');
}

export const ECPrivateKey = asn1.define('ECPrivateKey', function () {
    this.seq().obj(
        this.key('version').int(),
        this.key('privateKey').octstr(),
        this.key('parameters').explicit(0).optional().any(),
        this.key('publicKey').explicit(1).optional().bitstr()
    );
});
