// wb_node.js
// const CryptoJS = require("crypto-js");
const CryptoJS = require("./lib/crypto-js.min.js");
class RevealHelper {
    constructor() { this.salt = "b723375b3aac60afa239c149"; }
    reveal(arrayKey) {
        const t = Buffer.from(this.salt, "utf-8");
        const a = Buffer.alloc(arrayKey.length);
        for (let i = 0; i < arrayKey.length; i++) {
            a[i] = arrayKey[i] ^ t[i % t.length];
        }
        return a.toString("utf-8");
    }
}

class Encryptor {
    constructor() {
        this.arrayKey = Uint8Array.from([
            84,7,81,11,3,86,84,91,82,0,85,86,83,3,83,94,
            4,10,2,15,6,3,81,90,7,5,7,4,1,82,5,87,
            4,85,89,80,82,0,89,7,85,87,5,12,87,6,82,9,
            90,2,84,85,2,86,84,1,1,84,83,83,84,7,82,94
        ]);
        this.helper = new RevealHelper();
    }

    getKey() {
        const r = this.helper.reveal(this.arrayKey);
        const n = CryptoJS.SHA256(r).toString(CryptoJS.enc.Hex);
        return CryptoJS.enc.Hex.parse(n);
    }

    encode(input) {
        const t = CryptoJS.enc.Utf8.parse(input);
        const key = this.getKey();
        let o = null;

        for (let i = 0; i < 3; i++) {
            const plaintext = o ? CryptoJS.enc.Utf8.parse(o) : t;
            const iv = CryptoJS.lib.WordArray.random(16);
            const cipher = CryptoJS.AES.encrypt(plaintext, key, {
                iv: iv,
                mode: CryptoJS.mode.CTR,
                padding: CryptoJS.pad.NoPadding
            }).ciphertext;

            const combined = CryptoJS.lib.WordArray.create(iv.words.concat(cipher.words));
            o = CryptoJS.enc.Base64.stringify(combined);
        }
        return o;
    }

    generateGuid() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
            .replace(/[xy]/g, c => { const r = Math.random()*16|0; const v = c==='x'?r:(r&3|8); return v.toString(16); }).toUpperCase();
    }

    generateEncryptedHeaders() {
        const uuid = this.generateGuid();
        return { uuid, encodedUuid: this.encode(`RequestUUID:${uuid}`) };
    }
}

const result = new Encryptor().generateEncryptedHeaders();
console.log(JSON.stringify(result));
