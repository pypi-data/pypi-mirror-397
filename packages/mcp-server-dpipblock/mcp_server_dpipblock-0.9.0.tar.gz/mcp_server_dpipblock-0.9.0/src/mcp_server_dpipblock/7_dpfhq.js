global.window = {};
const JSEncrypt = require('/mnt/jsencrypt');
const encryptor = new JSEncrypt();

function encrypt(data, public_key1, public_key2) {
//    var c = HS.util.getStringByteLength(a);
//    var d = c > 53 ? getGloableVariable('long_public_key') : getGloableVariable('public_key');
    encryptor.setPublicKey(public_key1);
    return encryptor.encrypt(data)
}