// copied from https://gist.github.com/allenhwkim/19c2f36a7afa6f0c507008613e966d1b

export const Cookie = {
  set: function (key, value, days=1) {
    let date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    let expires = date.toUTCString();
    document.cookie = key + '=' + value + '; expires=' + expires + '; path=/';
  },
  getAll: function () {
    let cookie = {};
    document.cookie.split(';').forEach(el => {
      let [k, v] = el.split('=');
      cookie[k.trim()] = v;
    });
    return cookie;
  },
  get: function (name) {
    return this.getAll()[name];
  },
  delete: function (name) {
    this.set(name, '', -1);
  }
};
