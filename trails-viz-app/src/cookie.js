// copied from https://gist.github.com/allenhwkim/19c2f36a7afa6f0c507008613e966d1b

export const Cookie = {
  set: function (key, value, days=1) {
    let date = new Date();
    // hack: intentionally expire the front end cookie 1 hour before auth token
    date.setTime(date.getTime() + (days * 23 * 60 * 60 * 1000));
    let expires = date.toUTCString();
    document.cookie = key + '=' + value + '; expires=' + expires + '; path=/';
  },
  get: function (name) {
    name = name + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
    return undefined;
  },
  delete: function (name) {
    this.set(name, '', -1);
  }
};
