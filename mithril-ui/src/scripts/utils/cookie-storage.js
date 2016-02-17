/**
    * The number of days until the cookie should expire
    */
var NB_EXPIRATION_DAYS = 14;

/**
    * Default constructor of Cookie Store
    */
function CookieStorage( ) {
    this.$storage = document.cookie = '';
}


/**
    * Stores the value for a given key
    * @param {string} key   a key
    * @param {object} value a value
    */
CookieStorage.prototype.set = function ( key , value ) {
    var expiration = new Date();
    var stringifiedValue = JSON.stringify( value );
    expiration.setTime( expiration.getTime() + ( NB_EXPIRATION_DAYS * 24*60*60*1000 ) );
    var expires = 'expires='+expiration.toUTCString();
    document.cookie = key + '=' + stringifiedValue + '; ' + expires;
};


/**
    * Returns the value given a key
    * @param {string} key a key
    */
CookieStorage.prototype.get = function ( key ) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + key + "=");
    if(parts.length == 2) {
        return JSON.parse(decodeURIComponent(parts.pop().split(";").shift()));
    }
    return  {};
};

/**
    * Removes the key from the store
    * @param {string} key a key
    */
CookieStorage.prototype.remove = function ( key ) {
    document.cookie = key+"=;expires=Thu, 01 Jan 1970 00:00:01 GMT";
};

var storage = new CookieStorage();
module.exports = storage;

